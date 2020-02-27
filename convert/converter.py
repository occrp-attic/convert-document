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

CONNECTION = 'socket,host=localhost,port=2002;urp;StarOffice.ComponentContext'  # noqa
COMMAND = 'soffice --nologo --headless --nocrashreport --nodefault --nofirststartwizard --norestore --invisible --accept="%s"'  # noqa

log = logging.getLogger(__name__)


class ConversionFailure(Exception):
    # A failure related to the content or structure of the document
    # given, which is expected to re-occur with consecutive attempts
    # to process the document.
    pass


class SystemFailure(Exception):
    # A failure of the service that lead to a failed conversion of
    # the document which may or may not re-occur when the document
    # is processed again.
    pass


class Converter(object):
    """Launch a background instance of LibreOffice and convert documents
    to PDF using it's filters.
    """
    OUT = '/tmp/output.pdf'
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
        # This gets executed in its own thread after `timeout` seconds.
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

    def convert_file(self, file_name, timeout):
        timer = Timer(timeout, self.terminate)
        timer.start()
        try:
            desktop = self.connect()
            if desktop is None:
                raise SystemFailure('Cannot connect to LibreOffice.')

            try:
                url = uno.systemPathToFileUrl(file_name)
                props = self.property_tuple({
                    'Hidden': True,
                    'MacroExecutionMode': 0,
                    'ReadOnly': True,
                    'Overwrite': True,
                })
                doc = desktop.loadComponentFromURL(url, '_blank', 0, props)
            except IllegalArgumentException:
                raise ConversionFailure('Cannot open document.')
            except DisposedException:
                raise SystemFailure('Bridge is disposed.')

            if doc is None:
                raise ConversionFailure('Cannot open document.')

            try:
                try:
                    doc.ShowChanges = False
                except AttributeError:
                    pass

                try:
                    doc.refresh()
                except AttributeError:
                    pass

                output_url = uno.systemPathToFileUrl(self.OUT)
                prop = self.get_output_properties(doc)
                doc.storeToURL(output_url, prop)
                doc.dispose()
                doc.close(True)
                del doc
            except DisposedException:
                raise ConversionFailure('Cannot generate PDF.')

            stat = os.stat(self.OUT)
            if stat.st_size == 0 or not os.path.exists(self.OUT):
                raise ConversionFailure('Cannot generate PDF.')
        finally:
            timer.cancel()

    def get_output_properties(self, doc):
        for (service, pdf) in self.PDF_FILTERS:
            if doc.supportsService(service):
                return self.property_tuple({
                    'FilterName': pdf,
                    'Overwrite': True,
                    'MaxImageResolution': 300,
                    'SelectPdfVersion': 2,
                })
        raise ConversionFailure('PDF export not supported.')

    def property_tuple(self, propDict):
        properties = []
        for k, v in propDict.items():
            prop = PropertyValue()
            prop.Name = k
            prop.Value = v
            properties.append(prop)
        return tuple(properties)
