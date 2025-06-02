<template>
  <div class="user-container">
    <nav class="modern-nav">
      <div class="nav-content">
        <router-link to="/" class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </router-link>
        <div class="nav-actions">
          <router-link to="/chat" class="nav-link">前往对话</router-link>
          <button class="nav-button" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </nav>

    <main class="user-content">
      <div class="profile-section">
        <div class="profile-header">
          <div class="avatar-container">
            <img :src="userInfo.gender === 'male' ? '/src/assets/images/boy.png' : '/src/assets/images/girl.png'"
              alt="用户头像" class="avatar" />
          </div>
          <h1 class="username">{{ username }}</h1>
        </div>

        <div class="info-cards">
          <div class="info-card">
            <h3 class="card-title">个人信息</h3>
            <div class="info-content">
              <div class="info-item">
                <span class="label">用户名</span>
                <span class="value">{{ username }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱</span>
                <span class="value">{{ email }}</span>
              </div>
              <div class="info-item">
                <span class="label">性别</span>
                <span class="value">{{ userInfo.gender === 'male' ? '男' : '女' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config' // 导入配置文件

const router = useRouter()
const username = ref('')
const email = ref('')
const userInfo = ref({})

const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    const response = await fetch(`${config.baseURL}/api/user/info`, {
      method: 'GET',
      headers: {
        'Authorization': token
      }
    })

    if (!response.ok) {
      throw new Error('获取用户信息失败')
    }

    const data = await response.json()
    if (data.code === 0) {
      username.value = data.data.username
      email.value = data.data.email
      userInfo.value = data.data
    } else {
      throw new Error(data.message || '获取用户信息失败')
    }
  } catch (error) {
    ElMessage.error(error.message)
    router.push('/login')
  }
}

onMounted(() => {
  fetchUserInfo()
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  router.push('/login')
}
</script>

<style scoped>
.user-container {
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
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 4rem;
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
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 6px;
  color: #4a4a4a;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.nav-link:hover {
  background-color: rgb(66, 185, 131, 0.4);
  color: #42b983;
}

.nav-button {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 6px;
  background: #f3f4f6;
  color: #4a4a4a;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-button:hover {
  background: #ff000089;
}

.user-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 100px 4rem 4rem;
}

.profile-section {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 3rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 3rem;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.avatar-container {
  width: 160px;
  height: 160px;
  border-radius: 80px;
  overflow: hidden;
  border: 4px solid #42b983;
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.15);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.username {
  font-size: 2.5rem;
  color: #1a1a1a;
  margin: 0;
  font-weight: 600;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-top: 1rem;
}

.info-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 2rem;
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-title {
  color: #1a1a1a;
  font-size: 1.5rem;
  margin: 0 0 2rem;
  font-weight: 600;
  border-bottom: 2px solid #42b983;
  padding-bottom: 0.75rem;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #4b5563;
  font-size: 1rem;
  font-weight: 500;
}

.value {
  color: #1a1a1a;
  font-size: 1rem;
  font-weight: 600;
}

@media (max-width: 1200px) {

  .nav-content,
  .user-content {
    padding-left: 2rem;
    padding-right: 2rem;
  }

  .profile-section {
    padding: 2rem;
  }
}

@media (max-width: 768px) {
  .info-cards {
    grid-template-columns: 1fr;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }

  .username {
    font-size: 2rem;
  }

  .avatar-container {
    width: 140px;
    height: 140px;
  }
}

@media (max-width: 480px) {

  .nav-content,
  .user-content {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .profile-section {
    padding: 1.5rem;
  }

  .username {
    font-size: 1.75rem;
  }

  .card-title {
    font-size: 1.25rem;
  }
}
</style>