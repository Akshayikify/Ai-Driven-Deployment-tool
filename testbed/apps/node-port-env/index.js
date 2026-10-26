const http = require('http');
const port = process.env.PORT || 5000;
http.createServer((req, res) => res.end('ok')).listen(port, '0.0.0.0');
