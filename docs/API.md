# Nurvo API 文件

後端採 **FastAPI**。

---

## API 治理：OpenTPI（digiRunner）

對外由 **[OpenTPI](https://tpi.dev/)** 生態下的開源 **API 管理平台 [digiRunner](https://github.com/TPIsoftwareOSPO/digiRunner-Open-Source)** 統一管理 Nurvo 的 HTTP API（與 `SPEC.md` 的「DigiRunner」為同一套）。

| 層級 | 角色 |
|------|------|
| **digiRunner** | 閘道與治理：路由、驗證、流量／配額、報表等；支援匯入 **OpenAPI 3.1+**，與 FastAPI 產出的規格對齊。 |
| **FastAPI（nurvobackend）** | 實作業務邏輯；本機／內網直連時仍以 `/docs`、`/openapi.json` 為開發用真相來源。 |

**約定**

- **規格單一真相**：路由與 schema 以 **FastAPI → OpenAPI** 為準，再匯入／同步至 digiRunner（部署流程依你們 DevOps 定）。
- **前端呼叫**：正式環境基底 URL 應指向 **digiRunner 對外入口**（而非裸 FastAPI），除非開發模式另有 proxy。
- **金鑰與限流**：API Key / OAuth / JWT 等由 digiRunner 與後端約定，細節實作後補到此節。

---

## 產品流程（與 API 邊界）

### 關卡頁（第一屏）

- 使用者看到 **10 個關卡**；**目前僅 1 個關卡可進入**（其餘可為 disabled 或占位）。
- 前端 **不必** 為「每個關卡」各呼叫一支 API；可靜態配置 `levelId` / `enabled`，或單一 `GET` 取得關卡列表（可選）。
- 進入**唯一可用關卡**後，切換到 **情境對話頁（第二屏）**，開始一場有時間上限的模擬。

### 情境對話頁（第二屏）

單回合流程（會重複多次直到時間到）：

1. **病患／情境發話**：後端用 **LLM** 依 **教案**（情境 prompt、角色、目標）產生**文字**。
2. **語音**：該文字送 **ElevenLabs TTS**，產生音訊（檔案 URL、`base64` 或串流，實作時定）。
3. **前端播放**音訊（例如底部波形／播放器 UI）。
4. **護士**按「回覆」後以**語音**作答；經 **STT（語音轉文字）** 得到文字後，將**文字**送回後端（實作可為瀏覽器語音辨識、音訊上傳後由後端轉寫、或 **ElevenLabs Scribe** 等，細節另定）。
5. 後端把護士文字併入對話脈絡，再產生下一輪病患／情境文字 → 再 TTS → 再播放 → **迴圈**。
6. **結束條件**：例如 **約 5 分鐘**到點（以前端計時或後端 `session_expires_at` 對齊）；亦可預留「情境完成」提早結束。

```
病患側：教案 + 歷史 ──► LLM ──► 文字 ──► ElevenLabs TTS ──► 音訊 ──► 播放

護士側：麥克風 ──► STT ──► nurse_text ──► 後端（併入歷史） ──► 下一輪 LLM …
```

---

## 初期範圍：一個「可玩關卡」對應的後端介面

目標是 **MVP 只實作一條情境**時，後端仍可收斂成 **少數路由**（甚至 **單一 REST 資源** 用 `phase` 區分首輪／回覆）。

建議慣例：`/api/v1/...`（實作時與 OpenAPI 一致）。

### 方案 A：單一路徑，用 phase 合併「開局」與「回覆」（適合「只要一個 API」的說法）

| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/api/v1/simulation/turn` | `phase: start` 建立 session 並回第一輪病患文字 + 音訊；`phase: reply` 帶上護士內容，回下一輪 |

**`start` 請求（示意）**

```json
{
  "phase": "start",
  "level_id": "level_01"
}
```

**`reply` 請求（示意）**

```json
{
  "phase": "reply",
  "session_id": "uuid",
  "nurse_message": "您好，請問哪裡不舒服？"
}
```

**回應（示意，兩種 phase 可共用形狀）**

```json
{
  "session_id": "uuid",
  "patient_text": "我從昨天開始一直頭暈……",
  "audio": {
    "format": "mp3",
    "url": "https://…"
  },
  "ends_at": "2026-03-18T12:10:00Z"
}
```

- `ends_at`：後端依 **5 分鐘**（或設定）給出結束時間，前端倒數或到點關閉。
- 若僅前端計時，可省略 `ends_at`，但 **伺服器仍應拒絕過期 session**，避免篡改時間。

### 方案 B：拆成兩支路由（可讀性較好，仍只有「一個情境」）

| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/api/v1/sessions` | 開局：教案 + level → 第一輪病患文字 + 音訊 + `session_id` |
| `POST` | `/api/v1/sessions/{session_id}/messages` | 護士一則訊息 → 下一輪病患文字 + 音訊 |

---

## 關卡列表（可選）

若首頁要動態顯示「哪一關可點」：

| 方法 | 路徑 | 說明 |
|------|------|------|
| `GET` | `/api/v1/levels` | 回傳 10 筆關卡 metadata（`id`, `title`, `enabled` 等） |

MVP 若全前端寫死，可暫不實作。

---

## 其他

| 方法 | 路徑 | 說明 |
|------|------|------|
| `GET` | `/health` | 健康檢查 |

---

## 基底 URL

| 環境 | Base URL |
|------|----------|
| 本機開發 | `http://localhost:8000`（埠號以實際 `uvicorn` 為準） |
| 正式 | _待部署後補上_ |

所有路徑除非註明，皆為 **REST + JSON**，`Content-Type: application/json`。

---

## 認證

_待實作後補上_（例如：Bearer JWT、Supabase session 轉發等）。

---

## 錯誤格式

建議統一錯誤 body（與 FastAPI `HTTPException` / 自訂 handler 對齊後再定稿）：

```json
{
  "detail": "人類可讀說明"
}
```

常見 HTTP 狀態碼：400、401、403、404、422、429、500。

---

## OpenAPI（單一真相）

服務跑起來後：

- **Swagger UI**：`{BASE_URL}/docs`
- **ReDoc**：`{BASE_URL}/redoc`
- **OpenAPI JSON**：`{BASE_URL}/openapi.json`

本檔描述 **產品流程與約定**；**欄位與型別** 以 **Pydantic model + OpenAPI** 為準。

---

## 後續可擴充（非 MVP 必須）

- **WebSocket**：串流 TTS 或串流 LLM token。
- **鍵盤輸入**：護士改以打字回覆（除 STT 外的輸入方式）。
- **多關卡**：`level_id` / 教案 ID 對應不同 prompt，路由可不變。

---

## 變更紀錄

| 日期 | 變更 |
|------|------|
| 2026-03-18 | 建立文件骨架 |
| 2026-03-18 | 補充關卡頁／情境頁流程、LLM→ElevenLabs 迴圈、單關卡 API 方案 A/B |
| 2026-03-18 | 護士回覆改為 **STT 為主**；鍵盤輸入列為可選擴充 |
