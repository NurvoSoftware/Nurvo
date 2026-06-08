/**
 * Regression tests for the digiRunner removal (client side).
 *
 * Lock in that the chat WebSocket connects directly to the FastAPI path-based endpoint
 * `/api/chat/{sessionId}` and no longer uses the `/website/<site>` gateway path or the
 * `session_join` handshake frame.
 */
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { connect, disconnect } from '@/services/wsService'

class FakeWebSocket {
  static OPEN = 1
  static instances: FakeWebSocket[] = []

  readonly url: string
  readyState = FakeWebSocket.OPEN
  sent: string[] = []
  onopen: (() => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onclose: (() => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    FakeWebSocket.instances.push(this)
  }

  send(data: string): void {
    this.sent.push(data)
  }

  close(): void {
    this.onclose?.()
  }
}

describe('wsService — no digiRunner gateway', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    FakeWebSocket.instances = []
    vi.stubGlobal('WebSocket', FakeWebSocket)
    Object.defineProperty(window, 'location', {
      value: { protocol: 'http:', host: 'localhost:5173' },
      writable: true,
    })
  })

  it('builds a path-based /api/chat/{sessionId} URL (not the /website gateway path)', () => {
    connect('abc-123')
    const socket = FakeWebSocket.instances[0]!

    expect(socket.url).toBe('ws://localhost:5173/api/chat/abc-123')
    expect(socket.url).not.toContain('/website')
    expect(socket.url).not.toContain('nurvo-chat')

    disconnect()
  })

  it('does not send a session_join handshake on open', () => {
    connect('abc-123')
    const socket = FakeWebSocket.instances[0]!

    socket.onopen?.()

    expect(socket.sent.some((frame) => frame.includes('session_join'))).toBe(false)

    disconnect()
  })
})
