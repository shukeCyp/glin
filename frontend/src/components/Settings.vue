<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['toast'])

// API 模式: official / custom
const api_mode = ref('custom')

// 官方 API
const guanfang_api_key = ref('')
const guanfang_sora2_provider = ref('dayangyu')
const guanfang_sora2_model = ref('')

// 自定义 API Keys
const dayangyu_api_key = ref('')
const yunwu_api_key = ref('')
const xiaobanshou_api_key = ref('')

// Model selections
const sora2_model = ref('dayangyu')
const nanobanana_model = ref('yunwu')

// NanoBanana image settings
const nanobanana_ratio = ref('9:16')
const nanobanana_quality = ref('1K')

// 大洋芋 Sora2 配置
const dayangyu_sora2_model = ref('')

// 云雾 Sora2 配置
const yunwu_sora2_orientation = ref('portrait')
const yunwu_sora2_duration = ref('10')

// 小扳手 Sora2 配置
const xiaobanshou_sora2_model = ref('')

// 斑点蛙 配置
const bandianwa_api_key = ref('')
const bandianwa_sora2_model = ref('')

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
      api_mode: api_mode.value,
      guanfang_api_key: guanfang_api_key.value,
      guanfang_sora2_provider: guanfang_sora2_provider.value,
      guanfang_sora2_model: guanfang_sora2_model.value,
      dayangyu_api_key: dayangyu_api_key.value,
      yunwu_api_key: yunwu_api_key.value,
      xiaobanshou_api_key: xiaobanshou_api_key.value,
      sora2_model: sora2_model.value,
      nanobanana_model: nanobanana_model.value,
      nanobanana_ratio: nanobanana_ratio.value,
      nanobanana_quality: nanobanana_quality.value,
      dayangyu_sora2_model: dayangyu_sora2_model.value,
      yunwu_sora2_orientation: yunwu_sora2_orientation.value,
      yunwu_sora2_duration: yunwu_sora2_duration.value,
      xiaobanshou_sora2_model: xiaobanshou_sora2_model.value,
      bandianwa_api_key: bandianwa_api_key.value,
      bandianwa_sora2_model: bandianwa_sora2_model.value,
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
    if (settings.api_mode) api_mode.value = settings.api_mode
    if (settings.guanfang_api_key) guanfang_api_key.value = settings.guanfang_api_key
    if (settings.guanfang_sora2_provider) guanfang_sora2_provider.value = settings.guanfang_sora2_provider
    if (settings.guanfang_sora2_model) guanfang_sora2_model.value = settings.guanfang_sora2_model
    if (settings.dayangyu_api_key) dayangyu_api_key.value = settings.dayangyu_api_key
    if (settings.yunwu_api_key) yunwu_api_key.value = settings.yunwu_api_key
    if (settings.sora2_model) sora2_model.value = settings.sora2_model
    if (settings.nanobanana_model) nanobanana_model.value = settings.nanobanana_model
    if (settings.nanobanana_ratio) nanobanana_ratio.value = settings.nanobanana_ratio
    if (settings.nanobanana_quality) nanobanana_quality.value = settings.nanobanana_quality
    if (settings.dayangyu_sora2_model) dayangyu_sora2_model.value = settings.dayangyu_sora2_model
    if (settings.yunwu_sora2_orientation) yunwu_sora2_orientation.value = settings.yunwu_sora2_orientation
    if (settings.yunwu_sora2_duration) yunwu_sora2_duration.value = settings.yunwu_sora2_duration
    if (settings.xiaobanshou_api_key) xiaobanshou_api_key.value = settings.xiaobanshou_api_key
    if (settings.xiaobanshou_sora2_model) xiaobanshou_sora2_model.value = settings.xiaobanshou_sora2_model
    if (settings.bandianwa_api_key) bandianwa_api_key.value = settings.bandianwa_api_key
    if (settings.bandianwa_sora2_model) bandianwa_sora2_model.value = settings.bandianwa_sora2_model
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
      <div class="settings-grid">
        <!-- API 设置（模式切换） -->
        <div class="settings-card full-width">
          <div class="card-header">
            <h3 class="card-title">API 设置</h3>
          </div>
          <div class="card-body">
            <div class="radio-group horizontal">
              <label class="radio-item">
                <input
                  type="radio"
                  v-model="api_mode"
                  value="official"
                />
                <span class="radio-label">官方 API</span>
              </label>
              <label class="radio-item">
                <input
                  type="radio"
                  v-model="api_mode"
                  value="custom"
                />
                <span class="radio-label">自定义 API</span>
              </label>
            </div>
          </div>
        </div>

        <!-- ========== 官方 API 模式 ========== -->
        <template v-if="api_mode === 'official'">
          <!-- 官方秘钥 -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">官方秘钥</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">API Key</span>
                <input
                  v-model="guanfang_api_key"
                  type="password"
                  placeholder="请输入官方 API Key"
                  autocomplete="off"
                />
              </label>
            </div>
          </div>

          <!-- 官方 Sora2 渠道选择 -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">Sora2 渠道选择</h3>
            </div>
            <div class="card-body">
              <div class="radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="guanfang_sora2_provider"
                    value="dayangyu"
                  />
                  <span class="radio-label">DYY 渠道</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="guanfang_sora2_provider"
                    value="xiaobanshou"
                  />
                  <span class="radio-label">XBS 渠道</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="guanfang_sora2_provider"
                    value="bandianwa"
                  />
                  <span class="radio-label">BDW 渠道</span>
                </label>
              </div>
            </div>
          </div>

          <!-- DYY Sora2 模型配置（官方） -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">DYY Sora2 配置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">模型</span>
                <select v-model="guanfang_sora2_model">
                  <option value="sora2-pro-landscape-25s">sora2-pro-landscape-25s</option>
                  <option value="sora2-pro-landscape-hd-10s">sora2-pro-landscape-hd-10s</option>
                  <option value="sora2-pro-landscape-hd-15s">sora2-pro-landscape-hd-15s</option>
                  <option value="sora2-pro-portrait-25s">sora2-pro-portrait-25s</option>
                  <option value="sora2-pro-portrait-hd-10s">sora2-pro-portrait-hd-10s</option>
                  <option value="sora2-pro-portrait-hd-15s">sora2-pro-portrait-hd-15s</option>
                </select>
              </label>
            </div>
          </div>

          <!-- XBS Sora2 模型配置（官方） -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">XBS Sora2 配置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">模型</span>
                <select v-model="xiaobanshou_sora2_model">
                  <option value="sora-2">sora-2</option>
                  <option value="sora-2-landscape-10s">sora-2-landscape-10s</option>
                  <option value="sora-2-landscape-15s">sora-2-landscape-15s</option>
                  <option value="sora-2-portrait-10s">sora-2-portrait-10s</option>
                  <option value="sora-2-portrait-15s">sora-2-portrait-15s</option>
                  <option value="sora-2-pro">sora-2-pro</option>
                  <option value="sora-2-pro-landscape-25s">sora-2-pro-landscape-25s</option>
                  <option value="sora-2-pro-landscape-hd-10s">sora-2-pro-landscape-hd-10s</option>
                  <option value="sora-2-pro-landscape-hd-15s">sora-2-pro-landscape-hd-15s</option>
                  <option value="sora-2-pro-portrait-25s">sora-2-pro-portrait-25s</option>
                  <option value="sora-2-pro-portrait-hd-10s">sora-2-pro-portrait-hd-10s</option>
                  <option value="sora-2-pro-portrait-hd-15s">sora-2-pro-portrait-hd-15s</option>
                </select>
              </label>
            </div>
          </div>

          <!-- BDW Sora2 模型配置（官方） -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">BDW Sora2 配置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">模型</span>
                <select v-model="bandianwa_sora2_model">
                  <option value="sora-2-landscape-10s-guanzhuan">sora-2-landscape-10s-guanzhuan</option>
                  <option value="sora-2-landscape-15s-guanzhuan">sora-2-landscape-15s-guanzhuan</option>
                  <option value="sora-2-portrait-10s-guanzhuan">sora-2-portrait-10s-guanzhuan</option>
                  <option value="sora-2-portrait-15s-guanzhuan">sora-2-portrait-15s-guanzhuan</option>
                </select>
              </label>
            </div>
          </div>

          <!-- NanoBanana 配置（官方） -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">NanoBanana 配置</h3>
            </div>
            <div class="card-body">
              <div class="settings-section">
                <span class="section-label">生图渠道</span>
                <div class="radio-group horizontal">
                  <label class="radio-item">
                    <input type="radio" v-model="nanobanana_model" value="yunwu" />
                    <span class="radio-label">YW 渠道</span>
                  </label>
                  <label class="radio-item">
                    <input type="radio" v-model="nanobanana_model" value="haotian" />
                    <span class="radio-label">HT 渠道</span>
                  </label>
                </div>
              </div>
              <div class="settings-section">
                <span class="section-label">图片比例</span>
                <div class="radio-group horizontal">
                  <label class="radio-item">
                    <input type="radio" v-model="nanobanana_ratio" value="9:16" />
                    <span class="radio-label">9:16</span>
                  </label>
                  <label class="radio-item">
                    <input type="radio" v-model="nanobanana_ratio" value="16:9" />
                    <span class="radio-label">16:9</span>
                  </label>
                </div>
              </div>
              <div class="settings-section">
                <span class="section-label">图片清晰度</span>
                <div class="radio-group horizontal">
                  <label class="radio-item">
                    <input type="radio" v-model="nanobanana_quality" value="1K" />
                    <span class="radio-label">1K</span>
                  </label>
                  <label class="radio-item">
                    <input type="radio" v-model="nanobanana_quality" value="2K" />
                    <span class="radio-label">2K</span>
                  </label>
                  <label class="radio-item">
                    <input type="radio" v-model="nanobanana_quality" value="4K" />
                    <span class="radio-label">4K</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ========== 自定义 API 模式 ========== -->
        <template v-if="api_mode === 'custom'">
          <!-- 大洋芋 API -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">DYY API 设置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">API Key</span>
                <input
                  v-model="dayangyu_api_key"
                  type="password"
                  placeholder="请输入 DYY API Key"
                  autocomplete="off"
                />
              </label>
            </div>
          </div>

          <!-- 云雾 API -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">YW API 设置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">API Key</span>
                <input
                  v-model="yunwu_api_key"
                  type="password"
                  placeholder="请输入 YW API Key"
                  autocomplete="off"
                />
              </label>
            </div>
          </div>

          <!-- 小扳手 API -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">XBS API 设置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">API Key</span>
                <input
                  v-model="xiaobanshou_api_key"
                  type="password"
                  placeholder="请输入 XBS API Key"
                  autocomplete="off"
                />
              </label>
            </div>
          </div>

          <!-- 斑点蛙 API -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">BDW API 设置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">API Key</span>
                <input
                  v-model="bandianwa_api_key"
                  type="password"
                  placeholder="请输入 BDW API Key"
                  autocomplete="off"
                />
              </label>
            </div>
          </div>

          <!-- Sora2 模型选择 -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">Sora2 模型选择</h3>
            </div>
            <div class="card-body">
              <div class="radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="sora2_model"
                    value="dayangyu"
                  />
                  <span class="radio-label">DYY API</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="sora2_model"
                    value="yunwu"
                  />
                  <span class="radio-label">YW API</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="sora2_model"
                    value="xiaobanshou"
                  />
                  <span class="radio-label">XBS API</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="sora2_model"
                    value="bandianwa"
                  />
                  <span class="radio-label">BDW API</span>
                </label>
              </div>
            </div>
          </div>

          <!-- 大洋芋 Sora2 配置 -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">DYY Sora2 配置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">模型</span>
                <select v-model="dayangyu_sora2_model">
                  <option value="sora2-pro-landscape-25s">sora2-pro-landscape-25s</option>
                  <option value="sora2-pro-landscape-hd-10s">sora2-pro-landscape-hd-10s</option>
                  <option value="sora2-pro-landscape-hd-15s">sora2-pro-landscape-hd-15s</option>
                  <option value="sora2-pro-portrait-25s">sora2-pro-portrait-25s</option>
                  <option value="sora2-pro-portrait-hd-10s">sora2-pro-portrait-hd-10s</option>
                  <option value="sora2-pro-portrait-hd-15s">sora2-pro-portrait-hd-15s</option>
                </select>
              </label>
            </div>
          </div>

          <!-- 云雾 Sora2 配置 -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">YW Sora2 配置</h3>
            </div>
            <div class="card-body">
              <div class="settings-section">
                <span class="section-label">方向 (orientation)</span>
                <div class="radio-group horizontal">
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="yunwu_sora2_orientation"
                      value="portrait"
                    />
                    <span class="radio-label">portrait</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="yunwu_sora2_orientation"
                      value="landscape"
                    />
                    <span class="radio-label">landscape</span>
                  </label>
                </div>
              </div>
              <div class="settings-section">
                <span class="section-label">时长 (duration)</span>
                <div class="radio-group horizontal">
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="yunwu_sora2_duration"
                      value="10"
                    />
                    <span class="radio-label">10秒</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="yunwu_sora2_duration"
                      value="15"
                    />
                    <span class="radio-label">15秒</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- 小扳手 Sora2 配置 -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">XBS Sora2 配置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">模型</span>
                <select v-model="xiaobanshou_sora2_model">
                  <option value="sora-2">sora-2</option>
                  <option value="sora-2-landscape-10s">sora-2-landscape-10s</option>
                  <option value="sora-2-landscape-15s">sora-2-landscape-15s</option>
                  <option value="sora-2-portrait-10s">sora-2-portrait-10s</option>
                  <option value="sora-2-portrait-15s">sora-2-portrait-15s</option>
                  <option value="sora-2-pro">sora-2-pro</option>
                  <option value="sora-2-pro-landscape-25s">sora-2-pro-landscape-25s</option>
                  <option value="sora-2-pro-landscape-hd-10s">sora-2-pro-landscape-hd-10s</option>
                  <option value="sora-2-pro-landscape-hd-15s">sora-2-pro-landscape-hd-15s</option>
                  <option value="sora-2-pro-portrait-25s">sora-2-pro-portrait-25s</option>
                  <option value="sora-2-pro-portrait-hd-10s">sora-2-pro-portrait-hd-10s</option>
                  <option value="sora-2-pro-portrait-hd-15s">sora-2-pro-portrait-hd-15s</option>
                </select>
              </label>
            </div>
          </div>

          <!-- BDW Sora2 配置 -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">BDW Sora2 配置</h3>
            </div>
            <div class="card-body">
              <label class="field">
                <span class="field-label">模型</span>
                <select v-model="bandianwa_sora2_model">
                  <option value="sora-2-landscape-10s-guanzhuan">sora-2-landscape-10s-guanzhuan</option>
                  <option value="sora-2-landscape-15s-guanzhuan">sora-2-landscape-15s-guanzhuan</option>
                  <option value="sora-2-portrait-10s-guanzhuan">sora-2-portrait-10s-guanzhuan</option>
                  <option value="sora-2-portrait-15s-guanzhuan">sora-2-portrait-15s-guanzhuan</option>
                </select>
              </label>
            </div>
          </div>

          <!-- NanoBanana 配置 -->
          <div class="settings-card">
            <div class="card-header">
              <h3 class="card-title">NanoBanana 配置</h3>
            </div>
            <div class="card-body">
              <div class="settings-section">
                <span class="section-label">生图渠道</span>
                <div class="radio-group horizontal">
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="nanobanana_model"
                      value="yunwu"
                    />
                    <span class="radio-label">YW 渠道</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="nanobanana_model"
                      value="haotian"
                    />
                    <span class="radio-label">HT 渠道</span>
                  </label>
                </div>
              </div>
              <div class="settings-section">
                <span class="section-label">图片比例</span>
                <div class="radio-group horizontal">
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="nanobanana_ratio"
                      value="9:16"
                    />
                    <span class="radio-label">9:16</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="nanobanana_ratio"
                      value="16:9"
                    />
                    <span class="radio-label">16:9</span>
                  </label>
                </div>
              </div>
              <div class="settings-section">
                <span class="section-label">图片清晰度</span>
                <div class="radio-group horizontal">
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="nanobanana_quality"
                      value="1K"
                    />
                    <span class="radio-label">1K</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="nanobanana_quality"
                      value="2K"
                    />
                    <span class="radio-label">2K</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="nanobanana_quality"
                      value="4K"
                    />
                    <span class="radio-label">4K</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ========== 通用配置 ========== -->
        <!-- 下载配置 -->
        <div class="settings-card">
          <div class="card-header">
            <h3 class="card-title">下载配置</h3>
          </div>
          <div class="card-body">
            <label class="checkbox-item">
              <input
                type="checkbox"
                v-model="auto_download"
              />
              <span class="checkbox-label">自动下载生成结果</span>
            </label>
            <div class="field" style="margin-top: 16px;">
              <span class="field-label">下载路径</span>
              <div class="path-row">
                <input
                  v-model="download_path"
                  type="text"
                  placeholder="请选择下载目录"
                  readonly
                  class="path-input"
                />
                <button class="select-folder-btn" @click="selectDownloadFolder">选择文件夹</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 重试配置 -->
        <div class="settings-card">
          <div class="card-header">
            <h3 class="card-title">重试配置</h3>
          </div>
          <div class="card-body">
            <label class="checkbox-item">
              <input
                type="checkbox"
                v-model="auto_retry"
              />
              <span class="checkbox-label">失败后自动重试</span>
            </label>
            <label class="field" style="margin-top: 16px;">
              <span class="field-label">图片生成最大重试次数</span>
              <input
                v-model="image_max_retry"
                type="number"
                min="0"
                max="10"
                placeholder="3"
              />
            </label>
            <label class="field" style="margin-top: 16px;">
              <span class="field-label">视频生成最大重试次数</span>
              <input
                v-model="video_max_retry"
                type="number"
                min="0"
                max="10"
                placeholder="3"
              />
            </label>
          </div>
        </div>

        <!-- 线程池配置 -->
        <div class="settings-card">
          <div class="card-header">
            <h3 class="card-title">线程池配置</h3>
          </div>
          <div class="card-body">
            <label class="field">
              <span class="field-label">线程池大小（修改后需重启生效）</span>
              <input
                v-model="thread_pool_size"
                type="number"
                min="1"
                max="50"
                placeholder="10"
              />
            </label>
          </div>
        </div>

        <!-- 数据文件状态 -->
        <div class="settings-card full-width" v-if="dataStatus">
          <div class="card-header">
            <h3 class="card-title">数据文件</h3>
          </div>
          <div class="card-body">
            <div class="data-status-grid">
              <div class="data-status-item">
                <div class="data-status-icon db-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <ellipse cx="12" cy="5" rx="9" ry="3"/>
                    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
                    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
                  </svg>
                </div>
                <div class="data-status-info">
                  <span class="data-status-label">数据库文件</span>
                  <span class="data-status-value">{{ formatFileSize(dataStatus.db_size) }}</span>
                  <span class="data-status-path" :title="dataStatus.db_path">{{ dataStatus.db_path }}</span>
                </div>
              </div>
              <div class="data-status-item">
                <div class="data-status-icon log-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                  </svg>
                </div>
                <div class="data-status-info">
                  <span class="data-status-label">日志文件</span>
                  <span class="data-status-value">{{ dataStatus.log_files }} 个文件，{{ formatFileSize(dataStatus.log_total_size) }}</span>
                  <span class="data-status-path" :title="dataStatus.logs_dir">{{ dataStatus.logs_dir }}</span>
                </div>
              </div>
            </div>
            <div style="margin-top: 20px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <button class="open-dir-btn" @click="openRootDirectory">
                <svg class="open-dir-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
                <span>打开根目录</span>
              </button>
              <button class="open-dir-btn clean-log-btn" @click="cleanLogs" :disabled="cleaningLogs || (dataStatus && dataStatus.log_files <= 1)">
                <svg class="open-dir-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
                <span>{{ cleaningLogs ? '清理中...' : '清理日志' }}</span>
              </button>
              <span class="data-status-path" :title="dataStatus.base_dir">{{ dataStatus.base_dir }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 悬浮保存按钮 -->
    <button class="floating-save-btn" @click="saveSettings">
      <svg class="floating-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
        <polyline points="17 21 17 13 7 13 7 21"/>
        <polyline points="7 3 7 8 15 8"/>
      </svg>
      <span>保存设置</span>
    </button>
  </div>
</template>

<style scoped>
.page {
  position: relative;
  min-height: 100%;
}

.page-body {
  padding: 32px;
  padding-bottom: 80px;
}

.floating-save-btn {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border-radius: 14px;
  border: 1px solid rgba(91, 124, 255, 0.3);
  background: linear-gradient(135deg, #3b5bff, #7b5bff);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(59, 91, 255, 0.35), 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.floating-save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(59, 91, 255, 0.45), 0 4px 12px rgba(0, 0, 0, 0.3);
}

.floating-save-btn:active {
  transform: translateY(0);
}

.floating-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.full-width {
  grid-column: 1 / -1;
}

.settings-card {
  background: rgba(16, 20, 28, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #e6e9f2;
}

.card-body {
  padding: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  color: rgba(230, 233, 242, 0.6);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-group.horizontal {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 16px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

select {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(8, 11, 18, 0.8);
  color: #f5f7ff;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='rgba(230,233,242,0.4)' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

select:focus {
  border-color: rgba(91, 124, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(91, 124, 255, 0.15);
}

select option {
  background: #14182a;
  color: #f5f7ff;
}

.settings-section + .settings-section {
  margin-top: 20px;
}

.section-label {
  font-size: 13px;
  color: rgba(230, 233, 242, 0.6);
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.radio-item input[type="radio"] {
  width: 18px;
  height: 18px;
  margin: 0;
  accent-color: #5b7cff;
  cursor: pointer;
}

.radio-label {
  font-size: 14px;
  color: rgba(230, 233, 242, 0.85);
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin: 0;
  accent-color: #5b7cff;
  cursor: pointer;
}

.checkbox-label {
  font-size: 14px;
  color: rgba(230, 233, 242, 0.85);
}

.path-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.path-input {
  flex: 1;
  cursor: default;
  color: rgba(230, 233, 242, 0.6) !important;
}

.select-folder-btn {
  flex-shrink: 0;
  padding: 10px 18px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(230, 233, 242, 0.8);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.select-folder-btn:hover {
  background: rgba(91, 124, 255, 0.12);
  border-color: rgba(91, 124, 255, 0.3);
  color: #8ba3ff;
}


/* 数据文件状态 */
.data-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.data-status-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 10px;
  background: rgba(8, 11, 18, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.data-status-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.data-status-icon svg {
  width: 20px;
  height: 20px;
}

.db-icon {
  background: rgba(91, 124, 255, 0.12);
  color: #8ba3ff;
}

.log-icon {
  background: rgba(52, 199, 89, 0.12);
  color: #34c759;
}

.data-status-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.data-status-label {
  font-size: 13px;
  font-weight: 600;
  color: rgba(230, 233, 242, 0.85);
}

.data-status-value {
  font-size: 13px;
  color: rgba(230, 233, 242, 0.6);
}

.data-status-path {
  font-size: 11px;
  color: rgba(230, 233, 242, 0.3);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.open-dir-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(230, 233, 242, 0.8);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.open-dir-btn:hover {
  background: rgba(91, 124, 255, 0.12);
  border-color: rgba(91, 124, 255, 0.3);
  color: #8ba3ff;
}

.open-dir-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.open-dir-btn:disabled:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(230, 233, 242, 0.8);
}

.clean-log-btn {
  border-color: rgba(255, 69, 58, 0.25);
}

.clean-log-btn:hover:not(:disabled) {
  background: rgba(255, 69, 58, 0.12);
  border-color: rgba(255, 69, 58, 0.4);
  color: #ff453a;
}

.open-dir-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}
</style>
