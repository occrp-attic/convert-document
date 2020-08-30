import os
import logging
import subprocess
from convert.common import Converter
from convert.util import CONVERT_DIR, INSTANCE_DIR, flush_path
from convert.util import ConversionFailure

OUT_DIR = os.path.join(CONVERT_DIR, "out")
ENV = '"-env:UserInstallation=file:///%s"' % INSTANCE_DIR
COMMAND = [
    "/usr/bin/libreoffice",
    ENV,
    "--nologo",
    "--headless",
    "--nocrashreport",
    "--nodefault",
    "--norestore",
    "--nolockcheck",
    "--invisible",
    "--convert-to",
    "pdf",
    "--outdir",
    OUT_DIR,
]

log = logging.getLogger(__name__)


class ProcessConverter(Converter):

    PROCESS_NAME = "libreoffice"

    def check_healthy(self):
        return True

    def prepare(self):
        self.kill()
        flush_path(INSTANCE_DIR)
        flush_path(CONVERT_DIR)
        flush_path(OUT_DIR)

    def convert_file(self, file_name, timeout):
        cmd = list(COMMAND) + [file_name]
        try:
            log.info("Starting LibreOffice: %s with timeout %s", cmd, timeout)
            subprocess.run(cmd, timeout=timeout)

            for file_name in os.listdir(OUT_DIR):
                if not file_name.endswith(".pdf"):
                    continue
                out_file = os.path.join(OUT_DIR, file_name)
                stat = os.stat(out_file)
                if stat.st_size == 0:
                    continue
                return out_file
        except Exception:
            log.exception("LibreOffice conversion failed")
            self.kill()

        raise ConversionFailure("Cannot generate PDF.")
