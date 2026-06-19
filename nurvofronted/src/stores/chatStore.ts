import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { ChatMessage, FamilySender, TargetId } from '@/types/game'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const isConnected = ref(false)
  const typingIndicator = ref<'patient' | FamilySender | null>(null)
  // The conversation target(s) the nurse is addressing, shown as chips.
  // Fed by the @ dropdown, the tab buttons, and scene-character clicks.
  const selectedTargetIds = ref<TargetId[]>([])
  const errorMessage = ref<string>('')

  function addMessage(message: ChatMessage) {
    messages.value.push(message)
  }

  function setMessageAudio(messageId: string, audioBase64: string) {
    const message = messages.value.find((item) => item.id === messageId)
    if (message) {
      message.audio_base64 = audioBase64
    }
  }

  // Add a target (de-duped). Choosing 'all' collapses to a single broadcast
  // chip; choosing an individual drops any existing 'all'.
  function addTarget(id: TargetId) {
    if (id === 'all') {
      selectedTargetIds.value = ['all']
      return
    }
    const without = selectedTargetIds.value.filter((t) => t !== 'all')
    selectedTargetIds.value = without.includes(id) ? without : [...without, id]
  }

  // Toggle a target on/off (used by tab buttons and scene clicks).
  function toggleTarget(id: TargetId) {
    if (id === 'all') {
      selectedTargetIds.value = selectedTargetIds.value.includes('all') ? [] : ['all']
      return
    }
    const without = selectedTargetIds.value.filter((t) => t !== 'all')
    selectedTargetIds.value = without.includes(id)
      ? without.filter((t) => t !== id)
      : [...without, id]
  }

  function removeTarget(id: TargetId) {
    selectedTargetIds.value = selectedTargetIds.value.filter((t) => t !== id)
  }

  function clearTargets() {
    selectedTargetIds.value = []
  }

  function clearMessages() {
    messages.value = []
    typingIndicator.value = null
    errorMessage.value = ''
  }

  function setConnected(connected: boolean) {
    isConnected.value = connected
  }

  function setTyping(sender: 'patient' | FamilySender | null) {
    typingIndicator.value = sender
  }

  function setError(message: string) {
    errorMessage.value = message
  }

  function clearError() {
    errorMessage.value = ''
  }

  function reset() {
    messages.value = []
    isConnected.value = false
    typingIndicator.value = null
    selectedTargetIds.value = []
    errorMessage.value = ''
  }

  return {
    messages,
    isConnected,
    typingIndicator,
    selectedTargetIds,
    errorMessage,
    addMessage,
    setMessageAudio,
    addTarget,
    toggleTarget,
    removeTarget,
    clearTargets,
    clearMessages,
    setConnected,
    setTyping,
    setError,
    clearError,
    reset,
  }
})
