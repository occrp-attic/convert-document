from celestial import normalize_extension

PDF_FILTERS = (
    ("com.sun.star.text.GenericTextDocument", "writer_pdf_Export"),
    ("com.sun.star.text.WebDocument", "writer_web_pdf_Export"),
    ("com.sun.star.sheet.SpreadsheetDocument", "calc_pdf_Export"),
    ("com.sun.star.presentation.PresentationDocument", "impress_pdf_Export"),
    ("com.sun.star.drawing.DrawingDocument", "draw_pdf_Export"),
)


def parse_extensions(extensions):
    if extensions is not None:
        for ext in extensions.split(' '):
            if ext == '*':
                continue
            ext = normalize_extension(ext)
            if ext is not None:
                yield ext
