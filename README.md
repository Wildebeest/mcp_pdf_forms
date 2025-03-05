# MCP PDF Forms

A PDF form manipulation toolkit built with [MCP](https://github.com/llama-index-ai/mcp) and PyMuPDF.

## Features

- Find PDF files across multiple directories
- Extract form field information from PDF files
- Visualize form fields in PDF documents

## Installation

```bash
# Install package from PyPI
pip install mcp_pdf_forms

# Or install from source
git clone https://github.com/Wildebeest/mcp_pdf_forms.git
cd mcp_pdf_forms
pip install -e .
```

## Server

The server component provides PDF-related tools via MCP's API:

```bash
# Start the server with one or more directories to scan for PDFs
uv run -m mcp_pdf_forms.server examples
```

## Usage

Once installed, you can use the package to work with PDF forms. The package provides both an API and a command-line interface.

```python
# Example API usage coming soon
```

## Libraries Used

- [MCP](https://github.com/llama-index-ai/mcp) - Machine Conversation Protocol framework
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - Python bindings for MuPDF, a high-performance PDF library

## License

MIT