import pytest
import main

def test_get_first_bill_heading():
    """
    Tests that the bill heading is accessible in data being accessed
    """
    assert "H.R.2806" in main.get_first_bill_heading()