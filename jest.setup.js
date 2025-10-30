// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props) => {
    // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text
    return <img {...props} />
  },
}))

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock WebSocket
global.WebSocket = class MockWebSocket {
  constructor(url) {
    this.url = url
    this.readyState = 0 // CONNECTING
    this.CONNECTING = 0
    this.OPEN = 1
    this.CLOSING = 2
    this.CLOSED = 3

    // Simulate connection after a tick
    setTimeout(() => {
      this.readyState = 1 // OPEN
      if (this.onopen) this.onopen({ type: 'open' })
    }, 0)
  }

  send(data) {
    // Mock send - do nothing
  }

  close() {
    this.readyState = 3 // CLOSED
    if (this.onclose) this.onclose({ type: 'close', code: 1000 })
  }

  addEventListener(event, callback) {
    this[`on${event}`] = callback
  }

  removeEventListener(event, callback) {
    if (this[`on${event}`] === callback) {
      this[`on${event}`] = null
    }
  }
}

// Suppress console errors/warnings in tests unless DEBUG env var is set
if (!process.env.DEBUG) {
  global.console = {
    ...console,
    error: jest.fn(),
    warn: jest.fn(),
  }
}
