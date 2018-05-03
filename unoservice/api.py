import os
import logging
from threading import Lock
from flask import Flask, request, send_file
from tempfile import mkstemp

from unoservice.convert import PdfConverter
from unoservice.exceptions import SystemFailure, ConversionFailure

ERROR_BUSY = 503
ERROR_PERM = 406

app = Flask(__name__)
lock = Lock()
converter = PdfConverter()
logging.basicConfig(level=logging.DEBUG)


@app.route('/', methods=['GET', 'POST'])
def index():
    acquired = lock.acquire(blocking=False)
    if acquired:
        lock.release()
        return ('', 200)
    return ('', ERROR_BUSY)


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
        file = request.files['file']
        file.save(upload_file)
        extension = request.form.get('extension')
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
