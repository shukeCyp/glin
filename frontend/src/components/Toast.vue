<script setup>
import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

const show = (message, type = 'info', duration = 3000) => {
  const id = ++toastId
  toasts.value.push({ id, message, type })
  
  setTimeout(() => {
    remove(id)
  }, duration)
}

const remove = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

defineExpose({ show })
</script>

<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast--${toast.type}`]"
        @click="remove(toast.id)"
      >
        {{ toast.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  background: rgba(30, 34, 48, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px);
  cursor: pointer;
  pointer-events: auto;
  max-width: 320px;
}

.toast--success {
  border-color: rgba(74, 222, 128, 0.4);
  background: linear-gradient(135deg, rgba(30, 34, 48, 0.95), rgba(34, 60, 48, 0.95));
}

.toast--error {
  border-color: rgba(248, 113, 113, 0.4);
  background: linear-gradient(135deg, rgba(30, 34, 48, 0.95), rgba(60, 34, 34, 0.95));
}

.toast--info {
  border-color: rgba(96, 165, 250, 0.4);
  background: linear-gradient(135deg, rgba(30, 34, 48, 0.95), rgba(34, 48, 60, 0.95));
}

/* Transitions */
.toast-enter-active {
  transition: all 0.3s ease-out;
}

.toast-leave-active {
  transition: all 0.2s ease-in;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
