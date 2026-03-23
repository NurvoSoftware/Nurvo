# Nurvo
## 系統架構
    * Vue.js
    * Eleven LAb
    * Gemini(Huggingface)
    * Fast API
    * Supabase

## UI 參考
[ Canva Link ](https://www.canva.com/design/DAHEF8M_KoU/_A96ERatW-9VF8yBo8md1Q/edit?utm_content=DAHEF8M_KoU&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

## ElevenLabs Agent Skills（AI 編輯器用）

在專案根目錄執行一次即可，會裝到本機的 `.agents/skills/`（Cursor 等）與 `.claude/skills/`（Claude Code）；兩者皆已列入 `.gitignore`，不進版控。

```bash
cd /path/to/Nurvo
npx skills add elevenlabs/skills --yes
```

- 需要 **Node.js**（內建 `npx`）。
- 無互動安裝可加 `--yes`（或 `-y`）。
- 說明與技能列表：[ElevenLabs 智能体技能](https://elevenlabs.io/zh/blog/elevenlabs-agent-skills)

若使用 **Claude Code**，同一指令也會處理對應目錄；若只關心 Cursor，照跑即可。
