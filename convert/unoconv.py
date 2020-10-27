import os
import uno
import time
import logging
import subprocess
from threading import Timer
from com.sun.star.beans import PropertyValue
from com.sun.star.lang import DisposedException, IllegalArgumentException
from com.sun.star.connection import NoConnectException
from com.sun.star.io import IOException
from com.sun.star.script import CannotConvertException
from com.sun.star.uno import RuntimeException

from convert.common import Converter
from convert.util import CONVERT_DIR, INSTANCE_DIR, flush_path
from convert.util import SystemFailure, ConversionFailure


DESKTOP = "com.sun.star.frame.Desktop"
RESOLVER = "com.sun.star.bridge.UnoUrlResolver"
OUT_FILE = os.path.join(CONVERT_DIR, "output.pdf")
CONNECTION = (
    "socket,host=localhost,port=2002,tcpNoDelay=1;urp;StarOffice.ComponentContext"
)
COMMAND = [
    "/usr/bin/soffice",
    "-env:UserInstallation=file:///%s" % INSTANCE_DIR,
    "-env:JFW_PLUGIN_DO_NOT_CHECK_ACCESSIBILITY=1",
    "--nologo",
    "--headless",
    "--nocrashreport",
    # "--nodefault",
    "--norestore",
    "--accept=%s" % CONNECTION,
]

log = logging.getLogger(__name__)


class UnoconvConverter(Converter):
    """Launch a background instance of LibreOffice and convert documents
    to PDF using it's filters.
    """

    PDF_FILTERS = (
        ("com.sun.star.text.GenericTextDocument", "writer_pdf_Export"),
        ("com.sun.star.text.WebDocument", "writer_web_pdf_Export"),
        ("com.sun.star.presentation.PresentationDocument", "impress_pdf_Export"),
        ("com.sun.star.drawing.DrawingDocument", "draw_pdf_Export"),
    )

    def start(self):
        flush_path(INSTANCE_DIR)
        log.info("Starting LibreOffice: %s", " ".join(COMMAND))
        proc = subprocess.Popen(COMMAND, close_fds=True)
        time.sleep(2)
        log.info("PID: %s; return: %s", proc.pid, proc.returncode)

    def _svc_create(self, ctx, clazz):
        return ctx.ServiceManager.createInstanceWithContext(clazz, ctx)

    def connect(self):
        proc = self.get_proc()
        if proc is None:
            self.start()

        for attempt in range(15):
            try:
                context = uno.getComponentContext()
                resolver = self._svc_create(context, RESOLVER)
                context = resolver.resolve("uno:%s" % CONNECTION)
                return self._svc_create(context, DESKTOP)
            except NoConnectException:
                log.warning("No connection to LibreOffice (%s)", attempt)
                time.sleep(2)
            except DisposedException:
                raise SystemFailure("Bridge is disposed.")
        raise SystemFailure("No connection to LibreOffice")

    def check_healthy(self):
        desktop = self.connect()
        return desktop is not None

    def check_desktop(self, desktop):
        if desktop.getFrames().getCount() != 0:
            raise SystemFailure("LibreOffice has stray frames.")
        if desktop.getTasks() is not None:
            raise SystemFailure("LibreOffice has stray tasks.")

    def on_timeout(self):
        self.kill()
        raise SystemFailure("LibreOffice timed out.")

    def convert_file(self, file_name, timeout):
        timer = Timer(timeout, self.on_timeout)
        timer.start()
        try:
            return self._timed_convert_file(file_name)
        finally:
            timer.cancel()

    def _timed_convert_file(self, file_name):
        desktop = self.connect()
        self.check_desktop(desktop)
        # log.debug("[%s] connected.", file_name)
        try:
            url = uno.systemPathToFileUrl(file_name)
            props = self.property_tuple(
                {
                    "Hidden": True,
                    "MacroExecutionMode": 0,
                    "ReadOnly": True,
                    "Overwrite": True,
                    "OpenNewView": True,
                    "StartPresentation": False,
                    "RepairPackage": False,
                }
            )
            doc = desktop.loadComponentFromURL(url, "_blank", 0, props)
        except IllegalArgumentException:
            raise ConversionFailure("Cannot open document.")
        except DisposedException:
            raise SystemFailure("Bridge is disposed.")

        if doc is None:
            raise ConversionFailure("Cannot open document.")

        # log.debug("[%s] opened.", file_name)
        try:
            try:
                doc.ShowChanges = False
            except AttributeError:
                pass

            try:
                doc.refresh()
            except AttributeError:
                pass

            output_url = uno.systemPathToFileUrl(OUT_FILE)
            prop = self.get_output_properties(doc)
            # log.debug("[%s] refreshed.", file_name)
            doc.storeToURL(output_url, prop)
            # log.debug("[%s] exported.", file_name)
            doc.dispose()
            doc.close(True)
            del doc
            # log.debug("[%s] closed.", file_name)
        except (
            DisposedException,
            IOException,
            CannotConvertException,
            RuntimeException,
        ):
            raise ConversionFailure("Cannot generate PDF.")

        stat = os.stat(OUT_FILE)
        if stat.st_size == 0 or not os.path.exists(OUT_FILE):
            raise ConversionFailure("Cannot generate PDF.")
        return OUT_FILE

    def get_output_properties(self, doc):
        # https://github.com/unoconv/unoconv/blob/master/doc/filters.adoc
        filter_name = "writer_pdf_Export"
        for (service, pdf) in self.PDF_FILTERS:
            if doc.supportsService(service):
                filter_name = pdf
        return self.property_tuple(
            {
                "FilterName": filter_name,
                "Overwrite": True,
                "ReduceImageResolution": True,
                "MaxImageResolution": 300,
                "SelectPdfVersion": 1,
            }
        )

    def property_tuple(self, propDict):
        properties = []
        for k, v in propDict.items():
            prop = PropertyValue()
            prop.Name = k
            prop.Value = v
            properties.append(prop)
        return tuple(properties)
