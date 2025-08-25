<template>
  <nav class="modern-nav">
    <div class="nav-content">
      <div class="nav-logo">
        <img src="@/assets/images/others/Logo.png" alt="绘心同学" class="logo-img" />
        <span>绘心同学</span>
      </div>
      <div class="nav-actions">
        <router-link to="/" class="nav-link" :class="{ active: route.path === '/' }">首页</router-link>
        <router-link to="/draw" class="nav-link" :class="{ active: route.path === '/draw' }">绘画空间</router-link>
        <router-link to="/chat" class="nav-link" :class="{ active: route.path === '/chat' }">心理对话</router-link>
        <router-link to="/map" class="nav-link" :class="{ active: route.path === '/map' }">附近心理</router-link>

        <!-- 用户头像区域 -->
        <div class="user-avatar-container" @click="toggleSidebar">
          <img :src="userAvatar" :alt="userName" :key="avatarKey" class="user-avatar" @error="handleAvatarError" />
          <span class="user-name">{{ userName }}</span>
          <svg class="dropdown-icon" :class="{ 'rotate': showSidebar }" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M7 10l5 5 5-5z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 侧边栏遮罩 -->
    <div v-if="showSidebar" class="sidebar-overlay" @click="closeSidebar"></div>

    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ 'sidebar-open': showSidebar }">
      <div class="sidebar-header">
        <div class="sidebar-user-info">
          <div class="avatar-upload-container" @click="triggerAvatarUpload">
            <img :src="userAvatar" :alt="userName" :key="avatarKey" class="sidebar-avatar" @error="handleAvatarError" />
            <div class="avatar-overlay">
              <svg class="upload-icon" viewBox="0 0 24 24" width="24" height="24">
                <path fill="currentColor" d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"/>
              </svg>
              <span>更换头像</span>
            </div>
          </div>
          <div class="sidebar-user-details">
            <h3>{{ userName }}</h3>
            <p>{{ userEmail }}</p>
          </div>
        </div>
        <!-- 隐藏的文件输入 -->
        <input
          ref="avatarInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleAvatarUpload"
        />
      </div>

      <div class="sidebar-content">
        <div class="sidebar-section">
          <router-link to="/user" class="sidebar-item" @click="closeSidebar">
            <svg class="sidebar-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
            <span>个人信息</span>
          </router-link>

          <div class="sidebar-item disabled">
            <svg class="sidebar-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>我的记录</span>
            <span class="coming-soon">敬请期待</span>
          </div>

          <div class="sidebar-item disabled">
            <svg class="sidebar-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            <span>我的收藏</span>
            <span class="coming-soon">敬请期待</span>
          </div>

          <div class="sidebar-item disabled">
            <svg class="sidebar-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            <span>设置</span>
            <span class="coming-soon">敬请期待</span>
          </div>
        </div>
      </div>

      <div class="sidebar-footer">
        <button class="logout-button" @click="handleLogout">
          <svg class="sidebar-icon" viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.59L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
          </svg>
          退出登录
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 导入默认头像图片
import boyAvatar from '@/assets/images/avatars/Boy.png'
import girlAvatar from '@/assets/images/avatars/Girl.png'

import socket from '@/utils/network'

const route = useRoute()
const router = useRouter()

// 侧边栏状态
const showSidebar = ref(false)

// 用户信息
const userName = ref('用户')
const userEmail = ref('')
const userAvatar = ref('/images/default-avatar.jpg')
const avatarInput = ref(null)
const isUploading = ref(false)
const avatarKey = ref(0) // 用于强制刷新头像显示

// 获取用户信息
const getUserInfo = () => {
  const userInfo = localStorage.getItem('userInfo')
  console.log('NavBarUser - 获取用户信息:', userInfo)

  if (userInfo) {
    const user = JSON.parse(userInfo)
    console.log('NavBarUser - 解析后的用户信息:', user)
    console.log('NavBarUser - 用户性别:', user.profile?.gender)

    userName.value = user.name || '用户'
    userEmail.value = user.email || ''

    // 优先使用用户上传的头像
    if (user.profile?.avatar && user.profile.avatar.trim() !== '') {
      let avatarUrl = user.profile.avatar

      // 检查是否是相对路径 (以 /uploads/ 开头)
      if (avatarUrl.startsWith('/uploads/')) {
        // 从环境变量或默认值获取后端API地址
        const backendUrl = import.meta.env.VITE_API_BASE_URL || ' http://localhost:5000'
        // 组合成完整的绝对URL
        userAvatar.value = `${backendUrl}${avatarUrl}`
        console.log('NavBarUser - 设置用户头像的完整URL:', userAvatar.value)
      } else {
        // 如果已经是完整URL或其他格式，直接使用
        userAvatar.value = avatarUrl
        console.log('NavBarUser - 直接使用头像URL:', userAvatar.value)
      }
    } else {
      // 如果没有用户头像，根据性别使用默认头像
      userAvatar.value = generateAvatarUrl(userName.value)
      console.log('NavBarUser - 使用默认头像:', userAvatar.value)
    }
  } else {
    console.log('NavBarUser - 没有找到用户信息')
  }
}

// 根据用户性别生成默认头像
const generateAvatarUrl = (name) => {
  // 从localStorage获取用户信息，检查性别
  const userInfo = localStorage.getItem('userInfo')
  console.log('NavBarUser - generateAvatarUrl - 用户信息:', userInfo)

  if (userInfo) {
    const user = JSON.parse(userInfo)
    console.log('NavBarUser - generateAvatarUrl - 解析后用户信息:', user)
    console.log('NavBarUser - generateAvatarUrl - 用户性别:', user.profile?.gender)

    // 根据性别返回不同的默认头像
    if (user.profile?.gender === 'male') {
      console.log('NavBarUser - generateAvatarUrl - 返回男性头像:', boyAvatar)
      return boyAvatar
    } else if (user.profile?.gender === 'female') {
      console.log('NavBarUser - generateAvatarUrl - 返回女性头像:', girlAvatar)
      return girlAvatar
    }
  }

  // 如果无法确定性别或没有用户信息，使用字母头像作为备选
  const firstChar = (name || '用').charAt(0).toUpperCase()
  const letterAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(firstChar)}&size=60&background=42b983&color=ffffff&rounded=true`
  console.log('NavBarUser - generateAvatarUrl - 返回字母头像:', letterAvatar)
  return letterAvatar
}

// 处理头像加载失败
const handleAvatarError = (event) => {
  // 记录加载失败的URL
  console.error('头像加载失败:', event.target.src.substring(0, 50) + '...')

  // 获取用户信息（只声明一次）
  const userInfoStr = localStorage.getItem('userInfo')
  let userInfo = null
  if (userInfoStr) {
    try {
      userInfo = JSON.parse(userInfoStr)
    } catch (e) {
      console.error('解析用户信息失败:', e)
    }
  }

  // 如果之前已经尝试过修复，避免无限循环
  if (event.target.getAttribute('data-tried') === 'true') {
    // 最终失败，使用基于性别的默认头像
    console.log('尝试过所有修复方法，使用默认头像')
    console.log('NavBarUser - 用户信息:', userInfo)
    console.log('NavBarUser - 用户性别:', userInfo?.profile?.gender)

    if (userInfo && userInfo.profile?.gender === 'male') {
      console.log('NavBarUser - 设置男性默认头像:', boyAvatar)
      event.target.src = boyAvatar
    } else if (userInfo && userInfo.profile?.gender === 'female') {
      console.log('NavBarUser - 设置女性默认头像:', girlAvatar)
      event.target.src = girlAvatar
    } else {
      // 使用字母头像作为最终备选
      const firstChar = (userName.value || '用').charAt(0).toUpperCase()
      const letterAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(firstChar)}&size=60&background=42b983&color=ffffff&rounded=true`
      console.log('NavBarUser - 使用字母头像:', letterAvatar)
      event.target.src = letterAvatar
    }
    return
  }

  // 标记这个元素已经尝试过修复
  event.target.setAttribute('data-tried', 'true')

  // 方式1: 尝试使用原始头像URL
  if (userInfo && userInfo.profile?.avatar && userInfo.profile.avatar.trim() !== '') {
    let newSrc = userInfo.profile.avatar

    // 检查是否是相对路径 (以 /uploads/ 开头)
    if (newSrc.startsWith('/uploads/')) {
      // 从环境变量或默认值获取后端API地址
      const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
      // 组合成完整的绝对URL
      newSrc = `${backendUrl}${newSrc}`
    }

    console.log('尝试使用存储的原始URL:', newSrc)
    event.target.src = newSrc
    return
  }

  // 方式2: 尝试移除时间戳参数
  if (event.target.src.includes('?')) {
    const withoutParams = event.target.src.split('?')[0]
    console.log('尝试去除URL参数:', withoutParams)
    event.target.src = withoutParams
    return
  }

  // 最后使用基于性别的默认头像
  console.log('无法加载头像，使用基于性别的默认头像')
  console.log('NavBarUser - 最终处理 - 用户信息:', userInfo)
  console.log('NavBarUser - 最终处理 - 用户性别:', userInfo?.profile?.gender)

  if (userInfo && userInfo.profile?.gender === 'male') {
    console.log('NavBarUser - 最终设置男性头像:', boyAvatar)
    event.target.src = boyAvatar
  } else if (userInfo && userInfo.profile?.gender === 'female') {
    console.log('NavBarUser - 最终设置女性头像:', girlAvatar)
    event.target.src = girlAvatar
  } else {
    // 使用字母头像作为最终备选
    const firstChar = (userName.value || '用').charAt(0).toUpperCase()
    const letterAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(firstChar)}&size=60&background=42b983&color=ffffff&rounded=true`
    console.log('NavBarUser - 最终使用字母头像:', letterAvatar)
    event.target.src = letterAvatar
  }
}

// 触发头像上传
const triggerAvatarUpload = () => {
  // 先尝试刷新当前头像
  refreshAvatar()

  // 然后弹出文件选择框
  if (avatarInput.value) {
    avatarInput.value.click()
  }
}

// 处理头像上传
const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }

  // 验证文件大小 (限制为5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过5MB')
    return
  }

  try {
    isUploading.value = true

    // 创建FormData
    const formData = new FormData()
    formData.append('avatar', file)

    // 获取用户token
    const token = localStorage.getItem('token')
    if (!token) {
      alert('请先登录')
      return
    }

    // 上传头像
    const response = await fetch('/api/avatar/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    // 检查响应状态
    if (response.status === 401) {
      // 令牌无效或过期，提示用户重新登录
      alert('登录已过期，请重新登录')
      // 清除本地存储的令牌和用户信息
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('isLoggedIn')
      // 跳转到登录页面
      router.push('/login')
      return
    }

    const result = await response.json()
    console.log('头像上传响应:', result)

    if (result.code === 0) {
      // 获取返回的头像URL
      const returnedAvatarUrl = result.data.avatarUrl
      console.log('服务器返回的头像URL:', returnedAvatarUrl)

      // 从环境变量或默认值获取后端API地址
      const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

      // 立即更新头像显示
      if (returnedAvatarUrl.startsWith('/uploads/')) {
        // 如果是相对路径，组合成完整URL
        userAvatar.value = `${backendUrl}${returnedAvatarUrl}`
      } else {
        // 如果已经是完整URL，直接使用
        userAvatar.value = returnedAvatarUrl
      }

      // 强制刷新头像组件，只刷新一次
      avatarKey.value += 1

      // 更新localStorage中的用户信息
      let userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      if (!userInfo.profile) {
        userInfo.profile = {}
      }
      userInfo.profile.avatar = returnedAvatarUrl // 存储从后端获取的原始相对路径
      localStorage.setItem('userInfo', JSON.stringify(userInfo))

      // 发出全局事件通知其他组件刷新头像
      document.dispatchEvent(new CustomEvent('refreshAvatar'))

      console.log('头像更新成功:', userAvatar.value)
      ElMessage.success('头像上传成功')
    } else {
      if (result.message && result.message.includes('Invalid token')) {
        // 处理无效令牌
        alert('登录已过期，请重新登录')
        // 清除本地存储的令牌和用户信息
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('isLoggedIn')
        // 跳转到登录页面
        router.push('/login')
      } else {
        alert(result.message || '头像上传失败')
      }
    }
  } catch (error) {
    console.error('头像上传错误:', error)
    alert('网络错误，请稍后重试')
  } finally {
    isUploading.value = false
    // 清空input值，允许重复上传同一文件
    if (avatarInput.value) {
      avatarInput.value.value = ''
    }
  }
}

// 切换侧边栏
const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}

// 关闭侧边栏
const closeSidebar = () => {
  showSidebar.value = false
}

// 退出登录处理
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('isLoggedIn')
  // 清理聊天相关数据
  localStorage.removeItem('chatHistory')
  localStorage.removeItem('currentSessionId')

  if (socket && socket.connected) {
    socket.removeAllListeners(); // 移除所有事件监听
    socket.disconnect();
  }

  closeSidebar()
  router.push('/login')
}

// 组件挂载时获取用户信息
onMounted(() => {
  getUserInfo()

  // 添加手动刷新功能
  document.addEventListener('refreshAvatar', () => {
    console.log('触发手动刷新头像')
    refreshAvatar()
  })
})

// 手动刷新头像
const refreshAvatar = () => {
  console.log('执行手动刷新头像')
  getUserInfo()
  avatarKey.value += 1
}
</script>

<style scoped>
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
  transform: translateY(0px);
}

/* 用户头像区域 */
.user-avatar-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(66, 185, 131, 0.05);
}

.user-avatar-container:hover {
  background: rgba(66, 185, 131, 0.1);
  transform: translateY(-1px);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #42b983;
}

.user-name {
  color: #1a1a1a;
  font-size: 0.9rem;
  font-weight: 500;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  color: #6b7280;
  transition: transform 0.2s;
}

.dropdown-icon.rotate {
  transform: rotate(180deg);
}

/* 侧边栏遮罩 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 150;
}

/* 侧边栏 */
.sidebar {
  position: fixed;
  top: 0;
  right: -350px;
  width: 320px;
  height: 100vh;
  background: #ffffff;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  z-index: 200;
  display: flex;
  flex-direction: column;
}

.sidebar-open {
  right: 0;
}

/* 侧边栏头部 */
.sidebar-header {
  padding: 1.5rem 1.5rem 1.5rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.sidebar-user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar-upload-container {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-upload-container:hover .avatar-overlay {
  opacity: 1;
}

.sidebar-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #42b983;
  transition: filter 0.2s;
}

.avatar-upload-container:hover .sidebar-avatar {
  filter: brightness(0.7);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 50%;
}

.upload-icon {
  color: white;
  margin-bottom: 4px;
}

.avatar-overlay span {
  color: white;
  font-size: 0.7rem;
  font-weight: 500;
  text-align: center;
}

.sidebar-user-details h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.1rem;
  font-weight: 600;
}

.sidebar-user-details p {
  margin: 0.25rem 0 0 0;
  color: #6b7280;
  font-size: 0.875rem;
}

/* 侧边栏内容 */
.sidebar-content {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.sidebar-section {
  padding: 0 1rem;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  color: #4a4a4a;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}

.sidebar-item:hover:not(.disabled) {
  background: rgba(66, 185, 131, 0.1);
  color: #42b983;
  transform: translateX(4px);
}

.sidebar-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  position: relative;
}

.sidebar-icon {
  color: currentColor;
  flex-shrink: 0;
}

.sidebar-item span {
  font-size: 0.95rem;
  font-weight: 500;
}

.coming-soon {
  margin-left: auto;
  font-size: 0.75rem !important;
  background: #f3f4f6;
  color: #6b7280 !important;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-weight: 400 !important;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.logout-button {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: none;
  border: 1px solid #ef4444;
  color: #ef4444;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-button:hover {
  background: #ef4444;
  color: white;
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-name {
    display: none;
  }

  .sidebar {
    width: 100vw;
    right: -100vw;
  }

  .user-avatar-container {
    padding: 0.5rem;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #42b983;
    display: block; /* 确保在移动端显示 */
  }

  .sidebar-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #42b983;
    display: block; /* 确保在移动端显示 */
  }
}
</style>
