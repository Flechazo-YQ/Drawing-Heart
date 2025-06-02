<template>
  <div class="about-container">
    <nav class="modern-nav">
      <div class="nav-content">
        <router-link to="/" class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </router-link>
        <div class="nav-actions">
          <router-link to="/chat" class="nav-link">开始对话</router-link>
          <router-link to="/user" class="nav-link">个人中心</router-link>
        </div>
      </div>
    </nav>

    <main class="about-content">
      <div class="about-section">
        <h1>关于绘心同学</h1>
        <p>欢迎来到绘心同学，这是一个专注于心理健康的智能对话平台。</p>
      </div>
    </main>
  </div>
</template>

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
}
</style>
