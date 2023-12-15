const WebSocket = require('ws');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function asyncInput() {
  return new Promise((resolve) => {
    rl.question('Enter your message: ', (answer) => {
      resolve(answer);
    });
  });
}

async function asyncSend(ws) {
  while (true) {
    const message = await asyncInput();
    ws.send(message);
  }
}

function asyncReceive(ws) {
  ws.on('message', (data) => {
    console.log(`>>> ${data}`);
  });
}

function run() {
  const ws = new WebSocket('ws://127.0.0.1:8888');

  ws.on('open', () => {
    Promise.all([asyncSend(ws), asyncReceive(ws)]);
  });

  ws.on('close', (code, reason) => {
    console.log(`Connection closed: ${code} ${reason}`);
    process.exit(0);
  });
}

run();
