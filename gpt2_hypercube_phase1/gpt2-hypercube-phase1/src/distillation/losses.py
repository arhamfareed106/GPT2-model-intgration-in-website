"""
Distillation and regularization losses.
Keep lightweight, compatible with torch tensors.
"""
import torch
import torch.nn.functional as F


def token_lm_loss(student_logits: torch.Tensor, teacher_logits: torch.Tensor, labels: torch.Tensor = None):
    """
    Distillation loss between teacher and student logits (KL or MSE).
    If labels provided, include CE.
    """
    # KL between teacher soft targets and student log-probs
    with torch.no_grad():
        teacher_probs = F.softmax(teacher_logits / 1.0, dim=-1)
    student_log_probs = F.log_softmax(student_logits / 1.0, dim=-1)
    kd_loss = F.kl_div(student_log_probs, teacher_probs, reduction="batchmean")
    if labels is not None:
        ce = F.cross_entropy(student_logits.view(-1, student_logits.size(-1)), labels.view(-1), ignore_index=-100)
        return kd_loss + ce
    return kd_loss


def concept_prediction_loss(student_concepts: torch.Tensor, teacher_concepts: torch.Tensor):
    """
    MSE / cosine objective for concept (SONAR) vectors.
    """
    return F.mse_loss(student_concepts, teacher_concepts)


def hypercube_transition_regularizer(vertex_seq_preds: torch.Tensor, allow_multi_bit=False, penalty=1.0):
    """
    vertex_seq_preds: LongTensor shape (batch, seq_len) of vertex ids predicted for successive tokens/sentences
    Penalize transitions that are multi-bit flips (Hamming distance > 1).
    For simplicity compute Hamming via XOR and bitcount on CPU tensors.
    """
    if vertex_seq_preds.numel() == 0:
        return torch.tensor(0.0, device=vertex_seq_preds.device)
    # Move to CPU numpy for bitcount if needed
    v = vertex_seq_preds.detach().cpu().numpy()
    batch_pen = 0.0
    for seq in v:
        for i in range(1, len(seq)):
            a = int(seq[i - 1])
            b = int(seq[i])
            h = (a ^ b).bit_count()
            if h > 1 and not allow_multi_bit:
                batch_pen += (h - 1)
    return torch.tensor(batch_pen * penalty / max(1, vertex_seq_preds.shape[0]), dtype=torch.float32)
