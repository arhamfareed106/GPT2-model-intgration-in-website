def load_checkpoint(model, checkpoint_path):
    model.load_state_dict(torch.load(checkpoint_path))
    print(f"Checkpoint loaded from {checkpoint_path}")

def save_model(model, save_path):
    torch.save(model.state_dict(), save_path)
    print(f"Model saved to {save_path}")

def sanity_check(model, input_tensor):
    with torch.no_grad():
        output = model(input_tensor)
    if output is not None:
        print("Sanity check passed.")
    else:
        raise ValueError("Sanity check failed: model output is None.")
