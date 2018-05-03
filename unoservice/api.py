import os
import logging
from threading import Lock
from flask import Flask, request, send_file, jsonify
from tempfile import mkstemp

from unoservice.convert import FORMATS, PdfConverter
from unoservice.exceptions import SystemFailure, ConversionFailure
from unoservice.util import extract_extension

ERROR_BUSY = 503
ERROR_PERM = 406

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
lock = Lock()
converter = PdfConverter()
converter.prepare()  # warm it up


@app.route('/', methods=['GET', 'POST'])
def index():
    acquired = lock.acquire(blocking=False)
    payload = jsonify({
        'mime_types': FORMATS.mime_types,
        'extensions': FORMATS.extensions
    })
    if acquired:
        lock.release()
        return (payload, 200)
    return (payload, ERROR_BUSY)


@app.route('/convert', methods=['PUT', 'POST'])
def convert():
    acquired = lock.acquire(blocking=False)
    fd, upload_file = mkstemp()
    output_file = None
    if not acquired:
        return ('', ERROR_BUSY)
    try:
        if 'file' not in request.files:
            return ('', 400)
        upload = request.files['file']
        upload.save(upload_file)
        extension = extract_extension(upload.filename)
        extension = request.form.get('extension', extension)
        mime_type = request.form.get('mime_type')
        output_file = converter.convert_file(upload_file, extension, mime_type)
        if not os.path.exists(output_file):
            return ('', ERROR_PERM)
        if os.path.getsize(output_file) == 0:
            return ('', ERROR_PERM)
        return send_file(output_file, mimetype='application/pdf')
    except SystemFailure:
        return ('', ERROR_BUSY)
    except ConversionFailure:
        return ('', ERROR_PERM)
    finally:
        lock.release()
        if upload_file is not None and os.path.exists(upload_file):
            os.remove(upload_file)
        if output_file is not None and os.path.exists(output_file):
            os.remove(output_file)
