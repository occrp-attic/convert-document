import os
import shutil
import importlib
import logging
from abc import ABC
from tempfile import gettempdir
from psutil import process_iter, pid_exists, TimeoutExpired

CONVERT_DIR = os.path.join(gettempdir(), 'convert')
LOCK_FILE = os.path.join(gettempdir(), "convert.lock")
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


def flush_path(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


class Converter(object):
    """Generic libreoffice converter class."""
    def lock(self):
        # Race conditions galore, but how likely
        # are requests at that rate?
        if self.is_locked:
            return False
        with open(LOCK_FILE, "w") as fh:
            fh.write(str(os.getpid()))
        return True

    def unlock(self):
        if os.path.exists(LOCK_FILE):
            os.unlink(LOCK_FILE)

    @property
    def is_locked(self):
        if not os.path.exists(LOCK_FILE):
            return False
        with open(LOCK_FILE, "r") as fh:
            pid = int(fh.read())
        if not pid_exists(pid):
            return False
        return True

    def reset(self):
        flush_path(CONVERT_DIR)

    def kill(self):
        raise NotImplementedError()

    @property
    def setup_is_done(self):
        raise NotImplementedError()

    def convert_file(self, file_name, timeout):
        raise NotImplementedError()


class ProcessConverter(Converter, ABC):
    def __init__(self, process_name):
        self.process_name = process_name

    def kill(self):
        log.info("Disposing converter process.")
        # The Alfred Hitchcock approach to task management:
        # https://www.youtube.com/watch?v=0WtDmbr9xyY
        try:
            proc = self.get_proc()
            if proc is not None:
                proc.kill()
                proc.wait(timeout=5)
            self.unlock()
        except (TimeoutExpired, Exception) as exc:
            log.error("Failed to kill: %r (%s)", proc, exc)
            self.unlock()
            os._exit(23)

    def get_proc(self):
        for proc in process_iter(["cmdline"]):
            name = " ".join(proc.cmdline())
            if self.process_name in name:
                return proc


class ConverterFactory(object):
    @staticmethod
    def get_instance(implementation):
        print("loading " + implementation + " implementation")
        module = importlib.import_module("." + implementation, 'convert.converters')
        cls = getattr(module, implementation.capitalize() + 'Converter')
        return cls()
