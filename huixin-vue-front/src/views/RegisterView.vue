<template>
  <div class="register-container">
    <div class="register-content">
      <div class="register-left">
        <div class="brand-content">
          <router-link to="/" class="brand-logo">
            <h1>绘心同学</h1>
            <p class="brand-subtitle">AI心理绘画治疗平台</p>
          </router-link>
          <div class="features-grid">
            <div class="feature-item">
              <span class="feature-icon">🎨</span>
              <h3>心理绘画分析</h3>
              <p>通过AI技术解读您的心理状态</p>
            </div>
            <div class="feature-item">
              <span class="feature-icon">💭</span>
              <h3>智能对话</h3>
              <p>温暖贴心的AI心理陪伴</p>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🔒</span>
              <h3>隐私保护</h3>
              <p>严格的数据加密与隐私保护</p>
            </div>
          </div>
        </div>
      </div>

      <div class="register-right">
        <div class="register-box">
          <h2 class="register-title">创建账户</h2>
          <p class="register-subtitle">加入我们，开启您的心理健康之旅</p>

          <form class="register-form" @submit.prevent="handleRegister">
            <div class="form-group">
              <label>用户名</label>
              <input v-model="formData.username" type="text" class="form-input" placeholder="请设置用户名" required />
            </div>

            <div class="form-group">
              <label>电子邮箱</label>
              <input v-model="formData.email" type="email" class="form-input" placeholder="请输入邮箱地址" required />
            </div>

            <div class="form-group">
              <label>性别</label>
              <div class="gender-selector">
                <label class="gender-option">
                  <input type="radio" v-model="formData.gender" value="male" required />
                  <span>男</span>
                </label>
                <label class="gender-option">
                  <input type="radio" v-model="formData.gender" value="female" required />
                  <span>女</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>密码</label>
              <input v-model="formData.password" type="password" class="form-input" placeholder="请设置密码" required />
            </div>

            <div class="form-group">
              <label>确认密码</label>
              <input v-model="formData.confirmPassword" type="password" class="form-input" placeholder="请再次输入密码"
                required />
            </div>

            <div class="terms-agreement">
              <label class="checkbox-label">
                <input type="checkbox" v-model="formData.agreeToTerms" required />
                <span>我已阅读并同意</span>
              </label>
              <router-link to="/terms" class="terms-link">服务条款</router-link>
              <span>和</span>
              <router-link to="/privacy" class="terms-link">隐私政策</router-link>
            </div>

            <button type="submit" class="register-button" :disabled="isLoading">
              {{ isLoading ? '注册中...' : '立即注册' }}
            </button>

            <p class="login-hint">
              已有账号？
              <router-link to="/login" class="login-link">立即登录</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config' // 导入配置文件

const router = useRouter()
const isLoading = ref(false)

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false,
  gender: ''
})

const handleRegister = async () => {
  // 表单验证
  if (formData.password !== formData.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  if (!formData.agreeToTerms) {
    ElMessage.error('请阅读并同意服务条款和隐私政策')
    return
  }

  try {
    isLoading.value = true
    const apiUrl = `${config.baseURL}${config.registerPath}`
    console.log('正在发送注册请求到:', apiUrl)
    console.log('请求数据:', {
      username: formData.username,
      email: formData.email,
      gender: formData.gender
    })

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        username: formData.username,
        password: formData.password,
        email: formData.email,
        gender: formData.gender
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error('服务器返回错误:', errorData)
      throw new Error(errorData.message || '注册失败')
    }

    const data = await response.json()
    console.log('服务器响应：', data)

    if (data.code === 0) {
      ElMessage.success('注册成功!')
      router.push('/login')
    } else {
      ElMessage.error(data.message || '注册失败，请检查输入信息')
    }
  } catch (error) {
    console.error('注册过程中发生错误：', error)
    ElMessage.error(error.message || '注册失败，请检查网络连接')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-content {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.register-left {
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

.features-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 2rem;
  margin-top: 3rem;
}

.feature-item {
  text-align: left;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  transition: transform 0.2s;
}

.feature-item:hover {
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
  display: block;
}

.feature-item h3 {
  color: #1a1a1a;
  font-size: 1.25rem;
  margin: 0 0 0.5rem;
}

.feature-item p {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.register-right {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  padding: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-box {
  width: 100%;
  max-width: 450px;
  position: relative;
  padding-top: 100%;
}

.register-box::before {
  content: "";
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  box-sizing: border-box;
}

.register-title, .register-subtitle, .register-form {
  position: relative;
  z-index: 1;
}

.register-title {
  font-size: 1.75rem;
  color: #1a1a1a;
  margin: 0;
  font-weight: 600;
  position: absolute;
  top: 0.5rem;
  left: 1.5rem;
}

.register-subtitle {
  color: #6b7280;
  margin: 0;
  font-size: 0.9rem;
  position: absolute;
  top: 2.75rem;
  left: 1.5rem;
}

.register-form {
  position: absolute;
  top: 5rem;
  left: 0;
  width: 100%;
  height: calc(100% - 5rem);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding: 1.5rem;
  box-sizing: border-box;
  overflow-y: visible;
  max-height: none;
}

.form-group {
  margin-bottom: 0.6rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  color: #4b5563;
  font-size: 0.8rem;
}

.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s;
  background: #ffffff;
}

.form-input:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.gender-selector {
  display: flex;
  gap: 0.75rem;
}

.gender-option {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.terms-agreement {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: 1rem;
  color: #6b7280;
  font-size: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.terms-link {
  color: #42b983;
  text-decoration: none;
  transition: color 0.2s;
}

.terms-link:hover {
  color: #3aa876;
}

.register-button {
  width: 100%;
  padding: 0.6rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.register-button:hover {
  background: #3aa876;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

.login-hint {
  text-align: center;
  margin-top: 1rem;
  color: #6b7280;
  font-size: 0.75rem;
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
  .register-content {
    grid-template-columns: 1fr;
  }

  .register-left {
    display: none;
  }

  .register-right {
    padding: 2rem;
  }

  .register-box {
    max-width: 100%;
  }
}

@media (max-width: 640px) {
  .register-right {
    padding: 1.5rem;
  }

  .register-title {
    font-size: 1.75rem;
  }

  .terms-agreement {
    font-size: 0.75rem;
  }
}
</style>