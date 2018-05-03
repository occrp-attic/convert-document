# lifted from https://github.com/dagwieers/unoconv/blob/master/unoconv
# GPL 2.0


class FmtList:
    def __init__(self):
        self.list = []

    def add(self, doctype, name, extension, summary, filter):
        self.list.append(Fmt(doctype, name, extension, summary, filter))

    def byname(self, name):
        ret = []
        for fmt in self.list:
            if fmt.name == name:
                ret.append(fmt)
        return ret

    def byextension(self, extension):
        ret = []
        for fmt in self.list:
            if os.extsep + fmt.extension == extension:
                ret.append(fmt)
        return ret

    def bydoctype(self, doctype, name):
        ret = []
        for fmt in self.list:
            if fmt.name == name and fmt.doctype == doctype:
                ret.append(fmt)
        return ret

    def display(self, doctype):
        print("The following list of %s formats are currently available:\n" % doctype, file=sys.stderr)
        for fmt in self.list:
            if fmt.doctype == doctype:
                print("  %-8s - %s" % (fmt.name, fmt), file=sys.stderr)
        print(file=sys.stderr)

fmts = FmtList()

### TextDocument
fmts.add('document', 'bib', 'bib', 'BibTeX', 'BibTeX_Writer') ### 22
fmts.add('document', 'doc', 'doc', 'Microsoft Word 97/2000/XP', 'MS Word 97') ### 29
fmts.add('document', 'doc6', 'doc', 'Microsoft Word 6.0', 'MS WinWord 6.0') ### 24
fmts.add('document', 'doc95', 'doc', 'Microsoft Word 95', 'MS Word 95') ### 28
fmts.add('document', 'docbook', 'xml', 'DocBook', 'DocBook File') ### 39
fmts.add('document', 'docx', 'docx', 'Microsoft Office Open XML', 'Office Open XML Text')
fmts.add('document', 'docx7', 'docx', 'Microsoft Office Open XML', 'MS Word 2007 XML')
fmts.add('document', 'fodt', 'fodt', 'OpenDocument Text (Flat XML)', 'OpenDocument Text Flat XML')
fmts.add('document', 'html', 'html', 'HTML Document (OpenOffice.org Writer)', 'HTML (StarWriter)') ### 3
fmts.add('document', 'latex', 'ltx', 'LaTeX 2e', 'LaTeX_Writer') ### 31
fmts.add('document', 'mediawiki', 'txt', 'MediaWiki', 'MediaWiki')
fmts.add('document', 'odt', 'odt', 'ODF Text Document', 'writer8') ### 10
fmts.add('document', 'ooxml', 'xml', 'Microsoft Office Open XML', 'MS Word 2003 XML') ### 11
fmts.add('document', 'ott', 'ott', 'Open Document Text', 'writer8_template') ### 21
fmts.add('document', 'pdb', 'pdb', 'AportisDoc (Palm)', 'AportisDoc Palm DB')
fmts.add('document', 'pdf', 'pdf', 'Portable Document Format', 'writer_pdf_Export') ### 18
fmts.add('document', 'psw', 'psw', 'Pocket Word', 'PocketWord File')
fmts.add('document', 'rtf', 'rtf', 'Rich Text Format', 'Rich Text Format') ### 16
fmts.add('document', 'sdw', 'sdw', 'StarWriter 5.0', 'StarWriter 5.0') ### 23
fmts.add('document', 'sdw4', 'sdw', 'StarWriter 4.0', 'StarWriter 4.0') ### 2
fmts.add('document', 'sdw3', 'sdw', 'StarWriter 3.0', 'StarWriter 3.0') ### 20
fmts.add('document', 'stw', 'stw', 'Open Office.org 1.0 Text Document Template', 'writer_StarOffice_XML_Writer_Template') ### 9
fmts.add('document', 'sxw', 'sxw', 'Open Office.org 1.0 Text Document', 'StarOffice XML (Writer)') ### 1
fmts.add('document', 'text', 'txt', 'Text Encoded', 'Text (encoded)') ### 26
fmts.add('document', 'txt', 'txt', 'Text', 'Text') ### 34
fmts.add('document', 'uot', 'uot', 'Unified Office Format text','UOF text') ### 27
fmts.add('document', 'vor', 'vor', 'StarWriter 5.0 Template', 'StarWriter 5.0 Vorlage/Template') ### 6
fmts.add('document', 'vor4', 'vor', 'StarWriter 4.0 Template', 'StarWriter 4.0 Vorlage/Template') ### 5
fmts.add('document', 'vor3', 'vor', 'StarWriter 3.0 Template', 'StarWriter 3.0 Vorlage/Template') ### 4
fmts.add('document', 'wps', 'wps', 'Microsoft Works', 'MS_Works')
fmts.add('document', 'xhtml', 'html', 'XHTML Document', 'XHTML Writer File') ### 33

### WebDocument
fmts.add('web', 'etext', 'txt', 'Text Encoded (OpenOffice.org Writer/Web)', 'Text (encoded) (StarWriter/Web)') ### 14
fmts.add('web', 'html10', 'html', 'OpenOffice.org 1.0 HTML Template', 'writer_web_StarOffice_XML_Writer_Web_Template') ### 11
fmts.add('web', 'html', 'html', 'HTML Document', 'HTML') ### 2
fmts.add('web', 'html', 'html', 'HTML Document Template', 'writerweb8_writer_template') ### 13
fmts.add('web', 'mediawiki', 'txt', 'MediaWiki', 'MediaWiki_Web') ### 9
fmts.add('web', 'pdf', 'pdf', 'PDF - Portable Document Format', 'writer_web_pdf_Export') ### 10
fmts.add('web', 'sdw3', 'sdw', 'StarWriter 3.0 (OpenOffice.org Writer/Web)', 'StarWriter 3.0 (StarWriter/Web)') ### 3
fmts.add('web', 'sdw4', 'sdw', 'StarWriter 4.0 (OpenOffice.org Writer/Web)', 'StarWriter 4.0 (StarWriter/Web)') ### 4
fmts.add('web', 'sdw', 'sdw', 'StarWriter 5.0 (OpenOffice.org Writer/Web)', 'StarWriter 5.0 (StarWriter/Web)') ### 5
fmts.add('web', 'txt', 'txt', 'OpenOffice.org Text (OpenOffice.org Writer/Web)', 'writerweb8_writer') ### 12
fmts.add('web', 'text10', 'txt', 'OpenOffice.org 1.0 Text Document (OpenOffice.org Writer/Web)', 'writer_web_StarOffice_XML_Writer') ### 15
fmts.add('web', 'text', 'txt', 'Text (OpenOffice.org Writer/Web)', 'Text (StarWriter/Web)') ### 8
fmts.add('web', 'vor4', 'vor', 'StarWriter/Web 4.0 Template', 'StarWriter/Web 4.0 Vorlage/Template') ### 6
fmts.add('web', 'vor', 'vor', 'StarWriter/Web 5.0 Template', 'StarWriter/Web 5.0 Vorlage/Template') ### 7

### Spreadsheet
fmts.add('spreadsheet', 'csv', 'csv', 'Text CSV', 'Text - txt - csv (StarCalc)') ### 16
fmts.add('spreadsheet', 'dbf', 'dbf', 'dBASE', 'dBase') ### 22
fmts.add('spreadsheet', 'dif', 'dif', 'Data Interchange Format', 'DIF') ### 5
fmts.add('spreadsheet', 'fods', 'fods', 'OpenDocument Spreadsheet (Flat XML)', 'OpenDocument Spreadsheet Flat XML')
fmts.add('spreadsheet', 'html', 'html', 'HTML Document (OpenOffice.org Calc)', 'HTML (StarCalc)') ### 7
fmts.add('spreadsheet', 'ods', 'ods', 'ODF Spreadsheet', 'calc8') ### 15
fmts.add('spreadsheet', 'ooxml', 'xml', 'Microsoft Excel 2003 XML', 'MS Excel 2003 XML') ### 23
fmts.add('spreadsheet', 'ots', 'ots', 'ODF Spreadsheet Template', 'calc8_template') ### 14
fmts.add('spreadsheet', 'pdf', 'pdf', 'Portable Document Format', 'calc_pdf_Export') ### 34
fmts.add('spreadsheet', 'pxl', 'pxl', 'Pocket Excel', 'Pocket Excel')
fmts.add('spreadsheet', 'sdc', 'sdc', 'StarCalc 5.0', 'StarCalc 5.0') ### 31
fmts.add('spreadsheet', 'sdc4', 'sdc', 'StarCalc 4.0', 'StarCalc 4.0') ### 11
fmts.add('spreadsheet', 'sdc3', 'sdc', 'StarCalc 3.0', 'StarCalc 3.0') ### 29
fmts.add('spreadsheet', 'slk', 'slk', 'SYLK', 'SYLK') ### 35
fmts.add('spreadsheet', 'stc', 'stc', 'OpenOffice.org 1.0 Spreadsheet Template', 'calc_StarOffice_XML_Calc_Template') ### 2
fmts.add('spreadsheet', 'sxc', 'sxc', 'OpenOffice.org 1.0 Spreadsheet', 'StarOffice XML (Calc)') ### 3
fmts.add('spreadsheet', 'uos', 'uos', 'Unified Office Format spreadsheet', 'UOF spreadsheet') ### 9
fmts.add('spreadsheet', 'vor3', 'vor', 'StarCalc 3.0 Template', 'StarCalc 3.0 Vorlage/Template') ### 18
fmts.add('spreadsheet', 'vor4', 'vor', 'StarCalc 4.0 Template', 'StarCalc 4.0 Vorlage/Template') ### 19
fmts.add('spreadsheet', 'vor', 'vor', 'StarCalc 5.0 Template', 'StarCalc 5.0 Vorlage/Template') ### 20
fmts.add('spreadsheet', 'xhtml', 'xhtml', 'XHTML', 'XHTML Calc File') ### 26
fmts.add('spreadsheet', 'xls', 'xls', 'Microsoft Excel 97/2000/XP', 'MS Excel 97') ### 12
fmts.add('spreadsheet', 'xls5', 'xls', 'Microsoft Excel 5.0', 'MS Excel 5.0/95') ### 8
fmts.add('spreadsheet', 'xls95', 'xls', 'Microsoft Excel 95', 'MS Excel 95') ### 10
fmts.add('spreadsheet', 'xlt', 'xlt', 'Microsoft Excel 97/2000/XP Template', 'MS Excel 97 Vorlage/Template') ### 6
fmts.add('spreadsheet', 'xlt5', 'xlt', 'Microsoft Excel 5.0 Template', 'MS Excel 5.0/95 Vorlage/Template') ### 28
fmts.add('spreadsheet', 'xlt95', 'xlt', 'Microsoft Excel 95 Template', 'MS Excel 95 Vorlage/Template') ### 21
fmts.add('spreadsheet', 'xlsx', 'xlsx', 'Microsoft Excel 2007/2010 XML', 'Calc MS Excel 2007 XML')

### Graphics
fmts.add('graphics', 'bmp', 'bmp', 'Windows Bitmap', 'draw_bmp_Export') ### 21
fmts.add('graphics', 'emf', 'emf', 'Enhanced Metafile', 'draw_emf_Export') ### 15
fmts.add('graphics', 'eps', 'eps', 'Encapsulated PostScript', 'draw_eps_Export') ### 48
fmts.add('graphics', 'fodg', 'fodg', 'OpenDocument Drawing (Flat XML)', 'OpenDocument Drawing Flat XML')
fmts.add('graphics', 'gif', 'gif', 'Graphics Interchange Format', 'draw_gif_Export') ### 30
fmts.add('graphics', 'html', 'html', 'HTML Document (OpenOffice.org Draw)', 'draw_html_Export') ### 37
fmts.add('graphics', 'jpg', 'jpg', 'Joint Photographic Experts Group', 'draw_jpg_Export') ### 3
fmts.add('graphics', 'met', 'met', 'OS/2 Metafile', 'draw_met_Export') ### 43
fmts.add('graphics', 'odd', 'odd', 'OpenDocument Drawing', 'draw8') ### 6
fmts.add('graphics', 'otg', 'otg', 'OpenDocument Drawing Template', 'draw8_template') ### 20
fmts.add('graphics', 'pbm', 'pbm', 'Portable Bitmap', 'draw_pbm_Export') ### 14
fmts.add('graphics', 'pct', 'pct', 'Mac Pict', 'draw_pct_Export') ### 41
fmts.add('graphics', 'pdf', 'pdf', 'Portable Document Format', 'draw_pdf_Export') ### 28
fmts.add('graphics', 'pgm', 'pgm', 'Portable Graymap', 'draw_pgm_Export') ### 11
fmts.add('graphics', 'png', 'png', 'Portable Network Graphic', 'draw_png_Export') ### 2
fmts.add('graphics', 'ppm', 'ppm', 'Portable Pixelmap', 'draw_ppm_Export') ### 5
fmts.add('graphics', 'ras', 'ras', 'Sun Raster Image', 'draw_ras_Export') ## 31
fmts.add('graphics', 'std', 'std', 'OpenOffice.org 1.0 Drawing Template', 'draw_StarOffice_XML_Draw_Template') ### 53
fmts.add('graphics', 'svg', 'svg', 'Scalable Vector Graphics', 'draw_svg_Export') ### 50
fmts.add('graphics', 'svm', 'svm', 'StarView Metafile', 'draw_svm_Export') ### 55
fmts.add('graphics', 'swf', 'swf', 'Macromedia Flash (SWF)', 'draw_flash_Export') ### 23
fmts.add('graphics', 'sxd', 'sxd', 'OpenOffice.org 1.0 Drawing', 'StarOffice XML (Draw)') ### 26
fmts.add('graphics', 'sxd3', 'sxd', 'StarDraw 3.0', 'StarDraw 3.0') ### 40
fmts.add('graphics', 'sxd5', 'sxd', 'StarDraw 5.0', 'StarDraw 5.0') ### 44
fmts.add('graphics', 'sxw', 'sxw', 'StarOffice XML (Draw)', 'StarOffice XML (Draw)')
fmts.add('graphics', 'tiff', 'tiff', 'Tagged Image File Format', 'draw_tif_Export') ### 13
fmts.add('graphics', 'vor', 'vor', 'StarDraw 5.0 Template', 'StarDraw 5.0 Vorlage') ### 36
fmts.add('graphics', 'vor3', 'vor', 'StarDraw 3.0 Template', 'StarDraw 3.0 Vorlage') ### 35
fmts.add('graphics', 'wmf', 'wmf', 'Windows Metafile', 'draw_wmf_Export') ### 8
fmts.add('graphics', 'xhtml', 'xhtml', 'XHTML', 'XHTML Draw File') ### 45
fmts.add('graphics', 'xpm', 'xpm', 'X PixMap', 'draw_xpm_Export') ### 19

### Presentation
fmts.add('presentation', 'bmp', 'bmp', 'Windows Bitmap', 'impress_bmp_Export') ### 15
fmts.add('presentation', 'emf', 'emf', 'Enhanced Metafile', 'impress_emf_Export') ### 16
fmts.add('presentation', 'eps', 'eps', 'Encapsulated PostScript', 'impress_eps_Export') ### 17
fmts.add('presentation', 'fodp', 'fodp', 'OpenDocument Presentation (Flat XML)', 'OpenDocument Presentation Flat XML')
fmts.add('presentation', 'gif', 'gif', 'Graphics Interchange Format', 'impress_gif_Export') ### 18
fmts.add('presentation', 'html', 'html', 'HTML Document (OpenOffice.org Impress)', 'impress_html_Export') ### 43
fmts.add('presentation', 'jpg', 'jpg', 'Joint Photographic Experts Group', 'impress_jpg_Export') ### 19
fmts.add('presentation', 'met', 'met', 'OS/2 Metafile', 'impress_met_Export') ### 20
fmts.add('presentation', 'odg', 'odg', 'ODF Drawing (Impress)', 'impress8_draw') ### 29
fmts.add('presentation', 'odp', 'odp', 'ODF Presentation', 'impress8') ### 9
fmts.add('presentation', 'otp', 'otp', 'ODF Presentation Template', 'impress8_template') ### 38
fmts.add('presentation', 'pbm', 'pbm', 'Portable Bitmap', 'impress_pbm_Export') ### 21
fmts.add('presentation', 'pct', 'pct', 'Mac Pict', 'impress_pct_Export') ### 22
fmts.add('presentation', 'pdf', 'pdf', 'Portable Document Format', 'impress_pdf_Export') ### 23
fmts.add('presentation', 'pgm', 'pgm', 'Portable Graymap', 'impress_pgm_Export') ### 24
fmts.add('presentation', 'png', 'png', 'Portable Network Graphic', 'impress_png_Export') ### 25
fmts.add('presentation', 'potm', 'potm', 'Microsoft PowerPoint 2007/2010 XML Template', 'Impress MS PowerPoint 2007 XML Template')
fmts.add('presentation', 'pot', 'pot', 'Microsoft PowerPoint 97/2000/XP Template', 'MS PowerPoint 97 Vorlage') ### 3
fmts.add('presentation', 'ppm', 'ppm', 'Portable Pixelmap', 'impress_ppm_Export') ### 26
fmts.add('presentation', 'pptx', 'pptx', 'Microsoft PowerPoint 2007/2010 XML', 'Impress MS PowerPoint 2007 XML') ### 36
fmts.add('presentation', 'pps', 'pps', 'Microsoft PowerPoint 97/2000/XP (Autoplay)', 'MS PowerPoint 97 Autoplay') ### 36
fmts.add('presentation', 'ppt', 'ppt', 'Microsoft PowerPoint 97/2000/XP', 'MS PowerPoint 97') ### 36
fmts.add('presentation', 'pwp', 'pwp', 'PlaceWare', 'placeware_Export') ### 30
fmts.add('presentation', 'ras', 'ras', 'Sun Raster Image', 'impress_ras_Export') ### 27
fmts.add('presentation', 'sda', 'sda', 'StarDraw 5.0 (OpenOffice.org Impress)', 'StarDraw 5.0 (StarImpress)') ### 8
fmts.add('presentation', 'sdd', 'sdd', 'StarImpress 5.0', 'StarImpress 5.0') ### 6
fmts.add('presentation', 'sdd3', 'sdd', 'StarDraw 3.0 (OpenOffice.org Impress)', 'StarDraw 3.0 (StarImpress)') ### 42
fmts.add('presentation', 'sdd4', 'sdd', 'StarImpress 4.0', 'StarImpress 4.0') ### 37
fmts.add('presentation', 'sxd', 'sxd', 'OpenOffice.org 1.0 Drawing (OpenOffice.org Impress)', 'impress_StarOffice_XML_Draw') ### 31
fmts.add('presentation', 'sti', 'sti', 'OpenOffice.org 1.0 Presentation Template', 'impress_StarOffice_XML_Impress_Template') ### 5
fmts.add('presentation', 'svg', 'svg', 'Scalable Vector Graphics', 'impress_svg_Export') ### 14
fmts.add('presentation', 'svm', 'svm', 'StarView Metafile', 'impress_svm_Export') ### 13
fmts.add('presentation', 'swf', 'swf', 'Macromedia Flash (SWF)', 'impress_flash_Export') ### 34
fmts.add('presentation', 'sxi', 'sxi', 'OpenOffice.org 1.0 Presentation', 'StarOffice XML (Impress)') ### 41
fmts.add('presentation', 'tiff', 'tiff', 'Tagged Image File Format', 'impress_tif_Export') ### 12
fmts.add('presentation', 'uop', 'uop', 'Unified Office Format presentation', 'UOF presentation') ### 4
fmts.add('presentation', 'vor', 'vor', 'StarImpress 5.0 Template', 'StarImpress 5.0 Vorlage') ### 40
fmts.add('presentation', 'vor3', 'vor', 'StarDraw 3.0 Template (OpenOffice.org Impress)', 'StarDraw 3.0 Vorlage (StarImpress)') ###1
fmts.add('presentation', 'vor4', 'vor', 'StarImpress 4.0 Template', 'StarImpress 4.0 Vorlage') ### 39
fmts.add('presentation', 'vor5', 'vor', 'StarDraw 5.0 Template (OpenOffice.org Impress)', 'StarDraw 5.0 Vorlage (StarImpress)') ### 2
fmts.add('presentation', 'wmf', 'wmf', 'Windows Metafile', 'impress_wmf_Export') ### 11
fmts.add('presentation', 'xhtml', 'xml', 'XHTML', 'XHTML Impress File') ### 33
fmts.add('presentation', 'xpm', 'xpm', 'X PixMap', 'impress_xpm_Export') ### 10
