<template>
  <div class="register-container">
<<<<<<< HEAD
    <div class="register-content">
      <div class="register-left">
        <div class="brand-content">
          <router-link to="/" class="brand-logo">
            <h1>绘心同学</h1>
            <p class="brand-subtitle">AI心理绘画治疗平台</p>
          </router-link>
=======
    <!-- 统一导航栏 -->
    <nav class="modern-nav">
      <div class="nav-content">
        <div class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </div>
        <div class="nav-actions">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/login" class="nav-link">登录</router-link>
          <router-link to="/register" class="nav-link active">注册</router-link>
        </div>
      </div>
    </nav>

    <div class="register-content">
      <div class="register-left">
        <div class="brand-content">
          <div class="brand-logo">
            <h1>绘心同学</h1>
            <p class="brand-subtitle">AI心理绘画治疗平台</p>
          </div>
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
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
<<<<<<< HEAD
              <input v-model="formData.email" type="email" class="form-input" placeholder="请输入邮箱地址" required />
=======
              <input v-model="formData.email" type="email" class="form-input"
                     :class="{ 'error': emailError }"
                     placeholder="请输入邮箱地址"
                     @blur="validateEmail"
                     @input="clearEmailError"
                     required />
              <div v-if="emailError" class="error-message">{{ emailError }}</div>
            </div>

            <div class="form-group">
              <label>邮箱验证码</label>
              <div class="verification-code-group">
                <input v-model="formData.code" type="text" class="form-input" placeholder="请输入4位验证码" required />
                <button @click.prevent="sendCode" :disabled="isSendingCode || countdown > 0" class="send-code-button">
                  {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
                </button>
              </div>
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
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
import config from '@/config'
// 导入我们新创建的 API 客户端
import apiClient from '@/api'

const router = useRouter()
const isLoading = ref(false)
<<<<<<< HEAD
=======
const isSendingCode = ref(false)
const countdown = ref(0)
const emailError = ref('')
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false,
<<<<<<< HEAD
  gender: ''
})

const handleRegister = async () => {
  // 表单验证 (保持不变)
=======
  gender: '',
  code: ''
})

// 邮箱验证函数
const validateEmail = () => {
  const email = formData.email.trim()

  if (!email) {
    emailError.value = ''
    return false
  }

  // 检查@符号的存在和位置
  const atIndex = email.indexOf('@')
  if (atIndex === -1) {
    emailError.value = '您的邮箱填写不规范'
    return false
  }

  if (atIndex === 0) {
    emailError.value = '您的邮箱填写不规范'
    return false
  }

  if (atIndex === email.length - 1) {
    emailError.value = '您的邮箱填写不规范'
    return false
  }

  const localPart = email.substring(0, atIndex)
  const domainPart = email.substring(atIndex + 1)

  // 验证本地部分（@前面的部分）
  if (!validateLocalPart(localPart)) {
    return false
  }

  // 验证域名部分（@后面的部分）
  if (!validateDomainPart(domainPart)) {
    emailError.value = '您的邮箱填写不规范'
    return false
  }

  emailError.value = ''
  return true
}

// 验证邮箱本地部分（@符号前）
const validateLocalPart = (localPart) => {
  // 检查长度限制（最多64个字符）
  if (localPart.length > 64) {
    emailError.value = '您的邮箱填写不规范'
    return false
  }

  // 检查是否为空
  if (localPart.length === 0) {
    emailError.value = '您的邮箱填写不规范'
    return false
  }

  // 检查开头和结尾不能是句点
  if (localPart.startsWith('.') || localPart.endsWith('.')) {
    emailError.value = '您的邮箱填写不规范'
    return false
  }

  // 检查连续的句点
  if (localPart.includes('..')) {
    emailError.value = '您的邮箱填写不规范'
    return false
  }

  // 检查是否被引号包围
  const isQuoted = localPart.startsWith('"') && localPart.endsWith('"')

  if (isQuoted) {
    // 被引号包围的情况，检查引号内的内容
    const quotedContent = localPart.slice(1, -1)
    // 被引号包围时，大部分字符都是允许的，包括空格
    return true
  } else {
    // 未被引号包围的情况，检查字符合法性
    const allowedChars = /^[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~.]+$/

    if (!allowedChars.test(localPart)) {
      // 检查是否包含非法字符
      const illegalChars = /["\s()<>,;:@\\]/
      if (illegalChars.test(localPart)) {
        emailError.value = '您的邮箱包含非法字符'
        return false
      } else {
        emailError.value = '您的邮箱填写不规范'
        return false
      }
    }
  }

  return true
}

// 验证邮箱域名部分（@符号后）
const validateDomainPart = (domainPart) => {
  // 基本域名格式检查
  const domainRegex = /^[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)*$/

  if (!domainRegex.test(domainPart)) {
    return false
  }

  // 检查是否包含至少一个点号
  if (!domainPart.includes('.')) {
    return false
  }

  return true
}

// 清除邮箱错误信息
const clearEmailError = () => {
  if (emailError.value) {
    emailError.value = ''
  }
}

const sendCode = async () => {
  if (!formData.email) {
    ElMessage.error('请输入电子邮箱地址')
    return
  }

  // 发送验证码前先验证邮箱格式
  if (!validateEmail()) {
    return
  }

  isSendingCode.value = true
  try {
    await apiClient.post(config.sendCodePath, { email: formData.email })
    ElMessage.success('验证码已发送，请注意查收')
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    // 错误已由 apiClient 拦截器处理
  } finally {
    isSendingCode.value = false
  }
}

const handleRegister = async () => {
  // 表单验证
  if (!validateEmail()) {
    return
  }

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
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

    // 使用新的 apiClient 发送请求
    const data = await apiClient.post(config.registerPath, {
      username: formData.username,
      password: formData.password,
      email: formData.email,
<<<<<<< HEAD
      gender: formData.gender
=======
      gender: formData.gender,
      code: formData.code
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
    })

    console.log('服务器响应：', data)

    if (data.code === 0) {
      ElMessage.success('注册成功!')
      router.push('/login')
    } else {
      // 错误处理现在由 apiClient 的拦截器统一处理，
      // 但如果需要，这里仍然可以根据 code 进行特定的业务逻辑处理
      // ElMessage.error(data.message || '注册失败，请检查输入信息')
    }
  } catch (error) {
    // 由于 apiClient 中有统一的错误处理和提示，
    // 这里的 catch 块主要用于防止未捕获的 Promise 错误，
    // 或者进行一些组件级别的特定失败处理（比如重置表单状态）。
    console.error('注册组件捕获到错误：', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
<<<<<<< HEAD
=======
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

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
.register-container {
  min-height: 100vh;
  background-color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
<<<<<<< HEAD
=======
  padding-top: 64px; /* 为导航栏留出空间 */
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
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
<<<<<<< HEAD
  text-decoration: none;
=======
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
<<<<<<< HEAD
=======
  cursor: default; /* 默认光标，不显示可点击状态 */
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
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

<<<<<<< HEAD
=======
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

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
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

<<<<<<< HEAD
=======
.form-input.error {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error-message {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  margin-bottom: 0;
}

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
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
