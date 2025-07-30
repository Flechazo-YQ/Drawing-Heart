<template>
  <div class="draw-container">
    <nav class="modern-nav">
      <div class="nav-content">
<<<<<<< HEAD
        <router-link to="/" class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </router-link>
        <div class="nav-actions">
          <router-link to="/chat" class="nav-link">前往对话</router-link>
          <router-link to="/user" class="nav-link">个人中心</router-link>
=======
        <div class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </div>
        <div class="nav-actions">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/draw" class="nav-link active">绘画空间</router-link>
          <router-link to="/chat" class="nav-link">心理对话</router-link>
          <router-link to="/user" class="nav-link">个人空间</router-link>
          <button class="nav-button logout-btn" @click="handleLogout">退出登录</button>
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
        </div>
      </div>
    </nav>

    <main class="draw-content">
      <div class="drawing-area">
        <div class="canvas-container">
          <input type="file" ref="fileInput" accept="image/*" @change="handleFileUpload" style="display: none" />
          <canvas id="drawingCanvas" ref="canvasRef" @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing"
            @mouseleave="stopDrawing"></canvas>
          <div class="drawing-tools" v-if="!isImageUploaded">
            <div class="tool-group">
              <button class="tool-btn" :class="{ active: currentTool === 'pen' }" @click="switchTool('pen')">
                <span class="tool-icon">🖌️</span>
                画笔
              </button>
              <button class="tool-btn" :class="{ active: currentTool === 'eraser' }" @click="switchTool('eraser')">
                <span class="tool-icon">🗑️</span>
                橡皮
              </button>
              <button class="tool-btn">
                <input type="color" :value="currentColor" @input="(e) => changeColor(e.target.value)"
                  class="color-picker" />
                <span class="tool-icon">🎨</span>
                调色
              </button>
            </div>
            <div class="size-group">
              <input type="range" min="1" max="50" class="size-slider" :value="lineWidth"
                @input="(e) => changeLineWidth(Number(e.target.value))" />
            </div>
          </div>
        </div>
        <div class="action-buttons">
          <button class="action-btn upload" @click="triggerFileUpload" v-if="!hasDrawing">
            上传照片
          </button>
          <button class="action-btn clear" @click="clearCanvas">
            {{ isImageUploaded ? '返回手绘' : '清空画布' }}
          </button>
          <button class="action-btn save" @click="saveDrawing" v-if="!isImageUploaded && !currentFileName">
            保存图片
          </button>
          <button class="action-btn submit" @click="analyzeDrawing" v-if="(isImageUploaded || currentFileName)"
            :disabled="isLoading">
            {{ isLoading ? '分析中...' : '前往分析' }}
          </button>
        </div>
      </div>

      <div class="analysis-panel">
        <h2 class="panel-title">绘画分析</h2>
        <div class="analysis-content" :class="{ loading: isLoading }">
          <div v-if="isLoading" class="loading-indicator">
            <div class="spinner"></div>
            <p>AI正在分析您的绘画...</p>
          </div>
          <div v-else-if="sections.length > 0" class="analysis-text">
            <h3>{{ sections[currentPage - 1].title }}</h3>
            <p>{{ sections[currentPage - 1].content }}</p>
            <div class="pagination">
              <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
              <button @click="nextPage" :disabled="currentPage === sections.length">下一页</button>
            </div>
          </div>
          <div v-else-if="analysisResult" class="analysis-text">
            {{ analysisResult }}
          </div>
          <div v-else class="empty-state">
            <p>完成绘画后点击"提交分析"，AI将为您分析绘画中蕴含的情感。</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config'

const router = useRouter()
const canvasRef = ref(null)
const isLoading = ref(false)
const currentFileName = ref('')
const analysisResult = ref('')
const currentPage = ref(1)
const sections = ref([])

<<<<<<< HEAD
=======
// 退出登录处理
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('isLoggedIn')
  router.push('/login')
}

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
// 绘画相关的状态
const isDrawing = ref(false)
const currentTool = ref('pen') // pen, eraser
const currentColor = ref('#000000')
const lineWidth = ref(5)
let ctx = null
let lastX = 0
let lastY = 0

// 图片处理相关的状态
const isImageUploaded = ref(false)
const hasDrawing = ref(false)
const fileInput = ref(null)

// 初始化画布
const initCanvas = () => {
  const canvas = canvasRef.value
  ctx = canvas.getContext('2d')

  // 设置画布大小为容器大小
  const container = canvas.parentElement
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
<<<<<<< HEAD
  
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  // 保存当前画布内容（如果有的话）
  let imageData = null
  if (canvas.width > 0 && canvas.height > 0) {
    imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  }
<<<<<<< HEAD
  
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  canvas.width = containerWidth
  canvas.height = containerHeight

  // 设置默认样式
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.strokeStyle = currentColor.value
  ctx.lineWidth = lineWidth.value

  // 填充白色背景
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
<<<<<<< HEAD
  
=======

  // 初始化时不设置hasDrawing为true，让用户选择绘画或上传

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  // 如果有保存的画布内容，恢复它
  if (imageData && !isImageUploaded.value) {
    const tempCanvas = document.createElement('canvas')
    const tempCtx = tempCanvas.getContext('2d')
    tempCanvas.width = imageData.width
    tempCanvas.height = imageData.height
    tempCtx.putImageData(imageData, 0, 0)
<<<<<<< HEAD
    
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
    // 计算缩放比例保持宽高比
    const scale = Math.min(canvas.width / tempCanvas.width, canvas.height / tempCanvas.height)
    const newWidth = tempCanvas.width * scale
    const newHeight = tempCanvas.height * scale
    const x = (canvas.width - newWidth) / 2
    const y = (canvas.height - newHeight) / 2
<<<<<<< HEAD
    
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
    ctx.drawImage(tempCanvas, x, y, newWidth, newHeight)
  }
}

// 开始绘画
const startDrawing = (e) => {
  if (!isImageUploaded.value) {
    isDrawing.value = true
    const rect = canvasRef.value.getBoundingClientRect()
    lastX = e.clientX - rect.left
    lastY = e.clientY - rect.top
  }
}

// 绘画过程
const draw = (e) => {
  if (!isDrawing.value) return

  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  ctx.beginPath()
  ctx.moveTo(lastX, lastY)
  ctx.lineTo(x, y)
  ctx.stroke()

  lastX = x
  lastY = y
<<<<<<< HEAD
=======

  // 用户开始绘画时标记有内容
  if (!hasDrawing.value) {
    hasDrawing.value = true
  }
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
}

// 结束绘画
const stopDrawing = () => {
  isDrawing.value = false
}

// 切换工具
const switchTool = (tool) => {
  currentTool.value = tool
  if (tool === 'pen') {
    ctx.globalCompositeOperation = 'source-over'
    ctx.strokeStyle = currentColor.value
  } else if (tool === 'eraser') {
    ctx.globalCompositeOperation = 'destination-out'
    ctx.strokeStyle = 'rgba(0,0,0,1)'
  }
}

// 更改颜色
const changeColor = (color) => {
  currentColor.value = color
  if (currentTool.value === 'pen') {
    ctx.strokeStyle = color
  }
}

// 更改画笔大小
const changeLineWidth = (width) => {
  lineWidth.value = width
  ctx.lineWidth = width
}

// 清空画布
const clearCanvas = () => {
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)

  // 重置状态
  isImageUploaded.value = false
  hasDrawing.value = false
<<<<<<< HEAD
  if (!currentFileName.value) {
    currentFileName.value = ''
  }
=======
  currentFileName.value = ''
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
}

// 触发文件上传
const triggerFileUpload = () => {
  fileInput.value.click()
}

// 处理文件上传
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = async (e) => {
      const img = new Image()
      img.onload = async () => {
        // 清空画布
        clearCanvas()

        // 将图片绘制到画布上，保持其比例并适应画布大小
        const canvas = canvasRef.value
        const ctx = canvas.getContext('2d')

        // 计算缩放比例
        const scale = Math.min(
          canvas.width / img.width,
          canvas.height / img.height
        )

        // 计算居中位置
        const x = (canvas.width - img.width * scale) / 2
        const y = (canvas.height - img.height * scale) / 2

        // 绘制图片
        ctx.drawImage(
          img,
          x,
          y,
          img.width * scale,
          img.height * scale
        )

        // 保存上传的图片
        await saveDrawing(true)
        isImageUploaded.value = true
        hasDrawing.value = true
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// 监听画布大小变化
const handleResize = () => {
  if (canvasRef.value && canvasRef.value.width > 0) {
    // 延迟执行以确保容器大小已更新
    setTimeout(() => {
      const container = canvasRef.value.parentElement
      const newWidth = container.clientWidth
      const newHeight = container.clientHeight
<<<<<<< HEAD
      
      // 只有当尺寸真正改变时才重新初始化（容差为5px）
      if (Math.abs(canvasRef.value.width - newWidth) > 5 || 
=======

      // 只有当尺寸真正改变时才重新初始化（容差为5px）
      if (Math.abs(canvasRef.value.width - newWidth) > 5 ||
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
          Math.abs(canvasRef.value.height - newHeight) > 5) {
        console.log(`Canvas resizing from ${canvasRef.value.width}x${canvasRef.value.height} to ${newWidth}x${newHeight}`)
        initCanvas()
      }
    }, 150) // 增加延迟确保布局稳定
  }
}

// 组件挂载时初始化
onMounted(() => {
  initCanvas()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const saveDrawing = async (isUploaded = false) => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    isLoading.value = true
<<<<<<< HEAD
    let imageData = canvasRef.value.toDataURL('image/png')
=======

    // 检查画布是否为空
    if (!canvasRef.value) {
      ElMessage.error('画布未初始化')
      return
    }

    let imageData = canvasRef.value.toDataURL('image/png')
    console.log('Image data length:', imageData.length)
    console.log('Image data preview:', imageData.substring(0, 100))
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845

    // 确保图片数据格式正确
    if (!imageData.startsWith('data:image/')) {
      imageData = 'data:image/png;base64,' + imageData
    }

<<<<<<< HEAD
    const response = await fetch(`${config.baseURL}/save`, {
=======
    console.log('Sending request to:', `${config.baseURL}/api/save`)
    console.log('Request payload size:', JSON.stringify({
      image: imageData.substring(0, 100) + '...',
      isUploaded: isUploaded
    }))

    const response = await fetch(`${config.baseURL}/api/save`, {
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token
      },
      body: JSON.stringify({
        image: imageData,
        isUploaded: isUploaded
      })
    })

<<<<<<< HEAD
    const data = await response.json()
=======
    console.log('Response status:', response.status)
    console.log('Response ok:', response.ok)

    const data = await response.json()
    console.log('Response data:', data)

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
    if (response.ok) {
      currentFileName.value = data.file_name
      if (!isUploaded) {
        hasDrawing.value = true
      }
      ElMessage.success('保存成功!')
    } else {
<<<<<<< HEAD
=======
      console.error('Save failed with status:', response.status, data)
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
      ElMessage.error(data.message || '保存失败')
    }
  } catch (error) {
    console.error('Save error:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const parseAnalysisResult = (text) => {
  if (!text) return []
  // 将文本按章节分割
  const sectionTexts = text.split(/###\s+/).filter(Boolean)
  return sectionTexts.map(section => {
    const [title, ...content] = section.trim().split('\n')
    return {
      title: title.trim(),
      content: content.join('\n').trim()
    }
  })
}

const analyzeDrawing = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    isLoading.value = true
    const imageData = canvasRef.value.toDataURL('image/png')

<<<<<<< HEAD
    const response = await fetch(`${config.baseURL}/save`, {
=======
    console.log('Sending analysis request to:', `${config.baseURL}/api/save`)
    console.log('Analysis payload:', {
      imageDataLength: imageData.length,
      analyze: true,
      isUploaded: isImageUploaded.value
    })

    const response = await fetch(`${config.baseURL}/api/save`, {
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token
      },
      body: JSON.stringify({
        image: imageData,
        analyze: true,
        isUploaded: isImageUploaded.value
      })
    })

    const data = await response.json()
    console.log('Analysis response:', { status: response.status, data })
<<<<<<< HEAD
    
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
    if (response.ok) {
      if (data.analysis) {
        analysisResult.value = data.analysis
        sections.value = parseAnalysisResult(data.analysis)
        currentPage.value = 1
        ElMessage.success('分析完成!')
      } else if (data.message) {
        // 检查是否是成功消息
        if (data.message === '分析完成' || data.message.includes('成功')) {
          analysisResult.value = data.message
          ElMessage.success(data.message)
        } else {
          // 错误消息
          analysisResult.value = data.message
          ElMessage.error(data.message)
        }
      } else {
        // 没有分析结果也没有消息
        ElMessage.error('分析结果为空，请重试')
      }
      if (data.file_name) {
        currentFileName.value = data.file_name
      }
    } else {
      console.error('Analysis failed:', data)
      const errorMessage = data.message || data.error || `分析失败 (HTTP ${response.status})`
      ElMessage.error(errorMessage)
      analysisResult.value = errorMessage
    }
  } catch (error) {
    console.error('Analysis error:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const nextPage = () => {
  if (currentPage.value < sections.value.length) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}
</script>

<style scoped>
/* 确保页面充分利用视口高度 */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

.draw-container {
  min-height: 100vh;
  height: 100vh;
  background-color: var(--color-background);
  display: flex;
  flex-direction: column;
}

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
<<<<<<< HEAD
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
=======
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: default; /* 默认光标，不显示可点击状态 */
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
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
<<<<<<< HEAD
  transition: color 0.2s;
=======
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.2s;
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
}

.nav-link:hover {
  color: #42b983;
<<<<<<< HEAD
=======
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
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
}

.draw-content {
  flex: 1;
  max-width: 1920px;
  margin: 0 auto;
  padding: 84px 2rem 2rem;
  display: grid;
  grid-template-columns: 3fr 2fr; /* 调整比例：绘图区域3份，分析面板2份 */
  gap: 2rem;
  align-items: center; /* 垂直居中对齐 */
  justify-content: center; /* 水平居中对齐 */
  min-height: calc(100vh - 64px); /* 减去导航栏高度 */
}

.drawing-area {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  max-width: 800px; /* 限制绘图区域的最大宽度 */
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中 */
  position: relative; /* 确保正确的定位上下文 */
  overflow: visible; /* 确保按钮不会被裁剪 */
}

.canvas-container {
  position: relative;
  width: 100%;
  max-width: 700px; /* 默认最大宽度 */
  aspect-ratio: 4/3;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto; /* 居中显示 */
}

#drawingCanvas {
  position: absolute;
  width: 100%;
  height: 100%;
  cursor: crosshair;
}

.upload-preview {
  position: absolute;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  z-index: 1;
}

.drawing-tools {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 0.75rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 5; /* 确保工具栏在画布上方，但在按钮下方 */
}

.tool-group {
  display: flex;
  gap: 0.5rem;
}

.tool-btn {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #f3f4f6;
  color: #4a4a4a;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: #e5e7eb;
}

.tool-btn.active {
  background: #e5e7eb;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tool-icon {
  font-size: 1.25rem;
}

.color-picker {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  cursor: pointer;
}

.size-group {
  display: flex;
  align-items: center;
  padding: 0 0.5rem;
}

.size-slider {
  width: 120px;
  cursor: pointer;
}

.action-buttons {
  display: flex;
  justify-content: center; /* 改为居中对齐 */
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap; /* 允许按钮在必要时换行 */
  width: 100%; /* 确保占满容器宽度 */
  position: relative; /* 确保正确的层级 */
  z-index: 10; /* 确保按钮在最上层 */
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap; /* 防止文字换行 */
  flex-shrink: 0; /* 防止按钮被压缩 */
  position: relative; /* 确保正确的定位 */
}

.action-btn.clear {
  background: #f3f4f6;
  color: #4a4a4a;
}

.action-btn.clear:hover {
  background: #e5e7eb;
}

.action-btn.save {
  background: #42b983;
  color: white;
}

.action-btn.save:hover {
  background: #3aa876;
}

.action-btn.submit {
  background: #3b82f6;
  color: white;
}

.action-btn.submit:hover {
  background: #2563eb;
}

.action-btn.upload {
  background: #8b5cf6;
  color: white;
}

.action-btn.upload:hover {
  background: #7c3aed;
}

.analysis-panel {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 2.5rem; /* 增加内边距 */
  height: fit-content; /* 改为适应内容高度 */
  max-height: calc(100vh - 120px); /* 限制最大高度，留出空间 */
  overflow-y: auto; /* 允许垂直滚动 */
  align-self: center; /* 与画板居中对齐 */
}

.panel-title {
  margin: 0 0 1.5rem;
  font-size: 1.5rem;
  color: #1a1a1a;
  font-weight: 600;
}

.analysis-content {
  min-height: 300px;
  position: relative;
  line-height: 1.6; /* 改善行间距 */
}

.analysis-content.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.loading-indicator {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.empty-state {
  text-align: center;
  color: #666;
  padding: 2rem;
}

.analysis-text {
  white-space: pre-line;
  line-height: 1.7; /* 增加行间距 */
  color: #333;
  padding: 1.5rem; /* 增加内边距 */
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.95rem; /* 稍微调整字体大小 */
}

.analysis-text h3 {
  color: #1a1a1a;
  margin: 1.5rem 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.pagination {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
}

.pagination button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #f3f4f6;
  color: #4a4a4a;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination button:hover {
  background: #e5e7eb;
}

.pagination button:disabled {
  background: #e5e7eb;
  cursor: not-allowed;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 超大屏幕优化（4K等） */
@media (min-width: 1920px) {
  .draw-content {
    grid-template-columns: 800px 600px; /* 更大的固定尺寸 */
    gap: 4rem; /* 更大的间距 */
    justify-content: center;
    align-items: center;
  }
<<<<<<< HEAD
  
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .drawing-area {
    max-width: 800px;
    padding: 3rem;
  }
<<<<<<< HEAD
  
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .analysis-panel {
    padding: 3rem;
    font-size: 1.1rem; /* 稍大的字体 */
  }
}

/* 大屏幕优化 */
@media (min-width: 1400px) {
  .draw-content {
    grid-template-columns: 700px 500px; /* 绘图区域700px，分析面板500px */
    justify-content: center;
    align-items: center; /* 确保垂直居中 */
    gap: 3rem; /* 增加间距 */
  }
}

@media (min-width: 1200px) and (max-width: 1399px) {
  .drawing-area {
    max-width: 700px; /* 中大屏幕的限制 */
  }
}

/* 针对1200px以下分辨率的处理，解决按钮消失问题 */
@media (max-width: 1200px) {
  .draw-content {
    grid-template-columns: 1fr;
    align-items: center;
    justify-items: center;
    padding: 84px 1.5rem 2rem;
    gap: 2rem;
  }

  .drawing-area {
    max-width: 700px;
    width: 100%;
  }
<<<<<<< HEAD
  
  .canvas-container {
    max-width: 700px;
  }
  
=======

  .canvas-container {
    max-width: 700px;
  }

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 0.8rem;
    margin-top: 1.5rem;
    flex-wrap: wrap; /* 允许按钮换行 */
    width: 100%;
    padding: 0 1rem; /* 添加左右内边距 */
  }
<<<<<<< HEAD
  
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .action-btn {
    padding: 0.7rem 1rem;
    font-size: 0.85rem;
    min-width: 90px; /* 确保按钮有最小宽度 */
    white-space: nowrap; /* 防止文字换行 */
    flex: 0 0 auto; /* 防止按钮被压缩 */
  }

  .analysis-panel {
    margin-top: 2rem;
    width: 100%;
    max-width: 700px;
    align-self: center;
  }
}

/* 针对1120px以下分辨率的特殊处理 */
@media (max-width: 1120px) {
  .draw-content {
    padding: 84px 1rem 2rem; /* 减少侧边距 */
    gap: 1.5rem;
  }

  .drawing-area {
    max-width: 600px;
    width: 100%;
    padding: 1.5rem; /* 减少内边距 */
  }
<<<<<<< HEAD
  
  .canvas-container {
    max-width: 600px;
  }
  
=======

  .canvas-container {
    max-width: 600px;
  }

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .action-buttons {
    gap: 0.6rem;
    margin-top: 1rem;
    flex-direction: row; /* 确保是水平排列 */
    flex-wrap: wrap; /* 允许换行 */
    justify-content: center;
    align-items: center;
    padding: 0.5rem; /* 添加内边距 */
  }
<<<<<<< HEAD
  
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .action-btn {
    padding: 0.6rem 0.8rem;
    font-size: 0.8rem;
    min-width: 80px;
    max-width: 120px; /* 限制最大宽度防止过宽 */
    text-align: center;
  }

  .analysis-panel {
    max-width: 600px;
    padding: 1.5rem; /* 减少内边距 */
  }
}

@media (max-width: 768px) {
  .draw-content {
    padding: 84px 1rem 1rem; /* 减少侧边距 */
    gap: 1.5rem;
    align-items: center; /* 保持居中对齐 */
  }
<<<<<<< HEAD
  
  .canvas-container {
    max-width: 600px; /* 在小屏幕上进一步限制宽度 */
  }
  
=======

  .canvas-container {
    max-width: 600px; /* 在小屏幕上进一步限制宽度 */
  }

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .drawing-area {
    max-width: 100%;
    padding: 1.5rem;
  }
<<<<<<< HEAD
  
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .analysis-panel {
    padding: 1.5rem;
    align-self: center; /* 确保与画板对齐 */
  }
}

@media (max-width: 640px) {
  .draw-content {
    padding: 84px 0.5rem 1rem; /* 进一步减少侧边距 */
    min-height: calc(100vh - 64px);
    align-items: center; /* 保持居中对齐 */
  }
<<<<<<< HEAD
  
=======

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .drawing-tools {
    flex-direction: column;
    align-items: center;
    bottom: 0.5rem; /* 调整工具栏位置 */
  }

  .action-buttons {
    flex-direction: column;
    align-items: center; /* 确保垂直布局时也居中 */
    gap: 0.75rem;
  }

  .action-btn {
    width: 100%;
    max-width: 300px; /* 限制最大宽度，保持美观 */
  }
<<<<<<< HEAD
  
  .canvas-container {
    max-width: 100%; /* 在最小屏幕上使用全宽 */
  }
  
  .drawing-area {
    padding: 1rem;
  }
  
=======

  .canvas-container {
    max-width: 100%; /* 在最小屏幕上使用全宽 */
  }

  .drawing-area {
    padding: 1rem;
  }

>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
  .analysis-panel {
    padding: 1rem;
    align-self: center; /* 确保与画板对齐 */
  }
}
<<<<<<< HEAD
</style>
=======
</style>
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
