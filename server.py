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
        
        # Get form fields using widget iteration (compatible with PyMuPDF 1.25.3)
        for page in doc:
            for widget in page.widgets():
                field_name = widget.field_name
                field_value = widget.field_value
                field_type = widget.field_type
                field_type_name = widget.field_type_string
                
                # Only add if not already in results
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
    

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PDF Finder MCP Server")
    parser.add_argument("paths", nargs="+", help="Base paths to search for PDF files")
    args = parser.parse_args()
    
    # Store base paths globally
    BASE_PATHS = args.paths
    
    # Run the server
    mcp.run()