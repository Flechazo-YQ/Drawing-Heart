<template>
  <div class="chat-container">
    <button class="back-button" @click="goBack">
      <span class="back-icon">←</span> 返回
    </button>
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.type]">
        <img :src="getAvatarSrc(message.type)" :class="['avatar', message.type]"
          :alt="getAvatarAlt(message.type)" />
        <div class="message-content">
          {{ message.content }}
        </div>
      </div>
    </div>

    <div class="chat-input">
      <input v-model="inputMessage" type="text" placeholder="输入您想说的话..." @keyup.enter="(e: KeyboardEvent) => sendMessage()"
        :disabled="isLoading" />
      <button @click="(e: MouseEvent) => sendMessage()" :disabled="isLoading">
        {{ isLoading ? '发送中...' : '发送' }}
      </button>
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

// 修改发送消息逻辑
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return;
  
  const userMsg = inputMessage.value.trim();
  inputMessage.value = '';
  
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

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let currentMessage = '';

      if (!reader) throw new Error('无法读取响应流');

      messages.value.push({ 
        type: 'assistant', 
        content: '',
        time: new Date().toISOString()  // 添加时间戳
      });
      const currentIndex = messages.value.length - 1;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        currentMessage += text;
        messages.value[currentIndex].content = currentMessage;
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
.chat-container {
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.back-button {
  padding: 12px 24px;
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  width: fit-content;
  margin-bottom: 15px;
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
  padding: 20px;
  background: #f5f5f5;
  border-radius: 10px;
  margin-bottom: 20px;
  scroll-behavior: smooth;
  min-height: 400px;
  /* 添加最小高度 */
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
  opacity: 0;
  animation: fadeIn 0.3s ease-out forwards;
  gap: 10px;
}

.message.assistant, .message.admin {
  flex-direction: row;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 16px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  /* 移除左右margin */
}

.user .message-content {
  background: #95EC69;
  color: #000;
  margin-right: 10px;
  /* 添加右侧间距 */
}

.assistant .message-content, .admin .message-content {
  background: white;
  color: #000;
  margin-left: 10px;
  /* 添加左侧间距 */
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar.assistant, .avatar.admin {
  border: 2px solid #007AFF;
}

.avatar.user {
  border: 2px solid #28CD41;
}

.chat-input {
  display: flex;
  gap: 10px;
  background: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.chat-input input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input input:focus {
  border-color: #007AFF;
}

.chat-input button {
  padding: 12px 24px;
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-input button:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.chat-input button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
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
</style>