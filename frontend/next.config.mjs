/** @type {import('next').NextConfig} */
const nextConfig = {
    // Enable standalone output for Docker
    output: 'standalone',
    async rewrites() {
        // In Docker, BACKEND_URL will be "http://backend:8000"
        // In local dev, it falls back to localhost
        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
        return [
            {
                source: '/api/:path*',
                destination: `${backendUrl}/api/:path*`,
            },
        ];
    },
};

export default nextConfig;
