const express = require('express');
const multer  = require('multer');
const uuid = require('uuid/v4');
const fs = require('fs');
const { spawn, execSync } = require('child_process');

const app = express();

var storage = multer.diskStorage({
    destination: '/tmp',
    filename: function (req, file, cb) {
      cb(null, uuid() + '.' + file.originalname);
    }
});

const upload = multer({storage: storage});

app.post('/convert', upload.single('file'), function (req, res, next) {
    const format = req.body.format || 'pdf';
    const doctype = req.body.doctype || 'document';
    const args = ['-n', '-v', '-T', '1500', '--stdout',
                  '-d', doctype,
                  '-f', format,
                  req.file.path];
    
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
    });
});

app.listen(3000, '0.0.0.0', function () {
    let ip = execSync('hostname -i').toString().trim();
    console.log(`api: POST http://${ip}:3000/convert [@file, format, doctype]`);
});