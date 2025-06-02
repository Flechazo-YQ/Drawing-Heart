<template>
  <div class="home">
    <nav class="navbar">
      <div class="navbar-container">
        <router-link to="/" class="navbar-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span class="logo-text">绘心同学</span>
          <span class="logo-subtitle">AI心理绘画治疗平台</span>
        </router-link>
        <div class="navbar-links">
          <router-link to="/" class="nav-link">主页</router-link>
          <router-link to="/privacy" class="nav-link">隐私政策</router-link>
        </div>
      </div>
    </nav>

    <div class="main-content">
      <div class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h1>先进的共情陪伴大模型</h1>
            <p class="hero-description">通过AI赋能的心理绘画分析，带来专业的心理关怀</p>
            <router-link to="/login" class="cta-button">开始心理之旅</router-link>
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
            <div class="feature-card">
              <h3>智能诊断</h3>
              <p>基于先进的AI模型分析您的心理状态</p>
            </div>
            <div class="feature-card">
              <h3>专业解读</h3>
              <p>提供专业的心理绘画分析和建议</p>
            </div>
            <div class="feature-card">
              <h3>隐私保护</h3>
              <p>严格的数据加密和隐私保护机制</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <footer class="modern-footer">
      <div class="footer-content">
        <p>&copy; 2025 心理平台. 保留所有权利.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// 组件逻辑可以在这里添加
</script>

<style scoped>
/* 主页容器样式 */
.home {
  min-height: 100vh; /* 最小高度为视口高度 */
  background-color: #ffffff; /* 白色背景 */
}

/* 顶部导航栏 */
.navbar {
  position: fixed; /* 固定定位 */
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  background-color: rgba(255, 255, 255, 0.98); /* 半透明白色背景 */
  backdrop-filter: blur(10px); /* 背景模糊效果 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); /* 阴影效果 */
  z-index: 1000; /* 层级 */
}

/* 导航栏容器 */
.navbar-container {
  width: 100%;
  max-width: 1200px; /* 最大宽度限制 */
  margin: 0 auto; /* 水平居中 */
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between; /* 两端对齐 */
  align-items: center; /* 垂直居中 */
  box-sizing: border-box;
}

/* 导航栏Logo */
.navbar-logo {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

/* Logo主文字 */
.logo-text {
  color: #1a1a1a;
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: -0.5px;
}

/* Logo副标题 */
.logo-subtitle {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.2rem;
}

/* 导航链接容器 */
.navbar-links {
  display: flex;
  gap: 3rem; /* 链接间距 */
}

/* 导航链接样式 */
.nav-link {
  color: #1a1a1a;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 500;
  transition: color 0.3s ease; /* 颜色过渡动画 */
}

/* 导航链接悬停效果 */
.nav-link:hover {
  color: #42b983; /* 绿色 */
}

/* 主要内容区域 */
.main-content {
  width: 100%;
  max-width: 100%;
  padding-top: 80px; /* 为固定导航栏留出空间 */
  overflow-x: hidden;
}

/* Hero区域 */
.hero-section {
  width: 100%;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); /* 渐变背景 */
  padding: 6rem 2rem;
  box-sizing: border-box;
}

/* Hero内容 */
.hero-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr; /* 两列布局 */
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
  padding: 6rem 2rem;
  background-color: #ffffff;
  box-sizing: border-box;
}

/* 区域容器 */
.section-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  box-sizing: border-box;
}

/* 区域标题 */
.section-title {
  text-align: center;
  font-size: 2.5rem;
  color: #1a1a1a;
  margin-bottom: 4rem;
  font-weight: 700;
}

/* 功能特性网格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 三列布局 */
  gap: 2rem;
}

/* 功能特性卡片 */
.feature-card {
  background: #ffffff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

/* 功能特性卡片悬停效果 */
.feature-card:hover {
  transform: translateY(-5px);
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
}

/* 现代页脚 */
.modern-footer {
  background-color: #1a1a1a;
  color: #ffffff;
  padding: 2rem 4rem;
}

/* 页脚内容 */
.footer-content {
  max-width: 1440px;
  margin: 0 auto;
  text-align: center;
  font-size: 1rem;
  opacity: 0.8;
}

/* 响应式布局 - 大屏幕 */
@media (max-width: 1200px) {
  .navbar-container,
  .hero-content,
  .section-container {
    max-width: 1140px;
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

  .navbar-container {
    padding: 1rem 2rem;
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
