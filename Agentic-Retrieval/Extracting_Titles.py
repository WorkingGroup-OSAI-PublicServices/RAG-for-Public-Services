# Extracting chapter and section titles from PDF files to understand document structure
# By feeding document structure to RAG agents it is possible to apply filters to optimize retrieval

# Dependencies
import pdfplumber
from collections import defaultdict

# Optional:
# Some pre-processing can be applied to PDF documents to facilitate retrieval
# [ADD YOU CODE FOR PDF PRE-PROCESSING HERE]


# The below part introduces custom logic for identifying chapter and section titles
# This part can be further customised depending the on needs (types and format of documents)

# Mandatory condition checks:
def is_uniform_text(line_word_sizes):
    """Check if the text in the line has a uniform font size."""
    return len(set(line_word_sizes)) == 1

def is_preceded_by_line_break(lines, line_index):
    """Check if the line is preceded by a line break."""
    return line_index == 0 or lines[line_index - 1].strip() == ""

def is_less_than_avg_word_density(words_per_line, avg_words_per_line):
    """Check if the number of words on the line is less than the average word density per line."""
    return words_per_line < avg_words_per_line

def is_not_longer_than_two_lines(line_index, lines):
    """Check if the text is not longer than two lines."""
    return line_index < len(lines) - 1 and len(lines[line_index].splitlines()) <= 2


# Optional condition checks:
def is_different_font(line_font_size, avg_font_size):
    """Check if the font size of the line is larger than the average font size."""
    return line_font_size > avg_font_size

def is_bold_or_italic(line_word_fonts):
    """Check if the line has bold or italic text."""
    return any("Bold" in font or "Italic" in font for font in line_word_fonts)

def is_all_caps(line):
    """Check if the line has all capital letters."""
    return line.isupper()

def has_no_punctuation_at_end(line):
    """Check if the line does not end with punctuation."""
    return line.strip()[-1] not in ".!?," if line.strip() else False

def is_followed_by_line_break(lines, line_index):
    """Check if the line is followed by a line break."""
    return line_index == len(lines) - 1 or lines[line_index + 1].strip() == ""


# Helper functions to calculate averages:
def calculate_avg_words_per_line(lines):
    """Calculate the average number of words per line for a list of lines."""
    total_words = sum(len(line.split()) for line in lines)
    total_lines = len(lines)
    return total_words / total_lines if total_lines else 0

def calculate_avg_font_size(words):
    """Calculate the average font size for the words on the page."""
    total_font_size = sum(word['size'] for word in words)
    num_words = len(words)
    return total_font_size / num_words if num_words else 0

# Title extraction logic
def extract_document_outline(pdf_path):
    document_outline = defaultdict(list)

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(extra_attrs=["size", "fontname"])
            lines = page.extract_text().splitlines()

            # Calculate averages for the page
            avg_font_size = calculate_avg_font_size(words)
            avg_words_per_line = calculate_avg_words_per_line(lines)

            for i, line in enumerate(lines):
                words_in_line = line.split()
                words_per_line = len(words_in_line)

                # Extract font sizes and font names for the current line
                line_word_sizes = [word['size'] for word in words if word['text'] in words_in_line]
                line_word_fonts = [word['fontname'] for word in words if word['text'] in words_in_line]

                # Skip empty lines
                if not words_per_line or not line_word_sizes:
                    continue

                line_font_size = max(line_word_sizes)  # Get the largest font size on the line

                # Mandatory conditions
                if (is_uniform_text(line_word_sizes) and
                    is_preceded_by_line_break(lines, i) and
                    is_less_than_avg_word_density(words_per_line, avg_words_per_line) and
                    is_not_longer_than_two_lines(i, lines)):

                    # Optional conditions
                    optional_conditions_met = [
                        is_different_font(line_font_size, avg_font_size),
                        is_bold_or_italic(line_word_fonts),
                        is_all_caps(line),
                        has_no_punctuation_at_end(line),
                        is_followed_by_line_break(lines, i)
                    ]

                    # Title is classified if at least two optional conditions are met
                    if sum(optional_conditions_met) >= 2:
                        document_outline[line].append(page_num)

    return document_outline

# Example usage
pdf_path = 'saple_file.pdf' # Specify path to your document
document_outline = extract_document_outline(pdf_path)

# Print document outline
for title, pages in document_outline.items():
    print(f"Title: {title}, Pages: {pages}")