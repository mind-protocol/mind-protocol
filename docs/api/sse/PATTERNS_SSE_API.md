# PATTERNS: SSE API Module

## CHAIN:
- app/api/sse/route.ts
- modules.yaml

## PATTERN: Server-Sent Events (SSE) Endpoint

### Overview:

The `app/api/sse` module implements a standard Server-Sent Events (SSE) endpoint, providing a continuous stream of events to connected clients over a single HTTP connection. This pattern is suitable for scenarios where the server needs to push updates to clients in real-time without requiring client-initiated requests.

### Principles:

- **Simplicity:** SSE is simpler than WebSockets for one-way server-to-client communication.
- **Event-driven:** Communication is based on discrete events, each with a name and data payload.
- **Connection longevity:** A single HTTP connection is kept open for the duration of the stream.
- **Automatic reconnection:** Browsers typically handle automatic reconnection for SSE streams.

### Structure:

- **`route.ts`:** The main entry point for the SSE API.
  - Defines the `GET` handler responsible for initiating and managing the SSE stream.
  - Sets appropriate `Content-Type` and `Cache-Control` headers for SSE.
  - Utilizes `ReadableStream` to send event data to the client.
  - Includes a heartbeat mechanism (e.g., "ping" events) to keep the connection alive.
  - Formats events according to the SSE specification (`event: <name>\ndata: <payload>\n\n`).

### Usage:

Clients can connect to the SSE endpoint using `EventSource` in browsers or similar libraries in other environments.

```javascript
const eventSource = new EventSource('/api/sse');

eventSource.onmessage = (event) => {
  console.log('Received message:', event.data);
};

eventSource.addEventListener('connectome_health', (event) => {
  console.log('Connectome health update:', JSON.parse(event.data));
});

eventSource.addEventListener('ping', (event) => {
  console.log('Ping received:', JSON.parse(event.data));
});

eventSource.onerror = (error) => {
  console.error('EventSource failed:', error);
  eventSource.close();
};
```

### Constraints:

- **HTTP/1.1 limitations:** While persistent, SSE still operates over HTTP/1.1, potentially limiting the number of concurrent connections compared to WebSockets.
- **No bidirectional communication:** Not suitable for scenarios where clients also need to send frequent messages to the server over the same channel.

## RELATED PATTERNS:

- **Health Checks:** The inclusion of `connectome_health` events aligns with patterns for monitoring service health.
- **Heartbeat:** The "ping" mechanism is a common pattern for maintaining persistent connections and detecting client liveness.