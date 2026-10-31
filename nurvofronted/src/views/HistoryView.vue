<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/shared/NavBar.vue'
import { fetchHistory } from '@/services/apiService'
import type { HistoryItem } from '@/types/game'

const router = useRouter()

const items = ref<HistoryItem[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    items.value = await fetchHistory()
  } catch {
    error.value = '無法載入遊玩紀錄，請稍後再試'
  } finally {
    loading.value = false
  }
})

function formatDate(iso: string): string {
  const d = new Date(iso)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}  ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const difficultyLabel: Record<string, string> = {
  easy: '入門',
  medium: '標準',
  hard: '進階',
}

function scoreClass(score: number): string {
  if (score >= 85) return 'score-excellent'
  if (score >= 70) return 'score-good'
  if (score >= 55) return 'score-fair'
  return 'score-poor'
}

function viewDetail(sessionId: string) {
  router.push(`/history/${sessionId}`)
}
</script>

<template>
  <div class="history-page">
    <div class="bg-glow bg-glow--left"></div>
    <div class="bg-glow bg-glow--right"></div>

    <NavBar />

    <main class="history-shell">
      <div class="history-container">
        <h2 class="page-title">歷史遊玩報告</h2>

        <div v-if="loading" class="state-box">
          <div class="spinner" />
          <p>載入中...</p>
        </div>

        <div v-else-if="error" class="state-box">
          <p class="error-text">{{ error }}</p>
        </div>

        <div v-else-if="items.length === 0" class="state-box">
          <p class="empty-text">還沒有遊玩紀錄，快去開始第一局吧！</p>
          <button class="btn btn-primary" @click="router.push('/')">回首頁</button>
        </div>

        <div v-else class="table-wrap">
          <table class="history-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>難度</th>
                <th>情境</th>
                <th>分數</th>
                <th>等級</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.session_id">
                <td class="col-date">{{ formatDate(item.completed_at) }}</td>
                <td>
                  <span class="badge" :class="`badge--${item.difficulty}`">
                    {{ difficultyLabel[item.difficulty] ?? item.difficulty }}
                  </span>
                </td>
                <td class="col-scenario">
                  <span v-if="item.patient_name">
                    {{ item.patient_name }}
                    <span class="diagnosis">{{ item.patient_diagnosis }}</span>
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span
                    v-if="item.overall_score !== null"
                    class="score-num"
                    :class="scoreClass(item.overall_score)"
                  >
                    {{ item.overall_score }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span v-if="item.level_label" class="level-badge">{{ item.level_label }}</span>
                  <span v-else class="text-muted">進行中</span>
                </td>
                <td>
                  <button
                    v-if="item.overall_score !== null"
                    class="btn btn-sm"
                    @click="viewDetail(item.session_id)"
                  >
                    查看報告
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.history-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 12%, #dbeafe 0%, transparent 30%),
    radial-gradient(circle at 84% 8%, #e0f2fe 0%, transparent 34%),
    #f8fbff;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(52px);
  pointer-events: none;
  opacity: 0.3;
}

.bg-glow--left {
  width: 320px;
  height: 320px;
  left: -100px;
  top: 72px;
  background: #60a5fa;
}

.bg-glow--right {
  width: 340px;
  height: 340px;
  right: -120px;
  top: 64px;
  background: #7dd3fc;
}

.history-shell {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

.history-container {
  background: linear-gradient(160deg, rgba(255,255,255,0.56) 0%, rgba(255,255,255,0.3) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(219,234,254,0.88);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 24px 52px rgba(15,23,42,0.12);
}

.page-title {
  margin: 0 0 28px;
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 200px;
  color: #64748b;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-text { color: #dc2626; }
.empty-text { font-size: 16px; }

/* Table */
.table-wrap {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.history-table th {
  text-align: left;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e2e8f0;
}

.history-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
  vertical-align: middle;
}

.history-table tr:last-child td {
  border-bottom: none;
}

.history-table tbody tr:hover td {
  background: rgba(241,245,249,0.5);
}

.col-date {
  white-space: nowrap;
  font-size: 13px;
  color: #475569;
}

.col-scenario {
  max-width: 220px;
}

.diagnosis {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.text-muted {
  color: #94a3b8;
}

/* Difficulty badge */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
}

.badge--easy    { background: #dcfce7; color: #166534; }
.badge--medium  { background: #dbeafe; color: #1e40af; }
.badge--hard    { background: #fee2e2; color: #991b1b; }

/* Score */
.score-num {
  font-size: 18px;
  font-weight: 800;
}
.score-excellent { color: #16a34a; }
.score-good      { color: #2563eb; }
.score-fair      { color: #ca8a04; }
.score-poor      { color: #dc2626; }

/* Level badge */
.level-badge {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

/* Buttons */
.btn {
  padding: 8px 18px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  color: #fff;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 13px;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.btn-sm:hover {
  background: #dbeafe;
}
</style>
