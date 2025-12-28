# BEHAVIORS: SSE API Module

## CHAIN:
PATTERNS: ./PATTERNS_SSE_API.md
OBJECTIVES: ./OBJECTIVES_SSE_API.md
IMPLEMENTATION: ./IMPLEMENTATION_SSE_API.md
THIS: ./BEHAVIORS_SSE_API.md

## BEHAVIORS: Server-Sent Event Stream

### Functionality:

The SSE API module (`app/api/sse`) provides a single, long-lived HTTP endpoint that streams server-generated events to connected clients.

### Inputs:

- **HTTP GET Request:** A client initiates a connection by sending an HTTP GET request to the `/api/sse` endpoint.
  - Headers: The client may send standard HTTP headers. No specific custom headers are required by the SSE endpoint for basic operation.

### Outputs:

The module continuously streams text data formatted according to the Server-Sent Events specification. Each event consists of:
- `event:` (optional) - The event type (e.g., `connectome_health`, `ping`).
- `data:` - The event payload, typically a JSON string.
- Followed by two newlines (`\n\n`) to delimit the event.

#### Key Event Types:

- **`connectome_health` events:**
  - **Trigger:** Periodically generated, or upon significant changes in the `connectome` system's health.
  - **Payload:** A JSON object containing current health metrics, status, and related information for the Connectome system.
  - **Purpose:** Allows frontend clients to display real-time health dashboards.

- **`ping` events:**
  - **Trigger:** Sent at regular intervals (heartbeat).
  - **Payload:** A JSON object, typically containing a timestamp to indicate when the ping was sent.
  - **Purpose:** Keeps the connection alive, prevents timeouts, and allows clients to detect server liveness.

### Side Effects:

- **Persistent HTTP Connection:** A single HTTP/1.1 connection remains open between the server and each connected client for the duration of the stream.
- **Resource Consumption:** Each active connection consumes server resources (memory, network sockets).
- **Client Reconnection:** The server implicitly relies on browser `EventSource` clients to automatically attempt reconnection upon disconnect.

### Error Handling:

- If an error occurs during event generation or streaming, the server will attempt to close the connection gracefully.
- Clients are expected to handle connection errors and implement their own retry logic (which `EventSource` does by default).

### Observability:

- Event types and data payloads can be inspected by clients.
- Server logs may indicate connection establishment, disconnections, and errors.
