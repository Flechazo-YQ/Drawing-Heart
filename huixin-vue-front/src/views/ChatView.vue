<template>
  <div class="chat-container">
    <!-- 统一导航栏 -->
    <nav class="modern-nav">
      <div class="nav-content">
        <div class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </div>
        <div class="nav-actions">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/draw" class="nav-link">绘画空间</router-link>
          <router-link to="/chat" class="nav-link active">心理对话</router-link>
          <router-link to="/user" class="nav-link">个人空间</router-link>
          <button class="nav-button logout-btn" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </nav>

    <!-- 聊天历史侧边栏 -->
    <ChatSidebar
      :isOpen="sidebarOpen"
      @close="sidebarOpen = false"
      @chatLoaded="handleChatLoaded"
      @newChat="handleNewChat"
    />

    <!-- 顶部工具栏 -->
    <div class="chat-header">
      <button class="sidebar-toggle-btn" @click="toggleSidebar">
        <span class="menu-icon">☰</span> 聊天历史
      </button>
      <div class="chat-title">{{ currentChatTitle }}</div>
      <div class="header-spacer"></div>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <!-- 空状态显示 -->
      <div v-if="messages.length === 0" class="empty-chat">
        <div class="empty-icon">💬</div>
        <h3>开始和绘心同学对话吧</h3>
        <p>分享您的想法和感受，我会用心倾听</p>
      </div>

      <!-- 消息列表 -->
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.type]">
        <img :src="getAvatarSrc(message.type)" :class="['avatar', message.type]"
          :alt="getAvatarAlt(message.type)" />
        <div class="message-content">
          {{ message.content }}
        </div>
      </div>
    </div>

    <div class="chat-input">
      <div class="input-wrapper">
        <textarea
          v-model="inputMessage"
          ref="inputTextarea"
          placeholder="在这里分享您的想法和感受，绘心同学正在倾听..."
          @keydown="handleKeyDown"
          @input="handleInput"
          :disabled="isLoading"
          :maxlength="500"
          rows="1"
        ></textarea>
        <div class="input-footer">
          <span class="char-count" :class="{ 'warning': inputMessage.length > 400 }">
            {{ inputMessage.length }}/500
          </span>
          <div class="input-actions">
            <button
              class="send-button"
              @click="(e: MouseEvent) => sendMessage()"
              :disabled="isLoading || !inputMessage.trim()"
              :title="isLoading ? '发送中...' : '发送消息 (Enter)'"
            >
              <span v-if="isLoading" class="loading-spinner"></span>
              <svg v-else class="send-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="adminTyping" class="typing-indicator">
      <span>管理员正在输入</span>
      <span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import robotAvatar from '@/assets/images/绘制机器人 AI 头像.png'
import boyAvatar from '@/assets/images/boy.png'
import girlAvatar from '@/assets/images/girl.png'
import adminAvatar from '@/assets/images/admin.png'
import { ElMessage } from 'element-plus'
import io from 'socket.io-client'
import config from '../config'
import ChatSidebar from '@/components/ChatSidebar.vue'

const router = useRouter()
const messages = ref<Array<{ type: 'user' | 'assistant' | 'admin', content: string, time?: string, messageId?: string }>>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 3
const userGender = ref<string>('')
const userAvatar = ref(boyAvatar) // 默认使用男性头像
const isAdminMode = ref(false)
const adminTyping = ref(false)
const processedMessageIds = ref<Set<string>>(new Set())

// 退出登录处理
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('isLoggedIn')
  router.push('/login')
}

// 新增的聊天历史相关变量
const sidebarOpen = ref(false)
const currentChatId = ref<string>('')
const currentChatTitle = ref<string>('新对话')

// 获取头像源
const getAvatarSrc = (type: string) => {
  switch (type) {
    case 'user': return userAvatar.value
    case 'assistant': return robotAvatar
    case 'admin': return adminAvatar // 管理员使用独立头像
    default: return robotAvatar
  }
}

// 获取头像alt文本
const getAvatarAlt = (type: string) => {
  switch (type) {
    case 'user': return '用户头像'
    case 'assistant': return 'AI助手头像'
    case 'admin': return '管理员头像' // 管理员使用独立的alt文本
    default: return '头像'
  }
}

// 切换侧边栏
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

// 处理聊天加载
const handleChatLoaded = async (chatId: string) => {
  currentChatId.value = chatId
  sidebarOpen.value = false

  // 加载聊天消息
  await loadChatMessages(chatId)
}

// 处理新建聊天
const handleNewChat = (chatId: string) => {
  currentChatId.value = chatId
  currentChatTitle.value = '新对话'
  messages.value = []
  sidebarOpen.value = false

  // 清除管理员模式
  isAdminMode.value = false
  processedMessageIds.value.clear()
}

// 加载聊天消息
const loadChatMessages = async (chatId: string) => {
  try {
    const token = localStorage.getItem('token')

    const response = await fetch(`${config.baseURL}/api/chats/${chatId}/messages`, {
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json'
      }
    })

    const result = await response.json()

    if (result.code === 0) {
      const chat = result.data.chat
      const messagesList = result.data.messages

      currentChatTitle.value = chat.title

      // 转换消息格式
      messages.value = messagesList.map((msg: any) => ({
        type: msg.sender === 'user' ? 'user' :
              msg.sender === 'assistant' ? 'assistant' : 'admin',
        content: msg.content,
        time: msg.timestamp,
        messageId: msg._id
      }))

      // 滚动到底部
      await nextTick()
      scrollToBottom()

    } else {
      ElMessage.error(result.message || '加载聊天消息失败')
    }
  } catch (error) {
    console.error('加载聊天消息失败:', error)
    ElMessage.error('加载聊天消息失败')
  }
}

// 保存聊天状态到localStorage
const saveChatState = () => {
  if (messages.value.length > 0) {
    try {
      // 获取用户ID
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      const userId = userInfo.id

      if (!userId) {
        console.error('保存聊天记录失败：找不到用户ID')
        return
      }

      // 使用用户ID作为标识保存聊天记录
      localStorage.setItem(`chatMessages_${userId}`, JSON.stringify(messages.value))
      localStorage.setItem(`isAdminMode_${userId}`, isAdminMode.value.toString())
      localStorage.setItem(`lastChatTimestamp_${userId}`, new Date().getTime().toString())
    } catch (error) {
      console.error('保存聊天记录时出错:', error)
    }
  }
}

// 从localStorage恢复聊天状态
const restoreChatState = () => {
  try {
    // 获取用户ID
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const userId = userInfo.id

    if (!userId) {
      console.error('恢复聊天记录失败：找不到用户ID')
      return false
    }

    const savedMessages = localStorage.getItem(`chatMessages_${userId}`)
    const savedAdminMode = localStorage.getItem(`isAdminMode_${userId}`)
    const lastTimestamp = localStorage.getItem(`lastChatTimestamp_${userId}`)

    // 如果有保存的消息且不超过24小时
    if (savedMessages && lastTimestamp) {
      const currentTime = new Date().getTime()
      const savedTime = parseInt(lastTimestamp)
      const hoursDiff = (currentTime - savedTime) / (1000 * 60 * 60)

      if (hoursDiff < 24) {
        messages.value = JSON.parse(savedMessages)
        isAdminMode.value = savedAdminMode === 'true'

        // 初始化已处理消息ID集合
        processedMessageIds.value = new Set(
          messages.value
            .filter(msg => msg.messageId)
            .map(msg => msg.messageId as string)
        )

        return true
      }
    }
  } catch (error) {
    console.error('恢复聊天记录时出错:', error)
  }
  return false
}

// 获取用户性别并设置对应头像
const getUserInfo = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    const response = await fetch(`${config.baseURL}/api/user/info`, {
      headers: {
        'Authorization': token
      }
    })

    if (response.ok) {
      const data = await response.json()
      if (data.code === 0 && data.data) {
        userGender.value = data.data.gender
        // 根据性别设置头像
        userAvatar.value = data.data.gender === 'female' ? girlAvatar : boyAvatar
      }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 返回按钮处理函数
const goBack = () => {
  router.back()
}

// 自动滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
  saveChatState()
}

// 监听消息变化，自动滚动并保存状态
watch(() => messages.value.length, () => {
  scrollToBottom()
})

watch(() => messages.value[messages.value.length - 1]?.content, () => {
  scrollToBottom()
})

// 监听管理员模式状态变化，保存状态
watch(isAdminMode, (newValue) => {
  saveChatState()
  if (newValue) {
    // 切换到管理员模式，初始化WebSocket
    initWebSocket()
  } else {
    // 退出管理员模式，关闭WebSocket
    if (socket) {
      socket.disconnect()
    }
  }
})

// 显示欢迎消息和获取用户信息
onMounted(async () => {
  // 添加页面类名以便CSS样式正确应用
  document.body.classList.add('chat-page')

  await getUserInfo()

  // 获取用户登录状态
  const isJustLoggedIn = checkIfJustLoggedIn()

  // 如果用户刚登录或没有恢复成功的聊天记录，显示欢迎消息
  if (isJustLoggedIn) {
    // 用户刚刚登录，显示欢迎消息
    messages.value = [{
      type: 'assistant',
      content: '欢迎使用绘心同学AI聊天功能！我已经了解了您的绘画分析结果，让我们开始交流吧。'
    }]
  } else {
    // 尝试恢复聊天状态
    const restored = restoreChatState()

    // 如果没有恢复成功，显示欢迎消息
    if (!restored) {
      messages.value.push({
        type: 'assistant',
        content: '欢迎使用绘心同学AI聊天功能！我已经了解了您的绘画分析结果，让我们开始交流吧。'
      })
    }
  }

  // 初始化WebSocket连接
  initWebSocket()

  // 监听页面关闭事件，保存聊天状态
  window.addEventListener('beforeunload', saveChatState)

  // 滚动到底部
  scrollToBottom()
})

// 检查用户是否刚刚登录
const checkIfJustLoggedIn = () => {
  try {
    // 获取登录时设置的时间戳
    const lastLoginTimestamp = localStorage.getItem('lastLoginTimestamp')
    if (!lastLoginTimestamp) return false

    const currentTime = new Date().getTime()
    const loginTime = parseInt(lastLoginTimestamp)

    // 计算时间差（分钟）
    const timeDiffMinutes = (currentTime - loginTime) / (1000 * 60)

    // 如果时间差小于5分钟，认为是刚刚登录
    return timeDiffMinutes < 5
  } catch (error) {
    console.error('检查登录状态出错:', error)
    return false
  }
}

// 组件销毁时的清理
onUnmounted(() => {
  // 移除页面类名
  document.body.classList.remove('chat-page')

  // 移除事件监听器
  window.removeEventListener('beforeunload', saveChatState)

  // 关闭WebSocket连接
  if (socket) {
    socket.disconnect()
  }
})

// 修改TypeScript类型定义
interface ChatMessage {
  type: 'user' | 'assistant' | 'admin';
  content: string;
  time?: string;
  messageId?: string;
}

// 定义WebSocket客户端
let socket: any = null;

// 初始化WebSocket连接
const initWebSocket = () => {
  if (socket) {
    socket.disconnect()
  }

  // 获取WebSocket URL，确保始终有一个有效值
  const socketUrl = config.socketUrl || `${window.location.protocol === 'https:' ? 'https://' : 'http://'}${window.location.hostname}:5000`;

  // 创建WebSocket连接
  socket = io(socketUrl, {
    auth: {
      token: localStorage.getItem('token')
    },
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000
  })

  // 连接事件
  socket.on('connect', () => {
    console.log('WebSocket连接成功')
    // 用户连接时发送身份信息
    socket.emit('user_connect', {
      token: localStorage.getItem('token')
    })
  })

  // 连接错误事件
  socket.on('connect_error', (error: any) => {
    console.error('WebSocket连接错误:', error)
    ElMessage.error('连接服务器失败，请刷新页面重试')
  })

  // 断开连接事件
  socket.on('disconnect', (reason: string) => {
    console.log('WebSocket断开连接:', reason)
    if (reason === 'io server disconnect') {
      // 服务器主动断开，尝试重连
      socket.connect()
    }
  })

  // 接收管理员回复
  socket.on('admin_reply', (message: any) => {
    console.log('收到管理员回复:', message)

    // 检查消息是否已经处理过（避免重复）
    if (message.messageId && processedMessageIds.value.has(message.messageId)) {
      console.log('消息已处理，忽略重复消息:', message.messageId)
      return
    }

    // 标记消息为已处理
    if (message.messageId) {
      processedMessageIds.value.add(message.messageId)
    }

    // 检查是否是系统风险提示消息，并且已经在消息列表中有相同内容的消息
    const systemRiskMessage = "系统检测到您的内容可能存在风险，已切换到人工客服模式。请稍等片刻，管理员正在审核您的对话...";
    if (message.content === systemRiskMessage && messages.value.some(msg => msg.content === systemRiskMessage)) {
      console.log('已存在相同的系统风险提示消息，忽略重复消息');
      return;
    }

    adminTyping.value = false
    messages.value.push({
      type: 'admin',
      content: message.content,
      time: message.time || new Date().toISOString(),
      messageId: message.messageId
    })
    isAdminMode.value = true
    saveChatState()
    scrollToBottom()
  })

  // 连接响应
  socket.on('connect_response', (data: any) => {
    console.log('连接响应:', data)
    if (data.status === 'success') {
      console.log('用户身份验证成功')
    }
  })

  // 错误事件
  socket.on('error', (data: any) => {
    console.error('WebSocket错误:', data)
    ElMessage.error('发生错误: ' + (data.message || '未知错误'))
  })
}

// 添加重新连接WebSocket的函数
const reconnectSocket = () => {
  if (reconnectAttempts.value >= maxReconnectAttempts) {
    ElMessage.error('连接服务器失败，请刷新页面重试')
    return
  }

  reconnectAttempts.value++
  console.log(`尝试重新连接 (${reconnectAttempts.value}/${maxReconnectAttempts})`)

  if (socket) {
    socket.disconnect()
  }

  setTimeout(() => {
    initWebSocket()
  }, 1000) // 1秒后重试
}

// 新增的输入处理方法
const inputTextarea = ref<HTMLTextAreaElement | null>(null)

// 处理键盘事件
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 处理输入变化，自动调整高度
const handleInput = () => {
  if (inputTextarea.value) {
    // 重置高度
    inputTextarea.value.style.height = 'auto'
    // 设置新高度，最大3行
    const scrollHeight = inputTextarea.value.scrollHeight
    const maxHeight = 72 // 3行的大概高度
    inputTextarea.value.style.height = Math.min(scrollHeight, maxHeight) + 'px'
  }
}

// 修改发送消息逻辑
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return;

  const userMsg = inputMessage.value.trim();
  inputMessage.value = '';

  // 重置输入框高度
  if (inputTextarea.value) {
    inputTextarea.value.style.height = 'auto'
  }

  // 添加用户消息到消息列表
  messages.value.push({
    type: 'user',
    content: userMsg
  });

  // 自动滚动到底部
  await nextTick();
  scrollToBottom();

  try {
    isLoading.value = true;

    // 检查是否处于管理员模式
    if (isAdminMode.value) {
      // 使用WebSocket发送消息
      if (socket && socket.connected) {
        socket.emit('user_message', {
          content: userMsg
        });
      } else {
        reconnectSocket();
        ElMessage.warning('连接服务器中，请稍后再试');
      }
    } else {
      // 使用流式API获取回复
      const token = localStorage.getItem('token');
      if (!token) {
        ElMessage.error('登录状态已过期，请重新登录');
        router.push('/login');
        return;
      }

      const response = await fetch(`${config.baseURL}${config.chatPath}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token
        },
        body: JSON.stringify({ message: userMsg })
      });

      // 检查响应状态
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // 检查Content-Type来确定响应类型
      const contentType = response.headers.get('content-type');

      // 流式响应处理
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let currentMessage = '';

      if (!reader) throw new Error('无法读取响应流');

      messages.value.push({
        type: 'assistant',
        content: '',
        time: new Date().toISOString()
      });
      const currentIndex = messages.value.length - 1;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        currentMessage += text;
        messages.value[currentIndex].content = currentMessage;
      }

      // 检查是否是危机言论检测的回复
      if (currentMessage.includes('系统检测到您的内容可能存在风险')) {
        isAdminMode.value = true;
        // 保存状态变化
        saveChatState();
        // 初始化WebSocket连接以接收管理员消息
        initWebSocket();
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error);
    messages.value.push({
      type: 'assistant',
      content: '抱歉，消息发送失败，请检查网络连接',
      time: new Date().toISOString()
    });
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
};
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
  cursor: default; /* 默认光标，不显示可点击状态 */
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

.nav-button {
  background: none;
  border: 1px solid #ddd;
  color: #4a4a4a;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn {
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.logout-btn:hover {
  background-color: #ff6b6b;
  color: white;
}

.chat-container {
  height: 100vh;
  width: 100%;
  max-width: 1200px; /* 设置最大宽度 */
  min-width: 600px;
  margin: 0 auto; /* 居中对齐 */
  display: flex;
  flex-direction: column;
  padding: calc(var(--spacing-unit, 1rem) * 1.25);
  padding-top: 84px; /* 为导航栏留出空间 */
  box-sizing: border-box;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 0;
  border-bottom: 1px solid #e6e6e6;
  margin-bottom: 15px;
}

.header-spacer {
  width: 100px; /* 占位元素，保持标题居中 */
}

.sidebar-toggle-btn {
  padding: 10px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}

.sidebar-toggle-btn:hover {
  background: #218838;
  transform: translateY(-1px);
}

.menu-icon {
  margin-right: 5px;
  font-size: 16px;
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  flex: 1;
  text-align: center;
}

.back-button {
  padding: 10px 16px;
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}

.back-button:hover {
  background: #0056b3;
  transform: translateY(-1px);
}

.back-icon {
  margin-right: 5px;
  font-size: 18px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #ffffff;
  border-radius: 16px;
  margin-bottom: 20px;
  scroll-behavior: smooth;
  min-height: 500px;
  height: calc(100vh - 220px);
  width: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  position: relative;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  text-align: center;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.empty-chat h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #374151;
}

.empty-chat p {
  font-size: 0.875rem;
  opacity: 0.8;
}

.message {
  margin-bottom: 24px;
  display: flex;
  align-items: flex-start;
  opacity: 0;
  animation: fadeIn 0.4s ease-out forwards;
  gap: 12px;
}

.message.assistant, .message.admin {
  flex-direction: row;
  align-self: flex-start;
}

.message.user {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.message-content {
  max-width: 70%;
  padding: 16px 20px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: keep-all;
  overflow-wrap: break-word;
  hyphens: none;
  margin: 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  position: relative;
}

.user .message-content {
  background: linear-gradient(135deg, #007AFF 0%, #0056b3 100%);
  color: white;
  margin-right: 12px;
  border-bottom-right-radius: 6px;
}

.assistant .message-content, .admin .message-content {
  background: white;
  color: #374151;
  margin-left: 12px;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 6px;
}

.admin .message-content {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
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

.chat-input {
  background: white;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
}

.input-wrapper {
  width: 100%;
}

.input-wrapper textarea {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 16px;
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

.input-wrapper textarea:focus {
  border-color: #007AFF;
  background: white;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.input-wrapper textarea:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
  border-color: #d1d5db;
}

.input-wrapper textarea::placeholder {
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
  background: linear-gradient(135deg, #007AFF 0%, #0056b3 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.4);
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

.send-button:disabled .send-icon {
  opacity: 0.5;
}

.send-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.2s ease;
}

.send-button:hover:not(:disabled) .send-icon {
  transform: scale(1.1);
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.typing-indicator {
  padding: 10px;
  margin: 10px 0;
  font-size: 0.9rem;
  color: #6b7280;
  display: flex;
  align-items: center;
}

.typing-dots span {
  animation: typingAnimation 1.4s infinite;
  animation-fill-mode: both;
  margin-left: 2px;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingAnimation {
  0% {
    opacity: 0.2;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    min-width: 100%;
    padding: 12px;
  }

  .chat-input {
    padding: 12px;
    border-radius: 12px;
  }

  .input-wrapper textarea {
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
    font-size: 14px;
  }

  .avatar {
    width: 36px;
    height: 36px;
  }

  .chat-messages {
    padding: 16px;
    margin-bottom: 16px;
  }

  .char-count {
    font-size: 11px;
  }
}

/* 中等屏幕优化 (平板和小桌面) */
@media (min-width: 769px) and (max-width: 1024px) {
  .chat-container {
    max-width: 95vw;
    padding: 20px;
  }

  .chat-messages {
    padding: 20px;
    height: calc(100vh - 200px);
  }

  .message-content {
    max-width: 85%; /* 参考手机端的85% */
    font-size: 15px;
    padding: 14px 18px;
  }

  .message {
    max-width: 90%; /* 增加到90% */
  }

  .avatar {
    width: 40px;
    height: 40px;
  }

  .input-wrapper textarea {
    font-size: 15px;
    padding: 14px 18px;
  }

  .send-button {
    width: 42px;
    height: 42px;
  }

  .chat-title {
    font-size: 17px;
  }

  .sidebar-toggle-btn,
  .back-button {
    padding: 10px 14px;
    font-size: 14px;
  }
}

/* 常规桌面屏幕优化 */
@media (min-width: 1025px) and (max-width: 1199px) {
  .chat-container {
    max-width: 1000px;
    padding: 24px;
  }

  .chat-messages {
    padding: 22px;
    height: calc(100vh - 210px);
  }

  .message-content {
    max-width: 85%; /* 参考手机端的85% */
    font-size: 15px;
    padding: 15px 19px;
  }

  .message {
    max-width: 90%; /* 增加到90% */
  }

  .avatar {
    width: 41px;
    height: 41px;
  }

  .input-wrapper textarea {
    font-size: 15px;
    padding: 15px 19px;
  }

  .send-button {
    width: 43px;
    height: 43px;
  }

  .chat-title {
    font-size: 17px;
  }
}

/* 宽屏幕优化 */
@media (min-width: 1200px) {
  .chat-container {
    max-width: 1200px; /* 聊天容器最大宽度 */
  }

  .message-content {
    max-width: 85%; /* 参考1199px以下的成功设置 */
    line-height: 1.6;
    word-wrap: break-word;
    word-break: keep-all;
    overflow-wrap: break-word;
    hyphens: none;
  }

  .message {
    max-width: 90%; /* 参考1199px以下的成功设置 */
  }
}

/* 2K分辨率优化 */
@media (min-width: 2560px) {
  .chat-container {
    max-width: 1400px; /* 2K屏幕下稍微增加聊天容器宽度 */
    padding: 30px;
  }

  .message-content {
    font-size: 1.1rem;
    padding: 16px 20px;
    max-width: 85%; /* 保持与较小屏幕一致的85% */
    line-height: 1.7;
    word-wrap: break-word;
    word-break: keep-all;
    overflow-wrap: break-word;
    hyphens: none;
  }

  .message {
    max-width: 90%; /* 保持与较小屏幕一致的90% */
  }

  .chat-header {
    font-size: 1.2rem;
    padding: 20px 0;
  }

  .input-wrapper textarea {
    font-size: 1.1rem;
    padding: 16px 20px;
  }

  .send-button {
    width: 50px;
    height: 50px;
  }

  .avatar {
    width: 50px;
    height: 50px;
  }
}

/* 4K分辨率优化 */
@media (min-width: 3840px) {
  .chat-container {
    max-width: 1600px; /* 4K屏幕下的最大聊天容器宽度 */
    padding: 40px;
  }

  .message-content {
    font-size: 1.3rem;
    padding: 20px 24px;
    max-width: 85%; /* 保持与较小屏幕一致的85% */
    line-height: 1.8;
    word-wrap: break-word;
    word-break: keep-all;
    overflow-wrap: break-word;
    hyphens: none;
  }

  .message {
    max-width: 90%; /* 保持与较小屏幕一致的90% */
  }

  .chat-header {
    font-size: 1.4rem;
    padding: 24px 0;
  }

  .input-wrapper textarea {
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

  .avatar {
    width: 60px;
    height: 60px;
  }

  .empty-chat h3 {
    font-size: 2rem;
  }

  .empty-chat p {
    font-size: 1.3rem;
  }

  .chat-title {
    font-size: 1.6rem;
  }

  .sidebar-toggle-btn,
  .back-button {
    padding: 12px 20px;
    font-size: 1.2rem;
  }
}

/* 焦点样式优化 */
@media (prefers-reduced-motion: no-preference) {
  .input-wrapper textarea:focus {
    animation: focusPulse 0.3s ease-out;
  }
}

@keyframes focusPulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 122, 255, 0.3);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(0, 122, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 122, 255, 0);
  }
}
</style>
