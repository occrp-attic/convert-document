# derived from https://gist.github.com/six519/28802627584b21ba1f6a
# unlicensed
import os
import uno
import time
import signal
import logging
import subprocess
from tempfile import mkstemp
from com.sun.star.beans import PropertyValue

from unoservice.formats import Formats
from unoservice.exceptions import SystemFailure, ConversionFailure
from unoservice.exceptions import handle_timeout
from unoservice.util import PDF_FILTERS

CONNECTION_STRING = "socket,host=localhost,port=%s;urp;StarOffice.ComponentContext"  # noqa
COMMAND = 'soffice --nologo --headless --nocrashreport --nodefault --nofirststartwizard --norestore --invisible --accept="%s"'  # noqa
RESOLVER_CLASS = 'com.sun.star.bridge.UnoUrlResolver'
DESKTOP_CLASS = 'com.sun.star.frame.Desktop'
DEFAULT_PORT = 6519
FORMATS = Formats()

log = logging.getLogger(__name__)


class PdfConverter(object):
    """Launch a background instance of LibreOffice and convert documents
    to PDF using it's filters.
    """

    def __init__(self, host=None, port=None):
        self.port = port or DEFAULT_PORT
        self.desktop = None
        self.process = None

    def _svc_create(self, ctx, clazz):
        return ctx.ServiceManager.createInstanceWithContext(clazz, ctx)

    def prepare(self):
        # Check if the LibreOffice process has an exit code:
        if self.process is None or self.process.poll() is not None:
            log.info("LibreOffice not running; reset.")
            self.terminate()

        connection = CONNECTION_STRING % self.port
        if self.process is None:
            log.info("Starting headless LibreOffice...")
            command = COMMAND % connection
            self.process = subprocess.Popen(command,
                                            shell=True,
                                            stdin=None,
                                            stdout=None,
                                            stderr=None)
            time.sleep(5)
            self.desktop = None

        if self.desktop is None:
            log.info("Connecting to UNO service...")
            local_context = uno.getComponentContext()
            resolver = self._svc_create(local_context, RESOLVER_CLASS)
            context = resolver.resolve("uno:%s" % connection)
            self.desktop = self._svc_create(context, DESKTOP_CLASS)

    def terminate(self):
        if self.desktop is not None:
            # Clear out our local LO handle.
            log.info("Destroying UNO desktop instance...")
            try:
                self.desktop.terminate()
            except Exception:
                log.exception("Failed to terminate")
            self.desktop = None

        if self.process is not None:
            # Check if the LibreOffice process is still running
            if self.process.poll() is None:
                log.info("Killing LibreOffice process...")
                self.process.kill()
            self.process = None

    def convert_file(self, file_name, extension, mime_type, timeout=600):
        try:
            self.prepare()
        except Exception:
            log.exception("Failed to instantiate UNO bridge.")
            self.terminate()
            raise SystemFailure("Cannot process documents")

        file_name = os.path.abspath(file_name)
        input_filter = FORMATS.get_filter(extension, mime_type)
        if input_filter is None:
            raise ConversionFailure("Cannot determine input format.")

        fd, output_filename = mkstemp(suffix='.pdf')
        os.close(fd)
        input_url = uno.systemPathToFileUrl(file_name)
        output_url = uno.systemPathToFileUrl(output_filename)

        # Trigger SIGALRM after the timeout has passed.
        signal.signal(signal.SIGALRM, handle_timeout)
        signal.alarm(timeout)
        try:
            props = self.property_tuple({
                "Hidden": True,
                "FilterName": input_filter
            })
            doc = self.desktop.loadComponentFromURL(input_url,
                                                    '_blank',
                                                    0,
                                                    props)
            if doc is None:
                raise ConversionFailure("Cannot open document")
            if hasattr(doc, 'refresh'):
                doc.refresh()
            output_filter = self.get_output_filter(doc)
            if output_filter is None:
                raise ConversionFailure("Cannot export to PDF.")

            prop = self.property_tuple({
                "FilterName": output_filter,
                "MaxImageResolution": 300,
                "SelectPdfVersion": 1,
            })
            doc.storeToURL(output_url, prop)
            doc.close(True)
            return output_filename
        except ConversionFailure:
            raise
        except Exception as exc:
            log.exception("Failed to generate PDF.")
            os.unlink(output_filename)
            self.terminate()
            raise ConversionFailure(str(exc))
        finally:
            signal.alarm(0)

    def property_tuple(self, propDict):
        properties = []
        for k, v in propDict.items():
            property = PropertyValue()
            property.Name = k
            property.Value = v
            properties.append(property)
        return tuple(properties)

    def get_output_filter(self, doc):
        for (service, pdf) in PDF_FILTERS:
            if doc.supportsService(service):
                return pdf


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_libreoffice = PdfConverter()
    # convert MS Word Document file (docx) to PDF
    for i in range(100):
        test_libreoffice.convert_file("/unoservice/fixtures/agreement.docx",
                                      "docx", None, timeout=10)
        print('Round: %s' % i)
