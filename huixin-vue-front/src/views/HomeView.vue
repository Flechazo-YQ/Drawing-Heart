<template>
  <div class="home">
    <NavBarGuest v-if="!isLoggedIn" />
    <NavBarUser v-else />

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
            <img src="@/assets/images/others/Heart.png" alt="心理诊断" />
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
          <router-link to="/feedback" class="footer-link">意见反馈</router-link>
          <router-link to="/admin-login" class="footer-link admin-entry">管理入口</router-link>
        </div>
        <p>&copy; 2025 绘心同学. 保留所有权利.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NavBarGuest from '@/components/NavBarGuest.vue'
import NavBarUser from '@/components/NavBarUser.vue'

const isLoggedIn = ref(false)

// 检查登录状态
const checkLoginStatus = () => {
  const token = localStorage.getItem('token')
  const loginFlag = localStorage.getItem('isLoggedIn')
  isLoggedIn.value = !!(token && loginFlag === 'true')
}

// 页面加载时检查登录状态
onMounted(() => {
  checkLoginStatus()
})
</script>

<style scoped>
/* 主页容器样式 */
.home {
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* 主要内容区域 */
.main-content {
  width: 100%;
  max-width: 100%;
  padding-top: 64px;
  overflow-x: hidden;
}

/* Hero区域 */
.hero-section {
  width: 100%;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  padding: 3rem 2rem;
  box-sizing: border-box;
}

/* Hero内容 */
.hero-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
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
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

/* Hero图片悬停效果 */
.hero-image img:hover {
  transform: translateY(-10px);
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

/* 现代页脚 */
.modern-footer {
  background-color: #F8F9FA;
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

/* 响应式布局 */
@media (max-width: 992px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-text {
    padding-right: 0;
  }
}

@media (max-width: 768px) {
  .hero-text h1 {
    font-size: 2.5rem;
  }
}
</style>
