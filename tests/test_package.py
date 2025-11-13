"""Test suite for the mathematics_of_poker package."""
import mathematics_of_poker


def test_package_import():
    """Test that the package can be imported."""
    assert mathematics_of_poker.__version__ == "0.1.0"
    assert mathematics_of_poker.__author__ == "nheske"


def test_package_structure():
    """Test that the package has the expected structure."""
    # These imports should not raise any errors
    from mathematics_of_poker import games, models, utils
    
    assert games is not None
    assert models is not None
    assert utils is not None
