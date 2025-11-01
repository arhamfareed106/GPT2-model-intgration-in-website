"""
Inference manager that supports modes: factual, balanced, creative (PIP).
Returns output + provenance + confidence + warnings and integrates DialogueState and safety checks.
"""
from typing import Callable, Optional, Dict, Any, List
import numpy as np

from .dialogue_state import DialogueState
from .safety import basic_safety_check, fallback_safe_response

# type hints:
# generator(genome, prompt, temperature) -> str
# encoder(texts) -> np.ndarray (n, dim)
# vectordb must implement query(qvec, top_k) -> list of {vertex_id, score, meta}


class InferenceManager:
    def __init__(
        self,
        generator: Callable[[Any, str, float], str],
        encoder: Callable[[List[str]], np.ndarray],
        vectordb,
        dialogue_state: Optional[DialogueState] = None,
        evaluator: Optional[Callable[[str, str], Dict[str, float]]] = None,
        human_review_cb: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
    ):
        self.generator = generator
        self.encoder = encoder
        self.vectordb = vectordb
        self.dialogue_state = dialogue_state or DialogueState()
        self.evaluator = evaluator
        self.human_review_cb = human_review_cb

    def _mode_params(self, mode: str):
        # Returns (temperature, allow_multi_bit, hypercube_jump_scale, pip_flag)
        if mode == "factual":
            return 0.6, False, 0.1, False
        if mode == "creative":
            return 1.6, True, 1.0, True
        # balanced
        return 1.0, False, 0.5, False

    def generate(
        self,
        user_id: str,
        genome: Any,
        prompt: str,
        mode: str = "balanced",
        top_k_provenance: int = 3,
        require_human_review: bool = True,
    ) -> Dict[str, Any]:
        temp, allow_multi_bit, jump_scale, pip_flag = self._mode_params(mode)
        # update token context
        self.dialogue_state.push_tokens(user_id, prompt.split()[-10:])
        # call generator with genome and temperature
        raw_out = self.generator(genome, prompt, temp)
        # provenance: get top-k from vectordb using encoder
        try:
            qvec = self.encoder([prompt])[0]
            prov = self.vectordb.query(qvec, top_k=top_k_provenance)
        except Exception:
            prov = []
        # compute confidence: use evaluator if present else average provenance score
        if self.evaluator:
            scores = self.evaluator(raw_out, "")
            confidence = float(np.mean(list(scores.values()))) if scores else 0.5
        else:
            if prov:
                confidence = float(np.mean([p["score"] for p in prov]))
            else:
                confidence = 0.5
        # safety check
        is_safe, reason = basic_safety_check(raw_out)
        warning = None
        audited = {"user_id": user_id, "mode": mode, "temp": temp, "pip_flag": pip_flag}
        if not is_safe:
            # if creative mode and human review available, send for review
            if mode == "creative" and self.human_review_cb is not None and require_human_review:
                approved = self.human_review_cb(raw_out, audited)
                if not approved:
                    # block and return fallback plus label
                    fallback = fallback_safe_response(prompt)
                    return {
                        "output": fallback,
                        "mode": mode,
                        "warning": "PIP_output_blocked_by_human_review",
                        "confidence": 0.0,
                        "provenance": prov,
                        "unsafe": True,
                        "safety_reason": reason,
                    }
            # otherwise return fallback
            return {
                "output": fallback_safe_response(prompt),
                "mode": mode,
                "warning": "unsafe_output_filtered",
                "confidence": 0.0,
                "provenance": prov,
                "unsafe": True,
                "safety_reason": reason,
            }
        # If safe but creative mode, add explicit user-visible warning about PIP
        if mode == "creative":
            warning = f"PIP creative mode ON — outputs may be imaginative. Confidence: {confidence:.2f}"
        # persist vertex: choose top provenance vertex if available else None
        chosen_vid = prov[0]["vertex_id"] if prov else None
        if chosen_vid is not None:
            self.dialogue_state.push_vertex(user_id, chosen_vid)
        # compose result
        result = {
            "output": raw_out,
            "mode": mode,
            "warning": warning,
            "confidence": float(confidence),
            "provenance": prov,
            "unsafe": False,
            "safety_reason": reason if not is_safe else None,
        }
        return result

# Add the ChatAssistant class as requested
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class ChatAssistant:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def clean_output(self, text):
        """
        Cleans and filters unsafe or irrelevant content.
        """
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"[\x00-\x1f]+", "", text)
        # Basic profanity or explicit filter
        unsafe_words = ["sex", "vagina", "penis", "kill", "murder"]
        for word in unsafe_words:
            if word.lower() in text.lower():
                return "[Filtered: unsafe content detected]"
        return text.strip()

    def generate_response(self, user_input: str):
        """
        Generates a chat-style, safe response based on user input.
        """
        system_prompt = (
            "You are Zoid, a helpful and polite AI assistant. "
            "Always answer clearly, factually, and safely. "
            "Avoid any explicit, violent, or irrelevant content."
        )

        # Format the chat-like prompt
        full_prompt = f"{system_prompt}\nUser: {user_input}\nAssistant:"
        inputs = self.tokenizer(full_prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        raw_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Only return the assistant's reply (after "Assistant:")
        reply = raw_text.split("Assistant:")[-1]
        return self.clean_output(reply)

# Initialize the ChatAssistant for use
try:
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    chat_assistant = ChatAssistant(model, tokenizer)
except Exception as e:
    print(f"Warning: Could not initialize ChatAssistant: {e}")
    chat_assistant = None

# Add the generate_response function as requested
def generate_response(prompt: str) -> str:
    """
    Generate a response using the real GPT-2 model.
    This function provides a simple interface for generating responses.
    
    Args:
        prompt (str): The input prompt for the model
        
    Returns:
        str: The generated response from the model
    """
    # If we have a chat assistant, use it
    if chat_assistant is not None:
        try:
            return chat_assistant.generate_response(prompt)
        except Exception as e:
            print(f"Error using ChatAssistant: {e}")
    
    # Fallback to the original implementation
    try:
        # Import the required components
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # Initialize tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Generate response
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        # Decode and return response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from the response if it's at the beginning
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
            
        return response
    except Exception as e:
        print(f"Error in generate_response: {e}")
        return "Sorry, I encountered an error while generating a response."