export interface PatientProfile {
  name: string
  age: number
  gender: string
  diagnosis: string
  medications: string[]
  medical_history: string[]
  allergies: string[]
}

export interface PainDetails {
  location: string
  severity: number
  type: string
  duration: string
  onset: string
  aggravating_factors: string[]
  relieving_factors: string[]
  associated_symptoms: string[]
}

export interface FamilyMember {
  name: string
  relationship: string
  personality: string
  emotional_state: string
  interjection_triggers: string[]
}

export interface CorrectAnswers {
  expected_info_gathered: string[]
  ideal_empathy_phrases: string[]
  ideal_questioning_sequence: string[]
  family_calming_strategies: string[]
}

export interface Scenario {
  id: string
  patient_profile: PatientProfile
  pain_details: PainDetails
  family_member: FamilyMember
  communication_challenges: string[]
  correct_answers: CorrectAnswers
  time_limit_seconds: number
  created_at: string
}

export interface ChatMessage {
  id: string
  sender: 'patient' | 'family' | 'nurse'
  content: string
  timestamp: string
  elapsed_seconds: number
  is_interjection: boolean
  audio_base64?: string
}

export interface PatientRecord {
  session_id: string
  content: string
  submitted_at: string
  time_remaining_seconds: number
}

export interface DimensionScores {
  empathy: number
  guided_questioning: number
  family_calming: number
  info_gathering: number
  response_fluency: number
}

export interface KeyMoment {
  elapsed_seconds: number
  message_id: string
  quality: 'good' | 'needs_improvement'
  description: string
}

export interface ScoreResult {
  session_id: string
  overall_score: number
  level_label: string
  dimension_scores: DimensionScores
  strengths: string[]
  improvements: string[]
  key_moments: KeyMoment[]
}

export interface GameSession {
  session_id: string
  scenario: Scenario
  conversation_history: ChatMessage[]
  current_target: 'patient' | 'family'
  family_interjection_counter: number
  start_time: string
  status: 'briefing' | 'playing' | 'recording' | 'scoring' | 'completed'
}

export type GameStatus =
  | 'idle'
  | 'generating'
  | 'briefing'
  | 'playing'
  | 'recording'
  | 'scoring'
  | 'completed'
  | 'error'

export interface ScenarioGenerateResponse {
  session_id: string
  scenario: Scenario
}

export interface WsNpcMessage {
  type: 'npc_message'
  sender: 'patient' | 'family'
  content: string
  audio_base64?: string
  message_id: string
  elapsed_seconds: number
  is_interjection?: boolean
}

export interface WsTypingMessage {
  type: 'typing'
  sender: 'patient' | 'family'
}

export interface WsTimerMessage {
  type: 'timer_update'
  remaining_seconds: number
}

export interface WsTimerExpired {
  type: 'timer_expired'
  message: string
}

export interface WsErrorMessage {
  type: 'error'
  message: string
  retryable: boolean
}

export type WsServerMessage =
  | WsNpcMessage
  | WsTypingMessage
  | WsTimerMessage
  | WsTimerExpired
  | WsErrorMessage

export interface WsNurseMessage {
  type: 'nurse_message'
  target: 'patient' | 'family'
  content: string
}
