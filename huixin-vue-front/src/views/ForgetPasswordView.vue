<template>
  <div class="forget-container">
    <div class="forget-content">
      <div class="forget-left">
        <div class="brand-content">
          <router-link to="/" class="brand-logo">
            <h1>绘心同学</h1>
            <p class="brand-subtitle">AI心理绘画治疗平台</p>
          </router-link>
          <div class="hero-image">
            <img src="../assets/images/others/Heart.png" alt="心理诊断" />
          </div>
        </div>
      </div>

      <div class="forget-right">
        <div class="forget-box">
          <h2 class="forget-title">重置密码</h2>
          <p class="forget-subtitle">请输入您的注册邮箱和新密码</p>

          <form class="forget-form" @submit.prevent="handleSubmit">
            <div class="form-group">
              <label>电子邮箱</label>
              <input
                v-model="email"
                type="email"
                class="form-input"
                placeholder="请输入您的注册邮箱"
                required
              />
            </div>

            <div class="form-group">
              <label>邮箱验证码</label>
              <div class="verification-code-group">
                <input v-model="code" type="text" class="form-input" placeholder="请输入4位验证码" required />
                <button @click.prevent="sendCode" :disabled="isSendingCode || countdown > 0" class="send-code-button">
                  {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
                </button>
              </div>
            </div>

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

            <button type="submit" class="forget-button" :disabled="isLoading">
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config' // 导入配置文件
import apiClient from '@/api' // 导入API客户端

const router = useRouter()
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const code = ref('')
const isLoading = ref(false)
const isSendingCode = ref(false)
const countdown = ref(0)

const sendCode = async () => {
  if (!email.value) {
    ElMessage.error('请输入电子邮箱地址')
    return
  }
  isSendingCode.value = true
  try {
    const response = await apiClient.post(config.sendResetCodePath, { email: email.value })
    ElMessage.success('验证码已发送，请注意查收邮箱')
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    ElMessage.error(`请求失败，请稍后重试`)
  } finally {
    isSendingCode.value = false
  }
}

const handleSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  try {
    isLoading.value = true
    const data = await apiClient.post(config.resetPasswordDirectPath, {
      email: email.value,
      password: password.value,
      code: code.value
    })

    if (data.code === 0) {
      ElMessage.success('密码重置成功，请使用新密码登录')
      // 延迟跳转，让用户有时间看到成功消息
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      // 错误已由 apiClient 拦截器处理
    }
  } catch (error) {
    ElMessage.error('密码重置失败，请稍后再试')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.forget-container {
  min-height: 100vh;
  background-color: #f9fafb;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 0;
}

.forget-content {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.forget-left {
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

.hero-image {
  margin-top: 3rem;
}

.hero-image img {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.forget-right {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.forget-box {
  width: 100%;
  max-width: 450px;
  padding: 2rem;
}

.forget-title {
  font-size: 1.75rem;
  color: #1a1a1a;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.forget-subtitle {
  color: #6b7280;
  margin: 0 0 2rem 0;
  font-size: 0.9rem;
}

.forget-form {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.form-group {
  margin-bottom: 0.8rem;
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

.forget-button {
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

.forget-button:hover {
  background: #3aa876;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

.login-hint {
  text-align: center;
  margin-top: 0.8rem;
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

.verification-code-group {
  display: flex;
  gap: 0.5rem;
}

.send-code-button {
  padding: 0.5rem 0.75rem;
  border: 1px solid #42b983;
  background-color: #fff;
  color: #42b983;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.send-code-button:disabled {
  cursor: not-allowed;
  background-color: #f0f2f5;
  border-color: #e5e7eb;
  color: #a0aec0;
}

@media (max-width: 1024px) {
  .forget-content {
    grid-template-columns: 1fr;
  }

  .forget-left {
    display: none;
  }

  .forget-right {
    padding: 2rem;
  }

  .forget-box {
    max-width: 100%;
  }
}

@media (max-width: 640px) {
  .forget-right {
    padding: 1.5rem;
  }

  .forget-title {
    font-size: 1.75rem;
  }
}
</style>
