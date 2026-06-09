import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      coverage: {
        exclude: [
          'src/**/*.d.ts',
          'src/**/__tests__/**',
          'src/main.ts',
          'src/types/**',
          'src/env.d.ts',
        ],
        include: ['src/**/*.{ts,vue}'],
        provider: 'v8',
        reporter: ['text', 'html'],
      },
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      root: fileURLToPath(new URL('./', import.meta.url)),
    },
    
  }),
)
