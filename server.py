from pathlib import Path
from typing import List, Optional, Dict, Any
import os
import argparse
import fitz  # PyMuPDF

from mcp.server.fastmcp import FastMCP

# Create a named server
mcp = FastMCP("PDF Finder", dependencies=["mcp[cli]", "pymupdf"])

# Global variable to store base paths
BASE_PATHS = []

@mcp.tool()
def list_pdfs(path_filter: Optional[str] = None) -> List[str]:
    """
    List PDF files in configured base paths
    
    Args:
        path_filter: Optional string to filter PDF paths
        
    Returns:
        List of PDF paths matching the filter
    """
    results = []
    
    for base_path in BASE_PATHS:
        base = Path(base_path)
        if not base.exists():
            continue
            
        for root, _, files in os.walk(base):
            root_path = Path(root)
            for file in files:
                if file.lower().endswith(".pdf"):
                    pdf_path = root_path / file
                    path_str = str(pdf_path)
                    
                    # Apply filter if provided
                    if path_filter and path_filter not in path_str:
                        continue
                        
                    results.append(path_str)
    
    return sorted(results)
    
@mcp.tool()
def extract_form_fields(pdf_path: str) -> Dict[str, Any]:
    """
    Extract all form fields from a PDF
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary of form field names and their properties
    """
    try:
        doc = fitz.open(pdf_path)
        result = {}
        
        # Get form fields
        fields = doc.get_form_text_fields()
        for field_name, field_value in fields.items():
            result[field_name] = {
                "type": "text",
                "value": field_value
            }
            
        # Get additional form field types
        for widget in doc.first_page.widgets():
            field_name = widget.field_name
            field_type = widget.field_type
            field_value = widget.field_value
            field_type_name = widget.field_type_string
            
            if field_name not in result:
                result[field_name] = {
                    "type": field_type_name.lower(),
                    "value": field_value,
                    "field_type_id": field_type
                }
        
        doc.close()
        return result
    except Exception as e:
        return {"error": str(e)}
    
@mcp.tool()
def fill_pdf_form(pdf_path: str, output_path: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fill PDF form fields with provided data
    
    Args:
        pdf_path: Path to the PDF file with form fields
        output_path: Path to save the filled PDF
        field_data: Dictionary of field names and values to fill
        
    Returns:
        Status dictionary with success flag and message
    """
    try:
        doc = fitz.open(pdf_path)
        
        # Fill form fields
        for field_name, value in field_data.items():
            # For text fields
            try:
                doc.fill_textfield(field_name, str(value))
            except:
                pass
                
            # For other field types (checkboxes, radio buttons, etc.)
            try:
                widgets = []
                for page in doc:
                    for widget in page.widgets():
                        if widget.field_name == field_name:
                            widgets.append(widget)
                
                if widgets:
                    for widget in widgets:
                        if widget.field_type_string == "CheckBox":
                            widget.field_value = value in (True, "Yes", "yes", "true", "True", "X", "x", "on", "1")
                        elif widget.field_type_string == "Radio":
                            widget.field_value = value
                        elif widget.field_type_string == "ListBox" or widget.field_type_string == "ComboBox":
                            widget.field_value = value
                            
                        widget.update()
            except:
                pass
        
        # Save filled PDF
        doc.save(output_path)
        doc.close()
        
        return {
            "success": True,
            "message": f"Form filled and saved to {output_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PDF Finder MCP Server")
    parser.add_argument("paths", nargs="+", help="Base paths to search for PDF files")
    args = parser.parse_args()
    
    # Store base paths globally
    BASE_PATHS = args.paths
    
    # Run the server
    mcp.run()