from celestial import normalize_extension as _normalize_extension

PDF_FILTERS = (
    ("com.sun.star.text.GenericTextDocument", "writer_pdf_Export"),
    ("com.sun.star.text.WebDocument", "writer_web_pdf_Export"),
    ("com.sun.star.sheet.SpreadsheetDocument", "calc_pdf_Export"),
    ("com.sun.star.presentation.PresentationDocument", "impress_pdf_Export"),
    ("com.sun.star.drawing.DrawingDocument", "draw_pdf_Export"),
)


def normalize_extension(extension):
    if extension == '*':
        return None
    return _normalize_extension(extension)
