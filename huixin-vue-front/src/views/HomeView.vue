<template>
  <div class="home">
    <nav class="modern-nav">
      <div class="nav-content">
        <div class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </div>

        <!-- 未登录状态的导航 -->
        <div v-if="!isLoggedIn" class="nav-actions">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">首页</router-link>
          <router-link to="/login" class="nav-link login-btn">登录</router-link>
          <router-link to="/register" class="nav-link register-btn">注册</router-link>
        </div>

        <!-- 已登录状态的导航 -->
        <div v-else class="nav-actions">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">首页</router-link>
          <router-link to="/draw" class="nav-link" :class="{ active: $route.path === '/draw' }">绘画空间</router-link>
          <router-link to="/chat" class="nav-link" :class="{ active: $route.path === '/chat' }">心理对话</router-link>
          <router-link to="/user" class="nav-link" :class="{ active: $route.path === '/user' }">个人空间</router-link>
          <button class="nav-button logout-btn" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </nav>

    <div class="main-content">
      <div class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h1>先进的共情陪伴大模型</h1>
            <p class="hero-description">通过AI赋能的心理绘画分析，带来专业的心理关怀</p>
            <router-link :to="isLoggedIn ? '/draw' : '/login'" class="cta-button">
              {{ isLoggedIn ? '开始绘画创作' : '开始心理之旅' }}
            </router-link>
          </div>
          <div class="hero-image">
            <img src="@/assets/images/logo.png" alt="心理诊断" />
          </div>
        </div>
      </div>

      <div class="features-section">
        <div class="section-container">
          <h2 class="section-title">我们的服务</h2>
          <div class="features-grid">
            <router-link :to="isLoggedIn ? '/draw' : '/login'" class="feature-card">
              <h3>🎨 智能绘画分析</h3>
              <p>通过绘画作品深入了解您的内心世界</p>
              <span class="feature-action">{{ isLoggedIn ? '开始绘画 →' : '登录体验 →' }}</span>
            </router-link>
            <router-link :to="isLoggedIn ? '/chat' : '/login'" class="feature-card">
              <h3>💬 AI心理对话</h3>
              <p>与专业AI进行深度心理交流和陪伴</p>
              <span class="feature-action">{{ isLoggedIn ? '开始对话 →' : '登录体验 →' }}</span>
            </router-link>
            <router-link :to="isLoggedIn ? '/user' : '/login'" class="feature-card">
              <h3>👤 个人空间</h3>
              <p>管理您的心理健康记录和个人信息</p>
              <span class="feature-action">{{ isLoggedIn ? '进入空间 →' : '登录体验 →' }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <footer class="modern-footer">
      <div class="footer-content">
        <div class="footer-links">
          <router-link to="/about" class="footer-link">关于我们</router-link>
          <router-link to="/privacy" class="footer-link">隐私政策</router-link>
          <router-link to="/terms" class="footer-link">服务条款</router-link>
          <router-link to="/admin-login" class="footer-link admin-entry">管理入口</router-link>
        </div>
        <p>&copy; 2025 绘心同学. 保留所有权利.</p>
      </div>
    </footer>
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
/* 主页容器样式 */
.home {
  min-height: 100vh; /* 最小高度为视口高度 */
  background-color: #f8f9fa; /* 与页面底部相同的淡灰色背景 */
}

/* 统一导航栏样式 */
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
  cursor: default;
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
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  background: none;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
}

.nav-link.active {
  color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
  font-weight: 600;
}

.nav-button {
  background: none;
  border: 1px solid #ddd;
  color: #4a4a4a;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.login-btn {
  color: #42b983;
  border: 1px solid #42b983;
}

.login-btn:hover {
  background-color: #42b983;
  color: white;
}

/* 注册按钮特殊样式 */
.register-btn {
  background-color: #42b983;
  color: white;
}

.register-btn:hover {
  background-color: #3aa876;
  transform: translateY(-1px);
}

.logout-btn {
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.logout-btn:hover {
  background-color: #ff6b6b;
  color: white;
}

/* 主要内容区域 */
.main-content {
  width: 100%;
  max-width: 100%;
  padding-top: 64px; /* 减少导航栏下方的空白 */
  overflow-x: hidden;
}

/* Hero区域 */
.hero-section {
  width: 100%;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); /* 渐变背景 */
  padding: 3rem 2rem; /* 减少上下padding，让内容更紧凑 */
  box-sizing: border-box;
}

/* Hero内容 */
.hero-content {
  width: 100%;
  max-width: var(--container-max-width, 1200px);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr; /* 两列布局 */
  gap: calc(var(--spacing-unit, 1rem) * 4);
  align-items: center;
  box-sizing: border-box;
}

/* Hero文字区域 */
.hero-text {
  padding-right: 2rem;
}

/* Hero标题 */
.hero-text h1 {
  font-size: 3.2rem;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  color: #1a1a1a;
  font-weight: 700;
  letter-spacing: -1px;
}

/* Hero描述文字 */
.hero-description {
  font-size: 1.25rem;
  line-height: 1.6;
  color: #4a4a4a;
  margin-bottom: 2.5rem;
}

/* Hero图片区域 */
.hero-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Hero图片 */
.hero-image img {
  max-width: 100%;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  transition: transform 0.3s ease;
}

/* Hero图片悬停效果 */
.hero-image img:hover {
  transform: translateY(-10px); /* 向上浮动 */
}

/* 行动按钮 */
.cta-button {
  background-color: #42b983;
  color: white;
  padding: 1rem 2.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  display: inline-block;
}

/* 行动按钮悬停效果 */
.cta-button:hover {
  background-color: #3aa876;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(66, 185, 131, 0.4);
}

/* 功能特性区域 */
.features-section {
  width: 100%;
  padding: 4rem 2rem; /* 减少上下padding */
  background-color: #ffffff;
  box-sizing: border-box;
}

/* 区域容器 */
.section-container {
  width: 100%;
  max-width: var(--container-max-width, 1200px);
  margin: 0 auto;
  box-sizing: border-box;
}

/* 区域标题 */
.section-title {
  text-align: center;
  font-size: 2.5rem;
  color: #1a1a1a;
  margin-bottom: 2.5rem; /* 减少下边距 */
  font-weight: 700;
}

/* 功能特性网格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 三列布局 */
  gap: calc(var(--spacing-unit, 1rem) * 2);
}

/* 功能特性卡片 */
.feature-card {
  background: #ffffff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

/* 功能特性卡片悬停效果 */
.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  color: inherit;
  text-decoration: none;
}

/* 功能特性卡片标题 */
.feature-card h3 {
  font-size: 1.5rem;
  color: #1a1a1a;
  margin-bottom: 1rem;
  font-weight: 600;
}

/* 功能特性卡片描述 */
.feature-card p {
  font-size: 1.1rem;
  color: #4a4a4a;
  line-height: 1.6;
  flex-grow: 1;
  margin-bottom: 1rem;
}

/* 功能卡片操作提示 */
.feature-action {
  color: #42b983;
  font-weight: 500;
  font-size: 0.95rem;
  margin-top: auto;
  transition: color 0.2s;
}

.feature-card:hover .feature-action {
  color: #3aa876;
}

/* 现代页脚 */
.modern-footer {
  background-color: #1a1a1a;
  color: #ffffff;
  padding: 3rem 4rem 2rem;
}

/* 页脚内容 */
.footer-content {
  max-width: 1440px;
  margin: 0 auto;
  text-align: center;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.footer-link {
  color: #ccc;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #42b983;
}

.admin-entry {
  font-size: 0.8rem;
  opacity: 0.7;
}

.footer-content p {
  font-size: 0.9rem;
  opacity: 0.8;
  margin: 0;
}

/* 响应式布局 - 大屏幕 */
@media (max-width: 1200px) {
  .nav-content,
  .hero-content,
  .section-container {
    max-width: 1140px;
  }
}

/* 2K分辨率优化 */
@media (min-width: 2560px) {
  .hero-text h1 {
    font-size: 4rem;
  }

  .hero-description {
    font-size: 1.4rem;
  }

  .section-title {
    font-size: 3rem;
  }

  .feature-card h3 {
    font-size: 1.8rem;
  }

  .feature-card p {
    font-size: 1.25rem;
  }

  .cta-button {
    padding: 1.25rem 3rem;
    font-size: 1.25rem;
  }
}

/* 4K分辨率优化 */
@media (min-width: 3840px) {
  .hero-text h1 {
    font-size: 5rem;
    line-height: 1.1;
  }

  .hero-description {
    font-size: 1.6rem;
    margin-bottom: 3rem;
  }

  .section-title {
    font-size: 3.5rem;
    margin-bottom: 5rem;
  }

  .feature-card {
    padding: 3rem;
  }

  .feature-card h3 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
  }

  .feature-card p {
    font-size: 1.4rem;
  }

  .cta-button {
    padding: 1.5rem 3.5rem;
    font-size: 1.4rem;
  }

  .nav-link {
    font-size: 1.3rem;
  }

  .logo-text {
    font-size: 2rem;
  }

  .logo-subtitle {
    font-size: 1.1rem;
  }
}

/* 响应式布局 - 中等屏幕 */
@media (max-width: 992px) {
  .hero-content {
    grid-template-columns: 1fr; /* 单列布局 */
    text-align: center;
  }

  .hero-text {
    padding-right: 0;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr); /* 两列布局 */
  }

  .nav-content {
    padding: 0 1rem;
  }
}

/* 响应式布局 - 小屏幕 */
@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr; /* 单列布局 */
  }

  .hero-text h1 {
    font-size: 2.5rem;
  }

  .section-title {
    font-size: 2rem;
  }
}
</style>
