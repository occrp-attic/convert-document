import os
import logging
from threading import Lock
from celestial import normalize_mimetype, normalize_extension
from flask import Flask, request, send_file, jsonify
from tempfile import mkstemp

from unoservice.convert import FORMATS, PdfConverter
from unoservice.exceptions import SystemFailure, ConversionFailure

ERROR_BUSY = 503
ERROR_INVALID = 400

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
lock = Lock()
converter = PdfConverter()
converter.prepare()  # warm it up


@app.route('/', methods=['GET'])
@app.route('/convert', methods=['GET'])
def index():
    payload = jsonify(FORMATS.to_json())
    acquired = lock.acquire(blocking=False)
    if acquired:
        lock.release()
        return (payload, 200)
    return (payload, ERROR_BUSY)


@app.route('/', methods=['PUT', 'POST'])
@app.route('/convert', methods=['PUT', 'POST'])
def convert():
    acquired = lock.acquire(blocking=False)
    if not acquired:
        return ('', ERROR_BUSY)
    fd, upload_file = mkstemp()
    out_file = None
    try:
        if 'file' not in request.files:
            return ('', ERROR_INVALID)
        upload = request.files['file']
        upload.save(upload_file)
        extension = request.form.get('extension', upload.filename)
        extension = normalize_extension(extension)
        mime_type = request.form.get('mime_type', upload.mimetype)
        mime_type = normalize_mimetype(mime_type, default=None)

        filters = list(FORMATS.get_filters(extension, mime_type))
        out_file = converter.convert_file(upload_file, filters)

        if not os.path.exists(out_file) or os.path.getsize(out_file) == 0:
            return ('Empty document generated', ERROR_INVALID)
        return send_file(out_file, mimetype='application/pdf')
    except SystemFailure as exc:
        return (str(exc), ERROR_BUSY)
    except ConversionFailure as exc:
        return (str(exc), ERROR_INVALID)
    finally:
        lock.release()
        if os.path.exists(upload_file):
            os.remove(upload_file)
        if out_file is not None and os.path.exists(out_file):
            os.remove(out_file)
