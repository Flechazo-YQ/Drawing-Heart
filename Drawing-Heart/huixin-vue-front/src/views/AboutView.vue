<template>
  <div class="about-container">
    <nav class="modern-nav">
      <div class="nav-content">
        <div class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </div>

        <!-- 未登录状态的导航 -->
        <div v-if="!isLoggedIn" class="nav-actions">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/about" class="nav-link active">关于</router-link>
          <router-link to="/login" class="nav-link">登录</router-link>
          <router-link to="/register" class="nav-link">注册</router-link>
        </div>

        <!-- 已登录状态的导航 -->
        <div v-else class="nav-actions">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/draw" class="nav-link">绘画空间</router-link>
          <router-link to="/chat" class="nav-link">心理对话</router-link>
          <router-link to="/about" class="nav-link active">关于我们</router-link>
          <router-link to="/user" class="nav-link">个人空间</router-link>
          <button class="nav-link logout-btn" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </nav>

    <main class="about-content">
      <div class="about-section">
        <h1>关于绘心同学</h1>
        <p>欢迎来到绘心同学，这是一个专注于心理健康的智能对话平台。</p>

        <div class="features-overview">
          <div class="feature-item">
            <h3>🎨 绘画分析</h3>
            <p>通过AI分析您的绘画作品，了解内心的情感状态</p>
            <router-link to="/draw" class="feature-link">开始绘画 →</router-link>
          </div>

          <div class="feature-item">
            <h3>💬 心理对话</h3>
            <p>与AI进行深度心理对话，获得专业的情感支持</p>
            <router-link to="/chat" class="feature-link">开始对话 →</router-link>
          </div>

          <div class="feature-item">
            <h3>👤 个人中心</h3>
            <p>管理您的个人信息和历史记录</p>
            <router-link to="/user" class="feature-link">进入中心 →</router-link>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = ref(false)

// 检查登录状态
const checkLoginStatus = () => {
  const token = localStorage.getItem('token')
  const loginFlag = localStorage.getItem('isLoggedIn')
  isLoggedIn.value = !!(token && loginFlag === 'true')
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('isLoggedIn')
  localStorage.removeItem('rememberLogin')
  localStorage.removeItem('savedUsername')

  // 清除其他可能的用户数据
  const keys = Object.keys(localStorage)
  keys.forEach(key => {
    if (key.startsWith('chatMessages_') ||
        key.startsWith('isAdminMode_') ||
        key.startsWith('lastChatTimestamp_')) {
      localStorage.removeItem(key)
    }
  })

  isLoggedIn.value = false
  router.push('/')
}

// 页面加载时检查登录状态
onMounted(() => {
  checkLoginStatus()
})
</script>

<style scoped>
.about-container {
  min-height: 100vh;
  background-color: var(--color-background);
}

.modern-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.nav-content {
  max-width: 1920px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  color: #1a1a1a;
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: default; /* 默认光标，不显示可点击状态 */
}

.logo-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: #4a4a4a;
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
}

.nav-link.active {
  color: #42b983;
  background-color: rgba(66, 185, 131, 0.15);
  font-weight: 600;
}

/* 按钮样式 */
.nav-link {
  border: none;
  background: none;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.logout-btn {
  color: #ff6b6b;
  border: 1px solid #ff6b6b;
}

.logout-btn:hover {
  background-color: #ff6b6b;
  color: white;
}

.about-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 84px 2rem 2rem;
}

.about-section {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-top: 2rem;
}

.about-section h1 {
  margin: 0 0 1.5rem;
  font-size: 2rem;
  color: #1a1a1a;
  font-weight: 600;
}

.about-section p {
  color: #4a4a4a;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.features-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.feature-item {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.feature-item h3 {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  color: #1a1a1a;
  font-weight: 600;
}

.feature-item p {
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 1.5rem;
}

.feature-link {
  color: #42b983;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s;
}

.feature-link:hover {
  color: #3aa876;
}
</style>
