from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import os
import argparse
import re
import fitz  # PyMuPDF
import io
from PIL import Image as PILImage, ImageDraw

from mcp.server.fastmcp import FastMCP, Image

# Create a named server
mcp = FastMCP("PDF Forms", dependencies=["pymupdf", "pillow"])

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

        # Get form fields using widget iteration
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
                        "field_type_id": field_type,
                    }

        doc.close()
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def highlight_form_field(pdf_path: str, field_name: str) -> Image:
    """
    Generate an image with the specified form field highlighted with a red box

    Args:
        pdf_path: Path to the PDF file
        field_name: Name of the form field to highlight

    Returns:
        Image of the page with the field highlighted
    """
    try:
        doc = fitz.open(pdf_path)

        # Find the field and its page
        field_found = False
        field_page = None
        field_rect = None

        for page_num, page in enumerate(doc):
            for widget in page.widgets():
                if widget.field_name == field_name:
                    field_found = True
                    field_page = page
                    field_rect = widget.rect
                    break
            if field_found:
                break

        if not field_found:
            raise ValueError(f"Field '{field_name}' not found in the document")

        # Render the page as an image
        zoom = 2  # higher zoom for better quality
        mat = fitz.Matrix(zoom, zoom)
        pix = field_page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Draw red rectangle around the form field
        draw = ImageDraw.Draw(img)

        # Scale rectangle coordinates according to zoom factor
        rect = (
            field_rect.x0 * zoom,
            field_rect.y0 * zoom,
            field_rect.x1 * zoom,
            field_rect.y1 * zoom,
        )

        # Draw rectangle with 3-pixel width
        for i in range(3):
            draw.rectangle(
                (rect[0] - i, rect[1] - i, rect[2] + i, rect[3] + i), outline="red"
            )

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

        doc.close()

        # Return MCP Image object
        return Image(data=img_bytes, format="png")
    except Exception as e:
        raise Exception(f"Error highlighting form field: {str(e)}")


@mcp.tool()
def render_pdf_page(pdf_path: str, page_num: int = 0, zoom: float = 2.0) -> Image:
    """
    Generate an image of a PDF page without any highlighting
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number to render (0-indexed)
        zoom: Zoom factor for rendering (higher values for better quality)
        
    Returns:
        Image of the specified page
    """
    try:
        doc = fitz.open(pdf_path)
        
        # Check if page number is valid
        if page_num < 0 or page_num >= len(doc):
            raise ValueError(f"Page number {page_num} is out of range (0-{len(doc)-1})")
            
        # Get the requested page
        page = doc[page_num]
        
        # Render the page as an image
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        
        doc.close()
        
        # Return MCP Image object
        return Image(data=img_bytes, format="png")
    except Exception as e:
        raise Exception(f"Error rendering PDF page: {str(e)}")


@mcp.tool()
def extract_text(pdf_path: str, start_page: Optional[int] = None, end_page: Optional[int] = None) -> Union[str, Dict[int, str]]:
    """
    Extract text from PDF pages
    
    Args:
        pdf_path: Path to the PDF file
        start_page: Page number to start extraction (0-indexed). If None, starts from first page.
        end_page: Page number to end extraction (0-indexed, inclusive). If None, ends at start_page if specified, otherwise extracts all pages.
        
    Returns:
        If extracting a single page: string containing the page text
        If extracting multiple pages: dictionary mapping page numbers to page text
    """
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        # Validate page parameters
        if start_page is not None and (start_page < 0 or start_page >= total_pages):
            raise ValueError(f"Start page {start_page} is out of range (0-{total_pages-1})")
            
        if end_page is not None and (end_page < 0 or end_page >= total_pages):
            raise ValueError(f"End page {end_page} is out of range (0-{total_pages-1})")
            
        # Set defaults if parameters are None
        if start_page is None:
            start_page = 0
            
        if end_page is None:
            if start_page is not None:
                end_page = start_page
            else:
                end_page = total_pages - 1
                
        # Ensure start_page <= end_page
        if start_page > end_page:
            start_page, end_page = end_page, start_page
        
        # Extract text
        if start_page == end_page:
            # Single page extraction
            page = doc[start_page]
            text = page.get_text()
            doc.close()
            return text
        else:
            # Multiple page extraction
            result = {}
            for page_num in range(start_page, end_page + 1):
                page = doc[page_num]
                result[page_num] = page.get_text()
            
            doc.close()
            return result
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")


@mcp.tool()
def search_text(pdf_path: str, pattern: str, case_sensitive: bool = False, start_page: Optional[int] = None, end_page: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Search for text pattern in a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        pattern: Regular expression pattern to search for
        case_sensitive: Whether to perform case-sensitive matching
        start_page: Page number to start search (0-indexed). If None, starts from first page.
        end_page: Page number to end search (0-indexed, inclusive). If None, searches all pages.
        
    Returns:
        List of matches with page number, match text, and context
    """
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        # Validate page parameters
        if start_page is not None and (start_page < 0 or start_page >= total_pages):
            raise ValueError(f"Start page {start_page} is out of range (0-{total_pages-1})")
            
        if end_page is not None and (end_page < 0 or end_page >= total_pages):
            raise ValueError(f"End page {end_page} is out of range (0-{total_pages-1})")
            
        # Set defaults if parameters are None
        if start_page is None:
            start_page = 0
            
        if end_page is None:
            end_page = total_pages - 1
            
        # Ensure start_page <= end_page
        if start_page > end_page:
            start_page, end_page = end_page, start_page
        
        # Compile regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
        
        # List to store matches
        matches = []
        
        # Character context window
        context_size = 50
        
        # Search pages
        for page_num in range(start_page, end_page + 1):
            page = doc[page_num]
            text = page.get_text()
            
            # Find all matches in the page text
            for match in regex.finditer(text):
                start_pos = match.start()
                end_pos = match.end()
                match_text = match.group()
                
                # Extract context around match
                context_start = max(0, start_pos - context_size)
                context_end = min(len(text), end_pos + context_size)
                
                # Get text before and after match
                before = text[context_start:start_pos]
                after = text[end_pos:context_end]
                
                # Add match information to results
                matches.append({
                    "page": page_num,
                    "match": match_text,
                    "context": f"...{before}{match_text}{after}...",
                    "position": {
                        "start": start_pos,
                        "end": end_pos
                    }
                })
        
        doc.close()
        return matches
    except Exception as e:
        raise Exception(f"Error searching text: {str(e)}")




def start_server(paths=None):
    """Start the MCP PDF Forms server with the specified paths"""
    global BASE_PATHS
    if paths:
        BASE_PATHS = paths
    mcp.run()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PDF Forms MCP Server")
    parser.add_argument("paths", nargs="+", help="Base paths to search for PDF files")
    args = parser.parse_args()

    # Store base paths globally
    BASE_PATHS = args.paths

    # Run the server
    start_server()