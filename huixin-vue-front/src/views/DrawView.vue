<template>
  <div class="draw-container">
    <nav class="modern-nav">
      <div class="nav-content">
        <router-link to="/" class="nav-logo">
          <img src="@/assets/images/logo.png" alt="绘心同学" class="logo-img" />
          <span>绘心同学</span>
        </router-link>
        <div class="nav-actions">
          <router-link to="/chat" class="nav-link">前往对话</router-link>
          <router-link to="/user" class="nav-link">个人中心</router-link>
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
          <button class="action-btn iterate" v-if="!isImageUploaded && currentFileName" @click="checkIteration">
            继续迭代
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
  canvas.width = container.clientWidth
  canvas.height = container.clientHeight

  // 设置默认样式
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.strokeStyle = currentColor.value
  ctx.lineWidth = lineWidth.value

  // 填充白色背景
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
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
  if (!currentFileName.value) {
    currentFileName.value = ''
  }
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
  if (canvasRef.value) {
    const imageData = ctx.getImageData(0, 0, canvasRef.value.width, canvasRef.value.height)
    initCanvas()
    ctx.putImageData(imageData, 0, 0)
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

const checkIteration = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const response = await fetch(`${config.baseURL}/api/check-iteration`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token
      },
      body: JSON.stringify({
        fileName: currentFileName.value
      })
    })

    const data = await response.json()
    if (data.canIterate) {
      await saveDrawing(true)
    } else {
      ElMessage.warning(data.message)
    }
  } catch (error) {
    ElMessage.error('检查迭代状态时出错')
  }
}

const saveDrawing = async (isUploaded = false) => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    isLoading.value = true
    let imageData = canvasRef.value.toDataURL('image/png')

    // 确保图片数据格式正确
    if (!imageData.startsWith('data:image/')) {
      imageData = 'data:image/png;base64,' + imageData
    }

    const response = await fetch(`${config.baseURL}/save`, {
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

    const data = await response.json()
    if (response.ok) {
      currentFileName.value = data.file_name
      if (!isUploaded) {
        hasDrawing.value = true
      }
      ElMessage.success('保存成功!')
    } else {
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

    const response = await fetch(`${config.baseURL}/save`, {
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
    if (response.ok) {
      if (data.analysis) {
        analysisResult.value = data.analysis
        sections.value = parseAnalysisResult(data.analysis)
        currentPage.value = 1
      } else if (data.message) {
        analysisResult.value = data.message
      }
      currentFileName.value = data.file_name
      ElMessage.success('分析完成!')
    } else {
      ElMessage.error(data.message || '分析失败')
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
.draw-container {
  min-height: 100vh;
  background-color: var(--color-background);
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
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  transition: color 0.2s;
}

.nav-link:hover {
  color: #42b983;
}

.draw-content {
  max-width: 1920px;
  margin: 0 auto;
  padding: 84px 2rem 2rem;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.drawing-area {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

.canvas-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
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
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
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

.action-btn.iterate {
  background: #9333ea;
  color: white;
}

.action-btn.iterate:hover {
  background: #7e22ce;
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
  padding: 2rem;
  height: 100%;
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
  line-height: 1.6;
  color: #333;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 1rem;
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

@media (max-width: 1200px) {
  .draw-content {
    grid-template-columns: 1fr;
  }

  .analysis-panel {
    margin-top: 2rem;
  }
}

@media (max-width: 640px) {
  .drawing-tools {
    flex-direction: column;
    align-items: center;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}
</style>