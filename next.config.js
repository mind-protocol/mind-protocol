/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow WebSocket connections to visualization_server.py
  async rewrites() {
    return [
      {
        source: '/api/graphs',
        destination: 'http://localhost:8000/api/graphs',
      },
      {
        source: '/ws/:path*',
        destination: 'http://localhost:8000/ws/:path*',
      },
    ]
  },
  // Development settings
  reactStrictMode: true,
  // Optimize for consciousness visualization
  experimental: {
    optimizeCss: true,
  },
}

module.exports = nextConfig
