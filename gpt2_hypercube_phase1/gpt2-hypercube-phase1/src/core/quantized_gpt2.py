import torch
from transformers import GPT2LMHeadModel, BitsAndBytesConfig

class QuantizedGPT2:
    def __init__(self, model_name="gpt2", quantization_bits=4):
        self.quantization_bits = quantization_bits
        self.model = self.load_model(model_name)

    def load_model(self, model_name):
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model = GPT2LMHeadModel.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=bnb_config,
            dtype=torch.float16,
        )
        return model

    def verify_load_stability(self, input_ids):
        with torch.no_grad():
            outputs = self.model(input_ids)
            return outputs.logits

    def inference(self, input_ids):
        with torch.no_grad():
            outputs = self.model(input_ids)
            return outputs.logits

    def save_model(self, save_directory):
        self.model.save_pretrained(save_directory)

    def load_quantized_model(self, save_directory):
        self.model = GPT2LMHeadModel.from_pretrained(save_directory)
