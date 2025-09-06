const { PeerServer } = require('peer');
const fs = require('fs');
const path = require('path');

const sslOptions = {
    key: fs.readFileSync(path.join(__dirname, 'ssl', 'key.pem')),
    cert: fs.readFileSync(path.join(__dirname, 'ssl', 'cert.pem'))
};

const peerServer = PeerServer({
    ssl: sslOptions,
    port: 9000,
    path: '/peerjs',
    allow_disconnection: true,
    proxied: true,
    debug: 3,
    key: 'peerjs', // Должно совпадать с клиентским ключом
    corsOptions: {
        origin: '*',
        methods: ['GET', 'POST', 'OPTIONS']
    }
});

peerServer.on('connection', (client) => {
    console.log(`Client connected: ${client.getId()}`);
});

peerServer.on('disconnect', (client) => {
    console.log(`Client disconnected: ${client.getId()}`);
});

console.log('PeerJS server running on port 9000');