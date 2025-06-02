<template>
  <div class="admin-login-container">
    <div class="admin-login-box">
      <h1>管理员登录</h1>
      <div class="admin-form">
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="username" 
            type="text" 
            class="form-input" 
            placeholder="管理员用户名" 
            required
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="password" 
            type="password" 
            class="form-input" 
            placeholder="管理员密码" 
            required
          />
        </div>
        <button 
          @click="handleLogin" 
          class="login-button" 
          :disabled="isLoading"
        >
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
        <p class="back-link">
          <router-link to="/">返回主页</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config' // 导入配置文件

const router = useRouter()
const username = ref('')
const password = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  isLoading.value = true

  try {
    const response = await fetch(`${config.baseURL}/api/admin/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })

    const data = await response.json()

    if (data.code === 0) {
      // 登录成功
      localStorage.setItem('isAdminLoggedIn', 'true')
      localStorage.setItem('adminToken', data.token)
      localStorage.setItem('adminUsername', username.value)
      
      ElMessage.success('登录成功')
      router.push('/admin')
    } else {
      ElMessage.error(data.message || '登录失败，请检查用户名和密码')
    }
  } catch (error) {
    console.error('登录错误:', error)
    ElMessage.error('登录失败，请检查网络连接')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f3f4f6;
}

.admin-login-box {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #1f2937;
  margin-bottom: 2rem;
}

.admin-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
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

.login-button {
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
  margin-top: 1rem;
}

.login-button:hover {
  background: #3aa876;
}

.login-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.back-link {
  text-align: center;
  margin-top: 1.5rem;
}

.back-link a {
  color: #42b983;
  text-decoration: none;
  font-size: 0.875rem;
}

.back-link a:hover {
  text-decoration: underline;
}
</style>