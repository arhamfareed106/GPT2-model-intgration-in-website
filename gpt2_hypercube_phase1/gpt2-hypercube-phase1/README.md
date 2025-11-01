# gpt2-hypercube-phase1

## Project Overview
The gpt2-hypercube-phase1 project aims to develop a quantized version of the GPT-2 model, optimized for performance and efficiency. This project includes the implementation of a hypercube conceptual framework, structured pruning of low-importance components, and a robust routing mechanism for concept embeddings.

## Features
- **Quantized GPT-2 Model**: A lightweight version of the GPT-2 model using 4-bit quantization, targeting approximately 63 MB.
- **Hypercube Structure**: A conceptual skeleton that defines the properties and relationships within a hypercube topology.
- **Pruning Mechanism**: Structured pruning of low-importance attention heads and neurons to enhance model performance.
- **Concept Mapping**: A mapping system that links concept embeddings to vertex IDs within the hypercube.
- **Bit-Transition Routing**: A routing table that defines connections based on Hamming distance, facilitating efficient data flow.

## Directory Structure
- **src/**: Contains the source code for the project.
  - **core/**: Implements the quantized GPT-2 model and utility functions.
  - **hypercube/**: Defines the hypercube structure and topology.
  - **pruning/**: Implements the pruning logic for the model.
  - **embeddings/**: Manages concept embedding mappings.
  - **routing/**: Contains the bit-transition routing table.
  - **utils/**: Provides utility functions for metrics and testing.
  
- **tests/**: Contains unit tests for verifying numerical stability and sample quality.
  
- **notebooks/**: Jupyter notebooks for conducting experiments and documenting results.
  
- **configs/**: Configuration files for project parameters.
  
- **scripts/**: Shell scripts for automating build and test processes.
  
- **requirements.txt**: Lists the dependencies required for the project.
  
- **pyproject.toml**: Project configuration file.

## Installation
To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd gpt2-hypercube-phase1
pip install -r requirements.txt
```

## Usage
1. **Building the Quantized Model**: Run the build script to create the quantized GPT-2 model.
   ```bash
   ./scripts/build_quantized.sh
   ```

2. **Running Tests**: Execute the test script to verify numerical stability and sample quality.
   ```bash
   ./scripts/run_tests.sh
   ```

3. **Experimentation**: Use the Jupyter notebook in the `notebooks/` directory to conduct experiments and analyze results.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.