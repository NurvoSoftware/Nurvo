import type { ScenarioGenerateResponse, ScoreResult } from '@/types/game'

const API_BASE = '/api'
const MAX_RETRIES = 2
const RETRY_DELAY_MS = 2000

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function getErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return '請求格式錯誤，請檢查輸入內容'
    case 401:
    case 403:
      return '認證失敗，請重新登入'
    case 404:
      return '找不到請求的資源'
    case 408:
      return '請求逾時，請稍後再試'
    case 429:
      return '請求過於頻繁，請稍後再試'
    case 500:
      return '伺服器內部錯誤，請稍後再試'
    case 502:
      return '服務暫時無法使用，請稍後再試'
    case 503:
      return '伺服器維護中，請稍後再試'
    case 504:
      return '伺服器回應逾時，請稍後再試'
    default:
      return `請求失敗（${status}），請稍後再試`
  }
}

function isRetryable(status: number): boolean {
  return status === 503 || status === 502 || status === 504 || status === 408 || status === 429
}

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  let lastError: Error | null = null

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000)

      const response = await fetch(`${API_BASE}${url}`, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const shouldRetry = isRetryable(response.status) && attempt < MAX_RETRIES

        if (shouldRetry) {
          lastError = new Error(getErrorMessage(response.status))
          await delay(RETRY_DELAY_MS)
          continue
        }

        // Try to get server error message, fall back to localized message
        const errorBody = await response.json().catch(() => null)
        const message = errorBody?.detail || errorBody?.message || getErrorMessage(response.status)
        throw new Error(message)
      }

      return response.json()
    } catch (err: any) {
      if (err.name === 'AbortError') {
        lastError = new Error('請求逾時，請檢查網路連線後再試')
      } else if (err instanceof TypeError && err.message.includes('fetch')) {
        lastError = new Error('無法連線至伺服器，請檢查網路連線')
      } else if (err instanceof Error) {
        lastError = err
      } else {
        lastError = new Error('發生未知錯誤，請稍後再試')
      }

      // Only retry on network-level errors, not on thrown HTTP errors
      if (attempt < MAX_RETRIES && (err.name === 'AbortError' || (err instanceof TypeError && err.message.includes('fetch')))) {
        await delay(RETRY_DELAY_MS)
        continue
      }

      throw lastError
    }
  }

  throw lastError || new Error('請求失敗，請稍後再試')
}

export async function generateScenario(): Promise<ScenarioGenerateResponse> {
  return request<ScenarioGenerateResponse>('/scenario/generate', { method: 'POST' })
}

export async function submitRecord(
  sessionId: string,
  content: string,
): Promise<{ status: string; session_id: string }> {
  return request('/record/submit', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, content }),
  })
}

export async function evaluateScore(sessionId: string): Promise<ScoreResult> {
  return request<ScoreResult>('/score/evaluate', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })
}
