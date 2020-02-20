LIBREOFFICE_DOC_FAMILIES = [
    "TextDocument",
    "WebDocument",
    "Spreadsheet",
    "Presentation",
    "Graphics"
]

LIBREOFFICE_IMPORT_TYPES = {
    "docx": {
        "FilterName": "MS Word 2007 XML"
    },
    "pdf": {
        "FilterName": "PDF - Portable Document Format"
    },
    "jpg": {
        "FilterName": "JPEG - Joint Photographic Experts Group"
    },
    "html": {
        "FilterName": "HTML Document"
    },
    "odp": {
        "FilterName": "OpenDocument Presentation (Flat XML)"
    },
    "pptx": {
        "FilterName": "Microsoft PowerPoint 2007 XML"
    }
}

LIBREOFFICE_EXPORT_TYPES = {
    "pdf": {
        LIBREOFFICE_DOC_FAMILIES[0]: {"FilterName": "writer_pdf_Export"},
        LIBREOFFICE_DOC_FAMILIES[1]: {"FilterName": "writer_web_pdf_Export"},
        LIBREOFFICE_DOC_FAMILIES[2]: {"FilterName": "calc_pdf_Export"},
        LIBREOFFICE_DOC_FAMILIES[3]: {"FilterName": "impress_pdf_Export"},
        LIBREOFFICE_DOC_FAMILIES[4]: {"FilterName": "draw_pdf_Export"}
    },
    "jpg": {
        LIBREOFFICE_DOC_FAMILIES[3]: {"FilterName": "impress_jpg_Export"},
        LIBREOFFICE_DOC_FAMILIES[4]: {"FilterName": "draw_jpg_Export"}
    },
    "png": {
        LIBREOFFICE_DOC_FAMILIES[3]: {"FilterName": "impress_png_Export"},
        LIBREOFFICE_DOC_FAMILIES[4]: {"FilterName": "draw_png_Export"}
    },
    "html": {
        LIBREOFFICE_DOC_FAMILIES[0]: {"FilterName": "HTML (StarWriter)"},
        LIBREOFFICE_DOC_FAMILIES[1]: {"FilterName": "HTML"},
        LIBREOFFICE_DOC_FAMILIES[2]: {"FilterName": "HTML (StarCalc)"},
        LIBREOFFICE_DOC_FAMILIES[3]: {"FilterName": "impress_html_Export"},
        LIBREOFFICE_DOC_FAMILIES[4]: {"FilterName": "draw_html_Export"}
    },
    "docx": {
        LIBREOFFICE_DOC_FAMILIES[0]: {"FilterName": "MS Word 2007 XML"}
    },
    "odp": {
        LIBREOFFICE_DOC_FAMILIES[3]: {"FilterName": "impress8"}
    },
    "pptx": {
        LIBREOFFICE_DOC_FAMILIES[3]: {"FilterName": "Impress MS PowerPoint 2007 XML"}
    }
}