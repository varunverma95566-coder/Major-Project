import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({ command, mode }) => {
  const isProd = command === 'build' || mode === 'production';
  const base = process.env.VITE_BASE_PATH || (isProd ? '/Major-Project/' : '/');

  return {
    base,
    plugins: [
      tailwindcss(),
      react()
    ],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        }
      }
    }
  };
});
