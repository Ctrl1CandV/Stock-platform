import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/',
  server: {
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000/',
        // 允许跨域并去掉路径中的api前缀
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, '')
      }
    }
  }
})
