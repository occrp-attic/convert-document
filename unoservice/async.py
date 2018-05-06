import os
import shutil
import logging
from aiohttp import web
from threading import Lock
from tempfile import mkstemp
from celestial import normalize_mimetype, normalize_extension

from unoservice.convert import FORMATS, PdfConverter
from unoservice.util import SystemFailure, ConversionFailure

MEGABYTE = 1024 * 1024
BUFFER_SIZE = 8 * MEGABYTE
MAX_UPLOAD = 800 * MEGABYTE
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('aiohttp').setLevel(logging.WARNING)
log = logging.getLogger('unoservice')

lock = Lock()
converter = PdfConverter()


async def info(request):
    return web.Response(text="OK")


async def convert(request):
    acquired = lock.acquire(blocking=False)
    if not acquired:
        return web.Response(status=503)
    data = await request.post()
    upload = data['file']
    fd, upload_file = mkstemp()
    out_file = None
    try:
        os.close(fd)
        with open(upload_file, 'wb') as fh:
            shutil.copyfileobj(upload.file, fh, BUFFER_SIZE)

        extension = normalize_extension(upload.filename)
        mime_type = normalize_mimetype(upload.content_type, default=None)
        filters = list(FORMATS.get_filters(extension, mime_type))

        out_file = converter.convert_file(upload_file, filters)
        out_size = os.path.getsize(out_file) if os.path.exists(out_file) else 0
        lock.release()

        response = web.StreamResponse()
        response.content_length = out_size
        response.content_type = 'application/pdf'
        await response.prepare(request)
        with open(out_file, 'rb') as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                await response.write(chunk)
        return response
    except SystemFailure as exc:
        log.error('%s', exc)
        lock.release()
        return web.Response(text=str(exc))
    except ConversionFailure as exc:
        log.warning('Failure: %s', exc)
        lock.release()
        return web.Response(text=str(exc), status=400)
    finally:
        if os.path.exists(upload_file):
            os.remove(upload_file)
        if out_file is not None and os.path.exists(out_file):
            os.remove(out_file)


app = web.Application(client_max_size=MAX_UPLOAD)
app.add_routes([web.get('/', info)])
app.add_routes([web.get('/convert', info)])
app.add_routes([web.post('/', convert)])
app.add_routes([web.post('/convert', convert)])
web.run_app(app, port=3000)
