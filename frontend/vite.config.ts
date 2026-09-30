import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true, // Prevents silent port jumping to 5174/5175 if 5173 is in use
    host: '0.0.0.0',  // Binds to all interfaces, allowing reliable connection via 127.0.0.1 and localhost
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
