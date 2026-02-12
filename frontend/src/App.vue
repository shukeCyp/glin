<script setup>
import { ref, onMounted } from 'vue'
import Toast from './components/Toast.vue'
import Settings from './components/Settings.vue'
import Debug from './components/Debug.vue'
import ImageProcess from './components/ImageProcess.vue'
import ImageGeneration from './components/ImageGeneration.vue'
import VideoGeneration from './components/VideoGeneration.vue'

const state = ref('loading') // loading | pending | activated
const deviceId = ref('')
const activationCode = ref('')
const toastRef = ref(null)
const currentPage = ref('video') // video | image_process | debug | settings
const isDevMode = ref(false)

const checkStatus = async () => {
  try {
    const res = await window.pywebview.api.get_status()
    state.value = res.state
    if (res.state === 'pending') {
      deviceId.value = res.device_id
    }
    // 获取应用信息（是否开发模式）
    try {
      const info = await window.pywebview.api.get_app_info()
      isDevMode.value = info.is_dev
    } catch { /* ignore */ }
  } catch {
    setTimeout(checkStatus, 100)
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    toastRef.value?.show('已复制到剪贴板', 'success')
  } catch {
    toastRef.value?.show('复制失败', 'error')
  }
}

const handleActivate = async () => {
  if (!activationCode.value.trim()) {
    toastRef.value?.show('请输入激活码', 'error')
    return
  }

  const res = await window.pywebview.api.activate(activationCode.value)
  if (res.ok) {
    toastRef.value?.show('激活成功', 'success')
    state.value = 'activated'
  } else {
    toastRef.value?.show(res.msg || '激活失败', 'error')
  }
}

onMounted(() => {
  checkStatus()
})
</script>

<template>
  <div class="app-shell">
    <div class="bg-glow bg-glow--top"></div>
    <div class="bg-glow bg-glow--bottom"></div>

    <!-- Loading -->
    <div v-if="state === 'loading'" class="login-card">
      <div class="brand">
        <div class="brand-mark"></div>
        <div>
          <div class="brand-title">万米霖</div>
          <div class="brand-subtitle">Loading...</div>
        </div>
      </div>
    </div>

    <!-- Pending activation -->
    <div v-else-if="state === 'pending'" class="login-card">
      <div class="brand">
        <div class="brand-mark"></div>
        <div>
          <div class="brand-title">万米霖</div>
          <div class="brand-subtitle">设备激活</div>
        </div>
      </div>

      <div class="info-section">
        <div class="info-row">
          <span class="info-label">设备ID</span>
          <div class="info-value-row">
            <code class="info-code">{{ deviceId }}</code>
            <button class="copy-btn" @click="copyToClipboard(deviceId)">复制</button>
          </div>
        </div>
        <p class="info-hint">请将设备ID发送给管理员获取激活码</p>
      </div>

      <form class="login-form" @submit.prevent="handleActivate">
        <label class="field">
          <span class="field-label">激活码</span>
          <input
            v-model="activationCode"
            type="text"
            autocomplete="off"
            placeholder="请输入激活码"
          />
        </label>
        <button class="primary-btn" type="submit">激活</button>
      </form>
    </div>

    <!-- Activated / Main view with sidebar -->
    <div v-else-if="state === 'activated'" class="main-layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="brand brand--small">
            <div class="brand-mark"></div>
            <div class="brand-title">万米霖</div>
          </div>
        </div>
        
        <nav class="sidebar-nav">
          <button
            :class="['nav-item', { active: currentPage === 'video' }]"
            @click="currentPage = 'video'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="23 7 16 12 23 17 23 7"></polygon>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
            </svg>
            <span>视频生成</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'image_process' }]"
            @click="currentPage = 'image_process'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <span>图片处理</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'image_gen' }]"
            @click="currentPage = 'image_gen'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="12" y1="8" x2="12" y2="16"/>
              <line x1="8" y1="12" x2="16" y2="12"/>
            </svg>
            <span>图片生成</span>
          </button>
          <button
            v-if="isDevMode"
            :class="['nav-item', { active: currentPage === 'debug' }]"
            @click="currentPage = 'debug'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path>
              <path d="M12 6v6l4 2"></path>
            </svg>
            <span>调试</span>
          </button>
        </nav>

        <div class="sidebar-footer">
          <button
            :class="['nav-item', { active: currentPage === 'settings' }]"
            @click="currentPage = 'settings'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            <span>设置</span>
          </button>
        </div>
      </aside>

      <!-- Main content -->
      <main class="main-content">
        <!-- Video page -->
        <VideoGeneration
          v-show="currentPage === 'video'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- Image Process page -->
        <ImageProcess
          v-show="currentPage === 'image_process'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- Image Generation page -->
        <ImageGeneration
          v-show="currentPage === 'image_gen'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- Debug page (dev mode only) -->
        <Debug
          v-if="isDevMode"
          v-show="currentPage === 'debug'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- Settings page -->
        <Settings
          v-show="currentPage === 'settings'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />
      </main>
    </div>

    <Toast ref="toastRef" />
  </div>
</template>
