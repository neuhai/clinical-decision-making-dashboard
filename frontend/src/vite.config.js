import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import commonjs from 'vite-plugin-commonjs';

export default defineConfig({
  plugins: [
    vue(),
    commonjs(), // Add the commonjs plugin
  ],
});