/** @type {import('next').NextConfig} */
const nextConfig = {
  // Development settings
  reactStrictMode: true,
  // Optimize for consciousness visualization
  experimental: {
    optimizeCss: true,
  },
  // Proxy API requests to Python backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
}

module.exports = nextConfig
