"""Scoring evaluation prompt template for GPT-4o."""

SCORING_PROMPT = """你是一位護理溝通教育評分專家。請分析以下護理師與病患/家屬的對話紀錄，並根據五大溝通面向進行評分。

## 情境資訊
{scenario_summary}

## 正確答案基準
應收集的資訊：{expected_info}
理想的同理心回應：{ideal_empathy}
建議的提問順序：{ideal_questioning}
有效的安撫策略：{calming_strategies}

## 對話紀錄
{conversation_transcript}

## 病患狀況摘要（護理師填寫）
{patient_summary}

## 遊戲時間
總用時：{elapsed_seconds} 秒（限時 {time_limit} 秒）

## 評分標準

請根據以下五大面向評分（每項 0-100 分）：

1. **同理心表達**（權重 20%）：護理師是否展現關懷、使用溫暖語調、回應病患的情緒
2. **引導式提問**（權重 25%）：護理師是否用開放式和封閉式問題引導病患描述具體疼痛狀況
3. **家屬安撫**（權重 15%）：護理師是否適時回應家屬、緩解焦慮情緒
4. **資訊採集完整性**（權重 25%）：護理師收集的資訊是否完整（對照正確答案基準）
5. **回應速度與流暢度**（權重 15%）：對話是否流暢、回應是否及時

## 輸出格式

請以 JSON 格式回傳：

{{
  "overall_score": 總分（0-100，按權重計算）,
  "level_label": "優秀"（>=85）/ "良好"（>=70）/ "尚可"（>=55）/ "待改進"（<55）,
  "dimension_scores": {{
    "empathy": 分數,
    "guided_questioning": 分數,
    "family_calming": 分數,
    "info_gathering": 分數,
    "response_fluency": 分數
  }},
  "strengths": [
    "做得好的具體表現（引用對話內容）",
    "至少列出 2 項"
  ],
  "improvements": [
    "可以改進的具體建議（引用對話內容並給出更好的回應範例）",
    "至少列出 3 項"
  ],
  "key_moments": [
    {{
      "elapsed_seconds": 對話發生的時間（秒）,
      "message_id": "相關訊息的 ID",
      "quality": "good" 或 "needs_improvement",
      "description": "為什麼這個時刻很重要的說明"
    }}
  ]
}}

只回傳 JSON，不要有其他文字。"""


def build_scoring_input(
    scenario_summary: str,
    expected_info: str,
    ideal_empathy: str,
    ideal_questioning: str,
    calming_strategies: str,
    conversation_transcript: str,
    patient_summary: str,
    elapsed_seconds: float,
    time_limit: int,
) -> str:
    return SCORING_PROMPT.format(
        scenario_summary=scenario_summary,
        expected_info=expected_info,
        ideal_empathy=ideal_empathy,
        ideal_questioning=ideal_questioning,
        calming_strategies=calming_strategies,
        conversation_transcript=conversation_transcript,
        patient_summary=patient_summary,
        elapsed_seconds=elapsed_seconds,
        time_limit=time_limit,
    )
