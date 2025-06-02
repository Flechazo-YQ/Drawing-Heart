<template>
  <div class="reset-container">
    <div class="reset-content">
      <div class="reset-left">
        <div class="brand-content">
          <router-link to="/" class="brand-logo">
            <img src="../assets/images/logo.png" alt="绘心同学" class="logo-img" />
            <h1>绘心同学</h1>
            <p class="brand-subtitle">AI心理绘画治疗平台</p>
          </router-link>
          <div class="hero-image">
            <img src="../assets/images/3.png" alt="心理诊断" />
          </div>
        </div>
      </div>

      <div class="reset-right">
        <div class="reset-box">
          <h2 class="reset-title">重置密码</h2>
          <p class="reset-subtitle">请输入您的新密码</p>

          <form class="reset-form" @submit.prevent="handleSubmit">
            <div class="form-group">
              <label>新密码</label>
              <input 
                v-model="password"
                type="password" 
                class="form-input" 
                placeholder="请输入新密码"
                required
              />
            </div>

            <div class="form-group">
              <label>确认新密码</label>
              <input 
                v-model="confirmPassword"
                type="password" 
                class="form-input" 
                placeholder="请再次输入新密码"
                required
              />
            </div>

            <button type="submit" class="reset-button" :disabled="isLoading">
              {{ isLoading ? '重置中...' : '重置密码' }}
            </button>

            <p class="login-hint">
              想起密码了？
              <router-link to="/login" class="login-link">返回登录</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config' // 导入配置文件

const router = useRouter()
const route = useRoute()
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)

onMounted(() => {
  // 检查URL中是否包含重置token
  const token = route.query.token
  if (!token) {
    ElMessage.error('无效的重置链接')
    router.push('/login')
  }
})

const handleSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  try {
    isLoading.value = true
    const response = await fetch(`${config.baseURL}/api/update-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        token: route.query.token,
        password: password.value
      })
    })

    const data = await response.json()
    if (data.code === 0) {
      ElMessage.success('密码重置成功，请重新登录')
      router.push('/login')
    } else {
      ElMessage.error(data.message || '重置失败，请稍后重试')
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.reset-container {
  min-height: 100vh;
  background-color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reset-content {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.reset-left {
  background: #ffffff;
  padding: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-content {
  max-width: 480px;
  text-align: center;
}

.brand-logo {
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.logo-img {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.brand-logo h1 {
  font-size: 2.5rem;
  color: #1a1a1a;
  margin: 0;
  font-weight: 600;
}

.brand-subtitle {
  color: #6b7280;
  font-size: 1.125rem;
  margin: 0.5rem 0 0;
}

.hero-image {
  margin-top: 3rem;
}

.hero-image img {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.reset-right {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  padding: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reset-box {
  width: 100%;
  max-width: 400px;
}

.reset-title {
  font-size: 2rem;
  color: #1a1a1a;
  margin: 0;
  font-weight: 600;
}

.reset-subtitle {
  color: #6b7280;
  margin: 0.5rem 0 2rem;
}

.reset-form {
  margin-top: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4b5563;
  font-size: 0.875rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
  background: #ffffff;
}

.form-input:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.reset-button {
  width: 100%;
  padding: 0.875rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-button:hover {
  background: #3aa876;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

.login-hint {
  text-align: center;
  margin-top: 2rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.login-link {
  color: #42b983;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.login-link:hover {
  color: #3aa876;
}

@media (max-width: 1024px) {
  .reset-content {
    grid-template-columns: 1fr;
  }

  .reset-left {
    display: none;
  }

  .reset-right {
    padding: 2rem;
  }

  .reset-box {
    max-width: 100%;
  }
}

@media (max-width: 640px) {
  .reset-right {
    padding: 1.5rem;
  }

  .reset-title {
    font-size: 1.75rem;
  }
}
</style>