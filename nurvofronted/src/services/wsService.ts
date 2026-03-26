import { useChatStore } from '@/stores/chatStore'
import type { WsServerMessage, WsNurseMessage, ChatMessage } from '@/types/game'

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let currentSessionId: string | null = null
const RECONNECT_DELAY = 3000

// Timer event callbacks
let _onTimerUpdate: ((seconds: number) => void) | null = null
let _onTimerExpired: (() => void) | null = null

/**
 * Register a callback for timer_update events.
 */
export function onTimerUpdate(cb: (seconds: number) => void): void {
  _onTimerUpdate = cb
}

/**
 * Register a callback for timer_expired events.
 */
export function onTimerExpired(cb: () => void): void {
  _onTimerExpired = cb
}

function getWsUrl(sessionId: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.hostname
  return `${protocol}//${host}:8000/api/chat/${sessionId}`
}

function handleMessage(event: MessageEvent) {
  const chatStore = useChatStore()

  let data: WsServerMessage
  try {
    data = JSON.parse(event.data)
  } catch {
    console.error('[wsService] 無法解析伺服器訊息:', event.data)
    return
  }

  switch (data.type) {
    case 'npc_message': {
      const message: ChatMessage = {
        id: data.message_id,
        sender: data.sender,
        content: data.content,
        timestamp: new Date().toISOString(),
        elapsed_seconds: data.elapsed_seconds,
        is_interjection: data.is_interjection ?? false,
        audio_base64: data.audio_base64,
      }
      chatStore.setTyping(null)
      chatStore.addMessage(message)
      break
    }
    case 'typing': {
      chatStore.setTyping(data.sender)
      break
    }
    case 'timer_update': {
      if (_onTimerUpdate) {
        _onTimerUpdate(data.remaining_seconds)
      }
      break
    }
    case 'timer_expired': {
      console.warn('[wsService] 時間已到:', data.message)
      if (_onTimerExpired) {
        _onTimerExpired()
      }
      break
    }
    case 'error': {
      console.error('[wsService] 伺服器錯誤:', data.message)
      break
    }
  }
}

export function connect(sessionId: string) {
  disconnect()
  currentSessionId = sessionId

  const chatStore = useChatStore()
  const url = getWsUrl(sessionId)

  ws = new WebSocket(url)

  ws.onopen = () => {
    chatStore.setConnected(true)
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  ws.onmessage = handleMessage

  ws.onclose = () => {
    chatStore.setConnected(false)
    if (currentSessionId) {
      reconnectTimer = setTimeout(() => {
        if (currentSessionId) {
          connect(currentSessionId)
        }
      }, RECONNECT_DELAY)
    }
  }

  ws.onerror = (error) => {
    console.error('[wsService] WebSocket 錯誤:', error)
  }
}

export function sendMessage(target: 'patient' | 'family', content: string) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.error('[wsService] WebSocket 尚未連線')
    return
  }

  const payload: WsNurseMessage = {
    type: 'nurse_message',
    target,
    content,
  }

  ws.send(JSON.stringify(payload))
}

export function disconnect() {
  currentSessionId = null
  _onTimerUpdate = null
  _onTimerExpired = null

  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }

  if (ws) {
    ws.onclose = null
    ws.close()
    ws = null
  }

  const chatStore = useChatStore()
  chatStore.setConnected(false)
}
