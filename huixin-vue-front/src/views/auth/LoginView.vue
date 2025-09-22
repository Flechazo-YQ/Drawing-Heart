<template>
  <div class="login-container">

    <!-- 统一导航栏 -->
    <NavBarGuest />

    <div class="login-content">
      <div class="login-left">
        <div class="brand-content">
          <div class="brand-logo">
            <h1>绘心同学</h1>
            <p class="brand-subtitle">AI心理绘画治疗平台</p>
          </div>
          <div class="hero-image">
            <img src="@/assets/images/others/Heart.png" alt="心理诊断" />
          </div>
        </div>
      </div>

      <div class="login-right">
        <div class="login-box">
          <h2 class="login-title">欢迎回来</h2>
          <p class="login-subtitle">请登录您的账户继续使用服务</p>

          <form class="login-form" @submit.prevent="handleLogin">
            <div class="form-group">
              <label>用户名 / 邮箱</label>
              <input
                v-model="formData.usernameOrEmail"
                type="text"
                class="form-input"
                placeholder="请输入用户名或邮箱"
                required
              />
            </div>

            <div class="form-group">
              <label>密码</label>
              <input
                v-model="formData.password"
                type="password"
                class="form-input"
                placeholder="请输入密码"
                required
              />
            </div>

            <div class="form-options">
              <label class="remember-me">
                <input type="checkbox" v-model="formData.remember" />
                <span>记住我</span>
              </label>
              <router-link to="/forget" class="forgot-link">忘记密码？</router-link>
            </div>

            <button type="submit" class="login-button" :disabled="isLoading">
              {{ isLoading ? '登录中...' : '登录' }}
            </button>

            <p class="register-hint">
              还没有账号？
              <router-link to="/register" class="register-link">立即注册</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config' // 导入配置文件
import NavBarGuest from '@/components/NavBarGuest.vue'
import socket from '@/utils/network'

const router = useRouter()
const route = useRoute()
const isLoading = ref(false)

const formData = reactive({
  usernameOrEmail: '',
  password: '',
  remember: false
})

const handleLogin = async () => {
  try {
    isLoading.value = true

    // 添加请求超时控制
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.requestTimeout || 30000);

    try {
      const response = await fetch(`${config.baseURL}${config.loginPath}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          username: formData.usernameOrEmail,
          password: formData.password
        }),
        signal: controller.signal
      })

      clearTimeout(timeout);

      // 检查是否能获取到JSON响应
      let data;
      try {
        data = await response.json()
      } catch (e) {
        throw new Error('服务器返回了无效的数据格式')
      }

      if (data.code === 0) {
        // 登录成功，保存token到localStorage
        localStorage.setItem('token', data.token)

        // 获取用户信息
        try {
          const userInfoResponse = await fetch(`${config.baseURL}${config.userInfoPath}`, {
            headers: {
              'Authorization': data.token
            }
          });

          const userInfo = await userInfoResponse.json();

          if (userInfo.code === 0) {
            const info = { ...userInfo.data, id: userInfo.data._id }

            localStorage.setItem('userInfo', JSON.stringify(info));

            // 添加登录状态标志到localStorage
            localStorage.setItem('isLoggedIn', 'true')

            //向后端发送登录用户id
            if (!socket.connected) {
              socket.connect();
              socket.once('connect', () => {
                socket.emit('user_auth', { token: data.token });
              });
            } else {
              socket.emit('user_auth', { token: data.token });
            }

            // 如果选择了"记住我"，保存用户名
            if (formData.remember) {
              localStorage.setItem('rememberLogin', 'true')
              localStorage.setItem('savedUsername', formData.usernameOrEmail)
            } else {
              localStorage.removeItem('rememberLogin')
              localStorage.removeItem('savedUsername')
            }

            // 清除用户的聊天记录和状态
            await clearChatHistory(userInfo.data.id);
          } else {
            throw new Error('获取用户信息失败');
          }
        } catch (userInfoError) {
          console.error('获取用户信息错误:', userInfoError);
          ElMessage.error('登录成功但获取用户信息失败，请刷新页面重试');
        }

        // 设置最新登录时间戳，用于在聊天页面检测是否刚登录
        localStorage.setItem('lastLoginTimestamp', new Date().getTime().toString());

        router.push('/') // 登录成功后跳转到首页
      } else {
        ElMessage.error(data.message || '登录失败')
      }
    } catch (fetchError) {
      clearTimeout(timeout);
      if (fetchError.name === 'AbortError') {
        throw new Error('请求超时，请检查网络连接')
      } else {
        throw fetchError;
      }
    }
  } catch (error) {
    console.error('登录错误:', error)
    ElMessage.error(error.message || '登录失败，请检查网络连接')
  } finally {
    isLoading.value = false
  }
}

// 清除聊天历史记录和状态的函数
const clearChatHistory = async (userId) => {
  if (!userId) return;

  // 清除与聊天相关的所有localStorage条目
  localStorage.removeItem(`chatMessages_${userId}`);
  localStorage.removeItem(`isAdminMode_${userId}`);
  localStorage.removeItem(`lastChatTimestamp_${userId}`);

  // 清除可能存在的其他聊天相关状态
  localStorage.removeItem('text_result');
  localStorage.removeItem('current_context');

  // 调用后端API清除服务器端的聊天上下文
  try {
    const token = localStorage.getItem('token');
    if (token) {
      await fetch(`${config.baseURL}/api/clear/chats/context`, {
        method: 'POST',
        headers: {
          'Authorization': token,
          'Content-Type': 'application/json'
        }
      });
      console.log('服务器聊天上下文已清除');
    }
  } catch (error) {
    console.error('清除服务器聊天上下文失败:', error);
    // 忽略错误，不影响主要登录流程
  }
}

// 页面加载时检查是否有记住的登录信息
onMounted(() => {
  if (localStorage.getItem('rememberLogin') === 'true') {
    const savedUsername = localStorage.getItem('savedUsername')
    if (savedUsername) {
      formData.usernameOrEmail = savedUsername
      formData.remember = true
    }
  }
})
</script>

<style scoped>
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
  transform: translateY(-1px);
}

.nav-link.active {
  color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
  font-weight: 600;
}

.login-container {
  height: 80%;
  min-height: 100vh;
  background-color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 64px; /* 为导航栏留出空间 */
}

.login-content {
  width: 100%;
  max-width: var(--container-max-width, 1440px);
  margin: 0 auto;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.login-left {
  height: 92%;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  cursor: default; /* 默认光标，不显示可点击状态 */
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

.login-right {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  padding: 4rem;
  margin-top: -10%;
  display: flex;
  align-items: center;
  justify-content: center;
  height:100%;
}

.login-box {
  width: 100%;
  max-width: 450px;
  /* 移除固定高度比例和绝对定位，改为更灵活的布局 */
  padding: 2rem;
}

.login-title {
  font-size: 1.75rem;
  color: #1a1a1a;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.login-subtitle {
  color: #6b7280;
  margin: 0 0 1.5rem 0;
  font-size: 0.9rem;
}

.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.form-group {
  margin-bottom: 1rem;
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #4b5563;
  font-size: 0.75rem;
  cursor: pointer;
}

.forgot-link {
  color: #42b983;
  text-decoration: none;
  font-size: 0.75rem;
  transition: color 0.2s;
}

.login-button {
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

.login-button:hover {
  background: #3aa876;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

.register-hint {
  text-align: center;
  margin-top: 1rem;
  color: #6b7280;
  font-size: 0.75rem;
}

.register-link {
  color: #42b983;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.register-link:hover {
  color: #3aa876;
}

@media (max-width: 1024px) {
  .login-content {
    grid-template-columns: 1fr;
  }

  .login-left {
    display: none;
  }

  .login-right {
    padding: 2rem;
  }

  .login-box {
    max-width: 100%;
  }
}

/* 2K分辨率优化 */
@media (min-width: 2560px) {
  .login-left {
    padding: 6rem;
  }

  .login-right {
    padding: 6rem 4rem;
  }

  .login-title {
    font-size: 2.5rem;
  }

  .login-subtitle {
    font-size: 1.2rem;
  }

  .brand-logo h1 {
    font-size: 3rem;
  }

  .brand-subtitle {
    font-size: 1.3rem;
  }

  .form-input {
    padding: 1rem;
    font-size: 1.1rem;
  }

  .login-button {
    padding: 1rem;
    font-size: 1.2rem;
  }
}

/* 4K分辨率优化 */
@media (min-width: 3840px) {
  .login-left {
    padding: 8rem;
  }

  .login-right {
    padding: 8rem 6rem;
  }

  .login-box {
    max-width: 600px;
  }

  .login-title {
    font-size: 3rem;
    margin-bottom: 1.5rem;
  }

  .login-subtitle {
    font-size: 1.4rem;
    margin-bottom: 3rem;
  }

  .brand-logo h1 {
    font-size: 4rem;
  }

  .brand-subtitle {
    font-size: 1.6rem;
  }

  .form-input {
    padding: 1.25rem;
    font-size: 1.3rem;
    border-radius: 12px;
  }

  .login-button {
    padding: 1.25rem;
    font-size: 1.4rem;
    border-radius: 12px;
  }

  .form-group {
    margin-bottom: 2rem;
  }

  .form-group label {
    font-size: 1.2rem;
    margin-bottom: 0.75rem;
  }

  .form-options {
    margin: 2rem 0;
  }

  .remember-me, .forgot-link {
    font-size: 1.1rem;
  }
}

@media (max-width: 640px) {
  .login-container {
    padding: 1rem;
  }

  .login-right {
    padding: 1rem;
  }

  .login-box {
    padding: 1rem;
  }

  .login-title {
    font-size: 1.5rem;
  }

  .login-subtitle {
    font-size: 0.85rem;
    margin-bottom: 1rem;
  }

  .form-group {
    margin-bottom: 0.75rem;
  }
}

/* 添加触屏设备特定样式 */
@media (hover: none) {
  .login-button {
    padding: 0.75rem;
    font-size: 1rem;
  }

  .form-input {
    padding: 0.6rem 0.75rem;
    font-size: 1rem;
  }
}
</style>
