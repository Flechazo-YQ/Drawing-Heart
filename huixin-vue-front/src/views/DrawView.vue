<template>
  <div class="draw-container">
    <NavBarUser v-if="!isFullscreen" />

    <main class="draw-content">
      <div class="drawing-area">
        <!-- 灵动岛工具栏（画布内上方） -->
        <div class="dynamic-island-toolbar">
          <div v-if="currentMode === 'draw'" class="toolbar-tools">
            <button class="toolbar-btn" @click="undoCanvas" :disabled="!canUndo" title="撤回">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M9 17L4 12L9 7" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M20 12H4" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="redoCanvas" :disabled="!canRedo" title="取消撤回">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M15 7L20 12L15 17" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M4 12H20" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="triggerFileUpload" title="上传图片">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 9l5-5 5 5" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 4v12" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="saveDrawing" title="保存图片">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M19 21H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M17 3v4" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 3v4" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 13l3 3 4-4" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <div class="pen-tool-container" @mouseleave="handleSliderMouseLeave">
              <button class="toolbar-btn" :class="{ active: currentTool === 'pen' }" @click="switchTool('pen')"
                @mouseenter="handlePenMouseEnter" title="画笔">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M3 21v-3.75l12.15-12.16a2.12 2.12 0 0 1 3 3L6 20.25H3Zm15.085-13.085a.62.62 0 0 0-.88 0l-1.2 1.2 1.88 1.88 1.2-1.2a.62.62 0 0 0 0-.88l-1-1Z"
                    stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>

              <!-- 画笔粗细调节栏 -->
              <div class="pen-size-slider" v-if="showSizeSlider && currentTool === 'pen'"
                @mouseenter="handleSliderMouseEnter" @mouseleave="handleSliderMouseLeave">
                <svg t="1755766522553" class="icon" viewBox="0 0 1024 1024" version="1.1"
                  xmlns="http://www.w3.org/2000/svg" p-id="20214" width="16" height="16">
                  <path
                    d="M643.4 993.8c-26.8 0-51.2-18.1-58.1-45.2-8.2-32.1 11.3-64.8 43.4-72.9 0.7-0.2 76.9-20.1 146.6-62.2 37.6-22.7 65.6-47.2 83.4-72.8 19.2-27.5 25.9-56 20.6-87-7.1-41.7-21.1-51.2-25.7-54.3-15.3-10.4-44.6-13.8-87.1-10.2-50.3 4.3-115.3 17.9-190.5 33.7-80.8 16.9-172.4 36.1-278.1 51.1-55.1 7.8-101 5.8-140.3-6.1-41-12.4-73.2-35.4-95.8-68.3-28.1-41-39.3-95.8-33.3-162.8 4.2-47.1 17-101.4 38.1-161.4 34.7-99 80.1-180.4 82-183.8 16.2-28.9 52.8-39.2 81.7-23 28.9 16.2 39.2 52.7 23 81.6-0.4 0.8-42.8 77-74 166.4-50.5 144.9-29.8 198.8-18.5 215.2 4.3 6.3 12.3 15.4 31.6 21.2 21.9 6.6 51.7 7.3 88.6 2.1 101.7-14.4 191.3-33.2 270.3-49.7s147.3-30.8 204.8-35.8c33.1-2.8 61.2-2.4 85.9 1.2 30.9 4.6 56.7 14.2 78.9 29.3 21 14.3 38.3 33.5 51.2 56.9 11.9 21.6 20.2 46.6 25.3 76.4 5.6 33 4.5 65.5-3.5 96.8-7.2 28-19.9 55-37.7 80.4C928.4 850 887.6 886 835 917.5c-84.7 50.7-173 73.5-176.8 74.4-5 1.3-9.9 1.9-14.8 1.9z"
                    p-id="20215"></path>
                </svg>
                <input type="range" min="1" max="15" v-model="lineWidth" @input="changeLineWidth(lineWidth)"
                  @mousedown="startSizePreview" @mousemove="updateSizePreview" @mouseup="endSizePreview"
                  @mouseleave="endSizePreview" @touchstart="startSizePreview" @touchmove="updateSizePreview"
                  @touchend="endSizePreview">
              </div>
            </div>
            <div class="eraser-tool-container">
              <button class="toolbar-btn" :class="{ active: currentTool === 'eraser' }" @click="switchTool('eraser')"
                @mouseenter="handleEraserMouseEnter" title="橡皮擦">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M7.5 17.5 3 13a2.12 2.12 0 0 1 0-3l7-7a2.12 2.12 0 0 1 3 0l7 7a2.12 2.12 0 0 1 0 3l-4.5 4.5M7.5 17.5h9M7.5 17.5l4-4"
                    stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>

              <!-- 橡皮擦粗细调节栏 -->
              <div class="eraser-size-slider" v-if="showEraserSlider && currentTool === 'eraser'"
                @mouseenter="handleEraserSliderMouseEnter" @mouseleave="handleEraserSliderMouseLeave">
                <input type="range" min="15" max="30" step="1" v-model="eraserWidth"
                  @input="changeEraserWidth(eraserWidth)">
                <div class="eraser-preview" :style="{
                  width: `${eraserWidth * 1.6}px`,
                  height: `${eraserWidth * 0.9}px`,
                  borderRadius: `${eraserWidth * 0.2}px`
                }"></div>
              </div>
            </div>
            <button class="toolbar-btn" :class="{ active: showPalette }" @click="showPalette = !showPalette" title="调色盘">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="#333" stroke-width="1.5" />
                <circle cx="8.5" cy="10" r="1.5" fill="#f59e42" />
                <circle cx="15.5" cy="10" r="1.5" fill="#3b82f6" />
                <circle cx="10" cy="15" r="1.5" fill="#10b981" />
                <circle cx="14" cy="15" r="1.5" fill="#ef4444" />
              </svg>
            </button>
            <!-- 调色盘面板将移至右侧，与SVG素材库类似 -->
          </div>
          <div v-else class="toolbar-tools">
            <!-- 拼贴模式下的房树人按钮 -->
            <button class="toolbar-btn" @click="showSvgCategory(svgCategories[0])" title="添加房">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M3 21h18v-3H3v3zm3-6h12v-3H6v3zm-3-7l9-4 9 4v2H3V8z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="showSvgCategory(svgCategories[1])" title="添加树">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 3L8 10H16L12 3z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 10L6 16H18L14 10" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 21V16" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="showSvgCategory(svgCategories[2])" title="添加人">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="7" r="4" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M6 21v-2a4 4 0 014-4h4a4 4 0 014 4v2" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="canvas-container" style="display: flex; justify-content: center; align-items: center;">
          <input type="file" ref="fileInput" accept="image/*" @change="handleFileUpload" style="display: none" />
          <canvas :id="currentTool === 'pen' ? 'drawingCanvas' : 'erasingCanvas'" ref="canvasRef" @mousedown="startDrawing" @mouseup="stopDrawing"
            @mouseenter="handleCanvasMouseEnter" @mousemove="handleCanvasAreaMove" @mouseleave="handleCanvasMouseLeave"></canvas>
        <!-- 橡皮预览矩形 -->
        <div v-if="eraserPreview.show" :style="{
          position: 'absolute',
          left: eraserPreview.x + 'px',
          top: eraserPreview.y + 'px',
          width: eraserPreview.width + 'px',
          height: eraserPreview.height + 'px',
          background: 'rgba(0,0,0,0.03)',
          borderRadius: '4px',
          pointerEvents: 'none',
          zIndex: 20,
          transform: 'translate(-50%, -50%)'
        }"></div>

          <!-- 全屏按钮 -->
          <button class="fullscreen-toggle" @click="toggleFullscreen" v-if="!isImageUploaded">
            <!-- 进入全屏图标 -->
            <svg v-if="!isFullscreen" class="fullscreen-icon" viewBox="0 0 1024 1024" version="1.1"
              xmlns="http://www.w3.org/2000/svg">
              <path
                d="M409.2 897.1H215.5c-50.2 0-91-40.8-91-91V612.4c0-11 9-20 20-20s20 9 20 20v193.7c0 28.1 22.9 51 51 51h193.7c11 0 20 9 20 20s-8.9 20-20 20zM878.9 427.4c-11 0-20-9-20-20V213.7c0-28.1-22.9-51-51-51H614.2c-11 0-20-9-20-20s9-20 20-20h193.7c50.2 0 91 40.8 91 91v193.7c0 11.1-9 20-20 20zM144.5 427.4c-11 0-20-9-20-20V213.7c0-50.2 40.8-91 91-91h193.7c11 0 20 9 20 20s-9 20-20 20H215.5c-28.1 0-51 22.9-51 51v193.7c0 11.1-8.9 20-20 20zM807.9 897.1H614.2c-11 0-20-9-20-20s9-20 20-20h193.7c28.1 0 51-22.9 51-51V612.4c0-11 9-20 20-20s20 9 20 20v193.7c0 50.2-40.9 91-91 91z"
                fill="currentColor" />
              <path
                d="M382.5 398.8c-5.1 0-10.2-2-14.1-5.9L176.8 201.4c-7.8-7.8-7.8-20.5 0-28.3 7.8-7.8 20.5-7.8 28.3 0l191.6 191.6c7.8 7.8 7.8 20.5 0 28.3-3.9 3.8-9.1 5.8-14.2 5.8z"
                fill="currentColor" />
              <path
                d="M842.3 860.5c-5.1 0-10.2-2-14.1-5.9L636.6 663.1c-7.8-7.8-7.8-20.5 0-28.3s20.5-7.8 28.3 0l191.6 191.6c7.8 7.8 7.8 20.5 0 28.3-4 3.8-9.1 5.8-14.2 5.8z"
                fill="currentColor" />
              <path
                d="M189.7 859.8c-5.1 0-10.2-2-14.1-5.9-7.8-7.8-7.8-20.5 0-28.3L367.2 634c7.8-7.8 20.5-7.8 28.3 0s7.8 20.5 0 28.3L203.9 854c-3.9 3.9-9.1 5.8-14.2 5.8z"
                fill="currentColor" />
              <path
                d="M651.4 400.1c-5.1 0-10.2-2-14.1-5.9-7.8-7.8-7.8-20.5 0-28.3l191.6-191.6c7.8-7.8 20.5-7.8 28.3 0 7.8 7.8 7.8 20.5 0 28.3L665.6 394.2c-4 3.9-9.1 5.9-14.2 5.9z"
                fill="currentColor" />
            </svg>
            <!-- 退出全屏图标 -->
            <svg v-if="isFullscreen" class="fullscreen-icon" viewBox="0 0 1024 1024" version="1.1"
              xmlns="http://www.w3.org/2000/svg">
              <path
                d="M404.3 915.2c-11 0-20-9-20-20V692.8c0-29.9-24.3-54.2-54.2-54.2H127.7c-11 0-20-9-20-20s9-20 20-20h202.4c51.9 0 94.2 42.2 94.2 94.2v202.4c0 11-9 20-20 20zM894.9 424.5H692.5c-51.9 0-94.2-42.2-94.2-94.2V128c0-11 9-20 20-20s20 9 20 20v202.4c0 29.9 24.3 54.2 54.2 54.2h202.4c11 0 20 9 20 20s-8.9 19.9-20 19.9zM330.1 424.5H127.7c-11 0-20-9-20-20s9-20 20-20h202.4c29.9 0 54.2-24.3 54.2-54.2V128c0-11 9-20 20-20s20 9 20 20v202.4c0 51.9-42.3 94.1-94.2 94.1zM618.4 915.2c-11 0-20-9-20-20V692.8c0-51.9 42.2-94.2 94.2-94.2H895c11 0 20 9 20 20s-9 20-20 20H692.5c-29.9 0-54.2 24.3-54.2 54.2v202.4c0.1 11-8.9 20-19.9 20z"
                fill="currentColor" />
              <path
                d="M355.8 378.1c-5.1 0-10.2-2-14.1-5.9L141.5 172.1c-7.8-7.8-7.8-20.5 0-28.3s20.5-7.8 28.3 0l200.1 200.1c7.8 7.8 7.8 20.5 0 28.3-3.9 3.9-9 5.9-14.1 5.9zM856.7 877c-5.1 0-10.2-2-14.1-5.9L642.4 671c-7.8-7.8-7.8-20.5 0-28.3 7.8-7.8 20.5-7.8 28.3 0l200.1 200.1c7.8 7.8 7.8 20.5 0 28.3-3.8 3.9-8.9 5.9-14.1 5.9zM156.9 877.7c-5.1 0-10.2-2-14.1-5.9-7.8-7.8-7.8-20.5 0-28.3l200.1-200.1c7.8-7.8 20.5-7.8 28.3 0s7.8 20.5 0 28.3L171.1 871.8c-3.9 4-9 5.9-14.2 5.9zM655.9 376.8c-5.1 0-10.2-2-14.1-5.9-7.8-7.8-7.8-20.5 0-28.3l200.1-200.1c7.8-7.8 20.5-7.8 28.3 0 7.8 7.8 7.8 20.5 0 28.3L670 370.9c-3.9 3.9-9 5.9-14.1 5.9z"
                fill="currentColor" />
            </svg>
          </button>

          <!-- 调色盘面板 -->
          <div class="palette-sidebar" v-if="showPalette && currentMode === 'draw'">
            <div class="palette-header">调色盘</div>
            <div class="palette-basic-colors">
              <div v-for="color in basicColors" :key="color" class="palette-color-block"
                :style="{ backgroundColor: color }" @click="selectBasicColor(color)"></div>
            </div>
            <div class="palette-rgb-picker">
              <label>挑个喜欢的颜色</label>
              <input type="color" v-model="currentColor" @input="changeColor(currentColor)">
            </div>
          </div>

          <!-- SVG素材面板 -->
          <div class="svg-panel" v-if="showSvgPanel && currentMode === 'collage'">
            <div class="svg-panel-header">
              {{ currentSvgCategory?.name }}素材
              <button class="svg-panel-close" @click="showSvgPanel = false">×</button>
            </div>
            <div class="svg-panel-content">
              <div class="svg-grid">
                <div class="svg-item" v-for="(item, index) in currentSvgCategory?.items" :key="index"
                  @click="addSvgElement(item, canvasRef.value.width / 2, canvasRef.value.height / 2)">
                  <div class="svg-icon" v-html="item.svgCode"></div>
                  <div class="svg-name">{{ item.name }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 功能管理器 -->
          <div class="tool-manager" @mouseenter="showToolMenu = true" @mouseleave="showToolMenu = false">
            <button class="manager-btn">
              <svg t="1755683864144" class="icon" viewBox="0 0 1024 1024" version="1.1"
                xmlns="http://www.w3.org/2000/svg" p-id="7428" width="20" height="20">
                <path
                  d="M291.52 67.52l4.48 3.648 217.024 217.088 130.56-130.496c54.72-54.72 141.568-60.608 204.736-16.448l9.28 6.976 10.752 9.472c60.992 60.992 60.992 161.152 0 224.832L736.832 513.92l215.872 213.952a32 32 0 0 1 3.84 40.96l-3.712 4.416-179.52 179.52a32 32 0 0 1-40.832 3.648l-4.48-3.648-214.976-215.04-179.008 179.136a32 32 0 0 1-17.6 8.96l-5.056 0.384H131.84a32 32 0 0 1-32-32v-179.52a32 32 0 0 1 9.344-22.656l179.968-179.968-217.856-216.064a32 32 0 0 1-3.84-40.96l3.712-4.416 179.52-179.52a32 32 0 0 1 40.832-3.648z m400.064 491.712l-133.312 133.312 192.384 192.384 134.144-134.208-193.216-191.488zM567.936 323.84L163.84 727.936v134.336h134.208l404.16-404.16L567.936 323.84zM273.344 139.072L139.2 273.152l195.264 193.664 133.312-133.312-194.432-194.432z m544 58.88c-38.528-31.168-94.528-28.928-128.512 5.12L613.12 278.592l134.272 134.272 75.136-75.072c32-33.472 36.032-83.84 13.312-119.232L830.72 211.2l-6.144-6.784z"
                  fill="currentColor" p-id="7429"></path>
              </svg>
            </button>
            <div class="tool-menu" v-show="showToolMenu">
              <button class="menu-item" @mouseenter="highlightItem('draw')" @mouseleave="highlightItem(null)"
                @click="switchMode('draw')">绘画模式</button>
              <button class="menu-item" @mouseenter="highlightItem('collage')" @mouseleave="highlightItem(null)"
                @click="switchMode('collage')">拼贴模式</button>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <div style="position: absolute; left: 50%; bottom: 32px; transform: translateX(-50%); z-index: 100; display: flex; gap: 12px;">
            <button class="action-btn clear" @click="clearCanvas" v-if="hasDrawing">
              {{ isImageUploaded ? '返回手绘' : '清空画布' }}
            </button>
            <button class="action-btn submit" @click="analyzeDrawing" v-if="(isImageUploaded || currentFileName)"
              :disabled="isLoading">
              {{ isLoading ? '分析中...' : '前往分析' }}
            </button>
          </div>
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
// 撤回与取消撤回功能
import { ref, computed } from 'vue'
const undoStack = ref([])
const redoStack = ref([])
// 计算属性：只有当撤回栈中有元素时才能撤回
const canUndo = computed(() => undoStack.value.length > 0)
// 计算属性：只有当取消撤回栈中有元素时才能取消撤回
const canRedo = computed(() => redoStack.value.length > 0)
// 计算属性：当画布上有内容或撤回栈/取消撤回栈中有内容时才能清空画布
const canClear = computed(() => hasDrawing.value || undoStack.value.length > 1 || redoStack.value.length > 0)

// 初始化画布
onMounted(() => {
  if (canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    // 填充白色背景
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    // 初始状态不保存到撤回栈
    // 确保初始状态下撤回按钮是禁用的
  }
})

function saveCanvasState() {
  // 新绘制时保存快照
  if (canvasRef.value) {
    step.value++
    // 如果当前步骤小于历史记录长度，说明是在历史中间进行的新绘制
    // 需要截断数组，删除当前步骤之后的所有历史记录
    if (step.value < canvasHistory.value.length) {
      canvasHistory.value.length = step.value
    }
    // 添加新的绘制到历史记录
    canvasHistory.value.push(canvasRef.value.toDataURL())
    hasDrawing.value = true // 确保标记为有绘画内容
  }
}

function undoCanvas() {
  // 确保撤回栈中有状态可以撤回，并且画布引用存在
  if (undoStack.value && undoStack.value.length > 0 && canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')
    // 当前状态保存到取消撤回栈
    redoStack.value.push(canvasRef.value.toDataURL())
    // 移除当前状态
    undoStack.value.pop()

    if (undoStack.value.length > 0) {
      // 获取上一个状态
      const previousState = undoStack.value[undoStack.value.length - 1]

      // 加载并显示上一个状态
      const img = new window.Image()
      img.onload = function() {
        ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
        ctx.drawImage(img, 0, 0)
      }
      img.src = previousState
    } else {
      // 如果撤回栈为空，则清空画布
      ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
      hasDrawing.value = false
    }
  }
}

function redoCanvas() {
  // 检查是否可以重做（步骤小于历史记录长度-1）
  if (step.value < canvasHistory.value.length - 1 && canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')
    // 步骤加1
    step.value++

    // 加载并显示下一个状态
    const canvasPic = new Image()
    canvasPic.src = canvasHistory.value[step.value]
    canvasPic.addEventListener('load', () => {
      ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
      ctx.drawImage(canvasPic, 0, 0)
      hasDrawing.value = true // 重做后一定有内容
    })
  } else {
    console.log('已经是最新的记录了')
  }
}
// 合并画布mousemove事件，既处理绘画又处理橡皮预览
function handleCanvasAreaMove(e) {
  draw(e)
  if (currentTool.value === 'eraser') {
    const rect = canvasRef.value.getBoundingClientRect()
    eraserPreview.x = e.clientX - rect.left
    eraserPreview.y = e.clientY - rect.top
    eraserPreview.width = eraserWidth.value * 2
    eraserPreview.height = eraserWidth.value * 2 * 9 / 16
    eraserPreview.show = true
  } else {
    eraserPreview.show = false
  }
}
import { reactive } from 'vue'
// ...existing code...
const showPalette = ref(false)
const basicColors = [
  '#000000', '#FFFFFF', '#808080', '#FF0000', '#FFFF00',
  '#0000FF', '#FFA500', '#008000', '#800080', '#E34234', '#008080', '#4B0082'
]
function selectBasicColor(color) {
  currentColor.value = color
  changeColor(color)
  showPalette.value = false
}
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config'
import NavBarUser from '@/components/NavBarUser.vue'

const router = useRouter()
const canvasRef = ref(null)
const isLoading = ref(false)
const currentFileName = ref('')
const analysisResult = ref('')
const currentPage = ref(1)
const sections = ref([])

// 绘画相关的状态
// 橡皮预览状态
const eraserPreview = reactive({
  show: false,
  x: 0,
  y: 0,
  width: 32,
  height: 18
})

function handleCanvasMouseEnter(e) {
  if (currentTool.value === 'eraser') {
    eraserPreview.show = true
  }
}

function handleCanvasMouseMove(e) {
  if (currentTool.value === 'eraser') {
    const rect = canvasRef.value.getBoundingClientRect()
    eraserPreview.x = e.clientX - rect.left
    eraserPreview.y = e.clientY - rect.top
    eraserPreview.width = eraserWidth.value * 2
    eraserPreview.height = eraserWidth.value * 2 * 9 / 16
    eraserPreview.show = true
  } else {
    eraserPreview.show = false
  }
}

function handleCanvasMouseLeave() {
  eraserPreview.show = false
}
const isDrawing = ref(false)
const isDragging = ref(false)
const currentTool = ref('pen') // pen, eraser
const currentColor = ref('#000000')
const lineWidth = ref(5)
const showSizeSlider = ref(false) // 控制画笔粗细调节栏显示
const showEraserSlider = ref(false) // 控制橡皮擦粗细调节栏显示
const sliderHoverTimer = ref(null) // 用于控制滑块显示/隐藏的定时器
const eraserHoverTimer = ref(null) // 用于控制橡皮擦滑块显示/隐藏的定时器
const eraserWidth = ref(10) // 橡皮擦默认宽度

// 鼠标进入画笔按钮时显示滑块
const handlePenMouseEnter = () => {
  clearTimeout(sliderHoverTimer.value)
  showSizeSlider.value = true
}

// 鼠标进入滑块时保持滑块显示
const handleSliderMouseEnter = () => {
  clearTimeout(sliderHoverTimer.value)
  showSizeSlider.value = true
}

// 鼠标离开滑块时延迟隐藏滑块，给用户足够时间移动到滑块上
const handleSliderMouseLeave = () => {
  sliderHoverTimer.value = setTimeout(() => {
    showSizeSlider.value = false
  }, 300) // 300毫秒延迟，避免鼠标移动过程中的闪烁
}

// 鼠标进入橡皮擦按钮时显示滑块
const handleEraserMouseEnter = () => {
  clearTimeout(eraserHoverTimer.value)
  showEraserSlider.value = true
}

// 鼠标进入橡皮擦滑块时保持滑块显示
const handleEraserSliderMouseEnter = () => {
  clearTimeout(eraserHoverTimer.value)
  showEraserSlider.value = true
}

// 鼠标离开橡皮擦滑块时延迟隐藏滑块
const handleEraserSliderMouseLeave = () => {
  eraserHoverTimer.value = setTimeout(() => {
    showEraserSlider.value = false
  }, 300)
}

// 改变橡皮擦宽度
const changeEraserWidth = (width) => {
  eraserWidth.value = width
  if (ctx) {
    ctx.lineWidth = width
  }
}
const previewCircle = ref({ visible: false, x: 0, y: 0, size: 5 }) // 预览圆圈
let ctx = null
let lastX = 0
let lastY = 0
let canvasBeforePreview = null // 保存预览前的画布状态

// 模式切换相关
const currentMode = ref('draw') // 'draw' 或 'collage'
const showDynamicToolbar = ref(true) // 控制灵动岛工具栏显示
const showSvgPanel = ref(false) // 控制SVG面板显示
const currentSvgCategory = ref(null) // 当前选中的SVG类别

// SVG素材分类
const svgCategories = ref([
  {
    name: '房',
    items: [
      { name: '现代房', svgCode: '<!-- 开发者可在此处插入现代房SVG代码 -->' },
      { name: '传统房', svgCode: '<!-- 开发者可在此处插入传统房SVG代码 -->' },
      { name: '别墅', svgCode: '<!-- 开发者可在此处插入别墅SVG代码 -->' },
      { name: '公寓', svgCode: '<!-- 开发者可在此处插入公寓SVG代码 -->' }
    ]
  },
  {
    name: '树',
    items: [
      { name: '松树', svgCode: '<!-- 开发者可在此处插入松树SVG代码 -->' },
      { name: '柳树', svgCode: '<!-- 开发者可在此处插入柳树SVG代码 -->' },
      { name: '樟树', svgCode: '<!-- 开发者可在此处插入樟树SVG代码 -->' },
      { name: '枫树', svgCode: '<!-- 开发者可在此处插入枫树SVG代码 -->' },
      { name: '橡树', svgCode: '<!-- 开发者可在此处插入橡树SVG代码 -->' }
    ]
  },
  {
    name: '人',
    items: [
      { name: '男人', svgCode: '<!-- 开发者可在此处插入男人SVG代码 -->' },
      { name: '女人', svgCode: '<!-- 开发者可在此处插入女人SVG代码 -->' },
      { name: '小孩', svgCode: '<!-- 开发者可在此处插入小孩SVG代码 -->' },
      { name: '老人', svgCode: '<!-- 开发者可在此处插入老人SVG代码 -->' }
    ]
  }
])

// 显示工具菜单
const showToolMenu = ref(false)
const highlightedItem = ref(null)

const highlightItem = (item) => {
  highlightedItem.value = item
}

// 开始SVG拖拽
const startSvgDrag = (event, svg) => {
  event.dataTransfer.setData('text/plain', JSON.stringify(svg))
}

// 添加SVG元素
const addSvgElement = (svgData, x, y) => {
  const canvas = canvasRef.value
  const element = {
    id: Date.now(),
    type: 'svg',
    svgCode: svgData.svgCode,
    name: svgData.name,
    x: x,
    y: y,
    width: 100,
    height: 100,
    color: currentColor.value,
    rotation: 0,
    opacity: 1,
    zIndex: collageElements.value.length
  }
  collageElements.value.push(element)
  selectedElement.value = element
  hasDrawing.value = true
  redrawCollageElements()
}

// 显示SVG类别面板
const showSvgCategory = (category) => {
  currentSvgCategory.value = category
  showSvgPanel.value = true
}

// 图片处理相关的状态
const isImageUploaded = ref(false)
const hasDrawing = ref(false)
const fileInput = ref(null)
const isFullscreen = ref(false)

// 初始化画布
const initCanvas = () => {
  const canvas = canvasRef.value
  ctx = canvas.getContext('2d')

  // 设置画布大小为容器大小
  const container = canvas.parentElement
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight

  // 保存当前画布内容（如果有的话）
  let imageData = null
  if (canvas.width > 0 && canvas.height > 0) {
    imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  }

  // 确保画布尺寸与显示尺寸一致
  const rect = canvas.getBoundingClientRect()
  canvas.width = rect.width
  canvas.height = rect.height

  // 设置CSS尺寸为100%
  canvas.style.width = '100%'
  canvas.style.height = '100%'

  // 设置默认样式
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.strokeStyle = currentColor.value
  ctx.lineWidth = lineWidth.value

  // 填充白色背景
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // 初始化时不设置hasDrawing为true，让用户选择绘画或上传

  // 如果有保存的画布内容，恢复它
  if (imageData && !isImageUploaded.value) {
    const tempCanvas = document.createElement('canvas')
    const tempCtx = tempCanvas.getContext('2d')
    tempCanvas.width = imageData.width
    tempCanvas.height = imageData.height
    tempCtx.putImageData(imageData, 0, 0)

    // 计算缩放比例保持宽高比
    const scale = Math.min(canvas.width / tempCanvas.width, canvas.height / tempCanvas.height)
    const newWidth = tempCanvas.width * scale
    const newHeight = tempCanvas.height * scale
    const x = (canvas.width - newWidth) / 2
    const y = (canvas.height - newHeight) / 2

    ctx.drawImage(tempCanvas, x, y, newWidth, newHeight)
  }

  // 重绘拼接元素
  redrawCollageElements()
}

// 开始绘画
const startDrawing = (e) => {
  if (currentMode.value === 'draw' && !isImageUploaded.value) {
    isDrawing.value = true
    const rect = canvasRef.value.getBoundingClientRect()
    lastX = e.clientX - rect.left
    lastY = e.clientY - rect.top
  } else if (currentMode.value === 'collage') {
    handleCollageClick(e)
  }
}

// 绘画过程
const draw = (e) => {
  if (currentMode.value === 'draw' && isDrawing.value) {
    const rect = canvasRef.value.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    if (currentTool.value === 'eraser') {
      // 16:9矩形擦除
      ctx.save();
      // 设置橡皮擦模式
      ctx.globalCompositeOperation = 'destination-out';
      const width = eraserWidth.value * 2;
      const height = eraserWidth.value * 2 * 9 / 16;
      const steps = Math.max(Math.abs(x - lastX), Math.abs(y - lastY));

      // 使用插值确保连续擦除
      for (let i = 0; i <= steps; i++) {
        const ix = lastX + (x - lastX) * (i / steps);
        const iy = lastY + (y - lastY) * (i / steps);
        ctx.clearRect(ix - width / 2, iy - height / 2, width, height);
      }

      // 恢复之前的绘图状态
      ctx.restore();
    } else {
      ctx.beginPath()
      ctx.moveTo(lastX, lastY)
      ctx.lineTo(x, y)
      ctx.stroke()
    }

    lastX = x
    lastY = y

    // 用户开始绘画时标记有内容
    if (!hasDrawing.value) {
      hasDrawing.value = true
    }
  } else if (currentMode.value === 'collage') {
    const rect = canvasRef.value.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    if (isDragging.value && selectedElement.value) {
      // 拼接模式下的拖拽
      selectedElement.value.x = x - dragStartX
      selectedElement.value.y = y - dragStartY
    } else if (isScaling.value && selectedElement.value) {
      // 缩放元素
      const scaleX = x - selectedElement.value.x
      const scaleY = y - selectedElement.value.y

      selectedElement.value.width = Math.max(50, scaleX)
      selectedElement.value.height = Math.max(50, scaleY)
    } else if (isRotating.value && selectedElement.value) {
      // 旋转元素
      const centerX = selectedElement.value.x + selectedElement.value.width / 2
      const centerY = selectedElement.value.y + selectedElement.value.height / 2

      const angle = Math.atan2(y - centerY, x - centerX) * 180 / Math.PI
      selectedElement.value.rotation = angle
    }

    redrawCollageElements()
  }

  // 绘制预览圆圈 - 不在这里绘制，改为单独的函数
}

// 结束绘画
const stopDrawing = () => {
  if (isDrawing.value) {
    // 每次绘制结束时保存快照，无论是画笔还是橡皮擦
    saveCanvasState()
    isDrawing.value = false
  }
  isDragging.value = false
  isScaling.value = false
  isRotating.value = false
}

// 切换工具
const switchTool = (tool) => {
  currentTool.value = tool
  if (!ctx) return
  if (tool === 'pen') {
    ctx.globalCompositeOperation = 'source-over'
    ctx.strokeStyle = currentColor.value
    ctx.lineWidth = lineWidth.value
  } else if (tool === 'eraser') {
    ctx.globalCompositeOperation = 'destination-out'
    ctx.strokeStyle = 'rgba(0,0,0,1)'
    ctx.lineWidth = eraserWidth.value
  }
}

// 更改颜色
const changeColor = (color) => {
  currentColor.value = color
  if (!ctx) return
  if (currentTool.value === 'pen') {
    ctx.strokeStyle = color
  }
}

// 更改画笔大小
const changeLineWidth = (width) => {
  lineWidth.value = width
  ctx.lineWidth = width
}

// 开始预览画笔大小
const startSizePreview = () => {
  // 保存预览前的画布状态
  if (ctx) {
    canvasBeforePreview = ctx.getImageData(0, 0, canvasRef.value.width, canvasRef.value.height)
  }
  previewCircle.value.visible = true
  previewCircle.value.size = lineWidth.value
  drawPreviewCircle()
}

// 更新预览圆圈
const updateSizePreview = () => {
  if (previewCircle.value.visible) {
    const canvas = canvasRef.value
    previewCircle.value.x = canvas.width / 2
    previewCircle.value.y = canvas.height / 2
    previewCircle.value.size = lineWidth.value

    // 恢复原始画布状态并重新绘制预览圆圈
    if (ctx && canvasBeforePreview) {
      ctx.putImageData(canvasBeforePreview, 0, 0)
      drawPreviewCircle()
    }
  }
}

// 结束预览
const endSizePreview = () => {
  previewCircle.value.visible = false
  // 恢复预览前的画布状态，撤销预览圆圈
  if (ctx && canvasBeforePreview) {
    ctx.putImageData(canvasBeforePreview, 0, 0)
    canvasBeforePreview = null
  }
}

// 绘制预览形状
const drawPreviewCircle = () => {
  if (!previewCircle.value.visible || !ctx) return

  // 保存当前画布状态
  const imageData = ctx.getImageData(0, 0, canvasRef.value.width, canvasRef.value.height)

  ctx.save()

  // 根据当前工具绘制不同的预览形状
  if (currentTool.value === 'pen') {
    // 绘制圆形预览
    ctx.beginPath()
    ctx.arc(
      previewCircle.value.x,
      previewCircle.value.y,
      previewCircle.value.size,
      0,
      2 * Math.PI
    )
    ctx.fillStyle = 'rgba(128, 128, 128, 0.5)' // 半透明灰色
    ctx.fill()
    ctx.strokeStyle = 'rgba(80, 80, 80, 0.8)' // 深灰色边框
    ctx.lineWidth = 1
    ctx.stroke()
  } else if (currentTool.value === 'eraser') {
    // 绘制16:9长方形预览
    const width = eraserWidth.value * 1.6
    const height = eraserWidth.value * 0.9
    const x = previewCircle.value.x - width / 2
    const y = previewCircle.value.y - height / 2

    // 绘制阴影
    ctx.shadowColor = 'rgba(0, 0, 0, 0.3)'
    ctx.shadowBlur = 4
    ctx.shadowOffsetX = 2
    ctx.shadowOffsetY = 2

    // 绘制长方形
    ctx.beginPath()
    ctx.rect(x, y, width, height)
    ctx.fillStyle = 'rgba(239, 68, 68, 0.2)' // 淡红色半透明
    ctx.fill()
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.8)' // 红色边框
    ctx.lineWidth = 1
    ctx.stroke()
  }

  ctx.restore()

  // 在结束预览时会通过endSizePreview函数恢复原始画布状态
}

// 切换模式
const switchMode = (mode) => {
  currentMode.value = mode
  showDynamicToolbar.value = true
  selectedElement.value = null
  if (mode === 'collage') {
    redrawCollageElements()
  }
  if (mode === 'draw') {
    currentTool.value = 'pen'
    changeColor(currentColor.value)
  }
}

// 处理拼接模式的点击
const handleCollageClick = (e) => {
  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  // 检查是否点击了缩放控制点
  if (selectedElement.value) {
    const scaleX = selectedElement.value.x + selectedElement.value.width - 5
    const scaleY = selectedElement.value.y + selectedElement.value.height - 5

    if (x >= scaleX && x <= scaleX + 10 && y >= scaleY && y <= scaleY + 10) {
      isScaling.value = true
      return
    }

    // 检查是否点击了旋转控制点
    const rotateX = selectedElement.value.x + selectedElement.value.width / 2
    const rotateY = selectedElement.value.y - 20
    const distance = Math.sqrt(Math.pow(x - rotateX, 2) + Math.pow(y - rotateY, 2))

    if (distance <= 5) {
      isRotating.value = true
      return
    }
  }

  // 查找点击的元素（从上到下）
  const sortedElements = [...collageElements.value].sort((a, b) => b.zIndex - a.zIndex)
  let foundElement = null

  for (const element of sortedElements) {
    if (isPointInElement(x, y, element)) {
      foundElement = element
      break
    }
  }

  if (foundElement) {
    selectedElement.value = foundElement
    isDragging.value = true
    // 记录拖拽起始位置
    dragStartX = x - foundElement.x
    dragStartY = y - foundElement.y
  } else {
    selectedElement.value = null
  }

  redrawCollageElements()
}

// 检查点是否在元素内
const isPointInElement = (x, y, element) => {
  return x >= element.x &&
    x <= element.x + element.width &&
    y >= element.y &&
    y <= element.y + element.height
}


// 触发图片文件上传
const triggerShapeFileUpload = () => {
  shapeFileInput.value.click()
}

// 添加图片元素
const addImageElement = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = canvasRef.value
        const element = {
          id: Date.now(),
          type: 'image',
          src: e.target.result,
          image: img,
          x: canvas.width / 2 - img.width / 4,
          y: canvas.height / 2 - img.height / 4,
          width: img.width / 2,
          height: img.height / 2,
          rotation: 0,
          opacity: 1,
          zIndex: collageElements.value.length
        }
        collageElements.value.push(element)
        selectedElement.value = element
        hasDrawing.value = true
        redrawCollageElements()
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// 重绘拼接元素
const redrawCollageElements = () => {
  if (currentMode.value !== 'collage' || !ctx) return

  // 清空画布并填充白色背景
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)

  // 按z-index排序绘制元素
  const sortedElements = [...collageElements.value].sort((a, b) => a.zIndex - b.zIndex)

  sortedElements.forEach(element => {
    ctx.save()
    ctx.globalAlpha = element.opacity
    ctx.translate(element.x + element.width / 2, element.y + element.height / 2)
    ctx.rotate(element.rotation * Math.PI / 180)

    if (element.type === 'shape') {
      drawShape(element)
    } else if (element.type === 'text') {
      drawText(element)
    } else if (element.type === 'image') {
      drawImage(element)
    } else if (element.type === 'svg') {
      // 绘制SVG元素
      const tempSvg = document.createElement('div')
      tempSvg.innerHTML = element.svgCode
      const svgElement = tempSvg.firstChild

      // 设置SVG颜色
      if (svgElement) {
        svgElement.style.fill = element.color
        svgElement.style.width = `${element.width}px`
        svgElement.style.height = `${element.height}px`

        // 将SVG绘制到canvas
        const img = new Image()
        img.onload = () => {
          ctx.drawImage(img, -element.width / 2, -element.height / 2, element.width, element.height)
        }
        img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(tempSvg.innerHTML)}`
      }
    }

    ctx.restore()

    // 绘制选中状态的边框
    if (selectedElement.value && selectedElement.value.id === element.id) {
      drawSelectionBorder(element)

      // 绘制缩放控制点
      ctx.fillStyle = '#007bff'
      ctx.fillRect(
        element.x + element.width - 5,
        element.y + element.height - 5,
        10,
        10
      )

      // 绘制旋转控制点
      ctx.beginPath()
      ctx.arc(
        element.x + element.width / 2,
        element.y - 20,
        5,
        0,
        2 * Math.PI
      )
      ctx.fill()
    }
  })
}

// 绘制形状
const drawShape = (element) => {
  ctx.fillStyle = element.color
  const halfWidth = element.width / 2
  const halfHeight = element.height / 2

  switch (element.shapeType) {
    case 'rectangle':
      ctx.fillRect(-halfWidth, -halfHeight, element.width, element.height)
      break
    case 'circle':
      ctx.beginPath()
      ctx.arc(0, 0, halfWidth, 0, 2 * Math.PI)
      ctx.fill()
      break
    case 'triangle':
      ctx.beginPath()
      ctx.moveTo(0, -halfHeight)
      ctx.lineTo(-halfWidth, halfHeight)
      ctx.lineTo(halfWidth, halfHeight)
      ctx.closePath()
      ctx.fill()
      break
  }
}

// 绘制文字
const drawText = (element) => {
  ctx.fillStyle = element.color
  ctx.font = `${element.fontSize}px ${element.fontFamily}`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(element.text, 0, 0)
}

// 绘制图片
const drawImage = (element) => {
  if (element.image) {
    ctx.drawImage(element.image, -element.width / 2, -element.height / 2, element.width, element.height)
  }
}

// 绘制选中边框
const drawSelectionBorder = (element) => {
  ctx.save()
  ctx.strokeStyle = '#007bff'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.strokeRect(element.x - 2, element.y - 2, element.width + 4, element.height + 4)
  ctx.restore()
}

// 清空画布
const clearCanvas = () => {
  if (canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')
    // 清空画布
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    // 填充白色背景
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)

    // 重置状态
    isImageUploaded.value = false
    hasDrawing.value = false
    currentFileName.value = ''
    collageElements.value = []
    selectedElement.value = null

    // 关键修复：完全重置撤回和取消撤回栈
    // 创建全新的数组实例，彻底断开与之前历史记录的引用关系
    undoStack.value = []
    redoStack.value = []

    // 保存初始空白状态到撤回栈
    saveCanvasState()

    // 确保在保存初始状态后重置 hasDrawing 为 false
    hasDrawing.value = false

    // 保存一个新的初始空白状态到撤回栈
    // 这是清空后的第一个状态，作为新的起点
    const emptyState = canvasRef.value.toDataURL()
    undoStack.value.push(emptyState)

    // 确保清空画布是一个完全重置的操作
    console.log('画布已清空，历史记录已重置')
  }
}

// 全屏功能
const toggleFullscreen = async () => {
  const container = document.querySelector('.draw-container')

  try {
    if (!isFullscreen.value) {
      // 进入全屏
      if (container.requestFullscreen) {
        await container.requestFullscreen()
      } else if (container.webkitRequestFullscreen) {
        await container.webkitRequestFullscreen()
      } else if (container.mozRequestFullScreen) {
        await container.mozRequestFullScreen()
      } else if (container.msRequestFullscreen) {
        await container.msRequestFullscreen()
      }
    } else {
      // 退出全屏
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        await document.webkitExitFullscreen()
      } else if (document.mozCancelFullScreen) {
        await document.mozCancelFullScreen()
      } else if (document.msExitFullscreen) {
        await document.msExitFullscreen()
      }
    }
    isFullscreen.value = !isFullscreen.value
  } catch (err) {
    console.error('全屏切换错误:', err)
  }
}

// 监听全屏状态变化
const handleFullscreenChange = () => {
  const isCurrentlyFullscreen = !!(
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  )

  isFullscreen.value = isCurrentlyFullscreen

  // 全屏状态改变时重新初始化画布
  setTimeout(() => {
    initCanvas()
  }, 100)
}

// 处理键盘事件（ESC退出全屏）
const handleKeyDown = (event) => {
  if (event.key === 'Escape' && isFullscreen.value) {
    toggleFullscreen()
  }
  // F11 切换全屏
  if (event.key === 'F11') {
    event.preventDefault()
    toggleFullscreen()
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
  if (canvasRef.value && canvasRef.value.width > 0) {
    // 延迟执行以确保容器大小已更新
    setTimeout(() => {
      const container = canvasRef.value.parentElement
      const newWidth = container.clientWidth
      const newHeight = container.clientHeight

      // 只有当尺寸真正改变时才重新初始化（容差为5px）
      if (Math.abs(canvasRef.value.width - newWidth) > 5 ||
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

  // 添加全屏状态监听
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)

  // 添加键盘事件监听
  document.addEventListener('keydown', handleKeyDown)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)

  // 移除全屏状态监听
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange)

  // 移除键盘事件监听
  document.removeEventListener('keydown', handleKeyDown)
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

    // 检查画布是否为空
    if (!canvasRef.value) {
      ElMessage.error('画布未初始化')
      return
    }

    let imageData = canvasRef.value.toDataURL('image/png')
    console.log('Image data length:', imageData.length)
    console.log('Image data preview:', imageData.substring(0, 100))

    // 确保图片数据格式正确
    if (!imageData.startsWith('data:image/')) {
      imageData = 'data:image/png;base64,' + imageData
    }

    console.log('Sending request to:', `${config.baseURL}/api/save`)
    console.log('Request payload size:', JSON.stringify({
      image: imageData.substring(0, 100) + '...',
      isUploaded: isUploaded
    }))

    const response = await fetch(`${config.baseURL}/api/save`, {
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

    console.log('Response status:', response.status)
    console.log('Response ok:', response.ok)

    const data = await response.json()
    console.log('Response data:', data)

    if (response.ok) {
      currentFileName.value = data.file_name
      if (!isUploaded) {
        hasDrawing.value = true
      }
      ElMessage.success('保存成功!')
    } else {
      console.error('Save failed with status:', response.status, data)
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

    console.log('Sending analysis request to:', `${config.baseURL}/api/save`)
    console.log('Analysis payload:', {
      imageDataLength: imageData.length,
      analyze: true,
      isUploaded: isImageUploaded.value
    })

    const response = await fetch(`${config.baseURL}/api/save`, {
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
/* 优化撤回按钮置灰和禁止悬浮高亮 */
.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
  box-shadow: none;
}
/* 优化取消撤回按钮置灰和禁止悬浮高亮 */
.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
  box-shadow: none;
}
/* 右侧调色盘侧边栏样式 */
/* 右侧调色盘侧边栏卡片风格 */
/* 画布右侧调色盘侧边栏（窄、贴近画布右侧，距离上下边距相等） */
.palette-sidebar {
  position: absolute;
  top: 64px;
  right: 36px;
  width: 140px;
  min-height: calc(100% - 128px);
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 18px 12px 18px 12px;
  animation: palette-slide-in-canvas 0.28s cubic-bezier(.4, 1.4, .6, 1);
}

@keyframes palette-slide-in-canvas {
  from {
    right: -180px;
    opacity: 0;
  }

  to {
    right: 36px;
    opacity: 1;
  }
}

.palette-header {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 14px;
  color: #333;
}

.palette-basic-colors {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 16px;
}

.palette-color-block {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.18s, border-color 0.18s;
}

.palette-color-block:hover {
  transform: scale(1.18);
  border-color: #8b5cf6;
}

.palette-rgb-picker {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
}

.palette-rgb-picker label {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.palette-rgb-picker input[type="color"] {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  margin-top: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10);
}

.palette-rgb-value {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
}

.palette-close {
  margin-top: auto;
  margin-bottom: 6px;
  padding: 6px 16px;
  border: none;
  border-radius: 8px;
  background: #f3f4f6;
  color: #333;
  cursor: pointer;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: background 0.2s;
}

.palette-close:hover {
  background: #e5e7eb;
}

/* 灵动岛工具栏样式 */
/* 灵动岛工具栏（画布内上方，半透明白色） */
.dynamic-island-toolbar {
  position: absolute;
  top: 36px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.85);
  border-radius: 18px;
  padding: 6px 18px;
  display: flex;
  flex-direction: row;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.10);
  z-index: 11;
  min-width: 180px;
  max-width: 90%;
  height: 38px;
}

.toolbar-mode-switch {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.toolbar-mode-switch button {
  background: none;
  border: none;
  color: #fff;
  font-weight: bold;
  font-size: 16px;
  padding: 4px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.toolbar-mode-switch button.active {
  background: #444;
}

.toolbar-tools {
  display: flex;
  gap: 16px;
  align-items: center;
}

/* 工具栏按钮适配白色背景 */
/* 圆形工具栏按钮，SVG图标，悬浮浮起动画 */
.pen-tool-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pen-size-slider {
  position: absolute;
  top: 100%;
  margin-top: 0;
  /* 移除间距 */
  padding: 4px 12px;
  /* 减小上下内边距 */
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pen-size-slider input[type="range"] {
  width: 120px;
  height: 4px;
  appearance: none;
  -webkit-appearance: none;
  background: #e5e7eb;
  border-radius: 2px;
  outline: none;
}

.pen-size-slider input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}

.eraser-tool-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.eraser-size-slider {
  position: absolute;
  top: 100%;
  padding-top: 8px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding-left: 12px;
  padding-right: 12px;
  padding-bottom: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9;
}

.eraser-size-slider input[type="range"] {
  width: 120px;
  height: 4px;
  appearance: none;
  -webkit-appearance: none;
  background: #e5e7eb;
  border-radius: 2px;
  outline: none;
}

.eraser-size-slider input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #ef4444;
  border-radius: 50%;
  cursor: pointer;
}

.eraser-preview {
  margin-top: 8px;
  background: rgba(0, 0, 0, 0.1);
  border: 1px dashed #ef4444;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}

.toolbar-btn {
  background: rgba(255, 255, 255, 0.95);
  border: none;
  color: #333;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  margin: 0 4px;
  transition: transform 0.18s cubic-bezier(.4, 1.4, .6, 1), box-shadow 0.18s, background 0.2s;
}

.toolbar-btn:hover {
  transform: translateY(-6px) scale(1.12);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  background: #f3f4f6;
}

.toolbar-btn.active {
  background: #e5e7eb;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.12);
}

.color-picker.toolbar-btn {
  padding: 0;
  margin: 0 4px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: none;
}

.color-label {
  display: flex;
  align-items: center;
  gap: 2px;
}

/* 颜色选择器适配小尺寸 */
.color-label {
  display: flex;
  align-items: center;
  gap: 2px;
}

.color-picker {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
}

/* 确保页面充分利用视口高度 */
html,
body {
  height: 100%;
  margin: 0;
  padding: 0;
}

/* SVG面板样式 */
.svg-panel {
  position: absolute;
  right: 36px;
  top: 64px;
  width: 200px;
  max-height: 60vh;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: panel-slide-in 0.28s cubic-bezier(.4, 1.4, .6, 1);
}

@keyframes panel-slide-in {
  from {
    right: -220px;
    opacity: 0;
  }
  to {
    right: 36px;
    opacity: 1;
  }
}

.svg-panel-header {
  padding: 12px 16px;
  font-weight: bold;
  font-size: 16px;
  color: #333;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.svg-panel-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.svg-panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.svg-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.svg-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.svg-item:hover {
  background: #f3f4f6;
  transform: scale(1.05);
}

.svg-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.svg-name {
  font-size: 12px;
  margin-top: 4px;
  color: #666;
  text-align: center;
}

/* 功能管理器样式 */
.tool-manager {
  position: absolute;
  left: 10px;
  bottom: 10px;
  z-index: 10;
}

.manager-btn {
  margin-bottom: 8px;
  margin-left: 8px;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.2s;
  color: #4a4a4a;
}

.manager-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}

.manager-btn svg {
  width: 20px;
  height: 20px;
}

.tool-menu {
  position: absolute;
  bottom: 100%;
  left: 0;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  min-width: 120px;
}

.menu-item {
  display: block;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
}

.menu-item {
  transition: all 0.2s ease;
}

.menu-item:hover {
  background: #f0f8ff;
  transform: scale(1.02);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.menu-item.highlighted {
  background: #e1f0ff;
  font-weight: bold;
}

.draw-container {
  min-height: 100vh;
  height: 100vh;
  background-color: var(--color-background);
  display: flex;
  flex-direction: column;
}

.draw-content {
  flex: 1;
  max-width: 1920px;
  margin: 0 auto;
  padding: 84px 2rem 2rem;
  display: grid;
  grid-template-columns: 3fr 2fr;
  /* 调整比例：绘图区域3份，分析面板2份 */
  gap: 2rem;
  align-items: center;
  /* 垂直居中对齐 */
  justify-content: center;
  /* 水平居中对齐 */
  min-height: calc(100vh - 64px);
  /* 减去导航栏高度 */
}

.drawing-area {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  max-width: 800px;
  /* 限制绘图区域的最大宽度 */
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* 水平居中 */
  position: relative;
  /* 确保正确的定位上下文 */
  overflow: visible;
  /* 确保按钮不会被裁剪 */
}

.canvas-container {
  position: relative;
  width: 100%;
  max-width: 700px;
  /* 默认最大宽度 */
  aspect-ratio: 4/3;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto;
  /* 居中显示 */
}

#drawingCanvas {
  position: absolute;
  width: 100%;
  height: 100%;
  cursor: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1024 1024' width='32' height='32'><path d='M314.88 626.133333l96.213333 94.933334a130.346667 130.346667 0 0 1-108.16 54.826666 104.32 104.32 0 0 1-73.386666-27.52 102.4 102.4 0 0 0 42.666666-26.88 110.933333 110.933333 0 0 0 25.386667-64v-2.346666a59.52 59.52 0 0 1 7.893333-26.88 31.146667 31.146667 0 0 1 10.026667-2.56m14.08-64c-64 0-85.333333 27.733333-95.146667 85.333333v2.773333c-2.986667 18.773333-5.12 25.386667-8.533333 29.013334a39.68 39.68 0 0 1-8.746667 7.04 33.493333 33.493333 0 0 1-18.133333 5.12 29.866667 29.866667 0 0 1-8.746667-1.066667h-1.92a29.013333 29.013333 0 0 0-10.24-1.92A27.946667 27.946667 0 0 0 149.333333 717.013333c8.96 81.28 78.72 122.88 153.386667 122.88A189.226667 189.226667 0 0 0 481.28 725.333333a27.946667 27.946667 0 0 0-6.4-30.293333l-126.293333-125.653333a28.16 28.16 0 0 0-19.626667-8.106667l0.64 0.426667zM808.32 234.666667H810.666667c0 10.453333-9.386667 49.066667-97.493334 158.72-15.36 18.986667-31.146667 37.76-47.146666 56.106666-31.146667 35.84-147.626667 157.44-147.626667 157.44l-80.853333-81.493333s117.12-114.346667 154.24-147.413333c19.84-17.493333 40.32-34.56 60.586666-50.986667 100.053333-80.426667 140.8-92.373333 155.946667-92.373333m0-64c-47.146667 0-111.786667 38.826667-196.053333 106.666666-21.333333 17.066667-42.666667 34.773333-62.72 52.906667-38.677333 34.133333-76.373333 69.269333-113.066667 105.386667-14.72 14.72-29.653333 29.653333-44.16 44.586666l-3.413333 3.626667a60.8 60.8 0 0 0 0 85.333333l85.333333 86.4c11.306667 11.306667 26.666667 17.706667 42.666667 17.706667a60.586667 60.586667 0 0 0 42.666666-17.706667l3.2-3.2 9.813334-9.813333 34.773333-35.413333c35.84-37.12 71.893333-76.16 105.386667-114.773334 16.64-18.986667 32.853333-38.4 48.64-58.026666 102.186667-126.08 142.72-208 89.173333-249.813334a66.56 66.56 0 0 0-42.666667-13.866666h0.426667z' fill='%233D424D'/></svg>") 8 24, crosshair;
}

#erasingCanvas {
  position: absolute;
  width: 100%;
  height: 100%;
  cursor: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1029 1024' width='32' height='32'><path d='M968.96 387.2l-302.4-302.4c-17.76-17.76-41.28-27.36-65.76-27.36s-48 9.6-65.28 26.88l-476.16 476.16c-17.76 17.76-27.36 41.28-27.36 65.76s9.6 48 26.88 65.28l0.96 1.92h0.96l205.44 205.44c43.2 43.2 100.8 67.2 161.76 67.2 60.96 0 118.56-23.52 161.76-67.2l379.68-379.68c17.76-17.76 27.36-41.28 27.36-66.24-0.48-24.48-10.08-48-27.84-65.76z m-432.96 469.92c-29.76 26.88-68.16 41.76-108.48 41.76-43.2 0-83.52-16.8-114.24-47.04l-206.88-206.88c-10.08-10.08-10.08-26.88 0-36.96l90.24-90.24 339.36 339.36z m385.44-385.44l-337.92 337.92-339.36-339.36 337.92-337.92c4.8-4.8 11.52-7.68 18.24-7.68 7.2 0 13.44 2.88 18.24 7.68l302.4 302.4c10.56 10.08 10.56 26.88 0.48 36.96z' fill='%233D424D'/></svg>") 2 26, crosshair;
}

.fullscreen-toggle {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.2s;
  z-index: 10;
}

.fullscreen-toggle:hover {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}

.fullscreen-icon {
  width: 20px;
  height: 20px;
  color: #4a4a4a;
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
  z-index: 1;
  /* 确保工具栏在画布上方，但在按钮下方 */
  flex-wrap: wrap;
  max-width: 90%;
}

.mode-group {
  display: flex;
  gap: 0.5rem;
  margin-right: 1rem;
  padding-right: 1rem;
  border-right: 1px solid #e5e7eb;
}

.mode-btn {
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

.mode-btn:hover {
  background: #e5e7eb;
}

.mode-btn.active {
  background: #3b82f6;
  color: white;
}

.collage-tools {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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
  justify-content: center;
  /* 改为居中对齐 */
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
  /* 允许按钮在必要时换行 */
  width: 100%;
  /* 确保占满容器宽度 */
  position: relative;
  /* 确保正确的层级 */
  z-index: 10;
  /* 确保按钮在最上层 */
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  /* 防止文字换行 */
  flex-shrink: 0;
  /* 防止按钮被压缩 */
  position: relative;
  /* 确保正确的定位 */
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
  padding: 2.5rem;
  /* 增加内边距 */
  height: fit-content;
  /* 改为适应内容高度 */
  max-height: calc(100vh - 120px);
  /* 限制最大高度，留出空间 */
  overflow-y: auto;
  /* 允许垂直滚动 */
  align-self: center;
  /* 与画板居中对齐 */
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
  line-height: 1.6;
  /* 改善行间距 */
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
  line-height: 1.7;
  /* 增加行间距 */
  color: #333;
  padding: 1.5rem;
  /* 增加内边距 */
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.95rem;
  /* 稍微调整字体大小 */
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

.element-properties {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
  max-width: 600px;
  border: 1px solid #e5e7eb;
}

.element-properties h4 {
  margin: 0 0 1rem 0;
  color: #1a1a1a;
  font-size: 1rem;
  font-weight: 600;
}

.property-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.property-group label {
  min-width: 80px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a4a4a;
}

.property-group input[type="range"] {
  flex: 1;
  min-width: 120px;
}

.property-group input[type="color"] {
  width: 40px;
  height: 30px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.property-group span {
  font-size: 0.875rem;
  color: #666;
  min-width: 50px;
}

.delete-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.delete-btn:hover {
  background: #dc2626;
}

.layer-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.layer-btn:hover {
  background: #4b5563;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 全屏模式样式 */
.draw-container:fullscreen {
  background: #000000;
}

.draw-container:fullscreen .draw-content {
  padding: 2rem;
  grid-template-columns: 1fr;
  justify-items: center;
  align-items: center;
  max-width: none;
  min-height: 100vh;
  /* 全屏时使用100vh */
}

.draw-container:fullscreen .drawing-area {
  max-width: none;
  width: 100%;
  height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.draw-container:fullscreen .canvas-container {
  max-width: none;
  width: 90vw;
  height: 80vh;
  aspect-ratio: unset;
}

.draw-container:fullscreen .analysis-panel {
  display: none;
}

.draw-container:fullscreen .drawing-tools {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.draw-container:fullscreen .action-buttons {
  background: rgba(0, 0, 0, 0.8);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.draw-container:fullscreen .fullscreen-toggle {
  background: rgba(255, 255, 255, 0.8);
}

.draw-container:fullscreen .fullscreen-toggle:hover {
  background: rgba(255, 255, 255, 1);
}

/* WebKit 全屏样式 */
.draw-container:-webkit-full-screen {
  background: #000000;
}

.draw-container:-webkit-full-screen .draw-content {
  padding: 2rem;
  grid-template-columns: 1fr;
  justify-items: center;
  align-items: center;
  max-width: none;
  min-height: 100vh;
}

.draw-container:-webkit-full-screen .drawing-area {
  max-width: none;
  width: 100%;
  height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.draw-container:-webkit-full-screen .canvas-container {
  max-width: none;
  width: 90vw;
  height: 80vh;
  aspect-ratio: unset;
}

.draw-container:-webkit-full-screen .analysis-panel {
  display: none;
}

.draw-container:-webkit-full-screen .drawing-tools {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.draw-container:-webkit-full-screen .action-buttons {
  background: rgba(0, 0, 0, 0.8);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.draw-container:-webkit-full-screen .fullscreen-toggle {
  background: rgba(255, 255, 255, 0.8);
}

.draw-container:-webkit-full-screen .fullscreen-toggle:hover {
  background: rgba(255, 255, 255, 1);
}

/* Mozilla 全屏样式 */
.draw-container:-moz-full-screen {
  background: #000000;
}

.draw-container:-moz-full-screen .draw-content {
  padding: 2rem;
  grid-template-columns: 1fr;
  justify-items: center;
  align-items: center;
  max-width: none;
  min-height: 100vh;
}

.draw-container:-moz-full-screen .drawing-area {
  max-width: none;
  width: 100%;
  height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.draw-container:-moz-full-screen .canvas-container {
  max-width: none;
  width: 90vw;
  height: 80vh;
  aspect-ratio: unset;
}

.draw-container:-moz-full-screen .analysis-panel {
  display: none;
}

.draw-container:-moz-full-screen .drawing-tools {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.draw-container:-moz-full-screen .action-buttons {
  background: rgba(0, 0, 0, 0.8);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.draw-container:-moz-full-screen .fullscreen-toggle {
  background: rgba(255, 255, 255, 0.8);
}

.draw-container:-moz-full-screen .fullscreen-toggle:hover {
  background: rgba(255, 255, 255, 1);
}

/* MS 全屏样式 */
.draw-container:-ms-fullscreen {
  background: #000000;
}

.draw-container:-ms-fullscreen .draw-content {
  padding: 2rem;
  grid-template-columns: 1fr;
  justify-items: center;
  align-items: center;
  max-width: none;
  min-height: 100vh;
}

.draw-container:-ms-fullscreen .drawing-area {
  max-width: none;
  width: 100%;
  height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.draw-container:-ms-fullscreen .canvas-container {
  max-width: none;
  width: 90vw;
  height: 80vh;
  aspect-ratio: unset;
}

.draw-container:-ms-fullscreen .analysis-panel {
  display: none;
}

.draw-container:-ms-fullscreen .drawing-tools {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.draw-container:-ms-fullscreen .action-buttons {
  background: rgba(0, 0, 0, 0.8);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.draw-container:-ms-fullscreen .fullscreen-toggle {
  background: rgba(255, 255, 255, 0.8);
}

.draw-container:-ms-fullscreen .fullscreen-toggle:hover {
  background: rgba(255, 255, 255, 1);
}

/* 超大屏幕优化（4K等） */
@media (min-width: 1920px) {
  .draw-content {
    grid-template-columns: 800px 600px;
    /* 更大的固定尺寸 */
    gap: 4rem;
    /* 更大的间距 */
    justify-content: center;
    align-items: center;
  }

  .drawing-area {
    max-width: 800px;
    padding: 3rem;
  }

  .analysis-panel {
    padding: 3rem;
    font-size: 1.1rem;
    /* 稍大的字体 */
  }
}

/* 大屏幕优化 */
@media (min-width: 1400px) {
  .draw-content {
    grid-template-columns: 700px 500px;
    /* 绘图区域700px，分析面板500px */
    justify-content: center;
    align-items: center;
    /* 确保垂直居中 */
    gap: 3rem;
    /* 增加间距 */
  }
}

@media (min-width: 1200px) and (max-width: 1399px) {
  .drawing-area {
    max-width: 700px;
    /* 中大屏幕的限制 */
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

  .canvas-container {
    max-width: 700px;
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 0.8rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
    /* 允许按钮换行 */
    width: 100%;
    padding: 0 1rem;
    /* 添加左右内边距 */
  }

  .action-btn {
    padding: 0.7rem 1rem;
    font-size: 0.85rem;
    min-width: 90px;
    /* 确保按钮有最小宽度 */
    white-space: nowrap;
    /* 防止文字换行 */
    flex: 0 0 auto;
    /* 防止按钮被压缩 */
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
    padding: 84px 1rem 2rem;
    /* 减少侧边距 */
    gap: 1.5rem;
  }

  .drawing-area {
    max-width: 600px;
    width: 100%;
    padding: 1.5rem;
    /* 减少内边距 */
  }

  .canvas-container {
    max-width: 600px;
  }

  .action-buttons {
    gap: 0.6rem;
    margin-top: 1rem;
    flex-direction: row;
    /* 确保是水平排列 */
    flex-wrap: wrap;
    /* 允许换行 */
    justify-content: center;
    align-items: center;
    padding: 0.5rem;
    /* 添加内边距 */
  }

  .action-btn {
    padding: 0.6rem 0.8rem;
    font-size: 0.8rem;
    min-width: 80px;
    max-width: 120px;
    /* 限制最大宽度防止过宽 */
    text-align: center;
  }

  .analysis-panel {
    max-width: 600px;
    padding: 1.5rem;
    /* 减少内边距 */
  }
}

@media (max-width: 768px) {
  .draw-content {
    padding: 84px 1rem 1rem;
    /* 减少侧边距 */
    gap: 1.5rem;
    align-items: center;
    /* 保持居中对齐 */
  }

  .canvas-container {
    max-width: 600px;
    /* 在小屏幕上进一步限制宽度 */
  }

  .drawing-area {
    max-width: 100%;
    padding: 1.5rem;
  }

  .analysis-panel {
    padding: 1.5rem;
    align-self: center;
    /* 确保与画板对齐 */
  }
}

@media (max-width: 640px) {
  .draw-content {
    padding: 84px 0.5rem 1rem;
    /* 进一步减少侧边距 */
    min-height: calc(100vh - 64px);
    align-items: center;
    /* 保持居中对齐 */
  }

  .drawing-tools {
    flex-direction: column;
    align-items: center;
    bottom: 0.5rem;
    /* 调整工具栏位置 */
    max-width: 95%;
    gap: 0.5rem;
  }

  .mode-group {
    margin-right: 0;
    padding-right: 0;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .collage-tools {
    flex-wrap: wrap;
    justify-content: center;
  }

  .element-properties {
    margin-top: 1rem;
    padding: 0.75rem;
    max-width: 100%;
  }

  .property-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .property-group input[type="range"] {
    width: 100%;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
    /* 确保垂直布局时也居中 */
    gap: 0.75rem;
  }

  .action-btn {
    width: 100%;
    max-width: 300px;
    /* 限制最大宽度，保持美观 */
  }

  .canvas-container {
    max-width: 100%;
    /* 在最小屏幕上使用全宽 */
  }

  .drawing-area {
    padding: 1rem;
  }

  .analysis-panel {
    padding: 1rem;
    align-self: center;
    /* 确保与画板对齐 */
  }
}
</style>
