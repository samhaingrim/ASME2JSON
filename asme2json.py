#!/usr/bin/env python
#
# Convert ASME Code Books From PDF to JSON

import argparse
import logging
import json
import re
import fitz
import time

# Set start time for total execution calculation
startTime = time.time()

# Set up logger
logging.basicConfig(
format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

def is_bold(span):
    return "Bold" in span["font"]

def extract_sections_and_codes(pdf_file):
    doc = fitz.open(pdf_file)
    sections_and_codes = []

    current_section = ""
    current_section_title = ""
    current_code = ""
    doc_pages = len(doc)

    logger.info("Parsing " + pdf_file)
    for i in range(0, doc_pages):     
        page = doc.load_page(i)
        logger.info("parsing page " + i.__str__() + " of " + doc_pages.__str__())
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]

        # Process each block of text
        for block in blocks:
            if block["type"] == 0:
                for line in block["lines"]:
                    spans = line["spans"]

                    # Search for SECTION and possible SECTION_TITLE in the first span of the line
                    first_span_text = spans[0]["text"]
                    match = re.match(r"^\s*(\d+(\.\d+)*)\s+(.*)$", first_span_text)

                    if match and is_bold(spans[0]):
                        if current_section:
                            sections_and_codes.append({
                                "SECTION": current_section,
                                "SECTION_TITLE": current_section_title,
                                "CODE": current_code.strip(),
                            })

                        current_section = match.group(1)
                        current_section_title = ""
                        current_code = ""

                        # Check if the paragraph has a SECTION_TITLE (bold)
                        current_section_title = match.group(3).rstrip('.').strip()

                        # Check if the SECTION_TITLE is followed by CODE (not bold)
                        if len(spans) > 1 and not is_bold(spans[1]):
                            current_code = spans[1]["text"]
                    else:
                        for span in spans:
                            current_code += " " + span["text"]
    
    # Add the last section
    sections_and_codes.append({
        "SECTION": current_section,
        "SECTION_TITLE": current_section_title,
        "CODE": current_code.strip(),
    })
    
    return sections_and_codes

def main():
    parser = argparse.ArgumentParser(description='Convert ASME Code Books to JSON')
    parser.add_argument('--input', '-i', type=str, dest='pdf_input', required=True,
        help='ASME Code Book PDF Filename')
    parser.add_argument('--output', '-o', type=str, dest='json_output',
        help='JSON Output Filename')
    parser.add_argument('--verbose', '-v', dest='verbose', default=False, action='store_true',
        help='Verbose Console Output')
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.INFO)
    pdf_file = args.pdf_input
    if args.json_output is not None:
        json_file = args.json_output
    else:
        json_file = pdf_file + ".json"
    logger.info("Opening " + pdf_file)
    sections_and_codes = extract_sections_and_codes(pdf_file)
    logger.info("Writing output to " + json_file)
    with open(json_file, "w") as json_file:
        json.dump(sections_and_codes, json_file, indent=2)
    logger.info("Conversion complete, exiting.")
    # Execution time calculation
    executionTime = (time.time() - startTime)
    logger.info('Execution time in seconds: ' + str(executionTime))
    exit(0)

if __name__ == "__main__":
    main()
