import os
import pytest
from pathlib import Path
from mcp_pdf_forms.server import extract_form_fields

@pytest.fixture
def dor_form_fields():
    # Get the examples directory path
    examples_dir = Path(__file__).parent.parent / "examples"
    dor_pdf_path = str(examples_dir / "dor-2024-inc-form-1.pdf")
    return extract_form_fields(dor_pdf_path)

def test_filing_status_field_exists(dor_form_fields):
    """Test that the 'filing status' field is correctly extracted from DOR form"""
    # Check that the filing status field exists
    assert "filing status" in dor_form_fields
    
    # Verify the field is a radio button
    assert dor_form_fields["filing status"]["type"] == "radiobutton"
    
    # Verify the field type ID is correct (5 is for radio buttons)
    assert dor_form_fields["filing status"]["field_type_id"] == 5

def test_personal_info_fields_exist(dor_form_fields):
    """Test that personal information fields are correctly extracted"""
    # Check for basic personal info fields
    personal_fields = ["fname", "mi", "lname", "SSN", "madd", "city", "state", "zip"]
    
    for field in personal_fields:
        assert field in dor_form_fields
        assert dor_form_fields[field]["type"] == "text"
        assert dor_form_fields[field]["field_type_id"] == 7

def test_checkbox_fields_exist(dor_form_fields):
    """Test that checkbox fields are correctly extracted"""
    # Sample of checkbox fields from the form
    checkbox_fields = ["Checkcash.0.0.0", "Check112", "not using same federal filing status"]
    
    for field in checkbox_fields:
        assert field in dor_form_fields
        assert dor_form_fields[field]["type"] == "checkbox"
        assert dor_form_fields[field]["field_type_id"] == 2

def test_direct_deposit_field(dor_form_fields):
    """Test that the direct deposit radio button is correctly extracted"""
    # Check that the direct deposit field exists
    assert "direct deposit" in dor_form_fields
    
    # Verify it's a radio button
    assert dor_form_fields["direct deposit"]["type"] == "radiobutton"
    assert dor_form_fields["direct deposit"]["field_type_id"] == 5