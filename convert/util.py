import os
import shutil
from tempfile import gettempdir

CONVERT_DIR = os.path.join(gettempdir(), "convert")
LOCK_FILE = os.path.join(gettempdir(), "convert.lock")
INSTANCE_DIR = os.path.join(gettempdir(), "soffice")


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


def flush_path(path):
    for i in range(100):
        try:
            shutil.rmtree(path, ignore_errors=True)
            os.makedirs(path)
            return
        except Exception:
            pass
    raise SystemFailure("Cannot flush: %s" % path)
