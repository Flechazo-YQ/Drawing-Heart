<template>
  <div class="user-container">
    <NavBarUser />

    <main class="user-content">
      <div class="profile-section">
        <div class="profile-header">
          <div class="avatar-upload-container" @click="triggerAvatarUpload">
            <img
              v-if="userAvatar"
              :src="userAvatar"
              :key="`avatar-${avatarKey}-${userAvatar}`"
              alt="用户头像"
              class="avatar"
              @error="handleAvatarError"
              @load="(e) => console.log('UserView - 头像加载成功:', e.target.src)"
            />
            <div v-else class="avatar-placeholder">
              <span>加载中...</span>
            </div>
            <div class="avatar-overlay">
              <svg class="upload-icon" viewBox="0 0 24 24" width="32" height="32">
                <path fill="currentColor" d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z" />
              </svg>
              <span>更换头像</span>
            </div>
          </div>
          <h1 class="username">{{ userInfo.name || '用户' }}</h1>
        </div>        <!-- 隐藏的文件输入 -->
        <input
          ref="avatarInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleAvatarUpload"
        />

        <div class="info-cards">
          <div class="info-card">
            <h3 class="card-title">个人信息</h3>
            <div class="info-content">
              <div class="info-item">
                <span class="label">用户名</span>
                <span class="value">{{ userInfo.name || '用户' }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱</span>
                <span class="value">{{ userInfo.email || '' }}</span>
              </div>
              <div class="info-item">
                <span class="label">性别</span>
                <span class="value">{{ userInfo.profile?.gender === 'male' ? '男' : '女' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue' // 1. 引入 onUnmounted
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBarUser from '@/components/NavBarUser.vue'
import config from '@/config'

// 导入默认头像图片
import boyAvatar from '@/assets/images/avatars/Boy.png'
import girlAvatar from '@/assets/images/avatars/Girl.png'

const router = useRouter()
const userInfo = ref({})
const userAvatar = ref(boyAvatar) // 设置默认的男性头像作为初始值
const avatarInput = ref(null)
const isUploading = ref(false)
const avatarKey = ref(0)

// 根据用户性别生成默认头像
const generateAvatarUrl = (name, gender) => {
  console.log('generateAvatarUrl - 姓名:', name, '性别:', gender)

  if (gender === 'male') {
    console.log('generateAvatarUrl - 返回男性头像:', boyAvatar)
    return boyAvatar
  } else if (gender === 'female') {
    console.log('generateAvatarUrl - 返回女性头像:', girlAvatar)
    return girlAvatar
  }

  // 备用字母头像
  const firstChar = (name || '用').charAt(0).toUpperCase()
  const letterAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(
    firstChar
  )}&size=160&background=42b983&color=ffffff&rounded=true`
  console.log('generateAvatarUrl - 返回字母头像:', letterAvatar)
  return letterAvatar
}

const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    const createCacheBustedUrl = (path) => {
        if (!path || typeof path !== 'string') return null;
        const backendUrl = config.baseURL || 'http://localhost:5000';
        const fullUrl = path.startsWith('/uploads/') ? `${backendUrl}${path}` : path;
        return fullUrl.split('?')[0] + '?t=' + new Date().getTime();
    }

    // 从 localStorage 获取基本信息以快速显示
    const localUserInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    if (localUserInfo && localUserInfo.profile?.avatar) {
        const bustedUrl = createCacheBustedUrl(localUserInfo.profile.avatar)
        if (bustedUrl) userAvatar.value = bustedUrl;
    }
    console.log('UserView - 获取到的本地用户信息:', localUserInfo)

    if (localUserInfo) {
      userInfo.value = localUserInfo

      if (localUserInfo.profile?.avatar && localUserInfo.profile.avatar.trim() !== '') {
        let avatarUrl = localUserInfo.profile.avatar
        if (avatarUrl.startsWith('/uploads/')) {
          const backendUrl = config.baseURL || 'http://localhost:5000'
          userAvatar.value = `${backendUrl}${avatarUrl}`
        } else {
          userAvatar.value = avatarUrl
        }
        console.log('UserView - 使用用户上传的头像:', userAvatar.value)
      } else {
        console.log('UserView - 用户性别:', localUserInfo.profile?.gender)
        // 强制设置性别头像，确保移动端能正确显示
        if (localUserInfo.profile?.gender === 'male') {
          userAvatar.value = boyAvatar
          console.log('UserView - 设置男性默认头像:', boyAvatar)
        } else if (localUserInfo.profile?.gender === 'female') {
          userAvatar.value = girlAvatar
          console.log('UserView - 设置女性默认头像:', girlAvatar)
        } else {
          // 如果没有性别信息，根据用户名首字母生成
          const firstChar = (localUserInfo.name || '用').charAt(0).toUpperCase()
          userAvatar.value = `https://ui-avatars.com/api/?name=${encodeURIComponent(firstChar)}&size=160&background=42b983&color=ffffff&rounded=true`
          console.log('UserView - 设置字母头像:', userAvatar.value)
        }
      }
    } else {
      // 如果没有本地用户信息，设置默认头像
      console.log('UserView - 没有本地用户信息，使用默认头像')
      userAvatar.value = boyAvatar
    }

    // 然后从服务器获取最新信息
    const response = await fetch(`${config.baseURL}/api/info`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login')
      }
      throw new Error('获取用户信息失败')
    }

    const data = await response.json()
    if (data.code === 0) {
      // 更新本地存储和当前页面状态
      localStorage.setItem('userInfo', JSON.stringify(data.data))
      userInfo.value = data.data

      if (data.data.profile?.avatar && data.data.profile.avatar.trim() !== '') {
        let avatarUrl = data.data.profile.avatar
        if (avatarUrl.startsWith('/uploads/')) {
          const backendUrl = config.baseURL || 'http://localhost:5000'
          userAvatar.value = `${backendUrl}${avatarUrl}`
        } else {
          userAvatar.value = avatarUrl
        }
      } else {
        userAvatar.value = generateAvatarUrl(data.data.name, data.data.profile?.gender)
      }
      avatarKey.value++ // 强制刷新头像
    } else {
      throw new Error(data.message || '获取用户信息失败')
    }
  } catch (error) {
    console.error(error.message)
  }
}

// 处理头像加载失败
const handleAvatarError = (event) => {
  console.error('头像加载失败:', event.target.src)

  // 防止无限循环 - 如果已经尝试过修复，就不再尝试
  if (event.target.getAttribute('data-tried') === 'true') {
    console.log('已经尝试过修复，停止循环')
    return
  }

  // 标记已经尝试过修复
  event.target.setAttribute('data-tried', 'true')

  console.log('UserView - 头像加载失败，尝试使用默认头像')

  // 获取用户信息并强制使用默认头像
  const userInfoStr = localStorage.getItem('userInfo')
  if (userInfoStr) {
    try {
      const user = JSON.parse(userInfoStr)
      console.log('UserView - 用户性别信息:', user.profile?.gender)

      if (user.profile?.gender === 'male') {
        console.log('UserView - 强制设置男性头像:', boyAvatar)
        event.target.src = boyAvatar
        userAvatar.value = boyAvatar
      } else if (user.profile?.gender === 'female') {
        console.log('UserView - 强制设置女性头像:', girlAvatar)
        event.target.src = girlAvatar
        userAvatar.value = girlAvatar
      } else {
        // 使用字母头像作为备选
        const firstChar = (user.name || '用').charAt(0).toUpperCase()
        const letterAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(firstChar)}&size=160&background=42b983&color=ffffff&rounded=true`
        console.log('UserView - 使用字母头像:', letterAvatar)
        event.target.src = letterAvatar
        userAvatar.value = letterAvatar
      }
    } catch (e) {
      console.error('解析用户信息失败:', e)
      // 解析失败时使用默认头像
      console.log('UserView - 解析失败，使用默认男性头像')
      event.target.src = boyAvatar
      userAvatar.value = boyAvatar
    }
  } else {
    // 没有用户信息时的备选
    console.log('UserView - 没有用户信息，使用默认男性头像')
    event.target.src = boyAvatar
    userAvatar.value = boyAvatar
  }
}

// 触发头像上传
const triggerAvatarUpload = () => {
  if (avatarInput.value) {
    avatarInput.value.click()
  }
}

// 处理头像上传// 调试方法：显示调试信息
const showDebugInfo = () => {
  const userInfoStr = localStorage.getItem('userInfo')
  const debugInfo = {
    userAvatar: userAvatar.value,
    boyAvatar: boyAvatar,
    girlAvatar: girlAvatar,
    username: username.value,
    userInfo: userInfoStr ? JSON.parse(userInfoStr) : null,
    avatarKey: avatarKey.value
  }
  console.log('UserView - 调试信息:', debugInfo)
  ElMessage({
    message: `调试信息已输出到控制台。当前头像: ${userAvatar.value.substring(0, 50)}...`,
    type: 'info',
    duration: 3000
  })
}

// 处理头像上传
const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过5MB')
    return
  }

  try {
    isUploading.value = true
    const formData = new FormData()
    formData.append('avatar', file)
    const token = localStorage.getItem('token')

    const response = await fetch(`${config.baseURL}/api/avatar/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    })

    const result = await response.json()

    if (result.code === 0) {
      const returnedAvatarUrl = result.data.avatarUrl
      const backendUrl = config.baseURL || 'http://localhost:5000'
      const fullAvatarUrl = `${backendUrl}${returnedAvatarUrl}`
      const cacheBustedUrl = fullAvatarUrl.split('?')[0] + '?t=' + new Date().getTime()

      userAvatar.value = cacheBustedUrl
      avatarKey.value++

      let localUserInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      if (!localUserInfo.profile) {
        localUserInfo.profile = {}
      }
      localUserInfo.profile.avatar = returnedAvatarUrl
      localStorage.setItem('userInfo', JSON.stringify(localUserInfo))

      // 通知 NavBarUser 组件刷新头像
      document.dispatchEvent(new CustomEvent('refreshAvatar'))

      ElMessage.success('头像上传成功')
    } else {
      throw new Error(result.message || '头像上传失败')
    }
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    isUploading.value = false
    if (avatarInput.value) {
      avatarInput.value.value = ''
    }
  }
}

onMounted(() => {
  // 验证静态资源是否正确加载
  console.log('UserView - 验证静态资源:')
  console.log('UserView - boyAvatar:', boyAvatar)
  console.log('UserView - girlAvatar:', girlAvatar)
  console.log('UserView - boyAvatar type:', typeof boyAvatar)
  console.log('UserView - girlAvatar type:', typeof girlAvatar)

  fetchUserInfo()
  document.addEventListener('refreshAvatar', fetchUserInfo)
})

onUnmounted(() => {
  document.removeEventListener('refreshAvatar', fetchUserInfo)
})
</script>

<style scoped>
.user-container {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.user-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 100px 4rem 4rem;
}

.profile-section {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 3rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 3rem;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.avatar-upload-container {
  position: relative;
  cursor: pointer;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #42b983;
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.15);
  transition: transform 0.2s;
}

.avatar-upload-container:hover {
  transform: scale(1.05);
}

.avatar-upload-container:hover .avatar-overlay {
  opacity: 1;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: filter 0.3s;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  color: #666;
  font-size: 14px;
}

.avatar-upload-container:hover .avatar {
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
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
  border-radius: 50%;
  text-align: center;
}

.upload-icon {
  margin-bottom: 8px;
}

.avatar-overlay span {
  font-weight: 500;
  font-size: 0.9rem;
}

.username {
  font-size: 2.5rem;
  color: #1a1a1a;
  margin: 0;
  font-weight: 600;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 1rem;
}

.info-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 2rem;
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-title {
  color: #1a1a1a;
  font-size: 1.5rem;
  margin: 0 0 2rem;
  font-weight: 600;
  border-bottom: 2px solid #42b983;
  padding-bottom: 0.75rem;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #4b5563;
  font-size: 1rem;
  font-weight: 500;
}

.value {
  color: #1a1a1a;
  font-size: 1rem;
  font-weight: 600;
}

@media (max-width: 1200px) {
  .user-content {
    padding-left: 2rem;
    padding-right: 2rem;
  }

  .profile-section {
    padding: 2rem;
  }
}

@media (max-width: 768px) {
  .info-cards {
    grid-template-columns: 1fr;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }

  .username {
    font-size: 2rem;
  }

  .avatar-upload-container {
    width: 140px;
    height: 140px;
  }

  .avatar {
    display: block !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
  }
}

@media (max-width: 480px) {
  .user-content {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .profile-section {
    padding: 1.5rem;
  }

  .username {
    font-size: 1.75rem;
  }

  .card-title {
    font-size: 1.25rem;
  }
}
</style>
