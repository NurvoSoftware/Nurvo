# 實作報告 — harden-web-security

> 日期：2026-06-20 · 變更：`openspec/changes/harden-web-security` · 狀態：實作完成（15/17 任務，2 項因環境延後），尚未 commit

---

## 1. 背景：為什麼做這件事

2026/6/4 用 **HCL AppScan Standard** 對線上站台 `https://meqa.ncu.edu.tw/nurvo/` 做了一次資安掃描，報告列出 **11 個問題**（5 中、5 低、1 參考）。其中 **8 個是缺少 HTTP 安全標頭**，另外是第三方字型缺 SRI、以及一個機密回應可被快取。

這些問題會讓使用者暴露於：XSS／點擊劫持（沒有 CSP）、MIME 嗅探下載攻擊（沒有 nosniff）、跨來源側信道洩漏（沒有 COOP/COEP/CORP）、HTTPS 降級中間人攻擊（沒有 HSTS）、Referrer URL 洩漏、以及第三方 CDN 被入侵的供應鏈攻擊（沒有 SRI）。

### 一個重要前提（掃描對象 ≠ 這個 repo）
被掃的線上站台**不是這個 repo build 出來的**（它有這裡沒有的舊版 Google OAuth、跑在 IIS/ARR 之下、且偵測到 Spring Actuator = 舊的 digiRunner）。所以「修這個 repo」**不會**直接讓線上掃描變乾淨；我們做的是讓**任何由這個 codebase 部署的版本**都能通過掃描。兩個純基建的問題（#1 強制 HTTPS、#6 Spring Actuator）屬於 IIS/NCU 運維端，只記錄、不在這個 repo 實作。

---

## 2. 做了什麼（檔案逐一說明）

### 後端 — 安全標頭 middleware
- **`nurvobackend/middleware/security_headers.py`（新增）** — 一個 `BaseHTTPMiddleware` 子類別，對**每一個**回應掛上 7 個安全標頭，並對 API 回應加上 `Cache-Control: no-store` + `Pragma: no-cache`。
  > **Why（放 app 層而非只放 nginx）：** app 層的標頭跟著應用程式走，不管前面是我們的 nginx、線上的 IIS/ARR、還是開發用的 Vite，都會生效。nginx 只負責它自己送出的靜態檔。
- **`nurvobackend/main.py`（修改）** — 註冊上述 middleware，且**刻意加在 CORS 之前**，讓 `CORSMiddleware` 維持最外層（最後加入 = 最外層），OPTIONS 預檢才能正常短路。
- **`nurvobackend/middleware/__init__.py`（新增）** — 讓 `middleware` 成為 Python package。

### 前端 — 自架字型（取代 Google Fonts CDN）
- **`nurvofronted/index.html`（修改）** — 移除 3 行 Google Fonts `<link>`（兩個 preconnect + 一個 stylesheet）。
- **`nurvofronted/src/main.ts`（修改）** — 改用 `import '@fontsource/inter/{400,500,600,700,800}.css'`，由 Vite 打包、字型檔從**同源** `/assets/` 提供。
- **`nurvofronted/package.json` / `package-lock.json`（修改）** — 新增 `@fontsource/inter` 相依。

### 前端 — nginx 靜態 SPA 標頭
- **`nurvofronted/nginx.conf`（修改）** — 在 `location /`（**只有這個 block**）加 7 個 `add_header … always`。
  > **Why（只放 location /，不放 server 層）：** 若放在 server 層，被代理的 `/api/*` 回應也會被加標頭，而 FastAPI middleware 已經加了 → **標頭重複**。分層所有權（design §D1）：nginx 管靜態、FastAPI 管 API，各管各的。

### 文件
- **`sysdoc/ARCHITECTURE.md`（修改）** — 新增 ADR「2026-06-20 — Baseline HTTP security headers + self-hosted font」，記錄分層決策與兩個設計取捨。
- **`sysdoc/RUNBOOK.md`（修改）** — 新增「Security headers & AppScan remediation」段：列出標頭、部署後 `curl` 驗證指令、以及兩個運維端（IIS）待辦。

### 測試
- **`nurvobackend/tests/test_security_headers.py`（新增，7 測試）** — 驗證標頭存在/值正確、HSTS max-age 足夠、CSP 的 script-src 不含 unsafe、機密回應為 no-store、錯誤回應也有標頭、標頭單值不重複、CORS 預檢不受影響。
- **`nurvofronted/src/__tests__/fonts.no-cdn.spec.ts`（新增，2 測試）** — 驗證 `index.html` 不再引用 Google Fonts CDN、且 `main.ts` 從 `@fontsource/inter` 載入。

---

## 3. 套用的標頭與實際值

```
Content-Security-Policy: default-src 'self'; script-src 'self';
  style-src 'self' 'unsafe-inline'; font-src 'self';
  img-src 'self' data: blob: https:; connect-src 'self' ws: wss:;
  object-src 'none'; base-uri 'self'; frame-ancestors 'none'
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
Cross-Origin-Embedder-Policy: credentialless
Strict-Transport-Security: max-age=31536000; includeSubDomains
Cache-Control: no-store   (API 回應)
Pragma: no-cache          (API 回應)
```

CSP 重點：`script-src 'self'`（不含 `unsafe-inline`/`unsafe-eval`，這是擋 XSS 的關鍵）；`style-src` 保留 `'unsafe-inline'` 因為 Vue/PrimeVue 會注入 runtime inline style。

---

## 4. 過程中的兩個設計修正（重要）

### 修正一：SRI → 自架字型
原計畫是在 Google Fonts `<link>` 釘 SRI `integrity` hash。實作時用兩個不同 User-Agent 抓同一個 Google Fonts URL，**得到兩個不同的 sha384 hash** → 證明 Google 回的 CSS 隨 UA 變動，釘死的 hash 會讓某些瀏覽器整個字型被擋掉（且當下因 auth 牆無法本地驗證）。
> **決定：** 改用 `@fontsource/inter` 自架。這同時：①徹底解決 #2（沒有第三方 CDN 可被竄改）②不會 UA 脆弱 ③字型變同源，不再受 CSP/COEP 影響。這是 design 本來就列為「推薦長期解」的方案。

### 修正二：COEP `require-corp` → `credentialless`
掃描報告建議 `require-corp`，但它會把**沒有 CORP 標頭的跨來源資源整個擋掉**（例如遠端 DALL·E 背景圖）。
> **決定：** 改用 `credentialless`，一樣滿足 AppScan #3，但不會弄壞跨來源圖片。因 auth 牆無法實測，採保守值；等本地環境修好後可再確認是否能升回 `require-corp`。

---

## 5. 驗證結果

| 項目 | 結果 |
|------|------|
| 後端測試 | **29 passed**（22 既有 + 7 新）|
| 前端測試 | 我新增/相關的全綠（唯一失敗 `LevelSelectView` 是 rebase 帶進的既有 authStore/localStorage 問題，已用 git stash 證實與本次無關）|
| `curl -I http://localhost:8080/` | 7 個安全標頭**各出現一次** |
| `curl -I .../api/health` | 標頭 + `Cache-Control: no-store`，**CSP 不重複**（證明分層所有權成立）|
| 前端 build | ✓ Inter woff2 已打包成同源 `/assets/` |
| `openspec validate` | ✓ valid |

---

## 6. AppScan findings 對照（9 個 repo 內問題全覆蓋）

| Finding | 修復位置 |
|---------|----------|
| #2 SRI / 第三方資源 | 自架 Inter 字型（移除 Google CDN）|
| #3 COEP | middleware + nginx：`credentialless` |
| #4 COOP | middleware + nginx：`same-origin` |
| #5 CORP | middleware + nginx：`same-origin` |
| #7 可快取機密回應 | middleware：`Cache-Control: no-store` + `Pragma` |
| #8 CSP | middleware + nginx |
| #9 X-Content-Type-Options | middleware + nginx：`nosniff` |
| #10 HSTS | middleware + nginx：`max-age=31536000; includeSubDomains` |
| #11 Referrer-Policy | middleware + nginx：`strict-origin-when-cross-origin` |

**純基建（不在本 repo，已記錄於 RUNBOOK）：** #1 強制 HTTPS + HSTS preload（IIS/ARR）、#6 Spring Actuator（線上殘留的 digiRunner）。

---

## 7. 延後的事項

- **Task 4.1 互動式煙霧測試** — 載入 SPA 看 console 有無 CSP/COEP 違規。被 rebase 帶進的 auth+Postgres+credits 牆擋住（同 chip 功能遇到的牆）。標頭已用 `curl` 驗證，字型已同源；等本地環境修好後做最終目視確認。

---

## 8. 異動檔案清單

**新增：**
- `nurvobackend/middleware/__init__.py`
- `nurvobackend/middleware/security_headers.py`
- `nurvobackend/tests/test_security_headers.py`
- `nurvofronted/src/__tests__/fonts.no-cdn.spec.ts`

**修改：**
- `nurvobackend/main.py`
- `nurvofronted/index.html` · `src/main.ts` · `nginx.conf` · `package.json` · `package-lock.json`
- `sysdoc/ARCHITECTURE.md` · `sysdoc/RUNBOOK.md`
- `openspec/changes/harden-web-security/{design,specs,tasks}.md`（實作中同步修正）
