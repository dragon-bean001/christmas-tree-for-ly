import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/christmas-tree-for-ly/',  // 将这里替换为你的GitHub仓库名称
})
