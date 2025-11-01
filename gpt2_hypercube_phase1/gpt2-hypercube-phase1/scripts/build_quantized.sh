#!/bin/bash

# Build the quantized GPT-2 model
echo "Starting the build process for the quantized GPT-2 model..."

# Step 1: Install required packages
echo "Installing required packages..."
pip install -r ../requirements.txt

# Step 2: Run the quantization script
echo "Running quantization..."
python ../src/core/quantized_gpt2.py --quantization 4bit

# Step 3: Prune low-importance attention heads and neurons
echo "Pruning low-importance attention heads and neurons..."
python ../src/pruning/prune.py --model_path ../src/core/quantized_gpt2.py

# Step 4: Verify the model
echo "Verifying the model for load/inference stability..."
python ../src/core/model_utils.py --verify ../src/core/quantized_gpt2.py

echo "Build process completed successfully!"