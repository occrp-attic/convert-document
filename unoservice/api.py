import os
import logging
from threading import Lock
from flask import Flask, request, send_file, jsonify
from tempfile import mkstemp

from unoservice.convert import FORMATS, PdfConverter
from unoservice.exceptions import SystemFailure, ConversionFailure
from unoservice.util import normalize_extension

ERROR_BUSY = 503
ERROR_INVALID = 400

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
lock = Lock()
converter = PdfConverter()
converter.prepare()  # warm it up


@app.route('/', methods=['GET', 'POST'])
@app.route('/convert', methods=['GET'])
def index():
    payload = jsonify({
        'mime_types': FORMATS.mime_types,
        'extensions': FORMATS.extensions
    })
    acquired = lock.acquire(blocking=False)
    if acquired:
        lock.release()
        return (payload, 200)
    return (payload, ERROR_BUSY)


@app.route('/convert', methods=['PUT', 'POST'])
def convert():
    acquired = lock.acquire(blocking=False)
    if not acquired:
        return ('', ERROR_BUSY)
    fd, upload_file = mkstemp()
    output_file = None
    try:
        if 'file' not in request.files:
            return ('', ERROR_INVALID)
        upload = request.files['file']
        upload.save(upload_file)
        extension = normalize_extension(upload.filename)
        extension = request.form.get('extension', extension)
        mime_type = request.form.get('mime_type')
        output_file = converter.convert_file(upload_file, extension, mime_type)
        if not os.path.exists(output_file):
            return ('', ERROR_INVALID)
        if os.path.getsize(output_file) == 0:
            return ('', ERROR_INVALID)
        return send_file(output_file, mimetype='application/pdf')
    except SystemFailure:
        return ('', ERROR_BUSY)
    except ConversionFailure:
        return ('', ERROR_INVALID)
    finally:
        lock.release()
        if upload_file is not None and os.path.exists(upload_file):
            os.remove(upload_file)
        if output_file is not None and os.path.exists(output_file):
            os.remove(output_file)
