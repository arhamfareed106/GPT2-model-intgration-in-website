# Save FP16 rollback checkpoint
from transformers import GPT2LMHeadModel
model.save_pretrained("gpt2-shrek-chaos-fp16")
# and record metadata
with open("gpt2-shrek-chaos-fp16/metadata.json","w") as f:
    import json, os
    json.dump({"git": os.popen("git rev-parse --short HEAD").read().strip()}, f)
