<template>
 
  <div class="plan-chat-container">
    <!-- 目的地补全确认弹窗 -->
    <div v-if="destConfirm.visible" class="modal-backdrop">
      <div class="modal">
        <div class="modal-header">确认目的地</div>
        <div class="modal-body">
          <div class="modal-row"><strong>原始输入：</strong><span>{{ destConfirm.raw }}</span></div>
          <div class="modal-row"><strong>请选择标准名称：</strong></div>
          <div class="modal-options">
            <label class="option" v-for="opt in [destConfirm.suggestion, ...destConfirm.alternatives]" :key="opt">
              <input type="radio" name="destOpt" :value="opt" v-model="destConfirm.selected" />
              <span>{{ opt }}</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn confirm" @click="destConfirmConfirm">确认使用</button>
        </div>
      </div>
    </div>
    <!-- 可收起的侧边栏 -->
    <div class="collapsible-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <!-- 收起/展开按钮 -->
      <button class="toggle-btn" @click="toggleSidebar">
        <span class="toggle-icon">{{ sidebarCollapsed ? '☰' : '✕' }}</span>
      </button>
      
      <!-- 侧边栏内容 -->
      <div class="sidebar-content" v-show="!sidebarCollapsed">
        <!-- 头部标题 -->
        <div class="sidebar-header">
          <h1 class="app-title">CHAT A.I+</h1>
        </div>
        
        <!-- 新建聊天按钮 -->
        <div class="new-chat-section">
          <button class="new-chat-btn" @click="startNewChat">
            <span class="plus-icon">+</span>
            <span>New chat</span>
          </button>
          <button class="search-icon-btn">
            <span class="search-icon">🔍</span>
          </button>
        </div>
        
        <!-- 对话历史 -->
        <div class="conversation-history">
          <div class="history-header">
            <h3>Your conversations</h3>
            <button class="clear-all-btn" @click="clearAllConversations">Clear All</button>
          </div>
          
          <div class="conversation-list">
            <div 
              v-for="conversation in conversationHistory" 
              :key="conversation.id"
              :class="['conversation-item', { 'active': conversation.id === currentConversationId }]"
              @click="selectConversation(conversation.id)"
            >
              <span class="conversation-title">{{ conversation.title }}</span>
              <div class="conversation-actions" v-if="conversation.id === currentConversationId">
                <button class="action-btn">🗑️</button>
                <button class="action-btn">✏️</button>
                <button class="action-btn">⋯</button>
              </div>
            </div>
          </div>
          
          <!-- 最近7天 -->
          <div class="time-separator">Last 7 Days</div>
          
          <div class="conversation-list">
            <div 
              v-for="conversation in recentConversations" 
              :key="conversation.id"
              :class="['conversation-item', { 'active': conversation.id === currentConversationId }]"
              @click="selectConversation(conversation.id)"
            >
              <span class="conversation-title">{{ conversation.title }}</span>
            </div>
          </div>
        </div>
        
        <!-- 底部设置和用户信息 -->
        <div class="sidebar-footer">
          <button class="settings-btn">
            <span class="settings-icon">⚙️</span>
            <span>Settings</span>
          </button>
          
          <div class="user-profile">
            <div class="user-avatar">
              <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='16' fill='%234ade80'/%3E%3Ctext x='16' y='20' text-anchor='middle' fill='white' font-size='16'%3E👤%3C/text%3E%3C/svg%3E" alt="Avatar" />
            </div>
            <span class="user-name">Andrew Neilson</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 左侧面板 - 40%  -->
    <div class="left-panel">
      <!-- 聊天消息区域 -->
      <div class="chat-messages" ref="chatMessages">
        <div 
          v-for="(message, idx) in messages" 
          :key="message.id"
          :class="['message', message.type]"
        >
          <div class="message-content">
            <div v-if="message.type === 'ai'" class="message-header">
              <span class="ai-label">CHAT A.I+</span>
            </div>
            <div class="message-text">{{ message.text }}</div>
            <div v-if="message.type === 'ai'" class="message-actions">
              <button class="regenerate-btn" @click="regenerate(idx)">Regenerate</button>
            </div>
          </div>
        </div>
        
        <div v-if="isTyping" class="message ai typing">
          <div class="message-content">
            <div class="message-header">
              <span class="ai-label">CHAT A.I+</span>
            </div>
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-container">
          <input 
            type="text" 
            v-model="userInput" 
            placeholder="What's in your mind?..."
            @keydown.enter.prevent="sendMessage"
            class="message-input"
          />
          <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim()">
            <span class="send-icon">✈️</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 右侧面板 - 60% (动态地图) -->
    <div class="right-panel">
      <div class="map-container">
        <div class="map-header">
          <h2>旅行地图</h2>
          <div class="map-controls">
            <button class="control-btn" @click="toggleMapType">
              <span class="control-icon">🗺️</span>
              {{ mapType === 'satellite' ? '卫星' : '标准' }}
            </button>
            
            <!-- 起点输入（左侧） -->
            <input 
              class="control-input" 
              v-model="startKeyword" 
              placeholder="请输入起点（所在位置）" />
            
            <!-- 目的地输入（右侧） -->
            <input 
              class="control-input" 
              v-model="searchData.destination" 
              placeholder="请输入目的地（例如：外滩）" />
            <button class="control-btn" @click="planRoute" :disabled="!startKeyword || !searchData.destination">
              <span class="control-icon">🧭</span>
              路线规划
            </button>
            <button class="control-btn" @click="openInAmap">
              <span class="control-icon">↗️</span>
              高德中打开
            </button>
          </div>
        </div>
        
        <div class="map-content">
          <!-- 高德地图容器 -->
          <div id="amap-container" class="amap-container">
            <div v-if="isRouteLoading" class="route-loading-mask">
              <div class="route-loading-text">{{ routeLoadingMsg || '正在加载...' }}</div>
            </div>
          </div>
          
          <!-- 地图信息面板 -->
          <div class="map-info">
            <div class="info-card">
              <div class="card-header" @click="infoCollapsed = !infoCollapsed">
                <h3>目的地信息</h3>
                <button type="button" class="card-toggle">{{ infoCollapsed ? '▼' : '▲' }}</button>
              </div>
              <div class="card-body" v-show="!infoCollapsed">
                <div class="info-item">
                  <span class="info-label">地点：</span>
                  <span class="info-value">{{ searchData.destination || '未选择' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">出发日期：</span>
                  <span class="info-value">{{ searchData.startDate || '未选择' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">返回日期：</span>
                  <span class="info-value">{{ searchData.endDate || '未选择' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">人数：</span>
                  <span class="info-value">{{ searchData.people || '未选择' }}</span>
                </div>
              </div>
            </div>
            
            <div class="weather-card" v-if="weatherInfo">
              <h3>天气信息</h3>
              <div class="weather-content">
                <div class="weather-icon">{{ weatherInfo.icon }}</div>
                <div class="weather-details">
                  <div class="temperature">{{ weatherInfo.temperature }}°C</div>
                  <div class="condition">{{ weatherInfo.condition }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 搜索数据
const searchData = ref({
  destination: '',
  startDate: '',
  endDate: '',
  people: ''
})

// 聊天相关数据
const userInput = ref('')
const messages = ref([])
const isTyping = ref(false)
const chatMessages = ref(null)
// 会话ID（由后端返回并在后续请求中复用）
const sessionId = ref(null)

// 侧边栏控制
const sidebarCollapsed = ref(false)

// 地图相关数据
const mapType = ref('standard')
const weatherInfo = ref(null)
let map = null // 高德地图实例
let satelliteLayer = null // 卫星图层
let roadNetLayer = null // 路网图层
// 路线规划相关
const routeSummary = ref(null)
let routePolyline = null
let userMarker = null
let destMarker = null
// 起点输入/定位来源
const startKeyword = ref('')
// 路线规划加载状态
const isRouteLoading = ref(false)
const routeLoadingMsg = ref('')
// 最近一次成功规划用到的起终点坐标
const lastStart = ref(null) // {lng, lat, name}
const lastEnd = ref(null)   // {lng, lat, name}
// 终点附近 POI 与次级路线
let foodMarkers = []
let hotelMarkers = []
let poiDriving = null
let poiInfoWindow = null
let poiHoverInfoWindow = null
// 主路线驾车实例（用于清除旧路线）
let mainDriving = null
// 已移除定位来源状态

// 目的地补全确认弹窗状态
const destConfirm = ref({
  visible: false,
  raw: '',
  suggestion: '',
  alternatives: [],
  selected: ''
})

// 弹窗Promise的resolve持有者与一次性自动规划标记
let destConfirmResolve = null
let plannedByConfirmOnce = false

// 本地仅确认一次的开关与记录
const destConfirmedOnce = ref(false)
const confirmedDestValue = ref('')

// 对话历史相关数据
const currentConversationId = ref(1)
const conversationHistory = ref([
  { id: 1, title: 'Create Chatbot GPT...', active: true },
  { id: 2, title: 'What Is UI UX Design?' },
  { id: 3, title: 'Create POS System' },
  { id: 4, title: 'What Is UX Audit?' },
  { id: 5, title: 'Apply To Leave For Emergency' },
  { id: 6, title: 'Create Html Game Environment...' },
  { id: 7, title: 'How Chat GPT Work?' }
])

const recentConversations = ref([
  { id: 8, title: 'Crypto Lending App Name' },
  { id: 9, title: 'Operator Grammar Types' },
  { id: 10, title: 'Min States For Binary DFA' }
])

// 目的地信息折叠状态
const infoCollapsed = ref(true)

// 模拟AI回复
const generateAIResponse = (userMessage) => {
  const responses = [
    "我来为您推荐几个不错的景点...",
    "根据您的需求，我建议您考虑以下行程安排...",
    "这个地方的美食很有特色，我推荐您尝试...",
    "考虑到您的预算和时间，我为您制定了以下方案...",
    "这个季节去那里天气很好，很适合户外活动..."
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim()) return

  const userMessage = {
    id: Date.now(),
    type: 'user',
    text: userInput.value,
    time: new Date().toLocaleTimeString()
  }

  messages.value.push(userMessage)
  const messageToSend = userInput.value
  userInput.value = ''

  // 显示AI正在输入
  isTyping.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 调用后端API
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId.value,
        message: messageToSend
      })
    })

    if (!response.ok) {
      throw new Error('Network response was not ok')
    }

    const data = await response.json()

  // 更新session_id
  sessionId.value = data.session_id
  try { localStorage.setItem('sessionId', sessionId.value) } catch (e) {}

    // 智能同步目的地、日期、人数到地图输入框（仅覆盖空值或与上次同步一致时，避免覆盖用户手动输入）
    if (data.travel_info) {
      const ti = data.travel_info
      let extractedDest = ti.destination || ''
      // 若有目的地，先走Kimi补全确认流程（仅确认一次：后续请求不再弹窗）
      if (extractedDest && !destConfirmedOnce.value) {
        try {
          const confirmed = await normalizeAndConfirmDestination(extractedDest)
          if (confirmed) {
            searchData.value.destination = confirmed
            localStorage.setItem('searchDestination', confirmed)
            destConfirmedOnce.value = true
            confirmedDestValue.value = confirmed
          } else {
            // 用户取消或未确认：不写入目的地
            console.log('[normalize] 用户未确认目的地，保持为空')
          }
        } catch (e) {
          console.warn('[normalize] 目的地补全失败，使用原值', extractedDest, e)
          // 兜底：使用原值
          searchData.value.destination = extractedDest
          localStorage.setItem('searchDestination', extractedDest)
          destConfirmedOnce.value = true
          confirmedDestValue.value = extractedDest
        }
      }
      // 出发日期
      if (ti.start_date && (!searchData.value.startDate || searchData.value.startDate === localStorage.getItem('searchStartDate'))) {
        searchData.value.startDate = ti.start_date
        localStorage.setItem('searchStartDate', ti.start_date)
      }
      // 结束日期
      if (ti.end_date && (!searchData.value.endDate || searchData.value.endDate === localStorage.getItem('searchEndDate'))) {
        searchData.value.endDate = ti.end_date
        localStorage.setItem('searchEndDate', ti.end_date)
      }
      // 人数
      if (ti.num_people && (!searchData.value.people || searchData.value.people === localStorage.getItem('searchPeople'))) {
        searchData.value.people = String(ti.num_people)
        localStorage.setItem('searchPeople', String(ti.num_people))
      }
      // 对话结束后，若起点和目的地都存在，立即自动路径规划
      nextTick(() => {
        if (startKeyword.value && searchData.value.destination) {
          // 若已在确认弹窗中写入过目的地，避免重复触发
          if (plannedByConfirmOnce) {
            plannedByConfirmOnce = false
            return
          }
          console.log('[autoPlan] sendMessage后立即自动触发 planRoute', startKeyword.value, searchData.value.destination)
          planRoute()
        }
      })
    }

    isTyping.value = false

    const aiMessage = {
      id: Date.now() + 1,
      type: 'ai',
      text: data.response,
      time: new Date().toLocaleTimeString()
    }

    messages.value.push(aiMessage)

    await nextTick()
    scrollToBottom()

  } catch (error) {
    console.error('Error sending message:', error)
    isTyping.value = false

    const errorMessage = {
      id: Date.now() + 1,
      type: 'ai',
      text: '抱歉，发送消息时出现错误，请稍后再试。',
      time: new Date().toLocaleTimeString()
    }

    messages.value.push(errorMessage)

    await nextTick()
    scrollToBottom()
  }
}

// 重新生成指定 AI 消息的回复（尝试给出不同回答）
const regenerate = async (aiIndex) => {
  try {
    // 找到对应的 AI 消息前最近的用户消息文本
    let i = aiIndex - 1
    let userMsg = null
    while (i >= 0) {
      if (messages.value[i].type === 'user') {
        userMsg = messages.value[i].text
        break
      }
      i--
    }
    if (!userMsg) {
      console.warn('[regenerate] 未找到对应的用户消息')
      return
    }

    isTyping.value = true
    // 在原消息后附加提示，要求模型给出不同的回答
    const regenPrompt = userMsg + '\n请基于上面的用户问题，给出一个不同于之前回答的替代回复（换一种措辞或思路），不要重复原有回答。'

    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId.value, message: regenPrompt })
    })

    if (!response.ok) {
      throw new Error('Network response was not ok')
    }

    const data = await response.json()
    // 替换指定 AI 消息的文本为新的回复（不改变会话的其它 UI 状态）
    if (data && data.response) {
      // 确保索引仍然有效
      if (messages.value[aiIndex] && messages.value[aiIndex].type === 'ai') {
        messages.value[aiIndex].text = data.response
      }
    }
    isTyping.value = false
  } catch (e) {
    console.error('[regenerate] error', e)
    isTyping.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatMessages.value) {
    chatMessages.value.scrollTop = chatMessages.value.scrollHeight
  }
}

// 返回搜索页面
const goBack = () => {
  router.push('/')
}

// 开始新聊天
const startNewChat = () => {
  currentConversationId.value = Date.now()
  messages.value = []
  userInput.value = ''
}

// 选择对话
const selectConversation = (conversationId) => {
  currentConversationId.value = conversationId
  // 这里可以加载对应对话的消息
}

// 清除所有对话
const clearAllConversations = () => {
  conversationHistory.value = []
  recentConversations.value = []
  messages.value = []
}

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 加载高德地图 SDK
const loadAmapScript = () => {
  return new Promise((resolve) => {
    if (window.AMap && window.AMap.Map) return resolve(window.AMap)
    const key = import.meta.env.VITE_AMAP_KEY
    const secret = import.meta.env.VITE_AMAP_SECRET
    window._AMapSecurityConfig = { securityJsCode: secret }
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${key}`
    script.type = 'text/javascript'
    script.onload = () => resolve(window.AMap)
    document.head.appendChild(script)
  })
}

// 初始化地图
const initMap = async () => {
  const AMap = await loadAmapScript()
  map = new AMap.Map('amap-container', {
    viewMode: '3D',
    zoom: 11,
    center: [121.4737, 31.2304]
  })
  satelliteLayer = new AMap.TileLayer.Satellite()
  roadNetLayer = new AMap.TileLayer.RoadNet()
}

// 切换地图类型
const toggleMapType = () => {
  mapType.value = mapType.value === 'standard' ? 'satellite' : 'standard'
  
  if (!map) return
  
  if (mapType.value === 'satellite') {
    // 切换到卫星图
    map.add(satelliteLayer)
    map.add(roadNetLayer)
  } else {
    // 切换回标准图
    map.remove(satelliteLayer)
    map.remove(roadNetLayer)
  }
}

// 调用后端：Kimi 补全目的地
const normalizeDestination = async (rawName, cityHint = '') => {
  const resp = await fetch('http://localhost:8000/api/normalize_destination', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: rawName, city_hint: cityHint })
  })
  if (!resp.ok) throw new Error('normalize api failed')
  const data = await resp.json()
  return data // { raw, suggestion, alternatives }
}

// 打开目的地确认弹窗，返回最终确认的名称或空
const normalizeAndConfirmDestination = async (rawName) => {
  try {
    const cityHint = '' // 可选：根据起点或已知上下文提供
    const res = await normalizeDestination(rawName, cityHint)
    const options = [res.suggestion, ...(res.alternatives || [])].filter(Boolean)
    if (!options.length) return rawName
    // 初始化弹窗状态
    destConfirm.value.visible = true
    destConfirm.value.raw = rawName
    destConfirm.value.suggestion = res.suggestion
    destConfirm.value.alternatives = res.alternatives || []
    destConfirm.value.selected = res.suggestion
    // 返回一个 Promise，等待用户确认/取消
    return await new Promise((resolve) => {
      destConfirmResolve = resolve
    })
  } catch (e) {
    console.warn('[normalize] 调用补全失败', e)
    return rawName
  }
}

const closeConfirm = () => {
  destConfirm.value.visible = false
}

const destConfirmConfirm = () => {
  const v = destConfirm.value.selected || destConfirm.value.suggestion || destConfirm.value.raw
  // 立即写入地图输入框
  if (v) {
    searchData.value.destination = v
    try { localStorage.setItem('searchDestination', v) } catch (e) {}
    // 将确认结果通知后端，避免大模型重复确认
    try {
      if (sessionId.value) {
        fetch(`http://localhost:8000/api/session/${sessionId.value}/confirm_destination`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ destination: v })
        }).catch(() => {})
      }
    } catch (e) {}
  }
  plannedByConfirmOnce = true
  closeConfirm()
  if (typeof destConfirmResolve === 'function') {
    destConfirmResolve(v)
  }
  destConfirmResolve = null
}

// 取消按钮已移除：若需要恢复“更换补全方式”，可重新添加对应按钮并调用此逻辑


// （保留此实现）关键字地理编码，带日志与 SDK 加载检查 + 超时
const withTimeout = (p, ms) => {
  let t
  const timeout = new Promise((_, reject) => {
    t = setTimeout(() => reject(new Error('timeout')), ms)
  })
  return Promise.race([p.finally(() => clearTimeout(t)), timeout])
}

// 清理地图上现有路线与叠加（在重新规划或用户修改起终点时调用）
const clearAllRouteOverlays = () => {
  try {
    if (map && typeof map.clearMap === 'function') {
      map.clearMap()
    }
  } catch (e) { /* ignore */ }
  // 关闭信息窗
  try { poiInfoWindow && poiInfoWindow.close() } catch (e) {}
  try { poiHoverInfoWindow && poiHoverInfoWindow.close() } catch (e) {}
  poiInfoWindow = null
  poiHoverInfoWindow = null
  // 清空 POI 驾车与标记缓存
  try { poiDriving && typeof poiDriving.clear === 'function' && poiDriving.clear() } catch (e) {}
  poiDriving = null
  foodMarkers = []
  hotelMarkers = []
  // 清空主线路结果
  try { mainDriving && typeof mainDriving.clear === 'function' && mainDriving.clear() } catch (e) {}
  // 置空主标记引用（已从地图移除）
  userMarker = null
  destMarker = null
}

const geocode = (kw) => {
  console.log('[geocode] Geocoding:', kw)
  const task = new Promise((resolve, reject) => {
    if (!kw) return reject(new Error('地址为空'))
    if (!window.AMap) {
      console.error('[geocode] window.AMap 未加载')
      return reject(new Error('地图SDK未加载'))
    }
    window.AMap.plugin('AMap.Geocoder', () => {
      const geocoder = new window.AMap.Geocoder()
      geocoder.getLocation(kw, (status, result) => {
        if (status === 'complete' && result && result.geocodes && result.geocodes.length) {
          const loc = result.geocodes[0].location
          console.log('[geocode] 解析成功:', kw, loc)
          resolve([loc.lng, loc.lat])
        } else {
          console.error('[geocode] 解析失败:', kw, result)
          reject(new Error('地理编码失败'))
        }
      })
    })
  })
  return withTimeout(task, 8000)
}

// 规划驾车路线并渲染到地图（统一实现，含 loading 与日志）
const planRoute = async () => {
  console.log('[planRoute] called, startKeyword:', startKeyword.value, 'destination:', searchData.value.destination)
  isRouteLoading.value = true
  routeLoadingMsg.value = ''
  try {
    // 清空上一次的路线与叠加物
    clearAllRouteOverlays()

    const [startLng, startLat] = await geocode(startKeyword.value)
    const destName = searchData.value.destination
    if (!destName) {
      isRouteLoading.value = false
      routeLoadingMsg.value = ''
      return alert('目的地为空')
    }
    const [endLng, endLat] = await geocode(destName)
    if (userMarker) try { map && map.remove(userMarker) } catch(e) {}
    if (destMarker) try { map && map.remove(destMarker) } catch(e) {}
    userMarker = new AMap.Marker({ position: [startLng, startLat] })
    destMarker = new AMap.Marker({ position: [endLng, endLat] })
    map.add(userMarker)
    map.add(destMarker)
    // 缓存坐标
    lastStart.value = { lng: startLng, lat: startLat, name: startKeyword.value || '起点' }
    lastEnd.value = { lng: endLng, lat: endLat, name: destName || '终点' }
    AMap.plugin('AMap.Driving', () => {
      const panel = document.getElementById('driving-panel')
      const opts = panel ? { map, panel: 'driving-panel' } : { map }
      if (panel) panel.innerHTML = ''
      // 清理上一次主线路并重新创建实例
      try { mainDriving && typeof mainDriving.clear === 'function' && mainDriving.clear() } catch (e) {}
      mainDriving = new AMap.Driving(opts)
      const drivingSearch = new Promise((resolve) => {
        mainDriving.search([startLng, startLat], [endLng, endLat], (status, result) => {
          resolve({ status, result })
        })
      })
      withTimeout(drivingSearch, 10000).then(({ status, result }) => {
        isRouteLoading.value = false
        routeLoadingMsg.value = ''
        if (status === 'complete' && result && result.routes && result.routes.length) {
          map.setFitView()
          // 加载终点附近POI（美食/酒店）
          loadNearbyPOIs()
        } else {
          alert('无路线')
        }
      }).catch(() => {
        isRouteLoading.value = false
        routeLoadingMsg.value = ''
        alert('超时')
      })
    })
  } catch (e) {
    isRouteLoading.value = false
    routeLoadingMsg.value = ''
    alert('错误')
  }
}

// 当用户修改起点或目的地时，立即清理现有路线，避免旧路线残留
watch(() => searchData.value.destination, (val, oldVal) => {
  if (val !== oldVal) {
    clearAllRouteOverlays()
    // 使下次 openInAmap 重新计算终点
    lastEnd.value = null
  }
})

watch(() => startKeyword.value, (val, oldVal) => {
  if (val !== oldVal) {
    clearAllRouteOverlays()
    // 使下次 openInAmap 重新计算起点
    lastStart.value = null
  }
})

// 防抖定时器 + 自动路径规划：监听起点和目的地
let autoPlanTimeout = null
watch(
  [() => startKeyword.value, () => searchData.value.destination],
  ([start, dest], [oldStart, oldDest]) => {
    console.log('[watch] startKeyword:', start, 'destination:', dest, '| old:', oldStart, oldDest)
    if (start && dest && (start !== oldStart || dest !== oldDest)) {
      if (autoPlanTimeout) clearTimeout(autoPlanTimeout)
      autoPlanTimeout = setTimeout(() => {
        console.log('[autoPlan] 自动触发 planRoute', start, dest)
        planRoute()
      }, 350)
    }
  }
)

// 在高德地图中打开完整路线
const openInAmap = async () => {
  try {
    const destName = searchData.value.destination
    if (!destName) return alert('目的地为空')
    let s = lastStart.value
    let e = lastEnd.value
    if (!s) {
      const [lng, lat] = await geocode(startKeyword.value)
      s = { lng, lat, name: startKeyword.value || '起点' }
    }
    if (!e) {
      const [lng, lat] = await geocode(destName)
      e = { lng, lat, name: destName || '终点' }
    }
    const from = `${s.lng},${s.lat},${encodeURIComponent(s.name)}`
    const to = `${e.lng},${e.lat},${encodeURIComponent(e.name)}`
    const url = `https://uri.amap.com/navigation?from=${from}&to=${to}&mode=car&policy=1&coordinate=gaode&callnative=0`
    window.open(url, '_blank')
  } catch (e) {
    alert('错误')
  }
}

// 加载终点附近的美食与酒店
const loadNearbyPOIs = () => {
  if (!lastEnd.value || !map) return
  const center = [lastEnd.value.lng, lastEnd.value.lat]
  // 清理旧标记
  clearPoiMarkers()
  AMap.plugin('AMap.PlaceSearch', () => {
    const common = { pageSize: 12, pageIndex: 1 }
    const psFood = new AMap.PlaceSearch({ ...common })
    const psHotel = new AMap.PlaceSearch({ ...common })
    psFood.searchNearBy('美食', center, 2000, (status, result) => {
      if (status === 'complete' && result && result.poiList && result.poiList.pois) {
        addPoiMarkers(result.poiList.pois, 'food')
      }
    })
    psHotel.searchNearBy('酒店', center, 2000, (status, result) => {
      if (status === 'complete' && result && result.poiList && result.poiList.pois) {
        addPoiMarkers(result.poiList.pois, 'hotel')
      }
    })
  })
}

const clearPoiMarkers = () => {
  if (foodMarkers.length) { map.remove(foodMarkers); foodMarkers = [] }
  if (hotelMarkers.length) { map.remove(hotelMarkers); hotelMarkers = [] }
}

const addPoiMarkers = (pois, type) => {
  pois.forEach(poi => {
    if (!poi.location) return
    const pos = [poi.location.lng, poi.location.lat]
    const el = document.createElement('div')
    el.className = `poi-marker ${type}`
    el.innerText = type === 'food' ? '🍜' : '🏨'
    const marker = new AMap.Marker({ position: pos, content: el, anchor: 'bottom-center' })
    marker.setExtData({ type, name: poi.name || '', address: poi.address || '', position: pos })
    // 悬浮显示名称
    marker.on('mouseover', () => {
      const data = marker.getExtData() || {}
      if (!poiHoverInfoWindow) poiHoverInfoWindow = new AMap.InfoWindow({ isCustom: false, offset: new AMap.Pixel(0, -28) })
      poiHoverInfoWindow.setContent(`<div class="poi-hover">${data.name || ''}</div>`)
      poiHoverInfoWindow.open(map, pos)
    })
    marker.on('mouseout', () => {
      if (poiHoverInfoWindow) poiHoverInfoWindow.close()
    })
    // 点击显示距离/时长并绘制路线
    marker.on('click', () => onPoiClick(marker))
    map.add(marker)
    if (type === 'food') foodMarkers.push(marker); else hotelMarkers.push(marker)
  })
}

const onPoiClick = (marker) => {
  if (!lastEnd.value) return
  // 避免与悬浮提示重叠
  if (poiHoverInfoWindow) poiHoverInfoWindow.close()
  const data = marker.getExtData() || {}
  const start = [lastEnd.value.lng, lastEnd.value.lat]
  const end = data.position
  if (!poiDriving) {
    poiDriving = new AMap.Driving({ map, hideMarkers: true, showTraffic: false, polylineOptions: { strokeColor: '#1e90ff', strokeWeight: 6, strokeOpacity: 0.8 } })
  }
  poiDriving.search(start, end, (status, result) => {
    if (status === 'complete' && result && result.routes && result.routes.length) {
      const r = result.routes[0]
      const distKm = (r.distance / 1000).toFixed(1)
      const mins = Math.round(r.time / 60)
      if (!poiInfoWindow) poiInfoWindow = new AMap.InfoWindow({ offset: new AMap.Pixel(0, -28) })
  poiInfoWindow.setContent(`<div class="poi-info"><div>${data.name || ''}</div><div>${distKm} km · ${mins} 分钟</div></div>`)
      poiInfoWindow.open(map, end)
    } else {
      // 最简提示
      alert('无路线')
    }
  })
}


// 组件挂载时获取搜索参数
onMounted(async () => {
  // 页面刷新时清除localStorage中的目的地、日期、人数信息（保留 sessionId 用于连续会话）
  localStorage.removeItem('searchDestination')
  localStorage.removeItem('searchStartDate')
  localStorage.removeItem('searchEndDate')
  localStorage.removeItem('searchPeople')

  // 恢复 sessionId（如存在）
  const savedSessionId = localStorage.getItem('sessionId')
  if (savedSessionId) {
    sessionId.value = savedSessionId
  }

  // 从URL参数获取搜索数据（不再从localStorage恢复）
  const urlParams = new URLSearchParams(window.location.search)
  searchData.value = {
    destination: urlParams.get('destination') || '',
    startDate: urlParams.get('startDate') || '',
    endDate: urlParams.get('endDate') || '',
    people: urlParams.get('people') || ''
  }

  // 设置起点关键词：优先使用 Home 页填写的“所在区域”
  const savedOrigin = urlParams.get('origin') || localStorage.getItem('searchOrigin')
  if (savedOrigin && typeof savedOrigin === 'string') {
    startKeyword.value = savedOrigin
  }

  // 确保高德地图SDK已加载
  await loadAmapScript()
  await nextTick()
  let city = '上海'
  window.AMap.plugin('AMap.Weather', function() {
    const weather = new window.AMap.Weather()
    weather.getLive(city, function(err, data) {
      if (!err && data && data.weather) {
        // 天气icon简单映射
        let icon = '☀️'
        if (data.weather.includes('雨')) icon = '🌧️'
        else if (data.weather.includes('雪')) icon = '❄️'
        else if (data.weather.includes('云')) icon = '⛅'
        else if (data.weather.includes('阴')) icon = '☁️'
        weatherInfo.value = {
          icon,
          temperature: data.temperature,
          condition: data.weather
        }
      } else {
        weatherInfo.value = { icon: '❓', temperature: '--', condition: '获取失败' }
      }
    })
  })

  // 添加欢迎消息
  const welcomeMessage = {
    id: Date.now(),
    type: 'ai',
    text: `您好！我是您的AI旅行助手。我看到您计划去${searchData.value.destination || '某地'}旅行，从${searchData.value.startDate || '开始日期'}到${searchData.value.endDate || '结束日期'}，共${searchData.value.people || '？'}人。有什么我可以帮助您的吗？`,
    time: new Date().toLocaleTimeString()
  }

  messages.value.push(welcomeMessage)

  await nextTick()
  scrollToBottom()

  // 确保 DOM 完全渲染后再初始化地图
  setTimeout(() => {
    initMap()
  }, 100)
})

// 组件卸载时清理地图
onUnmounted(() => {
  if (map) {
    map.destroy()
    map = null
  }
  if (routePolyline && map) { map.remove(routePolyline) }
  routePolyline = null
  if (userMarker && map) { map.remove(userMarker) }
  userMarker = null
  if (destMarker && map) { map.remove(destMarker) }
  destMarker = null
})
</script>

<style scoped>
.plan-chat-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  background: #f8f9fa;
  overflow: hidden;
}

/* 可收起的侧边栏 */
.collapsible-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 320px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  transition: transform 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.collapsible-sidebar.collapsed {
  transform: translateX(-100%);
}

/* 切换按钮 */
.toggle-btn {
  position: absolute;
  top: 1rem;
  right: -3rem;
  width: 2.5rem;
  height: 2.5rem;
  background: #4ade80;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 12px rgba(74, 222, 128, 0.3);
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: #22c55e;
  transform: scale(1.1);
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部标题 */
.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.app-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #1f2937;
  margin: 0;
  text-align: center;
}

/* 新建聊天按钮 */
.new-chat-section {
  padding: 1.5rem 1rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.new-chat-btn {
  flex: 1;
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.new-chat-btn:hover {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  transform: translateY(-1px);
}

.plus-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.search-icon-btn {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-icon-btn:hover {
  background: #e5e7eb;
}

/* 对话历史 */
.conversation-history {
  flex: 1;
  padding: 0 1rem;
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.history-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0;
}

.clear-all-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.75rem;
  cursor: pointer;
  text-decoration: underline;
}

.conversation-list {
  margin-bottom: 1.5rem;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.conversation-item:hover {
  background: #f3f4f6;
}

.conversation-item.active {
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: white;
}

.conversation-title {
  font-size: 0.875rem;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.conversation-item.active .conversation-actions {
  opacity: 1;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.time-separator {
  font-size: 0.75rem;
  color: #9ca3af;
  margin: 1rem 0 0.5rem 0;
  font-weight: 500;
}

/* 底部设置和用户信息 */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.settings-btn {
  width: 100%;
  background: none;
  border: none;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  color: #374151;
  transition: background-color 0.3s ease;
}

.settings-btn:hover {
  background: #f3f4f6;
}

.settings-icon {
  font-size: 1.1rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.user-profile:hover {
  background: #f3f4f6;
}

.user-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.user-name {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

/* 左侧面板 - 40% (聊天区域) */
.left-panel {
  width: 40%;
  margin-left: 320px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e5e7eb;
  transition: margin-left 0.3s ease;
}

.collapsible-sidebar.collapsed ~ .left-panel {
  margin-left: 0;
}

.chat-messages {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message {
  display: flex;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.ai {
  align-items: flex-start;
}

.message-content {
  max-width: 80%;
  background: #f3f4f6;
  padding: 1rem 1.5rem;
  border-radius: 18px;
  position: relative;
}

.message.user .message-content {
  background: #4ade80;
  color: white;
}

.message-header {
  margin-bottom: 0.5rem;
}

.ai-label {
  font-weight: 600;
  color: #4ade80;
  font-size: 0.875rem;
}

.message-text {
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.message-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.action-icon {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.action-icon:hover {
  background: rgba(0, 0, 0, 0.1);
}

.regenerate-btn {
  background: #4ade80;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.regenerate-btn:hover {
  background: #22c55e;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #9ca3af;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* 输入区域 */
.chat-input-area {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  background: #ffffff;
}

.input-container {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.message-input:focus {
  border-color: #4ade80;
}

.message-input::placeholder {
  color: #9ca3af;
}

.send-btn {
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  transform: translateY(-1px);
}

.send-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
}

.send-icon {
  font-size: 1.1rem;
}

/* 右侧面板 - 60% (地图区域) */
.right-panel {
  width: 60%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
}

.map-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.map-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.map-header h2 {
  color: #1f2937;
  font-size: 1.5rem;
  margin: 0;
}

.map-controls {
  display: flex;
  gap: 0.75rem;
}

.control-btn {
  background: #ffffff;
  border: 1px solid #d1d5db;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.control-btn:hover {
  background: #f3f4f6;
  border-color: #4ade80;
}

.control-icon {
  font-size: 1rem;
}

.map-content {
  flex: 1;
  display: flex;
  position: relative;
}

/* 高德地图容器 */
.amap-container {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 500px;
}

/* 地图信息面板 */
.map-info {
  width: 300px;
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
  padding: 1.5rem;
  overflow-y: auto;
}

.route-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1rem;
}
.route-card h3 {
  color: #1f2937;
  font-size: 1.1rem;
  margin: 0 0 1rem 0;
}
.route-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.driving-panel {
  margin-top: 1rem;
  max-height: 40vh;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.info-card, .weather-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.info-card h3, .weather-card h3 {
  color: #1f2937;
  font-size: 1rem;
  margin: 0 0 1rem 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.info-label {
  color: #6b7280;
  font-weight: 500;
}

.info-value {
  color: #1f2937;
  font-weight: 600;
}

.weather-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.weather-icon {
  font-size: 2rem;
}

.weather-details {
  flex: 1;
}

.temperature {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.condition {
  font-size: 0.875rem;
  color: #6b7280;
}
/* 卡片头部与折叠按钮 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.card-toggle {
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #374151;
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  font-size: 0.85rem;
  line-height: 1;
  transform: rotate(0deg);
  transition: transform 0.2s ease;
}

.card-body {
  margin-top: 0.5rem;
}

/* 方向箭头通过字符控制，无需旋转类 */

/* 响应式设计 */
@media (max-width: 768px) {
  .plan-chat-container {
    flex-direction: column;
  }
  
  .collapsible-sidebar {
    position: relative;
    width: 100%;
    height: auto;
    transform: none;
  }
  
  .collapsible-sidebar.collapsed {
    transform: none;
    height: 60px;
  }
  
  .collapsible-sidebar.collapsed .sidebar-content {
    display: none;
  }
  
  .toggle-btn {
    position: static;
    margin: 1rem;
    right: auto;
  }
  
  .left-panel,
  .right-panel {
    width: 100%;
    margin-left: 0;
  }
  
  .left-panel {
    height: 40vh;
    min-height: 300px;
  }
  
  .right-panel {
    height: 60vh;
  }
  
  .map-content {
    flex-direction: column;
  }
  
  .map-info {
    width: 100%;
    border-left: none;
    border-top: 1px solid #e5e7eb;
  }
  
  .chat-messages {
    padding: 1rem;
  }
  
  .chat-input-area {
    padding: 1rem;
  }
}
</style>

<style scoped>
.route-loading-mask {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background: rgba(255,255,255,0.7);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}
.route-loading-text {
  font-size: 1.2rem;
  color: #22c55e;
  background: #fff;
  padding: 1.5rem 2.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(34,197,94,0.08);
}
/* 目的地确认弹窗样式 */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal {
  background: #fff;
  border-radius: 12px;
  width: 520px;
  max-width: 90vw;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  overflow: hidden;
}
.modal-header {
  padding: 16px 20px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
}
.modal-body {
  padding: 16px 20px;
}
.modal-row {
  margin: 8px 0;
}
.modal-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}
.option {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 6px 8px;
  border-radius: 6px;
  background: #fafafa;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 12px 20px 16px;
  border-top: 1px solid #eee;
}
.btn {
  padding: 8px 14px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}
.btn.cancel {
  background: #f3f4f6;
}
.btn.confirm {
  background: #4ade80;
  color: #fff;
}
</style>

