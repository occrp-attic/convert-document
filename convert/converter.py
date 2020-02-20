import os
import uno
import time
import logging
import subprocess
from threading import Timer
from com.sun.star.beans import PropertyValue
from com.sun.star.lang import DisposedException
from com.sun.star.lang import IllegalArgumentException
from com.sun.star.connection import NoConnectException
from .document_types import *

CONNECTION = 'socket,host=localhost,port=2002;urp;StarOffice.ComponentContext'  # noqa
COMMAND = 'soffice --nologo --headless --nocrashreport --nodefault --nofirststartwizard --norestore --invisible --accept="%s"'  # noqa

log = logging.getLogger(__name__)


class ConversionFailure(Exception):
    pass


class SystemFailure(Exception):
    pass


class Converter(object):
    """Launch a background instance of LibreOffice and convert documents
    to PDF using it's filters.
    """
    OUT = '/tmp/output'
    PDF_FILTERS = (
        ('com.sun.star.text.GenericTextDocument', 'writer_pdf_Export'),
        ('com.sun.star.text.WebDocument', 'writer_web_pdf_Export'),
        ('com.sun.star.presentation.PresentationDocument', 'impress_pdf_Export'),  # noqa
        ('com.sun.star.drawing.DrawingDocument', 'draw_pdf_Export'),
    )

    def __init__(self):
        self.local_context = uno.getComponentContext()
        self.resolver = self._svc_create(self.local_context, 'com.sun.star.bridge.UnoUrlResolver')  # noqa
        self.process = None
        self.connect()

    def _svc_create(self, ctx, clazz):
        return ctx.ServiceManager.createInstanceWithContext(clazz, ctx)

    def terminate(self):
        # This gets executed in its own thread after timeout seconds.
        if self.process is None or self.process.poll() is not None:
            self.process.kill()
        log.error('Document conversion timed out.')
        os._exit(42)

    def connect(self):
        # Check if the LibreOffice process has an exit code
        if self.process is None or self.process.poll() is not None:
            log.info('Starting headless LibreOffice...')
            command = COMMAND % CONNECTION
            self.process = subprocess.Popen(command,
                                            shell=True,
                                            stdin=None,
                                            stdout=None,
                                            stderr=None)

        for attempt in range(12):
            try:
                context = self.resolver.resolve('uno:%s' % CONNECTION)
                return self._svc_create(context, 'com.sun.star.frame.Desktop')
            except NoConnectException:
                time.sleep(1)
        raise SystemFailure('Conversion timed out.')

    def convert_file(self, file_name, output_format, timeout):
        timer = Timer(timeout, self.terminate)
        timer.start()
        try:
            desktop = self.connect()
            if desktop is None:
                raise SystemFailure('Cannot connect to LibreOffice.')

            url = uno.systemPathToFileUrl(file_name)
            props = self.property_tuple({
                'Hidden': True,
                'MacroExecutionMode': 0,
                'ReadOnly': True,
                'Overwrite': True,
            })
            try:
                doc = desktop.loadComponentFromURL(url, '_blank', 0, props)
            except IllegalArgumentException:
                raise ConversionFailure('Cannot open document.')
            except DisposedException:
                raise SystemFailure('Bridge is disposed.')

            if doc is None:
                raise ConversionFailure('Cannot open document.')

            try:
                doc.ShowChanges = False
            except AttributeError:
                pass

            try:
                doc.refresh()
            except AttributeError:
                pass

            output_filename = "%s.%s" % (self.OUT, output_format)
            try:
                print("output_format", output_format)
                print("output_filename", output_filename)
                output_url = uno.systemPathToFileUrl(output_filename)
                print("output_url", output_url)
                prop = self.get_output_properties(doc, output_format)
                print('prop', prop)
                doc.storeToURL(output_url, prop)
                doc.dispose()
                doc.close(True)
                del doc
            except DisposedException:
                raise ConversionFailure('Cannot generate PDF.')

            stat = os.stat(output_filename)
            if stat.st_size == 0 or not os.path.exists(output_filename):
                raise ConversionFailure('Cannot generate PDF.')
        finally:
            timer.cancel()

    def get_output_properties(self, doc, output_format):
        output_properties = {'Overwrite': True}
        try:
            doc_family = self.get_document_family(doc)
            output_properties.update(
                LIBREOFFICE_EXPORT_TYPES[output_format][doc_family])
            return self.property_tuple(output_properties)
        except:
            raise ConversionFailure('PDF export not supported.')

    def get_document_family(self, doc):
        try:
            if doc.supportsService("com.sun.star.text.GenericTextDocument"):
                return LIBREOFFICE_DOC_FAMILIES[0]
            if doc.supportsService("com.sun.star.text.WebDocument"):
                return LIBREOFFICE_DOC_FAMILIES[1]
            if doc.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                return LIBREOFFICE_DOC_FAMILIES[2]
            if doc.supportsService("com.sun.star.presentation.PresentationDocument"):
                return LIBREOFFICE_DOC_FAMILIES[3]
            if doc.supportsService("com.sun.star.drawing.DrawingDocument"):
                return LIBREOFFICE_DOC_FAMILIES[4]
        except:
            pass

        return None

    def property_tuple(self, propDict):
        properties = []
        for k, v in propDict.items():
            prop = PropertyValue()
            prop.Name = k
            prop.Value = v
            properties.append(prop)
        return tuple(properties)
