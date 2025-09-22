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
import socket from '@/utils/network'

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
      // 登录成功，获取管理员信息
      try {
        const adminInfoResponse = await fetch(`${config.baseURL}/api/admin/info`, {
          headers: {
            'Authorization': data.token
          }
        });

        const adminInfo = await adminInfoResponse.json();

        if (adminInfo.code === 0) {
          // 存储完整的管理员信息
          localStorage.setItem('adminInfo', JSON.stringify(adminInfo.data));
          localStorage.setItem('isAdminLoggedIn', 'true');
          localStorage.setItem('adminToken', data.token);

          if (socket && socket.connected) {
            socket.disconnect()
          }

          socket.io.opts.auth = { token: data.token };

          // 先解绑所有 connect 事件，防止重复注册
          socket.off('connect');

          socket.once('connect', () => {
            socket.emit('admin_auth', { token: data.token });
          });

          socket.connect();

          ElMessage.success('登录成功')
          router.push('/admin')
        } else {
          throw new Error('获取管理员信息失败');
        }
      } catch (adminInfoError) {
        console.error('获取管理员信息错误:', adminInfoError);
        ElMessage.error('登录成功但获取管理员信息失败，请刷新页面重试');

        // 即使获取信息失败，也允许进入管理页面
        localStorage.setItem('isAdminLoggedIn', 'true')
        localStorage.setItem('adminToken', data.token)
        localStorage.setItem('adminUsername', username.value)
        router.push('/admin')
      }
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
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f8fafc;
  padding: 20px;
  box-sizing: border-box;
}

.admin-login-box {
  width: 100%;
  max-width: 600px;
  min-width: 500px;
  padding: 3rem 2.5rem;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
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
  padding: 1rem 1.25rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #fafafa;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.login-button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1.5rem;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.login-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-login-container {
    padding: 16px;
  }

  .admin-login-box {
    padding: 2rem 1.5rem;
    min-width: 400px;
    max-width: 90vw;
  }

  .form-input {
    padding: 0.875rem 1rem;
    font-size: 16px; /* 防止iOS缩放 */
  }

  h1 {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }
}

@media (max-width: 480px) {
  .admin-login-container {
    padding: 12px;
  }

  .admin-login-box {
    padding: 1.5rem 1rem;
    min-width: 350px;
    max-width: 95vw;
  }
}
</style>
