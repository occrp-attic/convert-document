import os
import logging
from threading import Lock
from flask import Flask, request, send_file
from pantomime import FileName, normalize_mimetype, mimetype_extension

from convert.converter import Converter, ConversionFailure, SystemFailure
from convert.converter import CONVERT_DIR
from convert.formats import load_mime_extensions

PDF = 'application/pdf'
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('convert')
lock = Lock()
extensions = load_mime_extensions()
converter = Converter()
app = Flask('convert')


@app.route('/')
@app.route('/healthz')
@app.route('/health/live')
def check_health():
    acquired = lock.acquire(timeout=2)
    try:
        if acquired:
            converter.prepare()
        desktop = converter.connect()
        if acquired:
            converter.check_health(desktop)
        return ('OK', 200)
    except Exception:
        converter.kill()
        return ('DEAD', 500)
    finally:
        if acquired:
            lock.release()


@app.route('/health/ready')
def check_ready():
    acquired = lock.acquire(timeout=2)
    if not acquired:
        return ('BUSY', 503)
    lock.release()
    return ('OK', 200)


@app.route('/reset')
def reset():
    converter.kill()
    if lock.locked():
        lock.release()
    return ('OK', 200)


@app.route('/convert', methods=['POST'])
def convert():
    upload_file = None
    acquired = lock.acquire(timeout=1)
    if not acquired:
        return ('BUSY', 503)
    try:
        converter.prepare()
        timeout = int(request.args.get('timeout', 7200))
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
            return send_file(out_file, mimetype=PDF,
                             attachment_filename='output.pdf')
        return ('No file uploaded', 400)
    except ConversionFailure as ex:
        converter.kill()
        return (str(ex), 400)
    except (SystemFailure, Exception) as ex:
        converter.kill()
        log.warn('Error: %s', ex)
        return ('CRASH', 503)
    finally:
        lock.release()
