<template>
  <div class="chat-sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-header">
      <h3>聊天历史</h3>
      <button class="new-chat-btn" @click="createNewChat">
        <span class="plus-icon">+</span> 新建对话
      </button>
      <button class="close-btn" @click="closeSidebar">×</button>
    </div>
    
    <div class="chat-list">
      <div 
        v-for="chat in chatList" 
        :key="chat._id"
        :class="['chat-item', { 'active': currentChatId === chat._id, 'dangerous': chat.type === 'dangerous' }]"
        @click="loadChat(chat._id)"
      >
        <div class="chat-title">
          <span v-if="chat.type === 'dangerous'" class="danger-badge">⚠️</span>
          {{ chat.title }}
        </div>
        <div class="chat-info">
          <span class="message-count">{{ chat.message_count }}条消息</span>
          <span class="chat-time">{{ formatTime(chat.updated_at) }}</span>
        </div>
        <button 
          class="delete-chat-btn" 
          @click.stop="deleteChat(chat._id)"
          title="删除对话"
        >
          🗑️
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-if="!loading && chatList.length === 0" class="empty-state">
      暂无聊天记录
    </div>
  </div>
  
  <div v-if="isOpen" class="sidebar-overlay" @click="closeSidebar"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import config from '@/config'

interface Chat {
  _id: string
  title: string
  message_count: number
  updated_at: string
  created_at: string
  type?: string  // 对话类型，'dangerous' 表示危险对话
}

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  close: []
  chatLoaded: [chatId: string]
  newChat: [chatId: string]
}>()

const chatList = ref<Chat[]>([])
const loading = ref(false)
const currentChatId = ref<string>('')

// 获取聊天列表
const fetchChatList = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('token')
    
    const response = await fetch(`${config.baseURL}/api/chats`, {
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json'
      }
    })
    
    const result = await response.json()
    
    if (result.code === 0) {
      chatList.value = result.data
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
      currentChatId.value = result.data.chat_id
      ElMessage.success('创建新对话成功')
      await fetchChatList()
      emit('newChat', result.data.chat_id)
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
    
    const response = await fetch(`${config.baseURL}/api/chats/${chatId}/load`, {
      method: 'POST',
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json'
      }
    })
    
    const result = await response.json()
    
    if (result.code === 0) {
      currentChatId.value = chatId
      ElMessage.success('加载对话成功')
      emit('chatLoaded', chatId)
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
    
    const response = await fetch(`${config.baseURL}/api/chats/${chatId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json'
      }
    })
    
    const result = await response.json()
    
    if (result.code === 0) {
      ElMessage.success('删除对话成功')
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

// 监听侧边栏开启状态
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    fetchChatList()
  }
})

onMounted(() => {
  if (props.isOpen) {
    fetchChatList()
  }
})
</script>

<style scoped>
.chat-sidebar {
  position: fixed;
  top: 0;
  left: -350px;
  width: 350px;
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid #e6e6e6;
  transition: left 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-open {
  left: 0;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
  background: #f8f9fa;
  position: relative;
}

.sidebar-header h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.new-chat-btn {
  width: 100%;
  padding: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.new-chat-btn:hover {
  background: #0056b3;
}

.plus-icon {
  font-size: 16px;
  margin-right: 5px;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.chat-item {
  padding: 15px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  background: #ffffff;
}

.chat-item:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.chat-item.active {
  background: #e3f2fd;
  border-color: #007bff;
}

.chat-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.message-count {
  color: #007bff;
}

.chat-time {
  color: #999;
}

.delete-chat-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  width: 25px;
  height: 25px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-item:hover .delete-chat-btn {
  opacity: 1;
}

.delete-chat-btn:hover {
  background: #ffebee;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 14px;
}

/* 滚动条样式 */
.chat-list::-webkit-scrollbar {
  width: 6px;
}

.chat-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 危险对话样式 */
.chat-item.dangerous {
  border-left: 3px solid #ff4757;
  background: linear-gradient(90deg, #fff5f5 0%, #ffffff 100%);
}

.chat-item.dangerous:hover {
  background: linear-gradient(90deg, #ffebee 0%, #f8f9fa 100%);
}

.danger-badge {
  color: #ff4757;
  margin-right: 5px;
  font-size: 12px;
}
</style>
