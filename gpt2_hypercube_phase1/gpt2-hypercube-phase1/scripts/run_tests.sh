#!/bin/bash

# Run unit tests for numerical stability and sample quality

echo "Running unit tests for numerical stability..."
pytest tests/test_numerical_stability.py

echo "Running unit tests for sample quality..."
pytest tests/test_sample_quality.py

echo "All tests completed."