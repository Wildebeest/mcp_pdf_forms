from pathlib import Path
from typing import List, Optional
import os
import argparse

from mcp.server.fastmcp import FastMCP

# Create a named server
mcp = FastMCP("PDF Finder", dependencies=["mcp[cli]"])

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

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PDF Finder MCP Server")
    parser.add_argument("paths", nargs="+", help="Base paths to search for PDF files")
    args = parser.parse_args()
    
    # Store base paths globally
    BASE_PATHS = args.paths
    
    # Run the server
    mcp.run()