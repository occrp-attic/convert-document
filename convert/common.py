import os
import logging
from abc import ABC
from psutil import process_iter, pid_exists, TimeoutExpired
from convert.util import LOCK_FILE, CONVERT_DIR, flush_path

log = logging.getLogger(__name__)


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
