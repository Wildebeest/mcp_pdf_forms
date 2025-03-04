# MCP PDF Toolkit

A PDF manipulation toolkit built with [MCP](https://github.com/llama-index-ai/mcp) and PyMuPDF.

## Features

- Find PDF files across multiple directories
- Extract form field information from PDF files
- Fill out PDF forms programmatically

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-pdf.git
cd mcp-pdf

# Install dependencies with uv
uv venv
uv add "mcp[cli]" pymupdf
```

## Server

The server component provides PDF-related tools via MCP's API:

```bash
# Start the server with one or more directories to scan for PDFs
python server.py /path/to/pdfs /another/path
```

## Client

The client provides a command-line interface to interact with the server:

```bash
# List all PDFs in the configured directories
python examples/client.py --list

# Filter PDFs by a specific string
python examples/client.py --list --filter "invoice"

# Extract form fields from a PDF
python examples/client.py --form-fields /path/to/form.pdf

# Fill a PDF form
python examples/client.py --fill-form /path/to/form.pdf --output /path/to/output.pdf --data '{"field1": "value1", "field2": "value2"}'

# Fill a PDF form using a JSON file
python examples/client.py --fill-form /path/to/form.pdf --output /path/to/output.pdf --data /path/to/data.json
```

## Libraries Used

- [MCP](https://github.com/llama-index-ai/mcp) - Machine Conversation Protocol framework
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - Python bindings for MuPDF, a high-performance PDF library

## License

MIT