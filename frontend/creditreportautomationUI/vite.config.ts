import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables based on mode
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      port: Number(env.VITE_SERVER_PORT) || 3002,
      host: env.VITE_SERVER_HOST || 'localhost',
      fs: {
        // Allow serving files from parent directories
        allow: ['..', '../..', '../../..']
      },
      // Security: Disable directory listing
      proxy: {
        // Proxy API requests to backend (optional)
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    },
    publicDir: 'public',
    build: {
      // Security: Remove console logs in production
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: mode === 'production',
        },
      },
      // Generate source maps for production debugging (optional)
      sourcemap: mode !== 'production',
    },
    // Define global constants
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    }
  }
})