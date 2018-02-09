const express = require('express');
const http = require('http');
const multer  = require('multer');
const uuid = require('uuid/v4');
const locks = require('locks');
const fs = require('fs');
const { spawn, execSync } = require('child_process');

const mutex = locks.createMutex();
const app = express();
const server = http.createServer(app);

const request_threshold = 500;
app.locals.req_count = 0;

spawn("unoconv", ["--listener"]).on('close', function() {
  spawn("unoconv", ["--listener", "-v"])
})

var storage = multer.diskStorage({
  destination: '/tmp',
  filename: function (req, file, cb) {
    cb(null, uuid() + '.' + file.originalname);
  }
});

const upload = multer({storage: storage});

app.get('/', function(req, res, next) {
  if (mutex.tryLock()) {
    mutex.unlock();
    res.status(200).send('OK');
  } else {
    res.status(502).send('BUSY');
  }
});

app.post('/convert', upload.single('file'), function (req, res, next) {
  const format = req.body.format || 'pdf';
  const args = ['-n', '-T', '1500', '--stdout',
                '-eSelectPdfVersion=1',
                '-f', format, req.file.path];
  
  mutex.lock(function() {
    app.locals.req_count += 1;
    res.status(200);
    res.type(format);

    const conv = spawn('unoconv', args);
    conv.stdout.on('data', (data) => {
      res.write(data);
    });

    conv.stderr.on('data', (data) => {
      console.log(`${data}`);
    });

    conv.on('close', (code) => {
      res.end();
      fs.unlink(req.file.path);
      mutex.unlock();

      if (app.locals.req_count > request_threshold) {
        server.getConnections(function(err, count) {
          // Check to see if there are no other requests being processed
          if (count === 1) {
              console.log("exiting.")
              process.exit(1)
          }
        })
      }
    });
  });
});

process.on('SIGINT', function() {
  process.exit(1);
});

server.listen(3000, '0.0.0.0', function () {
  let ip = execSync('hostname -i').toString().trim();
  console.log(`api: POST http://${ip}:3000/convert [@file, format, doctype]`);
});