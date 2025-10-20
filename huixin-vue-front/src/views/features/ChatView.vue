<template>
  <div class="chat-page" @mousedown.capture="handleBackgroundMouseDown">
    <div class="chat-experience">
      <NavBarUser />
      <div class="chat-shell">
        <div class="chat-sidebar-shell">
          <ChatSidebar :displayMode="isDesktop ? 'inline' : 'drawer'" :isOpen="isDesktop ? true : sidebarOpen"
            @close="sidebarOpen = false" @chatLoaded="handleChatLoaded" @newChat="handleNewChat" />
        </div>

        <div class="chat-main" :class="[{ 'no-messages': !hasMessages, 'has-messages': hasMessages }]">
          <header v-if="!hasMessages" :class="['chat-hero', { 'hero-empty': !hasMessages }]">
            <div class="hero-visual">
              <AnimatedBear />
            </div>
            <div class="hero-left">
              <div class="hero-tagline">
                <img src="@/assets/images/others/Logo.png" alt="绘心同学" class="logo-img" />
                <span>绘心同学</span>
              </div>
              <h1 class="hero-title">{{ heroHeadline }}</h1>
              <p class="hero-subtitle">分享你的心绪与灵感，<br />我会以温柔与洞察回应你。</p>
              <div v-if="currentChatInfo" class="hero-meta">
                <span v-if="currentChatInfo.stats?.messageCount" class="hero-meta-chip">
                  {{ currentChatInfo.stats.messageCount }} 条记录
                </span>
                <span v-if="currentChatInfo.stats?.isDangerous" class="hero-meta-chip danger">
                  ⚠ 危机对话
                </span>
                <span v-if="currentChatInfo.timeNode?.lastMessageAt" class="hero-meta-chip subtle">
                  上次更新 · {{ formatTime(currentChatInfo.timeNode.lastMessageAt) }}
                </span>
              </div>
            </div>
            <div class="hero-footer">
              <div class="hero-controls">
                <div class="composer composer-inline">
                  <div class="composer-card">
                    <div class="composer-input">
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
                      <input ref="fileInput" type="file" class="file-input-hidden" @change="handleFileSelect" />
                      <input
                        ref="imageInput"
                        type="file"
                        accept="image/*"
                        class="file-input-hidden"
                        @change="handleImageSelect"
                      />
                      <div class="composer-footer">
                        <div class="composer-actions">
                          <button type="button" class="action-button" @click="triggerFilePicker" title="发送文件">
                            <span class="action-icon">📎</span>
                          </button>
                          <button type="button" class="action-button" @click="openDrawingHistory" title="调取绘画记录">
                            <span class="action-icon">🎨</span>
                          </button>
                        </div>
                        <button
                          type="button"
                          class="send-button"
                          @click="(e: MouseEvent) => sendMessage()"
                          :disabled="isLoading || !inputMessage.trim() || (isAdminMode && !socket.connected)"
                          :title="isLoading ? '发送中...' : (isAdminMode && !socket.connected ? '正在连接服务器...' : '发送消息 (Enter)')"
                        >
                          <span v-if="isLoading" class="loading-spinner"></span>
                          <svg v-else class="send-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                              d="M22 2L11 13"
                              stroke="currentColor"
                              stroke-width="2"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            />
                            <path
                              d="M22 2L15 22L11 13L2 9L22 2Z"
                              stroke="currentColor"
                              stroke-width="2"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <button v-if="!isDesktop" type="button" class="hero-history-btn" @click="toggleSidebar">
                  <span class="menu-icon">📁</span>
                  <span>历史记录</span>
                </button>
              </div>
            </div>
          </header>

          <section v-if="hasMessages" class="message-area">
            <header class="conversation-header">
              <div v-if="currentChatInfo" class="conversation-meta">
                <span v-if="currentChatInfo.stats?.messageCount" class="conversation-chip">
                  {{ currentChatInfo.stats.messageCount }} 条消息
                </span>
                <span v-if="currentChatInfo.stats?.isDangerous" class="conversation-chip danger">
                  ⚠ 风险会话
                </span>
                <span v-if="currentChatInfo.timeNode?.lastMessageAt" class="conversation-chip subtle">
                  更新于 {{ formatTime(currentChatInfo.timeNode.lastMessageAt) }}
                </span>
              </div>
              <button v-if="!isDesktop" type="button" class="conversation-history-btn" @click="toggleSidebar">
                <span class="menu-icon">📁</span>
                <span>历史记录</span>
              </button>
            </header>

            <div ref="messagesContainer" class="message-list">
              <TransitionGroup name="message-fade" tag="div">
                <div v-for="(message, index) in messages" :key="message.messageId || index" class="message-card"
                  :class="message.type">
                  <img class="message-avatar" :src="getAvatarSrc(message.type)" :alt="getAvatarAlt(message.type)" />
                  <div class="message-body">
                    <p class="message-text">
                      {{ message.content }}
                    </p>
                    <div v-if="message.metadata || message.timeNode" class="message-meta">
                      <span
                        v-if="typeof message.metadata?.emotionScore === 'number' && !Number.isNaN(message.metadata.emotionScore)"
                        class="meta-item emotion"
                      >
                        情绪得分 {{ message.metadata.emotionScore.toFixed(2) }}
                      </span>
                      <span v-if="message.metadata?.riskLevel" class="meta-item"
                        :class="`risk-${message.metadata.riskLevel}`">
                        风险 {{ getRiskLevelText(message.metadata.riskLevel) }}
                      </span>
                      <span v-if="message.timeNode?.createdAt" class="meta-item time">
                        {{ formatTime(message.timeNode.createdAt) }}
                      </span>
                      <span v-if="message.timeNode?.processedAt" class="meta-item time">
                        审核 {{ formatTime(message.timeNode.processedAt) }}
                      </span>
                    </div>
                  </div>
                </div>
              </TransitionGroup>
            </div>

          </section>

          <div v-if="hasMessages" class="composer composer-docked">
            <div class="composer-card">
              <div class="composer-input">
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
                <input ref="fileInput" type="file" class="file-input-hidden" @change="handleFileSelect" />
                <input
                  ref="imageInput"
                  type="file"
                  accept="image/*"
                  class="file-input-hidden"
                  @change="handleImageSelect"
                />
                <div class="composer-footer">
                  <div class="composer-actions">
                    <button type="button" class="action-button" @click="triggerFilePicker" title="发送文件">
                      <span class="action-icon">📎</span>
                    </button>
                    <button type="button" class="action-button" @click="openDrawingHistory" title="调取绘画记录">
                      <span class="action-icon">🎨</span>
                    </button>
                  </div>
                  <button
                    type="button"
                    class="send-button"
                    @click="(e: MouseEvent) => sendMessage()"
                    :disabled="isLoading || !inputMessage.trim() || (isAdminMode && !socket.connected)"
                    :title="isLoading ? '发送中...' : (isAdminMode && !socket.connected ? '正在连接服务器...' : '发送消息 (Enter)')"
                  >
                    <span v-if="isLoading" class="loading-spinner"></span>
                    <svg v-else class="send-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path
                        d="M22 2L11 13"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <path
                        d="M22 2L15 22L11 13L2 9L22 2Z"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import robotAvatar from '@/assets/images/avatars/AI.png'
import boyAvatar from '@/assets/images/avatars/Boy.png'
import girlAvatar from '@/assets/images/avatars/Girl.png'
import adminAvatar from '@/assets/images/avatars/Admin.png'
import { ElMessage } from 'element-plus'
import config from '@/config'
import ChatSidebar from '@/components/ChatSidebar.vue'
import NavBarUser from '@/components/NavBarUser.vue'
import AnimatedBear from '@/components/AnimatedBear.vue'

import socket from '@/utils/network'

// 消息数据接口定义
interface MessageData {
  type: 'user' | 'assistant' | 'admin'
  content: string
  time?: string
  messageId?: string
  metadata?: {
    emotionScore?: number
    riskLevel?: string
    processedAt?: string
  }
  timeNode?: {
    createdAt: string
    updatedAt?: string
    processedAt?: string
  }
}

const router = useRouter()
const messages = ref<Array<MessageData>>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 3
const userGender = ref<string>('')
const userAvatar = ref<string>(boyAvatar)
const isAdminMode = ref(false)
const adminTyping = ref(false)
const processedMessageIds = ref<Set<string>>(new Set())

const userName = ref('朋友')
const isDesktop = ref(false)

const CHAT_TITLE_KEY_PREFIX = 'chatFirstTitle_'
const PLACEHOLDER_TITLES = ['新对话', '新会话', '未命名会话']
const CHAT_LIST_REFRESH_EVENT = 'chatListRefresh'
const ACTIVE_CHAT_ID_KEY_PREFIX = 'activeChatId_'

let chatCreationPromise: Promise<string | null> | null = null

const buildChatScopedKey = (userId: string, chatId: string, key: string) => `chat_${key}_${userId}_${chatId}`
const buildActiveChatKey = (userId: string) => `${ACTIVE_CHAT_ID_KEY_PREFIX}${userId}`

const resolveUserIdFromStorage = () => {
  try {
    const stored = localStorage.getItem('userInfo')
    if (!stored) return ''
    const parsed = JSON.parse(stored)
    return parsed?.id || parsed?._id || ''
  } catch (error) {
    console.error('解析用户信息失败:', error)
    return ''
  }
}

const sanitizeTitle = (value: string | null | undefined) => {
  const safe = (value ?? '').toString()
  return safe.replace(/\s+/g, ' ').trim()
}

const normalizeMessageType = (raw: any): 'user' | 'assistant' | 'admin' => {
  const candidate = (raw?.sender ?? raw?.role ?? raw?.from ?? raw?.source ?? raw?.type ?? '').toString().toLowerCase()
  if (['user', 'customer', 'client', 'member'].includes(candidate)) return 'user'
  if (['assistant', 'ai', 'bot', 'robot', 'system'].includes(candidate)) return 'assistant'
  if (candidate === 'admin' || candidate === 'moderator' || candidate === 'staff' || candidate === 'service') return 'admin'
  return 'assistant'
}

const normalizeMessageContent = (raw: any): string => {
  const content = raw?.content ?? raw?.message ?? raw?.text ?? ''
  if (typeof content === 'string') return content
  if (Array.isArray(content)) {
    return content
      .map((item) => {
        if (!item) return ''
        if (typeof item === 'string') return item
        if (typeof item.text === 'string') return item.text
        if (typeof item.content === 'string') return item.content
        return ''
      })
      .join('')
  }
  if (typeof content === 'object' && content !== null) {
    if (typeof content.text === 'string') return content.text
    if (typeof content.value === 'string') return content.value
  }
  return ''
}

const isValidTitle = (title: string) => {
  const normalized = sanitizeTitle(title)
  if (!normalized) return false
  return !PLACEHOLDER_TITLES.includes(normalized)
}

const getStoredChatTitle = (chatId: string) => {
  if (!chatId) return ''
  return localStorage.getItem(`${CHAT_TITLE_KEY_PREFIX}${chatId}`) || ''
}

const emitChatTitleUpdate = (chatId: string, title: string) => {
  document.dispatchEvent(new CustomEvent('chatTitleUpdated', {
    detail: { chatId, title }
  }))
}

const persistChatTitle = (chatId: string, rawTitle: string) => {
  if (!chatId) return
  const normalized = sanitizeTitle(rawTitle)
  if (!isValidTitle(normalized)) return
  const key = `${CHAT_TITLE_KEY_PREFIX}${chatId}`
  const existing = localStorage.getItem(key)
  if (existing !== normalized) {
    localStorage.setItem(key, normalized)
  }
  emitChatTitleUpdate(chatId, normalized)
}

const clearStoredChatTitle = (chatId: string) => {
  if (!chatId) return
  localStorage.removeItem(`${CHAT_TITLE_KEY_PREFIX}${chatId}`)
  emitChatTitleUpdate(chatId, '')
}

const extractFirstUserMessage = (rawMessages: any[]) => {
  if (!Array.isArray(rawMessages)) return ''
  const target = rawMessages.find((msg) => {
    const sender = normalizeMessageType(msg)
    const content = normalizeMessageContent(msg).trim()
    return sender === 'user' && content
  })
  return target ? normalizeMessageContent(target) : ''
}

const bumpCurrentChatMeta = (increment = 0, overrides?: {
  isDangerous?: boolean
  type?: 'normal' | 'dangerous'
  updatedAt?: string
}) => {
  if (!currentChatId.value) return

  const now = overrides?.updatedAt || new Date().toISOString()
  const currentStats = currentChatInfo.value?.stats || {}
  const currentTimeNode = currentChatInfo.value?.timeNode || {}

  currentChatInfo.value = {
    _id: currentChatId.value,
    ...(currentChatInfo.value || {}),
    title: currentChatTitle.value || currentChatInfo.value?.title || '未命名会话',
    type: overrides?.type || currentChatInfo.value?.type || 'normal',
    stats: {
      ...currentStats,
      messageCount: (currentStats.messageCount || 0) + increment,
      isDangerous: overrides?.isDangerous ?? currentStats.isDangerous ?? false,
      emotionAnalysis: currentStats.emotionAnalysis
    },
    timeNode: {
      ...currentTimeNode,
      lastMessageAt: now,
      updatedAt: now
    }
  }
}

const createChatSession = async (): Promise<string | null> => {
  if (chatCreationPromise) return chatCreationPromise

  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.error('登录状态已过期，请重新登录')
    router.push('/login')
    return null
  }

  chatCreationPromise = (async () => {
    try {
      const response = await fetch(`${config.baseURL}/api/chats`, {
        method: 'POST',
        headers: {
          'Authorization': token,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: '新对话' })
      })

      if (!response.ok) {
        throw new Error(`创建对话失败，状态码: ${response.status}`)
      }

      const result = await response.json()
      if (result.code !== 0 || !result.data?.chatId) {
        throw new Error(result.message || '创建对话失败')
      }

      const newChatId: string = result.data.chatId
      currentChatId.value = newChatId
      currentChatTitle.value = ''
      currentChatInfo.value = {
        _id: newChatId,
        title: '未命名会话',
        type: 'normal',
        stats: {
          messageCount: 0,
          isDangerous: false,
          emotionAnalysis: [] as string[]
        },
        timeNode: {}
      }
      clearStoredChatTitle(newChatId)

      document.dispatchEvent(new CustomEvent(CHAT_LIST_REFRESH_EVENT, {
        detail: { chatId: newChatId }
      }))

      return newChatId
    } catch (error) {
      console.error('创建新对话失败:', error)
      ElMessage.error('创建新对话失败，请稍后重试')
      return null
    } finally {
      chatCreationPromise = null
    }
  })()

  return chatCreationPromise
}

const ensureActiveChat = async (): Promise<string | null> => {
  if (currentChatId.value) return currentChatId.value
  const chatId = await createChatSession()
  return chatId
}

const timeGreeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 11) return '早上好'
  if (hour < 13) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

const heroHeadline = computed(() => `${timeGreeting.value}，${userName.value}`)
const hasMessages = computed(() => messages.value.length > 0)

const envBase = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() || ''
const configBase = (config.baseURL ?? '').toString().trim()
const backendBaseUrl = envBase || configBase || 'http://localhost:5000'

const buildAbsoluteUrl = (rawUrl: string) => {
  if (!rawUrl) return ''
  if (/^https?:\/\//i.test(rawUrl)) return rawUrl
  if (/^(data:|blob:)/i.test(rawUrl)) return rawUrl
  if (rawUrl.startsWith('//')) return `${window.location.protocol}${rawUrl}`
  if (!backendBaseUrl) return rawUrl

  const cleanBase = backendBaseUrl.endsWith('/') ? backendBaseUrl.slice(0, -1) : backendBaseUrl
  const cleanPath = rawUrl.startsWith('/') ? rawUrl : `/${rawUrl}`
  return `${cleanBase}${cleanPath}`
}

const createLetterAvatar = (name: string) => {
  const firstChar = (name || '用').charAt(0).toUpperCase()
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(firstChar)}&size=60&background=42b983&color=ffffff&rounded=true`
}

const resolveUserName = (data: any) => {
  const profile = data?.profile ?? {}
  return (
    data?.nickname ||
    data?.nickName ||
    profile?.nickname ||
    profile?.nickName ||
    data?.realName ||
    profile?.realName ||
    data?.username ||
    profile?.username ||
    data?.name ||
    profile?.name ||
    userName.value ||
    '朋友'
  )
}

const resolveGender = (profile?: any, fallback?: string) => profile?.gender || profile?.sex || fallback || ''

const resolveUserAvatar = (profile: any, displayName: string) => {
  const rawAvatar = profile?.avatar ?? profile?.avatarUrl ?? profile?.avatarURL ?? ''
  const avatarPath = typeof rawAvatar === 'string' ? rawAvatar.trim() : ''
  if (avatarPath) {
    return buildAbsoluteUrl(avatarPath)
  }

  const gender = resolveGender(profile, userGender.value)
  if (gender === 'male') return boyAvatar
  if (gender === 'female') return girlAvatar

  return createLetterAvatar(displayName)
}

const syncAvatarFromLocalStorage = () => {
  try {
    const stored = localStorage.getItem('userInfo')
    if (!stored) return

    const user = JSON.parse(stored)
    const displayName = resolveUserName(user)
    userName.value = displayName
    userGender.value = resolveGender(user?.profile, userGender.value)
    userAvatar.value = resolveUserAvatar(user?.profile ?? user, displayName)
  } catch (error) {
    console.error('同步用户头像失败:', error)
  }
}

const handleAvatarRefresh = () => {
  syncAvatarFromLocalStorage()
}

const updateViewport = () => {
  isDesktop.value = window.innerWidth >= 1180
}

const handleResize = () => {
  updateViewport()
  if (isDesktop.value) {
    sidebarOpen.value = false
  }
}

// 新增的聊天历史相关变量
const sidebarOpen = ref(false)
const currentChatId = ref<string>('')
const currentChatTitle = ref<string>('')
const currentChatInfo = ref<any>(null)

// 时间格式化函数
const formatTime = (dateInput: any) => {
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

// 风险等级文本转换函数
const getRiskLevelText = (riskLevel: string) => {
  switch (riskLevel) {
    case 'low': return '低风险'
    case 'medium': return '中风险'
    case 'high': return '高风险'
    case 'critical': return '严重风险'
    default: return riskLevel
  }
}

// 获取头像源
const getAvatarSrc = (type: string) => {
  switch (type) {
    case 'user': return userAvatar.value || createLetterAvatar(userName.value)
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
  if (isDesktop.value) return
  sidebarOpen.value = !sidebarOpen.value
}

// 处理聊天加载
const handleChatLoaded = async (chatId: string, messagesList?: any[], chatInfo?: any) => {
  currentChatId.value = chatId
  sidebarOpen.value = false

  if (Array.isArray(messagesList)) {
    // 直接用传递过来的消息数组
    messages.value = messagesList.map((msg: any) => ({
      type: normalizeMessageType(msg),
      content: normalizeMessageContent(msg),
      time: msg.timestamp,
      messageId: msg._id,
      metadata: msg.metaData ? {
        emotionScore: msg.metaData.emotionScore,
        riskLevel: msg.metaData.riskLevel,
        processedAt: msg.metaData.processedAt
      } : undefined,
      timeNode: msg.timeNode ? {
        createdAt: msg.timeNode.createdAt,
        updatedAt: msg.timeNode.updatedAt,
        processedAt: msg.timeNode.processedAt
      } : undefined
    }))

  const storedTitle = sanitizeTitle(getStoredChatTitle(chatId))
  const firstQuestion = sanitizeTitle(extractFirstUserMessage(messagesList) || '')
    const fallbackTitle = sanitizeTitle(chatInfo?.title || '')
    const resolvedTitle = [firstQuestion, storedTitle, fallbackTitle].find(title => isValidTitle(title)) || ''
    currentChatTitle.value = resolvedTitle

    if (resolvedTitle) {
      persistChatTitle(chatId, resolvedTitle)
    } else if (storedTitle) {
      emitChatTitleUpdate(chatId, storedTitle)
    }

    if (chatInfo) {
      currentChatInfo.value = {
        ...chatInfo,
        title: currentChatTitle.value || chatInfo.title
      }
      isAdminMode.value = chatInfo.type === 'dangerous'
    } else if (currentChatInfo.value) {
      isAdminMode.value = currentChatInfo.value.type === 'dangerous'
    }

    // 你可以在这里设置 currentChatTitle、currentChatInfo 等
    // 也可以根据需要 fetch 一下 chat 信息
    await nextTick()
    scrollToBottom()
  } else {
    // 兼容旧逻辑
    await loadChatMessages(chatId)
  }
}

// 处理新建聊天
const handleNewChat = (chatId: string) => {
  currentChatId.value = chatId
  currentChatTitle.value = ''
  currentChatInfo.value = chatId ? {
    _id: chatId,
    title: '未命名会话',
    type: 'normal',
    stats: {
      messageCount: 0,
      isDangerous: false,
      emotionAnalysis: [] as string[]
    },
    timeNode: {}
  } : null
  messages.value = []
  sidebarOpen.value = false

  if (chatId) {
    clearStoredChatTitle(chatId)
  }

  // 清除管理员模式
  isAdminMode.value = false
  processedMessageIds.value.clear()
}

// 加载聊天消息
const loadChatMessages = async (chatId: string): Promise<boolean> => {
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

      const storedTitle = sanitizeTitle(getStoredChatTitle(chatId))
      const firstQuestion = sanitizeTitle(extractFirstUserMessage(messagesList) || '')
      const fallbackTitle = sanitizeTitle(chat?.title || '')
      const resolvedTitle = [firstQuestion, storedTitle, fallbackTitle].find(title => isValidTitle(title)) || ''

      currentChatTitle.value = resolvedTitle
      currentChatInfo.value = {
        ...chat,
        title: currentChatTitle.value || chat?.title
      }
      isAdminMode.value = chat.type === 'dangerous'

      if (resolvedTitle) {
        persistChatTitle(chatId, resolvedTitle)
      } else if (storedTitle) {
        emitChatTitleUpdate(chatId, storedTitle)
      }

      // 转换消息格式
      messages.value = messagesList.map((msg: any) => ({
        type: normalizeMessageType(msg),
        content: normalizeMessageContent(msg),
        messageId: msg._id,
        metadata: msg.metaData ? {
          emotionScore: msg.metaData.emotionScore,
          riskLevel: msg.metaData.riskLevel,
          processedAt: msg.metaData.processedAt
        } : undefined,
        timeNode: {
          createdAt: msg.timeNode?.createdAt || msg.timestamp || new Date().toISOString(),
          updatedAt: msg.timeNode?.updatedAt,
          processedAt: msg.timeNode?.processedAt
        }
      }))
      console.log('加载聊天消息成功:', messages.value)

      processedMessageIds.value = new Set(
        messagesList
          .filter((msg: any) => Boolean(msg?._id))
          .map((msg: any) => msg._id as string)
      )
      // 滚动到底部
      await nextTick()
      scrollToBottom()
      const lastMessageFromServer = chat?.timeNode?.lastMessageAt ||
        (messagesList && messagesList.length
          ? (messagesList[messagesList.length - 1]?.timeNode?.createdAt || messagesList[messagesList.length - 1]?.timestamp)
          : undefined) ||
        new Date().toISOString()

      bumpCurrentChatMeta(0, {
        isDangerous: currentChatInfo.value?.stats?.isDangerous,
        type: currentChatInfo.value?.type,
        updatedAt: lastMessageFromServer
      })

      return true
    } else {
      ElMessage.error(result.message || '加载聊天消息失败')
    }
  } catch (error) {
    console.error('加载聊天消息失败:', error)
    ElMessage.error('加载聊天消息失败')
  }
  return false
}

// 保存聊天状态到localStorage
const saveChatState = () => {
  const chatId = currentChatId.value
  if (!chatId) return

  try {
    const userId = resolveUserIdFromStorage()
    if (!userId) {
      console.error('保存聊天记录失败：找不到用户ID')
      return
    }

    if (messages.value.length === 0) {
      localStorage.removeItem(buildChatScopedKey(userId, chatId, 'messages'))
      localStorage.removeItem(buildChatScopedKey(userId, chatId, 'adminMode'))
      localStorage.removeItem(buildChatScopedKey(userId, chatId, 'timestamp'))
      return
    }

    localStorage.setItem(buildChatScopedKey(userId, chatId, 'messages'), JSON.stringify(messages.value))
    localStorage.setItem(buildChatScopedKey(userId, chatId, 'adminMode'), isAdminMode.value.toString())
    localStorage.setItem(buildChatScopedKey(userId, chatId, 'timestamp'), new Date().getTime().toString())
    localStorage.setItem(buildActiveChatKey(userId), chatId)
  } catch (error) {
    console.error('保存聊天记录时出错:', error)
  }
}

// 从localStorage恢复聊天状态
const restoreChatState = async (): Promise<boolean> => {
  try {
    const userId = resolveUserIdFromStorage()
    if (!userId) {
      console.error('恢复聊天记录失败：找不到用户ID')
      return false
    }

    const activeChatId = localStorage.getItem(buildActiveChatKey(userId))
    if (!activeChatId) return false

    currentChatId.value = activeChatId

    const restoredFromBackend = await loadChatMessages(activeChatId)
    if (restoredFromBackend) {
      const savedAdminMode = localStorage.getItem(buildChatScopedKey(userId, activeChatId, 'adminMode'))
      if (savedAdminMode !== null) {
        isAdminMode.value = savedAdminMode === 'true'
      }
      return true
    }

    const savedMessages = localStorage.getItem(buildChatScopedKey(userId, activeChatId, 'messages'))
    if (!savedMessages) return false

    const lastTimestamp = localStorage.getItem(buildChatScopedKey(userId, activeChatId, 'timestamp'))
    if (lastTimestamp) {
      const currentTime = new Date().getTime()
      const savedTime = parseInt(lastTimestamp, 10)
      const hoursDiff = (currentTime - savedTime) / (1000 * 60 * 60)
      if (hoursDiff >= 24) {
        return false
      }
    }

    messages.value = JSON.parse(savedMessages)
    isAdminMode.value = localStorage.getItem(buildChatScopedKey(userId, activeChatId, 'adminMode')) === 'true'

    processedMessageIds.value = new Set(
      messages.value
        .filter(msg => msg.messageId)
        .map(msg => msg.messageId as string)
    )

    const storedTitle = sanitizeTitle(getStoredChatTitle(activeChatId))
    currentChatTitle.value = storedTitle
    currentChatInfo.value = {
      _id: activeChatId,
      title: storedTitle || '未命名会话',
      type: isAdminMode.value ? 'dangerous' : 'normal',
      stats: {
        messageCount: messages.value.length,
        isDangerous: isAdminMode.value,
        emotionAnalysis: currentChatInfo.value?.stats?.emotionAnalysis || []
      },
      timeNode: {
        lastMessageAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    }

    return messages.value.length > 0
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

    const response = await fetch(`${config.baseURL}/api/info`, {
      headers: {
        'Authorization': token
      }
    })

    if (response.ok) {
      const data = await response.json()
      if (data.code === 0 && data.data) {
        const profile = data.data.profile ?? data.data
        const displayName = resolveUserName(profile)
        userName.value = displayName
        userGender.value = resolveGender(profile, userGender.value)
        userAvatar.value = resolveUserAvatar(profile, displayName)
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
  if (currentChatId.value) {
    bumpCurrentChatMeta(0, {
      isDangerous: newValue,
      type: newValue ? 'dangerous' : 'normal'
    })
  }
  saveChatState()
})

// 显示欢迎消息和获取用户信息
onMounted(async () => {
  // 添加页面类名以便CSS样式正确应用
  document.body.classList.add('chat-page')
  updateViewport()
  window.addEventListener('resize', handleResize)

  syncAvatarFromLocalStorage()
  document.addEventListener('refreshAvatar', handleAvatarRefresh)

  await getUserInfo()

  // 获取用户登录状态
  const isJustLoggedIn = checkIfJustLoggedIn()

  // 如果用户刚登录或没有恢复成功的聊天记录，显示欢迎消息
  if (isJustLoggedIn) {
    // 用户刚刚登录，重置对话状态
    messages.value = []
    isAdminMode.value = false
    processedMessageIds.value.clear()
  } else {
    // 尝试恢复聊天状态
    const restored = await restoreChatState()

    // 如果没有恢复成功，确保处于初始空状态
    if (!restored) {
      messages.value = []
      isAdminMode.value = false
      processedMessageIds.value.clear()
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
  document.removeEventListener('refreshAvatar', handleAvatarRefresh)
  window.removeEventListener('beforeunload', saveChatState)
  window.removeEventListener('resize', handleResize)

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

// 初始化WebSocket连接
const initWebSocket = () => {
  socket.off('connect')
  socket.off('connect_error')
  socket.off('disconnect')
  socket.off('new_message')
  socket.off('admin_reply')
  socket.off('connect_response')
  socket.off('error')

  // 连接事件
  socket.on('connect', () => {
    console.log('WebSocket连接成功')
    // 用户连接时发送身份信息
    socket.emit('user_auth', {
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

  // 监听新消息
  socket.on('new_message', (data: any) => {
    console.log('新消息:', data)
    // 只处理当前聊天的管理员消息
    if (
      data.role === 'admin' &&
      (currentChatId.value === data.chatId || !data.chatId)
    ) {
      const messageTime = data.time || new Date().toISOString()
      messages.value.push({
        type: 'admin',
        content: data.content,
        time: messageTime,
        // 可根据后端返回补充 messageId、metadata、timeNode 等
        timeNode: {
          createdAt: messageTime
        }
      })
      isAdminMode.value = true
      bumpCurrentChatMeta(1, { isDangerous: true, type: 'dangerous', updatedAt: messageTime })
      scrollToBottom()
      saveChatState()
      if (currentChatId.value) {
        document.dispatchEvent(new CustomEvent(CHAT_LIST_REFRESH_EVENT, {
          detail: { chatId: currentChatId.value }
        }))
      }
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
      messageId: message.messageId,
      metadata: message.metadata,
      timeNode: message.timeNode || {
        createdAt: new Date().toISOString()
      }
    })
    isAdminMode.value = true
    bumpCurrentChatMeta(1, {
      isDangerous: true,
      type: 'dangerous',
      updatedAt: message.time || new Date().toISOString()
    })
    saveChatState()
    scrollToBottom()
    if (currentChatId.value) {
      document.dispatchEvent(new CustomEvent(CHAT_LIST_REFRESH_EVENT, {
        detail: { chatId: currentChatId.value }
      }))
    }
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
const fileInput = ref<HTMLInputElement | null>(null)
const imageInput = ref<HTMLInputElement | null>(null)

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

const triggerFilePicker = () => {
  if (isLoading.value) return
  fileInput.value?.click()
}

const triggerImagePicker = () => {
  if (isLoading.value) return
  imageInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  ElMessage.info(`已选择文件：${file.name}`)
  input.value = ''
}

const handleImageSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  ElMessage.info(`已选择图片：${file.name}`)
  input.value = ''
}

const openDrawingHistory = () => {
  router.push('/records')
}

const handleBackgroundMouseDown = (event: MouseEvent) => {
  const activeElement = document.activeElement as HTMLElement | null
  if (!activeElement) return

  const activeTag = activeElement.tagName
  if (activeTag !== 'INPUT' && activeTag !== 'TEXTAREA') return

  const target = event.target as HTMLElement | null
  if (!target) return

  if (target === activeElement || activeElement.contains(target)) return

  if (target.closest('textarea, input, [contenteditable], .composer-input')) return

  activeElement.blur()
}

// 修改发送消息逻辑
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMsg = inputMessage.value.trim()
  const activeChatId = await ensureActiveChat()
  if (!activeChatId) return

  inputMessage.value = ''

  if (inputTextarea.value) {
    inputTextarea.value.style.height = 'auto'
  }

  const createdAt = new Date().toISOString()
  messages.value.push({
    type: 'user',
    content: userMsg,
    timeNode: {
      createdAt
    }
  })
  bumpCurrentChatMeta(1, { updatedAt: createdAt })

  if (!isValidTitle(currentChatTitle.value)) {
    const resolvedTitle = sanitizeTitle(userMsg)
    if (resolvedTitle) {
      currentChatTitle.value = resolvedTitle
      persistChatTitle(activeChatId, resolvedTitle)
    }
  }

  await nextTick()
  scrollToBottom()

  try {
    isLoading.value = true

    if (isAdminMode.value) {
      if (socket && socket.connected) {
        socket.emit('user_message', {
          chatId: activeChatId,
          content: userMsg
        })
        document.dispatchEvent(new CustomEvent(CHAT_LIST_REFRESH_EVENT, {
          detail: { chatId: activeChatId }
        }))
      } else {
        reconnectSocket()
        ElMessage.warning('连接服务器中，请稍后再试')
      }
    } else {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('登录状态已过期，请重新登录')
        router.push('/login')
        return
      }

      const requestBody = {
        message: userMsg,
        chatId: activeChatId
      }
      const response = await fetch(`${config.baseURL}${config.chatPath}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token
        },
        body: JSON.stringify(requestBody)
      })

      if (response.status === 204) {
        document.dispatchEvent(new CustomEvent(CHAT_LIST_REFRESH_EVENT, {
          detail: { chatId: activeChatId }
        }))
        return
      }
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let currentMessage = ''

      if (!reader) throw new Error('无法读取响应流')

      const assistantCreatedAt = new Date().toISOString()
      messages.value.push({
        type: 'assistant',
        content: '',
        time: assistantCreatedAt,
        timeNode: {
          createdAt: assistantCreatedAt
        }
      })
      bumpCurrentChatMeta(1, { updatedAt: assistantCreatedAt })
      const currentIndex = messages.value.length - 1

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        text.split('\n').forEach(line => {
          if (line.startsWith('data: ')) {
            const dataString = line.slice(6).trim()
            if (dataString === '[DONE]') return
            try {
              const data = JSON.parse(dataString)
              if (data.content) {
                currentMessage += data.content
                messages.value[currentIndex].content = currentMessage
              }
            } catch (error) {
              console.error('解析数据失败:', error)
            }
          }
        })
      }

      document.dispatchEvent(new CustomEvent(CHAT_LIST_REFRESH_EVENT, {
        detail: { chatId: activeChatId }
      }))

      if (currentMessage.includes('系统检测到您的内容可能存在风险')) {
        isAdminMode.value = true
        bumpCurrentChatMeta(0, { isDangerous: true, type: 'dangerous' })
        saveChatState()
        initWebSocket()
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    const failedAt = new Date().toISOString()
    messages.value.push({
      type: 'assistant',
      content: '抱歉，消息发送失败，请检查网络连接',
      time: failedAt,
      timeNode: {
        createdAt: failedAt
      }
    })
    bumpCurrentChatMeta(1, { updatedAt: failedAt })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.chat-page {
  background: radial-gradient(circle at 10% 10%, rgba(238, 242, 255, 0.7), transparent 40%),
    radial-gradient(circle at 90% 20%, rgba(236, 253, 245, 0.6), transparent 45%),
    #f6f7fb;
  min-height: 100vh;
  overflow: hidden;
}

.chat-experience {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-shell {
  flex: 1;
  display: flex;
  gap: 24px;
  align-items: flex-start;
  width: calc(100% - 6.1%);
  margin: 0;
  margin-left: 2.5%;
  margin-right: 3.6%;
  padding: 32px 24px 24px;
  box-sizing: border-box;
  min-height: 0;
  overflow: hidden;
  max-width: none;
}

.chat-sidebar-shell {
  flex: 0 0 22%;
  max-width: 270px;
  min-width: 240px;
  margin-top: 2%;
  margin-left: -2%;
}


.chat-main {
  flex: 1 1 78%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16px;
  min-height: 0;
  overflow: visible;
  padding: 24px 0;
}

.chat-main.has-messages {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  align-items: stretch;
  justify-content: stretch;
  gap: 24px;
  height: 100%;
  padding-top: 32px;
  padding-bottom: 32px;
}

.chat-main.no-messages {
  align-items: center;
  height: 100%;
  gap: 28px;
  padding: 72px 0 32px;
}

.chat-main.no-messages .chat-hero,
.chat-main.no-messages .composer {
  width: min(720px, 100%);
  margin: 0 auto;
}

.chat-hero {
  --hero-padding-inline: clamp(32px, 4vw, 44px);
  --hero-padding-block: clamp(34px, 5vh, 48px);
  background: linear-gradient(115deg, rgba(248, 250, 255, 0.97) 0%, rgba(248, 250, 255, 0.97) 42%, #ffffff 42%, #ffffff 100%);
  border-radius: 36px;
  padding: var(--hero-padding-block) var(--hero-padding-inline) calc(var(--hero-padding-block) + 132px);
  box-shadow: 0 28px 54px rgba(15, 23, 42, 0.1);
  display: grid;
  grid-template-columns: clamp(240px, 28%, 320px) minmax(0, 1fr);
  gap: clamp(28px, 4vw, 42px);
  position: relative;
  overflow: visible;
  min-height: 360px;
}

.chat-hero::after {
  display: none;
}

.chat-hero.hero-empty {
  background: #ffffff;
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.05);
  padding: 24px 0px 24px 0px;
  text-align: center;
}

.chat-hero.hero-empty::after {
  display: none;
}

.hero-left {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
  text-align: center;
  padding: 24px 0 0 0;
  grid-column: 2;
  align-self: flex-start;
  width: 100%;
  max-width: none;
}

.hero-empty .hero-left {
  align-items: center;
  text-align: center;
}

.hero-visual {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 16px;
  position: relative;
  z-index: 1;
  min-width: clamp(220px, 26vw, 320px);
  width: clamp(240px, 30vw, 360px);
  align-self: stretch;
  margin-bottom: 10px;
  padding-left: 10px;
  padding-right: clamp(12px, 1.5vw, 24px);
  grid-column: 1;
  overflow: visible;
}

.hero-empty .hero-visual {
  min-width: unset;
}

.logo-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.hero-tagline,
.hero-title,
.hero-subtitle {
  font-family: 'AiDianFengYaHei', 'YEFONTColor', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
}
.hero-tagline {
  align-items: center;
  cursor: default;
  font-size: 28px;
  font-weight: 700;
  color: #000000;
  text-transform: uppercase;
  letter-spacing: 1.2px;
}


.hero-title {
  margin: 0;
  font-size: clamp(30px, 2vw, 40px);
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.4px;
}

.hero-subtitle {
  margin: 0;
  font-size: 16px;
  line-height: 1.7;
  color: rgba(30, 41, 59, 0.78);
  max-width: 540px;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-meta-chip {
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
  font-size: 12px;
  font-weight: 500;
}

.hero-meta-chip.danger {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}

.hero-meta-chip.subtle {
  background: rgba(129, 140, 248, 0.14);
  color: #4338ca;
}

.hero-footer {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: clamp(12px, 2.2vw, 20px);
  margin-top: clamp(16px, 3vh, 24px);
  width: 100%;
  padding: clamp(12px, 0vw, 20px)  clamp(20px, 3vw, 40px) clamp(20px, 1.5vw, 40px);
  box-sizing: border-box;
}

.hero-controls {
  width: 100%;
  max-width: none;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: clamp(16px, 2.5vw, 24px);
}

.composer-inline {
  width: 100%;
  max-width: none;
}

.hero-history-btn {
  align-self: flex-start;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(79, 70, 229, 0.12);
  color: #4338ca;
  border: none;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-weight: 500;
}

.conversation-history-btn {
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(79, 70, 229, 0.12);
  color: #4338ca;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 8px;
}

.menu-icon {
  font-size: 16px;
}


.message-area {
  width: 100%;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0 8px 24px;
  background: transparent;
  border: none;
  box-shadow: none;
  overflow: hidden;
}

.conversation-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.conversation-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.conversation-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.conversation-chip {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
  color: #475569;
  font-size: 12px;
}

.conversation-chip.danger {
  background: rgba(248, 113, 113, 0.25);
  color: #b91c1c;
}

.conversation-chip.subtle {
  background: rgba(148, 163, 184, 0.16);
  color: rgba(30, 41, 59, 0.6);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding-right: 6px;
  padding-bottom: 24px;
  scroll-padding-bottom: 24px;
}

.message-list > div {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-align: center;
  color: #64748b;
  padding: 48px 0;
}

.empty-bubble {
  font-size: 42px;
  filter: drop-shadow(0 12px 20px rgba(99, 102, 241, 0.18));
}

.empty-state h2 {
  margin: 0;
  font-size: 24px;
  color: #0f172a;
}

.empty-state p {
  font-size: 14px;
  color: #475569;
}

.empty-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.suggestion-chip {
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(241, 245, 249, 0.6);
  color: #1f2937;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-chip:hover {
  background: rgba(196, 181, 253, 0.2);
  border-color: rgba(129, 140, 248, 0.4);
}

.message-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.message-card.assistant,
.message-card.admin {
  margin-right: auto;
}

.message-card.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.message-avatar {
  width: 46px;
  height: 46px;
  border-radius: 18px;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.9);
  background: #fff;
}

.message-body {
  padding: 18px 22px;
  border-radius: 24px;
  background: rgba(248, 250, 252, 0.92);
  max-width: min(640px, 75vw);
  color: #0f172a;
  line-height: 1.7;
  font-size: 15px;
  position: relative;
}

.message-card.user .message-body {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: #fff;
}

.message-card.admin .message-body {
  background: linear-gradient(135deg, #10b981, #22d3ee);
  color: #fff;
}

.message-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-meta {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
}

.meta-item {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.meta-item.emotion {
  background: rgba(79, 70, 229, 0.16);
  color: #4338ca;
}

.meta-item.time {
  background: transparent;
  color: rgba(15, 23, 42, 0.55);
}

.risk-low {
  background: rgba(34, 197, 94, 0.18);
  color: #15803d;
}

.risk-medium {
  background: rgba(248, 196, 113, 0.24);
  color: #b45309;
}

.risk-high {
  background: rgba(251, 113, 133, 0.24);
  color: #be123c;
}

.risk-critical {
  background: rgba(248, 113, 113, 0.3);
  color: #b91c1c;
}

.message-fade-enter-active,
.message-fade-leave-active {
  transition: all 0.25s ease;
}

.message-fade-enter-from,
.message-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: transparent;
}

.message-list::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.4);
  border-radius: 999px;
}

.composer {
  position: relative;
  width: 100%;
  flex-shrink: 0;
  display: flex;
  justify-content: center;
}

.chat-main.has-messages .composer {
  margin-top: 0;
}

.composer-docked {
  position: sticky;
  bottom: clamp(20px, 3vh, 36px);
  width: min(720px, calc(100% - 64px));
  margin: 0 auto;
  z-index: 25;
}

.composer-docked .composer-card {
  width: 100%;
}

.composer-card {
  background: transparent;
  border-radius: 32px;
  border: none;
  box-shadow: none;
  padding: 0;
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.composer-input {
  background: #ffffff;
  border-radius: 26px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  padding: 24px 26px 16px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.composer-input textarea {
  width: 100%;
  border: none;
  background: transparent;
  resize: none;
  font-family: inherit;
  line-height: 1.6;
  font-size: 16px;
  color: #0f172a;
  max-height: 120px;
  padding: 0;
}

.composer-input textarea:focus {
  outline: none;
}

.composer-input textarea::placeholder {
  color: rgba(71, 85, 105, 0.7);
}

.composer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.composer-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(241, 245, 249, 0.8);
  color: #334155;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: rgba(224, 231, 255, 0.9);
  border-color: rgba(99, 102, 241, 0.45);
  color: #3730a3;
}

.action-icon {
  font-size: 16px;
  line-height: 0.8;
}

.file-input-hidden {
  display: none;
}

.send-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 16px 30px rgba(99, 102, 241, 0.28);
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 22px 40px rgba(99, 102, 241, 0.32);
}

.send-button:disabled {
  background: rgba(148, 163, 184, 0.6);
  box-shadow: none;
  cursor: not-allowed;
}

.send-icon {
  width: 20px;
  height: 20px;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #475569;
  margin-left: 60px;
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

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 1100px) {
  .chat-shell {
    flex-direction: column;
    padding: 0 20px 48px;
    margin: 84px 0 0;
    width: 100%;
    max-width: none;
    margin-left: 0;
    margin-right: 0;
  }

  .chat-sidebar-shell {
    width: 100%;
    flex: none;
    max-width: none;
    min-width: 0;
    margin: 0;
  }

  .chat-hero {
    grid-template-columns: 1fr;
    padding: 32px clamp(20px, 5vw, 32px) calc(32px + clamp(96px, 18vw, 132px));
    background: #ffffff;
  }

  .hero-visual {
    align-items: center;
    align-self: center;
    margin-bottom: 0;
    padding-right: 0;
  }

  .hero-controls {
    gap: 20px;
  }

  .composer-inline {
    max-width: 100%;
  }

  .message-area {
    max-height: none;
  }

  .composer-docked {
    width: min(660px, calc(100% - 40px));
  }

  .typing-indicator {
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .chat-shell {
    padding: 0 16px 48px;
    width: 100%;
    margin-left: 0;
    margin-right: 0;
  }

  .chat-main {
    gap: 20px;
  }

  .chat-hero {
    padding: 28px clamp(18px, 6vw, 28px) calc(28px + clamp(90px, 22vw, 136px));
    border-radius: 28px;
    gap: 18px;
    background: #ffffff;
  }

  .hero-visual {
    min-width: unset;
    align-items: center;
    margin-bottom: 0;
  }

  .hero-left {
    order: -1;
  }

  .hero-subtitle {
    max-width: 100%;
  }

  .hero-meta {
    justify-content: center;
  }

  .hero-controls {
    gap: 18px;
  }

  .composer-inline {
    max-width: 100%;
  }

  .message-area {
    padding: 24px;
    padding-bottom: 24px;
    border-radius: 28px;
  }

  .composer-docked {
    bottom: clamp(16px, 3vh, 28px);
    width: calc(100% - 24px);
    margin: 0 auto;
  }

  .message-body {
    max-width: 100%;
  }

  .composer-card {
    padding: 18px;
  }

  .conversation-header {
    gap: 6px;
  }

  .conversation-meta {
    gap: 6px;
  }
}

@media (max-width: 520px) {
  .chat-shell {
    margin: 72px 12px 32px;
    width: auto;
  }

  .chat-hero {
    padding: 24px clamp(16px, 8vw, 24px) calc(24px + clamp(84px, 26vw, 132px));
    background: #ffffff;
  }

  .hero-controls {
    gap: 12px;
  }

  .composer-inline {
    max-width: 100%;
  }

  .hero-title {
    font-size: 26px;
  }

  .hero-visual {
    min-width: unset;
  }

  .hero-left {
    order: -1;
  }

  .message-area {
    padding: 18px;
    padding-bottom: 18px;
  }

  .message-avatar {
    width: 38px;
    height: 38px;
  }

  .composer-input textarea {
    font-size: 15px;
  }

  .send-button {
    width: 42px;
    height: 42px;
  }

  .typing-indicator {
    margin-left: 0;
  }

  .composer-docked {
    bottom: clamp(14px, 3vh, 24px);
    width: calc(100% - 16px);
    margin: 0 auto;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .message-body,
  .composer-card {
    transition: transform 0.3s ease;
  }

  .message-card.user .message-body:hover,
  .message-card.assistant .message-body:hover,
  .message-card.admin .message-body:hover {
    transform: translateY(-2px);
  }
}
</style>
