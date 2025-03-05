from pathlib import Path
from typing import List, Optional, Dict, Any
import os
import argparse
import fitz  # PyMuPDF
import io
from PIL import Image as PILImage, ImageDraw

from mcp.server.fastmcp import FastMCP, Image

# Create a named server
mcp = FastMCP("PDF Finder", dependencies=["pymupdf", "pillow"])

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


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PDF Finder MCP Server")
    parser.add_argument("paths", nargs="+", help="Base paths to search for PDF files")
    args = parser.parse_args()

    # Store base paths globally
    BASE_PATHS = args.paths

    # Run the server
    mcp.run()
