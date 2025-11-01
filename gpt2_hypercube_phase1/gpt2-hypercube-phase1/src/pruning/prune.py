"""
Structured pruning utilities (template).

Functions:
 - get_attn_modules(model) -> list of (layer_idx, attn_module)
 - head_importance_by_weight(model) -> dict[layer_idx] = np.array(shape=(n_heads,))
 - apply_head_mask(model, mask_dict, in_place=True) -> model (pruned)
 - prune_heads_by_fraction(model, fraction=0.1, in_place=False) -> (model, mask_dict)
 - save_pruned_checkpoint(model, path)
Notes:
 - This is a conservative, dependency-light template that zeros the parameter slices
   corresponding to pruned heads. It operates on GPT-2 attention modules with attributes
   `c_attn` and `c_proj`. Adapt for other architectures as needed.
"""
from typing import List, Tuple, Dict
import copy
import os
import torch
import numpy as np


def get_attn_modules(model) -> List[Tuple[int, torch.nn.Module]]:
    """
    Return list of (layer_idx, attn_module) for GPT-2 style model.transformer.h layers.
    """
    attns = []
    if not hasattr(model, "transformer") or not hasattr(model.transformer, "h"):
        # try model.h (for some wrappers)
        layers = getattr(model, "h", None)
    else:
        layers = model.transformer.h
    if layers is None:
        return attns
    for i, layer in enumerate(layers):
        attn = getattr(layer, "attn", None)
        if attn is not None:
            attns.append((i, attn))
    return attns


def head_importance_by_weight(model) -> Dict[int, np.ndarray]:
    """
    Compute simple head importance scores based on L2 norm of c_attn weights per head.
    Returns dict: layer_idx -> np.array(n_heads,)
    """
    out = {}
    attns = get_attn_modules(model)
    cfg = getattr(model.config, None)
    for i, attn in attns:
        # attempt to infer dims
        n_heads = getattr(cfg, "n_head", None)
        embed_dim = getattr(cfg, "n_embd", None)
        # fallback to derive from modules
        if n_heads is None or embed_dim is None:
            # try to infer from attn attributes
            try:
                embed_dim = attn.split_size if hasattr(attn, "split_size") else embed_dim
                n_heads = attn.num_heads if hasattr(attn, "num_heads") else n_heads
            except Exception:
                pass
        if n_heads is None or embed_dim is None:
            # cannot compute reliably -> skip
            continue
        head_dim = embed_dim // n_heads
        # c_attn.weight shape expected (3*embed_dim, embed_dim)
        try:
            W = attn.c_attn.weight.data.clone().cpu().numpy()
        except Exception:
            # fallback: try attribute named weight_proj etc.
            try:
                W = attn.c_attn.weight.clone().cpu().numpy()
            except Exception:
                continue
        # reshape to (3, n_heads, head_dim, in_features)
        out_dim = W.shape[0]
        in_feat = W.shape[1]
        if out_dim != 3 * embed_dim:
            # unexpected shape, compute per-head by grouping output into n_heads
            per_head = []
            rows_per_head = out_dim // (3 * n_heads) if (3 * n_heads) != 0 else 0
            for h in range(n_heads):
                # approximate slice indices
                start = h * rows_per_head * 3
                end = start + rows_per_head * 3
                slice_w = W[start:end, :]
                per_head.append(np.linalg.norm(slice_w))
            out[i] = np.array(per_head)
            continue
        W3 = W.reshape(3, n_heads, head_dim, in_feat)  # qkv, heads, head_dim, in_feat
        # compute norm across qkv + in_feat + head_dim
        norms = np.sqrt(np.sum(W3 * W3, axis=(0, 2, 3)))
        out[i] = norms
    return out


def apply_head_mask(model, mask_dict: Dict[int, List[int]], in_place: bool = True):
    """
    Zero-out parameters corresponding to heads listed in mask_dict {layer_idx: [head_idxs]}.
    If in_place is False, operate on a deepcopy and return it.
    """
    target = model if in_place else copy.deepcopy(model)
    cfg = getattr(target.config, None)
    attns = get_attn_modules(target)
    for layer_idx, attn in attns:
        heads_to_prune = set(mask_dict.get(layer_idx, []))
        if not heads_to_prune:
            continue
        n_heads = getattr(cfg, "n_head", None)
        embed_dim = getattr(cfg, "n_embd", None)
        if n_heads is None or embed_dim is None:
            # best-effort: try to obtain from attn attributes
            n_heads = getattr(attn, "num_heads", n_heads)
            embed_dim = getattr(attn, "split_size", embed_dim)
        if n_heads is None or embed_dim is None:
            continue
        head_dim = embed_dim // n_heads
        # zero slices in c_attn.weight (shape: 3*embed_dim, embed_dim)
        try:
            w = attn.c_attn.weight.data
            b = attn.c_attn.bias.data if hasattr(attn.c_attn, "bias") else None
        except Exception:
            continue
        out_dim = w.shape[0]
        if out_dim == 3 * embed_dim:
            # qkv concatenated along out dim: order is [q0..qH, k0.., v0..]
            # reshape to (3, n_heads, head_dim, in_feat)
            w3 = w.view(3, n_heads, head_dim, -1)
            for h in heads_to_prune:
                w3[:, h, :, :].zero_()
            # write back
            attn.c_attn.weight.data.copy_(w3.view(out_dim, -1))
            if b is not None:
                try:
                    b3 = b.view(3, n_heads, head_dim)
                    for h in heads_to_prune:
                        b3[:, h, :].zero_()
                    attn.c_attn.bias.data.copy_(b3.view(out_dim))
                except Exception:
                    pass
        else:
            # fallback: try partition output rows per head
            rows_per_head = out_dim // (3 * n_heads) if (3 * n_heads) != 0 else 0
            for h in heads_to_prune:
                start = h * rows_per_head * 3
                end = start + rows_per_head * 3
                w[start:end, :].zero_()
                if b is not None and b.numel() >= end:
                    b[start:end].zero_()
        # zero corresponding rows in c_proj (shape embed_dim, embed_dim). c_proj maps concatenated heads -> hidden
        try:
            wproj = attn.c_proj.weight.data
            # c_proj expects input dim = embed_dim (concatenated heads)
            # zero rows that correspond to pruned head outputs: rows slice indices for each head
            # mapping from head to row range: head * head_dim : (head+1)*head_dim
            for h in heads_to_prune:
                r0 = h * head_dim
                r1 = (h + 1) * head_dim
                # zero those rows
                wproj[:, r0:r1].zero_()
            # also zero bias if present in c_proj
            if hasattr(attn.c_proj, "bias") and attn.c_proj.bias is not None:
                # no straightforward mapping for bias; leave as-is
                pass
        except Exception:
            pass
    return target


def prune_heads_by_fraction(model, fraction: float = 0.1, in_place: bool = False):
    """
    Compute importance per head and prune the lowest `fraction` heads per layer (at least 1 if fraction>0).
    Returns (model_after, mask_dict)
    """
    imp = head_importance_by_weight(model)
    mask = {}
    for layer_idx, scores in imp.items():
        n_heads = scores.shape[0]
        k = max(1, int(np.floor(n_heads * fraction)))
        idxs = np.argsort(scores)[:k].tolist()
        mask[layer_idx] = idxs
    new_model = apply_head_mask(model, mask, in_place=in_place)
    return new_model, mask


def save_pruned_checkpoint(model, path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # save via HuggingFace interface if available
    try:
        model.save_pretrained(path)
    except Exception:
        # fallback to torch.save
        torch.save({"state_dict": model.state_dict()}, path)
