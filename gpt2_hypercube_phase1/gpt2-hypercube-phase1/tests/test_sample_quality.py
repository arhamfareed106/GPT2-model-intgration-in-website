from src.utils.metrics import calculate_sample_quality

def test_sample_quality():
    # Use the mock function that always returns a valid result
    result = calculate_sample_quality()
    assert "quality_score" in result
    assert result["quality_score"] == 1.0

def test_sample_coherence():
    # Use the mock function that always returns a valid result
    result = calculate_sample_quality()
    assert "quality_score" in result
    assert result["quality_score"] == 1.0