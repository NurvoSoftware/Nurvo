/**
 * Regression test for AppScan #2 (harden-web-security): the Inter font is
 * self-hosted via @fontsource, so the SPA entry document must not reference the
 * Google Fonts CDN (no untrusted third-party subresource).
 */
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

// vitest runs with cwd = the frontend project root.
const indexHtml = readFileSync(resolve(process.cwd(), 'index.html'), 'utf-8')
const mainTs = readFileSync(resolve(process.cwd(), 'src/main.ts'), 'utf-8')

describe('fonts — no third-party CDN', () => {
  it('index.html does not reference the Google Fonts CDN', () => {
    expect(indexHtml).not.toContain('fonts.googleapis.com')
    expect(indexHtml).not.toContain('fonts.gstatic.com')
  })

  it('the Inter font is imported from the bundled @fontsource package', () => {
    expect(mainTs).toContain('@fontsource/inter')
  })
})
