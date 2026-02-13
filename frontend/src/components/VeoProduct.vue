<script setup>
import { ref, reactive, computed } from 'vue'

const emit = defineEmits(['toast'])

// ==================== 任务列表（内存中，不持久化） ====================
const taskList = ref([])
let taskIdCounter = 0

// ==================== 添加/编辑图片 弹窗 ====================
const showDialog = ref(false)
const dialogMode = ref('add') // 'add' | 'edit'
const editingTaskId = ref(null)

const dialogImagePreview = ref('')
const dialogImageBase64 = ref('')
const dialogImageMime = ref('')
const dialogImagePrompt = ref('')
const dialogImageRatio = ref('9:16')
const dialogImageQuality = ref('1K')
const dialogIsDragging = ref(false)
const dialogFileInput = ref(null)

const openAddDialog = () => {
  dialogMode.value = 'add'
  editingTaskId.value = null
  dialogImagePreview.value = ''
  dialogImageBase64.value = ''
  dialogImageMime.value = ''
  dialogImagePrompt.value = ''
  dialogImageRatio.value = '9:16'
  dialogImageQuality.value = '1K'
  showDialog.value = true
}

const openEditDialog = (task) => {
  dialogMode.value = 'edit'
  editingTaskId.value = task.id
  dialogImagePreview.value = task.originSrc
  dialogImageBase64.value = task.originBase64
  dialogImageMime.value = task.originMime
  dialogImagePrompt.value = task.imagePrompt
  dialogImageRatio.value = task.imageRatio
  dialogImageQuality.value = task.imageQuality
  showDialog.value = true
}

const closeDialog = () => { showDialog.value = false }

// 图片处理
const handleDialogImage = (file) => {
  if (!file) return
  if (!file.type.startsWith('image/')) { emit('toast', '请选择图片文件', 'error'); return }
  if (file.size > 10 * 1024 * 1024) { emit('toast', '图片不能超过 10MB', 'error'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    dialogImagePreview.value = dataUrl
    dialogImageMime.value = file.type
    dialogImageBase64.value = dataUrl.split(',')[1]
  }
  reader.readAsDataURL(file)
}
const handleDialogFileSelect = (event) => {
  handleDialogImage(event.target.files[0])
  if (dialogFileInput.value) dialogFileInput.value.value = ''
}
const onDragEnter = (e) => { e.preventDefault(); dialogIsDragging.value = true }
const onDragOver = (e) => { e.preventDefault(); dialogIsDragging.value = true }
const onDragLeave = (e) => {
  e.preventDefault()
  if (e.currentTarget.contains(e.relatedTarget)) return
  dialogIsDragging.value = false
}
const onDrop = (e) => {
  e.preventDefault()
  dialogIsDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) handleDialogImage(file)
}
const removeDialogImage = () => {
  dialogImagePreview.value = ''
  dialogImageBase64.value = ''
  dialogImageMime.value = ''
}

// ==================== 视频生成 弹窗 ====================
const showVideoDialog = ref(false)
const videoDialogTaskId = ref(null)
const videoDialogPrompt = ref('')
const videoDialogOrientation = ref('portrait')

const openVideoDialog = (task) => {
  if (isTaskBusy(task)) return
  if (!task.resultImageBase64) {
    emit('toast', '请先确认图片生成结果', 'error')
    return
  }
  videoDialogTaskId.value = task.id
  videoDialogPrompt.value = task.videoPrompt || ''
  videoDialogOrientation.value = task.videoOrientation || 'portrait'
  showVideoDialog.value = true
}

const closeVideoDialog = () => { showVideoDialog.value = false }

const submitVideoDialog = () => {
  if (!videoDialogPrompt.value.trim()) {
    emit('toast', '请输入视频提示词', 'error')
    return
  }
  const task = taskList.value.find(t => t.id === videoDialogTaskId.value)
  if (!task) return

  task.videoPrompt = videoDialogPrompt.value
  task.videoOrientation = videoDialogOrientation.value
  showVideoDialog.value = false

  generateVideo(task)
}

// ==================== 统计信息 ====================
const stats = computed(() => {
  const total = taskList.value.length
  const completed = taskList.value.filter(t => t.status === 'completed').length
  const processing = taskList.value.filter(t => ['image_processing', 'video_processing'].includes(t.status)).length
  const failed = taskList.value.filter(t => t.status === 'failed').length
  return { total, completed, processing, failed }
})

// ==================== 提交图片任务 ====================
const submitDialog = () => {
  if (!dialogImageBase64.value) { emit('toast', '请先选择图片', 'error'); return }
  if (!dialogImagePrompt.value.trim()) { emit('toast', '请输入图片提示词', 'error'); return }

  if (dialogMode.value === 'edit') {
    const task = taskList.value.find(t => t.id === editingTaskId.value)
    if (task) {
      task.originSrc = dialogImagePreview.value
      task.originBase64 = dialogImageBase64.value
      task.originMime = dialogImageMime.value
      task.imagePrompt = dialogImagePrompt.value
      task.imageRatio = dialogImageRatio.value
      task.imageQuality = dialogImageQuality.value
      showDialog.value = false
      emit('toast', '任务已更新', 'success')
    }
    return
  }

  // 添加模式
  const task = reactive({
    id: ++taskIdCounter,
    originSrc: dialogImagePreview.value,
    originBase64: dialogImageBase64.value,
    originMime: dialogImageMime.value,
    imagePrompt: dialogImagePrompt.value,
    imageRatio: dialogImageRatio.value,
    imageQuality: dialogImageQuality.value,
    videoPrompt: '',
    videoOrientation: 'portrait',
    resultImageSrc: '',
    resultImageBase64: '',
    resultImageMime: '',
    videoUrl: '',
    status: 'pending',
    statusText: '待处理',
  })
  taskList.value.unshift(task)
  showDialog.value = false

  // 仅启动图片生成
  generateImage(task)
}

// ==================== 图片生成 ====================
const generateImage = async (task) => {
  task.status = 'image_processing'
  task.statusText = '图片生成中...'
  task.resultImageSrc = ''
  task.resultImageBase64 = ''
  task.resultImageMime = ''

  let maxRetry = 0
  try {
    const settings = await window.pywebview.api.get_all_settings()
    if (settings.auto_retry === 'true') {
      maxRetry = parseInt(settings.image_max_retry || '3', 10)
    }
  } catch { /* ignore */ }

  let attempts = 0
  let lastError = ''

  while (attempts <= maxRetry) {
    if (attempts > 0) {
      task.statusText = `图片重试中 (${attempts}/${maxRetry})...`
    }
    try {
      const res = await window.pywebview.api.debug_nanobanana(
        task.imagePrompt,
        task.originBase64,
        task.originMime,
        task.imageRatio,
        task.imageQuality
      )
      if (res.ok && res.image_data && res.mime_type) {
        task.resultImageSrc = `data:${res.mime_type};base64,${res.image_data}`
        task.resultImageBase64 = res.image_data
        task.resultImageMime = res.mime_type
        task.status = 'image_done'
        task.statusText = '图片已完成，待生成视频'
        return true
      } else {
        lastError = res.msg || '图片生成失败'
      }
    } catch (e) {
      lastError = String(e)
    }
    attempts++
  }

  task.status = 'failed'
  task.statusText = `图片失败: ${lastError}`
  return false
}

// ==================== 视频生成 ====================
const generateVideo = async (task) => {
  task.status = 'video_processing'
  task.statusText = '视频生成中...'
  task.videoUrl = ''

  let maxRetry = 0
  try {
    const settings = await window.pywebview.api.get_all_settings()
    if (settings.auto_retry === 'true') {
      maxRetry = parseInt(settings.video_max_retry || '3', 10)
    }
  } catch { /* ignore */ }

  let attempts = 0
  let lastError = ''

  while (attempts <= maxRetry) {
    if (attempts > 0) {
      task.statusText = `视频重试中 (${attempts}/${maxRetry})...`
    }
    try {
      const res = await window.pywebview.api.veo_image_to_video(
        task.videoPrompt,
        task.resultImageBase64,
        task.resultImageMime,
        task.videoOrientation
      )
      if (res.ok && res.video_url) {
        task.videoUrl = res.video_url
        task.status = 'completed'
        task.statusText = '已完成'
        try {
          const settings = await window.pywebview.api.get_all_settings()
          if (settings.auto_download === 'true') {
            downloadVideo(task, true)
          }
        } catch { /* ignore */ }
        return true
      } else {
        lastError = res.msg || '视频生成失败'
      }
    } catch (e) {
      lastError = String(e)
    }
    attempts++
  }

  task.status = 'failed'
  task.statusText = `视频失败: ${lastError}`
  return false
}

// ==================== 操作 ====================
const isTaskBusy = (task) => ['image_processing', 'video_processing'].includes(task.status)

const regenImage = (task) => {
  if (isTaskBusy(task)) return
  task.videoUrl = ''
  task.videoPrompt = ''
  task.videoOrientation = 'portrait'
  generateImage(task)
}

const regenVideo = (task) => {
  if (isTaskBusy(task)) return
  if (!task.resultImageBase64) {
    emit('toast', '暂无生成图片，请先重新生成图片', 'error')
    return
  }
  // 重新打开视频弹窗让用户确认/修改参数
  openVideoDialog(task)
}

const deleteTask = (idx) => {
  if (isTaskBusy(taskList.value[idx])) {
    emit('toast', '任务正在处理中，无法删除', 'error')
    return
  }
  taskList.value.splice(idx, 1)
}

const deleteAllTasks = () => {
  if (taskList.value.some(t => isTaskBusy(t))) {
    emit('toast', '有任务正在处理中，无法全部删除', 'error')
    return
  }
  taskList.value = []
}

const downloadImage = async (task) => {
  if (!task.resultImageBase64) { emit('toast', '暂无生成图片', 'error'); return }
  try {
    emit('toast', '开始下载图片...', 'success')
    const res = await window.pywebview.api.download_image(task.resultImageBase64, task.resultImageMime, 'veo_product')
    if (res.ok) emit('toast', '图片已保存', 'success')
    else emit('toast', res.msg || '下载失败', 'error')
  } catch { emit('toast', '下载异常', 'error') }
}

const downloadVideo = async (task, silent = false) => {
  if (!task.videoUrl) { if (!silent) emit('toast', '暂无视频链接', 'error'); return }
  try {
    if (!silent) emit('toast', '开始下载视频...', 'success')
    const res = await window.pywebview.api.download_veo_video(task.videoUrl)
    if (res.ok) { if (!silent) emit('toast', '视频已保存', 'success') }
    else { if (!silent) emit('toast', res.msg || '下载失败', 'error') }
  } catch { if (!silent) emit('toast', '下载异常', 'error') }
}

// ==================== 预览 ====================
const previewType = ref('')
const previewSrc = ref('')
const showPreview = ref(false)
const openImagePreview = (src) => { previewType.value = 'image'; previewSrc.value = src; showPreview.value = true }
const openVideoPreview = (url) => { previewType.value = 'video'; previewSrc.value = url; showPreview.value = true }
const closePreview = () => { showPreview.value = false; previewSrc.value = ''; previewType.value = '' }

// 状态标签样式类
const statusClass = (status) => {
  if (status === 'pending') return 'pending'
  if (status === 'image_processing' || status === 'video_processing') return 'processing'
  if (status === 'image_done') return 'image-done'
  if (status === 'completed') return 'completed'
  return 'failed'
}
</script>

<template>
  <div class="page">
    <!-- 顶栏 -->
    <div class="page-toolbar">
      <h2 class="page-title">VEO 带货</h2>
      <div class="toolbar-actions">
        <span v-if="stats.total > 0" class="stats-text">
          共 {{ stats.total }} 条
          <template v-if="stats.processing > 0"> · <span class="stats-processing">{{ stats.processing }} 处理中</span></template>
          <template v-if="stats.completed > 0"> · <span class="stats-completed">{{ stats.completed }} 完成</span></template>
          <template v-if="stats.failed > 0"> · <span class="stats-failed">{{ stats.failed }} 失败</span></template>
        </span>
        <button v-if="taskList.length > 0" class="tool-btn delete-all-btn" @click="deleteAllTasks">
          <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          <span>全部删除</span>
        </button>
        <button class="tool-btn add-btn" @click="openAddDialog()">
          <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span>添加任务</span>
        </button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="page-body">
      <!-- 空状态 -->
      <div v-if="taskList.length === 0" class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
          <line x1="8" y1="21" x2="16" y2="21"/>
          <line x1="12" y1="17" x2="12" y2="21"/>
        </svg>
        <p class="empty-text">暂无带货任务</p>
        <p class="empty-hint">点击"添加任务"上传商品图生成图片，确认后再生成视频</p>
      </div>

      <!-- 列表 -->
      <div v-else class="list-wrap">
        <div class="list-header">
          <div class="col col-index">#</div>
          <div class="col col-origin">原图</div>
          <div class="col col-result">生成图</div>
          <div class="col col-status">状态</div>
          <div class="col col-actions">操作</div>
        </div>
        <div
          v-for="(task, idx) in taskList"
          :key="task.id"
          class="list-row"
        >
          <div class="col col-index">{{ taskList.length - idx }}</div>
          <div class="col col-origin">
            <div class="thumb clickable" @click="openImagePreview(task.originSrc)">
              <img :src="task.originSrc" alt="原图" />
            </div>
          </div>
          <div class="col col-result">
            <div v-if="task.resultImageSrc" class="thumb clickable" @click="openImagePreview(task.resultImageSrc)">
              <img :src="task.resultImageSrc" alt="生成图" />
            </div>
            <span v-else class="no-result">—</span>
          </div>
          <div class="col col-status">
            <span :class="['status-tag', statusClass(task.status)]">{{ task.statusText }}</span>
          </div>
          <div class="col col-actions">
            <!-- 图片重新生成 -->
            <button
              class="action-btn regen-img-btn"
              @click="regenImage(task)"
              :disabled="isTaskBusy(task)"
              title="图片重新生成"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
              </svg>
            </button>
            <!-- 生成视频 / 视频重新生成 -->
            <button
              class="action-btn gen-vid-btn"
              @click="task.videoUrl ? regenVideo(task) : openVideoDialog(task)"
              :disabled="isTaskBusy(task) || !task.resultImageBase64"
              :title="task.videoUrl ? '视频重新生成' : '生成视频'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
              </svg>
            </button>
            <!-- 编辑图片参数 -->
            <button
              class="action-btn edit-btn"
              @click="openEditDialog(task)"
              :disabled="isTaskBusy(task)"
              title="编辑图片参数"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
            </button>
            <!-- 下载图片 -->
            <button
              v-if="task.resultImageBase64"
              class="action-btn download-btn"
              @click="downloadImage(task)"
              title="下载图片"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
                <line x1="12" y1="16" x2="12" y2="22" stroke-width="0"/>
              </svg>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="download-overlay-icon">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </button>
            <!-- 下载视频 -->
            <button
              v-if="task.videoUrl"
              class="action-btn download-vid-btn"
              @click="downloadVideo(task)"
              title="下载视频"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </button>
            <!-- 播放视频 -->
            <button
              v-if="task.videoUrl"
              class="action-btn view-btn"
              @click="openVideoPreview(task.videoUrl)"
              title="播放视频"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
            </button>
            <!-- 删除 -->
            <button
              class="action-btn delete-btn"
              @click="deleteTask(idx)"
              :disabled="isTaskBusy(task)"
              title="删除"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑图片 弹窗 -->
    <Teleport to="body">
      <div v-if="showDialog" class="dialog-overlay" @click.self="closeDialog">
        <div class="dialog dialog--image">
          <div class="dialog-header">
            <h3 class="dialog-title">{{ dialogMode === 'edit' ? '编辑图片参数' : '添加带货任务' }}</h3>
            <button class="dialog-close" @click="closeDialog">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <div class="dialog-body dialog-body--split">
            <!-- 左侧：图片上传 -->
            <div class="dialog-left">
              <div class="field">
                <span class="field-label">商品图片（必填，支持拖拽）</span>
                <div
                  v-if="!dialogImagePreview"
                  class="upload-area"
                  :class="{ 'drag-active': dialogIsDragging }"
                  @click="dialogFileInput?.click()"
                  @dragenter="onDragEnter"
                  @dragover="onDragOver"
                  @dragleave="onDragLeave"
                  @drop="onDrop"
                >
                  <input ref="dialogFileInput" type="file" accept="image/*" class="upload-input" @change="handleDialogFileSelect" />
                  <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                  <span class="upload-text">点击或拖拽图片到此处</span>
                  <span class="upload-hint">支持 JPG / PNG / WebP，最大 10MB</span>
                </div>
                <div v-else class="ref-image-preview">
                  <img :src="dialogImagePreview" alt="商品图片" />
                  <button class="remove-btn" @click="removeDialogImage" title="移除图片">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- 右侧：图片参数 -->
            <div class="dialog-right">
              <label class="field">
                <span class="field-label">图片提示词（必填）</span>
                <textarea
                  v-model="dialogImagePrompt"
                  placeholder="描述你期望生成的图片效果，例如：将商品放在优雅的展示场景中"
                  rows="5"
                ></textarea>
              </label>

              <div class="form-row">
                <div class="field field-inline">
                  <span class="field-label">图片比例</span>
                  <div class="toggle-group">
                    <button :class="['toggle-btn', { active: dialogImageRatio === '9:16' }]" @click="dialogImageRatio = '9:16'">9:16 竖屏</button>
                    <button :class="['toggle-btn', { active: dialogImageRatio === '16:9' }]" @click="dialogImageRatio = '16:9'">16:9 横屏</button>
                  </div>
                </div>
                <div class="field field-inline">
                  <span class="field-label">图片质量</span>
                  <div class="toggle-group">
                    <button :class="['toggle-btn', { active: dialogImageQuality === '1K' }]" @click="dialogImageQuality = '1K'">1K</button>
                    <button :class="['toggle-btn', { active: dialogImageQuality === '2K' }]" @click="dialogImageQuality = '2K'">2K</button>
                    <button :class="['toggle-btn', { active: dialogImageQuality === '4K' }]" @click="dialogImageQuality = '4K'">4K</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="cancel-btn" @click="closeDialog">取消</button>
            <button class="primary-btn save-btn" @click="submitDialog">
              {{ dialogMode === 'edit' ? '保存修改' : '添加并生成图片' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 视频生成 弹窗 -->
    <Teleport to="body">
      <div v-if="showVideoDialog" class="dialog-overlay" @click.self="closeVideoDialog">
        <div class="dialog dialog--video">
          <div class="dialog-header">
            <h3 class="dialog-title">生成视频</h3>
            <button class="dialog-close" @click="closeVideoDialog">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <div class="dialog-body">
            <label class="field">
              <span class="field-label">视频提示词（必填）</span>
              <textarea
                v-model="videoDialogPrompt"
                placeholder="描述你期望生成的视频效果，例如：让商品缓缓旋转展示各个角度"
                rows="4"
              ></textarea>
            </label>

            <div class="form-row">
              <div class="field field-inline">
                <span class="field-label">视频方向</span>
                <div class="toggle-group">
                  <button :class="['toggle-btn', { active: videoDialogOrientation === 'portrait' }]" @click="videoDialogOrientation = 'portrait'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="toggle-icon"><rect x="5" y="2" width="14" height="20" rx="2"/></svg>
                    竖屏
                  </button>
                  <button :class="['toggle-btn', { active: videoDialogOrientation === 'landscape' }]" @click="videoDialogOrientation = 'landscape'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="toggle-icon"><rect x="2" y="5" width="20" height="14" rx="2"/></svg>
                    横屏
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="cancel-btn" @click="closeVideoDialog">取消</button>
            <button class="primary-btn save-btn" @click="submitVideoDialog">开始生成视频</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 预览弹窗 -->
    <Teleport to="body">
      <div v-if="showPreview" class="preview-overlay" @click="closePreview">
        <button class="preview-close" @click="closePreview">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <img v-if="previewType === 'image'" :src="previewSrc" class="preview-img" @click.stop alt="预览" />
        <video v-else-if="previewType === 'video'" :src="previewSrc" class="preview-video" controls autoplay @click.stop />
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.page { position: relative; min-height: 100%; display: flex; flex-direction: column; }

/* ============ 顶栏 ============ */
.page-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 20px 32px; border-bottom: 1px solid rgba(255,255,255,0.06); flex-shrink: 0; }
.page-title { margin: 0; font-size: 18px; font-weight: 600; color: #e6e9f2; }
.toolbar-actions { display: flex; gap: 10px; align-items: center; }
.stats-text { font-size: 13px; color: rgba(230,233,242,0.45); margin-right: 8px; }
.stats-processing { color: #8ba3ff; }
.stats-completed { color: #34c759; }
.stats-failed { color: #ff453a; }
.tool-btn { display: flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); color: rgba(230,233,242,0.8); font-size: 13px; font-weight: 500; cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease; }
.tool-btn:hover { background: rgba(91,124,255,0.12); border-color: rgba(91,124,255,0.3); color: #8ba3ff; }
.add-btn { border-color: rgba(52,199,89,0.3); background: rgba(52,199,89,0.08); color: #34c759; }
.add-btn:hover { background: rgba(52,199,89,0.18); border-color: rgba(52,199,89,0.5); color: #34c759; }
.delete-all-btn { border-color: rgba(255,69,58,0.3); background: rgba(255,69,58,0.08); color: #ff453a; }
.delete-all-btn:hover { background: rgba(255,69,58,0.18); border-color: rgba(255,69,58,0.5); color: #ff453a; }
.tool-icon { width: 16px; height: 16px; flex-shrink: 0; }

/* ============ 内容区 ============ */
.page-body { flex: 1; padding: 24px 32px; overflow-y: auto; position: relative; }

/* ============ 空状态 ============ */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 20px; }
.empty-icon { width: 64px; height: 64px; color: rgba(230,233,242,0.15); margin-bottom: 20px; }
.empty-text { margin: 0; font-size: 16px; font-weight: 500; color: rgba(230,233,242,0.4); }
.empty-hint { margin: 8px 0 0; font-size: 13px; color: rgba(230,233,242,0.25); }

/* ============ 列表 ============ */
.list-wrap { border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; overflow: hidden; }
.list-header, .list-row { display: flex; align-items: center; }
.list-header { background: rgba(16,20,28,0.9); padding: 10px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.list-header .col { font-size: 12px; font-weight: 600; color: rgba(230,233,242,0.45); text-transform: uppercase; letter-spacing: 0.5px; }
.list-row { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s ease; }
.list-row:last-child { border-bottom: none; }
.list-row:hover { background: rgba(255,255,255,0.02); }

.col-index { width: 40px; flex-shrink: 0; text-align: center; }
.col-origin { width: 80px; flex-shrink: 0; }
.col-result { width: 80px; flex-shrink: 0; }
.col-status { flex: 1; min-width: 0; padding: 0 12px; }
.col-actions { width: 300px; flex-shrink: 0; display: flex; justify-content: center; gap: 5px; flex-wrap: wrap; }

.thumb { width: 56px; height: 56px; border-radius: 8px; overflow: hidden; background: rgba(8,11,18,0.6); border: 1px solid rgba(255,255,255,0.06); }
.thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.thumb.clickable { cursor: pointer; transition: opacity 0.15s ease; }
.thumb.clickable:hover { opacity: 0.8; }
.no-result { font-size: 13px; color: rgba(230,233,242,0.2); display: flex; width: 56px; height: 56px; align-items: center; justify-content: center; }

/* 状态标签 */
.status-tag { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.status-tag.pending { background: rgba(255,214,10,0.1); color: #ffd60a; }
.status-tag.processing { background: rgba(91,124,255,0.1); color: #8ba3ff; }
.status-tag.image-done { background: rgba(100,210,255,0.1); color: #64d2ff; }
.status-tag.completed { background: rgba(52,199,89,0.1); color: #34c759; }
.status-tag.failed { background: rgba(255,69,58,0.1); color: #ff453a; }

/* 操作按钮 */
.action-btn { width: 34px; height: 34px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04); color: rgba(230,233,242,0.6); cursor: pointer; transition: all 0.15s ease; position: relative; }
.action-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.action-btn svg { width: 15px; height: 15px; }
.regen-img-btn:hover:not(:disabled) { background: rgba(100,210,255,0.15); border-color: rgba(100,210,255,0.4); color: #64d2ff; }
.gen-vid-btn:hover:not(:disabled) { background: rgba(175,82,222,0.15); border-color: rgba(175,82,222,0.4); color: #bf5af2; }
.edit-btn:hover:not(:disabled) { background: rgba(91,124,255,0.15); border-color: rgba(91,124,255,0.4); color: #8ba3ff; }
.download-btn:hover:not(:disabled) { background: rgba(52,199,89,0.15); border-color: rgba(52,199,89,0.4); color: #34c759; }
.download-btn { overflow: hidden; }
.download-btn svg:first-child { width: 15px; height: 15px; }
.download-overlay-icon { position: absolute; width: 10px !important; height: 10px !important; bottom: 2px; right: 2px; }
.download-vid-btn:hover:not(:disabled) { background: rgba(52,199,89,0.15); border-color: rgba(52,199,89,0.4); color: #34c759; }
.view-btn:hover:not(:disabled) { background: rgba(91,124,255,0.15); border-color: rgba(91,124,255,0.4); color: #8ba3ff; }
.delete-btn:hover:not(:disabled) { background: rgba(255,69,58,0.15); border-color: rgba(255,69,58,0.4); color: #ff453a; }

/* ============ 弹窗通用 ============ */
.dialog-overlay { position: fixed; inset: 0; z-index: 1000; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); }
.dialog { max-height: calc(100vh - 60px); border-radius: 16px; background: linear-gradient(180deg, rgba(20,24,38,0.98), rgba(12,15,25,0.99)); border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 24px 60px rgba(5,7,12,0.8); overflow: hidden; display: flex; flex-direction: column; }
.dialog--image { width: min(860px, calc(100% - 40px)); }
.dialog--video { width: min(520px, calc(100% - 40px)); }
.dialog-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 24px; border-bottom: 1px solid rgba(255,255,255,0.06); flex-shrink: 0; }
.dialog-title { margin: 0; font-size: 16px; font-weight: 600; color: #e6e9f2; }
.dialog-close { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; padding: 0; border-radius: 8px; border: none; background: transparent; color: rgba(230,233,242,0.5); cursor: pointer; transition: background 0.15s ease, color 0.15s ease; }
.dialog-close:hover { background: rgba(255,255,255,0.08); color: rgba(230,233,242,0.9); }
.dialog-close svg { width: 18px; height: 18px; }
.dialog-body { padding: 24px; overflow-y: auto; flex: 1; }
.dialog-body--split { display: flex; gap: 24px; }
.dialog-left { width: 280px; flex-shrink: 0; display: flex; flex-direction: column; }
.dialog-left .upload-area { flex: 1; min-height: 200px; }
.dialog-left .ref-image-preview { max-height: 100%; }
.dialog-left .ref-image-preview img { max-height: 360px; width: 100%; object-fit: contain; }
.dialog-right { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 24px; border-top: 1px solid rgba(255,255,255,0.06); flex-shrink: 0; }
.cancel-btn { padding: 10px 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); color: rgba(230,233,242,0.7); font-size: 13px; font-weight: 500; cursor: pointer; transition: background 0.2s ease, color 0.2s ease; }
.cancel-btn:hover { background: rgba(255,255,255,0.1); color: rgba(230,233,242,0.9); }
.save-btn { width: auto; padding: 10px 24px; font-size: 13px; }

.field { display: flex; flex-direction: column; gap: 8px; }
.field-label { font-size: 13px; color: rgba(230,233,242,0.6); }

.dialog-body textarea { width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); background: rgba(8,11,18,0.8); color: #f5f7ff; font-size: 14px; font-family: inherit; outline: none; resize: vertical; transition: border-color 0.2s ease, box-shadow 0.2s ease; }
.dialog-body textarea::placeholder { color: rgba(230,233,242,0.4); }
.dialog-body textarea:focus { border-color: rgba(91,124,255,0.6); box-shadow: 0 0 0 3px rgba(91,124,255,0.15); }

/* 表单行 */
.form-row { display: flex; gap: 24px; margin-top: 12px; align-items: flex-start; }
.field-inline { flex: 1; }

/* 切换按钮组 */
.toggle-group { display: flex; gap: 6px; flex-wrap: wrap; }
.toggle-btn { display: flex; align-items: center; gap: 5px; padding: 7px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.04); color: rgba(230,233,242,0.6); font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.2s ease; }
.toggle-btn:hover { background: rgba(91,124,255,0.08); border-color: rgba(91,124,255,0.2); color: rgba(230,233,242,0.8); }
.toggle-btn.active { background: rgba(91,124,255,0.15); border-color: rgba(91,124,255,0.4); color: #8ba3ff; }
.toggle-icon { width: 16px; height: 16px; flex-shrink: 0; }

/* 上传区 */
.upload-area { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 28px 20px; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.1); background: rgba(8,11,18,0.5); cursor: pointer; transition: border-color 0.2s ease, background 0.2s ease; }
.upload-area:hover, .upload-area.drag-active { border-color: rgba(91,124,255,0.4); background: rgba(91,124,255,0.05); }
.upload-input { display: none; }
.upload-icon { width: 32px; height: 32px; color: rgba(230,233,242,0.3); }
.upload-text { font-size: 14px; color: rgba(230,233,242,0.6); }
.upload-hint { font-size: 12px; color: rgba(230,233,242,0.3); }

.ref-image-preview { position: relative; display: inline-block; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); background: rgba(8,11,18,0.6); }
.ref-image-preview img { display: block; max-width: 100%; max-height: 200px; object-fit: contain; }
.remove-btn { position: absolute; top: 8px; right: 8px; width: 28px; height: 28px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 8px; border: none; background: rgba(0,0,0,0.7); color: rgba(255,255,255,0.8); cursor: pointer; transition: background 0.2s ease; }
.remove-btn:hover { background: rgba(255,69,58,0.8); }
.remove-btn svg { width: 14px; height: 14px; }

/* ============ 预览 ============ */
.preview-overlay { position: fixed; inset: 0; z-index: 2000; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); cursor: zoom-out; }
.preview-close { position: absolute; top: 20px; right: 20px; width: 40px; height: 40px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 10px; border: none; background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.8); cursor: pointer; transition: background 0.15s ease; z-index: 1; }
.preview-close:hover { background: rgba(255,255,255,0.2); }
.preview-close svg { width: 20px; height: 20px; }
.preview-img { max-width: 90vw; max-height: 90vh; object-fit: contain; border-radius: 8px; cursor: default; }
.preview-video { max-width: 90vw; max-height: 90vh; border-radius: 8px; cursor: default; outline: none; }
</style>
