const { PeerServer } = require('peer');
const https = require('https');
const fs = require('fs');

// Пути к SSL сертификатам (замените на свои)
const options = {
  key: fs.readFileSync('/path/to/your/private.key'),
  cert: fs.readFileSync('/path/to/your/certificate.crt')
};

// Создаем HTTPS сервер
const server = https.createServer(options);

const peerServer = PeerServer({
  port: 9000,
  path: '/peerjs',
  ssl: options,
  allow_discovery: true,
  proxied: true
});

console.log('Secure PeerJS сервер запущен на https://yourdomain.com:9000');