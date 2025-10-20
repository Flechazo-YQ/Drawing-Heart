<template>
  <div
    v-show="isVisible"
    class="chat-sidebar"
    :class="[
      isInline ? 'sidebar-inline' : 'sidebar-drawer',
      { 'sidebar-open': !isInline && isOpen }
    ]"
  >
    <div class="sidebar-shell">
      <div class="sidebar-top">
        <button class="new-chat-btn" @click="createNewChat">
          <span class="plus-icon">+</span> 新建会话
        </button>

        <div
          :class="['search-card', { 'search-card-plain': !hasSearched }]"
        >
          <div class="search-bar">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索历史对话"
              @keyup.enter="performSearch"
            />
            <button
              class="search-btn"
              :disabled="!searchQuery.trim()"
              @click="performSearch"
            >
              搜索
            </button>
          </div>
        </div>
      </div>

      <div class="sidebar-content">
        <template v-if="!hasSearched">
          <div class="history-header">
            <span class="history-title">历史会话</span>
            <span class="history-count">{{ filteredChatList.length }} 个</span>
          </div>
          <div class="chat-list">
            <div
              v-for="chat in filteredChatList"
              :key="chat._id"
              :class="['chat-item', {
                'active': currentChatId === chat._id,
                'dangerous': chat.type === 'dangerous' || chat.stats?.isDangerous
              }]"
              @click="loadChat(chat._id)"
            >
              <div class="chat-meta">
                <div class="chat-title">
                  <span
                    v-if="chat.type === 'dangerous' || chat.stats?.isDangerous"
                    class="danger-badge"
                  >⚠️</span>
                  <span class="title-text">{{ chat.title }}</span>
                </div>
                <button
                  class="delete-chat-btn"
                  @click.stop="deleteChat(chat._id)"
                  title="删除对话"
                >🗑️</button>
              </div>
              <div class="chat-info">
                <span class="message-count">{{ chat.stats?.messageCount || 0 }} 条记录</span>
                <span class="chat-time">{{ formatTime(chat.timeNode.updatedAt) }}</span>
              </div>
            </div>
          </div>
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="!loading && filteredChatList.length === 0" class="empty-state">
            暂无聊天记录
          </div>
        </template>

        <template v-else>
          <div class="history-header">
            <span class="history-title">搜索结果</span>
            <span class="history-count">{{ searchResults.length }} 个</span>
          </div>
          <div v-if="searchResults.length" class="chat-list search-mode">
            <div
              v-for="chat in searchResults"
              :key="chat._id"
              :class="['chat-item', {
                'active': currentChatId === chat._id,
                'dangerous': chat.type === 'dangerous' || chat.stats?.isDangerous
              }]"
              @click="loadChat(chat._id)"
            >
              <div class="chat-meta">
                <div class="chat-title">
                  <span
                    v-if="chat.type === 'dangerous' || chat.stats?.isDangerous"
                    class="danger-badge"
                  >⚠️</span>
                  <span class="title-text">{{ chat.title }}</span>
                </div>
                <button
                  class="delete-chat-btn"
                  @click.stop="deleteChat(chat._id)"
                  title="删除对话"
                >🗑️</button>
              </div>
              <div class="chat-info">
                <span class="message-count">{{ chat.stats?.messageCount || 0 }} 条记录</span>
                <span class="chat-time">{{ formatTime(chat.timeNode.updatedAt) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="search-empty">
            <div class="empty-icon">🔍</div>
            <div class="empty-title">没有找到匹配的对话</div>
            <div class="empty-desc">换个关键词试试吧</div>
          </div>
        </template>
      </div>
    </div>
  </div>

  <div
    v-if="!isInline && isOpen"
    class="sidebar-overlay"
    @click="closeSidebar"
  ></div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import config from '@/config'
import navLogo from '@/assets/images/others/Logo.png'

interface Chat {
  _id: string
  userId: string
  adminId: string
  lastMessage: string
  title: string
  type: string  // 对话类型，'dangerous' 表示危险对话
  stats?: {
    messageCount: number
    isDangerous: boolean
    emotionAnalysis: [string]
  }
  timeNode: {
    updatedAt: string
  }
}

const CHAT_TITLE_KEY_PREFIX = 'chatFirstTitle_'
const CHAT_LIST_REFRESH_EVENT = 'chatListRefresh'
const PLACEHOLDER_TITLES = ['新对话', '新会话', '未命名会话']

const hydratedChatIds = new Set<string>()

const sanitizeTitle = (title: string | null | undefined) => {
  const safe = (title ?? '').toString()
  return safe.replace(/\s+/g, ' ').trim()
}

const isPlaceholderTitle = (title?: string) => {
  const normalized = sanitizeTitle(title)
  if (!normalized) return true
  return PLACEHOLDER_TITLES.includes(normalized)
}

const getStoredChatTitle = (chatId: string) => {
  if (!chatId) return ''
  return localStorage.getItem(`${CHAT_TITLE_KEY_PREFIX}${chatId}`) || ''
}

const applyTitleOverride = (chat: Chat) => {
  const stored = sanitizeTitle(getStoredChatTitle(chat._id))
  const fallback = isPlaceholderTitle(chat.title) ? '' : sanitizeTitle(chat.title)
  const resolved = stored || fallback || '未命名会话'
  return { ...chat, title: resolved }
}

const emitChatTitleUpdate = (chatId: string, title: string) => {
  document.dispatchEvent(new CustomEvent('chatTitleUpdated', {
    detail: { chatId, title }
  }))
}

const persistChatTitleLocally = (chatId: string, rawTitle: string) => {
  const normalized = sanitizeTitle(rawTitle)
  if (isPlaceholderTitle(normalized)) return
  const key = `${CHAT_TITLE_KEY_PREFIX}${chatId}`
  const existing = localStorage.getItem(key)
  if (existing !== normalized) {
    localStorage.setItem(key, normalized)
  }
  emitChatTitleUpdate(chatId, normalized)
}

const extractFirstUserMessage = (messages: any[]) => {
  if (!Array.isArray(messages)) return ''
  const target = messages.find((msg) => {
    const sender = msg?.sender ?? msg?.type
    const content = typeof msg?.content === 'string' ? msg.content.trim() : ''
    return sender === 'user' && content
  })
  return target ? target.content : ''
}

const hydrateMissingTitles = async (list: Chat[]) => {
  const token = localStorage.getItem('token')
  for (const chat of list) {
    if (hydratedChatIds.has(chat._id)) continue

    const stored = sanitizeTitle(getStoredChatTitle(chat._id))
    if (!isPlaceholderTitle(stored) || !isPlaceholderTitle(chat.title)) {
      hydratedChatIds.add(chat._id)
      continue
    }

    try {
      const response = await fetch(`${config.baseURL}/api/chats/${chat._id}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': token || '',
          'Content-Type': 'application/json'
        }
      })

      const result = await response.json()

      if (result.code === 0 && Array.isArray(result.data?.messages)) {
        const firstQuestion = sanitizeTitle(extractFirstUserMessage(result.data.messages))
        if (!isPlaceholderTitle(firstQuestion)) {
          persistChatTitleLocally(chat._id, firstQuestion)
        }
      }
    } catch (error) {
      console.error('补全对话标题失败:', error)
    } finally {
      hydratedChatIds.add(chat._id)
    }
  }
}

const props = withDefaults(defineProps<{
  isOpen: boolean
  displayMode?: 'inline' | 'drawer'
}>(), {
  displayMode: 'drawer'
})

const emit = defineEmits<{
  close: []
  chatLoaded: [chatId: string, messagesList: any[], chatInfo?: any]
  newChat: [chatId: string]
}>()

const chatList = ref<Chat[]>([])
const loading = ref(false)
const currentChatId = ref<string>('')
const searchQuery = ref('')
const hasSearched = ref(false)
const filteredChatList = computed(() =>
  chatList.value.filter(chat => (chat.stats?.messageCount || 0) > 0)
)

const searchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  const keyword = searchQuery.value.trim().toLowerCase()
  return filteredChatList.value.filter(chat => {
    const titleMatch = chat.title?.toLowerCase().includes(keyword)
    const countMatch = `${chat.stats?.messageCount || 0}`.includes(keyword)
    return titleMatch || countMatch
  })
})

const isInline = computed(() => props.displayMode === 'inline')
const isVisible = computed(() => isInline.value || props.isOpen)

// 获取聊天列表
const fetchChatList = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('token')

    const response = await fetch(`${config.baseURL}/api/chats/list`, {
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json'
      }
    })

    const result = await response.json()

    if (result.code === 0) {
      const sourceList: Chat[] = result.data.chats || []
      chatList.value = sourceList.map(applyTitleOverride)
      void hydrateMissingTitles([...chatList.value])
    } else {
      ElMessage.error(result.message || '获取聊天列表失败')
    }
  } catch (error) {
    console.error('获取聊天列表失败:', error)
    ElMessage.error('获取聊天列表失败')
  } finally {
    loading.value = false
  }
}

// 创建新对话
const createNewChat = async () => {
  try {
    const token = localStorage.getItem('token')

    const response = await fetch(`${config.baseURL}/api/chats`, {
      method: 'POST',
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: '新对话'
      })
    })

    const result = await response.json()

    if (result.code === 0) {
      currentChatId.value = result.data.chatId
      ElMessage.success('创建新对话成功')
      await fetchChatList()
      emit('newChat', result.data.chatId)
    } else {
      ElMessage.error(result.message || '创建新对话失败')
    }
  } catch (error) {
    console.error('创建新对话失败:', error)
    ElMessage.error('创建新对话失败')
  }
}

// 加载对话
const loadChat = async (chatId: string) => {
  try {
    const token = localStorage.getItem('token')

    const response = await fetch(`${config.baseURL}/api/chats/${chatId}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json'
      }
    })

    const result = await response.json()
    console.log(result)
    if (result.code === 0) {
      currentChatId.value = chatId
      ElMessage.success('加载对话成功')
      // 查找当前 chat 的完整信息
      const chatInfo = chatList.value.find(chat => chat._id === chatId) || null
      emit('chatLoaded', chatId, Array.isArray(result.data.messages) ? result.data.messages : [], chatInfo)
    } else {
      ElMessage.error(result.message || '加载对话失败')
    }
  } catch (error) {
    console.error('加载对话失败:', error)
    ElMessage.error('加载对话失败')
  }
}

// 删除对话
const deleteChat = async (chatId: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个对话吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const token = localStorage.getItem('token')

    const response = await fetch(`${config.baseURL}/api/chats/${chatId}/hide`, {
      method: 'DELETE',
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({chatId})
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => null)
      const errorMessage = errorData ? errorData.message : `服务器错误，状态码: ${response.status}`
      throw new Error(errorMessage)
    }

    const result = await response.json()

    if (result.code === 0) {
      ElMessage.success('删除对话成功')
      localStorage.removeItem(`${CHAT_TITLE_KEY_PREFIX}${chatId}`)
      await fetchChatList()

      // 如果删除的是当前对话，清空当前对话ID
      if (currentChatId.value === chatId) {
        currentChatId.value = ''
        emit('newChat', '') // 触发创建新对话
      }
    } else {
      ElMessage.error(result.message || '删除对话失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除对话失败:', error)
      ElMessage.error('删除对话失败')
    }
  }
}

const performSearch = () => {
  const trimmed = searchQuery.value.trim()
  hasSearched.value = Boolean(trimmed)
}

const handleChatTitleUpdated = (event: Event) => {
  const detail = (event as CustomEvent<{ chatId: string; title?: string }>).detail
  if (!detail?.chatId) return

  const incoming = detail.title ? sanitizeTitle(detail.title) : ''
  const index = chatList.value.findIndex(chat => chat._id === detail.chatId)
  if (index === -1) return

  const current = chatList.value[index]
  const fallback = isPlaceholderTitle(current.title) ? '' : sanitizeTitle(current.title)
  const resolved = incoming || fallback || '未命名会话'
  chatList.value = chatList.value.map((chat, idx) =>
    idx === index ? { ...chat, title: resolved } : chat
  )
}

const handleChatListRefresh = (event: Event) => {
  const detail = (event as CustomEvent<{ chatId?: string }>).detail
  void fetchChatList().then(() => {
    if (detail?.chatId) {
      currentChatId.value = detail.chatId
    }
  })
}

// 格式化时间
const formatTime = (timeString: string) => {
  const date = new Date(timeString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 如果是今天
  if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  // 如果是昨天
  else if (diff < 48 * 60 * 60 * 1000 && date.getDate() === now.getDate() - 1) {
    return '昨天'
  }
  // 其他时间显示日期
  else {
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }
}

// 关闭侧边栏
const closeSidebar = () => {
  emit('close')
}

// 监听侧边栏可见状态
watch(isVisible, (visible) => {
  if (visible) {
    fetchChatList()
  }
}, { immediate: true })

watch(searchQuery, (value) => {
  if (!value.trim()) {
    hasSearched.value = false
  }
})

onMounted(() => {
  document.addEventListener('chatTitleUpdated', handleChatTitleUpdated)
  document.addEventListener(CHAT_LIST_REFRESH_EVENT, handleChatListRefresh)
})

onUnmounted(() => {
  document.removeEventListener('chatTitleUpdated', handleChatTitleUpdated)
  document.removeEventListener(CHAT_LIST_REFRESH_EVENT, handleChatListRefresh)
})
</script>

<style scoped>
.chat-sidebar {
  background: #ffffff;
  border-right: 1px solid rgba(148, 163, 184, 0.18);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
}

.chat-sidebar.sidebar-drawer {
  position: fixed;
  inset: 0 auto 0 0;
  width: 320px;
  transform: translateX(-100%);
  z-index: 1100;
  box-shadow: 24px 0 48px rgba(15, 23, 42, 0.08);
}

.chat-sidebar.sidebar-drawer.sidebar-open {
  transform: translateX(0);
}

.chat-sidebar.sidebar-inline {
  position: sticky;
  top: 64px;
  width: 292px;
  height: calc(100vh - 64px);
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  z-index: 1000;
}

.sidebar-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 18px 14px 20px;
  gap: 16px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 48px rgba(148, 163, 184, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.sidebar-top {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex-shrink: 0;
}

.close-btn:hover {
  background: rgba(17, 24, 39, 0.08);
  color: #111827;
}

.new-chat-btn {
  width: 100%;
  border: none;
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #2563eb, #4338ca);
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.25);
}

.new-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 32px rgba(37, 99, 235, 0.28);
}

.plus-icon {
  font-size: 16px;
}


.search-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: 0 16px 32px rgba(15, 23, 42, 0.04);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.search-card-plain {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.24);
}

.search-icon {
  font-size: 15px;
  color: #94a3b8;
}

.search-bar input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 13px;
  color: #1f2937;
}

.search-bar input::placeholder {
  color: #9ca3af;
}

.search-btn {
  border: none;
  border-radius: 10px;
  padding: 6px 10px;
  background: #2563eb;
  color: #ffffff;
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.search-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.search-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.suggestion-btn {
  border: none;
  border-radius: 12px;
  padding: 5px 8px;
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.suggestion-btn:hover {
  background: rgba(37, 99, 235, 0.2);
}

.sidebar-content {
  flex: 1;
  min-height: 0;
  background: transparent;
  border-radius: 18px;
  border: none;
  padding: 16px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: none;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2px;
  color: #6b7280;
  font-size: 12px;
}

.history-title {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
}

.history-count {
  font-size: 11px;
  color: #9ca3af;
}

.chat-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-right: 2px;
}

.chat-item {
  border-radius: 13px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  padding: 10px 11px;
  background: rgba(248, 250, 252, 0.9);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border 0.2s ease, transform 0.2s ease, background 0.2s ease;
}

.chat-item:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.5);
  background: #ffffff;
}

.chat-item.active {
  border-color: rgba(59, 130, 246, 0.8);
  background: #ffffff;
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.15);
}

.chat-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
}

.chat-title {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.chat-title .title-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-info {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #6b7280;
}

.message-count {
  color: #2563eb;
  font-weight: 500;
}

.chat-time {
  color: #9ca3af;
}

.delete-chat-btn {
  border: none;
  background: transparent;
  color: #d97706;
  font-size: 13px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.chat-item:hover .delete-chat-btn,
.chat-item.active .delete-chat-btn {
  opacity: 1;
}

.loading,
.empty-state {
  text-align: center;
  padding: 18px 0;
  color: #9ca3af;
  font-size: 12px;
}

.search-mode {
  background: #f8fafc;
  border-radius: 10px;
  padding: 6px;
}

.search-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #9ca3af;
}

.empty-icon {
  font-size: 24px;
}

.empty-title {
  font-weight: 600;
  color: #1f2937;
}

.empty-desc {
  font-size: 12px;
}

.danger-badge {
  color: #f97316;
  font-size: 12px;
}

.chat-list::-webkit-scrollbar {
  width: 6px;
}

.chat-list::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.4);
  border-radius: 3px;
}

.chat-list::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 116, 139, 0.6);
}

@media (max-width: 1024px) {
  .chat-sidebar.sidebar-inline {
    top: 64px;
    width: 100%;
    height: auto;
    position: static;
  }

  .sidebar-shell {
    padding: 16px 12px 20px;
  }
}
</style>
