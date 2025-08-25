<template>
  <div class="draw-container">
    <NavBarUser v-if="!isFullscreen" />

    <main class="draw-content">
      <div class="drawing-area">
        <!-- 灵动岛工具栏（画布内上方） -->
        <div class="dynamic-island-toolbar">
          <div v-if="currentMode === 'draw'" class="toolbar-tools">
            <button class="toolbar-btn" @click="undoCanvas" :disabled="!hasDrawing || !canUndo" title="撤回">
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
            <!-- 清空画布按钮单独显示，不与其他按钮并列 -->
            <button class="toolbar-btn" @click="clearCanvas" :disabled="!hasDrawing && !canClear" title="清空画布" style="margin-left: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <rect x="4" y="4" width="16" height="16" rx="2" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M8 12h8" stroke="#333" stroke-width="1.5" stroke-linecap="round"/>
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
            <button class="toolbar-btn" @click="addSvgElement(svgCategories[0].items[0], canvasRef.value.width / 2, canvasRef.value.height / 2)" title="添加房">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M3 21h18v-3H3v3zm3-6h12v-3H6v3zm-3-7l9-4 9 4v2H3V8z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="openSelectionPanel('树木', svgCategories[0].items[1].subItems)" title="添加树">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 3L8 10H16L12 3z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 10L6 16H18L14 10" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 21V16" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="addSvgElement(svgCategories[0].items[2], canvasRef.value.width / 2, canvasRef.value.height / 2)" title="添加人">
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

          <!-- 右侧选择面板 -->
          <div class="selection-sidebar" v-if="showSelectionPanel && currentMode === 'collage'">
            <div class="selection-header">
              <h3>{{ selectedCategoryName }}</h3>
              <button class="close-btn" @click="closeSelectionPanel">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M18 6L6 18" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M6 6L18 18" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
            <div class="selection-items">
              <div
                class="selection-item"
                v-for="(item, index) in selectedItems"
                :key="index"
                @click="selectItem(item)"
              >
                <div class="item-icon">
                  <div v-html="item.svgCode"></div>
                </div>
                <span class="item-name">{{ item.name }}</span>
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
            <!-- 清空画布按钮已移至灵动岛工具栏 -->
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
// 计算属性：当撤回栈或取消撤回栈中有元素时可以清空画布
const canClear = computed(() => undoStack.value.length > 0 || redoStack.value.length > 0)

// 初始化时设置画布为白色背景
onMounted(() => {
  if (canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    // 填充白色背景
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    // 不保存初始状态到撤回栈，保持撤回栈为空
    // 这样确保初始状态下不能撤回
  }
})

function saveCanvasState() {
  // 新绘制时保存快照，并清空 redoStack
  if (canvasRef.value) {
    // 保存当前画布状态到撤回栈
    const currentState = canvasRef.value.toDataURL();
    undoStack.value.push(currentState);
    // 创建全新的数组实例，彻底断开与之前历史记录的引用关系
    redoStack.value = new Array(); // 清空取消撤回栈
    hasDrawing.value = true; // 确保标记为有绘画内容
  }
}

function undoCanvas() {
  // 确保撤回栈中有状态可以撤回，并且画布引用存在
  if (undoStack.value && undoStack.value.length > 0 && canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')

    // 保存当前状态到取消撤回栈，无论是画笔还是橡皮擦操作
    const currentState = canvasRef.value.toDataURL();
    redoStack.value.push(currentState);

    // 移除当前状态
    undoStack.value.pop();

    // 如果撤回栈为空，说明已经撤回到初始状态
    if (undoStack.value.length === 0) {
      // 清空画布
      ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
      // 填充白色背景
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height);
      // 标记为无绘画内容
      hasDrawing.value = false;
    } else {
      // 获取上一个状态
      const previousState = undoStack.value[undoStack.value.length - 1];

      // 加载并显示上一个状态
      const img = new window.Image();
      img.onload = function() {
        // 恢复绘图模式为默认
        ctx.globalCompositeOperation = 'source-over';
        ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
        ctx.drawImage(img, 0, 0);

        // 如果当前工具是橡皮擦，恢复橡皮擦模式
        if (currentTool.value === 'eraser') {
          ctx.globalCompositeOperation = 'destination-out';
        }
      }
      img.src = previousState;
    }
  }
}

function redoCanvas() {
  // 检查取消撤回栈是否有内容，并且确保画布引用存在
  if (redoStack.value && redoStack.value.length > 0 && canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d');

    // 获取最近的取消撤回状态
    const redoState = redoStack.value.pop();

    // 当前状态保存到撤回栈
    const currentState = canvasRef.value.toDataURL();
    undoStack.value.push(currentState);

    // 加载并显示取消撤回的状态
    const img = new window.Image();
    img.onload = function() {
      // 恢复绘图模式为默认
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
      ctx.drawImage(img, 0, 0);

      // 如果当前工具是橡皮擦，恢复橡皮擦模式
      if (currentTool.value === 'eraser') {
        ctx.globalCompositeOperation = 'destination-out';
      }

      hasDrawing.value = true; // 取消撤回后一定有内容
    }
    img.src = redoState;
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

// SVG素材分类
const svgCategories = ref([
  {
    name: '房树人',
    items: [
      {
        subItems: [
          {name: '房', svgCode: '<!-- 开发者可在此处插入房SVG代码 -->'},
        ]
       },
      {
        subItems: [
          { name: '树林', svgCode: '<svg t="1756132443539" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="59810" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M952.75 515.22a194.77 194.77 0 0 0-60.23-141.49a168.81 168.81 0 0 0 6.73-47.29c0-93.36-75.94-169.31-169.29-169.31-87.69 0-160 67-168.47 152.52a126.44 126.44 0 0 0-126.15 30.67a127.91 127.91 0 0 0-12.73 14.6c-4.34-69.48-20.05-134-45.34-184.9-33-66.41-79.11-103-129.79-103S150.69 103.6 117.68 170c-30 60.41-46.57 140.14-46.57 224.48S87.42 558.57 117.45 619c27 54.4 63.55 88.76 102.55 99.42V903h-60.28a27 27 0 1 0 0 54h663.74a27 27 0 1 0 0-54H766V711.09c104-4.97 186.75-90.92 186.75-195.87zM730 211.12a115.38 115.38 0 0 1 106.16 160.37l-8.09 19 16.29 12.76a141.37 141.37 0 0 1 54.54 111.92c0 78.36-63.75 142.11-142.11 142.11a141.22 141.22 0 0 1-44.3-7 164.48 164.48 0 0 0-62.83-206.06 127.29 127.29 0 0 0 0.76-13.87 125.93 125.93 0 0 0-34.47-86.65v-0.28A115.39 115.39 0 0 1 730 211.12zM451.24 453.9l0.4-24.74a72.39 72.39 0 1 1 141.82 21.7l-6.6 22.43 21.25 9.71a110.54 110.54 0 0 1-80.24 205.61l-12.17-4-10.77 6.91a128.24 128.24 0 1 1-108-230.25 26.81 26.81 0 0 0 11-2.94 128.17 128.17 0 0 1 18.68-2.73zM166 594.95c-26.39-53.09-40.92-124.28-40.92-200.45S139.65 247.14 166 194.05c23.07-46.41 52.75-73 81.43-73s58.37 26.62 81.43 73c26.39 53.09 40.92 124.28 40.92 200.45 0 6.42-0.11 12.85-0.32 19.26A182.24 182.24 0 0 0 271.39 662a53.51 53.51 0 0 1-23.92 6c-28.68 0-58.36-26.65-81.47-73.05z m108 123.38a107.61 107.61 0 0 0 27.62-11.42 181.51 181.51 0 0 0 133.87 58.85 179.31 179.31 0 0 0 47.51-6.32V903H274zM537 903V748.48c0-0.77 0.19-1.54 0.13-2.29a166.77 166.77 0 0 0 24.87 1.86 163.88 163.88 0 0 0 119.48-51.64 207.69 207.69 0 0 0 30.52 9.86V903z" p-id="59811"></path></svg>' },
          { name: '松树', svgCode: '<svg t="1756143790218" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="61039" width="100%" height="100%"  preserveAspectRatio="xMidYMid meet"><path d="M250.4 914.4c-8.3 0-15.9-3.4-21.4-8.9s-8.9-13-8.9-21.4v-92.9c0-16.7 13.5-30.2 30.2-30.2 8.3 0 15.9 3.4 21.4 8.9s8.9 13 8.9 21.4v92.9c0.1 16.6-13.5 30.2-30.2 30.2z" fill="#90EB7A" p-id="61040"></path><path d="M695.3 914.4c-8.3 0-15.9-3.4-21.4-8.9s-8.9-13-8.9-21.4v-92.9c0-16.7 13.5-30.2 30.2-30.2 8.3 0 15.9 3.4 21.4 8.9s8.9 13 8.9 21.4v92.9c0 16.6-13.5 30.2-30.2 30.2z" fill="#008486" p-id="61041"></path><path d="M356.2 914.4c-8.3 0-15.9-3.4-21.4-8.9s-8.9-13-8.9-21.4v-58.6c0-16.7 13.5-30.2 30.2-30.2 8.3 0 15.9 3.4 21.4 8.9s8.9 13 8.9 21.4v58.7c0 16.5-13.5 30.1-30.2 30.1z" fill="#00AD95" p-id="61042"></path><path d="M454.8 635h111.5v232.1H454.8z" fill="#B05C25" p-id="61043"></path><path d="M932 897.3c0 8.3-3.4 15.9-8.9 21.4s-13 8.9-21.4 8.9H122.2c-16.7 0-30.2-13.5-30.2-30.2 0-8.3 3.4-15.9 8.9-21.4s13-8.9 21.4-8.9h779.5c16.7 0 30.2 13.5 30.2 30.2z" fill="#00D16C" p-id="61044"></path><path d="M510.6 635h55.8v232.1h-55.8z" fill="#8E4A1F" p-id="61045"></path><path d="M932 897.3c0 8.3-3.4 15.9-8.9 21.4s-13 8.9-21.4 8.9H510.6v-60.5h391.2c16.7 0 30.2 13.5 30.2 30.2z" fill="#00AD95" p-id="61046"></path><path d="M798.1 723.5L771 712c-12.3-5.1-26.3-5.1-38.7 0l-81.9 34.2c-12.3 5.2-26.3 5.2-38.7 0L529.9 712c-6.2-2.6-12.8-3.9-19.3-3.9s-13.2 1.3-19.3 3.9l-81.9 34.2c-12.3 5.2-26.3 5.2-38.7 0L288.9 712c-12.3-5.1-26.3-5.1-38.7 0l-27.1 11.4c-19.8 8.3-37.7-15.2-24.4-32l295.6-376c4.1-5.3 10.2-8 16.3-8 6.1 0 12.2 2.6 16.3 8l295.6 376c13.3 16.9-4.5 40.3-24.4 32.1z" fill="#00AD95" p-id="61047"></path><path d="M714.3 509l-19.3-8.1c-8.7-3.7-18.6-3.7-27.4 0l-58 24.3c-8.7 3.7-18.6 3.7-27.4 0l-58-24.3c-4.4-1.9-9-2.7-13.7-2.7s-9.3 0.9-13.7 2.7l-58 24.3c-8.7 3.7-18.6 3.7-27.4 0l-58-24.3c-8.7-3.7-18.6-3.7-27.4 0l-19.3 8.1c-14.1 5.9-26.7-10.8-17.3-22.8L499 219.8c2.9-3.7 7.3-5.7 11.6-5.7s8.6 1.9 11.6 5.7l209.4 266.4c9.4 12-3.2 28.5-17.3 22.8z" fill="#00D16C" p-id="61048"></path><path d="M663.5 317.7l-14.5-6.1c-6.5-2.7-14-2.7-20.6 0l-43.5 18.2c-6.5 2.7-14 2.7-20.6 0l-43.5-18.1c-3.3-1.4-6.8-2.1-10.2-2.1s-7 0.7-10.2 2.1l-43.5 18.2c-6.5 2.7-14 2.7-20.6 0l-43.5-18.2c-6.5-2.7-14-2.7-20.6 0l-14.5 6.1c-10.6 4.4-20.1-8.1-13-17.1l157.2-200c2.2-2.8 5.4-4.3 8.7-4.3 3.3 0 6.4 1.4 8.7 4.3l157.2 200c7.1 8.9-2.4 21.4-13 17z" fill="#90EB7A" p-id="61049"></path><path d="M798.1 723.5L771 712c-12.3-5.1-26.3-5.1-38.7 0l-81.9 34.2c-12.3 5.2-26.3 5.2-38.7 0L529.9 712c-6.2-2.6-12.8-3.9-19.3-3.9V307.4c6.1 0 12.2 2.6 16.3 8l295.6 376c13.3 16.9-4.5 40.3-24.4 32.1z" fill="#008486" p-id="61050"></path><path d="M714.3 509l-19.3-8.1c-8.7-3.7-18.6-3.7-27.4 0l-58 24.3c-8.7 3.7-18.6 3.7-27.4 0l-58-24.3c-4.4-1.9-9-2.7-13.7-2.7v-284c4.4 0 8.6 1.9 11.6 5.7l209.4 266.4c9.5 11.9-3.1 28.4-17.2 22.7z" fill="#00AD95" p-id="61051"></path><path d="M663.5 317.7l-14.5-6.1c-6.5-2.7-14-2.7-20.6 0l-43.5 18.2c-6.5 2.7-14 2.7-20.6 0l-43.5-18.1c-3.3-1.4-6.8-2.1-10.2-2.1V96.4c3.3 0 6.4 1.4 8.7 4.3l157.2 200c7.1 8.9-2.4 21.4-13 17z" fill="#00D16C" p-id="61052"></path><path d="M402.3 237.1c-1.3-26.9 24.4-62.9 24.4-62.9l6.4 62.9h-30.8z" fill="#90EB7A" p-id="61053"></path><path d="M399.8 252.1c-12.2-24.1-3.6-67.4-3.6-67.4l31.6 54.7-28 12.7z" fill="#90EB7A" p-id="61054"></path><path d="M634.3 413.6l42.2-47.1s-0.3 44.3-17.2 65.2l-25-18.1z" fill="#00AD95" p-id="61055"></path><path d="M643.6 429c21.7-16 65.8-14.6 65.8-14.6l-48.7 40.2-17.1-25.6z" fill="#00AD95" p-id="61056"></path><path d="M637.4 418.6l57.8-25.6s-18.5 40.1-42.5 52.3l-15.3-26.7z" fill="#00AD95" p-id="61057"></path><path d="M337.1 476.9c-12-24.1-3.1-67.4-3.1-67.4l31.2 54.9-28.1 12.5z" fill="#00D16C" p-id="61058"></path><path d="M340.9 491.6c-20.9-17.1-30.4-60.2-30.4-60.2l51 37.3-20.6 22.9z" fill="#00D16C" p-id="61059"></path><path d="M382.8 385.7c-9.6-19.2-2.4-53.7-2.4-53.7l24.9 43.8-22.5 9.9z" fill="#00D16C" p-id="61060"></path><path d="M385.7 397.3c-16.7-13.6-24.3-48-24.3-48l40.7 29.8-16.4 18.2z" fill="#00D16C" p-id="61061"></path><path d="M267 632.6c-9.8-25.1 3.1-67.4 3.1-67.4l26.3 57.4-29.4 10z" fill="#00AD95" p-id="61062"></path><path d="M269.4 647.5c-19.3-18.9-24.9-62.7-24.9-62.7l47.4 41.6-22.5 21.1z" fill="#00AD95" p-id="61063"></path><path d="M259.4 652.9c-23.8-12.9-41.3-53.2-41.3-53.2l57.2 26.9-15.9 26.3z" fill="#00AD95" p-id="61064"></path><path d="M270.9 662.6c-26.9-2-59.6-31.6-59.6-31.6l63.1 1-3.5 30.6z" fill="#00AD95" p-id="61065"></path><path d="M738.3 643l6-62.9s25.9 35.7 24.9 62.7l-30.9 0.2z" fill="#008486" p-id="61066"></path><path d="M743.6 645.2l31.2-54.8s9 43.3-3.1 67.4l-28.1-12.6z" fill="#008486" p-id="61067"></path><path d="M759.4 639.9l45.2-44.1s-3.4 43.9-21.7 63.8l-23.5-19.7z" fill="#008486" p-id="61068"></path><path d="M761.9 644.8l59.4-21.6s-21.1 38.7-46 49.4l-13.4-27.8z" fill="#008486" p-id="61069"></path><path d="M636.6 286.4l4.3-44.9s18.5 25.5 17.8 44.7l-22.1 0.2z" fill="#00D16C" p-id="61070"></path><path d="M640.4 287.9l22.2-39.2s6.4 30.8-2.2 48.1l-20-8.9z" fill="#00D16C" p-id="61071"></path><path d="M651.6 284.1l32.4-31.5s-2.4 31.4-15.5 45.6l-16.9-14.1z" fill="#00D16C" p-id="61072"></path><path d="M653.5 287.6l42.4-15.4s-15.2 27.7-32.9 35.2l-9.5-19.8z" fill="#00D16C" p-id="61073"></path></svg>' },
          { name: '柳树', svgCode: '<svg t="1756144002788" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="63103" width="100%" height="100%"  preserveAspectRatio="xMidYMid meet"><path d="M516.2 261.2c-6.1 0-11.6-4.1-13.4-10.2-0.2-0.6-10.2-34.6-43.8-52.3-28.5-15.1-66.1-14.9-111.7 0.5-7.3 2.4-15.2-1.5-17.6-8.7-2.5-7.2 1.5-15.2 8.7-17.6 53.3-18 98.4-17.5 134 1.5 44.3 23.7 56.6 67.4 57.1 69.3 2 7.4-2.4 15-9.8 17-1.1 0.3-2.3 0.5-3.5 0.5zM186.4 578.6c-7.7 0-13.9-6.2-13.9-13.9 0-1.9 0.2-47.2 14.2-100.5 8.3-31.6 19.9-59.6 34.4-83 18.5-29.9 41.7-52.6 68.9-67.4 48.6-26.2 103.7-29.7 159-10.2 41.3 14.6 68.3 36.9 69.4 37.8 5.9 4.9 6.7 13.7 1.8 19.5-4.9 5.9-13.6 6.7-19.5 1.8-0.3-0.2-24.9-20.4-61.7-33.3-48.2-16.8-93.9-14-135.7 8.7-22.9 12.4-42.5 31.6-58.4 57.2-13 21-23.5 46.3-31.1 75.2-13.3 50-13.5 93.7-13.5 94.1 0 7.8-6.2 14-13.9 14z" fill="#B05C25" p-id="63104"></path><path d="M546.6 879H478l4.2-102.3 1-23.8 2.2-53 1.1-26.6 6.2-147.8v-0.2l0.4-9 0.4-7.9 1.6-36.1v-0.1l3.9-92.9 2.7-62.8 4-93.5c0.2-4.3 3.1-6.7 6.4-7.3H513.9c3.7 0.1 7.3 2.6 7.6 7.4l2.9 75.5 0.8 21.4 3.8 96.1 1.9 49.2 0.3 6.4L533 516v0.2l0.1 1.8v0.3l5.1 129.1v0.1l2.3 60.1v0.2l6.1 171.2z" fill="#B05C25" p-id="63105"></path><path d="M868.1 462.3c-0.6 3.1-2.2 6.2-4.8 8.4-2.4 1.9-5.3 3-8.1 3.1-4.2 0.2-8.5-1.5-11.4-5.1 0 0-1-1.2-3-3.2-1.2-1.3-2.7-2.9-4.5-4.7-0.7-0.7-1.6-1.6-2.5-2.4-3.2-3-7.1-6.6-11.6-10.2-0.5-0.4-0.8-0.6-1.3-1-3.4-2.8-7.2-5.5-11.3-8.3-0.9-0.6-1.8-1.2-2.8-1.8-0.9-0.6-1.8-1.1-2.7-1.7-0.9-0.6-1.8-1.1-2.8-1.7-0.9-0.6-1.8-1.1-2.9-1.7-3.6-2.1-7.3-4-10.9-5.7-0.6-0.3-1.1-0.6-1.7-0.7-5-2.3-10.1-4.2-15.1-5.9-3.5-1.1-6.9-2-10.4-2.9-0.4-0.1-0.7-0.2-1.1-0.3-1.7-0.4-3.3-0.7-5-1-5-0.8-10-1.4-15-1.6-3.7-0.1-7.4-0.1-11 0.2-3.1 0.2-6.3 0.6-9.3 1-0.3 0-0.6 0.1-0.9 0.2-4.1 0.6-7.9 1.5-11.8 2.4-0.6 0.2-1.2 0.3-1.8 0.5-3.2 0.8-6.5 1.8-9.7 2.8-1.3 0.5-2.6 0.8-3.9 1.3-4.8 1.7-9.5 3.6-14.1 5.6-5.4 2.4-10.5 5.1-15.5 7.9-1.8 1-3.4 2-5.1 3-1.8 1.1-3.8 2.3-5.6 3.5-0.3 0.2-0.6 0.4-0.7 0.6-3 2-6 4.1-9 6.3-12.9 9.5-24.9 20.3-36 31.8-3 3.1-6 6.3-8.9 9.4-10.6 11.7-20.3 23.9-29.3 35.8-2.8 3.7-5.5 7.4-8 11-6.8 9.4-13.1 18.6-18.9 27-1.5 2.2-3 4.3-4.4 6.4-1.5 2.1-2.9 4.2-4.2 6.1-2.7 3.9-7 5.9-11.4 5.9-2.4 0-4.8-0.6-7-1.9v-26.1c1.4-2 2.8-4.1 4.2-6.1 5.2-7.5 10.7-15.4 16.5-23.7 9.1-12.7 19.2-26.1 30.3-39.5 5-5.9 10.2-11.8 15.5-17.6 4.2-4.6 8.8-9.2 13.4-13.7 6.2-6 12.5-11.6 18.8-16.9 0.6-0.5 1.2-0.9 1.8-1.5 2.4-2 4.9-3.9 7.3-5.8 2.5-1.8 4.9-3.7 7.4-5.5 0.5-0.4 1-0.7 1.5-1 5.3-3.7 10.5-7 15.8-10.2 4.2-2.4 8.2-4.7 12.4-6.7 2.2-1.1 4.5-2.2 6.7-3.2 0.6-0.3 1.3-0.6 2-0.9 3.2-1.4 6.4-2.8 9.6-4 2.6-1 5.1-1.9 7.7-2.8 4.2-1.4 8.3-2.7 12.5-3.7 1.2-0.3 2.5-0.6 3.7-0.9 4.6-1.1 9.3-2 14-2.8 2.5-0.4 5-0.7 7.5-1 6.1-0.6 12.3-0.8 18.5-0.6h0.1c2.6 0.1 5.2 0.3 7.8 0.5l5.7 0.6c4.8 0.6 9.7 1.5 14.5 2.7 1.4 0.4 2.9 0.7 4.2 1.1 3.7 1 7.4 2.1 11.1 3.4 1.6 0.6 3.2 1.1 4.8 1.8 4.8 1.8 9.6 4 14.4 6.4l3 1.5 7.8 4.2c1.9 1.1 3.9 2.3 5.8 3.5 1.3 0.8 2.6 1.7 3.9 2.5 0.6 0.4 1 0.7 1.6 1 1.1 0.7 2.2 1.5 3.2 2.2 2.6 1.8 5.2 3.7 7.5 5.5 2.5 1.9 4.9 3.9 7.1 5.7 4 3.3 7.5 6.5 10.5 9.3 7.7 7.3 12 12.6 12.4 12.9 0.7 0.9 1.4 1.8 1.8 2.9 1.2 2.5 1.5 5.4 1.1 8.1z" fill="#8E4A1F" p-id="63106"></path><path d="M848.4 444.6c0.6 43.8 50.8 92.8 50.8 92.8 6.3-51.5-50.8-92.8-50.8-92.8zM880.9 436.1c-35.8 5.5-47.2-1-47.2-1 54-43.1 97-2.6 97-2.6-15.8-4.7-34.6 1.3-49.8 3.6zM845.4 407.4c-30.4 19.6-43.5 18.5-43.5 18.5 31.6-61.6 87.5-42.2 87.5-42.2-16.4 2.2-31 15.4-44 23.7zM809.4 376.7c-28.2 22.9-41.2 23.2-41.2 23.2 24.8-64.5 82.1-51.7 82.1-51.7-15.8 4.1-29 18.8-40.9 28.5zM751.5 371.1c-20.8 29.7-33.3 33.5-33.3 33.5 6.2-68.8 64.9-72.2 64.9-72.2-14.3 8.3-22.9 26.1-31.6 38.7zM689.8 377.3c-10.5 34.7-21.2 42.2-21.2 42.2-15.6-67.3 39.1-88.8 39.1-88.8-10.8 12.3-13.5 31.8-17.9 46.6zM838.4 525.8s-44.9-37.9-8.6-96.6c0 0 7.6 10.5 6.4 46.7-0.6 15.4-4.4 34.8 2.2 49.9z" fill="#008486" p-id="63107"></path><path d="M788.1 506.3s-35.6-46.7 12.6-96.2c0 0 5.1 11.9-4 47-3.8 14.9-11.6 33-8.6 49.2zM759.7 491.1s-46-36.5-11.5-96.4c0 0 7.9 10.3 7.8 46.6-0.1 15.4-3.2 34.9 3.7 49.8zM736.9 488.9s-55.9-18.1-44.5-86.2c0 0 11 6.9 23.7 40.8 5.1 14.5 8.9 33.9 20.8 45.4zM628.1 410.4c-0.3 36.3-8.3 46.5-8.3 46.5-34-60.1 12.4-96.3 12.4-96.3-7 14.9-4.1 34.3-4.1 49.8zM704.8 504.1s-58.7-1.5-67.2-70.1c0 0 12.5 3.5 34.2 32.5 9.3 12.4 18.5 29.9 33 37.6zM579.4 455.4c-0.3 36.3-8.3 46.5-8.3 46.5-34-60.1 12.4-96.3 12.4-96.3-7 14.8-4.1 34.3-4.1 49.8zM677.4 511.8s-53.5 24.2-91-33.8c0 0 12.7-2.3 45 14.3 13.6 7.2 29.5 19 46 19.5zM642.4 542.5s-47.9 34-95.7-15.8c0 0 12.1-4.7 46.8 5.5 14.8 4.4 32.7 12.8 48.9 10.3z" fill="#008486" p-id="63108"></path><path d="M160.7 737.5c-1.8 0-3.6-0.4-5.4-1.1-7-3-10.4-11.1-7.5-18.1 39.1-93.7 95.5-155.7 167.8-184.1 29.7-11.7 78.2-23.7 140.4-13.7 37.1 5.9 61.7 16.9 62.7 17.4 7 3.1 10.1 11.4 6.9 18.3-3.1 6.9-11.4 10.1-18.3 6.9-0.2-0.1-22.9-10.2-56.7-15.4-30.8-4.8-77.4-6.6-125.2 12.4-64.9 25.8-116 82.6-152.1 169-2 5.3-7.2 8.4-12.6 8.4z" fill="#B05C25" p-id="63109"></path><path d="M180.4 807.6s9.1-69.6-17.6-104.3c0 0-19.2 67.9 17.6 104.3zM90.7 744.9s8.6-58.6 77.9-58c0 0-5 12.1-36.5 30-13.4 7.6-31.9 14.5-41.4 28zM92.9 681s31.9-49.9 94.8-21.1c0 0-9.5 9-45.5 12.5-15.4 1.5-35.1 0.3-49.3 8.6zM120.4 638.1s36-46.5 96.3-12.6c0 0-10.3 8.1-46.5 8.4-15.4 0.1-34.9-2.8-49.8 4.2zM147.1 578.2s48.1-33.7 95.6 16.4c0 0-12.1 4.7-46.9-5.7-14.7-4.6-32.6-13.1-48.7-10.7zM193.6 532.1s56.3-17 85.7 45.5c0 0-13 0.6-42.8-20-12.5-8.9-26.7-22.6-42.9-25.5zM240.1 506.8s56.3-17 85.7 45.5c0 0-13 0.6-42.8-20-12.5-8.9-26.7-22.6-42.9-25.5zM294.6 479.7s58.2-8.4 78 57.7c0 0-12.9-1.3-39.3-26.2-11.2-10.7-23.2-26.3-38.7-31.5zM363.7 464.1s58.8 1.2 67.4 69.8c0 0-12.6-3.4-34.5-32.3-9.1-12.3-18.5-29.7-32.9-37.5zM435 462.9s56.8 15.2 49.1 83.7c0 0-11.5-6.3-25.9-39.5-6-14.2-11-33.3-23.2-44.2zM191.9 720.4c-23.4-27.7-23.9-40.7-23.9-40.7 64.9 23.7 53.1 81.2 53.1 81.2-4.4-15.8-19.3-28.7-29.2-40.5z" fill="#008486" p-id="63110"></path><path d="M211.1 681.3c-28.8-22-32.2-34.5-32.2-34.5 68.5 9.1 69.5 67.7 69.5 67.7-7.7-14.6-25-23.9-37.3-33.2zM243.1 659.6c-22.5-28.4-22.7-41.4-22.7-41.4 64.2 25.6 50.7 82.8 50.7 82.8-3.8-16-18.3-29.3-28-41.4z" fill="#008486" p-id="63111"></path><path d="M265.7 628c-11.2-34.5-6.7-46.7-6.7-46.7 51.1 46.5 18.4 95.3 18.4 95.3 2-16.3-6.9-33.9-11.7-48.6zM304.4 609.1c-11.2-34.5-6.7-46.7-6.7-46.7 51.1 46.5 18.4 95.3 18.4 95.3 2.1-16.4-6.9-33.9-11.7-48.6zM349.6 583.6c1.6-36.2 10-46.1 10-46.1 31.7 61.4-16 95.7-16 95.7 7.6-14.6 5.4-34.2 6-49.6zM392.7 577.6c4.5-35.9 13.7-45.2 13.7-45.2 26.5 63.7-23.7 94.1-23.7 94.1 8.7-13.9 8.1-33.7 10-48.9zM447.3 579.5c3-36.1 11.6-45.7 11.6-45.7 29.4 62.5-19.5 95.1-19.5 95.1 8.3-14.3 6.7-34 7.9-49.4z" fill="#008486" p-id="63112"></path><path d="M264.9 691.2c-0.6 0-1.3 0-1.9-0.1-7.6-1-12.8-8-11.8-15.6 1-7.4 25.9-181.8 88-249.9 27.2-29.7 66.7-45.8 114.3-46.3 35.1-0.4 62.3 7.9 63.4 8.1 7.3 2.2 11.5 10 9.2 17.3s-10 11.5-17.3 9.2c-0.6-0.2-25-7.4-55.8-6.9-39.9 0.6-71.3 13.1-93.3 37.2-56.4 61.8-80.8 233.4-81 235-1 7-7 12-13.8 12z" fill="#B05C25" p-id="63113"></path><path d="M274.2 659.6c-22.9 34.9-9.5 100.6-9.5 100.6 32.5-37.3 9.5-100.6 9.5-100.6zM299.6 652.8c-24.9-24-26.8-36.3-26.8-36.3 64 16 58.6 71.9 58.6 71.9-5.8-14.6-21.2-25.4-31.8-35.6zM220.6 709.9s-5.8-55.9 58.1-72.2c0 0-1.8 12.4-26.5 36.4-10.5 10.3-26.1 21.2-31.6 35.8zM308.9 614c-24.4-24.6-26-37-26-37 63.7 17.5 56.9 73.2 56.9 73.2-5.3-14.7-20.4-25.9-30.9-36.2zM212 656.7s3-56.1 68.6-62.3c0 0-3.7 11.9-31.9 31.9-11.9 8.5-28.9 16.8-36.7 30.4zM317.4 570.5C296 543.2 296 530.8 296 530.8c61.2 24.7 48 79.3 48 79.3-3.7-15.3-17.4-28.2-26.6-39.6zM217.3 599.8s12-54.9 77.8-50.4c0 0-5.5 11.2-36.6 26.3-13.2 6.4-31.3 11.9-41.2 24.1zM327.4 529.2c-18.3-29.5-17-41.8-17-41.8 58.1 31.2 39.2 84.1 39.2 84.1-2-15.6-14.3-29.9-22.2-42.3zM225.4 553.9s15.4-54 80.8-45.4c0 0-6.2 10.8-38.2 23.9-13.6 5.6-32 9.9-42.6 21.5zM350.2 479.7c-13.6-31.9-10.4-43.9-10.4-43.9 52.7 39.7 25.8 89.1 25.8 89.1 0.5-15.8-9.6-31.7-15.4-45.2zM242.2 473.7s34.9-44 92.1-11c0 0-9.9 7.6-44.4 7.5-14.9 0-33.5-3.1-47.7 3.5zM382.2 444.3c-2.3-34.6 4.6-44.9 4.6-44.9 36.7 54.9-5 92.6-5 92.6 5.7-14.6 1.4-33 0.4-47.7zM281 419.5s39.1-40.4 92.7-2c0 0-10.6 6.7-45 3.1-14.7-1.4-32.9-6.3-47.7-1.1z" fill="#00AD95" p-id="63114"></path><path d="M415.4 432.3c11-32.9 21.3-39.8 21.3-39.8 13.1 64.7-39.7 83.8-39.7 83.8 10.8-11.4 13.8-30.1 18.4-44zM333.7 364.9s51.5-22.5 86.6 33.3c0 0-12.3 2.1-42.8-14.1-13.1-6.9-28.2-18.3-43.8-19.2zM459.2 426.3c20.9-27.6 32.9-30.9 32.9-30.9-8.3 65.5-64.5 66.6-64.5 66.6 13.9-7.4 22.8-24 31.6-35.7zM403.2 340.3s56-4.9 71.3 59.2c0 0-12.3-1.9-36-27.1-10.2-10.7-20.8-26.3-35.3-32.1z" fill="#00AD95" p-id="63115"></path><path d="M821.4 694.8c-1.8 1.2-4 1.9-6.4 2.2h-1.2c-4.9 0-9.3-2.6-11.8-6.6-1.1-1.8-1.8-3.9-2-6.1 0-0.2-0.3-2.6-0.7-7-0.1-1.1-0.3-2.4-0.5-3.8v-0.1c-1.8-13.2-5.5-37.5-12.7-67.3-1.4-5.9-3-12-4.7-18.2-1.9-7.2-4.2-14.6-6.5-22.2-1.7-5.5-3.5-11-5.5-16.6-2.9-8.3-6-16.7-9.4-25.2-2.3-5.7-4.7-11.4-7.2-17.1-3-6.7-6.1-13.4-9.4-20-3-6-6.2-12-9.5-17.9-2.1-3.9-4.4-7.7-6.7-11.5-3.8-6.2-7.9-12-12.5-17.4-4.3-5.1-9-9.9-14-14.2-1.9-1.7-3.9-3.3-5.9-4.8-1.3-1-2.6-1.9-3.9-3-4.4-3.2-9.1-6.2-14.1-8.9-3.3-1.8-6.8-3.5-10.4-5.1-0.7-0.4-1.4-0.6-2.1-0.9-1.9-0.8-4-1.7-6-2.4-6.9-2.6-14.1-4.7-21.7-6.5-2.9-0.6-5.8-1.3-8.8-1.8-3.2-0.6-6.5-1.1-9.8-1.6-2-0.3-4.2-0.5-6.3-0.7-3.9-0.4-7.9-0.7-11.9-0.9-6-0.3-11.9-0.4-17.6-0.3-5.4 0.1-10.5 0.4-15.4 0.6-16.2 1.2-29.7 3.5-38.6 5.4-6.9 1.5-10.9 2.6-11 2.6-1.6 0.5-3.1 0.6-4.6 0.6v-28c3-0.7 7.9-1.9 14.6-3.2 3.1-0.6 6.7-1.3 10.6-1.8 5.5-0.8 11.5-1.7 18-2.3 9.2-0.9 19.4-1.6 30.3-1.6 5 0 10.2 0.1 15.3 0.4 1.1 0.1 2.2 0.1 3.3 0.2 8 0.6 15.9 1.4 23.5 2.7 0.8 0.1 1.7 0.3 2.5 0.5 3 0.6 6 1.1 9 1.8 4.3 0.9 8.5 1.9 12.7 3.1 5.3 1.5 10.3 3.1 15.2 5 0.5 0.2 0.9 0.4 1.4 0.6 0.6 0.2 1.1 0.5 1.7 0.6 6 2.4 11.8 5 17.4 7.9 0.5 0.3 0.9 0.5 1.5 0.7 3.6 1.9 7.1 4 10.4 6.1 0.6 0.4 1.1 0.6 1.6 1 5.9 3.9 11.5 8.1 16.9 12.7l0.1 0.1c3.5 3 6.9 6.3 10.3 9.6 3 3 5.7 6.2 8.4 9.4 0.2 0.3 0.5 0.6 0.6 0.8 3 3.6 5.7 7.3 8.3 11.2 1.7 2.4 3.2 4.9 4.8 7.4 1.7 2.8 3.3 5.5 4.9 8.3 4.2 7.2 8 14.4 11.7 21.6 2.1 4.2 4.2 8.4 6.2 12.7 4.3 9.2 8.3 18.5 12 27.6 2.1 5.3 4.1 10.4 6 15.5 3.8 10.3 7.2 20.3 10.2 30 1.8 5.5 3.3 10.9 4.8 16.2 2.8 9.9 5.2 19.2 7.2 27.7 0.3 1.1 0.6 2.2 0.7 3.3 2 8.7 3.8 16.8 5.3 24.3 6 30.6 7.8 50.6 7.9 51.6 0.2 5.5-2.3 10.3-6.5 13z" fill="#8E4A1F" p-id="63116"></path><path d="M820.3 722s7.9-66.5-17.8-99.5c0 0.1-17.8 65 17.8 99.5zM747.8 655.9s-10.1-55.2 52.4-76.5c0 0-0.7 12.4-23.7 38.4-9.8 11.1-24.3 23.1-28.7 38.1zM825.5 635.2c-26.7-21.9-29.5-34.1-29.5-34.1 65 11 63.9 67.2 63.9 67.2-6.7-14.2-23-23.7-34.4-33.1zM736.1 618.6s-11.4-55 50.6-77.7c0 0-0.5 12.5-22.7 39-9.6 11.3-23.8 23.7-27.9 38.7zM824.9 587.1c-29.8-17.6-34.5-29.1-34.5-29.1 66 0.7 73.6 56.4 73.6 56.4-8.8-12.9-26.3-19.7-39.1-27.3zM728.7 579s-17.6-53.3 41.3-83.1c0 0 1 12.4-18.1 41.4-8.1 12.2-20.9 26.2-23.2 41.7zM811.1 537.6c-32.2-12.5-38.7-23.2-38.7-23.2 65.2-9.9 81.8 43.8 81.8 43.8-10.9-11.4-29.4-15.2-43.1-20.6zM720 540.9s-23.4-51.1 32-87c0 0 2.3 12.2-13.5 43.1-6.8 13.1-17.9 28.2-18.5 43.9zM797.9 495.2c-33-10.4-40.1-20.7-40.1-20.7 64.5-14 84.4 38.5 84.4 38.5-11.6-10.5-30.2-13.3-44.3-17.8zM700 495.8s-30.9-46.9 18.3-90.9c0 0 4.2 11.7-6.7 44.6-4.7 14-13.4 30.7-11.6 46.3zM771.1 435c-34.5 3-44.9-3.7-44.9-3.7 54.1-37.6 92.7 3.3 92.7 3.3-14.8-5.4-33.1-0.8-47.8 0.4zM681.2 464.4s-44.6-34.1-12.7-91.8c0 0 7.8 9.7 8.3 44.3 0.2 14.7-2.4 33.4 4.4 47.5zM728.2 388.8c-34 6.3-45.1 0.6-45.1 0.6 50.3-42.7 92.6-5.6 92.6-5.6-15.3-3.9-33 2.5-47.5 5z" fill="#00AD95" p-id="63117"></path><path d="M664.7 450s-54.2-14.6-46.6-80.2c0 0 10.9 6 24.6 37.9 5.8 13.6 10.4 31.9 22 42.3zM676.5 356.5c-29 18.8-41.5 17.6-41.5 17.6 30.3-58.6 83.5-40.4 83.5-40.4-15.4 2.3-29.5 14.9-42 22.8zM633 438.5s-56.1 3.5-69.8-61.1c0 0 12.3 2.2 35.4 28 9.8 11 20 26.9 34.4 33.1zM614.8 350c-21.5 27.1-33.6 30-33.6 30 10-65.2 66.2-64.9 66.2-64.9-14.1 6.9-23.4 23.3-32.6 34.9zM563.9 348.4c-16.2 30.6-27.5 35.8-27.5 35.8-2.3-65.9 52.9-76.1 52.9-76.1-12.4 9.3-18.5 27.3-25.4 40.3z" fill="#00AD95" p-id="63118"></path><path d="M264.9 225.9s68.6-14.3 92.8-50.8c-0.1 0-70.4 4-92.8 50.8zM294.8 120.6s58.1-11.1 80.4 54.5c0 0-13.1-0.7-40.4-24.6-11.6-10.2-24.2-25.4-40-29.9zM355.9 101.7s57.6 13.8 51 82.7c0 0-11.6-6.1-26.7-39-6.5-14-11.8-33.1-24.3-43.7zM407.9 92.7s55.2 20.1 41.4 87.8c0 0-10.8-7.3-22.2-41.7-4.8-14.6-8-34-19.2-46.1zM473.1 115.7s47.7 34.5 15.9 95.7c0 0-8.4-9.9-10-46.2-0.6-15.3 1.6-34.9-5.9-49.5zM528.9 176.5s34.6 47.6-14.9 95.9c0 0-4.9-12.1 4.9-47 4.4-14.8 12.6-32.7 10-48.9z" fill="#90EB7A" p-id="63119"></path><path d="M351.1 208c18.5-31.1 30.6-35.9 30.6-35.9-1.1 69.1-59.3 76.9-59.3 76.9 13.6-9.4 20.9-27.7 28.7-41zM394.4 213.3c11.3-34.5 22-41.8 22-41.8 14 67.6-41.2 87.9-41.2 87.9 11.2-11.9 14.4-31.4 19.2-46.1zM437.3 222c19.4-30.6 31.6-35 31.6-35-3.1 69-61.5 75-61.5 75 13.9-8.8 21.7-27 29.9-40zM469.9 245.6c28.9-21.8 41.9-21.7 41.9-21.7-27.2 63.6-84 48.7-84 48.7 16.1-3.5 29.8-17.7 42.1-27z" fill="#90EB7A" p-id="63120"></path><path d="M836.1 478.2c-1.1 0.9-2.3 1.7-3.6 2.3-1.4 0.6-3 1-4.6 1.1h-0.8c-4.6 0-8.8-2.3-11.4-5.9-1.2-1.7-2-3.6-2.3-5.7-0.1-0.5-0.1-0.9-0.2-1.4 0-0.5-0.8-11.9-3.6-29.6-0.4-2.1-0.7-4.3-1.1-6.7-0.1-0.7-0.3-1.6-0.4-2.3-0.3-1.4-0.6-2.9-0.8-4.3 0-0.1 0-0.2-0.1-0.3-0.4-2.1-0.8-4.2-1.3-6.6-0.8-4.2-1.8-8.4-2.8-12.8-0.3-1.1-0.5-2.1-0.7-3.2-1.4-5.5-2.9-11.3-4.5-17.1l-0.9-3.3c-1.7-5.7-3.5-11.5-5.5-17.4-0.2-0.5-0.3-0.8-0.5-1.2-3.3-9.4-7.1-18.8-11.5-28.2-0.1-0.2-0.2-0.3-0.2-0.5-0.3-0.6-0.6-1.3-0.9-1.9-2.2-4.6-4.6-9.2-7.1-13.8-4-7.2-8.3-14.2-13.1-20.9-3.8-5.4-7.9-10.4-12.2-15.2-6.9-7.7-14.5-14.7-22.9-20.7-4.7-3.4-9.7-6.5-14.9-9.1-5.1-2.7-10.4-5-16.1-6.9-3.1-1.1-6.2-2-9.2-2.9-5.6-1.6-11.2-2.8-16.6-3.6-9.6-1.5-19.1-1.9-28.4-1.4-5.5 0.4-10.8 1.1-16.1 2.2-9.1 1.8-18.1 4.8-26.9 8.9-4.4 2-8.9 4.4-13.3 7.1-4.1 2.5-8.1 5.2-12.1 8.1-3.2 2.4-6.3 4.8-9.1 7.3-4.2 3.7-8.1 7.4-11.5 11-14.5 15.1-22 28.2-22.1 28.3-0.5 0.8-1 1.7-1.7 2.4-3.1 3.5-7.9 5.2-12.5 4.5v-35.2c3-3.9 6.6-8.4 10.8-13.1 7.4-8.3 16.8-17.6 28.2-26.1 0.5-0.4 0.9-0.7 1.4-1.1 5.5-4.1 11.6-8.1 18.4-12 7.2-4.1 15.2-7.9 23.7-11 6.8-2.5 14-4.6 21.8-6.2 8.8-1.8 18-2.8 27.8-3 6.6-0.1 13.3 0.3 20.3 1.1 10.6 1.3 21.8 3.7 33.4 7.5 0.9 0.3 1.8 0.6 2.9 0.9 5.7 1.9 11.4 4.2 16.8 6.9 8.7 4.2 17 9.4 24.9 15.4 5 3.8 9.9 8 14.6 12.6 7.3 7 14.2 14.9 20.7 23.7 0.4 0.5 0.7 0.9 1.1 1.5 2.5 3.4 4.9 6.9 7.3 10.6 5.9 9.1 11.4 18.8 16.4 29.4a355 355 0 0 1 6.9 15.3c2 5 4.1 10.1 6 15.3 1.3 3.4 2.5 6.9 3.7 10.5 0.6 1.8 1.1 3.5 1.7 5.3 0.5 1.4 0.9 2.8 1.3 4.2 1.3 4.2 2.5 8.5 3.6 12.6l2.7 10.2c1.8 7.4 3.4 14.5 4.7 21.2 0.1 0.6 0.3 1.4 0.4 2 0.5 2.2 0.8 4.4 1.2 6.6 0.6 3 1 5.9 1.5 8.7 0.1 0.3 0.1 0.6 0.2 0.8 0.2 1.2 0.4 2.5 0.6 3.7 2.3 15 3.2 25.6 3.4 29.1 0.1 0.6 0.1 1.1 0.1 1.3 0 4.2-1.9 8.2-5 11z" fill="#8E4A1F" p-id="63121"></path><path d="M815.4 539.7s29.2-63.7 14-104.9c-0.1 0.1-38.4 59.2-14 104.9zM778.4 477.4s-16-56.5 47-84.9c0 0 0.5 13-20.8 42.4-9.2 12.3-23 26.4-26.2 42.5zM857.3 448.1c-30-20.2-34.1-32.6-34.1-32.6 68.8 5.1 73.3 63.7 73.3 63.7-8.5-14.2-26.4-22.5-39.2-31.1zM762.6 439.7s-17.3-56.2 45.1-85.9c0 0 0.7 13-19.9 42.9-8.8 12.5-22.5 26.8-25.2 43zM852 398c-32.8-15.3-38.8-26.9-38.8-26.9 68.8-5.7 82.3 51.5 82.3 51.5-10.5-12.6-29.6-18-43.5-24.6zM750.9 399s-23.7-53.9 34.8-90.6c0 0 2.2 12.8-14.8 44.9-7.2 13.6-19.1 29.4-20 45.7zM831.8 347.5C799 332.2 793 320.6 793 320.6c68.8-5.7 82.3 51.5 82.3 51.5-10.6-12.6-29.6-18.1-43.5-24.6zM738.1 360.2s-29.4-50.9 24.8-93.9c0 0 3.6 12.5-9.8 46.2-5.9 14.4-16 31.4-15 47.7zM816 299.7c-35.4-7.6-43.8-17.6-43.8-17.6 65.8-21 91.6 31.8 91.6 31.8-13-9.9-32.8-10.9-47.8-14.2z" fill="#00D16C" p-id="63122"></path><path d="M724.9 332.6s-44.6-38.3-7.8-96.7c0 0 7.6 10.6 6.1 46.8-0.7 15.3-4.6 34.7 1.7 49.9zM777.7 255.5c-36.1 1-46.7-6.7-46.7-6.7 58.9-35.9 96.6 9.2 96.6 9.2-15-6.5-34.5-2.8-49.9-2.5zM695.2 312.9s-49.9-31.1-22.3-94.4c0 0 9.1 9.3 13.1 45.4 1.6 15.3 0.7 35 9.2 49zM735.5 222.9c-34.8 10-46.9 5.1-46.9 5.1 48.1-49.4 95.9-15.1 95.9-15.1-16.2-2.5-34.1 5.8-49 10z" fill="#00D16C" p-id="63123"></path><path d="M676.6 299.5s-57.9-9.9-56.4-78.9c0 0 11.9 5.2 29.4 37 7.3 13.5 13.8 32.2 27 41.9zM679.8 200.9c-28.5 22.4-41.5 22.5-41.5 22.5 25.8-64 83-50.3 83-50.3-16 3.8-29.4 18.3-41.5 27.8z" fill="#00D16C" p-id="63124"></path><path d="M653.3 296.5s-58.1 9.1-78.7-56.7c0 0 12.9 1.1 39.6 25.7 11.2 10.4 23.4 26 39.1 31zM624.6 202c-19.8 30.3-32.1 34.6-32.1 34.6 4-68.9 62.5-74.2 62.5-74.2-13.8 8.7-21.9 26.7-30.4 39.6zM626.6 302.7s-54.1 23-90.2-35.9c0 0 12.8-2.1 44.7 15.3 13.4 7.5 29 19.5 45.5 20.6zM575.8 218.1c-11.8 34.2-22.7 41.4-22.7 41.4-12.8-67.8 42.7-87.2 42.7-87.2-11.5 11.7-14.9 31.2-20 45.8z" fill="#00D16C" p-id="63125"></path><path d="M191.7 523.3c-30.1 31.8-28.5 101.9-28.5 101.9 40.5-32.4 28.5-101.9 28.5-101.9zM213 518.5c-21.2-29.4-20.8-42.4-20.8-42.4 63 28.3 47 84.9 47 84.9-3.2-16.1-17.1-30.1-26.2-42.5zM121.1 562.7s4.3-58.7 73.3-63.7c0 0-4.1 12.4-34.1 32.6-12.9 8.8-30.8 17.1-39.2 31.1zM229.8 480.2c-20.6-29.8-19.9-42.9-19.9-42.9 62.4 29.7 45.1 85.9 45.1 85.9-2.7-16.1-16.4-30.4-25.2-43zM122.1 506.3s13.5-57.3 82.3-51.5c0 0-6 11.6-38.8 26.9-14 6.6-33 12-43.5 24.6zM246.7 436.9c-17-32.1-14.8-44.9-14.8-44.9 58.5 36.8 34.8 90.6 34.8 90.6-0.9-16.3-12.8-32.1-20-45.7zM142.3 455.6s13.5-57.3 82.3-51.5c0 0-6 11.6-38.8 26.9-13.9 6.6-32.9 12.1-43.5 24.6zM264.6 396.2c-13.4-33.7-9.8-46.2-9.8-46.2 54.1 42.9 24.8 93.9 24.8 93.9 0.9-16.4-9.2-33.3-15-47.7zM153.8 397.5s26-52.8 91.6-31.8c0 0-8.4 10-43.8 17.6-15 3.3-34.8 4.3-47.8 14.2z" fill="#00D16C" p-id="63126"></path><path d="M294.4 366.3c-1.5-36.2 6.1-46.8 6.1-46.8 36.9 58.4-7.8 96.7-7.8 96.7 6.3-15.2 2.5-34.5 1.7-49.9zM189.9 341.6s37.7-45.2 96.6-9.2c0 0-10.5 7.7-46.7 6.7-15.4-0.3-34.8-4-49.9 2.5zM331.6 347.5c4-36 13.1-45.4 13.1-45.4 27.6 63.3-22.3 94.4-22.3 94.4 8.5-13.9 7.6-33.7 9.2-49zM233.2 296.6s47.7-34.4 95.9 15.1c0 0-12.1 4.8-46.9-5.1-14.9-4.3-32.9-12.6-49-10z" fill="#00D16C" p-id="63127"></path><path d="M368.1 341.3c17.4-31.9 29.4-37 29.4-37 1.5 69-56.4 78.9-56.4 78.9 13-9.8 19.7-28.4 27-41.9zM296.4 256.8s57.2-13.8 83 50.3c0 0-13-0.1-41.5-22.5-12.3-9.6-25.7-24.1-41.5-27.8zM414.2 343.2c26.7-24.6 39.6-25.7 39.6-25.7-20.7 65.9-78.7 56.7-78.7 56.7 15.7-5 27.9-20.5 39.1-31zM372.4 244.3s58.6 5.3 62.5 74.2c0 0-12.4-4.2-32.1-34.6-8.4-12.9-16.5-31-30.4-39.6zM454.3 355.4c31.9-17.4 44.7-15.3 44.7-15.3-36 58.9-90.1 35.9-90.1 35.9 16.3-1.1 32-13.1 45.4-20.6zM438.2 247.3s55.5 19.3 42.7 87.2c0 0-10.9-7.1-22.7-41.4-5.2-14.6-8.7-34.1-20-45.8z" fill="#00D16C" p-id="63128"></path><path d="M546.6 879h-34.3V215.6h1.4c3.7 0.1 7.3 2.6 7.6 7.4l1.8 47 1.1 28.5 0.6 15.5 0.2 5.9 1.8 47.2 1.1 28.1 0.8 20.8 1.9 49.2 0.3 6.4 1.8 44.3v0.2l0.1 1.8v0.3l0.3 6.7 1.8 45.8 3 76.5v0.1l2.3 60.1v0.2l6.4 171.4z" fill="#8E4A1F" p-id="63129"></path><path d="M633.2 916.7c-8.3 0-15.9-3.4-21.4-8.9s-8.9-13-8.9-21.4v-69.9c0-16.7 13.5-30.2 30.2-30.2 8.3 0 15.9 3.4 21.4 8.9s8.9 13 8.9 21.4v69.9c0.1 16.6-13.5 30.2-30.2 30.2z" fill="#00AD95" p-id="63130"></path><path d="M770.4 901.1c-8.3 0-15.9-3.4-21.4-8.9s-8.9-13-8.9-21.4v-92.9c0-16.7 13.5-30.2 30.2-30.2 8.3 0 15.9 3.4 21.4 8.9s8.9 13 8.9 21.4v92.9c0 16.6-13.5 30.2-30.2 30.2z" fill="#008486" p-id="63131"></path><path d="M312.3 901.1c-8.3 0-15.9-3.4-21.4-8.9s-8.9-13-8.9-21.4v-58.6c0-16.7 13.5-30.2 30.2-30.2 8.3 0 15.9 3.4 21.4 8.9s8.9 13 8.9 21.4V871c0 16.5-13.5 30.1-30.2 30.1z" fill="#00AD95" p-id="63132"></path><path d="M933.3 901c0 8.3-3.4 15.9-8.9 21.4s-13 8.9-21.4 8.9H123.5c-16.7 0-30.2-13.5-30.2-30.2 0-8.3 3.4-15.9 8.9-21.4s13-8.9 21.4-8.9h779.5c16.7 0 30.2 13.5 30.2 30.2z" fill="#00D16C" p-id="63133"></path><path d="M933.3 901c0 8.3-3.4 15.9-8.9 21.4s-13 8.9-21.4 8.9H511.9v-60.5h391.2c16.7 0 30.2 13.5 30.2 30.2z" fill="#00AD95" p-id="63134"></path><path d="M777.5 449.4c0.8-4.9 2.2-10.2 4.4-15.6-3.8 0.5-7.4 1-10.9 1.2-2.7 0.2-5.2 0.4-7.6 0.5-0.4 1.3-0.7 2.7-0.9 4.1 0 0-0.4-1.4-0.9-4-2 0.1-3.9 0.1-5.7 0.2 0 1.8 0.1 3.6 0.1 5.5 0 3.2-0.2 6.7-0.3 10.2 4.1 7.1 7.9 14.2 11.6 21.3 3-0.4 5.8-0.6 8.6-0.7-0.8-6.8-0.4-14.5 1.6-22.7z m-10.6 1.7c-0.4-0.7-0.7-1.3-1.1-2 0.6-0.2 1.1-0.5 1.7-0.8-0.2 1-0.4 1.9-0.6 2.8zM807.6 498c-3.3-0.9-6.6-1.8-9.6-2.8-3.7-1.2-7-2.3-10-3.5-0.6 4.9-0.6 9.8 0.2 14.5 0 0-5.2-6.9-8.9-18.1-2.1-0.9-4.1-1.9-5.8-2.8 0.1 0.1 0.1 0.2 0.2 0.3 4.3 9.2 8.3 18.4 11.9 27.5h2.3c7.5 0 14.1 0.9 20.1 2.5-0.8-5.9-0.9-11.8-0.4-17.6zM359.7 444.3c-1.6 1.8-3.2 3.6-4.7 5.6 4.2 4.8 7.4 9.6 9.9 14.4 2.8 0.2 10.5 1.1 19.6 4.6-0.5-8.5-1.8-17-2.3-24.5-0.5-7.1-0.6-13.2-0.4-18.4-8.2 5-15.5 11.1-22.1 18.3z m11.4 10.6c-1-1.6-2-3.2-3.1-4.8 1.4-1.5 2.8-2.9 4.3-4.3 0.2 3.1 0.6 6.2 0.9 9.5-0.7-0.2-1.4-0.3-2.1-0.4zM831.8 347.5c-9.1-4.2-16.1-8.2-21.5-11.7 2 4.8 3.9 9.8 5.8 14.9 5.6-1.9 11-2.8 15.7-3.2zM327.2 401c9.3 0 19.8 2 31.1 7.4 9.8-7.3 20.7-13.2 32.6-17.8-4-1.8-8.5-3.9-13.5-6.6-5-2.6-10.3-5.9-15.8-9-11.2 6.5-20.7 8.1-20.7 8.1 4.6-3.4 8.4-7.9 11.7-12.8-2-0.9-4-1.8-6-2.5-9 19.2-24.2 28.7-24.2 28.7 8.5-14 7.6-33.7 9.1-49.1 1-9.1 2.3-16.5 3.8-22.5-9 2.6-17.8 6.1-26.5 10.4 13.7 33 1.9 58-7.4 70.9 7.1-2.9 15.8-5.2 25.8-5.2z m34.2-14.5c0.4 0.2 0.8 0.5 1.2 0.7 1.8 1.1 3.6 2.1 5.5 3.2-3.7 2.1-7.4 4.3-10.9 6.7-4.5-1.8-9-3.2-13.5-4.2 2.6-0.7 9.4-2.4 17.7-6.4z m-39-46.3c-0.1 0.9-0.2 1.8-0.4 2.7-0.2-0.8-0.4-1.5-0.7-2.3 0.4-0.2 0.7-0.3 1.1-0.4zM809.6 439v-0.1c-0.9-0.6-1.8-1.2-2.8-1.8-0.9-0.5-1.7-1.1-2.6-1.6-1.2 1.6-2.5 3.2-3.8 4.9-0.8 4.9-2 10.4-3.6 16.8-1.3 5.1-3 10.5-4.7 16.1 7.1 1.2 13.2 3.4 18.6 6.1 0.8-3.3 1.7-6.5 2.7-9.5-0.1-0.4-0.1-0.8-0.2-1.2 0-0.6-0.9-12-3.6-29.7zM287.4 414.2c2-1.5 4.5-3.1 7.4-4.7 3.1-13.9 0.2-30-0.4-43.2-0.4-9.3-0.2-16.9 0.4-23.1-9 5.8-17.5 12.7-25.4 20.7 15.2 17.8 18.7 35.9 18 50.3z m-4.6-49.2c0.5-0.5 1-0.9 1.5-1.4 0 1 0.1 2.1 0.1 3.1V367.5c-0.5-0.9-1-1.7-1.6-2.5zM239.5 529.8c3.8-4.2 8.5-8.4 14.2-12-0.8-2.6-1.9-5.2-3.2-7.7-3.4-1.5-6.9-2.7-10.4-3.3 0 0 2.9-0.9 7.8-1.5-5.4-9-12.6-17.4-18-25.1-5.8-8.4-9.9-15.4-12.8-21.2-1.1 3.8-2.2 7.7-3.3 11.6-1.4 5.2-2.6 10.4-3.8 15.5 18.8 13.3 26.6 29.7 29.5 43.7zM247 468.7c2.9-2.7 7.1-6 12.4-9.2-4.1-8-9.1-15.6-12.8-22.6-5.4-10.2-8.8-18.4-11.1-24.9-5 9.9-9.6 20.6-13.6 32 11.8 7.5 19.8 16 25.1 24.7z m-11.6-31.9c0.8 1.6 1.6 3.2 2.5 4.8 0.6 1 1.1 2.1 1.7 3.1-1.8-1.5-3.6-3-5.5-4.5 0.4-1.1 0.8-2.3 1.3-3.4zM222.7 531c-3.4-4.3-6.8-8.5-9.7-12.5-2.8-3.8-5.2-7.4-7.2-10.6-1.4 8.2-2.4 15.8-3.2 22.7 2.4-0.3 5.2-0.5 8.3-0.5 3.6-0.1 7.6 0.2 11.8 0.9z" fill="#005E5E" p-id="63135"></path><path d="M368.1 341.3c5.3-9.8 10.2-17.1 14.3-22.5h-3.6c-9.4 0-18.6 0.8-27.7 2.5 3.5 15.7 2 29-1.7 39.7 2.8-0.4 5.8-0.6 9.1-0.6 3.4-6.6 6.4-13.3 9.6-19.1z m-4.9-11.7l-0.6 0.9c0-0.3-0.1-0.6-0.1-0.9 0.2 0.1 0.5 0 0.7 0zM759.3 416.6c-1.6-0.4-3.3-0.7-4.9-1 0.1 0.7 0.2 1.4 0.3 2.2 1.7-0.4 3.3-0.8 4.9-1.1-0.1-0.1-0.2-0.1-0.3-0.1zM454.3 355.4c7.9-4.3 14.7-7.5 20.4-9.7-7.6-4.3-16.7-8.8-26.9-12.9-2.9 5.9-6.2 11-9.7 15.4 4.4 2.3 8.7 5.3 13 9 1.1-0.6 2.2-1.2 3.2-1.8zM445.5 379.6c0-0.1 0-0.1 0 0h-0.6 0.6zM826.5 383.6c0.9 3.2 1.7 6.5 2.5 9.6 2.1-1.5 4.2-2.8 6.3-3.9-3.4-2-6.3-3.9-8.8-5.7z" fill="#005E5E" p-id="63136"></path><path d="M927.9 442.1c0.9 0.3 1.9 0.4 2.8 0.4 3.5 0 6.9-1.9 8.7-5 2.3-4 1.5-9.1-1.8-12.2-0.6-0.6-14.9-13.8-37.5-18.4-2-4.1-4.7-8.7-8.2-13.4 4-1 7-4.5 7.4-8.7 0.5-4.6-2.3-8.9-6.7-10.4-0.5-0.2-3.2-1.1-7.4-1.9 0-0.9-0.1-1.7-0.3-2.6-0.1-0.6-3.7-15.3-15.5-29.8-10.3-12.6-28.9-27.6-59.9-29.6-0.4-0.7-0.7-1.4-1.1-2.2l5.4 1.2c3.8 0.8 7.7 1.5 11.8 2.2 11.9 2 24.2 4.1 32.1 10.2 1.8 1.4 3.9 2 6 2 2.3 0 4.5-0.8 6.4-2.3 3.6-2.9 4.7-8 2.6-12.1-0.5-1.1-5.7-11.2-16.7-21.3-15-13.7-33.8-21-54.4-21-5.9 0-12 0.6-18.2 1.8-0.9-1.2-1.9-2.4-2.8-3.5 3-0.1 6-0.3 9.2-0.6 5-0.4 10.2-0.7 15.1-0.7 8 0 14 1 18.7 3 1.3 0.6 2.7 0.8 4 0.8 3.1 0 6.1-1.4 8-4 2.8-3.7 2.7-8.9-0.3-12.4-0.9-1.1-22.7-26.7-59.5-26.7-10.4 0-21 2.1-31.6 6.2-0.1-0.1-0.2-0.2-0.4-0.3l5.4-1.8c9.7-3.2 19.8-6.6 28.8-6.6 1.7 0 3.3 0.1 4.8 0.4 0.5 0.1 1.1 0.1 1.6 0.1 4 0 7.7-2.4 9.2-6.2 1.8-4.3 0.4-9.2-3.4-11.9-0.8-0.6-19.1-13.5-45-13.5-17.4 0-33.9 5.7-49.2 16.9-2.3-0.7-4.7-1.3-7-1.9 1.9-1.6 3.8-3.2 5.8-4.9 9.2-7.9 18.8-16.1 28.7-18.4 4.5-1 7.7-5.1 7.7-9.7s-3.2-8.7-7.7-9.8c-0.6-0.2-6.6-1.5-15.4-1.5-17.1 0-48.2 5.2-69.7 39.1-0.5 0-1 0.1-1.5 0.1 0.7-1.2 1.5-2.4 2.2-3.6 6.2-10.4 12.6-21.2 21.2-26.5 4-2.4 5.7-7.3 4.2-11.7-1.4-4.1-5.2-6.8-9.5-6.8h-0.9c-0.6 0.1-14.5 1.4-29.9 10.1-9.3 5.3-20.4 14-28.8 28.1 2-4.4 4.4-8.4 7.4-11.5 3.2-3.3 3.8-8.4 1.3-12.4-1.9-2.9-5.1-4.6-8.4-4.6-1.1 0-2.2 0.2-3.3 0.6-0.6 0.2-14 5-26.9 17.4-5.5 5.3-11.5 12.6-16.1 22.1-0.1-0.5-0.2-0.9-0.2-1.4-3.4-18-11.9-29.8-12.3-30.3-1.9-2.7-5-4.1-8.1-4.1-1.3 0-2.6 0.2-3.8 0.8-4.3 1.8-6.8 6.2-6 10.8 1 6.4-0.2 13.5-2.2 20.8-2.8-3.6-5.8-7-8.9-10.2 5.6-25.9-1.7-45.9-9.2-58.4-8.6-14.5-19.3-22.4-19.8-22.7-1.8-1.3-3.8-1.9-5.9-1.9-2.3 0-4.6 0.8-6.5 2.4-3.5 3-4.5 8-2.4 12.2 4.7 9.1 4.7 21.7 4.7 33.9v7.3c-2.4-1.1-4.9-2.1-7.4-3-0.3-28.1-12.7-46.6-23.5-57.4-12.7-12.7-26.1-17.6-26.7-17.9-1.1-0.4-2.3-0.6-3.4-0.6-3.3 0-6.4 1.6-8.3 4.5-2.6 3.9-2.1 9 1 12.3 7 7.5 10.4 19.7 13.8 31.5 1.1 3.8 2.1 7.4 3.3 11 0.9 2.8 1.9 5.5 2.9 8.2-1.9-0.1-3.9-0.2-5.9-0.3-4.6-18.5-15-33.9-30.2-45.1-13.2-9.6-25.6-12.7-26.1-12.8-0.8-0.2-1.6-0.3-2.3-0.3-3.7 0-7.2 2.1-8.9 5.5-2.1 4.1-1.1 9.2 2.5 12.2 7.6 6.4 12.3 17.7 16.8 28.8-7-8.3-15.3-14.9-24.9-19.7-14.1-7.1-27.9-8.6-36.9-8.6-6.7 0-11 0.8-11.5 0.9-4.5 0.9-7.9 4.7-8.1 9.4-0.2 4.6 2.8 8.8 7.2 10.1 9.8 2.8 19 11.6 27.8 20 2.9 2.8 5.6 5.3 8.4 7.8 2.3 2 4.5 3.8 6.7 5.6-4.1 1.5-7.7 4-10.4 7.4-42.2 11.8-60.5 33.9-68.5 50.5-1.6 3.4-1.2 7.5 1.2 10.5 1.9 2.4 4.8 3.8 7.9 3.8 0.7 0 1.4-0.1 2-0.2 1.6-0.3 38.3-8.1 68.5-27 1.1 0.4 2.2 0.6 3.3 0.8-0.5 1-1.1 2.1-1.7 3.1-5.8 10.9-11.8 22.2-20.4 28.1-1.8 1.2-3.1 3-3.8 4.9-1.2 0-2.3-0.1-3.4-0.1-8.9 0-14.8 1.4-15.4 1.5-4.5 1.1-7.7 5.1-7.7 9.8 0 4.6 3.2 8.7 7.7 9.7 9.8 2.3 19.3 10.4 28.5 18.3l4.2 3.6c-2.4 0.7-4.7 1.4-7.1 2.1-14.8-10.3-30.7-15.6-47.4-15.6-25.9 0-44.2 13-45 13.5-3.8 2.7-5.2 7.6-3.4 11.9 1.6 3.8 5.2 6.2 9.2 6.2 0.5 0 1.1 0 1.6-0.1 1.5-0.2 3.1-0.4 4.8-0.4 9 0 19.1 3.3 28.8 6.6 1 0.3 2 0.7 2.9 1-0.1 0.1-0.2 0.1-0.3 0.2-9.8-3.5-19.6-5.3-29.2-5.3-36.8 0-58.6 25.6-59.5 26.7-3 3.6-3.1 8.7-0.3 12.4 1.9 2.6 4.9 4 8 4 1.3 0 2.7-0.3 4-0.8 4.7-2.1 10.7-3 18.7-3 4.9 0 10.1 0.4 15.1 0.7 1.6 0.1 3.1 0.2 4.6 0.3-0.9 1-1.7 2-2.5 3.1-4.7-0.7-9.3-1-13.8-1-20.6 0-39.4 7.3-54.4 21-11.1 10.2-16.2 20.2-16.8 21.3-2 4.2-1 9.2 2.6 12.1 1.8 1.5 4.1 2.3 6.4 2.3 2.1 0 4.3-0.7 6-2 8-6.1 20.3-8.2 32.1-10.2 3.8-0.6 7.4-1.3 10.9-2-0.2 0.4-0.4 0.8-0.6 1.3-28.6 3.5-45.7 18.2-55.2 30.4-10.9 14-14.3 27.8-14.4 28.4-1 4.3 1 8.8 4.8 11-4.2 3.6-7.7 7.4-10.4 11-11.1 14.1-14.5 28.1-14.6 28.6-1.1 4.5 1.1 9.2 5.3 11.2 1.4 0.7 3 1.1 4.5 1.1 2.9 0 5.7-1.2 7.7-3.6 6.6-7.8 18.2-12.7 29.5-17.3 3.6-1.5 7.2-3 10.6-4.6 0.2-0.1 0.5-0.2 0.7-0.3-0.2 0.9-0.4 1.9-0.5 2.8-27.3 8-41.7 25-49.1 38.4-8.6 15.6-9.8 29.7-9.8 30.3-0.3 4.6 2.5 8.9 7 10.3 1 0.3 2 0.5 3 0.5 3.4 0 6.7-1.8 8.6-4.9 5.2-8.7 15.9-15.3 26.3-21.6 2.6-1.6 5.2-3.2 7.7-4.8-0.5 5.8-0.7 10.7-0.9 14.7-0.5 1.5-0.9 3-1.4 4.6-12.1 3.7-19.7 9-20.1 9.2-3.8 2.7-5.3 7.6-3.6 11.9 1.5 3.9 5.2 6.3 9.3 6.3 0.5 0 0.9 0 1.4-0.1 1.3-0.2 2.8-0.3 4.3-0.3 1 0 2 0 3 0.1-0.9 6.6-1.5 12.6-1.9 17.9-26.1 6.9-40.7 25.4-41.3 26.2-2.8 3.7-2.8 8.8 0.1 12.4 1.4 1.7 3.3 2.9 5.3 3.4-21.7 9.8-32.8 26.8-33.5 27.8-2.5 3.9-2 9 1.2 12.3 1.9 2 4.6 3.1 7.2 3.1 1.7 0 3.5-0.5 5.1-1.4 8.6-5.1 21-5.8 32.9-6.5-18 6.9-29.4 18.2-36.4 28.2-11.2 15.9-13.6 31.5-13.7 32.1-0.7 4.6 1.9 9 6.2 10.7 1.2 0.5 2.5 0.7 3.7 0.7 3.2 0 6.3-1.5 8.2-4.2 5.9-8.4 17.2-14.2 28.1-19.7 3.5-1.8 6.8-3.5 9.9-5.2 0.6 7.2 4.6 13.9 10.9 18 0.1 30 8.9 54.5 25.6 71.1 1.9 1.9 4.4 2.9 7 2.9 1.1 0 2.2-0.2 3.2-0.5 3.6-1.2 6.2-4.4 6.7-8.2 0.2-1.9 5.5-44.1-4.8-80.5 2 2.3 4 4.5 6.2 6.8 8.3 9 17 18.4 19.7 28.4 1.2 4.4 5.2 7.4 9.6 7.4h0.3c4.6-0.2 8.5-3.5 9.5-8 0.1-0.5 2.5-12.7-0.5-28.5-1.1-5.6-2.7-10.9-4.8-15.9 1.9-1.1 3.5-2.9 4.3-5.1 0.5-1.3 1.1-2.7 1.9-4 3.5 3.3 5.9 6.5 7.6 9.7 1.7 3.4 5.2 5.4 8.9 5.4 0.8 0 1.6-0.1 2.5-0.3h0.1c0.6 20.8 3.8 37 4 38.1 0.8 3.7 3.6 6.7 7.2 7.7 0.8 0.2 1.7 0.3 2.5 0.3 2.9 0 5.6-1.2 7.5-3.4 11-12.6 17.5-28.8 19.3-48.2 1.2-12.8 0.4-26.7-2.4-41.3 0.1-0.6 0.2-1.3 0.3-2.1 1.6-3.3 3.5-7.9 5.1-13.5 2 1.8 4.1 3.7 6.2 5.6 8.7 7.7 17.8 15.7 21.3 24.7 1.5 3.9 5.2 6.3 9.3 6.3 0.5 0 0.9 0 1.4-0.1 4.6-0.6 8.1-4.3 8.6-8.9 0.1-0.7 1.2-13.7-4-29.5 0.8 0.2 1.7 0.3 2.6 0.3 0.4 0 0.8 0 1.2-0.1 4.6-0.5 8.2-4.1 8.8-8.7 0.1-0.4 0.5-4.4 0.1-10.5 2.5-1.9 12.8-10.3 20.7-24.8 7.2-13.1 13.6-33.4 7-59.5 2.9-0.4 5.8-0.8 8.8-1-1.5 6.3-2.7 13.2-3.6 20.7-0.5 3.7-0.8 7.5-1.1 11.5-1 12.1-2 24.6-7.5 33.2-2.5 3.9-1.9 9 1.3 12.3 1.9 2 4.5 3 7.2 3 1.8 0 3.6-0.5 5.2-1.4 0.5-0.3 13-8 23.1-23.2 8-12.1 16-31.3 12.2-57 5.7 0.3 11.5 0.8 17.2 1.5-1.3 6.7-2.3 14.2-3 22.4-0.3 3.7-0.4 7.5-0.6 11.4-0.4 12.2-0.9 24.8-6 33.7-2.3 4-1.5 9.1 1.8 12.3 1.9 1.8 4.4 2.7 6.8 2.7 1.9 0 3.8-0.6 5.5-1.7 0.5-0.3 12-8.1 21.3-22.9 7-11.2 13.9-28.3 11.6-50.6 1.1 0.3 2.2 0.6 3.2 0.9l-4.5 108.2-1.1 26.6-2.2 53-1 23.8-3.7 89.1v0.4h-121v-53.5c0-9.4-3.7-18.3-10.4-24.9-6.7-6.7-15.5-10.4-24.9-10.4-19.4 0-35.2 15.8-35.2 35.2v53.6H123.6c-9.4 0-18.3 3.7-24.9 10.4-6.7 6.7-10.4 15.5-10.4 24.9 0 19.4 15.8 35.2 35.2 35.2H903c9.4 0 18.3-3.7 24.9-10.4 6.7-6.7 10.4-15.5 10.4-24.9 0-8.8-3.2-17.2-9.2-23.7-0.8-0.8-1.6-1.6-2.4-2.3-2.1-1.9-4.4-3.5-6.9-4.9-0.5-0.3-1-0.5-1.5-0.8-1-0.5-2.1-0.9-3.1-1.3-0.8-0.3-1.6-0.5-2.1-0.7-3.3-1-6.6-1.4-10-1.4h-97.5V778c0-9.4-3.7-18.3-10.4-24.9-6.7-6.7-15.5-10.4-24.9-10.4-19.4 0-35.2 15.8-35.2 35.2v87.9h-66.7v-49.2c0-9.4-3.7-18.3-10.4-24.9-6.7-6.7-15.5-10.4-24.9-10.4-19.4 0-35.2 15.8-35.2 35.2v49.3h-41.7v-0.4l-5.8-158v-0.4l-2.3-59.9v-0.3l-2.9-72.9c0.9-1.3 1.8-2.7 2.8-4l2-3c3.5-5.1 7.2-10.4 11-15.7 13.5 8.4 27.8 12.6 42.8 12.6 25.6 0 43.7-12.6 44.4-13.2 3.8-2.7 5.2-7.6 3.5-11.9-1.5-3.8-5.2-6.2-9.3-6.2-0.5 0-1 0-1.5 0.1-1.4 0.2-3 0.3-4.6 0.3-9.2 0-19.4-3.5-29.4-6.9-3.6-1.2-7.1-2.4-10.5-3.5h-0.1c-4.1-1.2-8-2.2-11.8-3.1 4-5 7.9-9.7 11.7-14.2 19.3 17.6 39.9 21.6 54.5 21.6 17.5 0 30.2-5.7 30.8-5.9 3.9-1.8 6.2-5.8 5.8-10 9.7 2.8 16.8 3.1 17.2 3.1h0.5c-0.2 17.5 5.4 30.2 5.8 31 1.2 2.6 3.4 4.5 6 5.4-0.1 1-0.2 2-0.3 2.9-1.4 16.1 2.5 28.2 2.7 28.7 1.2 3.8 4.6 6.4 8.4 6.8-0.2 0.8-0.4 1.7-0.6 2.5-3.4 16-0.9 28.7-0.8 29.2 0.9 4.5 4.9 7.8 9.5 8h0.3c1.2 0 2.3-0.2 3.4-0.6-0.1 0.3-0.2 0.6-0.2 1-3.6 15.7-1.4 28.2-1.3 28.7 0.8 4.6 4.7 7.9 9.3 8.2h0.5c4.4 0 8.3-2.9 9.6-7.2 2.8-9.3 11.1-18 19.3-26.4 1.4-1.5 2.8-2.9 4.1-4.3 3.3 15.6 6 31.3 8.1 46.4 0 0.2 0 0.3 0.1 0.5l0.1 0.7c0.1 1 0.3 2 0.3 2.6v0.2c0.2 2.1 0.4 3.8 0.5 5 0.1 0.8 0.2 1.4 0.2 1.7v0.2c0.3 3.4 1.3 6.6 2.9 9.6 4.2 13.8 11.1 25.3 20.4 34.4 1.9 1.8 4.4 2.8 7 2.8 1.1 0 2.3-0.2 3.3-0.6 3.6-1.3 6.1-4.5 6.6-8.2 0.1-0.4 1.2-10.1 1.2-23.9 4.5-4.9 6.8-11.5 6.1-18.2-0.2-2.5-1.2-12-3.4-26.7 7.1 5.5 13.6 11.4 16.8 18.1 1.7 3.5 5.2 5.7 9 5.7 0.7 0 1.4-0.1 2.1-0.2 4.5-1 7.8-4.9 7.9-9.6 0-0.5 0.2-13.5-6.1-28.7-5.5-13.2-17-30.6-40.8-41.1-0.1-0.4-0.2-0.8-0.3-1.3l7.2 3.9c10.1 5.4 20.6 11 26 18.8 1.9 2.8 5 4.3 8.2 4.3 1.2 0 2.4-0.2 3.6-0.7 4.3-1.7 6.9-6.1 6.3-10.7-0.1-0.6-2.1-14.7-11.9-29.5-8.4-12.8-24.3-28.5-52.8-33.7-0.3-0.8-0.5-1.6-0.8-2.4 0.2 0.1 0.5 0.2 0.7 0.3 1.7 1.3 3.8 2.1 6 2.1 1 0.3 1.9 0.7 2.9 1 10.9 3.7 22.2 7.5 28.8 14.4 1.9 2 4.6 3.1 7.2 3.1 1.7 0 3.5-0.4 5-1.4 4-2.3 5.9-7.1 4.5-11.6-0.2-0.8-4.3-13.6-15.8-26.4 0.7-2.3 0.7-4.8-0.3-7.1 0-0.1-0.1-0.2-0.1-0.3 0.1-0.1 0.2-0.1 0.3-0.2 3.8-2.6 5.4-7.5 3.7-11.8-0.2-0.6-2.3-5.8-6.8-12.5 0.2-3.1 0.4-6.3 0.7-9.3 0.1-1.7 0.3-3.5 0.4-5.3l0.1-0.1c0.7 0.3 1.5 0.5 2.2 0.7 15.1 33 42.9 60.3 44.1 61.5 1.9 1.9 4.4 2.8 7 2.8 1.1 0 2.2-0.2 3.3-0.6 3.6-1.3 6.1-4.4 6.6-8.2 1.5-12.5 0.3-29.8-9.8-49.8 0.1 0 0.2-0.1 0.3-0.1 4.4-1.4 7.3-5.7 6.9-10.3-0.1-0.9-1.5-17.3-12.3-34.5 7.9-1.5 16-3.1 23.5-3.1 3.9 0.2 7.3 0.6 10.3 1.5zM287 812.2c0-13.9 11.3-25.2 25.2-25.2 6.7 0 13.1 2.6 17.9 7.4s7.4 11.1 7.4 17.9v53.5H287v-53.6z m458.1-34.3c0-13.9 11.3-25.2 25.2-25.2 6.7 0 13.1 2.6 17.9 7.4 4.8 4.8 7.4 11.1 7.4 17.9v87.8h-50.5v-87.9z m-137.2 38.6c0-13.9 11.3-25.2 25.2-25.2 6.7 0 13.1 2.6 17.9 7.4 4.8 4.8 7.4 11.1 7.4 17.9v49.2h-50.5v-49.3z m295.2 59.3c2.4 0 4.8 0.3 7.2 1 0.4 0.1 1 0.3 1.5 0.5 0.8 0.3 1.5 0.6 2.3 1 0.4 0.2 0.7 0.4 1.1 0.6 1.8 1 3.4 2.1 4.9 3.5 0.6 0.5 1.2 1.1 1.7 1.7 4.2 4.6 6.5 10.7 6.5 17 0 6.7-2.6 13.1-7.4 17.9-4.8 4.8-11.1 7.4-17.9 7.4H123.5c-13.9 0-25.2-11.3-25.2-25.2 0-6.7 2.6-13.1 7.4-17.9 4.8-4.8 11.1-7.4 17.9-7.4h779.5zM709.9 488.2c0.1-1.1 0.3-2.2 0.4-3.2 0.2 0.2 0.4 0.4 0.7 0.5-0.3 0.9-0.7 1.8-1.1 2.7z m171-52.1c-1.8 0.3-3.6 0.5-5.3 0.7 19.1 18.6 20.9 42.3 20.9 42.3-6.5-10.9-18.7-18.3-29.7-25.1 0 0 0 0.1 0.1 0.1 1.3 2.5 1.7 5.5 1.2 8.1v0.1c15.8 16.8 34.9 44.1 31.1 75 0 0-30.4-29.7-44.2-63.5h-0.5c-4 0-8-1.7-10.7-5.1 0 0-0.9-1.1-2.7-2.9 0.1 0.6 0.1 1.1 0.1 1.3-0.1 4.2-1.9 8.3-5.1 11.1-0.4 6.8-1.2 14.3-1.4 21.7 5.3 7.3 7.5 13.1 7.5 13.1-2.3-2.1-4.8-3.8-7.5-5.4 0.3 6.3 1.3 12.5 3.7 18.1 0 0-6.4-5.4-12.4-15.3-1.1 3.9-2.3 7.6-3.5 10.9 24.2 13 31.6 36.8 31.6 36.8-9.7-10.2-25.4-14.3-38.5-18.9-0.1 0.3-0.2 0.5-0.2 0.5l-0.3-0.6c-1.4-0.5-2.7-1-4-1.5-8-3.1-14.4-6.1-19.6-8.8 0 0 0 0.1 0.1 0.1 3.8 10.2 7.2 20.2 10.1 29.8 55.6 6.5 62.4 55.7 62.4 55.7-8.9-12.8-26.4-19.7-39.2-27.3-7.7-4.6-13.8-8.7-18.5-12.3 0 0.1 0.1 0.2 0.1 0.3 2.8 9.9 5.2 19.2 7.2 27.7 0.3 1 0.5 2.1 0.7 3.1 46.4 17.3 45.5 62.3 45.5 62.3-6.7-14.1-23-23.7-34.5-33.1-2.1-1.7-4-3.3-5.8-4.9v0.2c6 30.6 7.8 50.6 7.9 51.6 0.6 5.2-2 10-6.2 12.7 0.2 15.7-1.1 27.2-1.1 27.2-9.2-8.9-14.9-19.9-18.1-31.3 0-0.1-0.1-0.1-0.1-0.2-1.1-1.8-1.8-3.9-2-6.1 0-0.2-0.3-2.6-0.7-7-0.1-1.1-0.3-2.4-0.5-3.8v-0.1c-1.8-13.2-5.5-37.5-12.7-67.3-2.6 3.5-5.8 7.4-9.5 11.6-9.8 11-24.3 23-28.7 38.1 0 0-7.9-43.2 33.5-67.9-1.9-7.2-4.2-14.6-6.5-22.2-2.9 4.2-6.4 8.8-10.8 14.1-9.6 11.3-23.8 23.7-27.9 38.7 0 0-9.1-43.9 33.2-69.5-2.9-8.3-6-16.7-9.4-25.1-2.2 4-4.8 8.4-8 13.3-8.1 12.2-20.9 26.1-23.2 41.7 0 0-13.8-41.9 24-72.1-3-6.6-6.1-13.4-9.4-19.9 0 0 0-0.1-0.1-0.1-1.4 3.1-3 6.5-4.8 10.1-6.7 13.1-17.8 28.3-18.5 44 0 0-13.2-29 3.8-58.6-5.7-3.6-12.4-9-18.2-16.5-3.6 9.8-6.7 20.1-5.5 30 0 0-16-24.4-6.6-54.5-1.5-5.7-2.5-12-2.6-19-4.8 1.7-9.5 3.6-14.1 5.6h-0.1c-0.3 12.3-0.6 25.7 4.5 36.5 0 0-13.2-10.1-20.1-28.5-1.7 1-3.3 2-5 3 0 0-0.1 0-0.1 0.1 2.4 4.1 5.2 7.9 8.7 11 0 0-4.8-1.3-11.4-4.9 5.1 4.8 11.3 11.6 18.5 21.3 9.2 12.5 18.5 29.9 33 37.6 0 0-49.5-1.3-64.2-54.7-12.9 9.5-24.8 20.3-35.9 31.7 6.7 2.1 15.5 5.6 26.6 11.3 13.7 7.2 29.6 18.9 46 19.5 0 0-11.1 5-26.7 5-15.9 0-36.5-5.2-54.9-26.2-10.6 11.7-20.3 23.9-29.2 35.7 6.8 0.8 15.7 2.6 26.9 5.8 12.9 3.9 28.3 10.8 42.7 10.8 2.1 0 4.1-0.1 6.1-0.5 0 0-15.9 11.3-38.6 11.3-13.4 0-29.1-3.9-45.2-16.4-6.8 9.4-13.1 18.5-18.9 26.9-1.5 2.2-3 4.3-4.4 6.4-0.1 0.1-0.1 0.2-0.2 0.3l3 76.3v0.1l2.3 60.1v0.2l5.8 158.2h-67.6l3.7-89.1 1-23.8 2.2-53 1.1-26.6 4.9-116c-6.9-2.2-15.8-4.7-26.3-6.9 14.6 51.8-25.7 78.6-25.7 78.6 8.2-14.3 6.7-34 7.9-49.3 1.2-14.4 3.3-24.5 5.3-31.6-0.6-0.1-1.3-0.2-1.9-0.3-11.4-1.8-25.1-3.1-40.1-3.2 15.9 55.5-28 82-28 82 8.8-13.9 8.1-33.6 10.1-48.9 1.9-15.4 4.7-26 7.3-32.9-11.3 0.4-23.2 1.7-35.4 4 20.9 54.4-21 84.5-21 84.5 7.7-14.6 5.5-34.2 6-49.6 0.3-7 0.9-13 1.6-18.2-0.8 3.8-1.6 6.1-1.6 6.1-0.8-6.1-3.1-12-6.1-17.6-3.7 1.1-7.3 2.3-11 3.6C350.7 582.3 344 610 344 610c-3.7-15.2-17.5-28.1-26.6-39.5-1.4-1.8-2.7-3.5-4-5.2-2.9 1.4-5.7 2.8-8.6 4.3 9.7 10.5 15.4 21.1 18.4 31 19.8 22.4 16.5 49.6 16.5 49.6-2.8-7.6-8.2-14.3-14.2-20.3-1 7.4-3 13.7-4.9 18.4 12.6 19.7 10.6 40.1 10.6 40.1-5.7-14.6-21.2-25.4-31.8-35.6-4.8-4.6-8.7-8.8-12-12.5-0.2 14.4-4.8 26-7.8 31.9-0.4 2.3-0.6 4.2-0.8 5.4 4.4 21.5 7.3 57.9-14.3 82.7 0 0-7.4-36.2-1.8-69.1-7.5-1.1-12.7-8.1-11.7-15.6 0-0.1 0-0.3 0.1-0.6-3.5 3.3-7.4 6.7-11.3 10.3 8.2 15.3 8.4 29.2 8.4 29.2-4-7.7-10.8-14-18.1-19.6-4.1 4.6-7.5 9.5-9.6 15 0 0-0.9-8.8 2-20.5-4-2.8-8-5.5-11.5-8.2-3.7-2.8-6.9-5.5-9.8-8-3.5 5.9-6.9 12-10.2 18.2 38.7 27 30 69.4 30 69.4-4.3-15.9-19.2-28.8-29.2-40.6-3.6-4.3-6.7-8.2-9.3-11.8-2.8 5.8-5.4 11.8-8 18 11.8 35.8 5.9 81.1 5.9 81.1-19.7-19.6-23.4-48.1-22.5-70.4-0.9-0.2-1.7-0.4-2.5-0.8-7-3-10.4-11.1-7.5-18.1 2.4-5.8 4.9-11.4 7.4-16.9-5.4 4.4-12.9 9.7-23.2 15.6-13.4 7.6-31.9 14.5-41.4 28 0 0 8.1-54.9 71.5-57.9 3.5-7 7.1-13.7 10.8-20.3-7 2.1-16.9 4.3-30.8 5.7-15.3 1.5-35.1 0.3-49.2 8.6 0 0 19.2-30 57.2-30 8.7 0 18.3 1.6 28.9 5.4 0.9-1.4 1.7-2.8 2.6-4.2-2.3-3.5-2.8-5.4-2.8-5.4 1.9 0.3 3.8 0.6 5.6 0.9 3.4-5.3 6.9-10.5 10.4-15.4-6.4 1-14.5 1.6-24.6 1.7h-0.7c-6.8 0-14.3-0.5-21.9-0.5-9.5 0-19 0.9-27.2 4.7 0 0 15.4-19.9 43-24.2 0.4-8.5 1.3-20.9 3.8-34.3-4.9-1.2-9.7-1.9-14.5-1.9-1.9 0-3.8 0.1-5.7 0.4 0 0 8.8-6.1 22.5-9.3 0.9-3.7 1.9-7.4 3.1-11 0.3-7.6 1.1-21 3.3-37.9-4.2 3.5-9.4 7.4-15.7 11.7-12.8 8.7-30.8 17-39.2 31 0 0 3.7-49.5 57.7-61.4 1.6-9.4 3.6-19.5 6.2-29.9-5.1 3.1-11.4 6.6-19.3 10.3-14 6.6-33 12-43.5 24.6 0 0 11.5-48.8 67.4-51.7 3.1-10.7 6.6-20.9 10.5-30.7-4 2.3-8.7 4.7-14.1 7.2-14 6.6-33 12-43.5 24.6 0 0 11.4-48.2 66.3-51.7 3.9-8 8-15.6 12.5-22.7 0.8-1.4 1.7-2.7 2.5-4-5.8 2-13.1 4.1-22 6-15.1 3.3-34.8 4.3-47.9 14.2 0 0 18.1-36.7 62.2-36.7 5.6 0 11.5 0.6 18 1.9 6.7-8.7 13.8-16.6 21.5-23.7-3 0.2-6.2 0.2-9.7 0.2-1.9 0-3.8 0-5.9-0.1-8.3-0.2-17.8-1.4-27.2-1.4-8 0-15.8 0.8-22.7 3.9 0 0 19.3-23.1 51.9-23.1 9.2 0 19.4 1.8 30.6 6.6 5.7-4.1 11.6-7.8 17.7-11.2 2.4-1.3 4.8-2.5 7.2-3.7-4.5-0.9-9.5-2.1-15.1-3.7-12.9-3.7-28.2-10.5-42.6-10.5-2.2 0-4.3 0.2-6.4 0.5 0 0 16.1-11.6 39.1-11.6 13.5 0 29.3 4 45.6 16.7 10.5-3.7 21.3-6.4 32.2-8.1-3.7-2.5-7.8-5.5-12.3-9-12.2-9.5-25.6-24-41.5-27.7 0 0 5.2-1.2 13.1-1.2 16 0 43.4 5.1 62.1 35.8 2.5-0.1 5-0.1 7.5-0.1 10.1 0 20.4 0.8 30.7 2.4-2.2-2.9-4.4-6.2-6.8-9.9-5.8-8.8-11.4-20-18.8-28.9-5.2 3.2-8.9 4.5-8.9 4.5 2.3-2.4 4.2-5.1 5.9-8-2.6-2.8-5.5-5.2-8.6-7.2 0 0 4.5 0.4 11.1 2.5 5-10.7 7.6-23.2 10.9-33.4 3.7-11.2 7.3-19.5 10.5-25.7-8 0.3-16.3 1.3-25.1 2.9-10 52.1-57.5 58.4-57.5 58.4 13.7-9.3 21-27.6 28.7-40.9 2.8-4.8 5.5-8.9 8-12.5-3.8 1.1-7.7 2.3-11.7 3.6-1.5 0.5-2.9 0.7-4.4 0.7-3 0-5.8-1-8.2-2.7-29.7 20.3-69.8 28.6-69.8 28.6 13.3-27.7 43.3-40.4 65.7-46.2 1.6-3.1 4.3-5.6 7.9-6.8 6.3-2.1 12.6-4 18.7-5.6-5.9-3.6-13.4-9-22.4-16.8-11.5-10.2-24.2-25.4-40-29.9 0 0 3.7-0.7 9.6-0.7 16.1 0 48.4 5.2 66.4 44.2 5.9-1.2 11.7-2.2 17.4-2.9-2.5-4.4-5.2-9.6-8.1-15.8-6.5-14-11.7-33.1-24.3-43.7 0 0 43.3 10.4 50.5 58.2h3.9c9.1 0 17.8 0.7 26.1 2.2-2.9-5.9-6.1-13.4-9.3-23.2-4.8-14.6-8-34.1-19.2-46.1 0 0 47 17.1 43.4 72.9 7.4 2.3 14.4 5.2 21.2 8.8 2.6 1.4 5.2 2.9 7.6 4.4-0.4-4.1-0.8-8.5-1-13.6-0.6-15.3 1.6-34.9-5.9-49.5 0 0 37.6 27.2 23.8 76.1 8.6 8.1 15.2 16.6 20 24.4 1.6 0.7 2.9 1.9 3.7 3.7 4.5-13.6 10.6-29.2 8.3-43.5 0 0 30.1 41.4-6.1 86.2l0.3 7.8c0.1-0.1 0.2-0.2 0.3-0.4 7.3-8.2 16.6-17.4 27.8-25.9-2.6-55.6 44.5-72.1 44.5-72.1-11.5 11.7-14.9 31.2-20 45.8-1.7 5-3.4 9.3-5 13.2 0.2-0.1 0.4-0.2 0.6-0.4 7.1-4 14.9-7.7 23.4-10.9 11.5-53.2 60.3-57.6 60.3-57.6-14 8.6-22 26.6-30.5 39.5-2.9 4.5-5.7 8.4-8.3 11.9 0.2 0 0.4-0.1 0.7-0.1 8.6-1.7 17.7-2.7 27.4-2.9 18.7-33.4 47.3-38.9 63.8-38.9 7.9 0 13.1 1.2 13.1 1.2-16 3.7-29.4 18.2-41.5 27.7-5.7 4.5-10.8 8.1-15.3 10.9 0.2 0 0.4 0 0.6 0.1 10.5 1.3 21.5 3.6 33 7.3 16.9-13.7 33.3-18 47.2-18 23 0 39.2 11.6 39.2 11.6-2.1-0.3-4.2-0.5-6.4-0.5-14.4 0-29.6 6.8-42.6 10.5-6.6 1.9-12.5 3.3-17.5 4.2 0.1 0 0.2 0.1 0.3 0.1 8.6 4.2 16.8 9.3 24.7 15.2 12.1-5.5 23.1-7.6 32.9-7.6 32.6 0 51.9 23.1 51.9 23.1-6.9-3-14.7-3.9-22.7-3.9-9.4 0-18.9 1.2-27.2 1.4-2.2 0.1-4.3 0.1-6.4 0.1-5.2 0-9.7-0.2-13.7-0.5l0.1 0.1c7.3 7 14.2 14.9 20.7 23.7l0.9 1.2c8.1-2 15.5-2.9 22.3-2.9 44.1 0 62.2 36.7 62.2 36.7-13-9.9-32.8-10.9-47.9-14.2-13.1-2.8-22.5-5.9-29.2-8.8 0 0 0 0.1 0.1 0.1 5.9 9 11.3 18.7 16.3 29.2 59.9 0.4 72.1 51.9 72.1 51.9-8.2-9.8-21.7-15.3-33.9-20.4-7.2 3.7-13.8 9.1-20 14.6 0.1 0.2 0.1 0.4 0.2 0.6l1.2 3.9c17.2 0 30.5 4.2 40.8 10.3 1.9-0.1 3.7-0.2 5.4-0.2 12.1 0 20.4 2.9 20.4 2.9-5.3 0.7-10.3 2.6-15.2 5 10.5 9.3 16.2 20.2 19 27 22.9 2.9 37.5 16.7 37.5 16.7-4.2-1.2-8.6-1.7-13.1-1.7-12.7 0.7-25.8 4.3-37 6z m-222.1 60c-4.4-2.2-8.8-4.7-13.1-7.2-3.3-1.9-6.5-3.8-9.7-5.4h-0.1c-4.5-2.3-8.9-4.4-13-6.2 4.3-4 8.6-7.8 13-11.4 6.1 13.6 14.4 23.4 22.9 30.2zM211.5 693.9l-0.3 2.1c-2.3-2.5-4.7-4.9-7.3-7.1 0.1-0.1 0.1-0.2 0.2-0.4 0.3 0.2 0.6 0.5 1 0.7 2 1.6 4.2 3.1 6.4 4.7z m-35-247.9c0.9-0.4 1.9-0.8 2.8-1.2 1-0.4 2-0.9 3-1.3-0.2 0.5-0.3 1.1-0.5 1.6-1.8 0.3-3.6 0.6-5.3 0.9z m190.6-193.2c0.1 0.1 0.2 0.1 0.3 0.2-2.8 3.4-3.1 8.2-0.7 11.9 1.9 2.9 5.1 4.5 8.4 4.5 1.2 0 2.3-0.2 3.4-0.6 0.2-0.1 1.1-0.4 2.6-1.1 2.5 3.7 4.8 7.6 7.1 11.4 0.5 0.8 1 1.6 1.5 2.5-3.6-0.2-7.1-0.3-10.7-0.3h-2.1c-10.1-14.6-22-23.4-33.6-28.6 2.9-1.3 6.1-3 9.2-4.9 3.5-2.2 7.2-4.8 11-8.1-0.2 0.5-0.4 0.9-0.6 1.4-1.5 4.4 0.3 9.2 4.2 11.7z m1.1-17.6c8.1-8.4 15.6-20 19.8-35.9 0.2 0 0.5-0.1 0.7-0.1-1.3 3.5-2.6 7.2-3.9 11-1.2 3.5-2.2 7.2-3.2 11-1.3 4.6-2.6 9.3-4.2 13.7-2.4-0.4-3.9-0.6-4.2-0.6h-0.9c-1.4 0-2.8 0.3-4.1 0.9z" fill="#005E5E" p-id="63137"></path><path d="M440.2 248.1c2.9 1.3 8.8 4.1 15.3 9.2 5-4 9.8-8.2 14.4-11.7 9.3-7 17-11.8 23.1-15-5.6-8.8-14-18.9-26-27.1-4.5 22.1-15.5 36-26.8 44.6z m32.2-27.3c2.1 2.1 4.2 4.3 6.1 6.7-4.7 2.9-9.6 6.3-14.6 10.1-0.1 0.1-0.2 0.1-0.2 0.2 3.4-5.2 6.3-10.9 8.7-17zM451.9 273.4c-3.5 0.4-6.7 0.6-9.6 0.6-8.7 0-14.5-1.5-14.5-1.5 7.2-1.5 13.9-5.2 20.2-9.6-2.3-5.2-5-10.1-8.6-14.2-11.9 8.8-24 11.9-29.3 12.9 9.1 8 17.4 19.8 21.8 36.9 5.7 1.5 11.4 3.3 17.2 5.3 5.5 1.9 10.7 4 15.6 6.1-2.1-4.7-4.3-10.2-6.6-16.8-2.1-6-3.9-12.9-6.2-19.7zM440 290.3c-0.7-2.2-1.5-4.3-2.3-6.4 1.5 0.1 3 0.1 4.7 0.1h2.4l0.3 0.9 2.4 7.8c-2.5-0.9-5-1.7-7.5-2.4zM388.2 367.4c8.8-6.3 16.6-15 23.9-22.1-2.8-2-5.8-3.8-8.9-5 0 0 1-0.1 2.7-0.1 2.4 0 6.1 0.2 10.7 0.9 6.4-5.8 12-10.1 16.8-13.4-12.4-3.9-24.6-6.6-36.7-7.9-2.4 19.9-10.4 33.8-19.6 43.3 3.6 1 7.3 2.4 11.1 4.3zM437.3 222c7.4-11.7 13.7-19.5 18.8-24.8-11.2-5.4-23.8-8.5-37.6-9.4 1.7 32.6-14 51.7-27 61.9 5.6 2.5 11.8 6 17.7 11 12.7-9.1 20.3-26.3 28.1-38.7z m-28.6 25.9c-0.1-0.1-0.2-0.2-0.4-0.2 4.3-4.8 8-10.1 11-15.8 5.2-9.9 8.3-20.9 9.1-32.8 3.8 0.6 7.5 1.5 11 2.5-3.5 4.5-7 9.6-10.5 15.1-2 3.1-3.8 6.4-5.8 9.8-4.4 7.6-8.9 15.5-14.4 21.4zM397.7 475.5c10.2-11.4 13.2-29.6 17.7-43.2 3.2-9.6 6.3-16.9 9.2-22.5-10 1.8-19.3 4.6-27.9 8.3 9.2 23.5 4.6 42.7-1.8 55.7 0.9 0.5 1.9 1.1 2.8 1.7zM434 380.4c-14.7 0-25.1-4.4-25.1-4.4 8.6-0.6 17-4.2 25.1-8.6-2.3-2.6-4.6-5.3-7-8-9.9 7.9-20.5 11.8-29.4 13.7 4.3 3.1 8.5 6.9 12.6 11.5 7.7-1.9 15.8-3.3 24.1-4.2h-0.3zM845.4 407.4c-4.2 2.7-8.1 5-11.6 7 0 0.2 0.1 0.3 0.1 0.5 0.1 0.6 0.2 1.3 0.3 1.9 7.3 1.3 13.8 3.2 19.5 5.6 11.1-5.3 21.6-7.2 30.9-7.2 1 0 1.9 0 2.8 0.1-9.3-6.7-21.1-10.9-31.2-15.3-3.7 2.6-7.3 5.2-10.8 7.4zM735.3 413.9c-2.3 0-4.7 0.1-6.9 0.2l0.2 0.2c2.9 2.9 5.7 6.1 8.3 9.3 0.6-3.1 1.5-6.4 2.6-9.7H735.3z" fill="#005E5E" p-id="63138"></path><path d="M427.6 462c13.9-7.4 22.7-24 31.6-35.8 6-8 11.3-13.9 15.8-18.3-5.9-0.6-12.3-0.9-19.1-0.9h-2.8c-4.9 0.1-9.7 0.3-14.3 0.7 2.4 47.3-33.6 65-40.5 68 11.7 7.7 23.4 20.4 29.5 41.6 9.1 0.6 18.5 1.6 28.3 3.2 3.2 0.5 6.4 1.1 9.4 1.7-2.3-4.3-4.7-9.3-7.3-15.1-6-14.1-11-33.3-23.2-44.2 0 0 45.4 12.1 49.5 63.6 2.9 0.7 5.6 1.5 8.1 2.2l0.1-3.3v-0.2l0.4-9 0.4-7.9 1.6-36.1v-0.1l2.5-60.8c-2.4-0.5-5.2-1-8.3-1.5-14 51.3-61.7 52.2-61.7 52.2z m21.1-44.8c1.5-0.1 3-0.1 4.5-0.1h0.5c-0.8 1-1.6 2.1-2.5 3.2l-3.3 4.5c0.4-2.5 0.7-5.1 0.8-7.6z m-3.7 83.5c1.1 3 2.2 5.8 3.4 8.6-4.4-0.6-8.8-1-13.2-1.4-4.4-12.1-10.9-22.3-19.3-30.7 2.4-1.7 5-3.8 7.6-6.1 1.3 0.6 2.7 0.9 4.2 0.9h0.2c0.1 0 0.9 0 2.2-0.1 6.6 7 10.8 18.1 14.9 28.8z m40.1-29v0.3l-0.8 18.9c-5.8-10.5-13.2-18-19.8-23.3-1.9-1.5-3.7-2.8-5.5-4.1 8.8-4.5 19.1-11.9 27.5-23.9l-1.4 32.1zM500.3 244.3c-9.9 13.5-21.5 21.1-32.5 25.2 8.7 11 15.7 26.9 14.9 49 7.1 3.7 13.3 7.4 18.4 10.7l0.5-12.8 2.6-62.1c-0.6-1-1.1-2.1-1.4-3.3 0-0.1-0.8-2.7-2.5-6.7z m-8.1 59.7c-1.3-11-4.5-21.2-9.6-30.3 3.9-2.3 7.7-4.9 11.2-7.8l-1.6 38.1zM352 559.8c0.6-3.3 1.2-6.2 1.9-8.7-0.5 0.1-1 0.2-1.4 0.3 0 3-0.2 5.9-0.5 8.4zM736.4 356.9c-4.5-10.1-15.4-42 9.4-73.7-6.9-7.6-14.4-14.6-22.8-20.6 0.4 5.6 0.5 12.2 0.1 20-0.7 15.3-4.6 34.7 1.7 49.9 0 0-35.8-30.8-16.8-79.1-5.1-2.7-10.4-5-16-6.9-3.1-1.1-6.2-2-9.2-2.9 1.2 5.5 2.4 12.2 3.3 20.2 1.6 15.3 0.6 35 9.1 49.1 0 0-38.5-24-29.1-72.8-7-1.1-13.9-1.6-20.6-1.6-2.6 0-5.1 0.1-7.6 0.2 3.5 4.9 7.5 11.1 11.7 18.9 7.3 13.5 13.9 32.2 27.1 41.9 0 0-46.1-7.9-55-58.5-9.1 1.8-18 4.8-26.7 8.8 5.3 3.7 11.8 8.7 19.2 15.6 11.2 10.5 23.5 26.1 39.1 31 0 0-2.7 0.4-7.2 0.4-14.2 0-46-4.3-64.5-40-4.1 2.5-8.1 5.2-12.1 8.1-3.2 2.4-6.2 4.8-9 7.2 5.7 2.3 12.6 5.4 20.6 9.8 13.4 7.5 29 19.5 45.5 20.6 0 0-10.4 4.4-25.1 4.4-15.2 0-34.9-4.7-52.6-23.8-14.5 15-21.9 28.1-22 28.2-0.5 0.8-1 1.7-1.7 2.4l-0.3 0.3 0.2 5.6 1.9 47.2h0.1c3.1-0.6 6.6-1.3 10.5-1.8 7.6-49.1 51.9-57.3 51.9-57.3-12.4 9.4-18.5 27.3-25.4 40.4-3 5.7-5.9 10.5-8.5 14.6h0.2c9.2-0.9 19.3-1.6 30.2-1.6 16.5-46.2 60.7-46.4 61.5-46.4-14 6.9-23.4 23.4-32.5 34.9-3.7 4.7-7.2 8.7-10.3 12h0.1c8 0.5 15.8 1.4 23.3 2.6 2.6-2.7 4.4-4 4.4-4-0.7 1.5-1.3 3-1.8 4.5h0.1c3 0.5 5.8 1.1 8.7 1.7 18.4-29.7 43.2-35.7 60.2-35.7 2.4 0 4.7 0.1 6.8 0.3 1-0.5 1.6-0.7 1.6-0.7-0.2 0.3-0.4 0.5-0.6 0.8 7 0.7 11.5 2.3 11.5 2.3-5.9 0.8-11.5 3.2-17 6.2-6 11.6-8.4 25.9-11.8 37.4-0.7 2.4-1.4 4.6-2.2 6.8 0 0 0.1 0 0.1 0.1 0.4 0.2 0.8 0.4 1.3 0.6 14-10.3 27.3-14.7 39.1-15.6 2.1-4.4 4.9-8.5 7.9-12zM560.6 310c-8.2 5.6-17.9 14.5-24.8 28l-0.7-18.4-0.1-2.1c0.1-0.2 0.3-0.5 0.4-0.7 0-0.1 0.1-0.1 0.1-0.2 1.9-3.1 6.4-10.2 13.8-18.8 4.9 4.2 9.8 7.5 14.7 10.1-1.1 0.6-2.3 1.3-3.4 2.1z m18.4 41.5c-1.8 0-3.7 0.1-5.5 0.2 1.5-2.8 2.9-5.9 4.3-8.8 4.7-9.9 9.6-20.1 16.5-26 2.5 0.2 4.9 0.3 7.1 0.3 2.6 0 5-0.1 7.3-0.3-13 8-23.1 19.8-29.7 34.6z m56.9-45.2h0z m29.6 22.5c-10.7 5.2-20.1 13-28.1 23.2-1.6-1-3.4-1.4-5.2-1.4-2.2 0-4.3 0.7-6.2 2.1-0.1 0.1-0.7 0.5-1.5 1.3h-0.1c1.6-2.1 3.2-4.2 4.8-6.5 6.9-9.4 13.9-19.2 22.6-23.5 4.2-2.1 6.4-6.7 5.3-11.2-0.6-2.6-2.2-4.8-4.4-6.2 1.2-0.1 1.9-0.2 2.1-0.3 1.7-0.3 3.3-1 4.6-2 8.7 3.8 15.1 5 15.5 5 0.4 0.1 0.8 0.1 1.2 0.1 7.1 7.7 13.4 11.7 13.7 11.9 0.1 0.1 0.3 0.2 0.4 0.2-8.6 1.1-16.9 3.5-24.7 7.3z m30.1-69.5c0-0.3-0.1-0.5-0.1-0.8 0.1 0 0.2 0.1 0.3 0.1-0.1 0.3-0.2 0.5-0.2 0.7z m5.3 61.8c0.5-0.3 0.9-0.7 1.3-1.1l0.3-0.3c0.3 0.5 0.6 1 0.8 1.5-0.8 0-1.6-0.1-2.4-0.1z m21.1 38.7c-6.3 1-12.5 2.7-18.6 5.3 1.6-6.2 3.4-12.4 5.8-17.8 4-1.9 7.5-3.1 10.8-3.6 0.6-0.1 1.2-0.2 1.7-0.4 0.9 4.6 2.1 8.7 3.3 12-1 1.4-2 3-3 4.5zM386.4 486.9c-2.7 3.3-4.6 5-4.6 5 1-2.7 1.7-5.5 2.2-8.3-5.4-7.2-11.3-14.1-18.6-18.5 11.9 23.5 5.9 45.6 2.3 55 12.7-2 26.6-3.3 41.7-3.3-3.8-4.1-8-9.1-12.7-15.2-3.3-4.5-6.7-9.6-10.3-14.7z m-5.2 21.3c0.3-2 0.6-4.1 0.8-6.3 0.8 0 1.6-0.1 2.4-0.3 1.4 2.1 2.8 4 4.3 6l-7.5 0.6zM344.5 464.7c-4.2 6.7-8.2 14-12 21.7 11.7 5.6 23.9 15.5 32.8 32.8-1.6-13.9-10-27.7-15.1-39.6-2.4-5.5-4.2-10.5-5.7-14.9zM714.8 440.5l1.2 3c3.6 10 6.5 22.2 11.8 32.6 1.8-2.4 3.7-4.8 6-7.2-2.1-3.8-4.4-7.6-6.7-11.3-3.7-6.1-7.8-11.8-12.3-17.1zM464.3 373.5c1.1 1.9 2.2 4 3.3 6.1 12.2 0.6 22.9 2.1 31.2 3.7l0.2-4.1 0.7-17.2c-1.7-1.3-5.4-4.1-10.9-7.8-7.9 9.2-16.3 15.3-24.5 19.3z m25-1.8c-1.1-0.2-2.3-0.3-3.4-0.4 1.2-1 2.4-2.1 3.6-3.2l-0.2 3.6zM627.6 424.5c0.1 0 0.1-0.1 0.2-0.1 0.4-0.3 0.9-0.7 1.3-0.9-0.4-0.7-0.9-1.3-1.3-2-0.1 0.9-0.2 2-0.2 3zM586.4 389.2h-4.1c4.6 3.9 10.1 9.2 16.3 16.2 2.8 3.2 5.7 6.8 8.7 10.5-0.3-9.7 1.5-18.2 4.1-25.5-3.9-0.4-7.8-0.7-11.9-0.9-4.3-0.2-8.8-0.3-13.1-0.3zM642.7 407.7c0.7 1.8 1.5 3.6 2.2 5.5 0 0 0.1 0 0.1-0.1 4.1-2.4 8.2-4.7 12.3-6.7 0.2-1.8 0.4-3.7 0.8-5.5-6.9-2.6-14-4.7-21.6-6.4 2 3.8 4.1 8.2 6.2 13.2zM580.4 414.8c-2.9 13.2-1 28.2-1 40.6 0 4.6-0.2 8.7-0.4 12.5l0.2-0.2c4.2-4.6 8.8-9.2 13.4-13.7 6.1-5.9 12.4-11.5 18.6-16.8-0.2-0.8-0.5-1.5-0.7-2.3-9.7-3.1-20.8-9-30.1-20.1z m8.7 28.6c-0.1-2.6-0.2-5.3-0.3-7.9 1.7 1.1 3.5 2.2 5.3 3.2-1.6 1.6-3.3 3.2-5 4.7zM787.9 396.5c4.8 1.8 9.6 4 14.4 6.4 0 0 0.1 0 0.1 0.1v-0.2c-1.4-5.5-2.9-11.3-4.5-17.1v-0.2c-1.7 1.2-3.4 2.3-4.9 3.3-1.6 2.5-3.3 5-5.1 7.7zM759 374.1c6.3 2.6 11 5.6 13.8 7.5 4.4-6.3 10.3-12.4 18-18-3.3-9.4-7.1-18.7-11.4-28 0-0.1-0.1-0.1-0.1-0.2-2.1 5.1-4.8 11-8.4 17.8-3.4 6.6-8 13.6-11.9 20.9z m19.8-14.3c0.1 0.2 0.1 0.3 0.2 0.5-0.3 0.3-0.6 0.5-0.9 0.8 0.2-0.4 0.5-0.9 0.7-1.3zM566.6 389.9c-16.2 1.2-29.7 3.5-38.6 5.4l0.8 20.7v0.1l1.9 49.2 0.3 6.4 1.8 44.3v0.2l0.1 1.8v0.3l0.3 6.7v0.2c0.1-0.1 0.1-0.2 0.2-0.3 9.1-12.7 19.2-26.1 30.2-39.4-13.4-37.4 4.2-63.4 14.1-74.2-4.2-5.8-8-12.8-10.9-21.3-0.1-0.1-0.2-0.1-0.2-0.1z m-14.3 45.4c-4.9 15.4-4.9 31.5 0 48-3.4 4.2-6.8 8.5-10.3 13l-1-25.1-0.3-6.4-1.9-49.2v-0.1l-0.5-12.1c6-1.1 13.4-2.1 21.8-3 1.5 3.5 3.2 6.9 5.1 10.1-4.6 6.2-9.6 14.5-12.9 24.8zM319.8 515.8c-2.1 5.5-4.1 11-6.1 16.6 0.5 0.6 1 1.3 1.5 2 0.2-0.1 0.3-0.1 0.5-0.2 3.7-1.5 7.8-3 12.1-4.4-0.1-0.2-0.3-0.4-0.4-0.6-3.1-5-5.6-9.4-7.6-13.4zM256.5 516.2c0.9-0.5 1.8-0.9 2.7-1.4-0.8-0.5-1.6-1-2.3-1.4-0.2 1-0.3 2-0.4 2.8zM212 656.7v-0.5c-0.2 0.2-0.3 0.5-0.5 0.7 7.6 4.1 13.7 9.1 18.4 14.3 2.8-4.8 6.5-9.6 11.2-14-5.3-6.9-9.3-12.8-12.2-17.7-6.7 4.8-13 10.3-16.9 17.2z m14.4-2.2l0.3-0.3c0.2 0.3 0.5 0.7 0.7 1-0.4-0.2-0.7-0.4-1-0.7zM277.6 528.2c-2.9 1.4-6.1 2.8-9.6 4.2-6.2 2.5-13.4 4.8-20.4 7.7 5.2 3.2 10.3 7.2 15.2 12.5 4.9-1.5 10.3-2.6 16.3-3.1 1.6-5.5 3.4-11 5.2-16.4-0.4-0.3-0.8-0.5-1.1-0.8-1.9-1.3-3.7-2.7-5.6-4.1zM242.7 630.4c5.6 4.1 10.1 8.5 13.8 13 1.5-8 3.3-17.2 5.5-27.2-3.7 3.1-8 6.5-13.2 10.2-1.9 1.2-4 2.6-6.1 4zM771.9 383.1c-2.3-0.3-4.6-0.5-7-0.5-3.4 0-6.8 0.3-10.2 0.8-0.6 1.4-1.1 2.8-1.5 4.1 4.8 0.6 9.7 1.5 14.5 2.7 1.2-2.3 2.6-4.7 4.2-7.1zM771.2 319.3c-4-7.2-8.3-14.1-13-20.7l-0.1-0.1c-1.3 4.2-3 8.9-5 14-5.2 12.8-13.8 27.7-14.9 42.4 4.8-5.2 9.9-9.2 15-12.3 3.8-7.8 9.6-15.7 18-23.3zM222.1 594.8c-1.8 1.5-3.4 3.2-4.9 4.9 0 0 0.5-2.1 1.7-5.4-6.3-1-13.9-2.7-23.2-5.5-2.5-0.8-5.1-1.7-7.7-2.6-2.8 9.4-7 18.7-13.2 26.9 8.9 0.1 18.7 2 29.5 6.4 6.8-8.6 13.8-16.7 21.2-24.3-1.1-0.1-2.2-0.2-3.4-0.4zM201 607.7c-3.2-1-6.4-1.9-9.6-2.6 1-2 1.9-4.1 2.8-6.2 4 1.2 7.9 2.2 11.7 3.1-1.7 1.8-3.3 3.7-4.9 5.7zM289.9 470.2c-6.1 0-12.8-0.5-19.6-0.7-1.4 8.1-3.6 13.1-3.6 13.1-0.3-4.4-1.3-8.8-2.9-13.1-5.2 0.1-10.4 0.6-15.2 1.9 6.7 12 8.5 23.9 8.7 33.3h0.2c6.6 0 14.6 0.9 22.9 3.7 3.8-0.5 7.8-0.8 12.1-0.8h0.8c3.1-8.1 6.4-16.1 9.9-23.8-2.7-1.7-5.6-3.1-8.6-4.1 0 0 2.4-0.3 6.4-0.3 1.2 0 2.7 0 4.2 0.1 1.6-3.5 3.3-6.9 5.1-10.3-5.4 0.6-11.9 1-19.7 1h-0.7z m-3.6 27.5c-1.7 0.1-3.4 0.3-5.1 0.4-4.7-1.4-9.6-2.4-14.7-3-0.1-0.9-0.2-1.7-0.4-2.6h0.4c3.9 0 7.5-2.3 9.2-6 0.2-0.4 1.2-2.8 2.4-6.8h0.2c2 0.1 4.1 0.2 6.2 0.3 0.1 3.6 2.3 6.9 5.5 8.5-1.2 3.1-2.4 6.1-3.7 9.2z" fill="#005E5E" p-id="63139"></path><path d="M651.8 369.9c0.1 0 0.3 0.1 0.4 0.1 5.2 1.5 10.2 3.1 15.1 4.9 0.4-0.8 0.8-1.6 1.3-2.3 0 0 0.3 0.3 0.7 1.1 2.2-7 5.3-13.1 8.8-18.2-0.5 0.3-1 0.7-1.5 1-10.3 6.7-18.5 10.8-24.8 13.4zM343.1 421.6c-4.3-0.1-9-0.4-14.4-1-9.8-1-21.1-3.5-32-3.5-3.2 0-6.4 0.2-9.6 0.8-1.5 15.5-7.6 26-7.6 26 0.9-16.4-9.1-33.4-15-47.7-3-7.5-5.1-13.9-6.6-19.4-4.6 5.8-9 11.9-13.1 18.5-0.8 1.3-1.7 2.7-2.5 4.1 22.2 17.9 28.4 38.4 29 54.5 6.2-2.2 13.4-3.6 21.4-3.6 7.7 0 16.1 1.3 25.2 4.6 6.5-11.1 13.6-21 21.2-29.4 1.4-1.3 2.7-2.6 4-3.9z m-29.6 21.6c-7-1.8-13.9-2.8-20.8-2.8h-0.7c1.3-3.5 2.7-8 3.8-13.3h0.8c6.4 0 13.2 1 19.9 2 2 0.3 4 0.6 6.1 0.9-3 4.1-6.1 8.5-9.1 13.2zM243.3 562c-1.2-0.8-2.4-1.6-3.7-2.4-0.2 0.9-0.3 1.4-0.3 1.4-0.1-0.6-0.3-1.3-0.4-1.9-0.7-0.5-1.5-1-2.2-1.5-2.7-1.9-5.6-4.1-8.5-6.3-0.9 0.8-1.9 1.7-2.7 2.6 0 0 0.4-1.4 1.3-3.7-7.6-5.8-15.8-12-24.6-15.5-1.9 18.1-1.9 29.8-1.9 30 0 1.4-0.2 2.7-0.6 3.9 8.4 1.8 17.2 5.4 26.3 11.6 4-6.1 9.6-12.6 17.3-18.2z m-33-0.8c0.1-2.4 0.2-5.9 0.5-10.3 1.5 1 3 2.1 4.5 3.2 0.1 3.4 2 6.7 5.1 8.4 1.5 0.9 3.2 1.3 4.9 1.3h0.8c-0.9 1-1.9 2.1-2.8 3.1-4.1-2.3-8.5-4.2-13-5.7zM739.7 386.4c-0.1 0-0.1 0 0 0-0.1 0-0.1 0 0 0 2.7 0.1 5.2 0.3 7.8 0.5-0.1-0.7-0.3-1.4-0.4-2.1-2.5 0.5-5 1-7.4 1.6zM346.9 524.3l1.2-0.3c-0.7-0.5-1.4-1.1-2.2-1.7 0.4 0.6 0.7 1.3 1 2zM294.7 598c-2 8.4-3.9 16.4-5.5 24 11.3 5 19.6 11.4 25.6 18.3-2.4-10.8-7.2-21.5-10.4-31-3.8-4.1-7-7.9-9.7-11.3z" fill="#005E5E" p-id="63140"></path></svg>' },
          { name: '椰树', svgCode: '<svg t="1756144123653" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="64435" width="100%" height="100%"  preserveAspectRatio="xMidYMid meet"><path d="M481.43 298.84l-1.79 42.46 73.14-11.77c8.64-113.57-76.42-212.64-189.99-221.28s-211.98 67.8-220.63 181.37l74.36-41.27 14.4 38.66 79.51-51.14-13.14 58.72 100.08-36.69-15.06 58.66 99.12-17.72z" fill="#88C626" p-id="64436"></path><path d="M479.64 356.1c-3.6 0-7.11-1.31-9.83-3.74a14.798 14.798 0 0 1-4.96-11.69l1.02-24.01-80.96 14.46a14.85 14.85 0 0 1-13.45-4.5 14.797 14.797 0 0 1-3.49-13.75l8.06-31.39-73.65 27c-5.06 1.85-10.78 0.81-14.85-2.76a14.8 14.8 0 0 1-4.68-14.36l5.26-23.54-49.19 31.64c-3.77 2.42-8.42 2.99-12.68 1.59a14.862 14.862 0 0 1-9.2-8.88l-8.39-22.54-59.32 32.91a14.782 14.782 0 0 1-15.16-0.47 14.806 14.806 0 0 1-6.78-13.58c4.46-58.51 31.6-110.68 76.43-146.9 43.96-35.52 100.89-52.56 160.08-48.11 58.87 4.49 112.48 31.62 150.93 76.42 38.47 44.79 57.17 101.88 52.69 160.75-0.52 6.82-5.66 12.39-12.41 13.48l-73.13 11.77c-0.78 0.14-1.55 0.2-2.34 0.2z m1.79-72.05c3.55 0 7.02 1.28 9.74 3.66 3.38 2.94 5.23 7.28 5.05 11.77l-1.03 24.33 43.37-6.98c0.79-46.85-15.39-91.8-46.17-127.64-33.3-38.8-79.74-62.3-130.72-66.18-51.77-3.99-101.16 10.84-139.24 41.6-30.93 25-52.05 58.92-61.09 97.43l48.01-26.64c3.78-2.11 8.28-2.44 12.31-0.95 4.04 1.49 7.23 4.68 8.74 8.72l7.98 21.44 64.05-41.2c5.04-3.22 11.56-3.12 16.48 0.32 4.93 3.43 7.28 9.5 5.97 15.36l-7.21 32.27L392.28 244c5.13-1.88 10.93-0.78 15.02 2.91 4.07 3.69 5.77 9.34 4.41 14.66l-9.34 36.35 76.46-13.65c0.86-0.14 1.73-0.22 2.6-0.22z" fill="#480662" p-id="64437"></path><path d="M559.94 361.12L577.07 400l-72.4 15.68c-49.42-102.62-6.3-225.87 96.32-275.29s222.12-14.09 271.54 88.53l-84.28-11.34 0.68 41.25-92.67-18.66 33.63 49.9-106.57 2.29 35.39 49.14-98.77 19.62z" fill="#88C626" p-id="64438"></path><path d="M504.67 430.48c-5.6 0-10.83-3.18-13.33-8.38-25.62-53.19-29-113.17-9.5-168.9 19.49-55.72 59.53-100.52 112.72-126.14 53.54-25.8 112.73-30.58 166.61-13.52 54.94 17.4 99.23 56.1 124.69 108.97a14.788 14.788 0 0 1-1.36 15.11c-3.2 4.41-8.55 6.73-13.95 5.98l-67.22-9.05 0.39 24.05c0.07 4.48-1.89 8.75-5.33 11.62-3.45 2.87-8.04 3.99-12.39 3.14l-57.31-11.55 13.47 20c3.02 4.49 3.36 10.27 0.87 15.07a14.833 14.833 0 0 1-12.82 8l-78.43 1.68 18.94 26.29c2.94 4.08 3.61 9.39 1.76 14.08a14.797 14.797 0 0 1-10.89 9.09l-80.66 16.02 9.69 21.99a14.82 14.82 0 0 1-0.35 12.68 14.812 14.812 0 0 1-10.05 7.75l-72.4 15.68c-1.07 0.23-2.11 0.34-3.15 0.34zM695.79 133.1c-29.79 0-59.95 6.94-88.39 20.63-46.07 22.18-80.73 60.98-97.62 109.25-15.61 44.6-14.3 92.34 3.5 135.69l42.93-9.3-9.82-22.28c-1.81-4.11-1.66-8.82 0.41-12.81 2.07-3.98 5.84-6.81 10.24-7.68l76.18-15.13-21.93-30.45a14.802 14.802 0 0 1-1.24-15.26c2.46-4.92 7.43-8.08 12.93-8.2l79.46-1.7-18.47-27.42a14.785 14.785 0 0 1-0.04-16.49c3.34-4.99 9.31-7.45 15.24-6.29l74.63 15.03-0.37-22.87c-0.07-4.32 1.74-8.44 4.97-11.3 3.22-2.86 7.47-4.19 11.81-3.61l54.41 7.32c-22.45-32.58-54.47-56.47-92.39-68.47-18.27-5.78-37.27-8.66-56.44-8.66z" fill="#480662" p-id="64439"></path><path d="M493.65 417.54l29.75 30.34 41.44-61.4c-76.93-83.99-207.38-89.71-291.37-12.78s-95.55 201.01-18.62 285l20.76-82.47 38.05 15.94 17.08-92.97 33.85 49.75 41.69-98.1 32.49 51.11 54.88-84.42z" fill="#97E937" p-id="64440"></path><path d="M254.85 673.5c-4.09 0-8.08-1.7-10.92-4.81-80.43-87.82-71.84-222.19 19.55-305.9 43.53-39.88 100.01-60.32 158.97-57.84 58.99 2.58 113.42 27.99 153.3 71.53 4.63 5.04 5.18 12.6 1.36 18.27l-41.44 61.41c-2.49 3.69-6.5 6.06-10.93 6.46-4.43 0.37-8.8-1.2-11.91-4.38L496 441.08l-44.81 68.94c-2.73 4.2-7.4 6.74-12.41 6.74h-0.07c-5.04-0.03-9.72-2.61-12.42-6.86l-17.38-27.36-30.68 72.19a14.815 14.815 0 0 1-12.18 8.94c-5.45 0.57-10.64-1.93-13.68-6.4l-13.56-19.94-10.57 57.51a14.85 14.85 0 0 1-7.51 10.35c-3.92 2.14-8.62 2.37-12.77 0.64l-22.18-9.3-16.57 65.78a14.772 14.772 0 0 1-10.72 10.74c-1.22 0.3-2.43 0.45-3.64 0.45z m157.72-339.16c-47.96 0-93.51 17.68-129.09 50.27-71.52 65.51-84.77 166.53-35.6 241.17l13.39-53.16a14.81 14.81 0 0 1 7.72-9.63c3.87-1.93 8.37-2.08 12.34-0.41l21.1 8.84 13.75-74.9a14.807 14.807 0 0 1 11.5-11.81c5.88-1.31 11.92 1.19 15.3 6.15l18.59 27.34 31.09-73.14c2.15-5.06 6.93-8.51 12.4-8.96 5.58-0.45 10.76 2.18 13.71 6.81l20.14 31.68 42.32-65.12c2.45-3.76 6.47-6.21 10.94-6.66 4.53-0.36 8.9 1.17 12.04 4.37l17.06 17.4 24.57-36.41c-33.64-32.62-77.49-51.56-124.7-53.63-2.85-0.13-5.72-0.2-8.57-0.2z" fill="#480662" p-id="64441"></path><path d="M584.17 408.24s264.18 181.87 196.08 507.65H610.06s106.41-400.27-64.69-473.16l38.8-34.49z" fill="#7CCCF6" p-id="64442"></path><path d="M584.17 408.24s264.18 181.87 196.08 507.65H610.06s106.41-400.27-64.69-473.16l38.8-34.49m0-24.57c-5.86 0-11.7 2.09-16.33 6.2l-38.8 34.48a24.56 24.56 0 0 0-7.92 22.32 24.56 24.56 0 0 0 14.62 18.64c124.3 52.95 78.65 338.64 50.58 444.25a24.58 24.58 0 0 0 4.27 21.29 24.566 24.566 0 0 0 19.48 9.59h170.19c11.63 0 21.67-8.15 24.05-19.54 36.92-176.63-21.02-312.11-76.12-394.66C668.71 437.17 600.95 389.97 598.1 388c-4.22-2.9-9.08-4.33-13.93-4.33z" fill="#480662" p-id="64443"></path><path d="M584.17 408.24l-13.81 12.28C608.4 456.16 702.74 565.43 707.37 693c5.67 156.02-25.04 222.89-25.04 222.89h97.93c68.09-325.78-196.09-507.65-196.09-507.65z" fill="#47A1DF" p-id="64444"></path><path d="M461.1 450.06a47.78 47.78 0 1 0 95.56 0 47.78 47.78 0 1 0-95.56 0z" fill="#7CCCF6" p-id="64445"></path><path d="M508.88 402.28c26.39 0 47.78 21.39 47.78 47.78s-21.39 47.78-47.78 47.78-47.78-21.39-47.78-47.78 21.39-47.78 47.78-47.78m0-24.57c-39.89 0-72.34 32.45-72.34 72.34s32.45 72.34 72.34 72.34 72.34-32.45 72.34-72.34-32.45-72.34-72.34-72.34z" fill="#480662" p-id="64446"></path><path d="M578.83 387.54a47.78 47.78 0 1 0 95.56 0 47.78 47.78 0 1 0-95.56 0z" fill="#7CCCF6" p-id="64447"></path><path d="M626.61 339.76c26.39 0 47.78 21.39 47.78 47.78s-21.39 47.78-47.78 47.78-47.78-21.39-47.78-47.78 21.4-47.78 47.78-47.78m0-24.56c-39.89 0-72.34 32.45-72.34 72.34s32.45 72.34 72.34 72.34 72.34-32.45 72.34-72.34-32.45-72.34-72.34-72.34z" fill="#480662" p-id="64448"></path><path d="M536.39 428.48a47.78 47.78 0 1 0 95.56 0 47.78 47.78 0 1 0-95.56 0z" fill="#7CCCF6" p-id="64449"></path><path d="M584.17 380.7c26.39 0 47.78 21.39 47.78 47.78s-21.39 47.78-47.78 47.78-47.78-21.39-47.78-47.78 21.39-47.78 47.78-47.78m0-24.57c-39.89 0-72.34 32.45-72.34 72.34s32.45 72.34 72.34 72.34 72.34-32.45 72.34-72.34-32.45-72.34-72.34-72.34zM702.97 684.52h-0.19l-56.86-0.72c-8.56-0.11-15.41-7.13-15.3-15.68 0.11-8.49 7.02-15.3 15.49-15.3h0.19l56.86 0.72c8.56 0.11 15.41 7.13 15.3 15.68-0.11 8.5-7.02 15.3-15.49 15.3z m4.4 75.46h-0.19l-56.86-0.71c-8.55-0.11-15.4-7.13-15.3-15.68 0.11-8.49 7.02-15.3 15.49-15.3h0.19l56.86 0.71c8.55 0.11 15.4 7.13 15.3 15.68-0.12 8.49-7.02 15.3-15.49 15.3z m10.32 72.27h-0.14l-77.51-0.71c-8.55-0.08-15.43-7.08-15.35-15.63 0.08-8.5 7-15.35 15.49-15.35h0.14l77.51 0.71c8.55 0.08 15.43 7.08 15.35 15.63-0.08 8.5-7 15.35-15.49 15.35z" fill="#480662" p-id="64450"></path></svg>' },
          { name: '枫叶', svgCode: '<svg t="1756144227387" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="65487" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M764.354 581.144c8.512 1.037-31.47 68.793-36.119 74.272-17.811 20.553-40.396 45.918-70.288 43.635-20.427-1.577-33.96-18.392-46.873-31.469-1.785-1.869-38.236-45.171-29.561-44.257 37.822 4.026 69.583 1.245 106.741-3.571-34.46-0.166-79.132 4.69-106.033-22.627 23.497-22.003 52.6-37.156 74.479-61.029 19.639-21.464 31.843-46.914 48.657-70.081-16.814 23.167-40.022 42.057-63.728 57.667-21.797 14.24-39.772 33.837-65.597 40.146-12.87 3.073-66.053-193.551-77.802-214.517 5.647 18.226 6.976 35.206 9.631 53.971 3.903 27.235 11.625 54.595 17.147 81.624 6.228 29.809 13.493 60.033 21.962 89.137 1.121 3.86-72.571-16.398-77.512-17.979-30.515-10.17-60.656-21.256-88.888-36.66 37.614 45.96 118.033 79.175 176.737 84.488-34.334 29.186-88.058 32.3-131.566 33.67 42.928 10.297 102.256 10.919 143.233-2.74 18.682-6.27 6.476 65.182-1.204 72.988-23.415 23.664-64.477 27.359-95.199 21.629-41.433-7.722-125.09-54.471-136.673-98.686 21.505-8.469 44.505-14.655 66.261-23.126-39.15 9.302-83.159-23.83-107.321-50.484-8.22-9.049-64.518-100.802-69.541-99.764 42.389-8.511 93.704-21.796 137.255-16.19 24.163 3.112 72.861 35.538 85.648 56.296-65.306-105.826-14.281-205.716 33.712-306.187 84.944 59.992 165.404 157.391 125.464 270.067 32.466-92.915 107.197-114.877 188.777-142.9 12.289 95.654-9.508 208.954-89.927 272.806 18.481-7.97 38.118-12.579 58.128-10.129z" fill="#d81e06" p-id="65488"></path></svg>' },
          { name: '苹果', svgCode: '<svg t="1756144276757" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="66685" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M720.779947 227.6352c-50.213547 0-167.6288 29.73696-208.776534 30.979413-41.08288-2.317653-158.5664-30.979413-208.776533-30.979413-118.985387 0-223.351467 84.804267-215.453013 258.542933 7.901867 173.728427 162.358613 460.649813 274.54464 468.39808 107.85792 7.44448 101.884587-23.422293 149.684906-25.818453 47.80032 2.39616 41.8304 33.262933 149.684907 25.818453 112.182613-7.74144 266.63936-294.669653 274.54464-468.39808 7.89504-173.738667-96.467627-258.542933-215.453013-258.542933z" fill="#FF1515" p-id="66686"></path><path d="M630.7328 976.213333h-0.006827c-49.175893-0.003413-70.642347-9.9328-87.893333-17.913173-10.277547-4.758187-17.769813-8.22272-30.83264-9.03168-13.062827 0.80896-20.55168 4.276907-30.825813 9.03168-17.247573 7.983787-38.710613 17.916587-87.90016 17.916587-9.90208 0-20.790613-0.406187-32.365227-1.20832-83.841707-5.789013-162.74432-129.396053-192.774827-182.272-58.279253-102.608213-96.907947-219.716267-100.816213-305.626454-3.9936-87.845547 19.346773-160.918187 67.505493-211.31264C177.117867 231.533227 236.926293 207.1552 303.22688 207.1552c30.50496 0 80.37376 9.202347 128.597333 18.100907 32.812373 6.05184 63.83616 11.779413 80.4352 12.858026 17.373867-0.70656 52.036267-7.185067 85.572267-13.45536 46.011733-8.605013 93.5936-17.50016 122.948267-17.50016 66.300587 0 126.1056 24.378027 168.403626 68.63872 48.151893 50.394453 71.49568 123.467093 67.50208 211.316054-3.91168 85.910187-42.540373 203.021653-100.819626 305.629866-30.030507 52.875947-108.93312 176.4864-192.774827 182.268587-11.5712 0.795307-22.459733 1.201493-32.3584 1.201493zM512 908.27776c0.341333 0 0.682667 0.01024 1.024 0.027307 21.63712 1.082027 34.536107 7.048533 47.008427 12.82048 15.008427 6.946133 30.532267 14.127787 70.693546 14.1312h0.006827c8.96 0 18.899627-0.372053 29.538987-1.10592 94.767787-6.539947 247.586133-275.039573 255.494826-448.897707 3.478187-76.404053-15.957333-139.045547-56.19712-181.15584-34.491733-36.096-83.78368-55.975253-138.789546-55.975253-25.555627 0-73.29792 8.925867-115.418454 16.800426-38.90176 7.273813-72.502613 13.55776-92.736853 14.165334a19.182933 19.182933 0 0 1-1.77152-0.023894c-18.947413-1.068373-50.230613-6.84032-86.45632-13.523626-44.250453-8.164693-94.409387-17.421653-121.166507-17.421654-55.00928 0-104.301227 19.879253-138.79296 55.978667-40.239787 42.110293-59.675307 104.751787-56.200533 181.15584 7.908693 173.851307 160.730453 442.350933 255.49824 448.897707 10.63936 0.733867 20.578987 1.10592 29.545813 1.10592 40.17152 0 55.688533-7.181653 70.69696-14.127787 12.468907-5.771947 25.36448-11.738453 47.005014-12.823893 0.334507-0.017067 0.67584-0.027307 1.017173-0.027307z" fill="#CC0202" p-id="66687"></path><path d="M186.79808 502.766933c3.82976 84.230827 52.933973 203.424427 110.14144 280.378027" fill="#FF2C2C" p-id="66688"></path><path d="M296.956587 803.628373a20.445867 20.445867 0 0 1-16.452267-8.260266c-62.276267-83.770027-110.291627-206.434987-114.16576-291.669334a20.48 20.48 0 0 1 19.52768-21.387946c11.322027-0.546133 20.875947 8.229547 21.387947 19.52768 3.488427 76.721493 49.11104 192.406187 106.120533 269.08672a20.48 20.48 0 0 1-16.418133 32.703146z" fill="#FFFFFF" p-id="66689"></path><path d="M254.47424 329.782613c-17.32608 10.693973-32.600747 25.012907-44.868267 43.001174" fill="#FF2C2C" p-id="66690"></path><path d="M209.588907 393.263787a20.48 20.48 0 0 1-16.90624-32.017067c13.58848-19.930453 30.76096-36.38272 51.032746-48.892587a20.48 20.48 0 0 1 21.510827 34.85696c-15.34976 9.472-28.371627 21.957973-38.700373 37.10976a20.456107 20.456107 0 0 1-16.93696 8.942934z" fill="#FFFFFF" p-id="66691"></path><path d="M599.48032 123.613867c-59.026773 52.33664-83.182933 129.324373-70.806187 201.755306 70.43072 20.944213 149.74976 6.161067 208.769707-46.1824 59.026773-52.343467 83.176107-129.324373 70.806187-201.755306-70.437547-20.944213-149.756587-6.167893-208.769707 46.1824z" fill="#3A960F" p-id="66692"></path><path d="M591.69792 355.013973h-0.013653c-23.3472 0-46.51008-3.36896-68.846934-10.01472a20.48 20.48 0 0 1-14.349653-16.1792c-14.114133-82.599253 14.824107-165.03808 77.407573-220.52864A239.889067 239.889067 0 0 1 745.229653 47.786667c23.343787 0 46.513493 3.36896 68.857174 10.01472a20.48 20.48 0 0 1 14.349653 16.182613c14.107307 82.599253-14.830933 165.03808-77.407573 220.52864a239.936853 239.936853 0 0 1-159.330987 60.501333z m-44.622507-45.974186c14.609067 3.331413 29.56288 5.0176 44.608854 5.0176h0.01024a199.010987 199.010987 0 0 0 132.15744-50.189654c48.66048-43.147947 72.79616-105.949867 65.989973-170.100053a200.454827 200.454827 0 0 0-44.612267-5.0176 198.987093 198.987093 0 0 0-132.160853 50.189653c-48.66048 43.147947-72.802987 105.949867-65.993387 170.100054z" fill="#0F5108" p-id="66693"></path><path d="M517.60128 369.363627c15.45216-156.736853-42.089813-241.169067-42.089813-241.169067" fill="#7CBC00" p-id="66694"></path><path d="M517.62176 389.843627a20.48 20.48 0 0 1-20.404907-22.490454c14.434987-146.397867-38.144-226.901333-38.679893-227.69664-6.270293-9.373013-3.812693-22.08768 5.533013-28.398933a20.43904 20.43904 0 0 1 28.361387 5.403307c2.51904 3.69664 61.545813 92.443307 45.544107 254.713173a20.473173 20.473173 0 0 1-20.353707 18.469547z" fill="#915823" p-id="66695"></path></svg>' },
          { name: '樱花', svgCode: '<svg t="1756144381436" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="70325" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M511.98406339 633.68974867m-20.31579308 0a20.31579309 20.31579309 0 1 0 40.63158615 0 20.31579309 20.31579309 0 1 0-40.63158615 0Z" fill="#FC99CB" p-id="70326"></path><path d="M725.997 670.33999998c68.496-22.256 103.965-61.99 121.268-105.916-22.534-10.632-38.477-23.387-38.477-23.387s5.739-20.921 18.508-43.561c-39.623-24.914-93.883-41.807-163.682-19.128-37.446 12.167-66.625 39.783-87.982 67.998 19.952-28.873 36.831-64.805 36.831-103.756 0-74.261-28.522-120.873-66.684-150.822-17.099 18.19-34.203 29.442-34.203 29.442s-16.155-10.629-32.76-27.925c-35.725 29.999-68.225 76.287-68.225 149.305 0 39.373 17.248 75.658 37.482 104.689-21.295-27.898-50.251-55.054-87.297-67.091-71.514-23.236-125.102-9.898-165.557 17.842 10.626 20.353 15.445 37.914 15.445 37.914s-14.153 11.321-34.636 21.523c17.039 44.342 50.944 91.506 122.366 114.712 37.426 12.16 77.241 6.981 111.091-3.28-33.096 11.634-67.845 30.78-90.727 62.275-43.228 59.499-47.883 113.5-35.079 159.859 21.414-3.33 38.222-2.549 38.222-2.549s6.93 18.387 10.166 42.419c48.112-1.893 104.903-18.989 150.008-81.072 23.143-31.854 30.516-71.346 31.211-106.725 0.83 35.086 8.294 74.076 31.189 105.588 42.066 57.899 90.469 79.453 137.316 82.55 3.372-22.643 9.769-39.613 9.769-39.613s21.878-1.015 47.512 4.216c12.563-46.056 13.208-104.578-31.28-165.811-23.108-31.806-58.321-51.02-91.709-62.619 33.596 10.025 72.923 14.942 109.914 2.923zM571.72 588.53699998c4.801-2.772 10.94-1.127 13.711 3.674 2.772 4.801 1.127 10.94-3.674 13.711-4.562 2.634-10.327 1.273-13.268-2.988l-49.783 28.742-0.813-1.408 49.782-28.742c-2.222-4.677-0.519-10.354 4.045-12.989z m-31.125-23.712c2.772-4.801 8.911-6.446 13.711-3.674s6.446 8.911 3.674 13.711c-2.634 4.562-8.306 6.266-12.984 4.046l-28.535 49.424-1.408-0.813 28.535-49.423c-4.265-2.939-5.628-8.707-2.993-13.271zM511.76 549.87999998c5.543 0 10.037 4.494 10.037 10.037 0 5.268-4.061 9.58-9.221 9.996v57.031h-1.626v-57.031c-5.164-0.413-9.228-4.726-9.228-9.997 0.001-5.542 4.495-10.036 10.038-10.036z m-42.401 11.361c4.801-2.772 10.94-1.127 13.711 3.674 2.634 4.562 1.273 10.327-2.988 13.268l28.528 49.413-1.408 0.813-28.528-49.413c-4.679 2.224-10.355 0.521-12.99-4.043-2.77-4.802-1.125-10.94 3.675-13.712z m-31.06 31.125c2.772-4.801 8.911-6.446 13.711-3.674 4.562 2.634 6.266 8.306 4.046 12.984l49.763 28.731-0.803 1.392v0.022l-49.773-28.736c-2.94 4.265-8.707 5.628-13.271 2.993-4.799-2.772-6.444-8.911-3.673-13.712z m-11.335 42.486c0-5.544 4.494-10.037 10.037-10.037 5.268 0 9.58 4.06 9.996 9.221h58.02v1.451l0.101 0.175h-58.121c-0.413 5.164-4.726 9.228-9.997 9.228-5.543-0.001-10.036-4.495-10.036-10.038z m25.136 46.135c-4.801 2.772-10.94 1.127-13.711-3.674-2.772-4.801-1.127-10.94 3.674-13.711 4.562-2.634 10.327-1.273 13.268 2.988l50.733-29.291 0.797 1.381 0.031 0.018-50.748 29.3c2.224 4.678 0.521 10.354-4.044 12.989z m31.126 23.712c-2.772 4.801-8.911 6.446-13.711 3.674-4.801-2.772-6.446-8.911-3.674-13.711 2.634-4.562 8.306-6.266 12.984-4.046l29.498-51.092 1.408 0.813-29.498 51.092c4.265 2.939 5.628 8.706 2.993 13.27zM512 719.70899998c-5.543 0-10.037-4.494-10.037-10.037 0-5.268 4.061-9.58 9.221-9.996v-59.152h1.626v59.152c5.164 0.413 9.228 4.726 9.228 9.997-0.001 5.542-4.495 10.036-10.038 10.036z m42.461-11.425c-4.801 2.772-10.94 1.127-13.711-3.674-2.634-4.562-1.273-10.327 2.988-13.268l-29.504-51.103 1.408-0.813 29.504 51.103c4.679-2.224 10.355-0.521 12.99 4.043 2.771 4.801 1.126 10.94-3.675 13.712z m31.06-31.126c-2.772 4.801-8.911 6.446-13.711 3.674-4.562-2.634-6.266-8.306-4.046-12.984l-50.752-29.302 0.813-1.408 50.752 29.302c2.94-4.265 8.707-5.628 13.271-2.993 4.8 2.771 6.445 8.91 3.673 13.711z m1.299-32.448c-5.268 0-9.58-4.061-9.996-9.221h-58.047l0.002-0.003v-1.623h58.045c0.413-5.164 4.726-9.228 9.997-9.228 5.544 0 10.037 4.494 10.037 10.037-0.001 5.544-4.495 10.038-10.038 10.038z" fill="#FFC0CB" p-id="70327"></path></svg>' },
          { name: '竹子', svgCode: '<svg t="1756144414125" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="71654" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M528.406 66.185h97.912S614.8 123.781 614.8 164.098s4.32 135.829 10.56 181.425h-97.913s13.418-103.742 12.477-183.585c-0.359-30.598-11.518-95.753-11.518-95.753zM528.406 372.882h97.912S614.8 430.477 614.8 470.795c0 40.316 4.32 135.826 10.56 181.425h-97.913s13.418-103.745 12.477-183.586c-0.359-30.598-11.518-95.752-11.518-95.752zM528.406 678.137h97.912S614.8 735.734 614.8 776.05c0 40.316 4.32 135.827 10.56 181.426h-97.913s13.418-103.746 12.477-183.586c-0.359-30.598-11.518-95.753-11.518-95.753zM390.178 678.137h97.913s-11.52 57.597-11.52 97.913c0 40.316 4.32 135.827 10.56 181.426h-97.913s13.418-103.746 12.478-183.586c-0.359-30.598-11.518-95.753-11.518-95.753zM387.298 450.158h100.793s-11.52 41.366-11.52 70.321c0 28.959 1.44 78.466 9.601 129.823h-95.034s8.618-76.09 7.678-133.432c-0.36-21.976-11.518-66.712-11.518-66.712zM773.187 571.107s12.477-76.797 68.152-107.512c55.678-30.717 116.154-68.155 116.154-68.155s-9.6 70.073-77.754 131.51c-68.152 61.437-106.552 44.157-106.552 44.157zM705.035 621.983s46.075-18.242 77.753-14.399c31.678 3.841 120.95 41.275 129.591 45.114 0 0-79.677 39.358-154.552 11.52-74.875-27.837-52.792-42.235-52.792-42.235zM723.27 401.2s-25.918 103.673-28.798 128.63c-2.88 24.955 18.239 63.353 31.676 71.993 0 0 38.398-20.158 32.64-79.672-5.759-59.517-25.917-108.472-35.518-120.952z" fill="#00AA00" p-id="71655"></path><path d="M620.2 668.778l160.664-104.392 7.442 5.282-161.628 107.03zM378.12 251.564s-9.232-77.251-63.566-110.285c-54.335-33.037-113.178-72.985-113.178-72.985s6.641 70.415 72.147 134.668c65.506 64.248 104.596 48.602 104.596 48.602zM444.071 305.265s-45.267-20.164-77.077-17.66c-31.813 2.502-122.583 36.145-131.374 39.619 0 0 77.944 42.675 153.924 18.015 75.98-24.657 54.527-39.974 54.527-39.974zM435.146 83.912s21.532 104.67 23.36 129.728c1.825 25.054-20.892 62.53-34.684 70.595 0 0-37.514-21.755-29.253-80.977 8.26-59.22 30.464-107.284 40.577-119.346z" fill="#00AA00" p-id="71656"></path><path d="M541.191 366.045l-170.46-121.517-7.655 4.962 172.052 123.392zM244.177 602.254s-20.4-63.572-71.574-82.527C121.43 500.778 65.33 476.74 65.33 476.74s17.1 58.236 82.787 101.661c65.684 43.423 96.059 23.853 96.059 23.853zM308.513 636.719s-41.43-9.59-67.818-2.285c-26.392 7.307-97.364 50.481-104.203 54.846 0 0 72.638 23.215 132.617-9.979 59.98-33.183 39.404-42.582 39.404-42.582zM264.823 451.696S300.065 536.36 305.7 557.17c5.631 20.804-7.38 56.09-17.682 65.137 0 0-35.158-12.197-37.877-63.44-2.718-51.24 8.133-95.357 14.682-107.172z" fill="#00AA00" p-id="71657"></path><path d="M400.264 672.051l-163.46-74.52-5.64 5.435L396.272 678.8z" fill="#00AA00" p-id="71658"></path></svg>' },
          { name: '树', svgCode: '<svg t="1756144626827" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="89107" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M760.5 568.6l-37-46.9-162.5 128V421.8H449.9v306.3L301.1 606.8l-37.8 46.3 186.6 152.2v128H561V725.9z" fill="#D68231" p-id="89108"></path><path d="M301.1 606.8l-37.8 46.4 83.9 68.4c18.5-10.1 32.8-25.8 40.1-44.5l-86.2-70.3zM723.5 521.7l-88 69.3c6.3 19.2 19.9 35.5 37.9 46.3l87.2-68.7-37.1-46.9zM449.9 421.8v187.8c18.2 2.5 36.8 3.8 55.5 3.8 18.8 0 37.3-1.3 55.5-3.8V421.8h-111z" fill="" p-id="89109"></path><path d="M207.2 316a298.3 250.7 0 1 0 596.6 0 298.3 250.7 0 1 0-596.6 0Z" fill="#00AD68" p-id="89110"></path><path d="M648.4 545.1a93.6 84.8 0 1 0 187.2 0 93.6 84.8 0 1 0-187.2 0Z" fill="#7CDFA8" p-id="89111"></path><path d="M188.6 630a93.6 84.8 0 1 0 187.2 0 93.6 84.8 0 1 0-187.2 0Z" fill="#218649" p-id="89112"></path><path d="M648.1 921.9c0-10.3-8.4-18.7-18.7-18.7H381.5c-10.3 0-18.7 8.4-18.7 18.7v18.7c0 10.3 8.4 18.7 18.7 18.7h247.9c10.3 0 18.7-8.4 18.7-18.7v-18.7z" fill="#218649" p-id="89113"></path><path d="M377.8 391.3c-16.7-16.7-71.2-33.3-73.9-30.5-2.8 2.8 13.8 57.2 30.5 73.9 16.7 16.7 40 20.5 52 8.5 11.9-11.9 8.1-35.2-8.6-51.9z" fill="#7CDFA8" p-id="89114"></path><path d="M616.2 414.6c16.7-16.7 33.3-71.2 30.5-73.9-2.8-2.8-57.2 13.8-73.9 30.5-16.7 16.7-20.5 40-8.5 52 11.9 11.9 35.2 8.1 51.9-8.6zM471.1 220.7c0-23.6-26.8-73.9-30.7-73.9-3.9 0-30.7 50.2-30.7 73.9s13.7 42.8 30.7 42.8 30.7-19.2 30.7-42.8z" fill="#218649" p-id="89115"></path><path d="M681.1 267.6c16.7-16.7 33.3-71.2 30.5-73.9-2.8-2.8-57.2 13.8-73.9 30.5-16.7 16.7-20.5 40-8.5 52 11.9 11.9 35.2 8.1 51.9-8.6z" fill="#7CDFA8" p-id="89116"></path></svg>' },
          { name: '圣诞树', svgCode: '<svg t="1756145154828" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="94173" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M435.94752 768m20.48 0l102.4 0q20.48 0 20.48 20.48l0 81.92q0 20.48-20.48 20.48l-102.4 0q-20.48 0-20.48-20.48l0-81.92q0-20.48 20.48-20.48Z" fill="#914C12" p-id="94174"></path><path d="M527.36 208.60928a30.72 30.72 0 0 1 3.80928 3.81952l149.22752 178.10432a30.72 30.72 0 0 1-23.552 50.45248h-19.97824l104.97024 125.27616a30.72 30.72 0 0 1-23.552 50.45248H672.5632l110.2336 131.55328a30.72 30.72 0 0 1-23.552 50.45248H256a30.72 30.72 0 0 1-23.552-50.45248l110.2336-131.56352H296.96a30.72 30.72 0 0 1-23.552-50.44224l104.96-125.2864H358.4a30.72 30.72 0 0 1-23.552-50.44224l149.22752-178.10432a30.72 30.72 0 0 1 43.27424-3.81952z" fill="#0FBA68" p-id="94175"></path><path d="M553.70752 640m-25.6 0a25.6 25.6 0 1 0 51.2 0 25.6 25.6 0 1 0-51.2 0Z" fill="#ABE4FE" p-id="94176"></path><path d="M461.54752 506.88m-25.6 0a25.6 25.6 0 1 0 51.2 0 25.6 25.6 0 1 0-51.2 0Z" fill="#ABE4FE" p-id="94177"></path><path d="M435.2512 274.1248a20.48 20.48 0 0 1 27.136 10.11712c37.6832 82.41152 85.67808 120.99584 146.39104 119.36768l3.29728-0.14336 0.2048-0.03072a204.4928 204.4928 0 0 1 24.9856-3.67616l4.02432-0.33792c25.40544-1.98656 30.88384 34.94912 6.00064 40.41728-7.96672 1.75104-15.79008 3.03104-23.47008 3.82976l-5.98016 0.52224-0.512 0.13312a60.54912 60.54912 0 0 0-4.8128 1.4336l-1.34144 0.49152-0.02048 0.11264c-25.856 100.32128-89.43616 157.00992-187.56608 169.53344l-4.95616 0.57344 1.5872 1.57696c92.2624 90.7264 205.42464 133.8368 340.736 129.72032l6.4512-0.22528a20.48 20.48 0 0 1 1.6896 40.91904c-158.84288 6.5536-291.54304-47.2064-396.52352-160.73728l-3.01056-3.28704-0.4608-0.28672c-2.85696-1.64864-9.13408-3.8912-18.35008-6.0416l-2.36544-0.52224-1.66912-0.3584-1.15712-0.07168a549.84704 549.84704 0 0 1-51.32288-6.62528l-5.35552-0.96256c-25.57952-4.7104-20.48-42.752 5.43744-40.5504 20.5824 1.75104 38.0416 3.86048 52.61312 6.49216l6.48192 1.23904 1.47456 0.11264c117.248 7.94624 187.06432-36.39296 214.76352-133.9392l0.512-1.8432-3.15392-0.7168c-57.2928-13.568-104.31488-59.10528-139.86816-134.77888l-1.9968-4.31104a20.48 20.48 0 0 1 10.10688-27.136z" fill="#09A456" p-id="94178"></path><path d="M507.62752 194.56m-71.68 0a71.68 71.68 0 1 0 143.36 0 71.68 71.68 0 1 0-143.36 0Z" fill="#FC9A24" p-id="94179"></path></svg>'}
        ]
      },
      {
        subItems: [
          { name: '人', svgCode: '<!-- 开发者可在此处插入人SVG代码 -->' },
        ]
      },
    ]
  }
])

// 显示工具菜单
const showToolMenu = ref(false)
const highlightedItem = ref(null)

// 右侧选择面板相关状态
const showSelectionPanel = ref(false)
const selectedCategoryName = ref('')
const selectedItems = ref([])

// 打开选择面板
const openSelectionPanel = (categoryName, items) => {
  selectedCategoryName.value = categoryName
  selectedItems.value = items
  showSelectionPanel.value = true
}

// 关闭选择面板
const closeSelectionPanel = () => {
  showSelectionPanel.value = false
}

// 选择项目
const selectItem = (item) => {
  addSvgElement(item, canvasRef.value.width / 2, canvasRef.value.height / 2)
  closeSelectionPanel()
}

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
        // 设置SVG颜色
        svgElement.style.fill = element.color

        // 确保SVG元素使用100%的宽高，并保持宽高比
        svgElement.setAttribute('width', '100%')
        svgElement.setAttribute('height', '100%')
        svgElement.setAttribute('preserveAspectRatio', 'xMidYMid meet')

        // 设置容器大小
        tempSvg.style.width = `${element.width}px`
        tempSvg.style.height = `${element.height}px`

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

    // 创建全新的数组实例，彻底断开与之前历史记录的引用关系
    // 这是关键修复：使用新数组实例而不是清空现有数组
    undoStack.value = new Array()
    redoStack.value = new Array()

    // 确保清空画布是一个完全重置的操作
    console.log('画布已清空，历史记录已完全重置')
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

/* 右侧选择面板样式 */
.selection-sidebar {
  position: absolute;
  right: 36px;
  top: 64px;
  width: 180px;
  max-height: calc(100% - 128px);
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 999;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow-y: auto;
  animation: slide-in 0.28s cubic-bezier(.4, 1.4, .6, 1);
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.selection-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
}

.selection-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.selection-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.selection-item:hover {
  background: #f3f4f6;
  transform: translateY(-2px);
}

.item-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.item-name {
  font-size: 12px;
  color: #666;
  text-align: center;
}

@keyframes slide-in {
  from {
    right: -200px;
    opacity: 0;
  }
  to {
    right: 36px;
    opacity: 1;
  }
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

/* SVG素材库样式 */
.svg-library {
  position: absolute;
  left: 36px;
  top: 64px;
  width: 140px;
  min-height: calc(100% - 128px);
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 18px 12px 18px 12px;
  animation: svg-slide-in-canvas 0.28s cubic-bezier(.4, 1.4, .6, 1);
}

@keyframes svg-slide-in-canvas {
  from {
    left: -180px;
    opacity: 0;
  }

  to {
    left: 36px;
    opacity: 1;
  }
}

.svg-category {
  margin-bottom: 16px;
  width: 100%;
}

.svg-category h3 {
  font-weight: bold;
  font-size: 16px;
  margin: 0 0 14px 0;
  color: #333;
  text-align: center;
}

.svg-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.svg-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.18s, border-color 0.18s;
}

.svg-item:hover {
  transform: scale(1.08);
  border-color: #8b5cf6;
  background: white;
}

.svg-item svg {
  width: 32px;
  height: 32px;
}

.svg-item span {
  font-size: 13px;
  margin-top: 4px;
  color: #666;
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
