import { defineConfig } from 'vite';
import path from 'path';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'serve-js-as-static',
      configureServer(server) {
        // 拦截.js文件请求，直接返回静态文件
        server.middlewares.use((req, res, next) => {
          if (req.url.startsWith('/js/') && req.url.endsWith('.js')) {
            const fs = require('fs');
            const filePath = path.join(__dirname, 'frontend', req.url);
            if (fs.existsSync(filePath)) {
              const content = fs.readFileSync(filePath, 'utf8');
              res.setHeader('Content-Type', 'application/javascript');
              res.end(content);
              return;
            }
          }
          next();
        });
      }
    }
  ],
  
  // 项目根目录
  root: 'frontend',
  
  // 构建输出目录
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'frontend/index.html')
      }
    }
  },
  
  // 开发服务器配置
  server: {
    port: 5000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    },
    hmr: {
      overlay: true
    }
  }
});