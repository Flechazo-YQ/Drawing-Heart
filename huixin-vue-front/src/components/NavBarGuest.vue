<template>
  <nav class="modern-nav">
    <div class="nav-content">
      <div class="nav-logo">
        <img src="@/assets/images/others/Logo.png" alt="绘心同学" class="logo-img" />
        <span>绘心同学</span>
      </div>
      <div class="nav-actions">
        <router-link
          to="/"
          class="nav-link"
          :class="{ active: route.path === '/' }"
        >首页</router-link>
        <router-link
          to="/login"
          class="nav-link"
          :class="{ active: route.path === '/login' }"
        >登录</router-link>
        <router-link
          to="/register"
          class="nav-link"
          :class="{ active: route.path === '/register' }"
        >注册</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<style scoped>
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
  transition: all 0.2s;
}

.nav-link:hover {
  color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
  transform: translateY(-1px);
}

.nav-link.active {
  color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
  font-weight: 600;
  transform: translateY(0px);
}
</style>
