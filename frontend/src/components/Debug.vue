<script setup>
import { ref } from 'vue'

const emit = defineEmits(['toast'])

// 当前 Tab
const activeTab = ref('official_sora2')

// ==================== Official Sora2 调试 ====================
const gf_prompt = ref('')
const gf_file_input = ref(null)
const gf_image_preview = ref('')
const gf_image_base64 = ref('')
const gf_image_mime = ref('')
const gf_loading = ref(false)
const gf_result = ref(null)

const handleGfImage = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { emit('toast', '请选择图片文件', 'error'); return }
  if (file.size > 10 * 1024 * 1024) { emit('toast', '图片不能超过 10MB', 'error'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    gf_image_preview.value = dataUrl
    gf_image_mime.value = file.type
    gf_image_base64.value = dataUrl.split(',')[1]
  }
  reader.readAsDataURL(file)
}

const removeGfImage = () => {
  gf_image_preview.value = ''
  gf_image_base64.value = ''
  gf_image_mime.value = ''
  if (gf_file_input.value) gf_file_input.value.value = ''
}

const debugGfSora2Create = async () => {
  if (!gf_prompt.value.trim()) { emit('toast', '请输入提示词', 'error'); return }
  gf_loading.value = true
  gf_result.value = null
  try {
    const res = await window.pywebview.api.debug_guanfang_sora2_create(
      gf_prompt.value, gf_image_base64.value || '', gf_image_mime.value || ''
    )
    gf_result.value = res
    if (res.ok) emit('toast', '官方任务已提交', 'success')
    else emit('toast', res.msg || '创建失败', 'error')
  } catch (e) {
    gf_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { gf_loading.value = false }
}

const gf_task_id = ref('')
const gf_query_loading = ref(false)
const gf_query_result = ref(null)

const debugGfSora2Query = async () => {
  if (!gf_task_id.value.trim()) { emit('toast', '请输入任务ID', 'error'); return }
  gf_query_loading.value = true
  gf_query_result.value = null
  try {
    const res = await window.pywebview.api.debug_guanfang_sora2_query(gf_task_id.value)
    gf_query_result.value = res
    if (res.ok) emit('toast', '查询成功', 'success')
    else emit('toast', res.msg || '查询失败', 'error')
  } catch (e) {
    gf_query_result.value = { ok: false, msg: String(e) }
    emit('toast', '查询异常', 'error')
  } finally { gf_query_loading.value = false }
}

const gf_content_loading = ref(false)
const gf_content_result = ref(null)
const gf_video_src = ref('')

const debugGfSora2Content = async () => {
  if (!gf_task_id.value.trim()) { emit('toast', '请输入任务ID', 'error'); return }
  gf_content_loading.value = true
  gf_content_result.value = null
  gf_video_src.value = ''
  try {
    const res = await window.pywebview.api.debug_guanfang_sora2_content(gf_task_id.value)
    gf_content_result.value = res
    if (res.ok && res.data && res.content_type) {
      gf_video_src.value = `data:${res.content_type};base64,${res.data}`
      emit('toast', '视频加载成功', 'success')
    } else {
      emit('toast', res.msg || '查看视频失败', 'error')
    }
  } catch (e) {
    gf_content_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { gf_content_loading.value = false }
}

// ==================== YW Sora2 调试 ====================
const yw_sora2_prompt = ref('')
const yw_sora2_file_input = ref(null)
const yw_sora2_image_preview = ref('')
const yw_sora2_image_base64 = ref('')
const yw_sora2_image_mime = ref('')
const yw_sora2_loading = ref(false)
const yw_sora2_result = ref(null)

const handleYwSora2Image = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { emit('toast', '请选择图片文件', 'error'); return }
  if (file.size > 10 * 1024 * 1024) { emit('toast', '图片不能超过 10MB', 'error'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    yw_sora2_image_preview.value = dataUrl
    yw_sora2_image_mime.value = file.type
    yw_sora2_image_base64.value = dataUrl.split(',')[1]
  }
  reader.readAsDataURL(file)
}

const removeYwSora2Image = () => {
  yw_sora2_image_preview.value = ''
  yw_sora2_image_base64.value = ''
  yw_sora2_image_mime.value = ''
  if (yw_sora2_file_input.value) yw_sora2_file_input.value.value = ''
}

const debugYwSora2Create = async () => {
  if (!yw_sora2_prompt.value.trim()) { emit('toast', '请输入提示词', 'error'); return }
  yw_sora2_loading.value = true
  yw_sora2_result.value = null
  try {
    const res = await window.pywebview.api.debug_yunwu_sora2_create(
      yw_sora2_prompt.value, yw_sora2_image_base64.value || '', yw_sora2_image_mime.value || ''
    )
    yw_sora2_result.value = res
    if (res.ok) emit('toast', '任务创建成功', 'success')
    else emit('toast', res.msg || '创建失败', 'error')
  } catch (e) {
    yw_sora2_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { yw_sora2_loading.value = false }
}

const yw_sora2_task_id = ref('')
const yw_sora2_query_loading = ref(false)
const yw_sora2_query_result = ref(null)

const debugYwSora2Query = async () => {
  if (!yw_sora2_task_id.value.trim()) { emit('toast', '请输入任务ID', 'error'); return }
  yw_sora2_query_loading.value = true
  yw_sora2_query_result.value = null
  try {
    const res = await window.pywebview.api.debug_yunwu_sora2_query(yw_sora2_task_id.value)
    yw_sora2_query_result.value = res
    if (res.ok) emit('toast', '查询成功', 'success')
    else emit('toast', res.msg || '查询失败', 'error')
  } catch (e) {
    yw_sora2_query_result.value = { ok: false, msg: String(e) }
    emit('toast', '查询异常', 'error')
  } finally { yw_sora2_query_loading.value = false }
}

// ==================== DYY Sora2 调试 ====================
const dy_prompt = ref('')
const dy_file_input = ref(null)
const dy_image_preview = ref('')
const dy_image_base64 = ref('')
const dy_image_mime = ref('')
const dy_loading = ref(false)
const dy_result = ref(null)

const handleDyImage = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { emit('toast', '请选择图片文件', 'error'); return }
  if (file.size > 10 * 1024 * 1024) { emit('toast', '图片不能超过 10MB', 'error'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    dy_image_preview.value = dataUrl
    dy_image_mime.value = file.type
    dy_image_base64.value = dataUrl.split(',')[1]
  }
  reader.readAsDataURL(file)
}

const removeDyImage = () => {
  dy_image_preview.value = ''
  dy_image_base64.value = ''
  dy_image_mime.value = ''
  if (dy_file_input.value) dy_file_input.value.value = ''
}

const debugDySora2Create = async () => {
  if (!dy_prompt.value.trim()) { emit('toast', '请输入提示词', 'error'); return }
  dy_loading.value = true
  dy_result.value = null
  try {
    const res = await window.pywebview.api.debug_dayangyu_sora2_create(
      dy_prompt.value, dy_image_base64.value || '', dy_image_mime.value || ''
    )
    dy_result.value = res
    if (res.ok) emit('toast', 'DYY 任务已提交', 'success')
    else emit('toast', res.msg || '创建失败', 'error')
  } catch (e) {
    dy_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { dy_loading.value = false }
}

const dy_task_id = ref('')
const dy_query_loading = ref(false)
const dy_query_result = ref(null)

const debugDySora2Query = async () => {
  if (!dy_task_id.value.trim()) { emit('toast', '请输入任务ID', 'error'); return }
  dy_query_loading.value = true
  dy_query_result.value = null
  try {
    const res = await window.pywebview.api.debug_dayangyu_sora2_query(dy_task_id.value)
    dy_query_result.value = res
    if (res.ok) emit('toast', '查询成功', 'success')
    else emit('toast', res.msg || '查询失败', 'error')
  } catch (e) {
    dy_query_result.value = { ok: false, msg: String(e) }
    emit('toast', '查询异常', 'error')
  } finally { dy_query_loading.value = false }
}

const dy_content_loading = ref(false)
const dy_content_result = ref(null)
const dy_video_src = ref('')

const debugDySora2Content = async () => {
  if (!dy_task_id.value.trim()) { emit('toast', '请输入任务ID', 'error'); return }
  dy_content_loading.value = true
  dy_content_result.value = null
  dy_video_src.value = ''
  try {
    const res = await window.pywebview.api.debug_dayangyu_sora2_content(dy_task_id.value)
    dy_content_result.value = res
    if (res.ok && res.data && res.content_type) {
      dy_video_src.value = `data:${res.content_type};base64,${res.data}`
      emit('toast', '视频加载成功', 'success')
    } else {
      emit('toast', res.msg || '查看视频失败', 'error')
    }
  } catch (e) {
    dy_content_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { dy_content_loading.value = false }
}

// ==================== XBS Sora2 调试 ====================
const xbs_prompt = ref('')
const xbs_file_input = ref(null)
const xbs_image_preview = ref('')
const xbs_image_base64 = ref('')
const xbs_image_mime = ref('')
const xbs_loading = ref(false)
const xbs_result = ref(null)

const handleXbsImage = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { emit('toast', '请选择图片文件', 'error'); return }
  if (file.size > 10 * 1024 * 1024) { emit('toast', '图片不能超过 10MB', 'error'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    xbs_image_preview.value = dataUrl
    xbs_image_mime.value = file.type
    xbs_image_base64.value = dataUrl.split(',')[1]
  }
  reader.readAsDataURL(file)
}

const removeXbsImage = () => {
  xbs_image_preview.value = ''
  xbs_image_base64.value = ''
  xbs_image_mime.value = ''
  if (xbs_file_input.value) xbs_file_input.value.value = ''
}

const debugXbsSora2Create = async () => {
  if (!xbs_prompt.value.trim()) { emit('toast', '请输入提示词', 'error'); return }
  xbs_loading.value = true
  xbs_result.value = null
  try {
    const res = await window.pywebview.api.debug_xiaobanshou_sora2_create(
      xbs_prompt.value, xbs_image_base64.value || '', xbs_image_mime.value || ''
    )
    xbs_result.value = res
    if (res.ok) emit('toast', 'XBS 任务已提交', 'success')
    else emit('toast', res.msg || '创建失败', 'error')
  } catch (e) {
    xbs_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { xbs_loading.value = false }
}

const xbs_task_id = ref('')
const xbs_query_loading = ref(false)
const xbs_query_result = ref(null)

const debugXbsSora2Query = async () => {
  if (!xbs_task_id.value.trim()) { emit('toast', '请输入任务ID', 'error'); return }
  xbs_query_loading.value = true
  xbs_query_result.value = null
  try {
    const res = await window.pywebview.api.debug_xiaobanshou_sora2_query(xbs_task_id.value)
    xbs_query_result.value = res
    if (res.ok) emit('toast', '查询成功', 'success')
    else emit('toast', res.msg || '查询失败', 'error')
  } catch (e) {
    xbs_query_result.value = { ok: false, msg: String(e) }
    emit('toast', '查询异常', 'error')
  } finally { xbs_query_loading.value = false }
}

// ==================== BDW Sora2 调试 ====================
const bdw_prompt = ref('')
const bdw_file_input = ref(null)
const bdw_image_preview = ref('')
const bdw_image_base64 = ref('')
const bdw_image_mime = ref('')
const bdw_loading = ref(false)
const bdw_result = ref(null)

const handleBdwImage = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { emit('toast', '请选择图片文件', 'error'); return }
  if (file.size > 10 * 1024 * 1024) { emit('toast', '图片不能超过 10MB', 'error'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    bdw_image_preview.value = dataUrl
    bdw_image_mime.value = file.type
    bdw_image_base64.value = dataUrl.split(',')[1]
  }
  reader.readAsDataURL(file)
}

const removeBdwImage = () => {
  bdw_image_preview.value = ''
  bdw_image_base64.value = ''
  bdw_image_mime.value = ''
  if (bdw_file_input.value) bdw_file_input.value.value = ''
}

const debugBdwSora2Create = async () => {
  if (!bdw_prompt.value.trim()) { emit('toast', '请输入提示词', 'error'); return }
  bdw_loading.value = true
  bdw_result.value = null
  try {
    const res = await window.pywebview.api.debug_bandianwa_sora2_create(
      bdw_prompt.value, bdw_image_base64.value || '', bdw_image_mime.value || ''
    )
    bdw_result.value = res
    if (res.ok) emit('toast', 'BDW 任务已提交', 'success')
    else emit('toast', res.msg || '创建失败', 'error')
  } catch (e) {
    bdw_result.value = { ok: false, msg: String(e) }
    emit('toast', '请求异常', 'error')
  } finally { bdw_loading.value = false }
}

const bdw_task_id = ref('')
const bdw_query_loading = ref(false)
const bdw_query_result = ref(null)

const debugBdwSora2Query = async () => {
  if (!bdw_task_id.value.trim()) { emit('toast', '请输入任务ID', 'error'); return }
  bdw_query_loading.value = true
  bdw_query_result.value = null
  try {
    const res = await window.pywebview.api.debug_bandianwa_sora2_query(bdw_task_id.value)
    bdw_query_result.value = res
    if (res.ok) emit('toast', '查询成功', 'success')
    else emit('toast', res.msg || '查询失败', 'error')
  } catch (e) {
    bdw_query_result.value = { ok: false, msg: String(e) }
    emit('toast', '查询异常', 'error')
  } finally { bdw_query_loading.value = false }
}

// ==================== NanoBanana 调试 ====================
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
      emit('toast', res.msg || 'NanoBanana 调试失败', 'error')
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
        :class="['tab-item', { active: activeTab === 'official_sora2' }]"
        @click="activeTab = 'official_sora2'"
      >
        Official Sora2 调试
      </button>
      <button
        :class="['tab-item', { active: activeTab === 'yunwu_sora2' }]"
        @click="activeTab = 'yunwu_sora2'"
      >
        YW Sora2 调试
      </button>
      <button
        :class="['tab-item', { active: activeTab === 'dayangyu_sora2' }]"
        @click="activeTab = 'dayangyu_sora2'"
      >
        DYY Sora2 调试
      </button>
      <button
        :class="['tab-item', { active: activeTab === 'xiaobanshou_sora2' }]"
        @click="activeTab = 'xiaobanshou_sora2'"
      >
        XBS Sora2 调试
      </button>
      <button
        :class="['tab-item', { active: activeTab === 'bandianwa_sora2' }]"
        @click="activeTab = 'bandianwa_sora2'"
      >
        BDW Sora2 调试
      </button>
      <button
        :class="['tab-item', { active: activeTab === 'nanobanana' }]"
        @click="activeTab = 'nanobanana'"
      >
        NanoBanana 调试
      </button>
    </div>

    <!-- Official Sora2 调试面板 -->
    <div v-if="activeTab === 'official_sora2'" class="page-body">
      <div class="debug-grid">
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">创建 Official Sora2 任务</h3>
            <span class="card-subtitle">文生视频或上传图片为图生视频，模型在设置中配置</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">提示词 (prompt)</span>
              <textarea v-model="gf_prompt" placeholder="请输入视频描述提示词" rows="4"></textarea>
            </label>
            <div class="field">
              <span class="field-label">图片（可选，上传后为图生视频）</span>
              <div v-if="!gf_image_preview" class="upload-area" @click="gf_file_input?.click()">
                <input ref="gf_file_input" type="file" accept="image/*" class="upload-input" @change="handleGfImage" />
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span class="upload-text">点击选择图片</span>
                <span class="upload-hint">支持 JPG / PNG / WebP，最大 10MB</span>
              </div>
              <div v-else class="ref-image-preview">
                <img :src="gf_image_preview" alt="参考图片" />
                <button class="remove-btn" @click="removeGfImage" title="移除图片">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <button class="primary-btn debug-btn" @click="debugGfSora2Create" :disabled="gf_loading">
              {{ gf_loading ? '请求中...' : (gf_image_base64 ? '图生视频' : '文生视频') }}
            </button>
          </div>
          <div v-if="gf_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', gf_result.ok ? 'success' : 'error']">{{ gf_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(gf_result, null, 2) }}</pre>
          </div>
        </div>
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">查询 Official Sora2 任务</h3>
            <span class="card-subtitle">建议优先用查询结果中的 video_url 拉取；查看视频内容接口较慢，可备用</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">任务 ID</span>
              <input v-model="gf_task_id" type="text" placeholder="请输入任务ID" />
            </label>
            <div class="button-row">
              <button class="primary-btn debug-btn" @click="debugGfSora2Query" :disabled="gf_query_loading">
                {{ gf_query_loading ? '查询中...' : '查询状态' }}
              </button>
              <button class="primary-btn debug-btn" @click="debugGfSora2Content" :disabled="gf_content_loading">
                {{ gf_content_loading ? '加载中...' : '查看视频内容' }}
              </button>
            </div>
          </div>
          <div v-if="gf_query_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', gf_query_result.ok ? 'success' : 'error']">{{ gf_query_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(gf_query_result, null, 2) }}</pre>
          </div>
          <div v-if="gf_content_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', gf_content_result.ok ? 'success' : 'error']">{{ gf_content_result.ok ? '视频内容' : '失败' }}</span>
            </div>
            <div v-if="gf_video_src" class="video-preview">
              <video :src="gf_video_src" controls preload="metadata" class="video-el"></video>
            </div>
            <pre v-else class="result-json">{{ JSON.stringify(gf_content_result, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- YW Sora2 调试面板 -->
    <div v-if="activeTab === 'yunwu_sora2'" class="page-body">
      <div class="debug-grid">
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">创建 YW Sora2 任务</h3>
            <span class="card-subtitle">选择图片后自动上传图床并创建图生视频任务</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">提示词 (prompt)</span>
              <textarea v-model="yw_sora2_prompt" placeholder="请输入视频描述提示词" rows="4"></textarea>
            </label>
            <div class="field">
              <span class="field-label">图片（可选，选择后为图生视频模式，内部自动上传图床）</span>
              <div v-if="!yw_sora2_image_preview" class="upload-area" @click="yw_sora2_file_input?.click()">
                <input ref="yw_sora2_file_input" type="file" accept="image/*" class="upload-input" @change="handleYwSora2Image" />
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span class="upload-text">点击选择图片</span>
                <span class="upload-hint">支持 JPG / PNG / WebP，最大 10MB</span>
              </div>
              <div v-else class="ref-image-preview">
                <img :src="yw_sora2_image_preview" alt="参考图片" />
                <button class="remove-btn" @click="removeYwSora2Image" title="移除图片">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <button class="primary-btn debug-btn" @click="debugYwSora2Create" :disabled="yw_sora2_loading">
              {{ yw_sora2_loading ? '处理中...' : (yw_sora2_image_base64 ? '图生视频' : '文生视频') }}
            </button>
          </div>
          <div v-if="yw_sora2_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', yw_sora2_result.ok ? 'success' : 'error']">{{ yw_sora2_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(yw_sora2_result, null, 2) }}</pre>
          </div>
        </div>
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">查询 YW Sora2 任务</h3>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">任务 ID</span>
              <input v-model="yw_sora2_task_id" type="text" placeholder="请输入任务ID" />
            </label>
            <button class="primary-btn debug-btn" @click="debugYwSora2Query" :disabled="yw_sora2_query_loading">
              {{ yw_sora2_query_loading ? '查询中...' : '查询状态' }}
            </button>
          </div>
          <div v-if="yw_sora2_query_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', yw_sora2_query_result.ok ? 'success' : 'error']">{{ yw_sora2_query_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(yw_sora2_query_result, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- DYY Sora2 调试面板 -->
    <div v-if="activeTab === 'dayangyu_sora2'" class="page-body">
      <div class="debug-grid">
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">创建 DYY Sora2 任务</h3>
            <span class="card-subtitle">文生视频或上传图片为图生视频，模型在设置中配置</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">提示词 (prompt)</span>
              <textarea v-model="dy_prompt" placeholder="请输入视频描述提示词" rows="4"></textarea>
            </label>
            <div class="field">
              <span class="field-label">图片（可选，上传后为图生视频）</span>
              <div v-if="!dy_image_preview" class="upload-area" @click="dy_file_input?.click()">
                <input ref="dy_file_input" type="file" accept="image/*" class="upload-input" @change="handleDyImage" />
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span class="upload-text">点击选择图片</span>
                <span class="upload-hint">支持 JPG / PNG / WebP，最大 10MB</span>
              </div>
              <div v-else class="ref-image-preview">
                <img :src="dy_image_preview" alt="参考图片" />
                <button class="remove-btn" @click="removeDyImage" title="移除图片">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <button class="primary-btn debug-btn" @click="debugDySora2Create" :disabled="dy_loading">
              {{ dy_loading ? '请求中...' : (dy_image_base64 ? '图生视频' : '文生视频') }}
            </button>
          </div>
          <div v-if="dy_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', dy_result.ok ? 'success' : 'error']">{{ dy_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(dy_result, null, 2) }}</pre>
          </div>
        </div>
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">查询 DYY Sora2 任务</h3>
            <span class="card-subtitle">建议优先用查询结果中的 video_url 拉取；查看视频内容接口较慢，可备用</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">任务 ID</span>
              <input v-model="dy_task_id" type="text" placeholder="请输入任务ID" />
            </label>
            <div class="button-row">
              <button class="primary-btn debug-btn" @click="debugDySora2Query" :disabled="dy_query_loading">
                {{ dy_query_loading ? '查询中...' : '查询状态' }}
              </button>
              <button class="primary-btn debug-btn" @click="debugDySora2Content" :disabled="dy_content_loading">
                {{ dy_content_loading ? '加载中...' : '查看视频内容' }}
              </button>
            </div>
          </div>
          <div v-if="dy_query_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', dy_query_result.ok ? 'success' : 'error']">{{ dy_query_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(dy_query_result, null, 2) }}</pre>
          </div>
          <div v-if="dy_content_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', dy_content_result.ok ? 'success' : 'error']">{{ dy_content_result.ok ? '视频内容' : '失败' }}</span>
            </div>
            <div v-if="dy_video_src" class="video-preview">
              <video :src="dy_video_src" controls preload="metadata" class="video-el"></video>
            </div>
            <pre v-else class="result-json">{{ JSON.stringify(dy_content_result, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- XBS Sora2 调试面板 -->
    <div v-if="activeTab === 'xiaobanshou_sora2'" class="page-body">
      <div class="debug-grid">
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">创建 XBS Sora2 任务</h3>
            <span class="card-subtitle">文生视频或上传图片为图生视频，模型在设置中配置</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">提示词 (prompt)</span>
              <textarea v-model="xbs_prompt" placeholder="请输入视频描述提示词，支持 @角色username" rows="4"></textarea>
            </label>
            <div class="field">
              <span class="field-label">图片（可选，上传后为图生视频）</span>
              <div v-if="!xbs_image_preview" class="upload-area" @click="xbs_file_input?.click()">
                <input ref="xbs_file_input" type="file" accept="image/*" class="upload-input" @change="handleXbsImage" />
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span class="upload-text">点击选择图片</span>
                <span class="upload-hint">支持 JPG / PNG / WebP，最大 10MB</span>
              </div>
              <div v-else class="ref-image-preview">
                <img :src="xbs_image_preview" alt="参考图片" />
                <button class="remove-btn" @click="removeXbsImage" title="移除图片">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <button class="primary-btn debug-btn" @click="debugXbsSora2Create" :disabled="xbs_loading">
              {{ xbs_loading ? '请求中...' : (xbs_image_base64 ? '图生视频' : '文生视频') }}
            </button>
          </div>
          <div v-if="xbs_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', xbs_result.ok ? 'success' : 'error']">{{ xbs_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(xbs_result, null, 2) }}</pre>
          </div>
        </div>
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">查询 XBS Sora2 任务</h3>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">任务 ID</span>
              <input v-model="xbs_task_id" type="text" placeholder="请输入任务ID" />
            </label>
            <button class="primary-btn debug-btn" @click="debugXbsSora2Query" :disabled="xbs_query_loading">
              {{ xbs_query_loading ? '查询中...' : '查询状态' }}
            </button>
          </div>
          <div v-if="xbs_query_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', xbs_query_result.ok ? 'success' : 'error']">{{ xbs_query_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(xbs_query_result, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- BDW Sora2 调试面板 -->
    <div v-if="activeTab === 'bandianwa_sora2'" class="page-body">
      <div class="debug-grid">
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">创建 BDW Sora2 任务</h3>
            <span class="card-subtitle">文生视频或上传图片为图生视频，模型在设置中配置</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">提示词 (prompt)</span>
              <textarea v-model="bdw_prompt" placeholder="请输入视频描述提示词" rows="4"></textarea>
            </label>
            <div class="field">
              <span class="field-label">图片（可选，上传后为图生视频）</span>
              <div v-if="!bdw_image_preview" class="upload-area" @click="bdw_file_input?.click()">
                <input ref="bdw_file_input" type="file" accept="image/*" class="upload-input" @change="handleBdwImage" />
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span class="upload-text">点击选择图片</span>
                <span class="upload-hint">支持 JPG / PNG / WebP，最大 10MB</span>
              </div>
              <div v-else class="ref-image-preview">
                <img :src="bdw_image_preview" alt="参考图片" />
                <button class="remove-btn" @click="removeBdwImage" title="移除图片">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <button class="primary-btn debug-btn" @click="debugBdwSora2Create" :disabled="bdw_loading">
              {{ bdw_loading ? '请求中...' : (bdw_image_base64 ? '图生视频' : '文生视频') }}
            </button>
          </div>
          <div v-if="bdw_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', bdw_result.ok ? 'success' : 'error']">{{ bdw_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(bdw_result, null, 2) }}</pre>
          </div>
        </div>
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">查询 BDW Sora2 任务</h3>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">任务 ID</span>
              <input v-model="bdw_task_id" type="text" placeholder="请输入任务ID" />
            </label>
            <button class="primary-btn debug-btn" @click="debugBdwSora2Query" :disabled="bdw_query_loading">
              {{ bdw_query_loading ? '查询中...' : '查询状态' }}
            </button>
          </div>
          <div v-if="bdw_query_result" class="card-result">
            <div class="result-header">
              <span :class="['result-badge', bdw_query_result.ok ? 'success' : 'error']">{{ bdw_query_result.ok ? '成功' : '失败' }}</span>
            </div>
            <pre class="result-json">{{ JSON.stringify(bdw_query_result, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- NanoBanana 调试面板 -->
    <div v-if="activeTab === 'nanobanana'" class="page-body">
      <div class="debug-grid">
        <div class="debug-card">
          <div class="card-header">
            <h3 class="card-title">NanoBanana 图片生成</h3>
            <span class="card-subtitle">支持文生图和图生图</span>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">提示词 (prompt)</span>
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
            <div v-if="!nb_result.ok" class="result-error">
              <pre class="result-json">{{ JSON.stringify(nb_result, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { position: relative; min-height: 100%; display: flex; flex-direction: column; }
.tab-bar { display: flex; gap: 0; padding: 0 32px; border-bottom: 1px solid rgba(255,255,255,0.06); background: rgba(12,15,22,0.5); flex-shrink: 0; }
.tab-item { position: relative; padding: 16px 24px; border: none; background: transparent; color: rgba(230,233,242,0.5); font-size: 14px; font-weight: 500; cursor: pointer; transition: color 0.2s ease; }
.tab-item:hover { color: rgba(230,233,242,0.8); }
.tab-item.active { color: #8ba3ff; }
.tab-item.active::after { content: ''; position: absolute; bottom: 0; left: 16px; right: 16px; height: 2px; background: linear-gradient(90deg,#5b7cff,#7f5bff); border-radius: 2px 2px 0 0; }
.page-body { flex: 1; padding: 24px 32px; }
.debug-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 20px; }
.debug-card { background: rgba(16,20,28,0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; overflow: hidden; }
.card-header { padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.card-title { margin: 0; font-size: 15px; font-weight: 600; color: #e6e9f2; }
.card-body { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 8px; }
.field-label { font-size: 13px; color: rgba(230,233,242,0.6); }
textarea { width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); background: rgba(8,11,18,0.8); color: #f5f7ff; font-size: 14px; font-family: inherit; outline: none; resize: vertical; transition: border-color 0.2s ease, box-shadow 0.2s ease; }
textarea::placeholder { color: rgba(230,233,242,0.4); }
textarea:focus { border-color: rgba(91,124,255,0.6); box-shadow: 0 0 0 3px rgba(91,124,255,0.15); }
.debug-btn { width: auto; align-self: flex-start; padding: 10px 24px; font-size: 13px; }
.debug-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; box-shadow: none !important; }
.button-row { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.video-preview { margin-top: 12px; border-radius: 10px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); background: rgba(8,11,18,0.6); }
.video-preview .video-el { display: block; max-width: 100%; max-height: 360px; width: auto; }
.card-result { border-top: 1px solid rgba(255,255,255,0.06); padding: 16px 20px; }
.result-header { margin-bottom: 12px; }
.result-badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }
.result-badge.success { background: rgba(52,199,89,0.15); color: #34c759; }
.result-badge.error { background: rgba(255,69,58,0.15); color: #ff453a; }
.result-json { margin: 0; padding: 14px; border-radius: 10px; background: rgba(8,11,18,0.8); border: 1px solid rgba(255,255,255,0.04); font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; font-size: 12px; color: rgba(230,233,242,0.75); line-height: 1.6; overflow-x: auto; white-space: pre-wrap; word-break: break-all; user-select: text; -webkit-user-select: text; cursor: text; }
.image-preview { margin: 12px 0; border-radius: 10px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); background: rgba(8,11,18,0.6); }
.image-preview img { display: block; max-width: 100%; max-height: 480px; margin: 0 auto; object-fit: contain; }
.result-text { margin-top: 12px; }
.result-text p { margin: 6px 0 0; padding: 12px 14px; border-radius: 10px; background: rgba(8,11,18,0.6); font-size: 14px; color: rgba(230,233,242,0.85); line-height: 1.6; }
.result-error { margin-top: 12px; }
.card-subtitle { display: block; margin-top: 4px; font-size: 12px; color: rgba(230,233,242,0.4); font-weight: 400; }
.upload-area { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 28px 20px; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.1); background: rgba(8,11,18,0.5); cursor: pointer; transition: border-color 0.2s ease, background 0.2s ease; }
.upload-area:hover { border-color: rgba(91,124,255,0.4); background: rgba(91,124,255,0.05); }
.upload-input { display: none; }
.upload-icon { width: 32px; height: 32px; color: rgba(230,233,242,0.3); }
.upload-text { font-size: 14px; color: rgba(230,233,242,0.6); }
.upload-hint { font-size: 12px; color: rgba(230,233,242,0.3); }
.ref-image-preview { position: relative; display: inline-block; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); background: rgba(8,11,18,0.6); }
.ref-image-preview img { display: block; max-width: 100%; max-height: 200px; object-fit: contain; }
.remove-btn { position: absolute; top: 8px; right: 8px; width: 28px; height: 28px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 8px; border: none; background: rgba(0,0,0,0.7); color: rgba(255,255,255,0.8); cursor: pointer; transition: background 0.2s ease; }
.remove-btn:hover { background: rgba(255,69,58,0.8); }
.remove-btn svg { width: 14px; height: 14px; }
</style>
