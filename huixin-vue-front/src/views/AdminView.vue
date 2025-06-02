<template>
  <div class="admin-container">
    <div class="admin-header">
      <div class="logo">
        <router-link to="/" class="nav-logo">绘心同学</router-link>
      </div>
      <div class="admin-title">管理员系统</div>
      <div class="admin-actions">
        <button @click="logout" class="logout-btn">退出登录</button>
      </div>
    </div>

    <div class="admin-content">
      <div class="admin-sidebar">
        <div class="alert-list">
          <h3>危险对话提醒</h3>
          <div v-if="dangerousUsers.length === 0" class="no-alerts">
            暂无危险对话
          </div>
          <div 
            v-for="user in dangerousUsers" 
            :key="user.userId"
            class="alert-item"
            :class="{ active: currentUserId === user.userId }"
            @click="selectUser(user.userId)"
          >
            <div class="alert-info">
              <div class="alert-user">用户: {{ user.username }}</div>
              <div class="alert-time">{{ user.time }}</div>
            </div>
            <div class="alert-preview">{{ user.lastMessage }}</div>
          </div>
        </div>
      </div>

      <div class="admin-main">
        <div v-if="!currentUserId" class="no-selection">
          <div class="empty-state">
            <div class="empty-icon">👨‍💼</div>
            <h2>请选择一个用户进行人工干预</h2>
            <p>当AI检测到危险对话时，用户将出现在左侧列表中</p>
          </div>
        </div>

        <div v-else class="chat-container">
          <div class="chat-header">
            <h3>正在与用户 {{ currentUser ? currentUser.username : '' }} 对话</h3>
          </div>
          
          <div class="chat-history" ref="chatHistory">
            <div 
              v-for="(msg, index) in currentChat" 
              :key="index"
              class="chat-message"
              :class="{ 'user-message': msg.role === 'user', 'admin-message': msg.role === 'admin', 'ai-message': msg.role === 'assistant' }"
            >
              <div class="message-content">
                <div class="message-sender">{{ getSenderLabel(msg.role) }}</div>
                <div class="message-text">{{ msg.content }}</div>
                <div class="message-time">{{ msg.time }}</div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <textarea 
              v-model="messageInput" 
              placeholder="输入回复内容..." 
              @keyup.enter.ctrl="sendMessage"
              class="input-area"
            ></textarea>
            <button @click="sendMessage" :disabled="!messageInput.trim()" class="send-btn">
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import io from 'socket.io-client'
import config from '@/config' // 导入配置文件

const router = useRouter()
const dangerousUsers = ref([])
const currentUserId = ref(null)
const currentChat = ref([])
const messageInput = ref('')
const chatHistory = ref(null)
let socket = null

// 模拟数据 - 实际应用中从WebSocket获取
onMounted(() => {
  // 初始化WebSocket
  initWebSocket()
  
  // 检查管理员登录状态
  if (!localStorage.getItem('isAdminLoggedIn')) {
    router.push('/admin-login')
    return
  }
})

const initWebSocket = () => {
  // 使用配置文件中的socketUrl或当前域名
  const socketUrl = config.socketUrl || config.baseURL || `${window.location.protocol}//${window.location.host}`
  
  try {
    socket = io(socketUrl, {
      withCredentials: false,
      transports: ['websocket']
    })
    
    socket.on('connect', () => {
      console.log('SocketIO连接已建立')
      // 发送管理员身份验证信息
      socket.emit('admin_auth', {
        token: localStorage.getItem('adminToken')
      })
    })
    
    socket.on('auth_response', (data) => {
      if (data.status === 'error') {
        ElMessage.error(data.message || '身份验证失败')
        router.push('/admin-login')
      } else {
        console.log('管理员身份验证成功')
      }
    })
    
    socket.on('dangerous_chats_list', (data) => {
      dangerousUsers.value = data.chats.map(chat => ({
        ...chat,
        time: formatTime(new Date())
      }))
    })
    
    socket.on('chat_history', (data) => {
      currentChat.value = data.messages
      scrollToBottom()
    })
    
    socket.on('new_message', (data) => {
      if (data.userId === currentUserId.value) {
        currentChat.value.push({
          role: data.role,
          content: data.content,
          time: formatTime(new Date())
        })
        scrollToBottom()
      }
      // 更新侧边栏中的最后一条消息
      updateUserLastMessage(data.userId, data.content)
    })
    
    socket.on('disconnect', () => {
      console.log('SocketIO连接已关闭')
      // 可以添加重连逻辑
      setTimeout(() => {
        if (localStorage.getItem('isAdminLoggedIn')) {
          initWebSocket()
        }
      }, 3000)
    })
    
    socket.on('error', (error) => {
      console.error('SocketIO错误:', error)
      ElMessage.error(error.message || '连接服务器失败，请检查网络或刷新页面')
    })
  } catch (error) {
    console.error('初始化SocketIO失败:', error)
    ElMessage.error('无法连接到服务器，请刷新页面重试')
  }
}

const addDangerousUser = (user) => {
  // 检查是否已存在该用户
  const existingIndex = dangerousUsers.value.findIndex(u => u.userId === user.userId)
  if (existingIndex >= 0) {
    // 更新已有用户信息
    dangerousUsers.value[existingIndex] = {
      ...user,
      time: formatTime(new Date())
    }
  } else {
    // 添加新用户
    dangerousUsers.value.push({
      ...user,
      time: formatTime(new Date())
    })
  }
}

const updateUserLastMessage = (userId, message) => {
  const index = dangerousUsers.value.findIndex(u => u.userId === userId)
  if (index >= 0) {
    dangerousUsers.value[index].lastMessage = message
    dangerousUsers.value[index].time = formatTime(new Date())
  }
}

const selectUser = (userId) => {
  currentUserId.value = userId
  
  // 通过SocketIO请求对话历史
  if (socket && socket.connected) {
    socket.emit('request_history', {
      userId: userId
    })
  } else {
    ElMessage.error('服务器连接已断开，请刷新页面')
  }
}

const sendMessage = () => {
  if (!messageInput.value.trim() || !currentUserId.value) return
  
  // 生成唯一的消息ID
  const messageId = Date.now().toString() + '-' + Math.random().toString(36).substr(2, 9)
  
  // 发送消息到服务器
  if (socket && socket.connected) {
    socket.emit('admin_message', {
      userId: currentUserId.value,
      content: messageInput.value,
      messageId: messageId
    })
    
    // 不在这里添加到本地聊天记录，而是由socket.on('new_message')事件处理
    // 清空输入框
    messageInput.value = ''
  } else {
    ElMessage.error('服务器连接已断开，请刷新页面')
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatHistory.value) {
    chatHistory.value.scrollTop = chatHistory.value.scrollHeight
  }
}

const formatTime = (date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

const getSenderLabel = (role) => {
  switch (role) {
    case 'user': return '用户'
    case 'assistant': return 'AI助手'
    case 'admin': return '管理员'
    default: return role
  }
}

const currentUser = computed(() => {
  return dangerousUsers.value.find(user => user.userId === currentUserId.value)
})

const logout = () => {
  // 断开SocketIO连接
  if (socket) {
    socket.disconnect()
  }
  
  // 清除管理员登录状态
  localStorage.removeItem('isAdminLoggedIn')
  localStorage.removeItem('adminToken')
  
  // 跳转到管理员登录页
  router.push('/admin-login')
}

// 监听路由变化，在离开页面时关闭SocketIO连接
watch(() => router.currentRoute.value.path, (newPath) => {
  if (!newPath.includes('admin') && socket) {
    socket.disconnect()
  }
})

// 组件销毁时清理资源
onMounted(() => {
  return () => {
    if (socket) {
      socket.disconnect()
    }
  }
})
</script>

<style scoped>
.admin-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-logo {
  font-size: 1.25rem;
  font-weight: 600;
  color: #42b983;
  text-decoration: none;
}

.admin-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background-color: #f1f5f9;
  border: none;
  border-radius: 4px;
  color: #64748b;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.logout-btn:hover {
  background-color: #e2e8f0;
  color: #475569;
}

.admin-content {
  display: flex;
  flex: 1;
  height: calc(100vh - 64px);
  overflow: hidden;
}

.admin-sidebar {
  width: 300px;
  background-color: #f8f9fa;
  border-right: 1px solid #e9ecef;
  overflow-y: auto;
}

.alert-list {
  padding: 1rem;
}

.alert-list h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.no-alerts {
  text-align: center;
  padding: 2rem 0;
  color: #9ca3af;
}

.alert-item {
  padding: 0.75rem;
  border-radius: 8px;
  background-color: #ffffff;
  margin-bottom: 0.75rem;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.alert-item:hover {
  background-color: #f3f4f6;
}

.alert-item.active {
  background-color: #ecfdf5;
  border-left: 3px solid #42b983;
}

.alert-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.alert-user {
  font-weight: 500;
  color: #1f2937;
}

.alert-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.alert-preview {
  font-size: 0.875rem;
  color: #4b5563;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
}

.no-selection {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #f9fafb;
}

.empty-state {
  text-align: center;
  max-width: 400px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6b7280;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.chat-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.chat-history {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.chat-message {
  margin-bottom: 1rem;
  max-width: 80%;
}

.user-message {
  align-self: flex-end;
}

.admin-message {
  align-self: flex-start;
}

.ai-message {
  align-self: flex-start;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  position: relative;
}

.user-message .message-content {
  background-color: #ecfdf5;
  border: 1px solid #d1fae5;
}

.admin-message .message-content {
  background-color: #eff6ff;
  border: 1px solid #dbeafe;
}

.ai-message .message-content {
  background-color: #f3f4f6;
  border: 1px solid #e5e7eb;
}

.message-sender {
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.user-message .message-sender {
  color: #065f46;
}

.admin-message .message-sender {
  color: #1e40af;
}

.ai-message .message-sender {
  color: #4b5563;
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.message-time {
  font-size: 0.7rem;
  color: #9ca3af;
  margin-top: 0.25rem;
  text-align: right;
}

.chat-input {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 0.5rem;
}

.input-area {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  resize: none;
  min-height: 60px;
  font-family: inherit;
}

.input-area:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.send-btn {
  align-self: flex-end;
  padding: 0.5rem 1rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  height: 40px;
}

.send-btn:hover {
  background-color: #3aa876;
}

.send-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .admin-container {
    flex-direction: column;
  }
  
  .admin-content {
    flex-direction: column;
    height: auto;
  }
  
  .admin-sidebar {
    width: 100%;
    height: 250px;
  }
  
  .admin-main {
    flex: none;
    height: calc(100vh - 64px - 250px);
  }
}
</style>