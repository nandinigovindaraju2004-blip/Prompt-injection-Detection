/** @type {import('next').NextConfig} */
const BACKEND_PORT = process.env.BACKEND_PORT || 5000;

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `http://localhost:${BACKEND_PORT}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
