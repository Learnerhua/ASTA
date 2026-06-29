#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown to HTML and PDF converter
Usage: python md_converter.py input.md [-o output_name] [--html] [--pdf]
"""

import os
import sys
import argparse
import markdown
from datetime import datetime

# ==============================
# Time-stamped log function
# ==============================
def log_info(message):
    """Print log message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def md_to_html(md_file, output_file):
    """Convert markdown to HTML with beautiful styling and embedded images"""
    import base64
    import re
    
    # Define custom slugify function to preserve Chinese characters
    def slugify(text, sep):
        """Generate anchor ID from text, preserving Chinese characters"""
        # Replace spaces and special chars with the separator
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s-]+', sep, slug)
        slug = slug.strip(sep)
        return slug
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Get the directory of the markdown file to resolve relative image paths
    md_dir = os.path.dirname(os.path.abspath(md_file))
    
    # Function to embed images as base64
    def embed_image(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        
        # Resolve relative path
        if not os.path.isabs(img_path):
            img_abs_path = os.path.join(md_dir, img_path)
        else:
            img_abs_path = img_path
        
        # Check if file exists
        if os.path.exists(img_abs_path):
            try:
                with open(img_abs_path, 'rb') as img_file:
                    img_data = img_file.read()
                    # Determine mime type from extension
                    ext = os.path.splitext(img_abs_path)[1].lower()
                    if ext == '.png':
                        mime_type = 'image/png'
                    elif ext in ['.jpg', '.jpeg']:
                        mime_type = 'image/jpeg'
                    elif ext == '.gif':
                        mime_type = 'image/gif'
                    elif ext == '.svg':
                        mime_type = 'image/svg+xml'
                    else:
                        mime_type = 'image/png'
                    
                    b64_data = base64.b64encode(img_data).decode('utf-8')
                    return f'<img src="data:{mime_type};base64,{b64_data}" alt="{alt_text}">'
            except Exception as e:
                log_info(f"Warning: Could not embed image {img_path}")
        
        # Return original if file not found
        return match.group(0)
    
    # Embed images in markdown before conversion
    md_content_with_embedded = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', embed_image, md_content)
    
    # Convert markdown to HTML with proper anchor IDs
    # Use toc extension with custom slugify to preserve Chinese
    html_content = markdown.markdown(
        md_content_with_embedded,
        extensions=[
            'tables',
            'fenced_code',
            'toc'  # Table of Contents extension
        ],
        extension_configs={
            'toc': {
                'permalink': False,  # Don't add extra permalinks
                'title': 'Table of Contents',
                'slugify': slugify  # Use custom slugify to preserve Chinese
            }
        }
    )
    
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Report</title>
    <style>
        body {{
            font-family: 'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'Microsoft YaHei', 'SimHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Arial', sans-serif;
            line-height: 1.8;
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
            background-color: #fff;
        }}
        h1 {{
            font-size: 28px;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 30px;
        }}
        h2 {{
            font-size: 22px;
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 35px;
            margin-bottom: 20px;
        }}
        h3 {{
            font-size: 18px;
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e8f4f8;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #ecf0f1;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        strong {{
            color: #2c3e50;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            padding: 0;
            background-color: transparent;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #95a5a6;
            font-size: 12px;
        }}
    </style>
</head>
<body>
{html_content}
<div class="footer">
    Analysis Report | Generated by NCBI_alignment pipeline
</div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    return output_file

def md_to_pdf(md_file, output_file):
    """Convert markdown to PDF via HTML using WeasyPrint or wkhtmltopdf"""
    import subprocess
    import tempfile
    
    # OLD METHOD: Direct conversion using pandoc with xelatex
    # COMMENTED OUT - Chinese font issues
    # cmd = [
    #     'pandoc',
    #     md_file,
    #     '-o', output_file,
    #     '--pdf-engine=xelatex',
    #     '-V', 'documentclass=ctexart',
    #     '-V', 'geometry:margin=2cm',
    #     '-V', 'pagestyle=plain',
    #     '-V', 'mainfont=Noto Serif CJK SC'
    # ]
    # result = subprocess.run(cmd, capture_output=True, text=True)
    # if result.returncode != 0:
    #     print(f"PDF conversion error: {result.stderr}", file=sys.stderr)
    #     return None
    
    # NEW METHOD: Convert MD -> HTML -> PDF
    # Step 1: Generate HTML first
    html_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
    html_path = html_file.name
    html_file.close()
    
    # Generate HTML using md_to_html function
    md_to_html(md_file, html_path)
    
    # Step 2: Try WeasyPrint first (better for anchor links), then fallback to wkhtmltopdf
    try:
        from weasyprint import HTML as WeasyHTML
        # Generate PDF with bookmarks (outlines) for navigation
        html_doc = WeasyHTML(html_path)
        html_doc.write_pdf(output_file)
        log_info(f"PDF generated using WeasyPrint")
        result_returncode = 0
    except ImportError:
        # Fallback to wkhtmltopdf if WeasyPrint not available
        cmd = [
            'wkhtmltopdf',
            '--enable-local-file-access',
            '--load-error-handling', 'ignore',
            '--load-media-error-handling', 'ignore',
            '--enable-internal-links',  # Enable internal anchor links
            '--disable-external-links',  # Disable external links
            '--outline',  # Generate PDF outline/bookmarks
            '--outline-depth', '4',  # Outline depth (up to 4 levels)
            html_path,
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        result_returncode = result.returncode

        if result.returncode != 0:
            print(f"PDF conversion error: {result.stderr}", file=sys.stderr)
    
    # Clean up temporary HTML file
    try:
        os.unlink(html_path)
    except:
        pass
    
    if result_returncode != 0:
        return None
    
    return output_file

def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown to HTML and PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python md_converter.py input.md                              # Convert to HTML and PDF in input directory
  python md_converter.py input.md --html                      # Convert to HTML only
  python md_converter.py input.md --pdf                       # Convert to PDF only
  python md_converter.py input.md -o output_dir               # Output to specified directory
  python md_converter.py input.md -o results --html --pdf      # Full options
        '''
    )
    
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument('-o', '--output', help='Output directory path (default: same as input)')
    parser.add_argument('--html', action='store_true', help='Generate HTML only')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF only')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output directory and base name
    # -o specifies a directory path
    # Default output name uses input file name (without extension)
    input_basename = os.path.splitext(os.path.basename(args.input))[0]

    if args.output:
        output_dir = args.output
        output_base = input_basename
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.dirname(args.input) or '.'
        output_base = input_basename

    # Default: generate both HTML and PDF
    # If only --html specified, generate only HTML
    # If only --pdf specified, generate only PDF
    # If both or neither specified, generate both
    if args.html and not args.pdf:
        generate_html = True
        generate_pdf = False
    elif args.pdf and not args.html:
        generate_html = False
        generate_pdf = True
    else:
        generate_html = True
        generate_pdf = True

    # ==============================
    # Print parameter info
    # ==============================
    print("================================================================")
    print(f"Input file      : {args.input}")
    print(f"Output dir      : {output_dir}")
    print(f"Output format   : {'HTML' if generate_html and not generate_pdf else 'PDF' if generate_pdf and not generate_html else 'HTML + PDF'}")
    print("================================================================")

    results = []

    # Generate HTML
    if generate_html:
        html_file = os.path.join(output_dir, f"{output_base}.html")
        log_info(f"Converting to HTML: {html_file}")
        result = md_to_html(args.input, html_file)
        if result:
            log_info(f"HTML generated: {result}")
            results.append(('HTML', result))
        else:
            print(f"Error: HTML conversion failed", file=sys.stderr)

    # Generate PDF
    if generate_pdf:
        pdf_file = os.path.join(output_dir, f"{output_base}.pdf")
        log_info(f"Converting to PDF: {pdf_file}")
        result = md_to_pdf(args.input, pdf_file)
        if result:
            log_info(f"PDF generated: {result}")
            results.append(('PDF', result))
        else:
            print(f"Error: PDF conversion failed", file=sys.stderr)
            print(f"Note: Make sure WeasyPrint or wkhtmltopdf are installed", file=sys.stderr)

    # Summary
    log_info("Conversion completed")
    if not results:
        print("No files generated.", file=sys.stderr)

if __name__ == '__main__':
    main()
