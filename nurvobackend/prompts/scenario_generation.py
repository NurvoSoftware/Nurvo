"""Scenario generation prompt template for GPT-4o."""

SCENARIO_GENERATION_PROMPT = """你是一個護理教育情境生成器。請生成一個獨特的疼痛評估護理情境。

請以 JSON 格式回傳以下結構的情境資料：

{
  "patient_profile": {
    "name": "病患全名（繁體中文）",
    "age": 數字,
    "gender": "男" 或 "女",
    "diagnosis": "主要診斷",
    "medications": ["目前用藥列表"],
    "medical_history": ["過去病史列表"],
    "allergies": ["過敏史列表"]
  },
  "pain_details": {
    "location": "疼痛位置",
    "severity": 1到10的數字,
    "type": "疼痛類型（如刺痛、鈍痛、絞痛）",
    "duration": "持續時間",
    "onset": "發作情況",
    "aggravating_factors": ["加重因素"],
    "relieving_factors": ["緩解因素"],
    "associated_symptoms": ["伴隨症狀"]
  },
  "family_member": {
    "name": "家屬姓名",
    "relationship": "與病患關係",
    "personality": "性格類型（如焦慮型、質疑型、沉默型）",
    "emotional_state": "當前情緒狀態描述",
    "interjection_triggers": ["會觸發插話的話題或情況"]
  },
  "communication_challenges": ["這個情境中護理師可能遇到的溝通挑戰"],
  "correct_answers": {
    "expected_info_gathered": ["護理師應該收集到的資訊"],
    "ideal_empathy_phrases": ["理想的同理心回應範例"],
    "ideal_questioning_sequence": ["建議的提問順序"],
    "family_calming_strategies": ["有效的安撫家屬策略"]
  }
}

要求：
1. 每次生成的情境必須獨特，包括不同的疼痛原因、位置和程度
2. 病患的疼痛描述要模糊且不具體，需要護理師透過引導來釐清
3. 家屬的性格要有明確特徵，且會影響溝通過程
4. 所有文字使用繁體中文
5. 情境要符合真實臨床場景
6. 只回傳 JSON，不要有其他文字"""
