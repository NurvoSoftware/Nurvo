"""Scenario generation prompt template for GPT-4o."""

SCENARIO_GENERATION_PROMPT = """你是一個護理教育情境生成器。請生成一個獨特的疼痛評估護理情境。

請以 JSON 格式回傳以下結構的情境資料：

{
  "patient_profile": {
    "name": "病患全名（繁體中文，姓+名）",
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
  "family_members": [
    {
      "name": "家屬1姓名（預設與病患同姓）",
      "relationship": "與病患的家庭關係，必須為以下之一：配偶、父、母、兒子、女兒、哥哥、姊姊、弟弟、妹妹、祖父、祖母、外祖父、外祖母、孫子、孫女、外孫、外孫女、媳婦、女婿、伯父、叔叔、姑姑、舅舅、阿姨、堂兄弟姊妹、表兄弟姊妹",
      "personality": "性格類型（如焦慮型、質疑型、沉默型）",
      "emotional_state": "當前情緒狀態描述",
      "interjection_triggers": ["會觸發插話的話題或情況"]
    },
    {
      "name": "家屬2姓名（預設與病患同姓；若為配偶或媳/婿，可為不同姓）",
      "relationship": "與病患的家庭關係（不同於家屬1，且仍須來自上述家庭關係清單）",
      "personality": "性格類型（不同於家屬1）",
      "emotional_state": "當前情緒狀態描述",
      "interjection_triggers": ["會觸發插話的話題或情況"]
    },
    {
      "name": "家屬3姓名（預設與病患同姓；若為配偶或媳/婿，可為不同姓）",
      "relationship": "與病患的家庭關係（不同於家屬1和2，且仍須來自上述家庭關係清單）",
      "personality": "性格類型（不同於家屬1和2）",
      "emotional_state": "當前情緒狀態描述",
      "interjection_triggers": ["會觸發插話的話題或情況"]
    }
  ],
  "communication_challenges": ["這個情境中護理師可能遇到的溝通挑戰"],
  "correct_answers": {
    "expected_info_gathered": ["護理師應該收集到的資訊"],
    "ideal_empathy_phrases": ["理想的同理心回應範例"],
    "ideal_questioning_sequence": ["建議的提問順序"],
    "family_calming_strategies": ["有效的安撫家屬策略"]
  }
}

要求：
1. 每次生成的情境必須獨特，包括不同的疼痛原因、位置和程度。
2. 病患的疼痛描述要模糊且不具體，需要護理師透過引導來釐清。
3. 必須生成 3 位家屬，每位的姓名、與病患關係、性格類型各不相同，且會影響溝通過程。
4. 家屬的 relationship 欄位**只能**是家庭成員關係（配偶、父/母、子/女、兄/姊/弟/妹、祖父母、外祖父母、孫子女、外孫子女、媳婦、女婿、伯叔姑舅姨、堂/表兄弟姊妹）。**禁止**出現醫師、主治醫師、護理師、住院醫師、藥師、社工、看護、照護員、朋友、同事、鄰居、同學、老闆、老師、學生等任何非家屬角色。
5. 家屬的姓氏規則：三位家屬的姓氏原則上與 `patient_profile.name` 的姓氏**相同**。僅當該家屬是配偶、媳婦或女婿時，可以使用不同的姓氏；其他所有家庭關係（父母、子女、手足、祖父母、孫子女、伯叔姑舅姨、堂/表親）皆**必須**與病患同姓。至少要有一位家屬與病患同姓。
6. 三位家屬必須是真實同家族的合理組合，例如「配偶＋子女」「子女＋父母」「子女＋手足」「配偶＋子女＋父母」，而非隨機湊三個不相關的人。
7. 所有文字使用繁體中文。
8. 情境要符合真實臨床場景。
9. 只回傳 JSON，不要有其他文字。"""
