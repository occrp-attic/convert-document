import os
import logging
from psutil import process_iter, pid_exists, TimeoutExpired, NoSuchProcess
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
        try:
            with open(LOCK_FILE, "r") as fh:
                pid = int(fh.read())
        except (ValueError, FileNotFoundError):
            return False
        if not pid_exists(pid):
            return False
        return True

    def prepare(self):
        flush_path(CONVERT_DIR)

    def convert_file(self, file_name, timeout):
        raise NotImplementedError()

    def kill(self):
        # The Alfred Hitchcock approach to task management:
        # https://www.youtube.com/watch?v=0WtDmbr9xyY
        for i in range(10):
            proc = self.get_proc()
            if proc is None:
                break
            log.info("Disposing converter process.")
            try:
                proc.kill()
                proc.wait(timeout=3)
            except NoSuchProcess:
                log.info("Process has disappeared")
            except (TimeoutExpired, Exception) as exc:
                log.error("Failed to kill: %r (%s)", proc, exc)
                # os._exit(23)

    def get_proc(self):
        for proc in process_iter(["cmdline"]):
            name = " ".join(proc.cmdline())
            if "soffice.bin" in name:
                return proc
