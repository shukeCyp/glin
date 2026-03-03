<script setup>
import { ref, onMounted, watch } from 'vue'

const emit = defineEmits(['toast'])

const themes = [
  { id: 'warm-cream', name: '暖奶油', colors: ['#faf7f5', '#c8607a', '#f5f0ed'] },
  { id: 'dark-rose', name: '暗夜玫瑰', colors: ['#0e0b09', '#d4748a', '#1a1614'] },
  { id: 'forest', name: '森林', colors: ['#f4f7f4', '#3d8b5e', '#eaf0ea'] },
  { id: 'eye-care', name: '护眼', colors: ['#f5f0e6', '#7a9a4a', '#ede8de'] },
  { id: 'ocean', name: '海洋蓝', colors: ['#f5f8fa', '#3a7fc8', '#edf2f6'] },
  { id: 'midnight', name: '午夜蓝', colors: ['#0c1018', '#5b9cff', '#151a26'] },
  { id: 'lavender', name: '薰衣草', colors: ['#f8f5fa', '#8a5cc8', '#f0ecf5'] },
]

const currentTheme = ref('warm-cream')

const applyTheme = (themeId) => {
  currentTheme.value = themeId
  document.documentElement.setAttribute('data-theme', themeId)
}

// API Keys
const dayangyu_api_key = ref('')
const yunwu_api_key = ref('')
const xiaobanshou_api_key = ref('')
const bandianwa_api_key = ref('')
const haotian_api_key = ref('')
const glin_api_key = ref('')

// Model selections
const sora2_model = ref('dayangyu')
const nanobanana_model = ref('yunwu')

// Sora2 通用配置
const sora2_orientation = ref('portrait')
const sora2_duration = ref('10')

// NanoBanana image settings
const nanobanana_ratio = ref('9:16')
const nanobanana_quality = ref('1K')

// 下载配置
const auto_download = ref(false)
const download_path = ref('')

// 重试配置
const auto_retry = ref(false)
const image_max_retry = ref('3')
const video_max_retry = ref('3')

// 线程池配置
const thread_pool_size = ref('10')

// 数据文件状态
const dataStatus = ref(null)


const selectDownloadFolder = async () => {
  try {
    const res = await window.pywebview.api.select_folder()
    if (res.ok && res.path) {
      download_path.value = res.path
      emit('toast', '已选择下载目录', 'success')
    }
  } catch {
    emit('toast', '选择文件夹失败', 'error')
  }
}

const saveSettings = async () => {
  try {
    await window.pywebview.api.save_settings({
      theme: currentTheme.value,
      dayangyu_api_key: dayangyu_api_key.value,
      yunwu_api_key: yunwu_api_key.value,
      xiaobanshou_api_key: xiaobanshou_api_key.value,
      bandianwa_api_key: bandianwa_api_key.value,
      haotian_api_key: haotian_api_key.value,
      glin_api_key: glin_api_key.value,
      sora2_model: sora2_model.value,
      sora2_orientation: sora2_orientation.value,
      sora2_duration: sora2_duration.value,
      nanobanana_model: nanobanana_model.value,
      nanobanana_ratio: nanobanana_ratio.value,
      nanobanana_quality: nanobanana_quality.value,
      auto_download: auto_download.value ? 'true' : 'false',
      download_path: download_path.value,
      auto_retry: auto_retry.value ? 'true' : 'false',
      image_max_retry: image_max_retry.value,
      video_max_retry: video_max_retry.value,
      thread_pool_size: thread_pool_size.value,
    })
    emit('toast', '设置已保存', 'success')
  } catch (e) {
    emit('toast', '保存失败', 'error')
  }
}

const loadDataStatus = async () => {
  try {
    const res = await window.pywebview.api.get_data_status()
    if (res.ok) {
      dataStatus.value = res
    }
  } catch { /* ignore */ }
}

const openRootDirectory = async () => {
  try {
    const res = await window.pywebview.api.open_root_directory()
    if (res.ok) {
      emit('toast', '已打开根目录', 'success')
    } else {
      emit('toast', res.msg || '打开失败', 'error')
    }
  } catch {
    emit('toast', '打开失败', 'error')
  }
}

const cleaningLogs = ref(false)
const cleanLogs = async () => {
  cleaningLogs.value = true
  try {
    const res = await window.pywebview.api.clean_logs()
    if (res.ok) {
      emit('toast', `已清理 ${res.count} 个日志文件`, 'success')
      await loadDataStatus()
    } else {
      emit('toast', res.msg || '清理失败', 'error')
    }
  } catch {
    emit('toast', '清理失败', 'error')
  } finally {
    cleaningLogs.value = false
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0) + ' ' + units[i]
}

const loadSettings = async () => {
  try {
    const settings = await window.pywebview.api.get_all_settings()
    if (settings.theme) {
      currentTheme.value = settings.theme
      applyTheme(settings.theme)
    }
    if (settings.dayangyu_api_key) dayangyu_api_key.value = settings.dayangyu_api_key
    if (settings.yunwu_api_key) yunwu_api_key.value = settings.yunwu_api_key
    if (settings.xiaobanshou_api_key) xiaobanshou_api_key.value = settings.xiaobanshou_api_key
    if (settings.bandianwa_api_key) bandianwa_api_key.value = settings.bandianwa_api_key
    if (settings.haotian_api_key) haotian_api_key.value = settings.haotian_api_key
    if (settings.glin_api_key) glin_api_key.value = settings.glin_api_key
    if (settings.sora2_model) sora2_model.value = settings.sora2_model
    if (settings.nanobanana_model) nanobanana_model.value = settings.nanobanana_model
    if (settings.nanobanana_ratio) nanobanana_ratio.value = settings.nanobanana_ratio
    if (settings.nanobanana_quality) nanobanana_quality.value = settings.nanobanana_quality
    if (settings.sora2_orientation) sora2_orientation.value = settings.sora2_orientation
    if (settings.sora2_duration) sora2_duration.value = settings.sora2_duration
    if (settings.auto_download) auto_download.value = settings.auto_download === 'true'
    if (settings.download_path) download_path.value = settings.download_path
    if (settings.auto_retry) auto_retry.value = settings.auto_retry === 'true'
    if (settings.image_max_retry) image_max_retry.value = settings.image_max_retry
    if (settings.video_max_retry) video_max_retry.value = settings.video_max_retry
    if (settings.thread_pool_size) thread_pool_size.value = settings.thread_pool_size
  } catch {
    // Settings not loaded yet
  }
}

onMounted(() => {
  loadSettings()
  loadDataStatus()
})
</script>

<template>
  <div class="page">
    <div class="page-body">
      <div class="settings-sections">

        <!-- ====== 主题配色 ====== -->
        <section class="settings-section-block">
          <h2 class="section-heading">主题配色</h2>
          <div class="theme-grid">
            <button
              v-for="t in themes"
              :key="t.id"
              :class="['theme-card', { active: currentTheme === t.id }]"
              @click="applyTheme(t.id)"
            >
              <div class="theme-preview">
                <div class="theme-dot" :style="{ background: t.colors[0], border: '1px solid rgba(0,0,0,0.1)' }"></div>
                <div class="theme-dot" :style="{ background: t.colors[1] }"></div>
                <div class="theme-dot" :style="{ background: t.colors[2], border: '1px solid rgba(0,0,0,0.08)' }"></div>
              </div>
              <span class="theme-name">{{ t.name }}</span>
              <div v-if="currentTheme === t.id" class="theme-check">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            </button>
          </div>
        </section>

        <!-- ====== API Keys ====== -->
        <section class="settings-section-block">
          <h2 class="section-heading">API Keys</h2>
          <div class="settings-grid">
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">DYY</h3></div>
              <div class="card-body">
                <label class="field">
                  <span class="field-label">API Key</span>
                  <input v-model="dayangyu_api_key" type="password" placeholder="请输入 DYY API Key" autocomplete="off" />
                </label>
              </div>
            </div>
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">YW</h3></div>
              <div class="card-body">
                <label class="field">
                  <span class="field-label">API Key</span>
                  <input v-model="yunwu_api_key" type="password" placeholder="请输入 YW API Key" autocomplete="off" />
                </label>
              </div>
            </div>
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">XBS</h3></div>
              <div class="card-body">
                <label class="field">
                  <span class="field-label">API Key</span>
                  <input v-model="xiaobanshou_api_key" type="password" placeholder="请输入 XBS API Key" autocomplete="off" />
                </label>
              </div>
            </div>
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">BDW</h3></div>
              <div class="card-body">
                <label class="field">
                  <span class="field-label">API Key</span>
                  <input v-model="bandianwa_api_key" type="password" placeholder="请输入 BDW API Key" autocomplete="off" />
                </label>
              </div>
            </div>
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">HT</h3></div>
              <div class="card-body">
                <label class="field">
                  <span class="field-label">API Key</span>
                  <input v-model="haotian_api_key" type="password" placeholder="请输入 HT API Key" autocomplete="off" />
                </label>
              </div>
            </div>
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">Glin</h3></div>
              <div class="card-body">
                <label class="field">
                  <span class="field-label">API Key</span>
                  <input v-model="glin_api_key" type="password" placeholder="请输入 Glin API Key" autocomplete="off" />
                </label>
              </div>
            </div>
          </div>
        </section>

        <!-- ====== Sora2 配置 ====== -->
        <section class="settings-section-block">
          <h2 class="section-heading">Sora2 视频生成</h2>
          <div class="settings-grid">
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">渠道选择</h3></div>
              <div class="card-body">
                <div class="radio-group">
                  <label class="radio-item"><input type="radio" v-model="sora2_model" value="dayangyu" /><span class="radio-label">DYY</span></label>
                  <label class="radio-item"><input type="radio" v-model="sora2_model" value="yunwu" /><span class="radio-label">YW</span></label>
                  <label class="radio-item"><input type="radio" v-model="sora2_model" value="xiaobanshou" /><span class="radio-label">XBS</span></label>
                  <label class="radio-item"><input type="radio" v-model="sora2_model" value="bandianwa" /><span class="radio-label">BDW</span></label>
                </div>
              </div>
            </div>
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">视频参数</h3></div>
              <div class="card-body">
                <div class="settings-sub-section">
                  <span class="sub-section-label">比例</span>
                  <div class="radio-group horizontal">
                    <label class="radio-item"><input type="radio" v-model="sora2_orientation" value="portrait" /><span class="radio-label">竖屏 9:16</span></label>
                    <label class="radio-item"><input type="radio" v-model="sora2_orientation" value="landscape" /><span class="radio-label">横屏 16:9</span></label>
                  </div>
                </div>
                <div class="settings-sub-section">
                  <span class="sub-section-label">时长</span>
                  <div class="radio-group horizontal">
                    <label class="radio-item"><input type="radio" v-model="sora2_duration" value="10" /><span class="radio-label">10秒</span></label>
                    <label class="radio-item"><input type="radio" v-model="sora2_duration" value="15" /><span class="radio-label">15秒</span></label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ====== NanoBanana 配置 ====== -->
        <section class="settings-section-block">
          <h2 class="section-heading">NanoBanana 图片生成</h2>
          <div class="settings-grid">
            <div class="settings-card wide-card">
              <div class="card-body">
                <div class="settings-sub-section">
                  <span class="sub-section-label">生图渠道</span>
                  <div class="radio-group horizontal">
                    <label class="radio-item"><input type="radio" v-model="nanobanana_model" value="yunwu" /><span class="radio-label">YW 渠道</span></label>
                    <label class="radio-item"><input type="radio" v-model="nanobanana_model" value="haotian" /><span class="radio-label">HT 渠道</span></label>
                    <label class="radio-item"><input type="radio" v-model="nanobanana_model" value="glin" /><span class="radio-label">Glin 渠道</span></label>
                  </div>
                </div>
                <div class="settings-sub-section">
                  <span class="sub-section-label">图片比例</span>
                  <div class="radio-group horizontal">
                    <label class="radio-item"><input type="radio" v-model="nanobanana_ratio" value="9:16" /><span class="radio-label">9:16</span></label>
                    <label class="radio-item"><input type="radio" v-model="nanobanana_ratio" value="16:9" /><span class="radio-label">16:9</span></label>
                  </div>
                </div>
                <div class="settings-sub-section">
                  <span class="sub-section-label">图片清晰度</span>
                  <div class="radio-group horizontal">
                    <label class="radio-item"><input type="radio" v-model="nanobanana_quality" value="1K" /><span class="radio-label">1K</span></label>
                    <label class="radio-item"><input type="radio" v-model="nanobanana_quality" value="2K" /><span class="radio-label">2K</span></label>
                    <label class="radio-item"><input type="radio" v-model="nanobanana_quality" value="4K" /><span class="radio-label">4K</span></label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ====== 下载与重试 ====== -->
        <section class="settings-section-block">
          <h2 class="section-heading">下载与重试</h2>
          <div class="settings-grid">
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">下载配置</h3></div>
              <div class="card-body">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="auto_download" />
                  <span class="checkbox-label">自动下载生成结果</span>
                </label>
                <div class="field" style="margin-top: 16px;">
                  <span class="field-label">下载路径</span>
                  <div class="path-row">
                    <input v-model="download_path" type="text" placeholder="请选择下载目录" readonly class="path-input" />
                    <button class="select-folder-btn" @click="selectDownloadFolder">选择文件夹</button>
                  </div>
                </div>
              </div>
            </div>
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">重试配置</h3></div>
              <div class="card-body">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="auto_retry" />
                  <span class="checkbox-label">失败后自动重试</span>
                </label>
                <label class="field" style="margin-top: 16px;">
                  <span class="field-label">图片最大重试次数</span>
                  <input v-model="image_max_retry" type="number" min="0" max="10" placeholder="3" />
                </label>
                <label class="field" style="margin-top: 16px;">
                  <span class="field-label">视频最大重试次数</span>
                  <input v-model="video_max_retry" type="number" min="0" max="10" placeholder="3" />
                </label>
              </div>
            </div>
          </div>
        </section>

        <!-- ====== 系统 ====== -->
        <section class="settings-section-block">
          <h2 class="section-heading">系统</h2>
          <div class="settings-grid">
            <div class="settings-card">
              <div class="card-header"><h3 class="card-title">线程池</h3></div>
              <div class="card-body">
                <label class="field">
                  <span class="field-label">线程池大小（修改后需重启生效）</span>
                  <input v-model="thread_pool_size" type="number" min="1" max="50" placeholder="10" />
                </label>
              </div>
            </div>
            <div class="settings-card" v-if="dataStatus">
              <div class="card-header"><h3 class="card-title">数据文件</h3></div>
              <div class="card-body">
                <div class="data-status-grid">
                  <div class="data-status-item">
                    <div class="data-status-icon db-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                    </div>
                    <div class="data-status-info">
                      <span class="data-status-label">数据库</span>
                      <span class="data-status-value">{{ formatFileSize(dataStatus.db_size) }}</span>
                    </div>
                  </div>
                  <div class="data-status-item">
                    <div class="data-status-icon log-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                    </div>
                    <div class="data-status-info">
                      <span class="data-status-label">日志</span>
                      <span class="data-status-value">{{ dataStatus.log_files }} 个，{{ formatFileSize(dataStatus.log_total_size) }}</span>
                    </div>
                  </div>
                </div>
                <div style="margin-top: 16px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                  <button class="action-btn" @click="openRootDirectory">
                    <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                    <span>打开根目录</span>
                  </button>
                  <button class="action-btn danger-btn" @click="cleanLogs" :disabled="cleaningLogs || (dataStatus && dataStatus.log_files <= 1)">
                    <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                    <span>{{ cleaningLogs ? '清理中...' : '清理日志' }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

      </div>
    </div>

    <button class="floating-save-btn" @click="saveSettings">
      <svg class="floating-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
      <span>保存设置</span>
    </button>
  </div>
</template>

<style scoped>
.page { position: relative; min-height: 100%; }
.page-body { padding: 32px; padding-bottom: 80px; }
.settings-sections { display: flex; flex-direction: column; gap: 36px; }
.section-heading { margin: 0 0 16px 0; font-size: 16px; font-weight: 600; color: var(--accent); letter-spacing: 0.3px; }

/* Theme selector */
.theme-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 12px; }
.theme-card { position: relative; display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 16px 12px; border-radius: 14px; border: 2px solid var(--border); background: var(--bg-card); cursor: pointer; transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease; }
.theme-card:hover { border-color: var(--accent-border); transform: translateY(-2px); box-shadow: var(--shadow-card); }
.theme-card.active { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-focus); }
.theme-preview { display: flex; gap: 6px; align-items: center; }
.theme-dot { width: 22px; height: 22px; border-radius: 50%; }
.theme-name { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.theme-check { position: absolute; top: 8px; right: 8px; width: 20px; height: 20px; color: var(--accent); }
.theme-check svg { width: 100%; height: 100%; }

/* Floating save */
.floating-save-btn { position: fixed; bottom: 28px; right: 28px; z-index: 100; display: flex; align-items: center; gap: 8px; padding: 14px 24px; border-radius: 14px; border: none; background: linear-gradient(135deg, var(--accent), var(--accent-hover)); color: var(--btn-text); font-size: 14px; font-weight: 600; cursor: pointer; box-shadow: var(--shadow-float); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.floating-save-btn:hover { transform: translateY(-2px); }
.floating-save-btn:active { transform: translateY(0); }
.floating-icon { width: 18px; height: 18px; flex-shrink: 0; }

/* Cards grid */
.settings-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.wide-card { grid-column: 1 / -1; }
.settings-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-card); }
.card-header { padding: 14px 20px; border-bottom: 1px solid var(--border-light); }
.card-title { margin: 0; font-size: 14px; font-weight: 600; color: var(--text-primary); }
.card-body { padding: 18px 20px; }

.field { display: flex; flex-direction: column; gap: 8px; }
.field-label { font-size: 13px; color: var(--text-tertiary); }
.radio-group { display: flex; flex-direction: column; gap: 12px; }
.radio-group.horizontal { flex-direction: row; flex-wrap: wrap; gap: 16px; }
.settings-sub-section { display: flex; flex-direction: column; gap: 10px; }
.settings-sub-section + .settings-sub-section { margin-top: 18px; }
.sub-section-label { font-size: 13px; color: var(--text-tertiary); }

select { width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--border-strong); background: var(--bg-surface); color: var(--text-primary); font-size: 14px; outline: none; cursor: pointer; appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='gray' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 14px center; transition: border-color 0.2s ease, box-shadow 0.2s ease; }
select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-focus); }
select option { background: var(--bg-card); color: var(--text-primary); }

.radio-item { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.radio-item input[type="radio"] { width: 18px; height: 18px; margin: 0; accent-color: var(--accent); cursor: pointer; }
.radio-label { font-size: 14px; color: var(--text-strong); }
.checkbox-item { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.checkbox-item input[type="checkbox"] { width: 18px; height: 18px; margin: 0; accent-color: var(--accent); cursor: pointer; }
.checkbox-label { font-size: 14px; color: var(--text-strong); }

.path-row { display: flex; gap: 10px; align-items: center; }
.path-input { flex: 1; cursor: default; color: var(--text-muted) !important; }
.select-folder-btn { flex-shrink: 0; padding: 10px 18px; border-radius: 10px; border: 1px solid var(--border-strong); background: var(--bg-card); color: var(--text-secondary); font-size: 13px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease; }
.select-folder-btn:hover { background: var(--accent-bg-subtle); border-color: var(--accent-border); color: var(--accent); }

.data-status-grid { display: flex; gap: 16px; flex-wrap: wrap; }
.data-status-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 10px; background: var(--bg-surface); border: 1px solid var(--border-light); }
.data-status-icon { width: 32px; height: 32px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 8px; }
.data-status-icon svg { width: 18px; height: 18px; }
.db-icon { background: var(--accent-bg); color: var(--accent); }
.log-icon { background: var(--success-bg); color: var(--success); }
.data-status-info { display: flex; flex-direction: column; gap: 2px; }
.data-status-label { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.data-status-value { font-size: 12px; color: var(--text-muted); }

.action-btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 18px; border-radius: 10px; border: 1px solid var(--border-strong); background: var(--bg-card); color: var(--text-secondary); font-size: 13px; font-weight: 500; cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease; }
.action-btn:hover { background: var(--accent-bg-subtle); border-color: var(--accent-border); color: var(--accent); }
.action-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.action-btn:disabled:hover { background: var(--bg-card); border-color: var(--border-strong); color: var(--text-secondary); }
.danger-btn { border-color: var(--error-bg); }
.danger-btn:hover:not(:disabled) { background: var(--error-bg); border-color: var(--error); color: var(--error); }
.action-icon { width: 16px; height: 16px; flex-shrink: 0; }
</style>
