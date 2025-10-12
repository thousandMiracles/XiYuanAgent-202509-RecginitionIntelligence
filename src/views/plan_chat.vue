<template>
  <div class="plan-chat-container">
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

    <!-- 左侧面板 - 40% (原来的右侧面板) -->
    <div class="left-panel">
      <!-- 聊天消息区域 -->
      <div class="chat-messages" ref="chatMessages">
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="['message', message.type]"
        >
          <div class="message-content">
            <div v-if="message.type === 'ai'" class="message-header">
              <span class="ai-label">CHAT A.I+</span>
            </div>
            <div class="message-text">{{ message.text }}</div>
            <div v-if="message.type === 'ai'" class="message-actions">
              <button class="action-icon">👍</button>
              <button class="action-icon">👎</button>
              <button class="action-icon">📋</button>
              <button class="action-icon">⋯</button>
              <button class="regenerate-btn">Regenerate</button>
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
            <button class="control-btn" @click="centerMap">
              <span class="control-icon">📍</span>
              定位
            </button>
          </div>
        </div>
        
        <div class="map-content">
          <!-- 模拟地图区域 -->
          <div class="mock-map" :class="mapType">
            <div class="map-overlay">
              <div class="destination-marker" v-if="searchData.destination">
                <div class="marker-icon">📍</div>
                <div class="marker-label">{{ searchData.destination }}</div>
              </div>
              
              <!-- 模拟路线 -->
              <div class="travel-route" v-if="searchData.destination">
                <div class="route-line"></div>
                <div class="route-points">
                  <div class="route-point start">起点</div>
                  <div class="route-point end">{{ searchData.destination }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 地图信息面板 -->
          <div class="map-info">
            <div class="info-card">
              <h3>目的地信息</h3>
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
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
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

// 侧边栏控制
const sidebarCollapsed = ref(false)

// 地图相关数据
const mapType = ref('standard')
const weatherInfo = ref(null)

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
  userInput.value = ''
  
  // 显示AI正在输入
  isTyping.value = true
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 模拟AI回复延迟
  setTimeout(() => {
    isTyping.value = false
    
    const aiMessage = {
      id: Date.now() + 1,
      type: 'ai',
      text: generateAIResponse(userMessage.text),
      time: new Date().toLocaleTimeString()
    }
    
    messages.value.push(aiMessage)
    
    nextTick(() => {
      scrollToBottom()
    })
  }, 1500)
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

// 切换地图类型
const toggleMapType = () => {
  mapType.value = mapType.value === 'standard' ? 'satellite' : 'standard'
}

// 定位地图
const centerMap = () => {
  // 模拟定位功能
  console.log('定位到当前位置')
}

// 模拟天气信息
const generateWeatherInfo = () => {
  const weatherData = [
    { icon: '☀️', temperature: '25', condition: '晴朗' },
    { icon: '⛅', temperature: '22', condition: '多云' },
    { icon: '🌧️', temperature: '18', condition: '小雨' },
    { icon: '❄️', temperature: '5', condition: '雪' }
  ]
  return weatherData[Math.floor(Math.random() * weatherData.length)]
}

// 组件挂载时获取搜索参数
onMounted(() => {
  // 从URL参数或localStorage获取搜索数据
  const urlParams = new URLSearchParams(window.location.search)
  searchData.value = {
    destination: urlParams.get('destination') || localStorage.getItem('searchDestination') || '',
    startDate: urlParams.get('startDate') || localStorage.getItem('searchStartDate') || '',
    endDate: urlParams.get('endDate') || localStorage.getItem('searchEndDate') || '',
    people: urlParams.get('people') || localStorage.getItem('searchPeople') || ''
  }
  
  // 生成天气信息
  weatherInfo.value = generateWeatherInfo()
  
  // 添加欢迎消息
  const welcomeMessage = {
    id: Date.now(),
    type: 'ai',
    text: `您好！我是您的AI旅行助手。我看到您计划去${searchData.value.destination || '某地'}旅行，从${searchData.value.startDate || '开始日期'}到${searchData.value.endDate || '结束日期'}，共${searchData.value.people || '？'}人。有什么我可以帮助您的吗？`,
    time: new Date().toLocaleTimeString()
  }
  
  messages.value.push(welcomeMessage)
  
  nextTick(() => {
    scrollToBottom()
  })
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

/* 模拟地图 */
.mock-map {
  flex: 1;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
  position: relative;
  overflow: hidden;
}

.mock-map.satellite {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.map-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
}

.destination-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.marker-icon {
  font-size: 2rem;
}

.marker-label {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1rem;
}

.travel-route {
  position: relative;
  width: 300px;
  height: 100px;
}

.route-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  border-radius: 2px;
  transform: translateY(-50%);
}

.route-points {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.route-point {
  background: #ffffff;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.route-point.start {
  background: #4ade80;
  color: white;
}

.route-point.end {
  background: #4ade80;
  color: white;
}

/* 地图信息面板 */
.map-info {
  width: 300px;
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
  padding: 1.5rem;
  overflow-y: auto;
}

.info-card, .weather-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.info-card h3, .weather-card h3 {
  color: #1f2937;
  font-size: 1.1rem;
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
  gap: 1rem;
}

.weather-icon {
  font-size: 2.5rem;
}

.weather-details {
  flex: 1;
}

.temperature {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.condition {
  color: #6b7280;
  font-size: 0.875rem;
}

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

