import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { ChatMessage, FamilySender } from '@/types/game'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const isConnected = ref(false)
  const typingIndicator = ref<'patient' | FamilySender | null>(null)
  const currentTarget = ref<'patient' | FamilySender>('patient')

  function addMessage(message: ChatMessage) {
    messages.value.push(message)
  }

  function setTarget(target: 'patient' | FamilySender) {
    currentTarget.value = target
  }

  function clearMessages() {
    messages.value = []
    typingIndicator.value = null
  }

  function setConnected(connected: boolean) {
    isConnected.value = connected
  }

  function setTyping(sender: 'patient' | FamilySender | null) {
    typingIndicator.value = sender
  }

  function reset() {
    messages.value = []
    isConnected.value = false
    typingIndicator.value = null
    currentTarget.value = 'patient'
  }

  return {
    messages,
    isConnected,
    typingIndicator,
    currentTarget,
    addMessage,
    setTarget,
    clearMessages,
    setConnected,
    setTyping,
    reset,
  }
})
