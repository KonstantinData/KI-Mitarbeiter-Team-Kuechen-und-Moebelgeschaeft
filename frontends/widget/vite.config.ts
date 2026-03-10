import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Vite Config für das Chat-Widget.
 * Baut als IIFE-Bundle (ein JS + ein CSS File) — einbettbar auf jeder Website.
 */
export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: 'src/main.tsx',
      name: 'KITeamWidget',
      fileName: 'loader',
      formats: ['iife'],
    },
    rollupOptions: {
      // React in Bundle einschließen (kein externes React auf Kunden-Website)
      external: [],
    },
    outDir: 'dist',
    cssCodeSplit: false,
  },
});
