<template>
  <div id="home">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-logo">
          <h2>曦源Agent</h2>
        </div>
        <div class="nav-menu">
          <a href="#" class="nav-link">Home</a>
          <a href="#" class="nav-link">Discover</a>
          <a href="#" class="nav-link">Services</a>
          <a href="#" class="nav-link">News</a>
          <a href="#" class="nav-link">About Us</a>
          <a href="#" class="nav-link">Contact</a>
        </div>
        <div class="nav-lang">
          <div class="lang-selector">
            <span class="flag">🇮🇩</span>
            <span>ID</span>
            <span class="arrow">▼</span>
          </div>
        </div>
      </div>
    </nav>

    <!-- 英雄区域 -->
    <section class="hero">
      <div class="hero-background"></div>
      <div class="hero-content">
        <h1 class="hero-title">探索世界，带着微笑</h1>
        <p class="hero-subtitle">
          发现令人惊叹的目的地，创造难忘的回忆。我们为您提供最佳的旅行体验，
          让每一次旅程都成为美好的故事。
        </p>
        
        <!-- 搜索栏 -->
        <div class="search-container">
          <div class="search-box">
            <div class="search-field">
              <span class="search-icon">📍</span>
              <input type="text" placeholder="城市或目的地" v-model="searchData.destination" />
            </div>
            <div class="search-field">
              <span class="search-icon">📅</span>
              <input type="date" placeholder="开始日期" v-model="searchData.startDate" />
            </div>
            <div class="search-field">
              <span class="search-icon">📆</span>
              <input type="date" placeholder="结束日期" v-model="searchData.endDate" />
            </div>
            <div class="search-field">
              <span class="search-icon">👥</span>
              <select v-model="searchData.people">
                <option value="">人数</option>
                <option value="1">1人</option>
                <option value="2">2人</option>
                <option value="3">3人</option>
                <option value="4">4人</option>
                <option value="5+">5人以上</option>
              </select>
            </div>
            <button class="search-btn" @click="handleSearch">
              <span>立即查找行程</span>
              <span class="search-icon-btn">🔍</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 搜索数据
const searchData = ref({
  destination: '',
  startDate: '',
  endDate: '',
  people: ''
})

// 处理搜索
const handleSearch = () => {
  // 保存搜索数据到localStorage
  localStorage.setItem('searchDestination', searchData.value.destination)
  localStorage.setItem('searchStartDate', searchData.value.startDate)
  localStorage.setItem('searchEndDate', searchData.value.endDate)
  localStorage.setItem('searchPeople', searchData.value.people)
  
  // 跳转到聊天页面
  router.push('/plan-chat')
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#home {
  min-height: 100vh;
}

/* 导航栏样式 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #81a3a6;
  backdrop-filter: blur(10px);
  z-index: 1000;
  padding: 1rem 0;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
}

.nav-logo h2 {
  color: white;
  font-size: 1.8rem;
  font-weight: bold;
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #4ade80;
}

.lang-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.lang-selector:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.flag {
  font-size: 1.2rem;
}

.arrow {
  font-size: 0.8rem;
  color: #ccc;
}

/* 英雄区域样式 */
.hero {
  position: relative;
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('/bg.jpg') center center / cover no-repeat;
  background-attachment: scroll;
  z-index: -1;
}

.hero-content {
  text-align: center;
  color: #775c55;
  max-width: none;
  padding: 0 2rem;
  z-index: 1;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 3rem;
  opacity: 0.9;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  line-height: 1.6;
}

/* 搜索栏样式 */
.search-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.search-box {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  gap: 1rem;
  align-items: center;
  max-width: none;
  width: 100%;
  flex-wrap: nowrap;
}

.search-field {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 0.8rem 1rem;
  flex: 1;
  min-width: 140px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.search-field:focus-within {
  border-color: #4ade80;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.1);
}

.search-icon {
  margin-right: 0.8rem;
  font-size: 1.1rem;
  color: #666;
}

.search-field input,
.search-field select {
  border: none;
  background: transparent;
  outline: none;
  flex: 1;
  font-size: 1rem;
  color: #333;
}

.search-field input::placeholder {
  color: #999;
}

.search-btn {
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.8rem 1.2rem;
  font-size: 0.9rem;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(74, 222, 128, 0.3);
  flex-shrink: 0;
  white-space: nowrap;
  min-width: 120px;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 222, 128, 0.4);
}

.search-icon-btn {
  font-size: 1.2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
  }
  
  .nav-menu {
    display: none;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .search-box {
    flex-direction: column;
    padding: 1rem;
    flex-wrap: wrap;
  }
  
  .search-field {
    min-width: 100%;
    flex: none;
  }
  
  .search-btn {
    width: 100%;
    justify-content: center;
    flex-shrink: 1;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .search-box {
    margin: 0 1rem;
  }
}
</style>

