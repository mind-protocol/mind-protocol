const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Development settings
  reactStrictMode: true,
  // Disable TypeScript and ESLint errors during build
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Output configuration for Vercel
  output: 'standalone',
  // Trailing slash configuration
  trailingSlash: false,
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
  webpack(config, { dev }) {
    config.resolve = config.resolve || {};
    config.resolve.alias = config.resolve.alias || {};
    config.resolve.alias['pino-pretty'] = path.resolve(__dirname, 'app/lib/pinoPrettyStub.cjs');

    if (dev) {
      config.watchOptions = config.watchOptions || {};
      const ignored = config.watchOptions.ignored || [];
      const ignoredList = Array.isArray(ignored) ? ignored : [ignored].filter(Boolean);
      config.watchOptions.ignored = [
        ...ignoredList,
        /C:\\(DumpStack\.log\.tmp|hiberfil\.sys|pagefile\.sys|swapfile\.sys)$/i
      ];
    }

    return config;
  },
}

module.exports = nextConfig
