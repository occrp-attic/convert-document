import os
import logging
import traceback
from threading import Lock
from flask import Flask, request, send_file
from werkzeug.wsgi import ClosingIterator
from werkzeug.exceptions import HTTPException
from pantomime import FileName, normalize_mimetype, mimetype_extension

from convert.converter import Converter, ConversionFailure
from convert.converter import CONVERT_DIR
from convert.formats import load_mime_extensions

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('convert')
lock = Lock()
extensions = load_mime_extensions()
converter = Converter()


class ShutdownMiddleware:
    def __init__(self, application):
        self.application = application

    def post_request(self):
        if app.is_dead:
            os._exit(127)

    def __call__(self, environ, after_response):
        iterator = self.application(environ, after_response)
        try:
            return ClosingIterator(iterator, [self.post_request])
        except Exception:
            traceback.print_exc()
            return iterator


app = Flask('convert')
app.is_dead = False
app.wsgi_app = ShutdownMiddleware(app.wsgi_app)


@app.route('/')
@app.route('/healthz')
@app.route('/health/live')
def check_health():
    if app.is_dead:
        return ('DEAD', 500)
    acquired = lock.acquire(timeout=1)
    try:
        desktop = converter.connect()
        if acquired:
            converter.check_health(desktop)
        return ('OK', 200)
    except Exception:
        app.is_dead = True
        log.exception('Health check error')
        return ('DEAD', 500)
    finally:
        if acquired:
            lock.release()


@app.route('/health/ready')
def check_ready():
    acquired = lock.acquire(timeout=1)
    if not acquired:
        return ('BUSY', 503)
    lock.release()
    return ('OK', 200)


@app.route('/convert', methods=['POST'])
def convert():
    if app.is_dead:
        return ('DEAD', 503)
    upload_file = None
    acquired = lock.acquire(timeout=1)
    if not acquired:
        return ('BUSY', 503)
    try:
        converter.cleanup()
        timeout = int(request.args.get('timeout', 100))
        for upload in request.files.values():
            file_name = FileName(upload.filename)
            mime_type = normalize_mimetype(upload.mimetype)
            if not file_name.has_extension:
                file_name.extension = extensions.get(mime_type)
            if not file_name.has_extension:
                file_name.extension = mimetype_extension(mime_type)
            upload_file = os.path.join(CONVERT_DIR, file_name.safe())
            log.info('PDF convert: %s [%s]', upload_file, mime_type)
            upload.save(upload_file)
            out_file = converter.convert_file(upload_file, timeout)
            return send_file(out_file,
                             mimetype='application/pdf',
                             attachment_filename='output.pdf')
        return ('No file uploaded', 400)
    except HTTPException:
        raise
    except ConversionFailure as ex:
        app.is_dead = True
        return (str(ex), 400)
    except Exception:
        app.is_dead = True
        log.exception('System error')
        return ('FAIL', 503)
    finally:
        converter.cleanup()
        lock.release()
