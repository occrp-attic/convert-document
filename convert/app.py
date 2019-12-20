import os
import time
import logging
import traceback
import subprocess
from threading import RLock
from flask import Flask, request, send_file
from tempfile import mkstemp
from werkzeug.wsgi import ClosingIterator
from pantomime import FileName, normalize_mimetype, mimetype_extension

from convert.formats import load_mime_extensions

TIMEOUT = 90
OUT_PATH = '/tmp/output.pdf'
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('convert')
lock = RLock()
extensions = load_mime_extensions()
listener = subprocess.Popen(['unoconv', '--listener', '-vvv'])
time.sleep(2)
app = Flask("convert")
app.is_dead = False


class ShutdownMiddleware:
    def __init__(self, application):
        self.application = application

    def post_request(self):
        if app.is_dead:
            os._exit(0)

    def __call__(self, environ, after_response):
        iterator = self.application(environ, after_response)
        try:
            return ClosingIterator(iterator, [self.post_request])
        except Exception:
            traceback.print_exc()
            return iterator


app.wsgi_app = ShutdownMiddleware(app.wsgi_app)


def convert_file(source_file):
    try:
        os.unlink(OUT_PATH)
    except OSError:
        pass
    args = ['unoconv',
            '-f', 'pdf',
            '-vvv',
            '--timeout', str(TIMEOUT + 5),
            '-o', OUT_PATH,
            '-i', 'MacroExecutionMode=0',
            '-i', 'ReadOnly=1',
            '-e', 'SelectPdfVersion=1',
            '-e', 'MaxImageResolution=300',
            # '--no-launch',
            source_file]
    err = subprocess.call(args, timeout=TIMEOUT)
    log.debug("LibreOffice exit code: %s", err)
    if err != 0 or not os.path.exists(OUT_PATH):
        raise RuntimeError()
    return OUT_PATH


@app.route("/")
def info():
    # acquired = lock.acquire(timeout=2)
    # if not acquired:
    #     return ("BUSY", 503)
    return ("OK", 200)


@app.route("/convert", methods=['POST'])
def convert():
    acquired = lock.acquire(timeout=5)
    if not acquired:
        return ("BUSY", 503)
    # if listener.poll() is not None:
    #     log.error("Listener has terminated.")
    #     app.is_dead = True
    #     return ("DEAD", 503)
    try:
        for upload in request.files.values():
            file_name = FileName(upload.filename)
            mime_type = normalize_mimetype(upload.mimetype)
            if not file_name.has_extension:
                file_name.extension = extensions.get(mime_type)
            if not file_name.has_extension:
                file_name.extension = mimetype_extension(mime_type)
            fd, upload_file = mkstemp(suffix=file_name.safe())
            os.close(fd)
            log.info('PDF convert: %s [%s]', upload_file, mime_type)
            upload.save(upload_file)
            out_file = convert_file(upload_file)
            if os.path.exists(upload_file):
                os.unlink(upload_file)
            return send_file(out_file, mimetype='application/pdf')
    except RuntimeError:
        app.is_dead = True
        return ('The document could not be converted to PDF.', 400)
    except subprocess.TimeoutExpired:
        log.error("Timeout exceeded: %s", upload.filename)
        app.is_dead = True
        return ('Processing the document timed out.', 400)
    finally:
        lock.release()


if __name__ == '__main__':
    # app.run(debug=True, port=3000, host='0.0.0.0')
    app.run(port=3000, host='0.0.0.0', threaded=True)
