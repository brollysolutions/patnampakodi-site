// Close only the isolated browser at the loopback port supplied by this audit.
const port = Number(process.argv[2]);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('Expected a loopback Chrome debug port');
}
const controller = new AbortController();
const timer = setTimeout(() => controller.abort(), 10000);
try {
  const response = await fetch(`http://127.0.0.1:${port}/json/version`, {signal: controller.signal});
  if (!response.ok) throw new Error(`Chrome version endpoint returned ${response.status}`);
  const info = await response.json();
  const endpoint = new URL(info.webSocketDebuggerUrl);
  if (endpoint.protocol !== 'ws:' || endpoint.hostname !== '127.0.0.1' || Number(endpoint.port) !== port) {
    throw new Error('Unexpected browser debugger endpoint');
  }
  await new Promise((resolve, reject) => {
    const ws = new WebSocket(endpoint);
    const deadline = setTimeout(() => { ws.close(); reject(new Error('Browser.close timed out')); }, 10000);
    ws.addEventListener('open', () => ws.send(JSON.stringify({id: 1, method: 'Browser.close'})));
    ws.addEventListener('close', () => { clearTimeout(deadline); resolve(); });
    ws.addEventListener('error', () => { clearTimeout(deadline); reject(new Error('Browser close socket failed')); });
    ws.addEventListener('message', event => {
      const message = JSON.parse(event.data);
      if (message.id === 1 && message.error) {
        clearTimeout(deadline);
        ws.close();
        reject(new Error(message.error.message));
      }
    });
  });
} finally {
  clearTimeout(timer);
}
