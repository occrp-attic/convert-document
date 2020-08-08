import os
import uno
import time
import shutil
import logging
import subprocess
from threading import Timer
from tempfile import gettempdir
from psutil import process_iter, TimeoutExpired
from com.sun.star.beans import PropertyValue
from com.sun.star.lang import DisposedException, IllegalArgumentException
from com.sun.star.connection import NoConnectException
from com.sun.star.io import IOException
from com.sun.star.script import CannotConvertException
from com.sun.star.uno import RuntimeException

DESKTOP = "com.sun.star.frame.Desktop"
RESOLVER = "com.sun.star.bridge.UnoUrlResolver"
CONVERT_DIR = os.path.join(gettempdir(), "convert")
OUT_FILE = os.path.join(CONVERT_DIR, "/tmp/output.pdf")
INSTANCE_DIR = os.path.join(gettempdir(), "soffice")
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
    # "--invisible",
    "--accept=%s" % CONNECTION,
]

log = logging.getLogger(__name__)


def flush_path(path):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


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

    PDF_FILTERS = (
        ("com.sun.star.text.GenericTextDocument", "writer_pdf_Export"),
        ("com.sun.star.text.WebDocument", "writer_web_pdf_Export"),
        ("com.sun.star.presentation.PresentationDocument", "impress_pdf_Export"),
        ("com.sun.star.drawing.DrawingDocument", "draw_pdf_Export"),
    )

    def __init__(self):
        self.alive = False
        self.start()

    def kill(self):
        log.info("Disposing of LibreOffice.")
        self.alive = False
        # The Alfred Hitchcock approach to task management:
        # https://www.youtube.com/watch?v=0WtDmbr9xyY
        try:
            for proc in process_iter(["cmdline"]):
                name = " ".join(proc.cmdline())
                if "soffice" not in name:
                    continue
                log.warn("Killing process: %r", proc)
                proc.kill()
                proc.wait(timeout=5)
        except TimeoutExpired:
            log.error("Hanging process: %r", name)
            os._exit(23)
        except Exception as exc:
            log.error("Failed to kill: %r (%s)", name, exc)
            os._exit(23)

    def start(self):
        self.kill()
        flush_path(INSTANCE_DIR)
        flush_path(CONVERT_DIR)
        log.info("Starting LibreOffice: %s", COMMAND)
        proc = subprocess.Popen(COMMAND, close_fds=True)
        log.info("PID: %s", proc.pid)
        time.sleep(3)
        log.info("Returncode: %s", proc.returncode)
        self.alive = True

    def prepare(self):
        if not self.alive:
            self.start()
        flush_path(CONVERT_DIR)

    def terminate(self):
        # This gets executed in its own thread after `timeout` seconds.
        log.error("Document conversion timed out.")
        self.kill()

    def _svc_create(self, ctx, clazz):
        return ctx.ServiceManager.createInstanceWithContext(clazz, ctx)

    def connect(self):
        for attempt in range(10):
            try:
                context = uno.getComponentContext()
                resolver = self._svc_create(context, RESOLVER)
                context = resolver.resolve("uno:%s" % CONNECTION)
                return self._svc_create(context, DESKTOP)
            except NoConnectException:
                log.warning("No connection to LibreOffice (%s)", attempt)
                time.sleep(2)
        self.kill()
        raise SystemFailure("No connection to LibreOffice")

    def check_health(self, desktop):
        if desktop.getFrames().getCount() != 0:
            raise SystemFailure("LibreOffice has stray frames.")
        if desktop.getTasks() is not None:
            raise SystemFailure("LibreOffice has stray tasks.")

    def convert_file(self, file_name, timeout):
        timer = Timer(timeout * 0.99, self.terminate)
        timer.start()
        try:
            return self._timed_convert_file(file_name)
        finally:
            timer.cancel()

    def _timed_convert_file(self, file_name):
        desktop = self.connect()
        self.check_health(desktop)
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
