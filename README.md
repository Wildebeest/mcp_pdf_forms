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

## Command Line Tool

After installation, you can use the `mcp-pdf-forms` command to start the server:

```bash
# Start the server with one or more directories to scan for PDFs
mcp-pdf-forms examples
```

You can also add it to Claude Code as an MCP:

```bash
claude mcp add pdf-forms mcp-pdf-forms .
```
## Usage

Once installed, you can use the package to work with PDF forms. The package provides tools through the MCP interface.

### PDF Discovery Tool

The PDF Discovery tool helps you find PDF files across specified directories.

- **Input**: Directory paths to search for PDFs
- **Output**: List of PDF files found in the specified directories
- **Usage**: Use this to quickly locate all PDF files in your project or specified folders

### Form Field Extraction Tool

The Form Field Extraction tool extracts information about all form fields in a PDF document.

- **Input**: Path to a PDF file
- **Output**: Detailed information about each form field including field name, type, position, and other properties
- **Usage**: Use this to analyze form structure and understand the fields available for filling

### Field Highlight Visualization Tool

The Field Highlight tool creates a visual representation of form fields in the PDF.

- **Input**: Path to a PDF file
- **Output**: Modified PDF with all form fields highlighted for easy identification
- **Usage**: Use this to visually inspect the layout and position of form fields in your document

## Libraries Used

- [MCP](https://github.com/llama-index-ai/mcp) - Machine Conversation Protocol framework
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - Python bindings for MuPDF, a high-performance PDF library

## License

MIT
