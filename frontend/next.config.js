/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    tsconfigPath: './tsconfig.json',
  },
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/graphql/:path*',
        destination: 'http://localhost:8000/graphql/:path*',
      },
      {
        source: '/api/gatekeeper/:path*',
        destination: 'http://localhost:8001/:path*',
      },
    ]
  },
}

module.exports = nextConfig