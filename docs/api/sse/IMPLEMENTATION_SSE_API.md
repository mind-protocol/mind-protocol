# IMPLEMENTATION: SSE API Module

## CHAIN:
BEHAVIORS: ./BEHAVIORS_SSE_API.md
ALGORITHM: ./ALGORITHM_SSE_API.md
VALIDATION: ./VALIDATION_SSE_API.md
PATTERNS: ./PATTERNS_SSE_API.md
OBJECTIVES: ./OBJECTIVES_SSE_API.md
THIS: ./IMPLEMENTATION_SSE_API.md

## IMPLEMENTATION: Server-Sent Events (SSE) API Code Architecture

This document details the code structure, file responsibilities, design patterns, and data flow within the `app/api/sse` module.

### CODE STRUCTURE

- `app/api/sse/
  └── route.ts

### File Responsibilities

| File          | Line Count | Status | Purpose                                                                       | Notes |
|---------------|------------|--------|-------------------------------------------------------------------------------|-------|
| `route.ts`    | ~30        | OK     | Main entry point for the SSE API. Handles GET requests, manages the event stream, and sends periodic health and heartbeat messages. | Handles Next.js API route for `/api/sse`.|

### DESIGN PATTERNS

- **Server-Sent Events (SSE):** The core pattern, establishing a unidirectional communication channel from server to client over a single HTTP connection.
  - *Why:* Chosen for its simplicity and native browser support for server-to-client streaming, fitting the objective of real-time updates without the overhead of full bidirectional WebSockets.
- **`ReadableStream`:** Utilized to efficiently push data to the client, allowing for asynchronous event generation and backpressure handling.
  - *Where:* `route.ts` uses `new ReadableStream()` to construct the response body.
- **Heartbeat Pattern:** A `setInterval` mechanism is used to send regular `ping` events.
  - *Why:* To keep the connection alive, prevent timeouts, and allow clients to detect server liveness.
  - *Where:* Implemented within the `start` method of the `ReadableStream` in `route.ts`.

### Boundaries

- **Inside:** The `route.ts` file, its event formatting logic, stream management, and the `setInterval` for heartbeat.
- **Outside:** The actual `connectome` health state (currently stubbed), client-side `EventSource` implementation, and network infrastructure (proxies, load balancers).

### Data Flow

1.  **Client Request:** A client (e.g., browser `EventSource`) sends an HTTP `GET` request to `/api/sse`.
2.  **Route Handler Activation:** The `GET` function in `route.ts` is invoked.
3.  **Headers and Stream Setup:**
    - HTTP headers (`Content-Type: text/event-stream`, `Cache-Control: no-cache, no-transform`, `Connection: keep-alive`) are set for the response.
    - A `ReadableStream` is instantiated.
4.  **Initial Event:** Inside the `ReadableStream`'s `start` method, an initial `connectome_health` event (currently with stubbed data) is immediately enqueued to the controller.
5.  **Heartbeat Activation:** A `setInterval` is started to enqueue `ping` events with a timestamp every 15 seconds.
6.  **Response Delivery:** The `ReadableStream` is returned as the body of a `Response` object.
7.  **Client Reception:** The client's `EventSource` continuously receives events from the stream.
8.  **Connection Cancellation:** If the client disconnects or the server terminates the stream, the `cancel` method of the `ReadableStream` is called, which clears the `heartbeat` `setInterval` to prevent resource leaks.

### Dependencies

- **External:** `Next.js` (for API route handling), `Node.js` (`TextEncoder`, `NodeJS.Timeout`).
- **Internal:** Currently no direct internal module dependencies for fetching dynamic health data; the `connectome_health` data is stubbed. Future implementations would likely depend on a `connectome_health_monitor` module or similar.