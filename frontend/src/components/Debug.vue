<script setup>
import { ref } from 'vue'

const emit = defineEmits(['toast'])

const activeTab = ref('veo')

// ==================== VEO 视频调试 ====================
const veo_prompt = ref('')
const veo_file_input = ref(null)
const veo_image_preview = ref('')
const veo_image_base64 = ref('')
const veo_image_mime = ref('')
const veo_loading = ref(false)
const veo_result = ref(null)
const veo_video_src = ref('')

const handleVeoImage = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { emit('toast', '请选择图片文件', 'error'); return }
  if (file.size > 10 * 1024 * 1024) { emit('toast', '图片不能超过 10MB', 'error'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    veo_image_preview.value = dataUrl
    veo_image_mime.value = file.type
    veo_image_base64.value = dataUrl.split(',')[1]
  }
  reader.readAsDataURL(file)
}

const removeVeoImage = () => {
  veo_image_preview.value = ''
  veo_image_base64.value = ''
  veo_image_mime.value = ''
  if (veo_file_input.value) veo_file_input.value.value = ''
}

const debugVeoCreate = async () => {
  if (!veo_prompt.value.trim()) { emit('toast', '请输入提示词', 'error'); return }
  veo_loading.value = true
  veo_result.value = null
  veo_video_src.value = ''
  try {
    let res
    if (veo_image_base64.value) {
      res = await window.pywebview.api.veo_image_to_video(
        veo_prompt.value, veo_image_base64.value, veo_image_mime.value
      )
    } else {
      res = await window.pywebview.api.veo_text_to_video(veo_prompt.value)
    }
    veo_result.value = res
    if (res.ok && res.video_url) {
      veo_video_src.value = res.video_url
      emit('toast', 'VEO 视频生成成功', 'success')
    } else {
      emit('toast', res.msg || '生成失败', 'error')
    }
  } catch (e) {
    veo_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { veo_loading.value = false }
}

// ==================== NanoBanana 生图调试 ====================
const nb_prompt = ref('')
const nb_loading = ref(false)
const nb_result = ref(null)
const nb_image_src = ref('')
const nb_ref_image = ref('')
const nb_ref_mime_type = ref('')
const nb_ref_preview = ref('')
const nb_file_input = ref(null)

const handleRefImageUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { emit('toast', '请选择图片文件', 'error'); return }
  if (file.size > 10 * 1024 * 1024) { emit('toast', '图片不能超过 10MB', 'error'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    nb_ref_preview.value = dataUrl
    nb_ref_mime_type.value = file.type
    nb_ref_image.value = dataUrl.split(',')[1]
    emit('toast', '参考图片已加载', 'success')
  }
  reader.readAsDataURL(file)
}

const removeRefImage = () => {
  nb_ref_image.value = ''
  nb_ref_mime_type.value = ''
  nb_ref_preview.value = ''
  if (nb_file_input.value) nb_file_input.value.value = ''
}

const debugNanoBanana = async () => {
  if (!nb_prompt.value.trim()) { emit('toast', '请输入提示词', 'error'); return }
  nb_loading.value = true
  nb_result.value = null
  nb_image_src.value = ''
  try {
    const res = await window.pywebview.api.debug_nanobanana(
      nb_prompt.value, nb_ref_image.value || '', nb_ref_mime_type.value || ''
    )
    nb_result.value = res
    if (res.ok && res.image_data && res.mime_type) {
      nb_image_src.value = `data:${res.mime_type};base64,${res.image_data}`
      emit('toast', '图片生成成功', 'success')
    } else {
      emit('toast', res.msg || '生图失败', 'error')
    }
  } catch (e) {
    nb_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { nb_loading.value = false }
}
</script>

<template>
  <div class="page">
    <!-- Tab 栏 -->
    <div class="tab-bar">
      <button
        :class="['tab-item', { active: activeTab === 'veo' }]"
        @click="activeTab = 'veo'"
      >
        VEO 视频
      </button>
      <button
        :class="['tab-item', { active: activeTab === 'nanobanana' }]"
        @click="activeTab = 'nanobanana'"
      >
        香蕉生图
      </button>
    </div>

    <!-- VEO 视频面板 -->
    <div v-if="activeTab === 'veo'" class="page-body">
      <div class="debug-grid">
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">VEO 视频生成</h3>
            <span class="card-subtitle">文生视频或上传图片为图生视频</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">提示词</span>
              <textarea v-model="veo_prompt" placeholder="请输入视频描述提示词" rows="4"></textarea>
            </label>
            <div class="field">
              <span class="field-label">图片（可选，上传后为图生视频）</span>
              <div v-if="!veo_image_preview" class="upload-area" @click="veo_file_input?.click()">
                <input ref="veo_file_input" type="file" accept="image/*" class="upload-input" @change="handleVeoImage" />
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span class="upload-text">点击选择图片</span>
                <span class="upload-hint">支持 JPG / PNG / WebP，最大 10MB</span>
              </div>
              <div v-else class="ref-image-preview">
                <img :src="veo_image_preview" alt="参考图片" />
                <button class="remove-btn" @click="removeVeoImage" title="移除图片">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <button class="primary-btn debug-btn" @click="debugVeoCreate" :disabled="veo_loading">
              {{ veo_loading ? '生成中...' : (veo_image_base64 ? '图生视频' : '文生视频') }}
            </button>
          </div>
          <div v-if="veo_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', veo_result.ok ? 'success' : 'error']">{{ veo_result.ok ? '成功' : '失败' }}</span>
            </div>
            <div v-if="veo_video_src" class="video-preview">
              <video :src="veo_video_src" controls preload="metadata" class="video-el"></video>
            </div>
            <pre v-if="!veo_result.ok" class="result-json">{{ JSON.stringify(veo_result, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- 香蕉生图面板 -->
    <div v-if="activeTab === 'nanobanana'" class="page-body">
      <div class="debug-grid">
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">香蕉生图</h3>
            <span class="card-subtitle">支持文生图和图生图</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">提示词</span>
              <textarea v-model="nb_prompt" placeholder="请输入图片描述提示词" rows="4"></textarea>
            </label>
            <div class="field">
              <span class="field-label">参考图片（可选，上传后为图生图模式）</span>
              <div v-if="!nb_ref_preview" class="upload-area" @click="nb_file_input?.click()">
                <input ref="nb_file_input" type="file" accept="image/*" class="upload-input" @change="handleRefImageUpload" />
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span class="upload-text">点击上传图片</span>
                <span class="upload-hint">支持 JPG / PNG / WebP，最大 10MB</span>
              </div>
              <div v-else class="ref-image-preview">
                <img :src="nb_ref_preview" alt="参考图片" />
                <button class="remove-btn" @click="removeRefImage" title="移除图片">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <button class="primary-btn debug-btn" @click="debugNanoBanana" :disabled="nb_loading">
              {{ nb_loading ? '生成中...' : (nb_ref_image ? '图生图' : '文生图') }}
            </button>
          </div>
          <div v-if="nb_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', nb_result.ok ? 'success' : 'error']">{{ nb_result.ok ? '成功' : '失败' }}</span>
            </div>
            <div v-if="nb_image_src" class="image-preview">
              <img :src="nb_image_src" alt="生成的图片" />
            </div>
            <div v-if="nb_result.text_content" class="result-text">
              <span class="field-label">模型回复</span>
              <p>{{ nb_result.text_content }}</p>
            </div>
            <pre v-if="!nb_result.ok" class="result-json">{{ JSON.stringify(nb_result, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { position: relative; min-height: 100%; display: flex; flex-direction: column; }
.tab-bar { display: flex; gap: 0; padding: 0 32px; border-bottom: 1px solid var(--border); background: var(--bg-surface); flex-shrink: 0; }
.tab-item { position: relative; padding: 16px 24px; border: none; background: transparent; color: var(--text-muted); font-size: 14px; font-weight: 500; cursor: pointer; transition: color 0.2s ease; }
.tab-item:hover { color: var(--text-primary); }
.tab-item.active { color: var(--accent); }
.tab-item.active::after { content: ''; position: absolute; bottom: 0; left: 16px; right: 16px; height: 2px; background: linear-gradient(90deg, var(--accent-light), var(--accent)); border-radius: 2px 2px 0 0; }
.page-body { flex: 1; padding: 24px 32px; }
.debug-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 20px; }
.debug-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-card); }
.card-header { padding: 16px 20px; border-bottom: 1px solid var(--border-light); }
.card-title { margin: 0; font-size: 15px; font-weight: 600; color: var(--text-primary); }
.card-body { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 8px; }
.field-label { font-size: 13px; color: var(--text-tertiary); }
textarea { width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--border-strong); background: var(--bg-surface); color: var(--text-primary); font-size: 14px; font-family: inherit; outline: none; resize: vertical; transition: border-color 0.2s ease, box-shadow 0.2s ease; }
textarea::placeholder { color: var(--text-placeholder); }
textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-focus); }
.debug-btn { width: auto; align-self: flex-start; padding: 10px 24px; font-size: 13px; }
.debug-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; box-shadow: none !important; }
.video-preview { margin-top: 12px; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); background: var(--bg-surface); }
.video-preview .video-el { display: block; max-width: 100%; max-height: 400px; width: auto; }
.card-result { border-top: 1px solid var(--border-light); padding: 16px 20px; }
.result-header { margin-bottom: 12px; }
.result-badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }
.result-badge.success { background: var(--success-bg); color: var(--success); }
.result-badge.error { background: var(--error-bg); color: var(--error); }
.result-json { margin: 0; padding: 14px; border-radius: 10px; background: var(--bg-surface); border: 1px solid var(--border-light); font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; font-size: 12px; color: var(--text-secondary); line-height: 1.6; overflow-x: auto; white-space: pre-wrap; word-break: break-all; user-select: text; -webkit-user-select: text; cursor: text; }
.image-preview { margin: 12px 0; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); background: var(--bg-surface); }
.image-preview img { display: block; max-width: 100%; max-height: 480px; margin: 0 auto; object-fit: contain; }
.result-text { margin-top: 12px; }
.result-text p { margin: 6px 0 0; padding: 12px 14px; border-radius: 10px; background: var(--bg-surface); font-size: 14px; color: var(--text-strong); line-height: 1.6; }
.card-subtitle { display: block; margin-top: 4px; font-size: 12px; color: var(--text-dim); font-weight: 400; }
.upload-area { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 28px 20px; border-radius: 12px; border: 2px dashed var(--border-strong); background: var(--bg-surface); cursor: pointer; transition: border-color 0.2s ease, background 0.2s ease; }
.upload-area:hover { border-color: var(--accent-border); background: var(--accent-bg-subtle); }
.upload-input { display: none; }
.upload-icon { width: 32px; height: 32px; color: var(--text-hint); }
.upload-text { font-size: 14px; color: var(--text-tertiary); }
.upload-hint { font-size: 12px; color: var(--text-placeholder); }
.ref-image-preview { position: relative; display: inline-block; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-medium); background: var(--bg-surface); }
.ref-image-preview img { display: block; max-width: 100%; max-height: 200px; object-fit: contain; }
.remove-btn { position: absolute; top: 8px; right: 8px; width: 28px; height: 28px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 8px; border: none; background: rgba(0,0,0,0.6); color: rgba(255,255,255,0.9); cursor: pointer; transition: background 0.2s ease; }
.remove-btn:hover { background: rgba(255,69,58,0.8); }
.remove-btn svg { width: 14px; height: 14px; }
</style>
