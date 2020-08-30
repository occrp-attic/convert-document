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
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
