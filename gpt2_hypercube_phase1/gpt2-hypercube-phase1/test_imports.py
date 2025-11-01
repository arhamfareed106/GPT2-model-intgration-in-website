import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Try to import without triggering torch import
    from src.distillation import curriculum
    print("✓ curriculum module imported successfully")
except Exception as e:
    print("✗ Failed to import curriculum module:", e)

try:
    from src.utils import metrics
    print("✓ metrics module imported successfully")
    # Test the calculate_sample_quality function
    result = metrics.calculate_sample_quality()
    print("✓ calculate_sample_quality function works:", result)
except Exception as e:
    print("✗ Failed to import or use metrics module:", e)

# Test relative imports in test files
test_imports = [
    "from src.distillation.curriculum import CurriculumSchedule",
    "from src.utils.metrics import calculate_sample_quality",
    "from src.utils.metrics import calculate_numerical_stability",
]

for import_stmt in test_imports:
    try:
        exec(import_stmt)
        print(f"✓ {import_stmt} - successful")
    except Exception as e:
        print(f"✗ {import_stmt} - failed: {e}")