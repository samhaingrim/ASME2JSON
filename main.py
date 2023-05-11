import json
import re
import fitz

def is_bold(span):
    return "Bold" in span["font"]

def extract_sections_and_codes(pdf_file, start_page, end_page):
    doc = fitz.open(pdf_file)
    sections_and_codes = []

    current_section = ""
    current_section_title = ""
    current_code = ""

    for i in range(start_page, end_page + 1):
        page = doc.load_page(i)
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
    pdf_file = "A17-3_2015.pdf"
    start_page = 0  # PDF page numbers start from 0, so subtract 1 from the provided page number
    end_page = 100

    sections_and_codes = extract_sections_and_codes(pdf_file, start_page, end_page)

    with open("173-2015.json", "w") as json_file:
        json.dump(sections_and_codes, json_file, indent=2)

if __name__ == "__main__":
    main()
