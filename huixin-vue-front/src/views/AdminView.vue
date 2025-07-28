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
            <button 
              @click.stop="deleteUserChat(user.userId)" 
              class="delete-chat-btn" 
              title="删除对话记录"
            >
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 6h18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c0-1 1-2 2-2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
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
              <img :src="getAvatarSrc(msg.role)" :class="['avatar', msg.role]" :alt="getAvatarAlt(msg.role)" />
              <div class="message-content">
                <div class="message-sender">{{ getSenderLabel(msg.role) }}</div>
                <div class="message-text">{{ msg.content }}</div>
                <div class="message-time">{{ formatTime(msg.time) }}</div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <div class="input-wrapper">
              <textarea 
                v-model="messageInput" 
                ref="adminTextarea"
                placeholder="回复用户消息，Enter发送，Shift+Enter换行..." 
                @keydown="handleKeyDown"
                @input="handleInput"
                class="input-area"
                :maxlength="500"
                rows="1"
              ></textarea>
              <div class="input-footer">
                <span class="char-count" :class="{ 'warning': messageInput.length > 400 }">
                  {{ messageInput.length }}/500
                </span>
                <div class="input-actions">
                  <button 
                    @click="sendMessage" 
                    :disabled="!messageInput.trim()" 
                    class="send-button"
                    title="发送消息 (Enter)"
                  >
                    <svg class="send-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import io from 'socket.io-client'
import config from '@/config' // 导入配置文件
import robotAvatar from '@/assets/images/绘制机器人 AI 头像.png'
import boyAvatar from '@/assets/images/boy.png'
import girlAvatar from '@/assets/images/girl.png'
import adminAvatar from '@/assets/images/admin.png'

const router = useRouter()
const dangerousUsers = ref([])
const currentUserId = ref(null)
const currentChat = ref([])
const messageInput = ref('')
const chatHistory = ref(null)
let socket = null

// 模拟数据 - 实际应用中从WebSocket获取
onMounted(() => {
  // 添加页面类名以便CSS样式正确应用
  document.body.classList.add('admin-page')
  
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

// 新增的输入处理方法
const adminTextarea = ref(null)

// 处理键盘事件
const handleKeyDown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 处理输入变化，自动调整高度
const handleInput = () => {
  if (adminTextarea.value) {
    // 重置高度
    adminTextarea.value.style.height = 'auto'
    // 设置新高度，最大3行
    const scrollHeight = adminTextarea.value.scrollHeight
    const maxHeight = 72 // 3行的大概高度
    adminTextarea.value.style.height = Math.min(scrollHeight, maxHeight) + 'px'
  }
}

const deleteUserChat = (userId) => {
  // 确认删除
  if (confirm('确定要删除这个用户的对话记录吗？此操作不可撤销。')) {
    // 发送删除请求到服务器
    if (socket && socket.connected) {
      socket.emit('delete_user_chat', {
        userId: userId
      })
      
      // 从本地列表中移除
      const index = dangerousUsers.value.findIndex(u => u.userId === userId)
      if (index >= 0) {
        dangerousUsers.value.splice(index, 1)
      }
      
      // 如果删除的是当前选中的用户，清空聊天记录
      if (currentUserId.value === userId) {
        currentUserId.value = null
        currentChat.value = []
      }
      
      ElMessage.success('对话记录已删除')
    } else {
      ElMessage.error('服务器连接已断开，请刷新页面')
    }
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
    
    // 重置输入框高度
    if (adminTextarea.value) {
      adminTextarea.value.style.height = 'auto'
    }
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

const formatTime = (dateInput) => {
  if (!dateInput) return ''
  
  try {
    let date
    if (dateInput instanceof Date) {
      date = dateInput
    } else {
      date = new Date(dateInput)
    }
    
    // 检查是否为有效日期
    if (isNaN(date.getTime())) return String(dateInput)
    
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date)
  } catch (error) {
    return String(dateInput)
  }
}

const getSenderLabel = (role) => {
  switch (role) {
    case 'user': return '用户'
    case 'assistant': return 'AI助手'
    case 'admin': return '管理员'
    default: return role
  }
}

const getAvatarSrc = (role) => {
  switch (role) {
    case 'user':
      // 这里可以根据用户性别选择头像，暂时使用默认头像
      return boyAvatar
    case 'assistant':
      return robotAvatar
    case 'admin':
      return adminAvatar
    default:
      return robotAvatar
  }
}

const getAvatarAlt = (role) => {
  switch (role) {
    case 'user': return '用户头像'
    case 'assistant': return 'AI助手头像'
    case 'admin': return '管理员头像'
    default: return '头像'
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
onUnmounted(() => {
  // 移除页面类名
  document.body.classList.remove('admin-page')
  
  if (socket) {
    socket.disconnect()
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
  position: relative;
}

.alert-item:hover {
  background-color: #f3f4f6;
}

.alert-item:hover .delete-chat-btn {
  opacity: 1;
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
  padding-right: 36px; /* 为删除按钮留出空间 */
}

.delete-chat-btn {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s ease;
  font-size: 12px;
}

.delete-chat-btn:hover {
  background: #dc2626;
  transform: scale(1.05);
}

.delete-chat-btn svg {
  width: 14px;
  height: 14px;
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  overflow: hidden; /* 确保内容不会溢出 */
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
  max-width: 1200px; /* 设置最大宽度 */
  margin: 0 auto; /* 居中对齐 */
  width: 100%;
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
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  scroll-behavior: smooth;
  width: 100%;
  box-sizing: border-box;
}

.chat-message {
  margin-bottom: 20px;
  max-width: 75%;
  opacity: 0;
  animation: fadeIn 0.4s ease-out forwards;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.user-message {
  flex-direction: row;
  align-self: flex-start;
}

.admin-message {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.ai-message {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.message-content {
  padding: 16px 20px;
  border-radius: 18px;
  position: relative;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  font-size: 14px;
  line-height: 1.6;
  max-width: 100%;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: keep-all;
  overflow-wrap: break-word;
  hyphens: none;
}

.user-message .message-content {
  background: white;
  color: #374151;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 6px;
  margin-left: 12px;
}

.admin-message .message-content {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-bottom-right-radius: 6px;
  margin-right: 12px;
}

.ai-message .message-content {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border-bottom-right-radius: 6px;
  margin-right: 12px;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.avatar:hover {
  transform: scale(1.05);
}

.avatar.assistant, .avatar.admin {
  border: 2px solid #007AFF;
}

.avatar.user {
  border: 2px solid #10b981;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-sender {
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 8px;
  opacity: 0.9;
}

.user-message .message-sender {
  color: #6b7280;
}

.admin-message .message-sender {
  color: rgba(255, 255, 255, 0.8);
}

.ai-message .message-sender {
  color: rgba(255, 255, 255, 0.8);
}

.message-text {
  white-space: pre-wrap;
  word-break: keep-all;
  margin-bottom: 8px;
}

.message-time {
  font-size: 10px;
  margin-top: 4px;
  text-align: right;
  opacity: 0.7;
}

.user-message .message-time {
  color: #9ca3af;
}

.admin-message .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.ai-message .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.chat-input {
  background: white;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  border-radius: 0 0 16px 16px;
  width: 100%;
  box-sizing: border-box;
}

.input-wrapper {
  width: 100%;
}

.input-wrapper .input-area {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  outline: none;
  transition: all 0.3s ease;
  resize: none;
  font-family: inherit;
  background: #fafafa;
  min-height: 24px;
  max-height: 72px;
  overflow-y: auto;
}

.input-wrapper .input-area:focus {
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.input-wrapper .input-area:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
  border-color: #d1d5db;
}

.input-wrapper .input-area::placeholder {
  color: #9ca3af;
  opacity: 1;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding: 0 4px;
}

.char-count {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  transition: color 0.2s;
}

.char-count.warning {
  color: #f59e0b;
}

.input-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.send-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
}

.send-button:active:not(:disabled) {
  transform: translateY(-1px);
}

.send-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.send-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.2s ease;
}

.send-button:hover:not(:disabled) .send-icon {
  transform: scale(1.1);
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
  
  .chat-input {
    padding: 12px;
  }
  
  .input-wrapper .input-area {
    padding: 12px 16px;
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  .send-button {
    width: 40px;
    height: 40px;
  }
  
  .send-icon {
    width: 18px;
    height: 18px;
  }
  
  .message-content {
    max-width: 85%;
    padding: 12px 16px;
    font-size: 13px;
  }
  
  .chat-history {
    padding: 16px;
  }
  
  .char-count {
    font-size: 11px;
  }
}

/* 中等屏幕优化 (平板和小桌面) */
@media (min-width: 769px) and (max-width: 1024px) {
  .admin-container {
    padding: 0;
  }
  
  .admin-content {
    flex-direction: column;
    height: calc(100vh - 80px);
  }
  
  .admin-sidebar {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .admin-main {
    flex: 1;
    padding: 20px;
  }
  
  .message-content {
    max-width: 85%;
    font-size: 15px;
    padding: 14px 18px;
  }
  
  .chat-message {
    max-width: 90%;
  }
  
  .input-area {
    font-size: 15px;
    padding: 14px 18px;
  }
  
  .send-button {
    width: 42px;
    height: 42px;
  }
}

/* 常规桌面屏幕优化 */
@media (min-width: 1025px) and (max-width: 1199px) {
  .admin-sidebar {
    width: 320px;
  }
  
  .admin-main {
    padding: 24px;
  }
  
  .message-content {
    max-width: 85%;
    font-size: 15px;
    padding: 15px 19px;
  }
  
  .chat-message {
    max-width: 90%;
  }
  
  .input-area {
    font-size: 15px;
    padding: 15px 19px;
  }
  
  .send-button {
    width: 43px;
    height: 43px;
  }
}

/* 宽屏幕优化 - 确保在宽屏幕上充分利用空间 */
@media (min-width: 1200px) {
  .admin-container {
    max-width: none; /* 移除任何可能的宽度限制 */
  }
  
  .admin-sidebar {
    width: 350px; /* 在宽屏幕上稍微增加侧边栏宽度 */
  }
  
  .chat-container {
    max-width: 1200px; /* 聊天容器最大宽度 */
  }
  
  .message-content {
    max-width: 85%; /* 参考ChatView的成功设置，使用85% */
    line-height: 1.6;
    word-wrap: break-word;
    word-break: keep-all;
    overflow-wrap: break-word;
    hyphens: none;
  }
  
  .chat-message {
    max-width: 90%; /* 参考ChatView的成功设置，使用90% */
  }
}

/* 2K分辨率优化 */
@media (min-width: 2560px) {
  .admin-header {
    padding: 1.5rem 3rem;
  }
  
  .admin-title {
    font-size: 1.8rem;
  }
  
  .nav-logo {
    font-size: 1.5rem;
  }
  
  .admin-sidebar {
    width: 400px;
  }
  
  .alert-list {
    padding: 1.5rem;
  }
  
  .alert-list h3 {
    font-size: 1.2rem;
  }
  
  .chat-container {
    max-width: 1400px; /* 2K屏幕下稍微增加聊天容器宽度 */
  }
  
  .message-content {
    max-width: 85%; /* 保持与1200px设置一致的85% */
    font-size: 1.1rem;
    padding: 16px 20px;
    line-height: 1.7;
    word-wrap: break-word;
    word-break: keep-all;
    overflow-wrap: break-word;
    hyphens: none;
  }
  
  .chat-message {
    max-width: 90%; /* 保持与1200px设置一致的90% */
  }
  
  .input-area {
    font-size: 1.1rem;
    padding: 16px 20px;
  }
}

/* 4K分辨率优化 */
@media (min-width: 3840px) {
  .admin-header {
    padding: 2rem 4rem;
  }
  
  .admin-title {
    font-size: 2.2rem;
  }
  
  .nav-logo {
    font-size: 1.8rem;
  }
  
  .admin-sidebar {
    width: 500px;
  }
  
  .alert-list {
    padding: 2rem;
  }
  
  .alert-list h3 {
    font-size: 1.4rem;
  }
  
  .chat-container {
    max-width: 1600px; /* 4K屏幕下的最大聊天容器宽度 */
  }
  
  .message-content {
    max-width: 85%; /* 保持与较小屏幕一致的85% */
    font-size: 1.3rem;
    padding: 20px 24px;
    line-height: 1.8;
    word-wrap: break-word;
    word-break: keep-all;
    overflow-wrap: break-word;
    hyphens: none;
  }
  
  .chat-message {
    max-width: 90%; /* 保持与较小屏幕一致的90% */
  }
  
  .input-area {
    font-size: 1.3rem;
    padding: 20px 24px;
    min-height: 80px;
  }
  
  .send-button {
    width: 60px;
    height: 60px;
  }
  
  .send-icon {
    width: 28px;
    height: 28px;
  }
  
  .logout-btn {
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
  }
}
</style>