<script setup>
import { ref, onMounted } from 'vue'
import Toast from './components/Toast.vue'
import Settings from './components/Settings.vue'
import NanoBanana from './components/NanoBanana.vue'
import GlinVeo from './components/GlinVeo.vue'
import VeoGeneration from './components/VeoGeneration.vue'
import Sora2Generation from './components/Sora2Generation.vue'
import VeoProduct from './components/VeoProduct.vue'
import VideoProduct from './components/VideoProduct.vue'
import MultiShotVideoProduct from './components/MultiShotVideoProduct.vue'
import VeoQihao from './components/VeoQihao.vue'
import Debug from './components/Debug.vue'

const isDevMode = ref(false)

const state = ref('loading')
const deviceId = ref('')
const activationCode = ref('')
const toastRef = ref(null)
const currentPage = ref('nanobanana')
const glinVeoRef = ref(null)

const handleAddVeoTask = (taskData) => {
  currentPage.value = 'veo'
  setTimeout(() => {
    glinVeoRef.value?.addExternalTask(taskData)
  }, 50)
}

const loadTheme = async () => {
  try {
    const settings = await window.pywebview.api.get_all_settings()
    if (settings.theme) {
      document.documentElement.setAttribute('data-theme', settings.theme)
    }
  } catch { /* ignore */ }
}

const checkStatus = async () => {
  try {
    const res = await window.pywebview.api.get_status()
    state.value = res.state
    if (res.state === 'pending') {
      deviceId.value = res.device_id
    }
    // pywebview 已就绪，检测调试模式
    try {
      const settings = await window.pywebview.api.get_all_settings()
      isDevMode.value = settings.__dev_mode__ === '1'
      if (settings.theme) {
        document.documentElement.setAttribute('data-theme', settings.theme)
      }
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
            :class="['nav-item', { active: currentPage === 'nanobanana' }]"
            @click="currentPage = 'nanobanana'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <span>香蕉生图</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'video_product' }]"
            @click="currentPage = 'video_product'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="14" rx="2" ry="2"/>
              <polygon points="11 9 16 12 11 15 11 9"/>
              <line x1="8" y1="20" x2="16" y2="20"/>
            </svg>
            <span>Sora2带货</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'multi_shot_sora2' }]"
            @click="currentPage = 'multi_shot_sora2'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="8" height="14" rx="2" ry="2"/>
              <rect x="13" y="4" width="8" height="14" rx="2" ry="2"/>
              <polygon points="9 9 14 12 9 15 9 9"/>
              <line x1="8" y1="20" x2="16" y2="20"/>
            </svg>
            <span>Sora2多镜头</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'multi_shot_veo' }]"
            @click="currentPage = 'multi_shot_veo'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="8" height="14" rx="2" ry="2"/>
              <rect x="13" y="4" width="8" height="14" rx="2" ry="2"/>
              <polygon points="9 9 14 12 9 15 9 9"/>
              <line x1="8" y1="20" x2="16" y2="20"/>
            </svg>
            <span>VEO多镜头</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'sora2' }]"
            @click="currentPage = 'sora2'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="23 7 16 12 23 17 23 7"></polygon>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
            </svg>
            <span>Sora2视频</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'veo_product' }]"
            @click="currentPage = 'veo_product'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
            <span>VEO带货</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'veo' }]"
            @click="currentPage = 'veo'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="23 7 16 12 23 17 23 7"></polygon>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
            </svg>
            <span>VEO视频</span>
          </button>
          <button
            :class="['nav-item', { active: currentPage === 'veo_qihao' }]"
            @click="currentPage = 'veo_qihao'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
            <span>VEO起号</span>
          </button>
        </nav>

        <div class="sidebar-footer">
          <button
            v-if="isDevMode"
            :class="['nav-item', { active: currentPage === 'debug' }]"
            @click="currentPage = 'debug'"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/>
              <path d="M12 8v4M12 16h.01"/>
            </svg>
            <span>调试</span>
          </button>
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
        <!-- 香蕉生图 -->
        <NanoBanana
          v-show="currentPage === 'nanobanana'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
          @add-veo-task="handleAddVeoTask"
        />

        <!-- VEO视频 -->
        <GlinVeo
          ref="glinVeoRef"
          v-show="currentPage === 'veo'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- Sora2视频 -->
        <Sora2Generation
          v-show="currentPage === 'sora2'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- VEO带货 -->
        <VeoProduct
          v-show="currentPage === 'veo_product'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- VEO起号 -->
        <VeoQihao
          v-show="currentPage === 'veo_qihao'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- 视频带货 -->
        <VideoProduct
          v-show="currentPage === 'video_product'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <MultiShotVideoProduct
          v-show="currentPage === 'multi_shot_sora2'"
          page-title="Sora2多镜头"
          video-platform="sora2"
          settings-key-prefix="multi_shot_sora2"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <MultiShotVideoProduct
          v-show="currentPage === 'multi_shot_veo'"
          page-title="VEO多镜头"
          video-platform="veo3"
          settings-key-prefix="multi_shot_veo"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- Settings page -->
        <Settings
          v-show="currentPage === 'settings'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />

        <!-- Debug page (only in dev mode) -->
        <Debug
          v-if="isDevMode"
          v-show="currentPage === 'debug'"
          @toast="(msg, type) => toastRef?.show(msg, type)"
        />
      </main>
    </div>

    <Toast ref="toastRef" />
  </div>
</template>
