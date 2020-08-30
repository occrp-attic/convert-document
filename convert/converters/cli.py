import os
import logging
import subprocess
from convert.common import ProcessConverter
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


class CliConverter(ProcessConverter):
    def __init__(self):
        super().__init__("libreoffice")

    def check_healthy(self):
        return True

    def convert_file(self, file_name, timeout):
        flush_path(INSTANCE_DIR)
        flush_path(OUT_DIR)
        self.kill()
        cmd = COMMAND.copy()
        cmd.append(file_name)

        out_file = None
        try:
            log.info("Starting LibreOffice: %s with timeout %s", cmd, timeout)
            subprocess.run(cmd, timeout=timeout)

            files = os.listdir(OUT_DIR)
            pdf_files = list(filter(lambda f: f.endswith(".pdf"), files))
            if len(pdf_files) <= 0:
                raise ConversionFailure("Cannot generate PDF.")

            out_file = os.path.join(OUT_DIR, pdf_files[0])
        except Exception as e:
            log.info("LibreOffice conversion failed", e)
            self.kill()
            raise ConversionFailure("Cannot generate PDF.", e)

        if out_file is None:
            raise ConversionFailure("Cannot generate PDF.")

        stat = os.stat(out_file)
        if stat.st_size == 0 or not os.path.exists(out_file):
            raise ConversionFailure("Cannot generate PDF.")
        return out_file
