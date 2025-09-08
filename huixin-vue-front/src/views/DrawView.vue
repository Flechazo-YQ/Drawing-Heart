
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
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M17 21v-8H7v8" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 3v5h8" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <!-- 前往分析按钮 -->
            <button class="toolbar-btn"
              :disabled="!hasSavedImage"
              @click="goToAnalysis"
              title="前往分析">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                  :stroke="hasSavedImage ? '#333' : '#ccc'"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"/>
                <circle cx="12" cy="12" r="3"
                  :fill="hasSavedImage ? '#4f46e5' : '#e5e7eb'"/>
                <path d="M9 12l2 2 4-4"
                  :stroke="hasSavedImage ? 'white' : '#ccc'"
                  stroke-width="1"
                  stroke-linecap="round"
                  stroke-linejoin="round"/>
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
            <button class="toolbar-btn" @click="openSelectionPanel('房', svgCategories[0].items[0].subItems)" title="房">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M3 21h18v-3H3v3zm3-6h12v-3H6v3zm-3-7l9-4 9 4v2H3V8z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="openSelectionPanel('树', svgCategories[0].items[1].subItems)" title="树">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 3L8 10H16L12 3z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 10L6 16H18L14 10" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 21V16" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="toolbar-btn" @click="openSelectionPanel('人', svgCategories[0].items[2].subItems)" title="人">
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
          <div v-if="currentMode === 'collage'" ref="svgCanvasRef" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10;"></div>
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
// 拼贴元素列表
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { SVG } from 'svg.js';
import '@svgdotjs/svg.draggable.js';

import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import config from '@/config'
import NavBarUser from '@/components/NavBarUser.vue'

import { reactive } from 'vue'

const collageElements = ref([]); // [{svgCode, x, y, width, height, rotate, id}]
const selectedElement = ref(null);
let svgDraw = null;

// 绘画内容备份 - 用于在拼贴模式下保持绘画内容
const drawingCanvasBackup = ref(null);

onMounted(() => {
  if (svgCanvasRef.value && !svgDraw) {
    svgDraw = SVG().addTo(svgCanvasRef.value).size('100%', '100%');
    redrawCollageElements();
  }
});

const svgCanvasRef = ref(null)
// ...existing code...

// ...existing code...

function addControlHandles(svgNode, el) {
  // 删除按钮
  const delBtn = svgDraw.circle(24).fill('#ff4d4f').stroke({ width: 2, color: '#fff' });
  delBtn.move(svgNode.x() + svgNode.width() - 12, svgNode.y() - 12);
  delBtn.attr('cursor', 'pointer');
  delBtn.on('click', () => {
    collageElements.value = collageElements.value.filter(e => e.id !== el.id);
    selectedElement.value = null;
    saveCollageState();
    redrawCollageElements();
  });
  // 缩放按钮
  const scaleBtn = svgDraw.circle(20).fill('#1890ff').stroke({ width: 2, color: '#fff' });
  scaleBtn.move(svgNode.x() + svgNode.width() - 10, svgNode.y() + svgNode.height() - 10);
  scaleBtn.attr('cursor', 'nwse-resize');
  let scaling = false;
  let startX = 0, startY = 0, startW = 0, startH = 0;
  scaleBtn.on('mousedown', (e) => {
    scaling = true;
    startX = e.clientX;
    startY = e.clientY;
    startW = svgNode.width();
    startH = svgNode.height();
    document.addEventListener('mousemove', scaleMove);
    document.addEventListener('mouseup', scaleUp);
  });
  function scaleMove(e) {
    if (!scaling) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    el.width = Math.max(20, startW + dx);
    el.height = Math.max(20, startH + dy);
    redrawCollageElements();
  }
  function scaleUp() {
    scaling = false;
    document.removeEventListener('mousemove', scaleMove);
    document.removeEventListener('mouseup', scaleUp);
    // 缩放完成后保存状态
    if (currentMode.value === 'collage') {
      saveCollageState();
    }
  }
}

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
  if (currentMode.value === 'collage' && canvasRef.value) {
    const rect = canvasRef.value.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // 如果处于拖拽准备状态，检查是否应该开始实际拖拽
    if (isDragReady.value && !isDragging.value && dragType && dragStart) {
      const threshold = 3; // 移动超过3像素才开始拖拽
      const dx = Math.abs(x - dragStart.mouseX);
      const dy = Math.abs(y - dragStart.mouseY);

      if (dx > threshold || dy > threshold) {
        isDragging.value = true;
      }
    }    // 如果正在拖拽，执行拖拽逻辑
    if (isDragging.value && dragType === 'move' && selectedElement.value) {
      // 移动元素
      selectedElement.value.x = x - dragStartX
      selectedElement.value.y = y - dragStartY

      // 边界检测
      if (selectedElement.value.x < 0) selectedElement.value.x = 0
      if (selectedElement.value.y < 0) selectedElement.value.y = 0
      if (selectedElement.value.x + selectedElement.value.width > canvasRef.value.width) {
        selectedElement.value.x = canvasRef.value.width - selectedElement.value.width
      }
      if (selectedElement.value.y + selectedElement.value.height > canvasRef.value.height) {
        selectedElement.value.y = canvasRef.value.height - selectedElement.value.height
      }

      redrawCollageElementsThrottled()
      return
    } else if (isDragging.value && dragType && selectedElement.value && dragStart) {
      // 调整大小逻辑
      const el = selectedElement.value;
      const dx = x - dragStart.mouseX; // 使用鼠标位置计算偏移
      const dy = y - dragStart.mouseY; // 使用鼠标位置计算偏移

      switch (dragType) {
        case 'n':
          // 上边：只调整上边和高度
          const nNewHeight = dragStart.height - dy;
          if (nNewHeight >= 10) {
            el.y = dragStart.y + dy;
            el.height = nNewHeight;
          } else {
            el.y = dragStart.y + dragStart.height - 10;
            el.height = 10;
          }
          break;
        case 's':
          // 下边：只调整高度
          const sNewHeight = dragStart.height + dy;
          if (sNewHeight >= 10) {
            el.height = sNewHeight;
          } else {
            el.height = 10;
          }
          break;
        case 'w':
          // 左边：调整左边和宽度
          const wNewWidth = dragStart.width - dx;
          if (wNewWidth >= 10) {
            el.x = dragStart.x + dx;
            el.width = wNewWidth;
          } else {
            el.x = dragStart.x + dragStart.width - 10;
            el.width = 10;
          }
          break;
        case 'e':
          // 右边：只调整宽度
          const eNewWidth = dragStart.width + dx;
          if (eNewWidth >= 10) {
            el.width = eNewWidth;
          } else {
            el.width = 10;
          }
          break;
        case 'nw':
          // 左上角：同时调整位置和尺寸
          const nwNewWidth = dragStart.width - dx;
          const nwNewHeight = dragStart.height - dy;

          // 确保宽度和位置都正确更新
          if (nwNewWidth >= 10) {
            el.x = dragStart.x + dx;
            el.width = nwNewWidth;
          } else {
            // 当宽度达到最小值时，x应该是原始右边位置减去最小宽度
            el.x = dragStart.x + dragStart.width - 10;
            el.width = 10;
          }

          // 确保高度和位置都正确更新
          if (nwNewHeight >= 10) {
            el.y = dragStart.y + dy;
            el.height = nwNewHeight;
          } else {
            // 当高度达到最小值时，y应该是原始底边位置减去最小高度
            el.y = dragStart.y + dragStart.height - 10;
            el.height = 10;
          }
          break;
        case 'ne':
          // 右上角：调整右边和上边
          const neNewWidth = dragStart.width + dx;
          const neNewHeight = dragStart.height - dy;

          // 确保宽度正确更新
          if (neNewWidth >= 10) {
            el.width = neNewWidth;
          } else {
            el.width = 10;
          }

          // 确保高度和位置正确更新
          if (neNewHeight >= 10) {
            el.y = dragStart.y + dy;
            el.height = neNewHeight;
          } else {
            // 当高度达到最小值时，y应该是原始底边位置减去最小高度
            el.y = dragStart.y + dragStart.height - 10;
            el.height = 10;
          }
          break;
        case 'sw':
          // 左下角：调整左边和下边
          const swNewWidth = dragStart.width - dx;
          const swNewHeight = dragStart.height + dy;

          // 确保宽度和位置都正确更新
          if (swNewWidth >= 10) {
            el.x = dragStart.x + dx;
            el.width = swNewWidth;
          } else {
            el.x = dragStart.x + dragStart.width - 10;
            el.width = 10;
          }

          // 确保高度正确更新
          if (swNewHeight >= 10) {
            el.height = swNewHeight;
          } else {
            el.height = 10;
          }
          break;
        case 'se':
          // 右下角：调整宽度和高度
          const seNewWidth = dragStart.width + dx;
          const seNewHeight = dragStart.height + dy;

          // 确保宽度正确更新
          if (seNewWidth >= 10) {
            el.width = seNewWidth;
          } else {
            el.width = 10;
          }

          // 确保高度正确更新
          if (seNewHeight >= 10) {
            el.height = seNewHeight;
          } else {
            el.height = 10;
          }
          break;
        case 'rotate':
          // 旋转逻辑：计算元素中心点到鼠标的角度
          const centerX = dragStart.x + dragStart.width / 2;
          const centerY = dragStart.y + dragStart.height / 2;

          // 计算起始角度（从中心点到拖拽开始点的角度）
          const startAngle = Math.atan2(dragStart.mouseY - centerY, dragStart.mouseX - centerX);

          // 计算当前角度（从中心点到当前鼠标位置的角度）
          const currentAngle = Math.atan2(y - centerY, x - centerX);

          // 计算角度差并转换为度数
          const angleDiff = (currentAngle - startAngle) * (180 / Math.PI);

          // 更新元素的旋转角度
          el.rotation = (dragStart.rotation + angleDiff) % 360;

          // 确保旋转角度在0-360度范围内
          if (el.rotation < 0) {
            el.rotation += 360;
          }
          break;
      }

      redrawCollageElementsThrottled()
      return
    }

    // 如果有选中元素，检查鼠标位置并设置光标样式
    if (selectedElement.value) {
      const el = selectedElement.value;

      // 控制点定义
      const points = [
        { x: el.x - 4, y: el.y - 4, type: 'nw' },
        { x: el.x + el.width / 2 - 4, y: el.y - 4, type: 'n' },
        { x: el.x + el.width - 4, y: el.y - 4, type: 'ne' },
        { x: el.x - 4, y: el.y + el.height / 2 - 4, type: 'w' },
        { x: el.x + el.width - 4, y: el.y + el.height / 2 - 4, type: 'e' },
        { x: el.x - 4, y: el.y + el.height - 4, type: 'sw' },
        { x: el.x + el.width / 2 - 4, y: el.y + el.height - 4, type: 's' },
        { x: el.x + el.width - 4, y: el.y + el.height - 4, type: 'se' }
      ];

      // 检查是否在控制点上（使用本地坐标系统）
      const localCoords = getLocalCoordinates(x, y, el);
      let found = null;
      for (let i = 0; i < points.length; i++) {
        const pt = points[i];
        if (localCoords.x >= pt.x && localCoords.x <= pt.x + 8 &&
            localCoords.y >= pt.y && localCoords.y <= pt.y + 8) {
          found = pt.type;
          break;
        }
      }

      // 边框线判定（±4px范围）
      let onBorder = false;
      if (!found) {
        // 上边
        if (y >= el.y - 4 && y <= el.y + 4 && x >= el.x - 4 && x <= el.x + el.width + 4) onBorder = 'n';
        // 下边
        if (y >= el.y + el.height - 4 && y <= el.y + el.height + 4 && x >= el.x - 4 && x <= el.x + el.width + 4) onBorder = 's';
        // 左边
        if (x >= el.x - 4 && x <= el.x + 4 && y >= el.y - 4 && y <= el.y + el.height + 4) onBorder = 'w';
        // 右边
        if (x >= el.x + el.width - 4 && x <= el.x + el.width + 4 && y >= el.y - 4 && y <= el.y + el.height + 4) onBorder = 'e';
      }

      // 检查旋转控制点
      const rotatePoint = {
        x: el.x + el.width / 2 - 5,
        y: el.y - 20 - 5,
        width: 10,
        height: 10
      };

      let onRotatePoint = false;
      if (localCoords.x >= rotatePoint.x && localCoords.x <= rotatePoint.x + rotatePoint.width &&
          localCoords.y >= rotatePoint.y && localCoords.y <= rotatePoint.y + rotatePoint.height) {
        onRotatePoint = true;
      }

      if (found) {
        // 角点等比缩放
        if (['nw','ne','sw','se'].includes(found)) {
          if (found === 'nw' || found === 'se') {
            canvasRef.value.style.cursor = 'nwse-resize';
          } else {
            canvasRef.value.style.cursor = 'nesw-resize';
          }
        } else {
          // 边点非等比缩放
          if (found === 'n' || found === 's') {
            canvasRef.value.style.cursor = 'ns-resize';
          } else {
            canvasRef.value.style.cursor = 'ew-resize';
          }
        }
      } else if (onRotatePoint) {
        // 旋转控制点
        canvasRef.value.style.cursor = 'grab';
      } else if (onBorder) {
        // 边框线也可缩放
        if (onBorder === 'n' || onBorder === 's') {
          canvasRef.value.style.cursor = 'ns-resize';
        } else {
          canvasRef.value.style.cursor = 'ew-resize';
        }
      } else if (x > el.x && x < el.x + el.width && y > el.y && y < el.y + el.height) {
        // 框内可抓取
        canvasRef.value.style.cursor = 'move';
      } else {
        canvasRef.value.style.cursor = 'default';
      }
    } else {
      // 检查鼠标是否悬停在任何元素上，即使没有选中元素
      const sortedElements = [...collageElements.value].sort((a, b) => b.zIndex - a.zIndex)
      let foundHoverElement = null

      for (const element of sortedElements) {
        if (isPointInElement(x, y, element)) {
          foundHoverElement = element
          break
        }
      }

      if (foundHoverElement) {
        canvasRef.value.style.cursor = 'move';
      } else {
        canvasRef.value.style.cursor = 'default';
      }
    }
    return;
  }

  // Drawing mode logic
  draw(e);
  if (currentTool.value === 'eraser') {
    const rect = canvasRef.value.getBoundingClientRect();
    eraserPreview.x = e.clientX - rect.left;
    eraserPreview.y = e.clientY - rect.top;
    eraserPreview.width = eraserWidth.value * 2;
    eraserPreview.height = eraserWidth.value * 2 * 9 / 16;
    eraserPreview.show = true;
  } else {
    eraserPreview.show = false;
  }
}
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

const router = useRouter()
const canvasRef = ref(null)
// ...existing code...
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
  // 鼠标离开画布时停止任何拖拽操作
  if (dragType || isDragging.value || isDragReady.value) {
    stopDrawing()
  }
  // 重置鼠标样式
  if (canvasRef.value) {
    canvasRef.value.style.cursor = 'default'
  }
}
const isDrawing = ref(false)
const isDragging = ref(false)
const isDragReady = ref(false) // 是否准备拖拽（鼠标按下但还未移动）
const isScaling = ref(false) // 是否正在缩放
const isRotating = ref(false) // 是否正在旋转
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

// 拼贴模式拖拽相关变量
let dragStartX = 0
let dragStartY = 0
let dragType = null // 'move', 'n', 's', 'e', 'w', 'nw', 'ne', 'sw', 'se'
let dragStart = null // 记录拖拽开始时的元素状态
let lastRedrawTime = 0 // 上次重绘时间
const redrawThrottle = 16 // 16ms 节流，约60fps

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
          { name: '别墅', svgCode: '<svg t="1756147198844" class="icon" viewBox="0 0 1053 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="95267" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M876.501554 24.406218a35.37133 35.37133 0 0 1-19.100518 42.799309h-3.537133l-82.768912 26.88221v240.525044h188.882902a35.37133 35.37133 0 0 1 35.37133 31.480483v221.070812h20.869084a35.37133 35.37133 0 0 1 35.37133 35.37133v141.485319a35.37133 35.37133 0 0 1-35.37133 35.37133h-20.869084v189.236615a35.37133 35.37133 0 0 1-31.480484 35.37133H35.37133a35.37133 35.37133 0 0 1-35.37133-35.37133V565.941278a35.37133 35.37133 0 0 1 35.37133-35.37133h106.11399V299.595164l-95.502591 30.773057a35.37133 35.37133 0 0 1-43.153023-19.454231V307.73057a35.37133 35.37133 0 0 1 18.039379-42.799309h3.537133L832.287392 1.768566a35.37133 35.37133 0 0 1 44.214162 22.637652z m-302.778583 773.924697h-111.065976v154.218999h111.065976zM392.621762 601.312608H70.74266v350.529879h321.879102z m287.215198 196.310881H601.312608v154.218998h78.170639z m245.123316 0h-99.039723v154.218998h99.039723z m-127.336787 0H707.426598v154.218998h89.843177z m183.577202-141.48532H462.656995v70.74266h518.543696z m-56.240415-252.197582H462.656995v182.162349h111.065976v-117.079102a14.148532 14.148532 0 0 1 11.318825-13.794818H813.540587a14.148532 14.148532 0 0 1 13.794819 11.672538v121.677375h99.039724z m-245.123316 77.109499H601.312608v106.11399h78.170639z m117.786529 0H707.426598v106.11399h89.843177z m-96.917444-343.455613L210.105699 284.739206v247.599309h182.516063v-161.293265a35.37133 35.37133 0 0 1 31.480483-35.371329h276.6038zM315.512263 314.804836a28.297064 28.297064 0 0 1 27.94335 27.943351v28.297063a28.297064 28.297064 0 0 1-27.94335 27.943351h-28.297064a28.297064 28.297064 0 0 1-27.943351-27.943351v-28.297063a28.297064 28.297064 0 0 1 27.943351-27.943351z" p-id="95268"></path></svg>'},
          { name: '小屋', svgCode: '<svg t="1756147264936" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="95429" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M513 226.1l346.8 388.5c3.7 4.1 10 4.5 14.1 0.8l46.6-41.6c4.1-3.7 4.5-10 0.8-14.1L520.4 110.5c-4-4.5-10.9-4.5-14.9 0l-240 269V244.7c0-5.5-4.5-10-10-10h-62.6c-5.5 0-10 4.5-10 10V472l-78.3 87.7c-3.7 4.1-3.3 10.4 0.8 14.1l46.6 41.6c4.1 3.7 10.4 3.3 14.1-0.8L513 226.1zM481.8 762.2h62.6c5.5 0 10 4.5 10 10v144.9c0 5.5-4.5 10-10 10h-62.6c-5.5 0-10-4.5-10-10V772.2c0-5.6 4.5-10 10-10z" p-id="95430"></path><path d="M907.4 887.3H843V684.9L519.4 316.3c-4-4.5-11.1-4.5-15.1 0L182.9 684.9v202.4h-64.5c-10.8 0-20.1 8.4-20.5 19.3-0.4 11.4 8.7 20.7 20 20.7h271.3V679.6h247.5v207.7h-0.2v40h271.4c11.3 0 20.4-9.4 20-20.7-0.4-10.9-9.7-19.3-20.5-19.3z" p-id="95431"></path></svg>'},
          { name: '庙宇', svgCode: '<svg t="1756147378600" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="99208" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M158.7 374.9l697.4-0.2s72 1 89.7-61.6c3.7-13.1-16.5 16.3-70.7-63.3l-85.8-134.2S766 68 733.2 68c-21.2 0-78.8 47.6-78.8 47.6l-282 0.1s-54-47.6-80.4-47.6c-23.3 0-58 48.6-58 48.6l-77.3 131.2s-42.6 61.2-79.8 79.8c-10.3 5.3 26.8 49.8 81.8 47.2z" fill="#F6A38B" p-id="99209"></path><path d="M857.9 385H856l-697 0.2c-49.8 1.9-88.5-30.8-93.3-49.6-2.3-8.8 2.2-14.5 6.7-16.8 34.4-17.2 75.5-75.9 76-76.5l76.9-130.6C232 102.1 265.4 58 292 58s71.5 36.7 84.2 47.6l274.6-0.1c14.6-11.8 60.3-47.4 82.3-47.6h0.2c38.7 0 64.2 51.1 65.3 53.3l85.2 133.2c35.1 51.6 53.7 53.6 59.8 54.2 2.9 0.3 7.8 0.8 10.9 5.5 3.2 4.7 1.7 9.9 1.2 11.9-15.4 54.2-69.6 68.7-97.8 69z m-699.3-20.3c0.1 0 0.1 0 0 0l697.5-0.2c2.8 0.2 59.1 0 77.6-47.1-16-4.3-36.9-17.6-66.9-61.8l-85.9-134.4c-6.3-12.6-25.9-42.9-47.5-42.9h-0.1c-10.9 0.1-45.9 23.6-72.2 45.3-1.8 1.5-4.3 2.6-6.5 2.3l-282 0.1c-2.5 0-4.9-0.9-6.7-2.6-19.8-17.4-57.3-45.1-73.7-45h-0.1c-12.3 0.1-36.9 26.5-49.6 44.3l-76.8 130.5c-2.1 3.1-40.9 58.5-78.3 80.7 7.1 10.3 34 32.7 71.1 30.8h0.1z" fill="#7F0518" p-id="99210"></path><path d="M372.3 128.1L236.9 374.9" fill="#EC1B23" p-id="99211"></path><path d="M237 385.1c-1.7 0-3.4-0.4-5-1.3-4.9-2.7-6.7-8.9-4-13.9l135.4-246.8c2.7-4.9 8.9-6.7 13.9-4 4.9 2.7 6.7 8.9 4 13.9L245.8 379.8c-1.8 3.4-5.3 5.3-8.8 5.3z" fill="#7F0518" p-id="99212"></path><path d="M651 128l135.5 246.8" fill="#EC1B23" p-id="99213"></path><path d="M786.6 385c-3.6 0-7.2-1.9-9.1-5.3L642.1 132.9c-2.7-4.9-0.9-11.1 4-13.8 4.9-2.7 11.1-0.9 13.8 4l135.5 246.8c2.7 4.9 0.9 11.1-4 13.8-1.5 0.9-3.1 1.3-4.8 1.3z m-414.2 0.1c-1.7 0-3.4-0.4-5-1.2-4.9-2.7-6.8-8.9-4.1-13.8L504.5 111c1.8-3.4 5.4-5.3 9.1-5.3 3.8 0.1 7.2 2.2 8.9 5.6l124.1 246.5c2.5 5 0.5 11.2-4.5 13.7-5 2.6-11.2 0.5-13.7-4.5L513.2 137.8l-131.9 242c-1.8 3.3-5.3 5.2-8.9 5.3z" fill="#7F0518" p-id="99214"></path><path d="M193.3 379.2h640.6v352.7H193.3z" fill="#d81e06" p-id="99215"></path><path d="M834 742.1l-640.7 0.1c-2.7 0-5.3-1.1-7.2-3-1.9-1.9-3-4.5-3-7.2l-0.1-352.7c0-5.6 4.6-10.2 10.2-10.2l640.6-0.1c5.6 0 10.2 4.6 10.2 10.2l0.1 352.7c0 2.7-1.1 5.3-3 7.2-1.9 1.9-4.4 3-7.1 3z m-630.5-20.3l620.2-0.1-0.1-332.3-620.2 0.1 0.1 332.3z" fill="#7F0518" p-id="99216"></path><path d="M193.4 734.1H834v151.2H193.4z" fill="#F6A38B" p-id="99217"></path><path d="M834.1 895.4c-0.1 0-0.1 0 0 0l-640.7 0.1c-5.6 0-10.2-4.6-10.2-10.2V734.1c0-2.7 1.1-5.3 3-7.2 1.9-1.9 4.7-2.7 7.2-3l640.6-0.1c5.6 0 10.2 4.6 10.2 10.2v151.2c0 2.7-1.1 5.3-3 7.2-1.9 1.9-4.5 3-7.1 3z m-630.5-20.2l620.2-0.1V744.3l-620.2 0.1v130.8z" fill="#7F0518" p-id="99218"></path><path d="M636.3 734c0-1.6 0.2-3.1 0.2-4.7V583.1c0-67.8-55-122.8-122.9-122.8s-122.9 55-122.8 122.9v146.2c0 1.6 0.2 3.1 0.2 4.7l245.3-0.1z" fill="#F6A38B" p-id="99219"></path><path d="M636.3 744.2l-255 0.1-0.4-9.8c-0.2-2.7-0.3-3.9-0.3-5.1V583.2c0-73.4 59-133.5 133-133.1 35.5 0 69 13.8 94.1 38.9 25.1 25.1 39 58.5 39 94.1l-0.8 159.1-9.6 2zM401 723.9h225.2l0.1-140.7c0-62.1-50.6-112.6-112.7-112.6h-1.1c-61.6 0.6-111.6 50.9-111.6 112.7l0.1 140.6z" fill="#7F0518" p-id="99220"></path><path d="M786.3 513.4c0 28.1-22.7 50.8-50.8 50.8-28.1 0-50.8-22.7-50.8-50.8 0-28.1 22.7-50.8 50.8-50.8 28 0 50.8 22.7 50.8 50.8z" fill="#FF6A48" p-id="99221"></path><path d="M736.1 574.4h-0.6c-33.6 0-61-27.4-61-61 0-33.4 27-60.7 60.4-61h0.6c16.3 0 31.6 6.3 43.1 17.8s17.9 26.8 17.9 43.1-6.3 31.6-17.9 43.1c-11.4 11.5-26.4 17.8-42.5 18z m-1-101.6c-22.2 0.2-40.2 18.3-40.2 40.6 0 22.4 18.2 40.6 40.6 40.6 10.9-0.1 21-4.2 28.7-11.9 7.7-7.7 11.9-17.9 11.9-28.7h10.2-10.2c0-10.8-4.2-21-11.9-28.7-7.7-7.7-17.9-11.9-28.7-11.9h-0.4z" fill="#7F0518" p-id="99222"></path><path d="M338.3 513.3c0 28.1-22.7 50.8-50.8 50.8-28.1 0-50.8-22.7-50.8-50.8 0-28.1 22.7-50.8 50.8-50.8 28.1 0 50.8 22.8 50.8 50.8z" fill="#FF6A48" p-id="99223"></path><path d="M288.1 574.3h-0.6c-16.3 0-31.6-6.3-43.1-17.8s-17.9-26.8-17.9-43.1c0-33.4 27-60.7 60.4-61h0.6c33.6 0 61 27.4 61 61 0 16.3-6.3 31.6-17.9 43.1-11.3 11.3-26.4 17.6-42.5 17.8z m-1-101.6c-22.2 0.2-40.2 18.3-40.2 40.6 0 10.8 4.2 21 11.9 28.7 7.7 7.7 17.9 11.9 28.7 11.9s21-4.2 28.7-11.9c7.7-7.7 11.9-17.9 11.9-28.7 0-22.4-18.2-40.6-40.6-40.6h-0.4zM513.7 742.1s0 0.1 0 0c-5.7 0-10.3-4.6-10.3-10.2l-0.1-271.6c0-5.6 5.2-10 10.2-10.2 5.6 0 10.2 4.6 10.2 10.2l0.1 271.6c0 5.7-4.5 10.2-10.1 10.2z" fill="#7F0518" p-id="99224"></path><path d="M79.54 618.74l230.9-2.21 2.538 265.2-230.9 2.21z" fill="#FFFFFF" p-id="99225"></path><path d="M313.1 891.9l-230.9 2.2c-5.6 0.1-10.2-4.5-10.3-10.1l-2.5-265.2c-0.1-5.6 4.5-10.2 10.1-10.3l230.9-2.2c5.6-0.1 10.2 4.5 10.3 10.1l2.5 265.2c0 5.6-4.5 10.2-10.1 10.3zM92.2 873.6l210.5-2-2.3-244.8-210.5 2 2.3 244.8z" fill="#7F0518" p-id="99226"></path><path d="M80.3 763.1h231.9v122.3H80.3z" fill="#F6A38B" p-id="99227"></path><path d="M312.3 895.6s-0.1 0 0 0h-232c-5.6 0-10.2-4.6-10.2-10.2V763.1c0-5.6 5.4-11 10.2-10.2l231.9-0.1c2.7 0 5.3 1.1 7.2 3 1.9 1.9 3 4.5 3 7.2v122.3c0 5.7-4.5 10.2-10.1 10.3zM90.5 875.2H302V773.3H90.5v101.9z" fill="#7F0518" p-id="99228"></path><path d="M717.37 618.54l230.9-2.21 2.538 265.2-230.9 2.21z" fill="#FFFFFF" p-id="99229"></path><path d="M950.9 891.6L720 893.9c-5.6 0.1-10.2-4.5-10.3-10.1l-2.5-265.2c-0.1-5.6 4.5-10.2 10.1-10.3l230.9-2.2c5.6-0.1 10.2 4.5 10.3 10.1l2.5 265.2c0.1 5.6-4.5 10.2-10.1 10.2zM730 873.4l210.5-2-2.3-244.8-210.5 2 2.3 244.8z" fill="#7F0518" p-id="99230"></path><path d="M718.1 762.9H950v122.3H718.1z" fill="#F6A38B" p-id="99231"></path><path d="M950.1 895.3l-232 0.1c-2.7 0-5.3-1.1-7.2-3-1.9-1.9-3-4.5-3-7.2V762.9c0-2.7 1.1-5.3 3-7.2 1.9-1.9 5.2-2.8 7.2-3H950c5.6 0 10.2 4.6 10.2 10.2v122.3c0 5.5-4.5 10.1-10.1 10.1zM728.3 875h211.5V773.1H728.3V875z" fill="#7F0518" p-id="99232"></path></svg>'},
          { name: '古风大门', svgCode: '<svg t="1756147514647" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="100691" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M360.131896 252.358122a8.904348 8.904348 0 0 1-8.904348-8.904348v-18.854957a8.904348 8.904348 0 0 1 17.808695 0v18.854957a8.904348 8.904348 0 0 1-8.904347 8.904348zM415.788522 252.358122a8.904348 8.904348 0 0 1-8.904348-8.904348v-18.854957a8.904348 8.904348 0 0 1 17.808696 0v18.854957a8.904348 8.904348 0 0 1-8.904348 8.904348zM471.445148 252.358122a8.904348 8.904348 0 0 1-8.904348-8.904348v-18.854957a8.904348 8.904348 0 0 1 17.808696 0v18.854957a8.904348 8.904348 0 0 1-8.904348 8.904348zM527.106226 252.358122a8.904348 8.904348 0 0 1-8.904348-8.904348v-18.854957a8.904348 8.904348 0 0 1 17.808696 0v18.854957a8.904348 8.904348 0 0 1-8.904348 8.904348zM582.762852 252.358122a8.904348 8.904348 0 0 1-8.904348-8.904348v-18.854957a8.904348 8.904348 0 0 1 17.808696 0v18.854957a8.904348 8.904348 0 0 1-8.904348 8.904348zM638.419478 252.358122a8.904348 8.904348 0 0 1-8.904348-8.904348v-18.854957a8.904348 8.904348 0 0 1 17.808696 0v18.854957a8.904348 8.904348 0 0 1-8.904348 8.904348zM694.076104 252.358122a8.904348 8.904348 0 0 1-8.904347-8.904348v-18.854957a8.904348 8.904348 0 0 1 17.808695 0v18.854957a8.904348 8.904348 0 0 1-8.904348 8.904348z" fill="#2c2c2c" p-id="100692"></path><path d="M892.500591 339.024139c-73.634504 0-115.449322-30.573078-117.724382-86.082782l-0.120209-16.544279c-0.004452-4.011409-0.400696-8.370087-0.98393-11.789356-2.787061 4.087096-7.119026 11.740383-13.218505 25.987339a8.904348 8.904348 0 0 1-8.187548 5.400487H301.941983a8.904348 8.904348 0 0 1-8.183096-5.400487c-6.099478-14.246957-10.431443-21.904696-13.218504-25.987339-0.583235 3.410365-0.979478 7.751235-0.983931 11.731478l-0.111304 16.237078c-2.288417 55.874783-44.098783 86.447861-117.733287 86.447861-10.418087 0-20.778296-1.37127-30.795687-4.078191a8.904348 8.904348 0 0 1 4.643617-17.189844c8.503652 2.297322 17.301148 3.459339 26.15207 3.459339 44.294678 0 97.5872-11.971896 99.933496-69.004243l-0.004453-0.311652 0.111305-15.631583c0-13.850713 2.470957-30.942609 14.238052-33.355687 10.520487-2.172661 19.375861 7.479652 31.784069 35.274574h438.668244c12.412661-27.799374 21.250226-37.447235 31.784069-35.274574 11.771548 2.413078 14.238052 19.504974 14.238053 33.418018l0.111304 16.24153c2.332939 56.66727 55.629913 68.639165 99.924591 68.639165 8.84647 0 17.648417-1.16647 26.15207-3.459339a8.904348 8.904348 0 0 1 4.643617 17.189844 117.893565 117.893565 0 0 1-30.795687 4.082643z" fill="#2c2c2c" p-id="100693"></path><path d="M802.784835 410.824348a8.9088 8.9088 0 0 1-0.783583-17.773078c87.004383-7.746783 109.674852-67.192209 110.596452-69.721044a8.917704 8.917704 0 0 1 11.393113-5.338156 8.886539 8.886539 0 0 1 5.373774 11.344139c-1.050713 2.965148-26.980174 72.655026-125.778365 81.452521a8.223165 8.223165 0 0 1-0.801391 0.035618zM247.701148 410.45927c-0.316104 0-0.641113-0.013357-0.96167-0.048974-95.619339-10.284522-120.863165-78.184626-121.891617-81.069635a8.904348 8.904348 0 0 1 16.762435-6.005983c0.917148 2.506574 22.991026 60.331409 107.030261 69.369322a8.904348 8.904348 0 0 1-0.939409 17.75527zM527.952139 674.072487a8.904348 8.904348 0 0 1-6.295374-2.608974l-108.103235-108.116591a8.904348 8.904348 0 0 1 0-12.590748l108.103235-108.103235a8.904348 8.904348 0 0 1 12.590748 0l108.107687 108.103235a8.904348 8.904348 0 0 1 0 12.590748l-108.107687 108.116591a8.904348 8.904348 0 0 1-6.295374 2.608974zM432.439652 557.051548l95.512487 95.525843 95.516939-95.525843-95.516939-95.512487-95.512487 95.512487z" fill="#2c2c2c" p-id="100694"></path><path d="M527.097322 746.130922h-0.008905a8.904348 8.904348 0 0 1-8.895443-8.913252l0.378435-377.468661a8.904348 8.904348 0 0 1 8.904348-8.895444h0.008904a8.904348 8.904348 0 0 1 8.895443 8.913252l-0.378434 377.468661a8.904348 8.904348 0 0 1-8.904348 8.895444zM356.218435 751.282087H251.400904a8.904348 8.904348 0 0 1-8.904347-8.904348V360.047304a8.904348 8.904348 0 0 1 17.808695 0v373.426087H347.314087V360.047304a8.904348 8.904348 0 0 1 17.808696 0v382.330435a8.904348 8.904348 0 0 1-8.904348 8.904348z" fill="#2c2c2c" p-id="100695"></path><path d="M327.034435 681.178157H280.580452a8.904348 8.904348 0 0 1-8.904348-8.904348v-216.892105a8.904348 8.904348 0 0 1 8.904348-8.904347h46.453983a8.904348 8.904348 0 0 1 8.904348 8.904347v216.892105a8.904348 8.904348 0 0 1-8.904348 8.904348z m-37.549635-17.808696h28.645287v-199.083409h-28.645287v199.083409zM802.789287 751.331061h-104.81753a8.904348 8.904348 0 0 1-8.904348-8.904348v-383.910956a8.904348 8.904348 0 0 1 17.808695 0v375.002156h87.008835V358.515757a8.904348 8.904348 0 0 1 17.808696 0v383.906504a8.904348 8.904348 0 0 1-8.904348 8.9088z" fill="#2c2c2c" p-id="100696"></path><path d="M773.618643 681.178157h-46.462886a8.904348 8.904348 0 0 1-8.904348-8.904348v-216.892105a8.904348 8.904348 0 0 1 8.904348-8.904347h46.462886a8.904348 8.904348 0 0 1 8.904348 8.904347v216.892105a8.904348 8.904348 0 0 1-8.904348 8.904348z m-37.558539-17.808696h28.654192v-199.083409h-28.654192v199.083409zM819.235617 794.405843H234.981287a23.81913 23.81913 0 0 1-23.792417-23.792417v-13.303096a23.81913 23.81913 0 0 1 23.792417-23.787965h584.25433a23.81913 23.81913 0 0 1 23.792418 23.787965v13.303096a23.81913 23.81913 0 0 1-23.792418 23.792417z m-584.25433-43.074782c-3.299061 0-5.983722 2.684661-5.983722 5.979269v13.303096c0 3.299061 2.684661 5.983722 5.983722 5.983722h584.25433c3.299061 0 5.983722-2.684661 5.983722-5.983722v-13.303096c0-3.294609-2.684661-5.97927-5.983722-5.979269H234.981287z" fill="#2c2c2c" p-id="100697"></path><path d="M439.95047 742.426713h174.30706v43.074783H439.95047z" fill="#2c2c2c" p-id="100698"></path><path d="M614.261983 794.405843H439.95047a8.904348 8.904348 0 0 1-8.904348-8.904347v-43.074783a8.904348 8.904348 0 0 1 8.904348-8.904348h174.30706a8.904348 8.904348 0 0 1 8.904348 8.904348v43.074783a8.904348 8.904348 0 0 1-8.899895 8.904347z m-165.407166-17.808695h156.498366v-25.266087h-156.498366v25.266087z" fill="#2c2c2c" p-id="100699"></path><path d="M402.966261 787.082017h248.284382v43.074783H402.966261z" fill="#2c2c2c" p-id="100700"></path><path d="M651.246191 839.061148H402.966261a8.904348 8.904348 0 0 1-8.904348-8.904348v-43.074783a8.904348 8.904348 0 0 1 8.904348-8.904347h248.284382a8.904348 8.904348 0 0 1 8.904348 8.904347v43.074783a8.913252 8.913252 0 0 1-8.9088 8.904348z m-239.375582-17.808696h230.475687v-25.266087H411.870609v25.266087z" fill="#2c2c2c" p-id="100701"></path><path d="M856.446887 839.061148H197.765565a23.81913 23.81913 0 0 1-23.787965-23.792418v-13.307547a23.814678 23.814678 0 0 1 23.787965-23.783513h658.681322a23.810226 23.810226 0 0 1 23.787965 23.783513v13.307547a23.81913 23.81913 0 0 1-23.787965 23.792418zM197.765565 795.986365c-3.294609 0-5.97927 2.680209-5.979269 5.974818v13.307547c0 3.299061 2.684661 5.983722 5.979269 5.983722h658.681322c3.294609 0 5.97927-2.684661 5.97927-5.983722v-13.307547c0-3.294609-2.684661-5.974817-5.97927-5.974818H197.765565zM834.568904 364.695374H219.456557c-51.907896-0.26713-91.193878-30.012104-92.845635-31.280974a8.904348 8.904348 0 0 1 10.841043-14.1312c0.360626 0.276035 36.677009 27.603478 82.716939 27.603478h613.879096c46.03993 0 82.351861-27.327443 82.712487-27.603478a8.913252 8.913252 0 0 1 12.479443 1.656209 8.890991 8.890991 0 0 1-1.633947 12.470539c-1.651757 1.26887-40.942191 31.013843-92.845635 31.280974l-0.191444 0.004452z" fill="#2c2c2c" p-id="100702"></path></svg>'},
          { name: '亭台楼阁', svgCode: '<svg t="1756147856806" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="109326" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M520.794353 132.156235l2.258823 2.620236 97.490824 129.987764h39.544471c5.180235 0 10.24 1.566118 14.516705 4.367059l3.041883 2.379294 6.505412 5.601883 6.595764 5.481411c10.330353 8.493176 21.353412 16.986353 32.527059 24.847059 10.360471 7.288471 20.299294 13.643294 29.605647 18.853647 8.011294 4.487529 15.36 8.011294 21.865412 10.450824 9.728 3.614118 23.100235 6.987294 38.640941 9.878588l7.951059 1.415529 7.529412 1.204706 13.94447 1.987765 13.161412 1.505882c26.804706 2.710588 32.225882 38.430118 9.366588 49.724236l-3.132235 1.325176-20.781176 7.228235-10.932706 3.704471-10.691765 3.463529-11.685647 3.614118-7.920941 2.288941-17.438118 4.638118c-10.24 2.620235-21.172706 5.270588-32.105412 7.80047l6.02353-1.445647v286.479059h61.530353c13.432471 0 24.515765 10.059294 26.142117 23.070118l0.210824 3.312941v105.411765a26.352941 26.352941 0 0 1-26.352941 26.322823h-632.470589a26.352941 26.352941 0 0 1-26.352941-26.352941v-105.411765c0-14.546824 11.776-26.352941 26.352941-26.352941h61.44v-286.418823l-2.68047-0.662589-2.680471-0.63247-19.877647-4.909177-18.070588-4.818823-13.643294-4.005647-12.739765-4.065883-14.998588-5.029647-20.781177-7.228235c-25.389176-9.065412-22.016-45.176471 3.011765-50.507294l3.343059-0.542118 16.414118-1.957647c12.468706-1.686588 24.907294-3.764706 36.382117-6.204235 11.294118-2.409412 20.931765-5.059765 28.310588-7.830588 6.505412-2.439529 13.854118-5.963294 21.89553-10.450824 9.276235-5.210353 19.215059-11.565176 29.575529-18.853647 7.439059-5.240471 14.848-10.752 21.985883-16.384l10.541176-8.432941 3.523765-2.921412 9.577412-8.192a26.352941 26.352941 0 0 1 13.733647-6.445176l3.855058-0.301177h39.544471l97.490824-129.987764a26.352941 26.352941 0 0 1 39.905882-2.620236z m271.028706 642.108236H730.352941l-0.481882-0.030118-455.800471 0.030118h-0.512l-0.481882-0.030118-61.018353 0.030118v52.705882h579.764706v-52.705882z m-87.823059-333.824H299.911529v281.118117h404.088471v-281.118117z m-53.76-122.970353l-42.375529-0.030118-0.481883 0.060235H396.047059l-42.405647-0.030117-7.017412 5.872941c-11.294118 9.246118-23.311059 18.522353-35.659294 27.226353-11.745882 8.222118-23.190588 15.540706-34.18353 21.684706l-7.529411 4.096-7.378824 3.674353-6.415059 2.861176 21.112471 4.879059h450.800941l21.022118-4.879059-6.324706-2.861176-7.378824-3.674353-7.559529-4.065883a397.071059 397.071059 0 0 1-34.153412-21.714823 585.276235 585.276235 0 0 1-24.154353-17.980236l-11.535059-9.246117-7.047529-5.872941z m-148.299294-122.970353l-52.705882 70.26447h105.411764l-52.705882-70.26447z" fill="#333333" p-id="109327"></path></svg>'},
          { name: '大厦', svgCode: '<svg t="1756147731306" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="104357" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M576 938.666667H341.333333V183.893333a63.8 63.8 0 0 1 57.633334-63.686666L725.333333 87.573333V704a21.333333 21.333333 0 0 0 42.666667 0V256h128v448a21.333333 21.333333 0 0 0 42.666667 0V256a42.713333 42.713333 0 0 0-42.666667-42.666667h-128V64a21.333333 21.333333 0 0 0-23.453333-21.226667l-349.826667 34.98A106.666667 106.666667 0 0 0 298.666667 183.893333V938.666667H170.666667v-89.5c10.873333-4.526667 20.14-12.666667 27.04-23.953334C208.22 808 213.333333 784.06 213.333333 752c0-31.2-5-66.666667-13.38-94.84-4.613333-15.513333-10-28.14-16.093333-37.526667C171.946667 601.2 158.506667 597.333333 149.333333 597.333333s-22.613333 3.866667-34.526666 22.3c-6.066667 9.386667-11.48 22-16.093334 37.526667C90.333333 685.333333 85.333333 720.8 85.333333 752c0 32.06 5.113333 56 15.626667 73.213333 6.9 11.293333 16.166667 19.426667 27.04 23.953334V938.666667H64a21.333333 21.333333 0 0 0 0 42.666666h512a21.333333 21.333333 0 0 0 0-42.666666z m-438.833333-260.44c4.306667-17 8.82-27.446667 12.166666-33.333334 3.333333 5.873333 7.86 16.32 12.166667 33.333334A314.266667 314.266667 0 0 1 170.666667 752c0 13.76-1.54 58.666667-21.333334 58.666667s-21.333333-44.906667-21.333333-58.666667a314.266667 314.266667 0 0 1 9.166667-73.773333zM469.333333 298.666667h-42.666666V213.333333h42.666666z m85.333334 0h-42.666667V213.333333h42.666667z m85.333333 0h-42.666667V213.333333h42.666667zM469.333333 426.666667h-42.666666V341.333333h42.666666z m85.333334 0h-42.666667V341.333333h42.666667z m85.333333 0h-42.666667V341.333333h42.666667zM469.333333 554.666667h-42.666666V469.333333h42.666666z m85.333334 0h-42.666667V469.333333h42.666667z m42.666666-85.333334h42.666667v85.333334h-42.666667z m-128 213.333334h-42.666666V597.333333h42.666666z m85.333334 0h-42.666667V597.333333h42.666667z m85.333333 0h-42.666667V597.333333h42.666667z m-213.333333 42.666666h42.666666v85.333334h-42.666666z m85.333333 0h42.666667v85.333334h-42.666667z m341.333333-298.666666h-42.666666V341.333333h42.666666z m0 128h-42.666666V469.333333h42.666666z m-42.666666 42.666666h42.666666v85.333334h-42.666666z m150.12 243.133334a85.513333 85.513333 0 0 0-41.026667-26.433334 106.666667 106.666667 0 0 0-173.093333-3.333333h-21.333334a85.333333 85.333333 0 0 0 0 170.666667h170.666667a85.333333 85.333333 0 0 0 64.786667-140.866667zM896 938.666667h-170.666667a42.666667 42.666667 0 0 1 0-85.333334h32.753334a21.333333 21.333333 0 0 0 18.466666-10.666666 64 64 0 0 1 111.253334 0.666666 21.333333 21.333333 0 0 0 15.146666 10.586667A42.666667 42.666667 0 0 1 896 938.666667z" fill="#5C5C66" p-id="104358"></path></svg>'},
          { name: '屋子', svgCode: '<svg t="1756148092769" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="111495" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M740.48 140.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM760.32 140.16h-3.84c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.84c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM778.24 140.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM853.12 188.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM872.96 188.16h-3.84c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.84c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM890.88 188.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM814.08 236.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM833.92 236.16h-3.84c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.84c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM851.84 236.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM775.68 284.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM795.52 284.16h-3.84c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.84c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM812.8 284.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="111496"></path><path d="M133.12 330.24c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 31.36 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-8.96 8.96-21.12 13.44-32.64 13.44zM284.8 330.24c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44zM436.48 330.24c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 31.36 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44zM587.52 330.24c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-8.96 8.96-20.48 13.44-32.64 13.44zM209.28 405.76c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44zM360.32 405.76c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-8.96 8.96-21.12 13.44-32.64 13.44zM512 405.76c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44zM663.68 405.76c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44zM815.36 405.76c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44zM209.28 254.08c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44zM360.32 254.08c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-8.96 8.96-21.12 13.44-32.64 13.44zM512 254.08c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44zM663.68 254.08c-11.52 0-23.04-4.48-32-13.44-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0c11.52 11.52 30.72 11.52 42.88 0 3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88c-9.6 8.96-21.12 13.44-32.64 13.44z" fill="#211D1C" p-id="111497"></path><path d="M966.4 476.16H57.6c-4.48 0-7.68-3.2-7.68-7.68V160c0-4.48 3.2-7.68 7.68-7.68h681.6c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68H65.28V460.8h893.44V167.68h-68.48c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68H966.4c4.48 0 7.68 3.2 7.68 7.68v308.48c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111498"></path><path d="M890.88 335.36h-151.68c-4.48 0-7.68-3.2-7.68-7.68v-243.2c0-4.48 3.2-7.68 7.68-7.68h151.68c4.48 0 7.68 3.2 7.68 7.68v243.2c0 4.48-3.84 7.68-7.68 7.68zM746.88 320H883.2V92.16h-136.32V320zM966.4 503.68H57.6c-4.48 0-7.68-3.2-7.68-7.68v-27.52c0-4.48 3.2-7.68 7.68-7.68h908.8c4.48 0 7.68 3.2 7.68 7.68v27.52c0 4.48-3.2 7.68-7.68 7.68zM65.28 488.96h893.44v-12.8H65.28v12.8z" fill="#211D1C" p-id="111499"></path><path d="M966.4 1000.96H57.6c-4.48 0-7.68-3.2-7.68-7.68V496c0-4.48 3.2-7.68 7.68-7.68h908.8c4.48 0 7.68 3.2 7.68 7.68v497.28c0 4.48-3.2 7.68-7.68 7.68zM65.28 985.6h893.44V503.68H65.28V985.6z" fill="#211D1C" p-id="111500"></path><path d="M103.68 996.48c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v1.28c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111501"></path><path d="M103.68 983.04c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111502"></path><path d="M94.08 981.12h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111503"></path><path d="M84.48 981.12H83.2c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111504"></path><path d="M83.2 968.32c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111505"></path><path d="M83.2 941.44c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-1.28 1.92-3.84 3.2-5.76 3.2z" fill="#211D1C" p-id="111506"></path><path d="M94.08 939.52h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111507"></path><path d="M103.68 939.52H102.4c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111508"></path><path d="M103.68 927.36c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111509"></path><path d="M103.68 899.84c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111510"></path><path d="M94.08 898.56h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111511"></path><path d="M84.48 898.56H83.2c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111512"></path><path d="M83.2 885.76c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c-0.64 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111513"></path><path d="M83.2 858.24c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-1.28 1.92-3.84 3.2-5.76 3.2z" fill="#211D1C" p-id="111514"></path><path d="M94.08 856.96h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111515"></path><path d="M103.68 856.96H102.4c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111516"></path><path d="M103.68 844.16c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111517"></path><path d="M103.68 816.64c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111518"></path><path d="M94.08 815.36h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111519"></path><path d="M84.48 815.36H83.2c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111520"></path><path d="M83.2 802.56c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111521"></path><path d="M83.2 775.04c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-1.28 1.92-3.84 3.2-5.76 3.2z" fill="#211D1C" p-id="111522"></path><path d="M94.08 773.76h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111523"></path><path d="M103.68 773.76H102.4c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111524"></path><path d="M103.68 760.96c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111525"></path><path d="M103.68 733.44c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111526"></path><path d="M94.08 732.16h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111527"></path><path d="M84.48 732.16H83.2c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111528"></path><path d="M83.2 719.36c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111529"></path><path d="M83.2 692.48c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-1.28 1.92-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111530"></path><path d="M94.08 690.56h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111531"></path><path d="M103.68 690.56H102.4c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111532"></path><path d="M103.68 677.76c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111533"></path><path d="M103.68 650.88c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111534"></path><path d="M94.08 648.96h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111535"></path><path d="M84.48 648.96H83.2c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111536"></path><path d="M83.2 636.8c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111537"></path><path d="M83.2 609.28c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-1.28 1.92-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111538"></path><path d="M94.08 607.36h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111539"></path><path d="M103.68 607.36H102.4c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111540"></path><path d="M103.68 595.2c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111541"></path><path d="M103.68 567.68c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111542"></path><path d="M94.08 566.4h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111543"></path><path d="M84.48 566.4H83.2c-4.48 0-7.68-3.2-7.68-7.68V556.8c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 4.48-3.2 8.32-7.68 8.32z" fill="#211D1C" p-id="111544"></path><path d="M83.2 553.6c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111545"></path><path d="M83.2 526.08c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-1.28 1.92-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111546"></path><path d="M94.08 524.8h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111547"></path><path d="M103.68 524.8H102.4c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111548"></path><path d="M103.68 515.2c-4.48 0-7.68-3.2-7.68-7.68V505.6c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v1.92c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111549"></path><path d="M103.68 505.6c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v1.28c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111550"></path><path d="M917.12 505.6c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v1.28c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111551"></path><path d="M917.12 515.2c-4.48 0-7.68-3.2-7.68-7.68V505.6c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v1.92c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111552"></path><path d="M919.04 524.8h-1.28c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111553"></path><path d="M928.64 524.8h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111554"></path><path d="M938.24 526.08c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111555"></path><path d="M938.24 553.6c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111556"></path><path d="M938.24 566.4h-1.28c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111557"></path><path d="M928.64 566.4h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111558"></path><path d="M917.12 567.68c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-0.64 1.92-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111559"></path><path d="M917.12 595.2c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111560"></path><path d="M919.04 607.36h-1.28c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111561"></path><path d="M928.64 607.36h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111562"></path><path d="M938.24 609.28c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111563"></path><path d="M938.24 636.16c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111564"></path><path d="M938.24 648.96h-1.28c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111565"></path><path d="M928.64 648.96h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111566"></path><path d="M917.12 650.88c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-0.64 1.92-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111567"></path><path d="M917.12 677.76c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111568"></path><path d="M919.04 690.56h-1.28c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111569"></path><path d="M928.64 690.56h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111570"></path><path d="M938.24 692.48c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111571"></path><path d="M938.24 719.36c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111572"></path><path d="M938.24 732.16h-1.28c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111573"></path><path d="M928.64 732.16h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111574"></path><path d="M917.12 733.44c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-0.64 2.56-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111575"></path><path d="M917.12 760.96c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111576"></path><path d="M919.04 773.76h-1.28c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111577"></path><path d="M928.64 773.76h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111578"></path><path d="M937.6 775.04c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111579"></path><path d="M937.6 802.56c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111580"></path><path d="M937.6 815.36h-1.28c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111581"></path><path d="M928.64 815.36h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111582"></path><path d="M917.12 816.64c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-0.64 1.92-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111583"></path><path d="M917.12 844.16c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111584"></path><path d="M919.04 856.32h-1.28c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111585"></path><path d="M928.64 856.32h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111586"></path><path d="M937.6 858.24c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111587"></path><path d="M937.6 885.76c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111588"></path><path d="M937.6 897.92h-1.28c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111589"></path><path d="M928.64 897.92h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111590"></path><path d="M917.12 899.84c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-1.28 1.92-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111591"></path><path d="M917.12 927.36c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111592"></path><path d="M918.4 939.52h-1.28c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68 2.56 0 4.48 1.28 5.76 3.2 1.92 1.28 3.2 3.84 3.2 5.76 0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111593"></path><path d="M928.64 939.52h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111594"></path><path d="M937.6 941.44c-2.56 0-4.48-1.28-5.76-3.2-1.92-1.28-3.2-3.84-3.2-5.76 0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68v1.28c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111595"></path><path d="M937.6 968.32c-4.48 0-7.68-3.2-7.68-7.68v-2.56c0-1.92 0.64-4.48 2.56-5.76-1.28-1.28-2.56-3.2-2.56-5.76v-2.56c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v2.56c0 1.92-0.64 4.48-2.56 5.76 1.28 1.28 2.56 3.2 2.56 5.76v2.56c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111596"></path><path d="M937.6 981.12h-1.28c-4.48 0-7.68-3.2-7.68-7.68 0-2.56 1.28-4.48 3.2-5.76 1.28-1.92 3.84-3.2 5.76-3.2 4.48 0 7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111597"></path><path d="M928.64 981.12h-1.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.92c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111598"></path><path d="M917.12 983.04c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 2.56-1.28 4.48-3.2 5.76-1.28 1.92-3.2 3.2-5.76 3.2z" fill="#211D1C" p-id="111599"></path><path d="M917.12 996.48c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v1.28c0 4.48-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111600"></path><path d="M360.32 1000.96H209.28c-4.48 0-7.68-3.2-7.68-7.68v-266.24c0-4.48 3.2-7.68 7.68-7.68h151.68c4.48 0 7.68 3.2 7.68 7.68v266.24c-0.64 4.48-3.84 7.68-8.32 7.68zM216.32 985.6h136.32v-250.88H216.32V985.6z" fill="#211D1C" p-id="111601"></path><path d="M391.04 1000.96c-4.48 0-7.68-3.2-7.68-7.68V704H186.24v289.28c0 4.48-3.2 7.68-7.68 7.68s-7.68-3.2-7.68-7.68v-296.32c0-4.48 3.2-7.68 7.68-7.68H390.4c4.48 0 7.68 3.2 7.68 7.68v296.32c0 4.48-3.2 7.68-7.04 7.68z" fill="#211D1C" p-id="111602"></path><path d="M799.36 871.68H506.24c-4.48 0-7.68-3.2-7.68-7.68v-204.8c0-4.48 3.2-7.68 7.68-7.68h293.12c4.48 0 7.68 3.2 7.68 7.68v204.8c0 3.84-3.84 7.68-7.68 7.68z m-285.44-15.36h277.76v-190.08H513.92v190.08z" fill="#00ABE0" p-id="111603"></path><path d="M829.44 901.76H476.16c-4.48 0-7.68-3.2-7.68-7.68V628.48c0-4.48 3.2-7.68 7.68-7.68h353.28c4.48 0 7.68 3.2 7.68 7.68v265.6c0 4.48-3.2 7.68-7.68 7.68z m-345.6-15.36h338.56V636.16H483.84v250.24z" fill="#211D1C" p-id="111604"></path><path d="M339.2 659.84H225.28c-4.48 0-7.68-3.2-7.68-7.68v-108.8c0-4.48 3.2-7.68 7.68-7.68H339.2c4.48 0 7.68 3.2 7.68 7.68v108.8c-0.64 4.48-3.84 7.68-7.68 7.68z m-106.24-14.72h98.56V551.04H232.96v94.08z" fill="#00ABE0" p-id="111605"></path><path d="M339.2 605.44H225.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68H339.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#00ABE0" p-id="111606"></path><path d="M282.24 659.84c-4.48 0-7.68-3.2-7.68-7.68v-108.8c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v108.8c0 4.48-3.84 7.68-7.68 7.68zM799.36 768.64H506.24c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h293.12c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#00ABE0" p-id="111607"></path><path d="M604.16 870.4c-4.48 0-7.68-3.2-7.68-7.68V659.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v204.16c-0.64 3.84-3.84 7.04-7.68 7.04zM701.44 870.4c-4.48 0-7.68-3.2-7.68-7.68V659.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v204.16c0 3.84-3.2 7.04-7.68 7.04z" fill="#00ABE0" p-id="111608"></path></svg>'},
          { name: '屋子', svgCode: '<svg t="1756148167335" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="111763" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M984.96 1016.96c-4.48 0-7.68-3.2-7.68-7.68 0-19.84-16-35.84-35.84-35.84H65.92c-19.84 0-35.84 16-35.84 35.84 0 4.48-3.2 7.68-7.68 7.68s-7.68-3.2-7.68-7.68c0-28.16 23.04-51.2 51.2-51.2H940.8c28.16 0 51.2 23.04 51.2 51.2 0 4.48-3.2 7.68-7.04 7.68z" fill="#211D1C" p-id="111764"></path><path d="M60.16 973.44c-1.92 0-3.84-0.64-5.12-1.92-1.28-1.28-1.92-3.2-1.92-5.12 0-28.16 23.04-51.2 51.2-51.2h799.36c28.16 0 51.2 23.04 51.2 51.2 0 4.48-3.2 7.68-7.68 7.68l-887.04-0.64z m8.32-15.36h869.76c-3.2-16-17.92-28.8-35.2-28.8H103.68c-17.28 0.64-31.36 12.8-35.2 28.8zM963.2 523.52c-3.2 0-5.76-1.92-7.04-4.48l-152.96-356.48c-7.68-15.36-23.68-25.6-40.96-25.6H244.48c-17.28 0-33.28 10.24-40.96 25.6L50.56 519.04c-1.92 3.84-6.4 5.76-10.24 3.84-3.84-1.92-5.76-6.4-3.84-10.24l152.96-356.48c10.24-21.12 31.36-34.56 55.04-34.56h517.76c23.04 0 44.8 13.44 54.4 34.56l152.96 357.12c1.92 3.84 0 8.32-3.84 10.24h-2.56z" fill="#211D1C" p-id="111765"></path><path d="M503.68 188.16c-4.48 0-7.68-3.2-7.68-7.68V179.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v1.28c0 4.48-3.84 7.68-7.68 7.68zM503.68 448.64c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.84c0 3.84-3.84 7.04-7.68 7.04z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68V416c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 4.48-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 4.48-3.84 7.68-7.68 7.68z m0-21.12c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 3.84-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 3.84-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 3.84-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 3.84-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 3.84-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 4.48-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 4.48-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 4.48-3.84 7.68-7.68 7.68z m0-21.76c-4.48 0-7.68-3.2-7.68-7.68v-3.2c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v3.2c0 4.48-3.84 7.68-7.68 7.68zM503.68 469.12c-4.48 0-7.68-3.2-7.68-7.68v-1.28c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v1.28c0 4.48-3.84 7.68-7.68 7.68zM576.64 188.16c-3.84 0-7.04-3.2-7.68-7.04v-1.28c-0.64-4.48 2.56-7.68 7.04-8.32 4.48-0.64 7.68 2.56 8.32 7.04v1.28c0.64 4.48-2.56 7.68-7.04 8.32h-0.64zM602.88 448.64c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 4.48-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-2.56-21.76c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 4.48-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-1.92-21.76c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 4.48-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-2.56-21.12c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 3.84-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-1.92-21.76c-3.84 0-7.04-3.2-7.68-7.04V352c-0.64-3.84 2.56-7.68 7.04-8.32 4.48-0.64 7.68 2.56 8.32 7.04v3.2c0.64 3.84-2.56 7.68-7.04 8.32h-0.64z m-1.92-21.76c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 3.84-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-2.56-21.76c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 3.84-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-1.92-21.76c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 3.84-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-2.56-21.76c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 3.84-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-1.92-21.76c-3.84 0-7.04-3.2-7.68-7.04V243.2c-0.64-4.48 2.56-7.68 7.04-8.32 4.48-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64z m-2.56-21.76c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-3.84 2.56-7.68 7.04-8.32 3.84-0.64 7.68 2.56 8.32 7.04v3.2c0.64 3.84-2.56 7.68-7.04 8.32h-0.64z m-1.92-21.76c-3.84 0-7.04-3.2-7.68-7.04v-3.2c-0.64-4.48 2.56-7.68 7.04-8.32 4.48-0.64 7.68 2.56 8.32 7.04v3.2c0.64 4.48-2.56 7.68-7.04 8.32h-0.64zM604.8 469.12c-3.84 0-7.04-3.2-7.68-7.04V460.8c-0.64-3.84 2.56-7.68 7.04-8.32 4.48-0.64 7.68 2.56 8.32 7.04v1.28c0.64 3.84-2.56 7.68-7.04 8.32h-0.64zM654.72 188.16c-3.84 0-6.4-2.56-7.68-5.76v-1.28c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76v1.28c0.64 3.84-1.92 8.32-5.76 8.96h-1.28zM707.2 448.64c-3.84 0-6.4-2.56-7.68-5.76l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96h-1.28z m-4.48-21.76c-3.84 0-6.4-2.56-7.68-5.76l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96h-1.28z m-4.48-21.76c-3.84 0-6.4-2.56-7.68-6.4l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96 0 0.64-0.64 0.64-1.28 0.64z m-3.84-21.12c-3.84 0-6.4-2.56-7.68-6.4l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96-0.64 0-1.28 0.64-1.28 0.64z m-4.48-21.76c-3.84 0-6.4-2.56-7.68-6.4l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96-0.64 0.64-1.28 0.64-1.28 0.64z m-4.48-21.76c-3.84 0-6.4-2.56-7.68-5.76l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96h-1.28z m-4.48-21.76c-3.84 0-6.4-2.56-7.68-5.76l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96h-1.28z m-4.48-21.76c-3.84 0-6.4-2.56-7.68-5.76l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96h-1.28zM672 275.2c-3.84 0-6.4-2.56-7.68-6.4l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96 0 0.64-0.64 0.64-1.28 0.64z m-4.48-21.76c-3.84 0-6.4-2.56-7.68-6.4l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96 0 0.64-0.64 0.64-1.28 0.64z m-3.84-21.76c-3.84 0-6.4-2.56-7.68-6.4l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96-0.64 0.64-1.28 0.64-1.28 0.64z m-4.48-21.76c-3.84 0-6.4-2.56-7.68-5.76l-0.64-3.2c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76l0.64 3.2c0.64 3.84-1.92 8.32-5.76 8.96h-1.28zM711.68 469.12c-3.84 0-6.4-2.56-7.68-5.76v-1.28c-0.64-3.84 1.92-8.32 5.76-8.96 3.84-0.64 8.32 1.92 8.96 5.76v1.28c0.64 3.84-1.92 8.32-5.76 8.96h-1.28zM732.8 188.16c-3.2 0-6.4-1.92-7.04-5.12l-0.64-1.28c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 1.28c1.28 3.84-1.28 8.32-5.12 9.6h-2.56zM812.16 450.56c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6-0.64-0.64-1.92 0-2.56 0z m-5.76-20.48c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6h-2.56z m-6.4-19.84c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6-1.28-0.64-1.92 0-2.56 0z m-5.76-20.48c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6h-2.56z m-6.4-19.84c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6-1.28-0.64-1.92 0-2.56 0z m-6.4-20.48c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6h-2.56z m-5.76-19.84c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6-1.28-0.64-1.92 0-2.56 0z m-6.4-20.48c-3.2 0-6.4-1.92-7.04-5.12l-0.64-3.2c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6-0.64 0.64-1.28 0.64-2.56 0.64z m-5.76-20.48c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6h-2.56z m-6.4-19.84c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6h-2.56z m-5.76-20.48c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6h-2.56z m-6.4-19.84c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6h-2.56z m-5.76-20.48c-3.2 0-6.4-1.92-7.04-5.12l-0.64-2.56c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 2.56c1.28 3.84-1.28 8.32-5.12 9.6h-2.56zM817.92 469.12c-3.2 0-6.4-1.92-7.04-5.12l-0.64-1.28c-1.28-3.84 1.28-8.32 5.12-9.6 3.84-1.28 8.32 1.28 9.6 5.12l0.64 1.28c1.28 3.84-1.28 8.32-5.12 9.6h-2.56zM352.64 188.16h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96v-1.28c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96v1.28c-1.28 3.2-4.48 5.76-7.68 5.76zM299.52 448.64h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-0.64 3.84-3.84 5.76-7.68 5.76z m4.48-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-0.64 3.84-3.84 5.76-7.68 5.76z m4.48-21.76H307.2c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-1.28 3.84-4.48 5.76-7.68 5.76z m4.48-21.12h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-1.28 2.56c-0.64 3.84-3.84 6.4-7.04 6.4z m4.48-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-1.28 3.2-4.48 5.76-7.68 5.76z m4.48-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-1.28 3.2-4.48 5.76-7.68 5.76z m3.84-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-0.64 3.2-3.84 5.76-7.68 5.76z m4.48-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-0.64 3.2-3.84 5.76-7.68 5.76z m4.48-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-6.4 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 2.56c-0.64 3.84-3.84 6.4-7.68 6.4z m4.48-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-1.28 3.2-4.48 5.76-7.68 5.76z m4.48-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-1.28 3.2-4.48 5.76-7.68 5.76z m4.48-21.76h-1.28c-3.84-0.64-7.04-5.12-5.76-8.96l0.64-3.2c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96l-0.64 3.2c-1.28 3.2-4.48 5.76-7.68 5.76zM295.68 469.12H294.4c-3.84-0.64-7.04-5.12-5.76-8.96v-1.28c0.64-3.84 5.12-7.04 8.96-5.76 3.84 0.64 7.04 5.12 5.76 8.96v1.28c-1.28 3.2-4.48 5.76-7.68 5.76zM273.92 188.16c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-1.28c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 1.92c-1.28 3.2-4.48 5.12-7.68 5.12zM194.56 450.56c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.28 3.2-4.48 5.76-7.68 5.76z m6.4-20.48c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.92 3.84-4.48 5.76-7.68 5.76z m5.76-19.84c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.12-5.12-9.6l0.64-2.56c1.28-3.84 5.12-6.4 9.6-5.12 3.84 1.28 6.4 5.12 5.12 9.6l-0.64 2.56c-1.28 3.2-4.48 5.76-7.68 5.76z m6.4-20.48c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.28 3.84-4.48 5.76-7.68 5.76z m5.76-19.84c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.28 3.2-4.48 5.76-7.68 5.76z m6.4-20.48c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.12-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.28 3.84-4.48 5.76-7.68 5.76z m5.76-19.84c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.28 3.2-3.84 5.76-7.68 5.76z m6.4-20.48c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.12-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.12 5.12 9.6l-0.64 2.56c-1.28 3.84-4.48 5.76-7.68 5.76z m6.4-20.48c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.92 3.84-4.48 5.76-7.68 5.76zM249.6 268.8c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.28 3.84-4.48 5.76-7.68 5.76z m6.4-20.48c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.12-5.12-9.6l0.64-2.56c1.28-3.84 5.12-6.4 9.6-5.12 3.84 1.28 6.4 5.12 5.12 9.6l-1.28 3.2c-1.28 3.2-3.84 5.12-7.04 5.12z m5.76-19.84c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-0.64 2.56c-1.28 3.84-4.48 5.76-7.68 5.76z m6.4-20.48c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.76-5.12-9.6l0.64-2.56c1.28-3.84 5.76-6.4 9.6-5.12 3.84 1.28 6.4 5.76 5.12 9.6l-1.28 3.2c-0.64 3.2-3.84 5.12-7.04 5.12zM188.8 469.12c-0.64 0-1.28 0-1.92-0.64-3.84-1.28-6.4-5.12-5.12-9.6l0.64-1.28c1.28-3.84 5.12-6.4 9.6-5.12 3.84 1.28 6.4 5.12 5.12 9.6l-0.64 1.28c-1.28 3.84-4.48 5.76-7.68 5.76z" fill="#211D1C" p-id="111766"></path><path d="M430.72 188.16h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-1.28c0.64-4.48 4.48-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v1.28c-0.64 4.48-3.84 7.04-7.68 7.04zM404.48 448.64h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-4.48 3.84-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 4.48-3.84 7.04-7.68 7.04z m1.92-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-3.84 3.84-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 4.48-3.84 7.04-7.68 7.04z m1.92-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-3.84 4.48-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c0 4.48-3.84 7.04-7.68 7.04z m2.56-21.12h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-3.84 4.48-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 3.84-3.84 7.04-7.68 7.04z m1.92-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-4.48 3.84-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c0 3.84-3.84 7.04-7.68 7.04z m2.56-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-3.84 3.84-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 3.84-3.84 7.04-7.68 7.04z m1.92-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32V307.2c0.64-4.48 3.84-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 3.84-3.84 7.04-7.68 7.04z m2.56-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-3.84 4.48-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 3.84-3.84 7.04-7.68 7.04z m1.92-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-3.84 4.48-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 3.84-3.84 7.04-7.68 7.04z m2.56-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-3.84 4.48-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 3.84-4.48 7.04-7.68 7.04z m1.92-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-3.2c0.64-4.48 3.84-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c-0.64 3.84-3.84 7.04-7.68 7.04z m1.92-21.76h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32V198.4c0.64-3.84 3.84-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v3.2c0 3.84-3.84 7.04-7.68 7.04zM401.92 469.12h-0.64c-4.48-0.64-7.04-3.84-7.04-8.32v-1.28c0.64-3.84 3.84-7.04 8.32-7.04 4.48 0.64 7.04 3.84 7.04 8.32v1.28c0 3.84-3.84 7.04-7.68 7.04z" fill="#211D1C" p-id="111767"></path><path d="M881.92 929.92H124.8c-4.48 0-7.68-3.2-7.68-7.68V515.84c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v398.72h742.4V515.84c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v406.4c-0.64 4.48-3.84 7.68-8.32 7.68z" fill="#211D1C" p-id="111768"></path><path d="M616.96 929.92H390.4c-4.48 0-7.68-3.2-7.68-7.68V585.6c0-4.48 3.2-7.68 7.68-7.68h226.56c4.48 0 7.68 3.2 7.68 7.68v336.64c0 4.48-3.84 7.68-7.68 7.68z m-218.88-15.36h211.2V593.28h-211.2v321.28z" fill="#211D1C" p-id="111769"></path><path d="M838.4 857.6h-179.2c-4.48 0-7.68-3.2-7.68-7.68V585.6c0-4.48 3.2-7.68 7.68-7.68h179.2c4.48 0 7.68 3.2 7.68 7.68v264.32c0 4.48-3.2 7.68-7.68 7.68z m-170.88-14.72h163.84v-249.6h-163.84v249.6zM346.88 857.6h-179.2c-4.48 0-7.68-3.2-7.68-7.68V585.6c0-4.48 3.2-7.68 7.68-7.68h179.2c4.48 0 7.68 3.2 7.68 7.68v264.32c-0.64 4.48-3.84 7.68-7.68 7.68z m-171.52-14.72H339.2v-249.6H175.36v249.6z" fill="#00ABE0" p-id="111770"></path><path d="M438.4 136.96H286.08c-4.48 0-7.68-3.2-7.68-7.68v-51.2c0-4.48 3.2-7.68 7.68-7.68h152.32c4.48 0 7.68 3.2 7.68 7.68v51.2c0 3.84-3.84 7.68-7.68 7.68zM293.76 121.6h136.96v-35.84H293.76V121.6z" fill="#211D1C" p-id="111771"></path><path d="M454.4 85.76H270.08c-4.48 0-7.68-3.2-7.68-7.68v-51.2c0-3.84 3.2-7.68 7.68-7.68H454.4c4.48 0 7.68 3.2 7.68 7.68v51.2c0 4.48-3.84 7.68-7.68 7.68zM277.76 70.4h168.96V34.56H277.76V70.4z" fill="#211D1C" p-id="111772"></path><path d="M346.88 625.28h-179.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h179.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM838.4 625.28h-179.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h179.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="111773"></path><path d="M441.6 800.64c-14.72 0-26.24-12.16-26.24-26.24 0-14.72 12.16-26.24 26.24-26.24 14.72 0 26.24 12.16 26.24 26.24 0 14.72-11.52 26.24-26.24 26.24z m0-37.76c-6.4 0-11.52 5.12-11.52 11.52s5.12 11.52 11.52 11.52 11.52-5.12 11.52-11.52c-0.64-6.4-5.12-11.52-11.52-11.52zM963.2 523.52H43.52c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h919.68c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM984.96 1016.96H22.4c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h962.56c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111774"></path></svg>'},
          { name: '屋子', svgCode: '<svg t="1756148187560" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="111929" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M645.76 949.76H67.84c-4.48 0-7.68-3.2-7.68-7.68V364.16c0-4.48 3.2-7.68 7.68-7.68h577.92c4.48 0 7.68 3.2 7.68 7.68v577.92c-0.64 3.84-3.84 7.68-7.68 7.68zM75.52 934.4h562.56V371.84H75.52V934.4zM1016.32 371.84c-2.56 0-5.12-1.28-6.4-3.2L851.2 130.56l-158.72 238.08c-2.56 3.2-7.04 4.48-10.24 1.92-3.2-2.56-4.48-7.04-1.92-10.24l165.12-247.68c1.28-1.92 3.84-3.2 6.4-3.2s5.12 1.28 6.4 3.2l165.12 247.68c2.56 3.2 1.28 8.32-1.92 10.24-1.92 0.64-3.84 1.28-5.12 1.28zM26.88 371.84c-1.28 0-3.2-0.64-4.48-1.28-3.2-2.56-4.48-7.04-1.92-10.24L185.6 112.64c1.28-1.92 3.84-3.2 6.4-3.2h122.88c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68H196.48L33.28 368.64c-1.28 1.92-3.84 3.2-6.4 3.2z" fill="#211D1C" p-id="111930"></path><path d="M975.36 949.76h-330.24c-4.48 0-7.68-3.2-7.68-7.68V364.16c0-4.48 3.2-7.68 7.68-7.68h40.96c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68H652.8V934.4h314.88V366.72l-143.36-215.04c-2.56-3.2-1.28-8.32 1.92-10.24 3.2-2.56 8.32-1.28 10.24 1.92l144.64 216.96c0.64 1.28 1.28 2.56 1.28 4.48v577.92c0.64 3.2-2.56 7.04-7.04 7.04z" fill="#211D1C" p-id="111931"></path><path d="M1016.32 371.84h-40.96c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h40.96c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM67.84 371.84H26.88c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h40.96c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM851.84 124.16H439.68c-4.48 0-7.68-3.2-7.68-7.68S435.2 108.8 439.68 108.8h412.16c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="111932"></path><path d="M439.68 206.72H315.52c-4.48 0-7.68-3.2-7.68-7.68V74.88c0-4.48 3.2-7.68 7.68-7.68h124.16c4.48 0 7.68 3.2 7.68 7.68v124.16c0 4.48-3.2 7.68-7.68 7.68z m-116.48-15.36h109.44v-108.8H323.2v108.8z" fill="#00ABE0" p-id="111933"></path><path d="M469.76 81.92H285.44c-4.48 0-7.68-3.2-7.68-7.68V33.28c0-4.48 3.2-7.68 7.68-7.68h184.32c4.48 0 7.68 3.2 7.68 7.68v41.6c0 3.84-3.2 7.04-7.68 7.04z m-176.64-14.72h169.6V40.32H293.12v26.88z" fill="#00ABE0" p-id="111934"></path><path d="M922.24 949.76h-223.36c-4.48 0-7.68-3.2-7.68-7.68V529.28c0-4.48 3.2-7.68 7.68-7.68h223.36c4.48 0 7.68 3.2 7.68 7.68v412.8c0 3.84-3.2 7.68-7.68 7.68z m-215.68-15.36h208V536.96h-208V934.4z" fill="#211D1C" p-id="111935"></path><path d="M752.64 778.24h-24.32c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h16.64v-49.92h-16.64c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h24.32c4.48 0 7.68 3.2 7.68 7.68v65.28c-0.64 4.48-3.84 7.68-7.68 7.68zM512 755.2H194.56c-4.48 0-7.68-3.2-7.68-7.68V535.04c0-4.48 3.2-7.68 7.68-7.68H512c4.48 0 7.68 3.2 7.68 7.68v212.48c0 4.48-3.2 7.68-7.68 7.68z m-310.4-15.36h302.72V542.72H201.6v197.12z" fill="#00ABE0" p-id="111936"></path><path d="M512 608H194.56c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68H512c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="111937"></path><path d="M512 755.2c-0.64 0-1.92 0-2.56-0.64-1.28-0.64-129.92-51.2-129.92-219.52 0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68c0 158.08 119.04 205.44 119.68 205.44 3.84 1.28 5.76 5.76 4.48 9.6-1.28 3.2-3.84 5.12-7.04 5.12zM194.56 755.2c-3.2 0-5.76-1.92-7.04-4.48-1.92-3.84 0-8.32 3.84-10.24 5.12-1.92 120.32-53.76 120.32-205.44 0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68c0 161.92-128 218.88-129.28 219.52-1.28 0.64-2.56 0.64-3.2 0.64z" fill="#00ABE0" p-id="111938"></path><path d="M355.84 949.76c-4.48 0-7.68-3.2-7.68-7.68 0-41.6-33.92-74.88-74.88-74.88-41.6 0-74.88 33.92-74.88 74.88 0 4.48-3.2 7.68-7.68 7.68s-7.68-3.2-7.68-7.68c0-49.92 40.32-90.24 90.24-90.24s90.24 40.32 90.24 90.24c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111939"></path><path d="M284.16 867.84c-1.28 0-2.56 0-3.84-0.64-3.84-1.92-5.12-6.4-3.2-10.24 16-28.8 46.08-46.72 78.72-46.72 32.64 0 62.72 17.92 78.72 46.08 1.92 3.84 0.64 8.32-3.2 10.24-3.84 1.92-8.32 0.64-10.24-3.2-13.44-23.68-38.4-38.4-65.28-38.4-27.52 0-52.48 14.72-65.28 38.4-0.64 3.2-3.84 4.48-6.4 4.48z" fill="#211D1C" p-id="111940"></path><path d="M521.6 949.76c-4.48 0-7.68-3.2-7.68-7.68 0-41.6-33.92-74.88-74.88-74.88s-74.88 33.92-74.88 74.88c0 4.48-3.2 7.68-7.68 7.68s-7.68-3.2-7.68-7.68c0-49.92 40.32-90.24 90.24-90.24s90.24 40.32 90.24 90.24c0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="111941"></path></svg>'},
          { name: '屋子', svgCode: '<svg t="1756148313727" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="112271" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M899.84 551.04h-39.04c-4.48 0-7.68-3.2-7.68-7.68V418.56c0-4.48 3.2-7.68 7.68-7.68h39.04c4.48 0 7.68 3.2 7.68 7.68v124.8c0 4.48-3.84 7.68-7.68 7.68z m-32-15.36h24.32V426.24h-24.32v109.44z" fill="#00ABE0" p-id="112272"></path><path d="M910.08 426.24h-60.8c-4.48 0-7.68-3.2-7.68-7.68v-38.4c0-4.48 3.2-7.68 7.68-7.68h60.8c4.48 0 7.68 3.2 7.68 7.68v38.4c0 4.48-3.2 7.68-7.68 7.68z m-53.12-15.36h45.44v-23.04h-45.44v23.04zM292.48 209.92c-4.48 0-7.68-3.2-7.68-7.68V71.68c0-4.48 3.2-7.68 7.68-7.68h113.92c4.48 0 7.68 3.2 7.68 7.68v48.64c0 4.48-3.2 7.68-7.68 7.68s-7.68-3.2-7.68-7.68v-40.96H300.16v122.88c0 4.48-3.2 7.68-7.68 7.68zM672 956.16H444.16c-4.48 0-7.68-3.2-7.68-7.68v-264.32c0-4.48 3.2-7.68 7.68-7.68H672c4.48 0 7.68 3.2 7.68 7.68v264.32c0 4.48-3.84 7.68-7.68 7.68z m-220.16-14.72h212.48v-249.6H451.84v249.6z" fill="#00ABE0" p-id="112273"></path><path d="M899.84 956.16H672c-4.48 0-7.68-3.2-7.68-7.68v-264.32c0-4.48 3.2-7.68 7.68-7.68h227.84c4.48 0 7.68 3.2 7.68 7.68v264.32c0 4.48-3.84 7.68-7.68 7.68z m-220.16-14.72h212.48v-249.6h-212.48v249.6zM483.84 728.96h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM613.76 728.96h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0H588.8c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM633.6 728.96h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM483.84 766.72h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68zM613.76 766.72h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68z m-21.76 0H588.8c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68zM633.6 766.72h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68zM483.84 803.84h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM613.76 803.84h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0H588.8c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM633.6 803.84h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM483.84 841.6h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68zM613.76 841.6h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68z m-21.76 0H588.8c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68zM633.6 841.6h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68zM483.84 878.72h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM613.76 878.72h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0H588.8c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM633.6 878.72h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM483.84 915.84h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM613.76 915.84h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0H588.8c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM633.6 915.84h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="112274"></path><path d="M711.04 728.96h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM840.96 728.96h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM860.8 728.96h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM711.04 766.72h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68zM840.96 766.72h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68zM860.8 766.72h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68zM711.04 803.84h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM840.96 803.84h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM860.8 803.84h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="112275"></path><path d="M711.04 841.6h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68zM840.96 841.6h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68zM860.8 841.6h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="112276"></path><path d="M711.04 878.72h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM840.96 878.72h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM860.8 878.72h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="112277"></path><path d="M711.04 915.84h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM840.96 915.84h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM860.8 915.84h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="112278"></path><path d="M405.76 956.16H103.04c-4.48 0-7.68-3.2-7.68-7.68V570.24c0-1.92 0.64-3.84 1.92-5.12l151.68-151.68c3.2-3.2 7.68-3.2 10.88 0l151.68 151.68c1.28 1.28 1.92 3.2 1.92 5.12v378.88c0 3.84-3.2 7.04-7.68 7.04z m-295.04-14.72h288V573.44L254.72 429.44 110.72 573.44v368z" fill="#211D1C" p-id="112279"></path><path d="M936.96 956.16H407.04c-4.48 0-7.68-3.2-7.68-7.68V570.24c0-4.48 3.2-7.68 7.68-7.68h529.92c4.48 0 7.68 3.2 7.68 7.68v378.88c0 3.84-3.2 7.04-7.68 7.04z m-522.24-14.72h515.2V577.92H414.72v363.52zM103.04 577.92h-37.12c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h37.12c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM330.88 956.16H179.84c-4.48 0-7.68-3.2-7.68-7.68v-227.2c0-4.48 3.2-7.68 7.68-7.68h151.68c4.48 0 7.68 3.2 7.68 7.68v227.2c-0.64 4.48-3.84 7.68-8.32 7.68z m-143.36-14.72h136.32V729.6H187.52v211.84zM785.92 551.04c-4.48 0-7.68-3.2-7.68-7.68V265.6L520.32 81.28 261.76 265.6v115.2c0 4.48-3.2 7.68-7.68 7.68s-7.68-3.2-7.68-7.68V261.76c0-2.56 1.28-4.48 3.2-6.4l265.6-190.08c2.56-1.92 6.4-1.92 8.96 0l265.6 190.08c1.92 1.28 3.2 3.84 3.2 6.4v281.6c0.64 4.48-3.2 7.68-7.04 7.68z" fill="#211D1C" p-id="112280"></path><path d="M209.28 269.44c-2.56 0-4.48-1.28-6.4-3.2-2.56-3.2-1.92-8.32 1.92-10.88L515.84 33.92c2.56-1.92 6.4-1.92 8.96 0L835.2 256c2.56 1.92 3.84 5.12 2.56 8.32-1.28 3.2-3.84 5.12-7.04 5.12h-44.8c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h21.12l-287.36-204.8-305.92 218.88c-1.28 0.64-2.56 1.28-4.48 1.28z" fill="#211D1C" p-id="112281"></path><path d="M254.72 269.44h-44.8c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h44.8c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM65.28 577.92c-1.92 0-3.84-0.64-5.12-1.92-3.2-3.2-3.2-7.68 0-10.88l188.8-188.8c3.2-3.2 7.68-3.2 10.88 0l160 160h554.88c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68H416.64c-1.92 0-3.84-0.64-5.12-1.92L254.72 391.68 71.04 575.36c-1.28 1.28-3.84 2.56-5.76 2.56z" fill="#211D1C" p-id="112282"></path><path d="M936.96 577.92c-2.56 0-4.48-1.28-6.4-3.2-2.56-3.2-1.92-8.32 1.92-10.88l37.12-26.88c3.2-2.56 8.32-1.92 10.88 1.92 2.56 3.2 1.92 8.32-1.92 10.88l-37.12 26.88c-1.28 0.64-2.56 1.28-4.48 1.28zM520.32 410.24H368.64c-4.48 0-7.68-3.2-7.68-7.68V250.88c0-4.48 3.2-7.68 7.68-7.68h151.68c4.48 0 7.68 3.2 7.68 7.68v151.68c-0.64 4.48-3.84 7.68-7.68 7.68z m-144-15.36h136.32V258.56H376.32v136.32z" fill="#211D1C" p-id="112283"></path><path d="M672 410.88H520.32c-4.48 0-7.68-3.2-7.68-7.68V250.88c0-4.48 3.2-7.68 7.68-7.68H672c4.48 0 7.68 3.2 7.68 7.68V403.2c0 3.84-3.84 7.68-7.68 7.68z m-144.64-15.36h136.96V258.56H527.36v136.96z" fill="#211D1C" p-id="112284"></path><path d="M671.36 307.84H368.64c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h302.72c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM330.88 670.08H179.84c-4.48 0-7.68-3.2-7.68-7.68V565.76c0-1.92 0.64-3.84 1.92-5.12l53.12-54.4c1.28-1.28 3.2-2.56 5.12-2.56h44.8c1.92 0 3.84 0.64 5.12 2.56l53.12 54.4c1.28 1.28 1.92 3.2 1.92 5.12v97.28c1.28 3.84-1.92 7.04-6.4 7.04z m-143.36-14.72h136.32V568.96l-49.28-49.92h-38.4l-49.28 49.92v86.4z" fill="#211D1C" p-id="112285"></path><path d="M322.56 567.68h-134.4c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h133.76c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.04 7.68z" fill="#211D1C" p-id="112286"></path><path d="M254.72 670.08c-4.48 0-7.68-3.2-7.68-7.68v-102.4c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v102.4c-0.64 4.48-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112287"></path></svg>'},
          { name: '屋子', svgCode: '<svg t="1756148217936" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="112096" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"><path d="M289.28 431.36c-1.92 0-3.84-0.64-5.12-1.92L224 369.28c-3.2-3.2-3.2-7.68 0-10.88s7.68-3.2 10.88 0l60.16 60.16c3.2 3.2 3.2 7.68 0 10.88-1.92 0.64-3.84 1.92-5.76 1.92z" fill="#00ABE0" p-id="112097"></path><path d="M821.76 270.08c-4.48 0-7.68-3.2-7.68-7.68V128h-95.36v34.56c0 4.48-3.2 7.68-7.68 7.68s-7.68-3.2-7.68-7.68v-42.24c0-4.48 3.2-7.68 7.68-7.68h110.08c4.48 0 7.68 3.2 7.68 7.68V262.4c0.64 3.84-2.56 7.68-7.04 7.68z" fill="#211D1C" p-id="112098"></path><path d="M872.96 431.36c-1.92 0-3.84-0.64-5.12-1.92-3.2-3.2-3.2-7.68 0-10.88L928 358.4c3.2-3.2 7.68-3.2 10.88 0s3.2 7.68 0 10.88l-60.16 60.16c-1.92 0.64-3.84 1.92-5.76 1.92zM518.4 928H390.4c-4.48 0-7.68-3.2-7.68-7.68v-256.64c0-4.48 3.2-7.68 7.68-7.68h128c4.48 0 7.68 3.2 7.68 7.68v256.64c0 4.48-3.2 7.68-7.68 7.68z m-120.32-14.72h113.28v-241.92H398.08v241.92z" fill="#00ABE0" p-id="112099"></path><path d="M922.24 961.28H78.72c-4.48 0-7.68-3.2-7.68-7.68v-33.28c0-4.48 3.2-7.68 7.68-7.68h843.52c4.48 0 7.68 3.2 7.68 7.68v33.28c0 4.48-3.84 7.68-7.68 7.68z m-835.84-15.36h828.16V928H86.4v17.92z" fill="#211D1C" p-id="112100"></path><path d="M872.96 928H289.28c-4.48 0-7.68-3.2-7.68-7.68V343.68c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v568.96h568.32V343.68c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v576.64c0 4.48-3.2 7.68-7.68 7.68zM154.24 928H121.6c-4.48 0-7.68-3.2-7.68-7.68v-194.56c0-4.48 3.2-7.68 7.68-7.68h33.28c4.48 0 7.68 3.2 7.68 7.68v194.56c-0.64 4.48-3.84 7.68-8.32 7.68z m-25.6-14.72h17.92v-179.2h-17.92v179.2z" fill="#211D1C" p-id="112101"></path><path d="M289.28 766.08H78.72c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h210.56c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM289.28 825.6H78.72c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h210.56c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM289.28 885.76H78.72c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h210.56c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68zM549.12 928H360.32c-4.48 0-7.68-3.2-7.68-7.68V633.6c0-4.48 3.2-7.68 7.68-7.68h188.8c4.48 0 7.68 3.2 7.68 7.68v287.36c-0.64 3.84-3.84 7.04-7.68 7.04z m-181.12-14.72h173.44v-272H368v272z" fill="#211D1C" p-id="112102"></path><path d="M805.76 830.08H616.96c-4.48 0-7.68-3.2-7.68-7.68V633.6c0-4.48 3.2-7.68 7.68-7.68h188.8c4.48 0 7.68 3.2 7.68 7.68v188.8c0 3.84-3.2 7.68-7.68 7.68z m-181.12-15.36h173.44v-173.44H624.64v173.44z" fill="#00ABE0" p-id="112103"></path><path d="M821.76 856.32H600.96c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h220.8c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="112104"></path><path d="M711.68 830.08c-4.48 0-7.68-3.2-7.68-7.68V633.6c0-4.48 3.2-7.68 7.68-7.68s7.68 3.2 7.68 7.68v188.8c0 3.84-3.84 7.68-7.68 7.68zM518.4 800H390.4c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h128c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z" fill="#00ABE0" p-id="112105"></path><path d="M835.84 366.08H327.04c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h508.8c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112106"></path><path d="M328.32 371.2h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68S332.8 371.2 328.32 371.2zM815.36 371.2h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-22.4 0h-2.56c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-8.32 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S576 371.2 571.52 371.2z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM505.6 371.2h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S509.44 371.2 505.6 371.2z m-22.4 0H480c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM460.8 371.2h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S465.28 371.2 460.8 371.2z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM835.84 371.2h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM835.84 436.48H327.04c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h508.8c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112107"></path><path d="M328.32 441.6h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68S332.8 441.6 328.32 441.6zM815.36 441.6h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-22.4 0h-2.56c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-8.32 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S576 441.6 571.52 441.6z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM505.6 441.6h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-22.4 0H480c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM460.8 441.6h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S465.28 441.6 460.8 441.6z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM835.84 441.6h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM835.84 506.88H327.04c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h508.8c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112108"></path><path d="M328.32 512h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68S332.8 512 328.32 512zM815.36 512h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-22.4 0h-2.56c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-8.32 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S576 512 571.52 512z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM505.6 512h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-22.4 0H480c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM460.8 512h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S465.28 512 460.8 512z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM835.84 512h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM686.08 225.28H476.16c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h209.28c4.48 0 7.68 3.2 7.68 7.68 0.64 4.48-3.2 7.68-7.04 7.68z" fill="#211D1C" p-id="112109"></path><path d="M478.08 230.4h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM666.24 230.4h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-20.48 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S608 230.4 603.52 230.4zM582.4 230.4h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S586.88 230.4 582.4 230.4z m-20.48 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0H537.6c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM499.2 230.4h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 4.48-3.84 7.68-7.68 7.68zM686.08 230.4h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112110"></path><path d="M760.96 295.68H401.92c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h359.04c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112111"></path><path d="M403.2 300.8h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68S407.04 300.8 403.2 300.8zM741.12 300.8h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM614.4 300.8h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S618.24 300.8 614.4 300.8z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S576 300.8 572.16 300.8z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0H505.6c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-21.12 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM760.96 300.8h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112112"></path><path d="M835.84 577.28H327.04c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h508.8c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112113"></path><path d="M328.32 582.4h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68S332.8 582.4 328.32 582.4zM815.36 582.4h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-22.4 0h-2.56c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-8.32 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S576 582.4 571.52 582.4z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM505.6 582.4h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S509.44 582.4 505.6 582.4z m-22.4 0H480c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68zM460.8 582.4h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68S465.28 582.4 460.8 582.4z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68zM835.84 582.4h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68s-3.84 7.68-7.68 7.68z" fill="#211D1C" p-id="112114"></path><path d="M602.88 862.08H601.6c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68zM801.28 862.08h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z m-21.76 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68-0.64 3.84-3.84 7.68-7.68 7.68z m-22.4 0h-3.2c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h3.2c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68zM821.76 862.08h-1.28c-4.48 0-7.68-3.2-7.68-7.68s3.2-7.68 7.68-7.68h1.28c4.48 0 7.68 3.2 7.68 7.68 0 3.84-3.2 7.68-7.68 7.68z" fill="#211D1C" p-id="112115"></path><path d="M987.52 419.2h-38.4c-1.92 0-3.84-0.64-5.12-1.92L581.12 92.16 218.88 417.28c-1.28 1.28-3.2 1.92-5.12 1.92h-38.4c-3.2 0-5.76-1.92-7.04-5.12-1.28-3.2-0.64-6.4 1.92-8.32L576 39.04c3.2-2.56 7.04-2.56 10.24 0l406.4 367.36c2.56 1.92 3.2 5.12 1.92 8.32-1.28 2.56-3.84 4.48-7.04 4.48z m-35.84-14.72h16L581.12 55.04 194.56 404.48h16L576 76.8c2.56-2.56 7.04-2.56 10.24 0l365.44 327.68z" fill="#00ABE0" p-id="112116"></path></svg>'},
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
          /* {name: '', svgCode: ''}, */
          { name: '男孩女孩', svgCode: '<svg width="100%" height="100%" preserveAspectRatio="xMidYMid meet" viewBox="0 -5.15 289.941 289.941" xmlns="http://www.w3.org/2000/svg"><defs><style>.a{fill:#ffffff;}.b{fill:#211715;}.c{fill:#957f6e;}.d{fill:#f7a19f;}.e{fill:#f2635f;}.f{fill:#7a7473;}.g{fill:#5394cf;}.h{fill:#b2cfe9;}</style></defs><path class="a" d="M261.009,162.295l2.124,9.888c.3,1.054.714,3.479.914,4.557.185,1,.518,3.111.963,5.444a3.139,3.139,0,0,0,2.6,2.74c2.207.279,4.762-.765,5.218-2.97a52.429,52.429,0,0,0,6.417,4.437c1.911,1.121,4.051,2.152,6.248,1.867a2.5,2.5,0,0,0,2.437-2.729c.106-3.417-2.776-6.07-5.267-8.411a72.9,72.9,0,0,1-9.236-10.531,38.028,38.028,0,0,1-2.609-5.4l-1.844-4.409-8.445,3.333Z"/><path class="a" d="M243.654,47.524a4.307,4.307,0,0,1,3.445-1.008,4.069,4.069,0,0,1,2.923,1.943,5.756,5.756,0,0,1,.6,2.313,17.218,17.218,0,0,1-1.757,9.129,10.939,10.939,0,0,1-2.83,3.716,3.3,3.3,0,0,1-3.31.773l-.5-.149c-.3,1.2-.707,2.245-.887,2.757-.986,2.5-6.536,11.4-13.5,14.565.07.549.16,1.177.309,2,.36,2.12.96,4.52,3.78,6.08.19.06,3.87,1.81,4.16,1.93,0,0-1.155,14.94-21.3,14.94-19.26,0-19.6-14.94-19.6-14.94.3-.12,3.97-1.87,4.17-1.93,2.81-1.56,3.41-3.96,3.78-6.08.089-.506.159-.933.209-1.311a27.152,27.152,0,0,1-9.8-7.229,30.945,30.945,0,0,1-6.137-10.43l-.734.2a4.116,4.116,0,0,1-3.73-1.179,10.942,10.942,0,0,1-2.831-3.716,17.217,17.217,0,0,1-1.756-9.129,5.739,5.739,0,0,1,.6-2.313,4.069,4.069,0,0,1,2.923-1.943,4.306,4.306,0,0,1,3.445,1.008S183.977,24.443,214.5,24.443,243.654,47.524,243.654,47.524Z"/><path class="b" d="M195.727,93.505c1.417-.584,2.785-1.286,4.178-1.925l.316-.142c.249-.115-.55.229-.352.147a6.248,6.248,0,0,0,.575-.251,8.615,8.615,0,0,0,1.871-1.394,9.044,9.044,0,0,0,2.161-3.452,17.387,17.387,0,0,0,.808-3.71,2.216,2.216,0,0,0-.2-1.541,2,2,0,0,0-3.655.478,20.911,20.911,0,0,1-.609,3.109c-.066.221-.142.438-.219.655a.934.934,0,0,0-.064.163c0,.007.185-.4.088-.208-.064.122-.116.251-.18.373a6.6,6.6,0,0,1-.4.678c-.042.061-.288.4-.1.151s-.116.127-.175.191c-.184.2-.382.38-.584.561-.275.247.267-.177-.047.04-.145.1-.289.2-.439.292-.369.229-.022.027.111.008a2.472,2.472,0,0,0-.523.221c-.087.037-.173.076-.259.115-.664.3-1.323.614-1.983.924l-1.14.534c-.235.11-1.214.529-.238.126a2.2,2.2,0,0,0-1.2.919,2.04,2.04,0,0,0-.2,1.541,2.019,2.019,0,0,0,2.46,1.4Z"/><path class="b" d="M225.845,81.557c.336,2.608.682,5.323,2.339,7.467a8.5,8.5,0,0,0,1.582,1.571,8.115,8.115,0,0,0,1.011.694,4.033,4.033,0,0,0,.638.291c.109.037-.617-.274-.342-.144.661.312,1.328.614,1.99.925s1.339.653,2.023.943a2.2,2.2,0,0,0,1.541.2,2,2,0,0,0,.478-3.655c-.748-.318-1.477-.687-2.213-1.032-.454-.213-.908-.427-1.364-.637-.145-.067-.29-.134-.436-.2a5.745,5.745,0,0,0-.574-.244c-.156.032.432.238.205.054a5,5,0,0,0-.482-.309q-.273-.2.03.033c-.079-.063-.156-.127-.231-.193-.213-.186-.7-.54-.788-.818.173.227.2.255.07.082-.051-.072-.1-.145-.148-.219q-.141-.219-.265-.447c-.033-.061-.171-.442-.225-.457.117.286.136.33.055.131-.03-.077-.059-.154-.088-.232a12.176,12.176,0,0,1-.486-1.87c-.073-.389-.14-.78-.2-1.171q-.05-.309-.095-.62c-.014-.094-.027-.188-.04-.282q.061.462.019.137a2.053,2.053,0,0,0-2-2c-.969.043-2.143.888-2,2Z"/><path class="c" d="M254.081,15.945c-.118-.842-.267-1.716-.458-2.695A12.922,12.922,0,0,0,251.3,8.227c-3.136-4.047-6.478-5.392-11.023-6.1s-9.037,1.183-10.658,6.008c0,0,.017,8.009,1.128,9.676,2.111,3.666,11.786,9.17,11.786,9.17,4.353.835,8.432,3.941,13.767,3.633a23.378,23.378,0,0,1-1.81-9.476A46.7,46.7,0,0,0,254.081,15.945Z"/><path class="b" d="M231.548,8.67c2.486-6.976,12.237-5.138,16.53-1.049a12.5,12.5,0,0,1,3.155,4.543,23.021,23.021,0,0,1,1.127,6.392c.16,2.146.131,4.3.4,6.44a24.337,24.337,0,0,0,1.816,6.632l1.727-3.01c-4.765.2-8.7-2.63-13.235-3.562-2.512-.517-3.587,3.338-1.063,3.857a46.011,46.011,0,0,1,6.691,2.312,19.485,19.485,0,0,0,7.607,1.393,2.031,2.031,0,0,0,1.727-3.009c-3.03-7.121-.073-15.7-4.9-22.259A17.165,17.165,0,0,0,245.2,1.271a17.451,17.451,0,0,0-9.61-.958,10.95,10.95,0,0,0-7.9,7.294c-.865,2.429,3,3.475,3.857,1.063Z"/><path class="c" d="M191.267,44.77a18.7,18.7,0,0,1-5.135,1.885s-1,.127-1.787.222a4.174,4.174,0,0,0-1.628-.388c.194,1.9-.971-5.088-.79-9.208a31.059,31.059,0,0,1,13.408-24.5,32.578,32.578,0,0,1,19.329-5.949A34.281,34.281,0,0,1,226.074,8.7a32.456,32.456,0,0,1,4.813,2.158,37.666,37.666,0,0,1,5.511,3.655c.659.573,1.628,1.515,2.266,2.159a30.161,30.161,0,0,1,4.188,5.3A31.633,31.633,0,0,1,247.4,37.281a42.305,42.305,0,0,1-.559,8.991l-.036.22a4.256,4.256,0,0,0-1.789.231c-.719-.406-1.245-.707-1.245-.707-1.477-.844-5.127-3.143-6.42-4.084-.37-.221-.739-.452-1.1-.694-.31-.211-.621-.421-.923-.64-4.574-3.263-8.317-7.843-9.643-12.066-4.036,4.713-9.793,8-14.15,8.177-1.147.191.584-4.4,1.42-6.524-6.661,4.384-14.616,11.036-21.7,14.584"/><path class="b" d="M245.068,48.938a2.22,2.22,0,0,1,3.227.531,5.425,5.425,0,0,1,.386,2.395,14.359,14.359,0,0,1-.205,2.891,15.28,15.28,0,0,1-2.046,5.409,7.542,7.542,0,0,1-1.608,1.884,1.475,1.475,0,0,1-1.563.414c-2.49-.664-3.552,3.193-1.063,3.857,3.162.843,5.639-1.188,7.364-3.648a18.437,18.437,0,0,0,2.989-8.313c.337-2.767.328-6.271-1.912-8.283a6.359,6.359,0,0,0-8.4.035,2.015,2.015,0,0,0,0,2.828,2.043,2.043,0,0,0,2.828,0Z"/><path class="b" d="M240.617,61.707a14.1,14.1,0,0,1-.943,4.034c-.085.242-.181.481-.26.725-.107.333.223-.41.039-.1-.156.265-.271.563-.416.836a34.382,34.382,0,0,1-3.158,4.837c-2.832,3.668-6.6,7.478-11.292,8.507-2.513.551-1.449,4.408,1.064,3.857,5.557-1.218,10.007-5.587,13.37-9.941,2.876-3.723,5.386-7.922,5.6-12.758.112-2.573-3.888-2.568-4,0Z"/><path class="b" d="M186.746,46.11a6.362,6.362,0,0,0-8.4-.035c-2.3,2.067-2.246,5.686-1.881,8.512a18.142,18.142,0,0,0,3.13,8.322c1.781,2.444,4.436,4.515,7.613,3.815a2,2,0,1,0-1.063-3.857c-1.344.3-2.781-1.476-3.433-2.457a15.048,15.048,0,0,1-2.176-5.5,14.347,14.347,0,0,1-.238-2.845,5.721,5.721,0,0,1,.39-2.594,2.22,2.22,0,0,1,3.227-.531,2.053,2.053,0,0,0,2.828,0,2.015,2.015,0,0,0,0-2.828Z"/><path class="b" d="M184.39,61.154A33.112,33.112,0,0,0,192,76.283c4,4.533,9.348,8.282,15.44,9.149a2.067,2.067,0,0,0,2.46-1.4,2.015,2.015,0,0,0-1.4-2.461c-10.486-1.493-18.22-11.6-20.252-21.485-.519-2.519-4.375-1.453-3.858,1.064Z"/><path class="b" d="M248.774,46.8c1.457-8.956.559-18.445-4.437-26.227A34.638,34.638,0,0,0,223.708,5.905a37.037,37.037,0,0,0-25.581,2.814,34.5,34.5,0,0,0-14.05,13.544,33.273,33.273,0,0,0-3.946,12.477,43.893,43.893,0,0,0,.564,12.067,2.015,2.015,0,0,0,2.46,1.4,2.048,2.048,0,0,0,1.4-2.46c-1.042-6.436-.906-13.112,1.81-19.147a30.391,30.391,0,0,1,11.049-12.824c13.04-8.55,31.508-5.742,41.508,6.144,6.006,7.138,7.461,16.829,6,25.825a2.061,2.061,0,0,0,1.4,2.46,2.017,2.017,0,0,0,2.461-1.4Z"/><path class="b" d="M244.784,44.289a83.355,83.355,0,0,1-9.142-5.93c-3.419-2.63-6.662-6.194-8.028-10.358a2.018,2.018,0,0,0-3.342-.883,25.725,25.725,0,0,1-6.55,5.475,17.861,17.861,0,0,1-3.317,1.523,14.641,14.641,0,0,1-1.59.431c-.228.047-.459.092-.69.12-.272.032-.943-.124-.249.09l.882.514a1.458,1.458,0,0,1,.4.883l.006-.174c-.136.156.022-.144.067-.341.128-.558.29-1.107.465-1.652.356-1.1.768-2.19,1.192-3.271.635-1.623-1.551-3.176-2.938-2.258-7.256,4.8-13.9,10.632-21.7,14.584-2.3,1.164-.274,4.617,2.019,3.454,7.793-3.952,14.441-9.785,21.7-14.584l-2.938-2.259a26.7,26.7,0,0,0-1.777,5.6,3.064,3.064,0,0,0,.68,2.846c.947.9,2.331.59,3.484.391,5.312-.915,10.222-4.564,13.686-8.544l-3.343-.883c2.9,8.838,11.348,14.262,19.008,18.679,2.234,1.288,4.251-2.167,2.019-3.454Z"/><path class="b" d="M190.257,43.043c-.668.327-1.34.646-2.025.937l.478-.2a12.6,12.6,0,0,1-3.035.938l.531-.071-.074.01a2.222,2.222,0,0,0-1.414.585,2,2,0,0,0,0,2.829,1.913,1.913,0,0,0,1.414.586,13.184,13.184,0,0,0,3.155-.82c1.016-.4,2.008-.858,2.989-1.338a2.019,2.019,0,0,0,.919-1.2,2.045,2.045,0,0,0-.2-1.542,2.021,2.021,0,0,0-1.2-.919,2.228,2.228,0,0,0-1.541.2Z"/><path class="a" d="M237.318,272.678a16.029,16.029,0,0,0,2.973,2.32,19.506,19.506,0,0,0,12.141,2.492,11.5,11.5,0,0,0,5.159-1.817,6.418,6.418,0,0,0,2.815-4.548c.22-2.609-1.363-5.08-3.218-6.927-4.761-4.738-9.808-9.389-14.013-14.575-2.108,2.9-5.884,3.733-9.268,3.04-3.112-.637-5.884-2.339-8.59-4-2.589-1.592-2.979,5.88-3.04,7.5-.1,2.566-.518,5.954,1.518,7.851a20.512,20.512,0,0,0,6.508,3.54C233.426,268.507,235.038,270.519,237.318,272.678Z"/><path class="a" d="M198.415,272.678a16.029,16.029,0,0,1-2.973,2.32A19.506,19.506,0,0,1,183.3,277.49a11.5,11.5,0,0,1-5.159-1.817,6.415,6.415,0,0,1-2.815-4.548c-.22-2.609,1.363-5.08,3.218-6.927,4.761-4.738,9.808-9.389,14.013-14.575,2.108,2.9,5.884,3.733,9.268,3.04,3.112-.637,5.884-2.339,8.59-4,2.589-1.592,2.979,5.88,3.04,7.5.1,2.566.518,5.954-1.518,7.851a20.512,20.512,0,0,1-6.508,3.54C202.307,268.507,200.7,270.519,198.415,272.678Z"/><path class="a" d="M241.094,250.783c0,.253,0,.513,0,.777a9.91,9.91,0,0,1-7.189,1.1,26.3,26.3,0,0,1-8.266-3.8c-.381-2.094-.667-4.2-.887-6.315,5.359-.009,9.98-.07,16.1-.383q.076,2.985.239,5.97S241.091,249.321,241.094,250.783Z"/><path class="a" d="M193.594,250.31q.188-4.071.406-8.141c6.129.311,10.772.368,16.187.374q-.392,3.31-.623,6.637a24.692,24.692,0,0,1-7.738,3.483,9.48,9.48,0,0,1-8.253-1.906Z"/><path class="b" d="M192.17,239.792q-.313,5.488-.57,10.98a2.014,2.014,0,0,0,2,2,2.043,2.043,0,0,0,2-2q.256-5.492.57-10.98a2.013,2.013,0,0,0-2-2,2.045,2.045,0,0,0-2,2Z"/><path class="b" d="M208.622,239.621c-.433,3.167-.787,6.342-1.012,9.531a2.01,2.01,0,0,0,2,2,2.047,2.047,0,0,0,2-2q.156-2.212.386-4.419.111-1.059.237-2.116.063-.529.131-1.057c.026-.205.053-.411.08-.616.011-.088.023-.176.035-.264-.032.238-.032.24,0,0a2.21,2.21,0,0,0-.2-1.541,2,2,0,0,0-3.655.478Z"/><path class="b" d="M227.4,247.886q-.168-1.006-.311-2.018c-.014-.1-.108-.708-.027-.2-.026-.161-.043-.324-.063-.485q-.061-.488-.117-.973c-.156-1.353-.282-2.708-.391-4.065a2,2,0,0,0-4,0c.236,2.946.565,5.886,1.052,8.8a2.007,2.007,0,0,0,2.46,1.4,2.057,2.057,0,0,0,1.4-2.46Z"/><path class="b" d="M243.1,248.628q-.238-4.426-.29-8.86a2,2,0,1,0-4,0q.047,4.433.29,8.86a2,2,0,0,0,4,0Z"/><path class="b" d="M235.9,274.092a20.143,20.143,0,0,0,10.58,5.228c3.914.635,8.533.469,11.94-1.8a8.252,8.252,0,0,0,3.545-9.592c-1.317-3.8-4.686-6.445-7.468-9.173a131.137,131.137,0,0,1-9.912-10.545c-.905-1.108-2.443-.508-3.141.405-2.639,3.45-7.681,2.356-10.979.706-1.037-.519-2.039-1.106-3.031-1.706a6.181,6.181,0,0,0-2.458-1.135,3.369,3.369,0,0,0-3.356,2.14c-1.108,2.285-1.235,5.046-1.347,7.543a19.889,19.889,0,0,0,.269,6.074,8.012,8.012,0,0,0,3.75,4.645,32.314,32.314,0,0,0,6.066,2.8c2.242.875,3.845,2.789,5.542,4.41,1.861,1.779,4.694-1.045,2.828-2.828a36.341,36.341,0,0,0-4.618-4.1c-1.616-1.091-3.5-1.493-5.233-2.32-1.387-.66-3.4-1.5-4.185-2.906-.8-1.426-.532-3.395-.457-4.953.107-2.216.03-4.516.923-6.55-.108.247.189-.262.225-.364-.13.361-.136.08,0,.051-.136.03-.244.223-.406.262-.559.138-1.2-.318-.3.227.5.3.989.606,1.489.9a26.038,26.038,0,0,0,6.369,2.878c4.6,1.234,9.415.1,12.367-3.76l-3.141.405a126.071,126.071,0,0,0,9.418,10.059c1.531,1.5,3.089,2.986,4.594,4.517a8.019,8.019,0,0,1,2.647,4.734c.307,4.11-5.079,5.262-8.157,5.294a16.587,16.587,0,0,1-11.531-4.377C236.853,269.507,234.019,272.33,235.9,274.092Z"/><path class="b" d="M197,271.264a16.576,16.576,0,0,1-11.531,4.377c-3.075-.036-8.465-1.182-8.157-5.294a8.026,8.026,0,0,1,2.646-4.734c1.5-1.534,3.064-3.012,4.595-4.517a126.071,126.071,0,0,0,9.418-10.059l-3.141-.405a11.088,11.088,0,0,0,10.822,4.081,20.029,20.029,0,0,0,6.4-2.341c.894-.48,1.766-1,2.633-1.531a3.8,3.8,0,0,0,.739-.454c.2-.332.158.064-.017.006-.5-.165-.527.049-.882-.116-.234-.109-.127-.117-.125-.126.031-.1.195.35.191.341-.018-.04.14.409.187.566a14.289,14.289,0,0,1,.423,2.007c.114.773.2,1.932.244,2.864a19.39,19.39,0,0,1-.036,4.91c-.375,1.738-1.775,2.521-3.24,3.331-1.9,1.051-4.053,1.515-5.924,2.6A29.238,29.238,0,0,0,197,271.264c-1.865,1.782.966,4.608,2.828,2.828a23.07,23.07,0,0,1,4.765-4.05c1.786-.954,3.8-1.428,5.595-2.418a10.18,10.18,0,0,0,4.378-3.813,12.1,12.1,0,0,0,.959-6.135,29.67,29.67,0,0,0-.956-7.895,4.5,4.5,0,0,0-2.624-3.214c-1.876-.586-3.647,1.077-5.151,1.93-3.556,2.018-9.413,4.165-12.51.116-.7-.913-2.236-1.513-3.141-.405a118.546,118.546,0,0,1-8.6,9.249c-1.529,1.512-3.073,3.009-4.6,4.52a17.1,17.1,0,0,0-3.6,4.567,8.239,8.239,0,0,0,1.8,10.089c3.013,2.621,7.413,3.287,11.278,2.924a20.719,20.719,0,0,0,12.406-5.465C201.713,272.33,198.88,269.506,197,271.264Z"/><path class="d" d="M165.707,140.431c.365-10.669,3.325-24.142,10.632-35.712,3-4.562,9.153-9.276,15.22-11.889l.195-.217c1.535-1.523,5.206-4.5,7.172-6.1a.839.839,0,0,1,1.313.352c3.706,9.4,7.641,13.845,16.867,19.809,5.559-6.6,11.012-13.991,13.343-19.824a.825.825,0,0,1,1.216-.361c2.313,1.494,4.98,3.808,7.39,5.618,6.287,3.136,12.214,7.357,15.313,12.06,4.223,6.412,7.174,14.027,10.063,21.14,4.038,9.94,7.644,21.36,11.682,31.3a59.087,59.087,0,0,1-20.869,7.154l-6.326.709a26.976,26.976,0,0,1-.466,5.332l-.239,3.107-.054.7c.278,8.218.231,14.741.272,23.135.064,12.963.013,28.694-.437,41.666a2.893,2.893,0,0,1-.351,1.65c-.929,1.42-4.123,1.935-6.475,2.065-9,.49-14.647.42-23.857.42s-14.865.07-23.867-.42c-2.362-.13-5.161-.45-6.09-1.87A2.815,2.815,0,0,1,187,238.6c-.92-18.528-.943-25.417-1.016-42.972-.033-7.982-.13-16.077.207-23.115l-.557-2.013a73.478,73.478,0,0,1-.416-8.772l-.1-1.256a25.7,25.7,0,0,1-4.852,3.015c-4.092,1.678-8.793-1.256-11.017-5.448a33.842,33.842,0,0,1-3.58-14.655Q165.657,141.95,165.707,140.431Z"/><path class="b" d="M269.094,162.2c.718,1.539,1.278,3.148,2.129,4.622a37.108,37.108,0,0,0,3.548,4.773,111.854,111.854,0,0,0,8.023,8.416,11.449,11.449,0,0,1,2.841,3.785,3.66,3.66,0,0,1,.287,1.928c-.17.708-.865.622-1.518.573-1.865-.139-3.581-1.265-5.13-2.22a50.3,50.3,0,0,1-5.029-3.532,2.028,2.028,0,0,0-3.343.883,2.458,2.458,0,0,1-2.651,1.545c-1.406-.053-1.366-1.576-1.566-2.682-.517-2.867-.862-5.818-1.623-8.634-.672-2.482-4.532-1.429-3.858,1.063.481,1.776.755,3.618,1.068,5.43.379,2.2.423,4.907,1.775,6.761,2.819,3.867,9.583,1.965,10.712-2.42l-3.342.883a58.356,58.356,0,0,0,6.033,4.277,15.352,15.352,0,0,0,6.736,2.635c2.324.165,4.775-.737,5.5-3.149a8,8,0,0,0-.879-5.954,19.47,19.47,0,0,0-3.887-4.682c-1.7-1.623-3.382-3.248-4.959-4.991a60.313,60.313,0,0,1-4.539-5.561,35.562,35.562,0,0,1-2.874-5.767,2.016,2.016,0,0,0-2.736-.718,2.045,2.045,0,0,0-.718,2.736Z"/><path class="b" d="M255.244,165.756a60.43,60.43,0,0,0,21.878-7.427,2.012,2.012,0,0,0,.919-2.258c-4.508-11.136-8.154-22.595-12.667-33.732a132.818,132.818,0,0,0-7.341-16.014,33.987,33.987,0,0,0-4.534-6.447,38.5,38.5,0,0,0-6.291-5.305q-1.6-1.113-3.283-2.1c-1.308-.773-2.774-1.374-4.025-2.221-2.289-1.549-4.3-3.5-6.586-5.066a3.119,3.119,0,0,0-3.717-.314,4.988,4.988,0,0,0-1.527,2.466,45.555,45.555,0,0,1-2.42,4.457A127.307,127.307,0,0,1,211.21,110.4q-3.686,4.1-7.566,8.015c-.805.81-1.616,1.615-2.446,2.4-.249.236-.5.465-.755.7a2.548,2.548,0,0,0-.243.209,1.853,1.853,0,0,1,1.229-.457l1.009.273,0,0,.99,1.727q-.536,1.417-.252.963c1.379-2.183-2.081-4.193-3.454-2.019a2.023,2.023,0,0,0,2.813,2.73,10.153,10.153,0,0,0,1.537-1.334c1.911-1.812,3.747-3.7,5.562-5.612a179.05,179.05,0,0,0,16.256-19.332c1.311-1.84,2.567-3.722,3.711-5.671.528-.9,1.033-1.815,1.5-2.749.42-.839.772-1.9,1.237-2.631l-.718.717c-.567.413-.882-.076-.159.427q.416.289.823.59c.434.319.862.647,1.287.979,1.142.89,2.266,1.8,3.411,2.691,2.179,1.688,4.829,2.773,7.143,4.293A36.77,36.77,0,0,1,250,102.012a27.6,27.6,0,0,1,4.25,5.76,117.812,117.812,0,0,1,7.1,15.222q3.192,7.871,6.049,15.859c2.2,6.117,4.344,12.255,6.783,18.281l.919-2.259a55.351,55.351,0,0,1-19.859,6.881,2.066,2.066,0,0,0-2,2,2.012,2.012,0,0,0,2,2Z"/><path class="b" d="M233.365,98.392a97.427,97.427,0,0,1-17.42,23.785c-1.817,1.829,1.011,4.658,2.828,2.829a101.042,101.042,0,0,0,18.046-24.595c1.18-2.284-2.27-4.309-3.454-2.019Z"/><path class="e" d="M248.657,135.646c-.015-.375-.031-.727-.046-1.055l-2.33-.243c-6.067-1.263-39.567-1.049-45.387-.965l-9.963.373-2.592,23.407a13.531,13.531,0,0,1-3.18,3.279c.1,4.315.3,9.428.478,10.059,10.806.065,44.97-.377,62.815-.7C249.331,167.424,249.038,144.866,248.657,135.646Z"/><path class="b" d="M200.894,135.383c12.607-.178,25.261-.232,37.858.323,1.462.065,2.925.141,4.385.259.573.046,1.144.1,1.716.165.665.072-.241-.059.285.038.2.038.409.068.612.109,2.513.509,3.588-3.346,1.063-3.857a45.932,45.932,0,0,0-6.717-.65c-3.311-.171-6.626-.254-9.941-.317-7.285-.138-14.573-.157-21.859-.128-2.467.01-4.935.023-7.4.058-2.571.036-2.579,4.036,0,4Z"/><path class="b" d="M183.221,161.729c.032,1.958.071,3.917.161,5.873a16.766,16.766,0,0,0,.326,3.431,2,2,0,1,0,3.858-1.064c-.034-.126-.1-.612-.04-.152s.007.035,0-.07-.021-.219-.03-.328c-.054-.644-.087-1.289-.116-1.934-.085-1.918-.124-3.837-.155-5.756a2,2,0,0,0-4,0Z"/><path class="b" d="M246.452,132.168c.48,4.465.4,9.04.479,13.524.11,6.181.186,12.374-.006,18.554-.036,1.158-.08,2.317-.171,3.473-.019.237-.043.473-.064.71-.031.358-.079.467-.007.1a5.233,5.233,0,0,1-.16.733c-.849,2.435,3.014,3.482,3.857,1.063a17.433,17.433,0,0,0,.5-4.816c.117-2.793.139-5.59.146-8.384q.025-9.5-.278-18.993c-.064-1.985-.084-3.992-.3-5.968a2.059,2.059,0,0,0-2-2,2.013,2.013,0,0,0-2,2Z"/><path class="b" d="M185.637,172.5c16.4.094,32.8-.233,49.2-.48q6.808-.1,13.617-.224c2.571-.047,2.579-4.047,0-4q-26.4.483-52.8.681c-3.337.022-6.675.042-10.012.023-2.574-.015-2.577,3.985,0,4Z"/><path class="b" d="M186.612,156.154c-1.45,2.244-4.065,3.889-6.377,5.13-2.27,1.218-4.838.564-6.818-1.169-2.612-2.287-3.836-5.793-4.686-9.064a36.286,36.286,0,0,1-1.033-10.335,73.482,73.482,0,0,1,3.55-20.281c2.231-6.926,5.35-14.25,10.847-19.2a37.218,37.218,0,0,1,5.115-3.839q1.389-.873,2.845-1.635a14.047,14.047,0,0,0,2.918-1.512c1.113-1,2.191-2.037,3.341-3q1.04-.874,2.091-1.736l.91-.745c.16-.13.327-.253.48-.391.485-.439.306.031-.125-.018l-1.009-.273-.207-.321q.106.267.216.533c.137.335.278.668.419,1,.214.5.432,1.008.659,1.508.449.986.928,1.959,1.45,2.909a34.579,34.579,0,0,0,3.455,5.121,44.575,44.575,0,0,0,9.919,8.566c2.138,1.445,4.142-2.019,2.019-3.454a39.413,39.413,0,0,1-9.368-8.265,32.3,32.3,0,0,1-3.194-5.169q-.72-1.422-1.341-2.892c-.5-1.171-.791-2.377-2.008-2.991-2.207-1.111-4.25,1.345-5.792,2.62-.835.689-1.666,1.383-2.486,2.09a24.59,24.59,0,0,1-2.091,1.9c-.878.587-2.089.958-3.042,1.483q-1.826,1-3.545,2.189a39.355,39.355,0,0,0-6.214,5.2c-3.671,3.852-6.058,8.848-8.077,13.716a74.84,74.84,0,0,0-4.388,14.8c-1.817,9.639-2.343,19.887,1.792,29.024,2.133,4.715,6.775,9.053,12.324,8.2a13.88,13.88,0,0,0,5.436-2.536,18.765,18.765,0,0,0,5.469-5.138c1.4-2.169-2.06-4.176-3.454-2.019Z"/><path class="b" d="M246.213,172.3c.377,13.2.282,26.424.228,39.623-.029,6.864-.1,13.729-.273,20.591q-.059,2.331-.132,4.66c-.036,1.1.258,1.773-.8,2.216-2.715,1.137-6.159.858-9.036.965-6.375.235-12.755.19-19.133.191-6.361,0-12.722.038-19.08-.208-1.64-.063-3.281-.127-4.919-.234-.971-.064-3.2-.018-3.89-.816-.2-.235-.139-.325-.174-.682-.087-.876-.087-1.769-.129-2.648q-.121-2.531-.231-5.063c-.237-5.49-.417-10.982-.51-16.477-.111-6.585-.12-13.172-.15-19.759-.037-7.92-.159-15.855.295-23.766.148-2.572-3.853-2.563-4,0-.426,7.425-.341,14.871-.3,22.3.033,6.4.039,12.8.128,19.2q.115,8.436.471,16.865.1,2.322.2,4.641a47.462,47.462,0,0,0,.322,5.908c.573,3.265,4.248,3.952,7.009,4.215,6.521.622,13.163.522,19.707.521,6.891,0,13.787.073,20.677-.084,3.349-.076,6.761-.082,10.09-.459,2.688-.3,6.454-.971,7.257-4.053a20.8,20.8,0,0,0,.248-4.452q.083-2.8.141-5.6.111-5.257.16-10.516c.158-15.681.273-31.411-.175-47.087-.074-2.568-4.074-2.579-4,0Z"/><path class="e" d="M166.345,102.66a9.656,9.656,0,0,1,.47-3.9,8.881,8.881,0,0,1-2.441-3.376c-.156-.875,3-4.622,10.944-6.444,6.056-1.389,12.926-.123,13.223,1a6.509,6.509,0,0,1-.993,3.865c1.521.884,2.514,3.214,3.092,4.566a11.256,11.256,0,0,1-.71,9.291,10.129,10.129,0,0,1-8.072,4.166,11.933,11.933,0,0,1-10.817-.11C168.485,110.274,166.412,106.467,166.345,102.66Z"/><path class="b" d="M179.312,112.636c.886,4.488,1.7,8.99,2.62,13.47a2,2,0,1,0,3.857-1.063c-.923-4.48-1.734-8.983-2.62-13.47a2.02,2.02,0,0,0-2.46-1.4,2.041,2.041,0,0,0-1.4,2.46Z"/><path class="b" d="M168.345,102.66a8.288,8.288,0,0,1,.4-3.367,1.92,1.92,0,0,0-.514-1.946,6.965,6.965,0,0,1-1.113-1.144c-.237-.3-.405-.726-.666-1-.234-.245,0-.328-.081.128-.132.785-.043.428-.021.264-.081.592-.174.217.028.028.046-.043.356-.457.009-.032.14-.171.292-.333.448-.491a16.156,16.156,0,0,1,6.5-3.546,25.218,25.218,0,0,1,10.929-1.037,14.431,14.431,0,0,1,1.878.37,6.691,6.691,0,0,1,.786.246c-.054-.022.188-.037.246.14-.008-.022-.754-.933-.59-.965a4.65,4.65,0,0,1-.1.834,4.184,4.184,0,0,1-.664,1.653,2.027,2.027,0,0,0,.717,2.736c1.133.735,1.793,2.386,2.268,3.6a8.617,8.617,0,0,1,.338,4.912,6.525,6.525,0,0,1-1.561,3.368,8.6,8.6,0,0,1-4.347,2.314,13.563,13.563,0,0,0-2.713.525,12.484,12.484,0,0,1-2.168.639,9.772,9.772,0,0,1-4.927-.286c-3.313-1.081-4.965-4.654-5.084-7.945-.094-2.567-4.094-2.579-4,0,.15,4.145,2.057,8.815,5.867,10.883a14.105,14.105,0,0,0,12.655.013l-1.009.273a11.264,11.264,0,0,0,11.017-8.185,12.676,12.676,0,0,0-.306-7.8c-.882-2.2-1.966-4.435-4.011-5.761l.717,2.737c1.437-1.994,2.189-5.775-.361-7.15-2.661-1.434-6.408-1.445-9.332-1.3a28.785,28.785,0,0,0-11.2,2.891,13.429,13.429,0,0,0-5.391,4.244c-1.533,2.331.535,5.18,2.41,6.672l-.515-1.946a11.246,11.246,0,0,0-.541,4.431C164.378,105.232,168.379,105.239,168.345,102.66Z"/><path class="a" d="M195.377,145.229c-.067-1.036-.624-2.7-2.049-2.735a3.359,3.359,0,0,0,1.869-5.114,3.174,3.174,0,0,0-2.4-1.2,2.984,2.984,0,0,0,1.69-2.306,2.271,2.271,0,0,0-.894-2.213,3.463,3.463,0,0,0-2.747-.818,2.179,2.179,0,0,0,.974-2.81,3.423,3.423,0,0,0-2.623-1.767,9.8,9.8,0,0,0-3.371.2,16.712,16.712,0,0,0-7.586,2.977,7.891,7.891,0,0,0-2.459,5.418,24.8,24.8,0,0,0,1.019,9.464c.683,2.193,1.808,4.428,3.911,5.489a10.74,10.74,0,0,0,3.405.874,9.843,9.843,0,0,0,6.518-.794,11.663,11.663,0,0,0,3.182-1.779A3.822,3.822,0,0,0,195.377,145.229Z"/><path class="b" d="M197.377,145.229c-.233-2.439-1.461-4.45-4.049-4.735l.532,3.928a5.43,5.43,0,0,0,3.927-5.437c-.111-2.822-2.357-4.536-4.99-4.805l1.009,3.727a4.983,4.983,0,0,0,2.523-5.656,5.3,5.3,0,0,0-5.483-3.408l1.009,3.727a4.225,4.225,0,0,0,1.692-5.546c-1.038-2.047-3.432-2.9-5.608-2.831-4.377.136-10.2,1.765-12.654,5.678-2.487,3.968-1.828,9.822-.667,14.11a13.722,13.722,0,0,0,3.087,6.056c1.8,1.858,4.173,2.363,6.643,2.678a14.248,14.248,0,0,0,8.232-1.506c2.423-1.124,4.746-3.116,4.8-5.98.047-2.575-3.953-2.576-4,0-.029,1.624-2.808,2.574-4.052,3.049a10.67,10.67,0,0,1-6.43.178c-3.868-.921-4.8-5.864-5.105-9.259a16.019,16.019,0,0,1,.283-5.816,5.778,5.778,0,0,1,3.611-3.7,19.148,19.148,0,0,1,5.832-1.467c.607-.053,1.745-.15,2.232.36.191.2.4.364.088.538-1.638.923-1.02,3.925,1.01,3.727,1.239-.12,2.423.772.941,1.61-1.861,1.054-.844,3.538,1.01,3.727,1.448.148,1.161,2.055,0,2.385-2.3.653-1.616,3.692.531,3.929-.4-.045.033.564.049.735a2.056,2.056,0,0,0,2,2A2.014,2.014,0,0,0,197.377,145.229Z"/><path class="b" d="M186.042,140.786q.492-.236.991-.458c.188-.085.377-.178.571-.25l-.19.08c.095-.041.192-.08.288-.12q1.01-.414,2.042-.774a41.144,41.144,0,0,1,4.192-1.213,2.018,2.018,0,0,0,1.4-2.46,2.045,2.045,0,0,0-2.461-1.4,43.7,43.7,0,0,0-8.849,3.138,2.01,2.01,0,0,0-.717,2.737,2.054,2.054,0,0,0,2.736.717Z"/><path class="b" d="M184.283,135.15l.275-.117q-.379.159-.075.032c.174-.072.348-.144.523-.214q.441-.178.885-.346.9-.342,1.823-.637c1.263-.405,2.548-.736,3.84-1.037a2.017,2.017,0,0,0,1.4-2.46,2.044,2.044,0,0,0-2.46-1.4,48.717,48.717,0,0,0-8.227,2.722,2,2,0,0,0-.919,1.2,2.043,2.043,0,0,0,.2,1.541,2.017,2.017,0,0,0,1.195.919,2.341,2.341,0,0,0,1.541-.2Z"/><path class="b" d="M187.364,146.46q.408-.21.824-.4.213-.1.428-.193c.073-.032.146-.061.218-.094-.072.033-.4.165-.149.064.61-.246,1.224-.476,1.849-.68a20.515,20.515,0,0,1,3.392-.835,2,2,0,0,0,1.2-.919,2,2,0,0,0-.718-2.737,2.332,2.332,0,0,0-1.541-.2,24.655,24.655,0,0,0-7.517,2.543,2.015,2.015,0,0,0-.717,2.736,2.046,2.046,0,0,0,2.736.718Z"/><path class="b" d="M209.4,70.409a9.967,9.967,0,0,0,11.9,0,2,2,0,0,0-2.828-2.829c-.077.076-.371.31-.041.056s-.04.018-.138.078c-.117.072-.238.139-.362.2-.081.041-.173.074-.252.119a1.3,1.3,0,1,0,.15-.069,8.5,8.5,0,0,1-1.206.33c-.151.028-.49.171-.019.013a1.69,1.69,0,0,1-.37.038c-.3.025-.59.036-.886.036-.271,0-.541-.009-.811-.03a2.832,2.832,0,0,0-.447-.044c.192-.022.352.053.048,0a7.469,7.469,0,0,1-1.223-.324c-.161-.058-.419-.228.1.051-.068-.037-.142-.065-.211-.1q-.207-.1-.4-.22c-.1-.062-.191-.137-.291-.2.577.35.277.223.113.063a2,2,0,0,0-2.828,2.829Z"/><path class="b" d="M213.636,56.8c-.235.895-.445,1.8-.6,2.71a3.792,3.792,0,0,0-.013,1.666,2.457,2.457,0,0,0,1.294,1.589,3.458,3.458,0,0,0,1.648.407c.359-.015.7-.1,1.055-.151a2,2,0,0,0,1.195-.919,2,2,0,0,0-.717-2.737l-.478-.2a2,2,0,0,0-1.063,0c-.134.018-.266.05-.4.069l.531-.072a1.5,1.5,0,0,1-.354,0l.531.072a1.623,1.623,0,0,1-.378-.111l.478.2a1.921,1.921,0,0,1-.224-.119l.405.313a.616.616,0,0,1-.093-.091l.313.405a.732.732,0,0,1-.062-.113l.2.477a.9.9,0,0,1-.043-.175l.071.531a1.7,1.7,0,0,1,.011-.39l-.072.531a26.407,26.407,0,0,1,.619-2.831,2.077,2.077,0,0,0-.2-1.541,2,2,0,0,0-2.736-.717,2.065,2.065,0,0,0-.919,1.2Z"/><path class="b" d="M200.1,50.279c-.463,1.5-.161,4.956,2.684,5.25,3.76-.022,3.96-4.2,2.695-6.163C204.439,47.758,201.391,47.089,200.1,50.279Z"/><path class="b" d="M230.087,50.279c.462,1.5.161,4.956-2.684,5.25-3.761-.022-3.961-4.2-2.695-6.163C225.744,47.758,228.792,47.089,230.087,50.279Z"/><path class="a" d="M103.432,46.3a4.3,4.3,0,0,1,3.445-1.008,4.062,4.062,0,0,1,2.922,1.943,5.724,5.724,0,0,1,.6,2.312,17.228,17.228,0,0,1-1.756,9.13,10.948,10.948,0,0,1-2.831,3.715,3.3,3.3,0,0,1-3.309.774l-.5-.15c-.3,1.2-.707,2.246-.887,2.757-.986,2.5-6.537,11.4-13.495,14.571.068.544.157,1.172.307,2,.36,2.12.96,4.52,3.78,6.08.19.06,3.87,1.81,4.16,1.93,0,0-3.661,16.756-22.118,16.756S54.973,90.354,54.973,90.354c.3-.12,3.97-1.87,4.17-1.93,2.81-1.56,3.41-3.96,3.78-6.08.089-.5.159-.933.209-1.31a27.155,27.155,0,0,1-9.8-7.229,30.945,30.945,0,0,1-6.137-10.43l-.735.2a4.114,4.114,0,0,1-3.73-1.179A10.961,10.961,0,0,1,39.9,58.679a17.228,17.228,0,0,1-1.756-9.13,5.756,5.756,0,0,1,.6-2.312,4.066,4.066,0,0,1,2.923-1.943A4.3,4.3,0,0,1,45.11,46.3s2.867-22.525,29.533-22.525C102.2,23.777,103.432,46.3,103.432,46.3Z"/><path class="f" d="M42.028,32.607A31.1,31.1,0,0,1,55.112,11.554a32.588,32.588,0,0,1,19.33-5.948A34.271,34.271,0,0,1,85.851,7.477a32.456,32.456,0,0,1,4.813,2.158,37.644,37.644,0,0,1,5.511,3.654c.66.574,1.629,1.515,2.266,2.16a30.115,30.115,0,0,1,4.188,5.3,31.615,31.615,0,0,1,4.552,15.312,42.31,42.31,0,0,1-.558,8.991l-.036.217a4.269,4.269,0,0,0-3.155,1.035,4.144,4.144,0,0,1-3.756.382,2.338,2.338,0,0,1-1.313-2.217,26.757,26.757,0,0,0-5.876-13.046c-1.116-1.292-3.061-3.126-4.637-3.611,0,0-.33-.1-.864-.257a54.906,54.906,0,0,1-5.876,2.4c-1.516.52-3.522.907-4.629-.059-1.049-.914-.622-2.571-1.871-3.314a4.235,4.235,0,0,0-3.053-.07C60.879,29.179,54.448,35.668,50.484,43.9a4.206,4.206,0,0,1-3.65,2.764A3.862,3.862,0,0,1,45.11,46.3a4.223,4.223,0,0,0-2.616-1.041c.2,1.919-.97-5.078-.789-9.2A34.4,34.4,0,0,1,42.028,32.607Z"/><path class="b" d="M55.505,92.283C56.921,91.7,58.29,91,59.682,90.358c.1-.048.211-.094.316-.143.25-.115-.549.229-.351.148s.39-.153.575-.251a8.618,8.618,0,0,0,1.87-1.394,9.054,9.054,0,0,0,2.162-3.452,17.4,17.4,0,0,0,.807-3.71,2.21,2.21,0,0,0-.2-1.541,2,2,0,0,0-3.656.478A20.784,20.784,0,0,1,60.6,83.6c-.065.221-.141.438-.219.655a1,1,0,0,0-.063.162c0,.008.184-.395.087-.208-.063.123-.116.251-.179.374a6.905,6.905,0,0,1-.4.678c-.041.061-.288.4-.1.151s-.117.126-.175.19c-.184.2-.383.381-.584.561-.276.247.267-.176-.047.04-.145.1-.289.2-.439.293-.37.229-.023.027.111.008a2.447,2.447,0,0,0-.524.22l-.258.115c-.665.3-1.323.614-1.983.924q-.57.269-1.141.535c-.234.109-1.214.528-.237.126a2.2,2.2,0,0,0-1.2.919,2.044,2.044,0,0,0-.2,1.541,2.021,2.021,0,0,0,2.461,1.4Z"/><path class="b" d="M85.623,80.334c.336,2.609.682,5.324,2.338,7.468a8.594,8.594,0,0,0,1.583,1.571,8.29,8.29,0,0,0,1.01.694,4.174,4.174,0,0,0,.639.29c.109.038-.617-.273-.343-.144.662.312,1.329.614,1.991.925s1.339.653,2.022.943a2.2,2.2,0,0,0,1.542.2,2,2,0,0,0,.477-3.656c-.748-.317-1.477-.686-2.212-1.032q-.681-.319-1.364-.637c-.146-.067-.291-.134-.437-.2a5.59,5.59,0,0,0-.573-.243c-.156.031.431.237.2.054a5.136,5.136,0,0,0-.482-.31q-.273-.2.03.033c-.079-.062-.156-.126-.232-.192-.212-.186-.7-.54-.787-.818q.26.341.069.082c-.05-.072-.1-.146-.148-.22q-.141-.217-.264-.447c-.033-.061-.172-.441-.225-.456.117.286.135.329.055.131-.031-.077-.06-.155-.088-.233a12.051,12.051,0,0,1-.486-1.869q-.109-.584-.2-1.171c-.034-.207-.066-.413-.1-.62-.013-.094-.027-.188-.039-.282q.061.462.019.136a2.055,2.055,0,0,0-2-2c-.969.044-2.143.889-2,2Z"/><path class="b" d="M104.846,47.716a2.219,2.219,0,0,1,3.226.531,5.421,5.421,0,0,1,.387,2.4,14.417,14.417,0,0,1-.2,2.89,15.285,15.285,0,0,1-2.046,5.409,7.533,7.533,0,0,1-1.609,1.885,1.473,1.473,0,0,1-1.562.414c-2.49-.665-3.553,3.193-1.064,3.857,3.162.843,5.64-1.189,7.365-3.648a18.44,18.44,0,0,0,2.988-8.313c.338-2.767.328-6.271-1.911-8.283a6.357,6.357,0,0,0-8.4.035,2.014,2.014,0,0,0,0,2.828,2.043,2.043,0,0,0,2.828,0Z"/><path class="b" d="M100.4,60.485a14.136,14.136,0,0,1-.943,4.034c-.085.242-.181.481-.26.725-.107.333.222-.41.039-.1-.157.266-.272.564-.417.837a34.523,34.523,0,0,1-3.157,4.837c-2.832,3.667-6.6,7.478-11.292,8.507-2.513.55-1.45,4.407,1.063,3.857C90.985,81.966,95.436,77.6,98.8,73.243c2.876-3.723,5.386-7.922,5.6-12.758.112-2.574-3.889-2.568-4,0Z"/><path class="b" d="M46.524,44.888a6.36,6.36,0,0,0-8.4-.035c-2.3,2.067-2.247,5.686-1.881,8.512a18.156,18.156,0,0,0,3.129,8.322c1.782,2.443,4.437,4.515,7.614,3.815a2,2,0,0,0-1.063-3.857c-1.344.3-2.782-1.477-3.433-2.458a15.037,15.037,0,0,1-2.176-5.5,14.2,14.2,0,0,1-.238-2.845,5.719,5.719,0,0,1,.39-2.594,2.219,2.219,0,0,1,3.227-.531,2.054,2.054,0,0,0,2.828,0,2.016,2.016,0,0,0,0-2.828Z"/><path class="b" d="M44.168,59.931a33.11,33.11,0,0,0,7.607,15.13c4,4.533,9.348,8.282,15.44,9.149a2.067,2.067,0,0,0,2.46-1.4,2.014,2.014,0,0,0-1.4-2.46c-10.486-1.493-18.22-11.6-20.253-21.485-.518-2.52-4.375-1.453-3.857,1.063Z"/><path class="b" d="M108.551,45.582c1.457-8.957.56-18.445-4.436-26.227A34.64,34.64,0,0,0,83.485,4.683,37.032,37.032,0,0,0,57.9,7.5,34.519,34.519,0,0,0,43.854,21.04a33.315,33.315,0,0,0-3.946,12.477,43.929,43.929,0,0,0,.565,12.067,2.014,2.014,0,0,0,2.46,1.4,2.048,2.048,0,0,0,1.4-2.46c-1.042-6.437-.906-13.112,1.81-19.147A30.385,30.385,0,0,1,57.189,12.55C70.229,4,88.7,6.808,98.7,18.693c6.006,7.138,7.461,16.83,6,25.825a2.061,2.061,0,0,0,1.4,2.46,2.014,2.014,0,0,0,2.46-1.4Z"/><path class="b" d="M88.723,24.412a50.666,50.666,0,0,1-5.374,2.578c-1.458.587-3.429,1.644-5.058,1.5-.6-.056-.468-.009-.658-.558a6.808,6.808,0,0,0-.983-2.159c-1.292-1.613-3.364-1.661-5.238-1.278A31.9,31.9,0,0,0,54.58,34.162a37.1,37.1,0,0,0-5.822,8.73c-1.122,2.306,2.327,4.336,3.453,2.019a30.209,30.209,0,0,1,11.177-12.9,27.836,27.836,0,0,1,9.088-3.663,2.727,2.727,0,0,1,.911-.1c.262.047.137-.006.171.031.175.189.227.765.306,1a6.113,6.113,0,0,0,.5,1.157,4.638,4.638,0,0,0,4.279,2.046,18.392,18.392,0,0,0,5.981-1.717,59.855,59.855,0,0,0,6.119-2.9c2.258-1.236.242-4.692-2.019-3.454Z"/><path class="b" d="M44.1,48.029a5.135,5.135,0,0,0,2.452.63,4.9,4.9,0,0,0,2.033-.318,6.275,6.275,0,0,0,2.213-1.4,7.067,7.067,0,0,0,1.413-2.034,2.156,2.156,0,0,0,.2-1.541,2,2,0,0,0-2.46-1.4,1.955,1.955,0,0,0-1.2.919,6.243,6.243,0,0,1-.7,1.169l.313-.405a4.8,4.8,0,0,1-.788.8l.4-.313a4.065,4.065,0,0,1-.887.519l.478-.2a3.9,3.9,0,0,1-.889.243l.532-.071a3.868,3.868,0,0,1-1.014-.006l.532.071a3.865,3.865,0,0,1-.931-.228l.478.2a1.252,1.252,0,0,1-.172-.095,2,2,0,0,0-2.938,2.258,2.223,2.223,0,0,0,.919,1.2Z"/><path class="b" d="M96.363,44.468a4.474,4.474,0,0,0,2.246,3.912,6.155,6.155,0,0,0,5.832-.351,2.017,2.017,0,0,0,.718-2.737,2.045,2.045,0,0,0-2.737-.717c-.169.089-.34.171-.515.248l.478-.2a5.7,5.7,0,0,1-1.366.394l.532-.071a3.949,3.949,0,0,1-1.036.007l.532.071a3,3,0,0,1-.643-.174l.478.2a2.954,2.954,0,0,1-.62-.361l.4.313a2.413,2.413,0,0,1-.395-.394l.313.405a2.428,2.428,0,0,1-.284-.488l.2.478a2.868,2.868,0,0,1-.178-.662l.071.531c-.017-.134-.027-.268-.031-.4a2.086,2.086,0,0,0-.585-1.414,2,2,0,0,0-3.415,1.414Z"/><path class="b" d="M87.318,29.739c.29.1.023-.01.2.077.137.067.27.141.4.218a8.4,8.4,0,0,1,.91.611,15.1,15.1,0,0,1,1.481,1.365,20.4,20.4,0,0,1,2.766,3.7A24.9,24.9,0,0,1,96.4,44.73a2.017,2.017,0,0,0,2.461,1.4,2.048,2.048,0,0,0,1.4-2.461,27.9,27.9,0,0,0-4.024-10.453c-1.866-2.941-4.427-6.173-7.851-7.331a2,2,0,1,0-1.064,3.857Z"/><path class="a" d="M121.166,159.962l2.123,9.888c.3,1.054.714,3.478.914,4.556.185,1,.519,3.111.963,5.445a3.138,3.138,0,0,0,2.6,2.739c2.208.28,4.763-.764,5.218-2.969a52.652,52.652,0,0,0,6.417,4.437c1.911,1.121,4.052,2.151,6.249,1.866a2.5,2.5,0,0,0,2.436-2.728c.106-3.417-2.776-6.071-5.267-8.412a72.891,72.891,0,0,1-9.236-10.53,38.065,38.065,0,0,1-2.608-5.4L129.755,156l-8.889,2.889Z"/><path class="a" d="M28.932,159.962l-2.124,9.888c-.3,1.054-.714,3.478-.914,4.556-.185,1-.518,3.111-.963,5.445a3.138,3.138,0,0,1-2.6,2.739c-2.207.28-4.762-.764-5.218-2.969a52.652,52.652,0,0,1-6.417,4.437c-1.911,1.121-4.051,2.151-6.248,1.866a2.917,2.917,0,0,1-1.724-.742,2.926,2.926,0,0,1-.713-1.986c-.106-3.417,2.776-6.071,5.267-8.412a72.891,72.891,0,0,0,9.236-10.53,38.08,38.08,0,0,0,2.609-5.4l.69-2.632,9.2,3.2Z"/><path class="a" d="M84.156,241.649c4.6-.021,8.83-.1,14.222-.377q.072,3.432.26,6.859l.146,3.338a9.853,9.853,0,0,1-7.33,1.194,26.354,26.354,0,0,1-8.266-3.8c-.435-2.389-.745-4.793-.975-7.207Q83.2,241.652,84.156,241.649Z"/><path class="a" d="M51.814,251.313a7.5,7.5,0,0,1-.694-.558q.218-4.738.476-9.472c6.145.31,10.8.365,16.244.372q-.465,3.751-.727,7.526a24.743,24.743,0,0,1-7.74,3.482A9.761,9.761,0,0,1,51.814,251.313Z"/><path class="a" d="M94.865,272.678A16.029,16.029,0,0,0,97.838,275a19.506,19.506,0,0,0,12.141,2.492,11.5,11.5,0,0,0,5.159-1.817,6.415,6.415,0,0,0,2.815-4.548c.22-2.609-1.363-5.08-3.218-6.927-4.761-4.738-9.808-9.389-14.013-14.575-2.108,2.9-5.884,3.733-9.268,3.04-3.112-.637-5.884-2.339-8.59-4-2.589-1.592-2.979,5.88-3.04,7.5-.1,2.566-.518,5.954,1.518,7.851a20.512,20.512,0,0,0,6.508,3.54C90.973,268.507,92.585,270.519,94.865,272.678Z"/><path class="a" d="M55.962,272.678A16.029,16.029,0,0,1,52.989,275a19.506,19.506,0,0,1-12.141,2.492,11.5,11.5,0,0,1-5.159-1.817,6.418,6.418,0,0,1-2.815-4.548c-.22-2.609,1.363-5.08,3.218-6.927,4.761-4.738,9.808-9.389,14.013-14.575,2.108,2.9,5.884,3.733,9.268,3.04,3.112-.637,5.884-2.339,8.59-4,2.589-1.592,2.979,5.88,3.04,7.5.1,2.566.518,5.954-1.518,7.851a20.512,20.512,0,0,1-6.508,3.54C59.854,268.507,58.242,270.519,55.962,272.678Z"/><path class="b" d="M50.917,220.493q-1.1,15.1-1.8,30.228c-.119,2.573,3.882,2.567,4,0q.7-15.126,1.8-30.228c.186-2.568-3.814-2.556-4,0Z"/><path class="b" d="M69.085,223.786a153.492,153.492,0,0,0-3.969,25.331c-.186,2.569,3.815,2.557,4,0a146.728,146.728,0,0,1,3.827-24.268c.61-2.5-3.246-3.567-3.858-1.063Z"/><path class="b" d="M79.311,223.512c.341,8.336.422,16.689,1.784,24.942a2.016,2.016,0,0,0,2.46,1.4,2.049,2.049,0,0,0,1.4-2.461c-1.3-7.887-1.315-15.911-1.641-23.878-.105-2.565-4.106-2.579-4,0Z"/><path class="b" d="M96.987,220.915a204.8,204.8,0,0,0-.349,27.216c.137,2.561,4.138,2.577,4,0a204.8,204.8,0,0,1,.349-27.216c.2-2.567-3.8-2.554-4,0Z"/><path class="b" d="M93.451,274.092a20.143,20.143,0,0,0,10.58,5.228c3.914.635,8.533.469,11.94-1.8a8.252,8.252,0,0,0,3.545-9.592c-1.317-3.8-4.686-6.445-7.468-9.173a131.137,131.137,0,0,1-9.912-10.545c-.905-1.108-2.443-.508-3.141.405-2.639,3.45-7.681,2.356-10.979.706-1.037-.519-2.039-1.106-3.031-1.706a6.184,6.184,0,0,0-2.457-1.135,3.368,3.368,0,0,0-3.356,2.14c-1.109,2.285-1.236,5.046-1.348,7.543a19.857,19.857,0,0,0,.27,6.074,8.007,8.007,0,0,0,3.749,4.645,32.314,32.314,0,0,0,6.066,2.8c2.242.875,3.845,2.789,5.542,4.41,1.861,1.779,4.694-1.045,2.828-2.828a36.4,36.4,0,0,0-4.617-4.1c-1.617-1.091-3.5-1.493-5.234-2.32-1.387-.66-3.395-1.5-4.185-2.906-.8-1.426-.532-3.395-.456-4.953.106-2.216.029-4.516.922-6.55-.108.247.189-.262.225-.364-.129.361-.136.08,0,.051-.136.03-.244.223-.406.262-.559.138-1.2-.318-.3.227.5.3.989.606,1.489.9a26.038,26.038,0,0,0,6.369,2.878c4.6,1.234,9.415.1,12.367-3.76l-3.141.405a126.071,126.071,0,0,0,9.418,10.059c1.531,1.5,3.089,2.986,4.595,4.517a8.023,8.023,0,0,1,2.646,4.734c.308,4.11-5.079,5.262-8.157,5.294a16.587,16.587,0,0,1-11.531-4.377C94.4,269.507,91.566,272.33,93.451,274.092Z"/><path class="b" d="M54.548,271.264a16.576,16.576,0,0,1-11.531,4.377c-3.075-.036-8.465-1.182-8.157-5.294a8.022,8.022,0,0,1,2.647-4.734c1.5-1.534,3.063-3.012,4.594-4.517a126.071,126.071,0,0,0,9.418-10.059l-3.141-.405A11.088,11.088,0,0,0,59.2,254.713a20.02,20.02,0,0,0,6.4-2.341c.894-.48,1.766-1,2.633-1.531a3.8,3.8,0,0,0,.739-.454c.2-.332.158.064-.017.006-.5-.165-.527.049-.882-.116-.234-.109-.127-.117-.124-.126.03-.1.194.35.19.341-.018-.04.14.409.187.566a14.292,14.292,0,0,1,.424,2.007c.113.773.2,1.932.243,2.864a19.39,19.39,0,0,1-.036,4.91c-.375,1.738-1.774,2.521-3.24,3.331-1.9,1.051-4.053,1.515-5.924,2.6a29.238,29.238,0,0,0-5.245,4.492c-1.865,1.782.966,4.608,2.828,2.828a23.049,23.049,0,0,1,4.766-4.05c1.785-.954,3.8-1.428,5.594-2.418a10.18,10.18,0,0,0,4.378-3.813,12.1,12.1,0,0,0,.959-6.135,29.711,29.711,0,0,0-.955-7.895,4.507,4.507,0,0,0-2.625-3.214c-1.876-.586-3.647,1.077-5.151,1.93-3.556,2.018-9.413,4.165-12.51.116-.7-.913-2.236-1.513-3.141-.405a118.353,118.353,0,0,1-8.6,9.249c-1.529,1.512-3.073,3.009-4.6,4.52a17.117,17.117,0,0,0-3.6,4.567,8.24,8.24,0,0,0,1.8,10.089c3.013,2.621,7.413,3.287,11.278,2.924a20.719,20.719,0,0,0,12.406-5.465C59.261,272.33,56.428,269.506,54.548,271.264Z"/><path class="g" d="M130.839,143.125c-2.261-6.291-4.494-12.674-6.877-18.542-2.89-7.113-5.841-14.728-10.064-21.14-3.1-4.7-9.026-8.924-15.312-12.06-2.411-1.81-5.078-4.123-7.39-5.618a.826.826,0,0,0-1.217.361c-2.328,5.825-7.628,13.034-13.013,19.424-.872-.634-1.525-1.107-1.525-1.107-8.148-5.481-11.847-9.938-15.342-18.8a.84.84,0,0,0-1.313-.353c-1.966,1.6-5.636,4.582-7.172,6.1,0,0-.089.1-.2.217-6.067,2.614-12.146,6.534-15.151,11.1-4.223,6.411-7.093,14.767-9.983,21.88-3.32,8.172-6.347,17.346-9.563,25.874-.7,1.844-1.4,3.658-2.118,5.426,5.779,3.307,14.768,6.777,21.356,7.746l7.943.184-.313,6.853h-.3c-.4,7.259-.293,15.729-.258,24.074.074,17.555.1,24.444,1.033,42.972a2.782,2.782,0,0,0,.357,1.65c.946,1.42,3.792,1.74,6.2,1.87,9.157.49,14.918.42,24.278.42s15.11.07,24.267-.42c2.393-.13,5.641-.645,6.587-2.065a2.85,2.85,0,0,0,.357-1.65c.458-12.972.509-28.7.445-41.666-.039-7.811,0-14-.223-21.445V163.549l7.334-.291a72.855,72.855,0,0,0,21.979-7.375C133.989,151.811,132.407,147.49,130.839,143.125Z"/><path class="b" d="M17.393,157.843a35.572,35.572,0,0,1-2.874,5.768,60.447,60.447,0,0,1-4.539,5.561c-1.578,1.743-3.261,3.368-4.959,4.99a19.508,19.508,0,0,0-3.887,4.682A7.994,7.994,0,0,0,.255,184.8c.725,2.413,3.176,3.314,5.5,3.149a15.351,15.351,0,0,0,6.736-2.634,58.473,58.473,0,0,0,6.033-4.278l-3.342-.882c1.13,4.386,7.892,6.283,10.712,2.42,1.327-1.818,1.38-4.461,1.75-6.615.319-1.86.6-3.753,1.093-5.576.673-2.488-3.185-3.55-3.858-1.064-.761,2.817-1.105,5.767-1.623,8.635-.2,1.113-.16,2.628-1.566,2.681a2.453,2.453,0,0,1-2.651-1.545,2.028,2.028,0,0,0-3.343-.882,50.213,50.213,0,0,1-4.833,3.411c-1.544.961-3.258,2.105-5.108,2.329-.67.081-1.555.2-1.736-.562a3.477,3.477,0,0,1,.253-1.827,11.188,11.188,0,0,1,2.875-3.886,113.319,113.319,0,0,0,7.879-8.241,39.562,39.562,0,0,0,3.576-4.754,52.628,52.628,0,0,0,2.245-4.815,2.057,2.057,0,0,0-.718-2.736,2.016,2.016,0,0,0-2.736.717Z"/><path class="b" d="M129.251,159.862c.717,1.539,1.277,3.147,2.129,4.622a37.154,37.154,0,0,0,3.548,4.773,111.836,111.836,0,0,0,8.022,8.415,11.462,11.462,0,0,1,2.842,3.785,3.661,3.661,0,0,1,.286,1.928c-.169.708-.865.623-1.518.574-1.865-.14-3.581-1.265-5.13-2.221a50.124,50.124,0,0,1-5.029-3.531,2.027,2.027,0,0,0-3.342.882,2.459,2.459,0,0,1-2.652,1.545c-1.405-.053-1.366-1.575-1.565-2.681-.518-2.868-.862-5.819-1.624-8.635-.671-2.482-4.531-1.428-3.857,1.064.48,1.775.755,3.618,1.067,5.429.379,2.2.423,4.907,1.775,6.762,2.819,3.866,9.583,1.964,10.713-2.42l-3.343.882a58.378,58.378,0,0,0,6.034,4.278,15.346,15.346,0,0,0,6.736,2.634c2.324.165,4.774-.736,5.5-3.149a8,8,0,0,0-.879-5.954,19.531,19.531,0,0,0-3.887-4.682c-1.7-1.622-3.382-3.247-4.959-4.99a60.447,60.447,0,0,1-4.539-5.561,35.41,35.41,0,0,1-2.874-5.768,2.016,2.016,0,0,0-2.737-.717,2.045,2.045,0,0,0-.717,2.736Z"/><path class="b" d="M93.225,97.169a97.432,97.432,0,0,1-17.42,23.786c-1.816,1.828,1.011,4.658,2.828,2.829a101.047,101.047,0,0,0,18.046-24.6c1.18-2.283-2.27-4.309-3.454-2.019Z"/><path class="b" d="M53.579,98.543A48.466,48.466,0,0,0,59.368,109.4a2.046,2.046,0,0,0,2.736.718,2.022,2.022,0,0,0,.718-2.736,46.734,46.734,0,0,1-3.084-4.926q-.669-1.239-1.262-2.515-.316-.681-.61-1.371c.155.365-.13-.325-.156-.39q-.14-.348-.273-.7a2.047,2.047,0,0,0-2.461-1.4,2.022,2.022,0,0,0-1.4,2.46Z"/><path class="b" d="M36.973,161.4a63.457,63.457,0,0,1-21.36-7.248l.919,2.258c4.539-11.21,8.31-22.718,12.748-33.97a131.9,131.9,0,0,1,6.811-15.562,24.709,24.709,0,0,1,4.516-6.193,34.024,34.024,0,0,1,6.745-4.841c1.393-.788,2.825-1.509,4.285-2.166A10.235,10.235,0,0,0,54.222,91.7c.96-.855,1.945-1.681,2.934-2.5q.818-.678,1.639-1.35l.5-.412.471-.383q.549-.415-.241.076l-1.009-.273-.207-.321c.071.178.143.355.216.533q.207.5.419,1c.214.505.432,1.008.659,1.507.449.987.929,1.96,1.45,2.91a34.56,34.56,0,0,0,3.456,5.121,44.566,44.566,0,0,0,9.918,8.565c2.138,1.446,4.142-2.018,2.019-3.454-5.273-3.564-9.662-7.7-12.562-13.434-.776-1.534-1.27-3.3-2.133-4.771a2.841,2.841,0,0,0-2.352-1.4,3.669,3.669,0,0,0-2.462,1.109c-1.252,1.02-2.5,2.042-3.736,3.083a32.877,32.877,0,0,1-3.128,2.742c-.717.454-1.655.729-2.428,1.115q-1.467.732-2.884,1.559a42.2,42.2,0,0,0-5.157,3.547,28.273,28.273,0,0,0-7.073,8.779c-3.9,7.13-6.656,14.964-9.574,22.532-3.551,9.212-6.581,18.619-10.287,27.772a2.005,2.005,0,0,0,.919,2.259,66.477,66.477,0,0,0,22.316,7.651,2.066,2.066,0,0,0,2.46-1.4,2.014,2.014,0,0,0-1.4-2.46Z"/><path class="b" d="M108.182,165.851a83.625,83.625,0,0,0,15.1-3.093,62.4,62.4,0,0,0,13.376-5.148,2.015,2.015,0,0,0,.919-2.259c-4.426-10.932-7.993-22.187-12.42-33.121a147.363,147.363,0,0,0-7.051-15.664A38.761,38.761,0,0,0,113.784,100a35.061,35.061,0,0,0-6.009-5.41,54.377,54.377,0,0,0-7.006-4.337c-2.413-1.266-4.425-3.21-6.605-4.84-.986-.737-2.088-1.76-3.385-1.775A3.022,3.022,0,0,0,87.97,85.8a41.409,41.409,0,0,1-2.253,4.4c-3.919,6.722-8.99,12.776-14.174,18.549q-3.627,4.038-7.456,7.89c-.827.83-1.661,1.653-2.515,2.454-.254.239-.515.47-.771.707a2.626,2.626,0,0,0-.227.193,1.775,1.775,0,0,1,1.22-.452l1.009.273,0,0,.991,1.727q-.535,1.418-.251.961c1.377-2.184-2.083-4.193-3.454-2.019a2.026,2.026,0,0,0,2.8,2.739,9.766,9.766,0,0,0,1.512-1.3c1.832-1.72,3.591-3.521,5.328-5.336A169.316,169.316,0,0,0,85.47,97.887c1.31-1.841,2.563-3.725,3.7-5.677.5-.852.972-1.717,1.414-2.6s.786-1.953,1.279-2.723l-.717.717c-.568.413-.882-.076-.159.428.277.192.551.39.823.59.434.319.861.646,1.286.978,1.142.891,2.266,1.8,3.411,2.691,2.179,1.688,4.83,2.773,7.144,4.293a36.814,36.814,0,0,1,5.879,4.707,27.675,27.675,0,0,1,4.25,5.76,117.806,117.806,0,0,1,7.1,15.222q3.193,7.87,6.049,15.859c2.2,6.117,4.344,12.255,6.784,18.281l.919-2.258a57.76,57.76,0,0,1-12.42,4.744,77.826,77.826,0,0,1-14.032,2.951,2.055,2.055,0,0,0-2,2,2.015,2.015,0,0,0,2,2Z"/><path class="h" d="M105.352,133.786l-1.466-.306c-7.826-1.629-51.307-.033-58.815.075l-2.09.029c-.54,7.546-.508,32.885.09,35.045,10.806.065,44.97-.377,62.815-.7.874-2.359.59-24.658.207-33.985Z"/><path class="b" d="M41.254,131.208a29.9,29.9,0,0,0-.42,5.081c-.113,2.856-.163,5.714-.2,8.572-.074,6.221-.085,12.45.1,18.67a26.11,26.11,0,0,0,.408,5.629c.644,2.49,4.5,1.435,3.857-1.063-.156-.6-.008.3-.029-.089-.017-.311-.059-.622-.08-.934-.067-.957-.1-1.916-.135-2.875-.091-2.737-.124-5.476-.144-8.214-.044-6.168-.025-12.342.179-18.507.039-1.179.084-2.359.16-3.536.028-.435.067-.869.1-1.3.03-.362.054-.385-.006-.011.019-.119.037-.238.063-.357.543-2.509-3.313-3.582-3.857-1.063Z"/><path class="b" d="M103.886,130.295c.48,4.465.4,9.041.479,13.525.11,6.181.186,12.373-.006,18.553-.036,1.158-.079,2.318-.171,3.473-.018.237-.043.474-.063.71-.032.358-.08.468-.007.1a5.254,5.254,0,0,1-.161.732c-.849,2.436,3.014,3.483,3.857,1.064a17.437,17.437,0,0,0,.5-4.817c.117-2.792.139-5.589.146-8.384q.026-9.5-.278-18.992c-.064-1.985-.084-3.992-.3-5.969a2.059,2.059,0,0,0-2-2,2.013,2.013,0,0,0-2,2Z"/><path class="b" d="M104.33,174.406c.392,13.4.305,26.833.212,40.236-.046,6.656-.14,13.312-.339,19.965-.025.833-.056,1.667-.081,2.5a2.694,2.694,0,0,1-.1,1.011c-.581.741-2.487.876-3.307.983a89.583,89.583,0,0,1-9.021.437c-6.393.175-12.79.11-19.184.115-6.222,0-12.442,0-18.66-.265-1.568-.067-3.147-.107-4.709-.264-.742-.075-2.52-.135-2.979-.777-.253-.353-.125-1.185-.146-1.617q-.059-1.18-.116-2.361-.124-2.595-.237-5.19-.342-7.992-.488-15.99c-.107-6.474-.117-12.949-.147-19.423-.038-7.921-.162-15.856.3-23.767.151-2.572-3.85-2.563-4,0-.433,7.425-.346,14.871-.308,22.3.033,6.288.04,12.576.125,18.863q.111,8.208.451,16.411c.143,3.487.229,6.992.473,10.473.246,3.513,3.245,4.6,6.329,4.989,3.2.4,6.473.411,9.692.5s6.412.112,9.619.117c6.794.009,13.592.058,20.386-.042q5.061-.075,10.116-.332c2.652-.134,5.8-.247,8.04-1.855a4.589,4.589,0,0,0,1.855-3.909c.066-1.678.11-3.357.155-5.036q.139-5.3.206-10.6c.212-15.81.323-31.67-.139-47.476-.075-2.568-4.075-2.579-4,0Z"/><path class="b" d="M45.071,135.555c6.967-.1,13.933-.369,20.9-.525,9.374-.21,18.762-.409,28.138-.211,1.932.041,3.866.1,5.8.221.745.048,1.491.1,2.234.184.152.017.3.036.456.052.352.039-.441-.075,0,0,.253.043.506.081.758.132,2.513.51,3.588-3.344,1.064-3.857a50.5,50.5,0,0,0-8.519-.688c-4.331-.129-8.665-.128-13-.1-9.446.062-18.89.3-28.332.55-3.166.085-6.332.193-9.5.24-2.572.038-2.579,4.038,0,4Z"/><path class="b" d="M43.071,170.629c16.4.094,32.8-.233,49.2-.48q6.809-.1,13.617-.224c2.571-.047,2.579-4.047,0-4q-26.4.481-52.8.68c-3.337.022-6.675.043-10.012.024-2.574-.015-2.577,3.985,0,4Z"/><path class="b" d="M69.176,69.186a8.55,8.55,0,0,0,5.951,1.973,8.565,8.565,0,0,0,5.952-1.973,2,2,0,1,0-2.829-2.828c-.076.075-.37.31-.041.055s-.04.019-.137.078c-.118.073-.239.139-.362.2-.081.041-.174.073-.252.119.1-.059.465-.178.15-.07a8.44,8.44,0,0,1-1.206.33c-.152.029-.49.172-.019.014a1.705,1.705,0,0,1-.371.038c-.294.024-.59.036-.885.036-.271,0-.542-.009-.811-.03a2.729,2.729,0,0,0-.447-.044c.192-.023.352.053.047,0a7.356,7.356,0,0,1-1.222-.323c-.161-.059-.42-.229.1.051-.068-.037-.141-.065-.211-.1-.137-.067-.271-.14-.4-.221-.1-.061-.191-.136-.29-.2.577.35.276.223.113.063a2,2,0,0,0-2.828,2.828Z"/><path class="b" d="M74.144,56.642a26.354,26.354,0,0,1,.619,2.831l-.072-.532a1.706,1.706,0,0,1,.011.391l.072-.532a1.051,1.051,0,0,1-.043.176l.2-.478a.688.688,0,0,1-.062.113l.313-.4a.616.616,0,0,1-.093.091l.405-.313a1.844,1.844,0,0,1-.224.119l.478-.2a1.67,1.67,0,0,1-.378.11l.532-.071a1.505,1.505,0,0,1-.355,0l.531.072c-.133-.019-.265-.052-.4-.07a1.515,1.515,0,0,0-.8-.035,1.486,1.486,0,0,0-.743.237,2,2,0,0,0-.718,2.736,1.917,1.917,0,0,0,1.2.92c.353.047.7.135,1.056.151a3.462,3.462,0,0,0,1.617-.394,2.449,2.449,0,0,0,1.324-1.6,3.788,3.788,0,0,0-.013-1.665c-.154-.912-.365-1.816-.6-2.71a2,2,0,0,0-2.46-1.4,2.017,2.017,0,0,0-1.195.919,2.1,2.1,0,0,0-.2,1.541Z"/><path class="b" d="M59.874,49.056c-.462,1.5-.161,4.957,2.684,5.251,3.761-.023,3.961-4.2,2.7-6.163C64.217,46.536,61.169,45.867,59.874,49.056Z"/><path class="b" d="M89.864,49.056c.463,1.5.161,4.957-2.684,5.251-3.76-.023-3.961-4.2-2.7-6.163C85.522,46.536,88.569,45.867,89.864,49.056Z"/></svg>'},
          { name: '职场男性', svgCode: '<svg width="100%" height="100%" preserveAspectRatio="xMidYMid meet" viewBox="-6.88 0 357.246 357.246" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><defs><style>.a{fill:#ffffff;}.b{fill:#211715;}.c{fill:#5c5c5c;}.d{fill:#3d8dcc;}.e{fill:#85807f;}</style></defs><path class="a" d="M171.221,173.6c-.96-.42-14.9-8.46-17.48-14.85-1.121-2.777-1.364-6.23-1.4-9.609,11.021-7.133,19.521-21.875,21.143-26.278a52.163,52.163,0,0,0,2.344-6.361l.653.11a8.829,8.829,0,0,0,6.812-1.966c4.262-3.487,6.029-8.35,7.109-11.529,1.523-4.488,1.619-11.743-.651-15.68-.76-1.319-2.527-3.566-6.681-3.712a8.017,8.017,0,0,0-5.794,2.121s5.309-46.428-49.858-46.428c-59.333,0-52.681,46.428-52.681,46.428a8.014,8.014,0,0,0-5.794-2.121c-4.153.146-5.92,2.393-6.681,3.712-2.27,3.937-2.174,11.192-.65,15.68,1.079,3.179,2.847,8.042,7.109,11.529a8.657,8.657,0,0,0,7.37,1.844,60.938,60.938,0,0,0,11.565,21.822,48.749,48.749,0,0,0,12.8,11.24c-.013,3.589-.2,7.336-1.41,10.318-2.59,6.39-14.34,13.31-15.3,13.73,0,0,4.117,29.818,40.562,29.818S171.221,173.6,171.221,173.6Z"></path><path class="b" d="M149.941,149.424c.074,4.05.3,8.588,2.553,12.1a28.387,28.387,0,0,0,6.077,6.416,78.321,78.321,0,0,0,7.327,5.294,33.729,33.729,0,0,0,4.112,2.44,2.472,2.472,0,0,0,3.284-.861,2.418,2.418,0,0,0-.861-3.283,31.834,31.834,0,0,1-3.712-2.185,70.892,70.892,0,0,1-6.292-4.423,43.067,43.067,0,0,1-3.306-2.91A20.773,20.773,0,0,1,156.9,159.5a11.245,11.245,0,0,1-.922-1.572c.261.549-.189-.52-.2-.564-.175-.52-.319-1.051-.442-1.586a30.91,30.91,0,0,1-.595-6.354c-.056-3.085-4.856-3.095-4.8,0Z"></path><path class="b" d="M84.953,175.676a28.878,28.878,0,0,0,3.958-2.42,58.674,58.674,0,0,0,6.77-5.239,21.891,21.891,0,0,0,5.235-6.48c1.766-3.729,1.916-8.028,1.935-12.083.015-3.089-4.785-3.093-4.8,0a44.235,44.235,0,0,1-.29,5.754,15.288,15.288,0,0,1-1.216,4.36,20.16,20.16,0,0,1-4.722,5.471,51.825,51.825,0,0,1-5.751,4.35,27.034,27.034,0,0,1-3.542,2.143,2.417,2.417,0,0,0-.861,3.283,2.456,2.456,0,0,0,3.284.861Z"></path><path class="c" d="M90.592,162.549a60.639,60.639,0,0,0-11.025,9.026L76.92,172.68c-11.408,4.759-25.942,10.746-37.072,16.122-3.425,1.655-8.344,3.223-11.314,5.6s-5.63,5.926-7.408,11.852c-6.181,20.6-13.832,80.74-18.721,148.3H203.648c-.02-11.124-.6-18.432-.6-28.293,0-7.544-.132-14.453.36-21.557l2.308,2.386c5.415,5.6,14.085,15.122,21.535,19.508a32.99,32.99,0,0,0,28.9,2.395c12.521-4.66,18.719-16.731,22.86-29.433,5.961-18.283,9.574-37.644,13.3-55.68-11.195-1.288-29.457-7.553-40.993-12.24-2.247,7.581-4.3,14.6-6.454,21.685-6.723-18.305-8.312-29.676-15.633-48.769a28.929,28.929,0,0,0-6.04-9.85c-2.59-2.78-6.61-3.56-10.03-5.22-11.13-5.37-25.67-11.36-37.08-16.12,0,0-.716-.3-1.941-.811a61.927,61.927,0,0,0-11.962-10c-4.983,21.36-13.835,44.417-20.852,65.2l-14.125,41.832c-6.28-15.57-10.432-26.049-15.762-41.832-7.017-20.78-15.869-43.837-20.852-65.2"></path><path class="a" d="M263.988,189.562c2.93-7.054,5.235-11.376,9.022-18.684.24-.462,1.922-2.807,3.517-3.268a4.1,4.1,0,0,1,4.091,1.053,5.307,5.307,0,0,1,1.668,3.8,50.023,50.023,0,0,1-2.235,14.653c8.494-1.14,25.5-9.214,34.573-14.008,2.18-1.151,4.348-2.47,6.795-2.816,2.526-.369,6.993,1.377,7.876,3.8,3.446-1.667,5.324-1.634,7.469-.818,2.548.972,3.3,1.989,3.8,3.43a6.187,6.187,0,0,1-.227,4.963,1.738,1.738,0,0,0-.224.693,1.444,1.444,0,0,0,.246.693,7.721,7.721,0,0,1-1.8,8.963,4.263,4.263,0,0,1-.453,5.006c-6.567,7.457-30.031,21.148-43.439,26.317a5.964,5.964,0,0,0-2.056,1.095,5.887,5.887,0,0,0-1.33,2.38c-.835,2.287-1.46,3.9-2.146,5.964-6.088-1.691-20.651-5.811-28.809-8.858a48.368,48.368,0,0,0,1.615-7.143l.155-1.823c-1.445-7.921-1.984-15.789,1.036-23.3Q263.57,190.568,263.988,189.562Z"></path><path class="b" d="M283.346,188.92c6.365-1.54,12.485-4.2,18.439-6.884q4.674-2.1,9.259-4.4c2.824-1.41,5.587-3.18,8.513-4.353a6.153,6.153,0,0,1,4.4-.338,7.474,7.474,0,0,1,2.081.957,4.185,4.185,0,0,1,.582.464c.02.019.4.439.274.28-.088-.108.23.426.088.083a2.455,2.455,0,0,0,3.525,1.434c1.755-.827,3.376-1.3,5.066-.77a6.135,6.135,0,0,1,2.161,1.116,1.919,1.919,0,0,1,.478.718c-.111-.234,0,.011.037.114a5.91,5.91,0,0,1,.272.953c.221,1.253-.413,2.092-.686,3.249-.315,1.335.4,2.266.7,3.427a5.444,5.444,0,0,1-1.195,4.879c-2.044,2.3,1.339,5.711,3.394,3.394a10.63,10.63,0,0,0,2.682-5.973,9.934,9.934,0,0,0-.119-2.955c-.167-.915-.685-1.716-.873-2.594V183a29.22,29.22,0,0,0,.911-3.375,8.691,8.691,0,0,0-.46-3.557,7.373,7.373,0,0,0-3.16-4.036,11.292,11.292,0,0,0-5.457-1.7,13.785,13.785,0,0,0-6.175,1.688l3.525,1.435c-1.362-3.285-4.824-5.061-8.226-5.509-4.017-.528-7.6,1.855-11.006,3.632-6.371,3.322-12.882,6.437-19.555,9.107a79.2,79.2,0,0,1-10.752,3.607c-3,.726-1.731,5.356,1.276,4.629Z"></path><path class="b" d="M341.271,192.289c-.414-3.07-4.21-4.237-6.829-3.709a17.247,17.247,0,0,0-4.044,1.775c-1.414.707-2.823,1.424-4.233,2.139-5.441,2.757-10.926,5.589-16.8,7.305-2.959.864-1.7,5.5,1.276,4.629a90.779,90.779,0,0,0,14.8-6.2c2.406-1.2,4.794-2.429,7.2-3.631.9-.45,2.062-1.326,3.086-1.385a4.022,4.022,0,0,1,.776.132s.346.231.219.137-.139-.423-.071.087a2.415,2.415,0,0,0,2.953,1.677,2.467,2.467,0,0,0,1.676-2.953Z"></path><path class="b" d="M341.323,180.351a6.1,6.1,0,0,0-4.578-1.753,10.065,10.065,0,0,0-4.332,1.24c-3.3,1.492-6.5,3.164-9.82,4.612-5.422,2.367-11.034,5.035-16.334,7.2a2.477,2.477,0,0,0-1.676,2.952,2.417,2.417,0,0,0,2.952,1.677c5.328-2.176,10.533-4.646,15.8-6.955,2.948-1.292,5.851-2.662,8.754-4.052,1.209-.58,2.419-1.21,3.666-1.7a2.37,2.37,0,0,1,2.171.174,2.42,2.42,0,0,0,3.394,0,2.449,2.449,0,0,0,0-3.394Z"></path><path class="b" d="M336.642,193.565c.439,1.614-1.044,2.669-2.115,3.655-1.184,1.089-2.555,2.205-3.7,3.076-3.556,2.691-7.3,5.137-11.1,7.469a171.514,171.514,0,0,1-24.174,12.655,26.808,26.808,0,0,0-3.527,1.481,7.607,7.607,0,0,0-3.055,4.275c-1.062,2.83-2.091,5.669-2.965,8.563-.895,2.963,3.736,4.23,4.628,1.276.793-2.626,1.727-5.195,2.674-7.768.374-1.017.583-1.979,1.632-2.453.961-.434,1.972-.776,2.944-1.185,4.225-1.779,8.346-3.793,12.4-5.934a164.6,164.6,0,0,0,24.13-15.127c3.537-2.745,8.254-6.145,6.865-11.259-.809-2.977-5.441-1.713-4.629,1.276Z"></path><path class="b" d="M264.921,216.983A60.394,60.394,0,0,1,263.4,201.5c.3-5.089,2.141-9.667,4.183-14.277,1.79-4.04,3.792-7.978,5.824-11.9.923-1.78,3.53-8.021,6-4.365a4.828,4.828,0,0,1,.44,3.111c-.053,1.341-.149,2.68-.3,4.014a44.389,44.389,0,0,1-1.886,8.66c-.945,2.948,3.688,4.211,4.629,1.276a50.3,50.3,0,0,0,1.981-9.281c.313-2.565.87-5.735.149-8.261a7.334,7.334,0,0,0-6.054-5.379c-2.652-.279-4.788,1.14-6.389,3.133a36.532,36.532,0,0,0-3.582,6.344c-1.144,2.22-2.272,4.449-3.343,6.707-2.442,5.144-5.105,10.525-6,16.19-1.105,6.963-.138,13.936,1.245,20.787a2.424,2.424,0,0,0,2.952,1.677,2.449,2.449,0,0,0,1.676-2.953Z"></path><path class="b" d="M328.084,172.019c-4.325,2.024-8.473,4.426-12.783,6.49-5.039,2.413-9.924,5.138-14.881,7.713-2.743,1.424-.318,5.568,2.422,4.145,4.957-2.575,9.843-5.3,14.882-7.714,4.31-2.063,8.458-4.465,12.782-6.489a2.42,2.42,0,0,0,.861-3.284,2.454,2.454,0,0,0-3.283-.861Z"></path><path class="b" d="M296.434,191.023q7.18,5.975,13.756,12.626a2.4,2.4,0,1,0,3.394-3.4q-6.567-6.643-13.756-12.625a2.454,2.454,0,0,0-3.394,0,2.428,2.428,0,0,0,0,3.394Z"></path><path class="b" d="M308.57,200.108c-2.805.059-5.607.2-8.4.426a34.428,34.428,0,0,0-7.987,1.222,17.209,17.209,0,0,0-10,8.652,2.461,2.461,0,0,0,.861,3.284,2.422,2.422,0,0,0,3.283-.861,12.456,12.456,0,0,1,7.856-6.665,35.824,35.824,0,0,1,6.705-.889c2.558-.2,5.12-.315,7.684-.369,3.084-.063,3.1-4.864,0-4.8Z"></path><path class="b" d="M259.539,216.777c-.019.216-.132.842.015-.02-.03.171-.052.344-.081.516-.07.406-.15.809-.237,1.211-.2.94-.436,1.872-.68,2.8-.456,1.739-.96,3.465-1.434,5.2a2.4,2.4,0,1,0,4.628,1.276c.986-3.6,2.251-7.244,2.589-10.985a2.408,2.408,0,0,0-2.4-2.4,2.463,2.463,0,0,0-2.4,2.4Z"></path><path class="a" d="M290.529,233.166c-5.288-1.46-24.141-6.715-32.246-10.042-.78,1.954-2.359,6.728-3.354,9.3l-.221.554c10.254,3.987,24.081,8.609,34.152,10.385l.062-.2c.985-3.144,2.406-8.755,2.738-9.688Z"></path><path class="b" d="M247.18,252.673c-5.139-14.038-8.446-28.641-13.413-42.734a66.5,66.5,0,0,0-4.684-11.325c-1.83-3.165-4.249-6.33-7.5-8.115a41.537,41.537,0,0,0-4.951-2.137c-1.628-.634-3.185-1.406-4.765-2.149-3.459-1.626-6.947-3.19-10.448-4.723-8.186-3.586-16.444-7-24.692-10.443a2.416,2.416,0,0,0-2.953,1.676,2.463,2.463,0,0,0,1.677,2.953c6.916,2.884,13.839,5.752,20.716,8.727,6.84,2.959,13.517,6.345,20.447,9.076a15.314,15.314,0,0,1,4.07,2.143,17.266,17.266,0,0,1,3.216,3.752,44.561,44.561,0,0,1,4.623,10.107c2.489,6.887,4.585,13.9,6.6,20.935,2.265,7.915,4.6,15.8,7.432,23.533a2.466,2.466,0,0,0,2.953,1.677,2.42,2.42,0,0,0,1.676-2.953Z"></path><path class="a" d="M129.025,171.791a.775.775,0,0,0-.2.206h-4.637a6,6,0,0,0-2.053-1.161c-10.565-4.25-19.38-10.732-23.241-15.921-3.808,3.5-5.018,6.209-7.495,10.953,5.086,20.413,13.392,42.169,20.047,61.878,5.329,15.783,9.482,26.262,15.761,41.831q7.063-20.915,14.126-41.831c6.688-19.806,15.043-41.681,20.123-62.182-2.371-4.557-3.61-7.224-7.337-10.649-3.86,5.189-12.675,11.671-23.24,15.921A9.142,9.142,0,0,0,129.025,171.791Z"></path><path class="a" d="M144.812,189.66a103.462,103.462,0,0,0,16-25.333c-1.984-3.828-3.318-6.309-6.7-9.412-3.86,5.189-12.675,11.671-23.24,15.921A6,6,0,0,0,128.823,172c-.253.471.239.885.471,1.256.363.581,2.148,2.074,5.185,5.407C137.925,182.442,141.96,186.253,144.812,189.66Z"></path><path class="a" d="M108.2,189.66a103.491,103.491,0,0,1-16-25.333c1.985-3.828,3.319-6.309,6.695-9.412,3.861,5.189,12.676,11.671,23.241,15.921A6,6,0,0,1,124.186,172c.253.471-.239.885-.47,1.256-.364.581-2.148,2.074-5.185,5.407C115.085,182.442,111.049,186.253,108.2,189.66Z"></path><path class="d" d="M129.454,174.993c-2.608.008-4.777.014-7.413.015-.864.857-2.04,2.039-3.51,3.652-.787.864-1.605,1.729-2.433,2.591.582,3.019.991,4.927,1.632,7.674.1.483.224.949.345,1.432a13.253,13.253,0,0,1,.518,3.175c0,.616-3.02,22.655-5.134,40.092,4.424,12.7,8.279,22.4,13.746,35.953l12.957-38.368c-2.658-17.775-5.471-36.349-5.454-37.332a19.332,19.332,0,0,1,1.242-5.625c.744-2.285,1.2-4.284,1.688-6.248-1.074-1.11-2.142-2.228-3.159-3.344-1.482-1.626-2.665-2.814-3.531-3.672Z"></path><path class="b" d="M119.326,195.785c4.969,0,9.938-.11,14.908-.112a2.4,2.4,0,0,0,0-4.8c-4.97,0-9.939.11-14.908.112a2.4,2.4,0,0,0,0,4.8Z"></path><path class="b" d="M114.018,183.093q.644,3.246,1.4,6.47a14.605,14.605,0,0,1,.758,4.184c-.1,1.482-.37,2.971-.563,4.444-.886,6.783-1.786,13.564-2.659,20.349q-.9,7-1.762,14.009a2.413,2.413,0,0,0,2.4,2.4,2.459,2.459,0,0,0,2.4-2.4c.991-8.115,2.041-16.223,3.1-24.329.625-4.764,1.471-9.555,1.866-14.345a13.876,13.876,0,0,0-.631-4.4c-.628-2.538-1.174-5.1-1.682-7.662a2.424,2.424,0,0,0-2.952-1.677,2.451,2.451,0,0,0-1.677,2.953Z"></path><path class="b" d="M130.664,172.594q-4.42.007-8.841.018a2.4,2.4,0,1,0,0,4.8q4.421-.007,8.841-.018a2.4,2.4,0,0,0,0-4.8Z"></path><path class="b" d="M142.474,230.559q-1.737-11.625-3.476-23.248-.64-4.321-1.266-8.644-.22-1.542-.433-3.083c-.025-.186.057.441-.006-.053-.019-.148-.039-.3-.058-.445-.033-.261-.072-.523-.094-.786a9.409,9.409,0,0,1,.459-3.278c.583-2.107,1.3-4.167,1.838-6.29.754-3-3.874-4.275-4.629-1.276-.852,3.385-2.635,6.99-2.5,10.536.058,1.48.371,2.978.577,4.443.9,6.405,1.873,12.8,2.83,19.2q1.064,7.1,2.127,14.2a2.416,2.416,0,0,0,2.952,1.676,2.46,2.46,0,0,0,1.676-2.952Z"></path><path class="b" d="M123.461,273.178a50.613,50.613,0,0,0-2.782,16.5c.073,3.537.459,7.083.683,10.612.682,10.781,1.125,21.572,1.876,32.35q.774,11.109,1.748,22.2a2.463,2.463,0,0,0,2.4,2.4,2.419,2.419,0,0,0,2.4-2.4c-1.86-21.156-2.784-42.353-4.23-63.534a44.907,44.907,0,0,1,2.534-16.858c.96-2.944-3.674-4.2-4.629-1.276Z"></path><path class="b" d="M159.868,161.911c-3.4,14.528-8.184,28.695-13.076,42.777q-7.478,21.522-14.76,43.1l-8.572,25.386c-.99,2.933,3.644,4.192,4.629,1.276q7.7-22.8,15.4-45.6c4.73-14.005,9.848-27.879,14.34-41.964,2.494-7.821,4.8-15.708,6.67-23.7.7-3.005-3.923-4.287-4.629-1.276Z"></path><path class="b" d="M160.971,164.621a55,55,0,0,1,10.09,8.2,56.188,56.188,0,0,1,4.583,5.121c.587.754,1.141,1.536,1.66,2.338.261.4.515.813.754,1.23q.153.265.3.535.107.2.207.4.169.345-.053-.174l.328-1.211q.254-.254-.111,0l-.646.357-.861.475-2.368,1.306-4.52,2.493a2.418,2.418,0,0,0-.486,3.769c2.22,2.011,4.43,4.033,6.573,6.126q.677.66,1.345,1.332a8.909,8.909,0,0,1,1.643,1.687c.091.2.118-.057-.031.291-.321.751-.785,1.478-1.17,2.2q-4.035,7.555-8.216,15.033c-5.742,10.293-11.642,20.5-17.619,30.655q-4.952,8.412-9.965,16.788c-1.589,2.658,2.559,5.074,4.144,2.422,12.585-21.053,25.033-42.212,36.547-63.875.832-1.565,1.542-3.1.944-4.889-.528-1.579-1.908-2.728-3.05-3.872-2.506-2.51-5.122-4.909-7.751-7.29l-.486,3.77,6.028-3.325c1.749-.965,4.406-1.885,4.528-4.237.081-1.571-1.04-3.14-1.863-4.41a45.375,45.375,0,0,0-2.985-4.025,61.093,61.093,0,0,0-15.069-13.352c-2.643-1.616-5.057,2.534-2.423,4.144Z"></path><path class="b" d="M88.278,163.187c3.405,14.528,8.185,28.695,13.077,42.778,4.723,13.6,9.24,27.282,14.3,40.759,2.8,7.458,5.759,14.853,8.736,22.241a2.475,2.475,0,0,0,2.952,1.676,2.415,2.415,0,0,0,1.676-2.952c-5.282-13.11-10.4-26.269-14.944-39.656-4.75-14-9.846-27.89-14.352-41.975-2.549-7.967-4.9-16-6.812-24.147-.7-3.006-5.334-1.734-4.629,1.276Z"></path><path class="b" d="M89.381,160.477a61.089,61.089,0,0,0-15.068,13.352,45.672,45.672,0,0,0-2.9,3.887c-.853,1.3-2.032,2.937-1.953,4.548.117,2.361,2.775,3.27,4.529,4.237l6.027,3.325-.486-3.77c-2.454,2.222-4.9,4.46-7.249,6.79a18.051,18.051,0,0,0-3.144,3.453,5.076,5.076,0,0,0,.113,5.01c2.655,5.313,5.675,10.476,8.607,15.64,6.281,11.061,12.82,21.974,19.453,32.828q5.508,9.015,11.093,17.983c1.626,2.619,5.78.212,4.144-2.422-12.589-20.274-25.138-40.611-36.539-61.584q-1.119-2.058-2.219-4.126a3.744,3.744,0,0,1-.472-.9c-.05-.308-.1.186.047-.136.277-.6,1.179-1.222,1.642-1.687,2.557-2.572,5.231-5.024,7.918-7.458a2.418,2.418,0,0,0-.486-3.769l-4.52-2.493L75.77,182l-1.077-.593c-.178-.1-.955-.724-.757-.354l.328,1.211c.016.383-.148.322.084-.09.1-.176.193-.356.293-.533q.353-.622.741-1.226c.511-.8,1.058-1.58,1.637-2.332A62.631,62.631,0,0,1,91.8,164.621c2.631-1.608.223-5.761-2.423-4.144Z"></path><path class="b" d="M146.509,191.357a109.671,109.671,0,0,0,12.858-18.7q1.314-2.456,2.512-4.971a17.533,17.533,0,0,0,1.248-2.718c.327-1.191-.451-2.264-.984-3.268a31.467,31.467,0,0,0-6.329-8.479,2.446,2.446,0,0,0-3.769.485c-4.025,5.338-10.918,9.6-17.06,12.668-2,1-4.088,1.762-6.09,2.731-2.092,1.012-3.315,2.98-1.836,5.134,1.56,2.271,3.865,4.1,5.723,6.121,3.4,3.7,7.087,7.155,10.333,11a2.42,2.42,0,0,0,3.394,0,2.45,2.45,0,0,0,0-3.394c-3.051-3.615-6.5-6.865-9.719-10.332-1.382-1.491-2.765-2.973-4.209-4.4-.389-.386-.773-.778-1.162-1.163-.156-.154-.5-.66-.008.043-.06-.084-.381-.633-.344-.472v1.276l.071-.276-.618,1.059c-.244.286.251-.17.433-.267s.373-.191.562-.277c.808-.364,1.642-.676,2.455-1.03q2.142-.933,4.222-2a69.957,69.957,0,0,0,7.382-4.372,44.011,44.011,0,0,0,10.616-9.621l-3.77.486a31.163,31.163,0,0,1,6.32,8.926v-2.423a109.915,109.915,0,0,1-15.625,24.848,2.466,2.466,0,0,0,0,3.394A2.42,2.42,0,0,0,146.509,191.357Z"></path><path class="b" d="M109.894,187.963A109.946,109.946,0,0,1,94.27,163.115v2.423a31.159,31.159,0,0,1,6.319-8.926l-3.769-.486a44.011,44.011,0,0,0,10.616,9.621,69.856,69.856,0,0,0,7.382,4.372q1.977,1.016,4.015,1.911c.812.356,1.638.681,2.451,1.035.263.114.517.226.773.362.163.087.721.606.432.267l-.617-1.059.07.276v-1.276c.037-.161-.284.388-.343.472.5-.7.148-.2-.008-.043-.39.385-.773.777-1.162,1.163-1.444,1.431-2.828,2.913-4.209,4.4-3.214,3.467-6.668,6.717-9.72,10.332a2.465,2.465,0,0,0,0,3.394,2.42,2.42,0,0,0,3.394,0c2.855-3.382,6.066-6.443,9.1-9.665,1.405-1.494,2.778-3.015,4.227-4.468.7-.7,1.459-1.372,2.1-2.135,1.372-1.644,1.985-3.831-.03-5.3-1.651-1.2-3.817-1.783-5.661-2.648a69.689,69.689,0,0,1-10.889-6.324,37.47,37.47,0,0,1-7.768-7.116,2.447,2.447,0,0,0-3.77-.485,31.505,31.505,0,0,0-6.328,8.479c-.487.916-1.173,1.87-1.027,2.949a10.624,10.624,0,0,0,1.2,2.845q1.245,2.61,2.6,5.163a109.671,109.671,0,0,0,12.858,18.7,2.42,2.42,0,0,0,3.394,0A2.451,2.451,0,0,0,109.894,187.963Z"></path><path class="b" d="M52.189,354.846c.016-9.94.585-19.866.6-29.806.017-11,.049-21.952-1.905-32.824q-5.524-30.735-9.465-61.732c-1.368-10.628-2.615-21.274-3.671-31.938a2.468,2.468,0,0,0-2.4-2.4,2.416,2.416,0,0,0-2.4,2.4c1.966,19.84,4.537,39.625,7.474,59.343q2.323,15.6,5.036,31.132a149.452,149.452,0,0,1,2.183,15.832c.364,5.367.373,10.749.359,16.126-.031,11.294-.594,22.574-.612,33.867-.005,3.088,4.795,3.093,4.8,0Z"></path><path class="b" d="M215.509,200.436c-1.956,19.661-4.521,39.264-7.489,58.8q-2.358,15.515-5.105,30.967a134.38,134.38,0,0,0-2,16.03c-.3,5.226-.287,10.463-.271,15.695.034,10.979.592,21.944.61,32.921,0,3.088,4.805,3.093,4.8,0-.016-9.535-.59-19.057-.6-28.59-.012-10.541-.258-21.148,1.523-31.579,3.521-20.626,6.9-41.246,9.6-62,1.4-10.729,2.664-21.476,3.735-32.242a2.417,2.417,0,0,0-2.4-2.4,2.452,2.452,0,0,0-2.4,2.4Z"></path><path class="b" d="M76.282,170.366q-22.075,9.207-43.841,19.057a22.668,22.668,0,0,0-8.175,5.766,27.862,27.862,0,0,0-5.181,9.554,107.471,107.471,0,0,0-2.842,11.281c-2.306,10.88-3.979,21.9-5.519,32.909C8.611,264.041,6.842,279.2,5.268,294.369Q2.51,320.96.518,347.622q-.262,3.463-.513,6.927a2.421,2.421,0,0,0,2.4,2.4,2.446,2.446,0,0,0,2.4-2.4q1.926-26.562,4.541-53.068c1.522-15.3,3.229-30.574,5.26-45.811,1.526-11.448,3.21-22.893,5.424-34.231.77-3.944,1.6-7.882,2.631-11.769,1.34-5.072,3.226-10.345,7.607-13.6,2.864-2.125,6.428-3.239,9.654-4.675,3.461-1.54,6.857-3.227,10.316-4.774,7.312-3.271,14.7-6.37,22.093-9.453q2.613-1.089,5.227-2.178a2.479,2.479,0,0,0,1.676-2.952,2.413,2.413,0,0,0-2.952-1.676Z"></path><path class="b" d="M143.467,283.1c.267.24.483.53.742.773q-.364-.481-.15-.185c.047.066.092.134.135.2.074.116.143.236.208.358.1.192.208.609-.024-.107.045.141.105.276.149.418a5.513,5.513,0,0,1,.183.834l-.086-.638a6.032,6.032,0,0,1,0,1.513l.086-.638a6.626,6.626,0,0,1-.173.838q-.049.176-.108.348c-.038.113-.231.587-.035.123s0-.018-.053.091-.11.208-.169.309-.117.185-.177.277c-.248.383.42-.482.141-.178-.1.107-.5.649-.644.625.016,0,.556-.389.188-.156-.059.038-.117.079-.177.116-.135.084-.274.163-.416.234-.063.033-.128.061-.192.093-.338.167.5-.184.228-.1-.136.044-.268.1-.406.139a6.952,6.952,0,0,1-1,.219l.638-.086a7.121,7.121,0,0,1-1.816.006l.638.086a8.3,8.3,0,0,1-1.4-.359c.724.232.394.172.209.081-.117-.058-.233-.12-.345-.187-.083-.05-.162-.105-.243-.158-.33-.212.512.441.129.1a8.719,8.719,0,0,1-.624-.622c-.283-.311.343.508-.006-.014-.067-.1-.13-.2-.189-.307s-.107-.208-.161-.312c-.187-.362.22.623.035.046a4.707,4.707,0,0,1-.171-.75l.086.638a5.2,5.2,0,0,1,0-1.3l-.086.638a6.1,6.1,0,0,1,.2-.906c.043-.14.093-.278.143-.417.162-.456-.243.5-.024.064a9.052,9.052,0,0,1,.46-.829c.08-.126.164-.249.251-.371a1.066,1.066,0,0,1,.133-.179c-.073.063-.394.477-.132.181.09-.1.177-.2.274-.3s.465-.391.1-.113.041-.019.14-.082q.2-.126.416-.234c.024-.012.173-.1.194-.093,0,0-.592.227-.273.117.139-.048.276-.1.416-.142a6.488,6.488,0,0,1,.983-.209l-.638.086a6.45,6.45,0,0,1,1.577,0l-.638-.086a6.2,6.2,0,0,1,.662.132c.091.024.18.051.269.08s.5.195.08.015c-.4-.171-.073-.028.019.018s.2.1.294.161.188.122.281.183c.338.221-.459-.377-.132-.095a2.559,2.559,0,0,0,1.7.7,2.4,2.4,0,0,0,1.7-4.1,7.636,7.636,0,0,0-4.905-1.866,8.111,8.111,0,0,0-4.511,1.236,8.607,8.607,0,0,0-3.607,8.656,7.446,7.446,0,0,0,3.058,4.352,8.368,8.368,0,0,0,11.584-2.63,8.382,8.382,0,0,0,.967-4.491,7.95,7.95,0,0,0-2.586-5.257,2.4,2.4,0,0,0-3.395,3.394Z"></path><path class="b" d="M291.236,243.8c.993-3.2,1.66-6.517,2.738-9.688a2.429,2.429,0,0,0-1.676-2.953c-8.695-2.4-17.386-4.852-25.953-7.681-2.5-.825-4.989-1.678-7.424-2.672-1.289-.526-2.525.591-2.953,1.676-1.208,3.066-2.173,6.223-3.353,9.3a2.417,2.417,0,0,0,1.676,2.952,2.454,2.454,0,0,0,2.952-1.676c1.18-3.077,2.146-6.234,3.354-9.3l-2.952,1.676c9.406,3.838,19.389,6.447,29.157,9.183q2.109.591,4.22,1.171l-1.676-2.952c-1.079,3.171-1.745,6.487-2.738,9.688-.918,2.957,3.714,4.221,4.628,1.276Z"></path><path class="b" d="M238.847,280.062c5.333-15.806,10.052-31.8,14.79-47.789l-2.952,1.676Q260.93,238.1,271.5,241.4a116.508,116.508,0,0,0,20.815,4.871L290,243.237c-2.278,11.032-4.434,22.092-7.04,33.054-1.336,5.618-2.788,11.211-4.432,16.748a119.041,119.041,0,0,1-4.7,13.605c-3.3,7.591-8.053,14.855-15.568,18.792a30.888,30.888,0,0,1-28.24-.05c-4.5-2.352-8.359-5.752-12.022-9.232s-7.09-7.145-10.587-10.766c-2.15-2.226-5.542,1.17-3.394,3.394,6.589,6.823,13.071,14.245,21.156,19.355a35.827,35.827,0,0,0,30.713,3.489c8.988-3.09,15.567-9.87,19.963-18.14,4.977-9.365,7.722-19.94,10.323-30.158,3.267-12.837,5.778-25.847,8.455-38.815a2.447,2.447,0,0,0-2.314-3.038c-6.6-.781-13.466-2.8-19.922-4.82q-10.359-3.245-20.433-7.335A2.426,2.426,0,0,0,249.009,231c-4.738,15.991-9.457,31.983-14.79,47.789-.99,2.933,3.645,4.192,4.628,1.276Z"></path><path class="e" d="M181.407,35.164a45.822,45.822,0,0,0-8.819-10.348L164.4,17.538c-10.614-11.827-24.721-15.1-38.626-15.1a63.017,63.017,0,0,0-39,12.821A56.94,56.94,0,0,0,75.778,26.711c-7.126,6.974-12.811,22.212-12.386,37.323a79.255,79.255,0,0,0,2.491,20.283,9.316,9.316,0,0,1,3.056-.588,8.014,8.014,0,0,1,5.794,2.121l2.3,1.61a85.754,85.754,0,0,1,1-9.211c1.066-6.475,7.785-9.46,10.64-15.24,1.645-3.329,2.624-7.221,5.437-9.59,2.119-1.784,4.946-2.389,7.673-2.676,4.224-.445,18.511.192,23.289,1.074,4.043.227,7.96,1.035,13.726,1.768,3.127.4,8.926,1.422,11.144,1.867,8.723,2.005,12.065,4.183,16.447,10.118,1.679,2.275,3.466,6.427,5.12,11.83l5.765,8.45a8.017,8.017,0,0,1,5.794-2.121,9.509,9.509,0,0,1,2.842.508c1.9-7.559,2.709-13.244,2.415-20.2C187.759,50.682,185.559,42.036,181.407,35.164Z"></path><path class="b" d="M117.464,128.968a20.66,20.66,0,0,0,9.954,2.3c3.551-.023,7.156-.714,10-2.932a2.412,2.412,0,0,0,0-3.394,2.462,2.462,0,0,0-3.394,0c.715-.557.114-.1-.07.019-.2.129-.41.249-.622.36-.155.082-.9.386-.279.154-.286.107-.568.218-.859.312a14.444,14.444,0,0,1-5.1.681,15.009,15.009,0,0,1-4.867-.655c-.314-.094-.621-.207-.931-.313-.1-.035-.2-.087-.3-.117.6.173.194.087.03.01-.385-.181-.764-.371-1.14-.569a2.453,2.453,0,0,0-3.284.861,2.426,2.426,0,0,0,.861,3.283Z"></path><path class="b" d="M126.3,105.393a47.537,47.537,0,0,1,1.111,5.084l-.086-.638a3.054,3.054,0,0,1,.019.7l.086-.638a1.788,1.788,0,0,1-.077.315l.242-.573a1.293,1.293,0,0,1-.112.2l.376-.486a1.036,1.036,0,0,1-.167.164l.486-.375a3.355,3.355,0,0,1-.4.213l.573-.242a2.986,2.986,0,0,1-.679.2l.638-.086a2.662,2.662,0,0,1-.637,0l.638.086c-.24-.034-.476-.092-.716-.124a2.649,2.649,0,0,0-1.849.241,2.4,2.4,0,0,0-.861,3.284,2.3,2.3,0,0,0,1.434,1.1c.528.071,1.041.206,1.578.23a5.007,5.007,0,0,0,2.3-.544,3.281,3.281,0,0,0,1.831-2.167,5.527,5.527,0,0,0-.024-2.357c-.277-1.638-.656-3.261-1.077-4.868a2.4,2.4,0,0,0-4.628,1.276Z"></path><path class="b" d="M99.109,91.051c-.849,2.759-.3,9.105,4.931,9.646,6.908-.042,7.276-7.715,4.95-11.323C107.086,86.42,101.488,85.192,99.109,91.051Z"></path><path class="b" d="M154.642,91.051c.85,2.759.3,9.106-4.93,9.646-6.909-.042-7.276-7.715-4.951-11.323C146.665,86.42,152.263,85.192,154.642,91.051Z"></path><path class="b" d="M76.43,84.153a11.1,11.1,0,0,0-12.2-1.72c-3,1.429-4.721,4.384-5.477,7.513-1.775,7.345.086,15.7,4.292,21.926,3.046,4.508,7.453,7.843,13.126,7.058a2.414,2.414,0,0,0,1.676-2.952,2.464,2.464,0,0,0-2.952-1.676c-3.194.442-5.954-2.309-7.6-4.7a27.627,27.627,0,0,1-3.467-7.419,22.427,22.427,0,0,1-.818-8.782,13.519,13.519,0,0,1,.909-3.937,8.68,8.68,0,0,1,.684-1.252c.087-.137.352-.449.1-.153.172-.2.354-.393.543-.579a4.454,4.454,0,0,1,1.405-.906,6.537,6.537,0,0,1,1.869-.427,5.86,5.86,0,0,1,4.518,1.4c2.283,2.072,5.688-1.312,3.394-3.394Z"></path><path class="b" d="M178.969,87.547a5.663,5.663,0,0,1,8.193.351c.318.33-.1-.185.137.163.131.194.259.389.376.591a11.159,11.159,0,0,1,1.2,3.772,24.16,24.16,0,0,1-3.453,16.082c-1.673,2.773-4.65,6.3-8.307,5.8a2.482,2.482,0,0,0-2.952,1.676,2.417,2.417,0,0,0,1.676,2.952c9.259,1.281,14.677-8,17.017-15.619a26.836,26.836,0,0,0,.676-11.986c-.522-3.237-1.887-6.34-4.643-8.252a11.011,11.011,0,0,0-13.314,1.08c-2.292,2.081,1.11,5.467,3.394,3.394Z"></path><path class="b" d="M174.477,112.1a67.112,67.112,0,0,1-3.512,10.637c.108-.28.108-.235-.072.151-.092.2-.182.4-.276.592-.243.509-.5,1.012-.761,1.511-.649,1.233-1.345,2.443-2.071,3.632a63.8,63.8,0,0,1-13.842,16.408,25.487,25.487,0,0,1-10.237,5.3c-3.009.693-1.736,5.322,1.276,4.629,7.756-1.786,14.208-7.469,19.267-13.355a69.6,69.6,0,0,0,10.789-16.3c.166-.368.323-.739.478-1.112.04-.1.324-.787.181-.451-.185.433.133-.284.135-.288.137-.311.267-.624.4-.938q.327-.786.625-1.583a50.65,50.65,0,0,0,2.252-7.563,2.459,2.459,0,0,0-1.676-2.952,2.423,2.423,0,0,0-2.952,1.676Z"></path><path class="b" d="M72.753,113.2a64.076,64.076,0,0,0,9.014,21.217c4.6,6.933,10.657,13.422,17.981,17.512a35.653,35.653,0,0,0,12.175,4.166,2.48,2.48,0,0,0,2.953-1.676,2.418,2.418,0,0,0-1.676-2.952C97.959,149.22,86.575,136.021,80.769,122.5a60.886,60.886,0,0,1-3.387-10.575c-.682-3.012-5.311-1.737-4.629,1.276Z"></path><path class="b" d="M166.1,15.841A47.7,47.7,0,0,0,138.771,1.134,72.151,72.151,0,0,0,106.83,2.58a62.3,62.3,0,0,0-26.848,15.5,56.94,56.94,0,0,0-5.668,6.565c-1.274,1.735-2.833,3.24-4.062,5.036a51.45,51.45,0,0,0-6.517,14.181,64.8,64.8,0,0,0-2.754,19.72,88.79,88.79,0,0,0,2.381,20.6c.765,2.991,5.4,1.723,4.629-1.276a76.183,76.183,0,0,1-2.172-17.2,66.273,66.273,0,0,1,1.452-16.436,53.4,53.4,0,0,1,5.263-14.139,31.463,31.463,0,0,1,3.482-5.153c.691-.808,1.448-1.531,2.073-2.393.8-1.105,1.652-2.165,2.553-3.192A56.415,56.415,0,0,1,104.667,8.3a67.175,67.175,0,0,1,29.558-3.008c10.93,1.219,21.039,5.734,28.479,13.946,2.078,2.294,5.464-1.109,3.394-3.394Z"></path><path class="b" d="M188.387,84.183a74.668,74.668,0,0,0,2.383-16.222,93.98,93.98,0,0,0-1.076-15.291c-1.065-7.363-3.278-14.649-7.57-20.8a52.294,52.294,0,0,0-7.839-8.75c-2.283-2.071-5.688,1.314-3.394,3.4,4.686,4.25,8.613,9.026,10.947,14.8,3.105,7.684,4.011,16.267,4.137,24.49a67.24,67.24,0,0,1-2.216,17.1c-.735,3,3.892,4.28,4.628,1.276Z"></path><path class="b" d="M125.708,49.5a95.3,95.3,0,0,0-12.49-1.121,74.245,74.245,0,0,0-11.827,0c-3.115.36-6.175,1.089-8.672,3.089-2.291,1.834-3.583,4.479-4.706,7.123a23.584,23.584,0,0,1-3.756,6.623c-1.631,1.863-3.489,3.518-5.051,5.443a16.483,16.483,0,0,0-3.7,8.3c-.48,3.2-.714,6.405-.968,9.626a2.421,2.421,0,0,0,2.4,2.4,2.448,2.448,0,0,0,2.4-2.4c.365-4.641.08-10.184,2.939-14.1,2.8-3.837,6.76-6.538,8.8-10.962,1.09-2.363,1.879-4.994,3.463-7.094,1.527-2.023,3.9-2.791,6.318-3.168a56.639,56.639,0,0,1,10.73-.148c2.465.093,4.928.226,7.387.417,1.117.086,2.233.184,3.346.306.2.022.407.045.611.07.107.012.913.121.37.044q.569.079,1.132.18a2.467,2.467,0,0,0,2.953-1.676,2.421,2.421,0,0,0-1.677-2.952Z"></path><path class="b" d="M149.3,57.766a38.71,38.71,0,0,1,7.452,2.344,15.614,15.614,0,0,1,4.963,3.577c3.865,3.985,5.83,9.018,7.476,14.351.908,2.942,5.543,1.687,4.628-1.276A58.86,58.86,0,0,0,169.9,66.718a28.314,28.314,0,0,0-4.789-6.425c-3.943-4.066-9.128-5.9-14.533-7.155-3-.7-4.288,3.929-1.276,4.628Z"></path><path class="b" d="M141.426,51.951c-.791-3.363-3.43-6.229-6.078-8.289a30.672,30.672,0,0,0-15.089-5.918,2.411,2.411,0,0,0-2.4,2.4,2.461,2.461,0,0,0,2.4,2.4,28.259,28.259,0,0,1,7.056,1.9c-.276-.114.343.152.4.177.273.124.544.254.812.387q.723.36,1.421.763.665.385,1.305.813.332.222.655.454c.078.056.594.442.222.155a19.486,19.486,0,0,1,2,1.779q.4.4.766.832c.137.158.269.321.4.483q.165.209-.108-.142.1.135.2.273a13.852,13.852,0,0,1,1.043,1.719c.061.123.109.256.175.376-.321-.586-.1-.274-.046-.086.082.269.175.529.239.8a2.4,2.4,0,0,0,4.629-1.276Z"></path></g></svg>' },
          { name: '男孩', svgCode: '<svg width="100%" height="100%"  preserveAspectRatio="xMidYMid meet" viewBox="-106.52 0 319.857 319.857" xmlns="http://www.w3.org/2000/svg"><defs><style>.a{fill:#3f88c9;}.b{fill:#ffffff;}.c{fill:#645d5c;}.d{fill:#211715;}.e{fill:#7a7473;}</style></defs><path class="a" d="M53.719,169.651c-12.076-.025-24.13-.051-31.542-.175v2.09c-.01,12.43.23,32.17.54,40.12.75,19.21,1.6,47.21,2.12,62.51l.94.01c3.19.07,10.03.42,13.27.42,1.29,0,10.42-.21,13.31-.24l1.013-.011,1.007.011c2.87.03,12.01.24,13.31.24,3.24,0,10.09-.35,13.28-.42l1.31.01c.02-.48.04-.97.07-1.47.71-15.56,1.79-42.42,1.92-61.06.065-9.582,1.112-29.431.931-41.867C77.678,169.7,65.687,169.675,53.719,169.651Z"/><path class="b" d="M28.362,285.063a15.809,15.809,0,0,1-3.125-.537c-.09-1.44-.23-5.16-.4-10.33,2.512-.005,10.6.43,14.21.43,1.29,0,10.42-.21,13.31-.24l1.013-.011,1.007.011c2.87.03,12.01.24,13.31.24,3.817,0,12.644-.486,14.59-.41-.25,5.16-.44,8.87-.53,10.31a37.261,37.261,0,0,1-8.51.83h-.1a133.381,133.381,0,0,1-14.92-.56c-1.8-.19-3.42-.42-4.72-.69-1.23.26-2.74.47-4.41.65a127.53,127.53,0,0,1-14.9.6C31.988,285.318,29.977,285.221,28.362,285.063Z"/><path class="b" d="M33.522,169.587c-4.364-.025-8.258-.059-11.345-.111h-.83c.01.64.01,1.31.01,2,0,0,0,.111,0,.246-1.684-.118-3.5-.249-5.473-.356-2.46-.15-5.15-.3-8.02-.5-.99-.07-1.99-.15-3.02-.23a1.993,1.993,0,0,1-1.84-2.16c1.18-13.15,2.91-44.57,5.41-59.06.17-.96.34-1.85.51-2.66.91-4.2,2.01-8.46,4.33-12.09,4.59-7.18,13.06-10.71,21-13.81l1.455-.568.745.538a34.179,34.179,0,0,0,17.93,5.18c9.22,0,15.81-3.2,17.66-4.94a1.3,1.3,0,0,0,.222-.244c7.978,3.105,16.489,6.635,21.1,13.844,2.32,3.63,3.42,7.89,4.33,12.09.05.21.09.43.14.65,2.85,14.1,4.74,51.01,5.98,63.13-1.66.14-3.27.27-4.83.37h-.03c-2.87.2-5.56.35-8.01.49-1.952.128-3.771.222-5.33.405,0-.684,0-1.342.01-1.975C73.814,169.628,50.218,169.681,33.522,169.587Z"/><path class="b" d="M72.187,81.126a.713.713,0,0,1-.14-.06c-.09-.04-.21-.1-.37-.17-.88-.41-2.63-1.25-3.24-1.55-2.45-1.24-2.58-2.7-2.91-4.56a38.069,38.069,0,0,1-.64-5.269c6.5-2.617,11.754-11.4,12.661-13.862.135-.41.41-1.181.655-2.1.325-.052.511-.08.511-.08A6.433,6.433,0,0,0,81.7,52.131a9.677,9.677,0,0,0,2.5-3.287,15.238,15.238,0,0,0,1.554-8.076,5.1,5.1,0,0,0-.533-2.046A3.6,3.6,0,0,0,82.64,37a3.811,3.811,0,0,0-3.048.892s.148-20.442-25.408-20.442S28.48,37.9,28.48,37.9A3.807,3.807,0,0,0,25.433,37a3.6,3.6,0,0,0-2.586,1.719,5.087,5.087,0,0,0-.532,2.046,15.229,15.229,0,0,0,1.554,8.076,9.677,9.677,0,0,0,2.5,3.287,6.429,6.429,0,0,0,2.985,1.346l.974.149a25.892,25.892,0,0,0,4.938,9.639,22.137,22.137,0,0,0,7.5,6.027c-.164,1.322-.193,2.829-.553,4.884-.32,1.86-.22,3.52-2.81,4.46-.17.06-3.87,1.82-4.13,1.93,0,0,2.019,14.887,17.13,14.887S72.187,81.126,72.187,81.126Z"/><path class="c" d="M58.167,288.226a18.5,18.5,0,0,0,11.72,4.06,6.515,6.515,0,0,0,3.32-.75,3.148,3.148,0,0,0,1.26-1.46,2.256,2.256,0,0,0,.12-1.45c1.85.35,3.24,1.82,4.48,3.24q4.74,5.445,9.01,11.27a19.109,19.109,0,0,1,2.95,5.14,6.884,6.884,0,0,1-.45,5.74c-.09.13-.17.25-.26.37a7.94,7.94,0,0,1-2.82,2.17,13.411,13.411,0,0,1-12.38-.45c-5.19-3.01-7.8-9.19-12.75-12.58-1.9-1.3-4.27-2.34-5.07-4.5a8.039,8.039,0,0,1-.34-2.81c-.02-3.89.02-5.18,0-9.07A14.257,14.257,0,0,0,58.167,288.226Z"/><path class="c" d="M28.257,291.866c1.24-1.42,2.63-2.89,4.48-3.24a2.172,2.172,0,0,0,.1,1.4,3.152,3.152,0,0,0,1.28,1.51,6.528,6.528,0,0,0,3.33.75,18.524,18.524,0,0,0,11.69-4.04,14.935,14.935,0,0,0,1.23-1.1c-.02,3.89.02,5.18,0,9.07a8.039,8.039,0,0,1-.34,2.81c-.8,2.16-3.17,3.2-5.07,4.5-4.95,3.39-7.56,9.57-12.74,12.58a13.413,13.413,0,0,1-12.38.45,7.888,7.888,0,0,1-2.83-2.17c-.09-.12-.17-.24-.25-.37a6.848,6.848,0,0,1-.46-5.74,19.109,19.109,0,0,1,2.95-5.14Q23.507,297.316,28.257,291.866Z"/><path class="b" d="M34.187,285.356a127.53,127.53,0,0,0,14.9-.6l.02.14c.01,1.12.02,2.24.03,3.35a18.524,18.524,0,0,1-11.69,4.04,6.528,6.528,0,0,1-3.33-.75,3.152,3.152,0,0,1-1.28-1.51,19.788,19.788,0,0,0,1.35-4.54Z"/><path class="b" d="M58.187,285.066l.03-.27a133.381,133.381,0,0,0,14.92.56h.1l.02.68a20.352,20.352,0,0,0,1.18,4.03l.03.01a3.148,3.148,0,0,1-1.26,1.46,6.515,6.515,0,0,1-3.32.75,18.5,18.5,0,0,1-11.72-4.06C58.177,287.176,58.187,286.126,58.187,285.066Z"/><path class="b" d="M97.147,191.756c-.14-1.54-.26-1.95-.55-4.24-.56.57-2.4,3.31-2.83,3.85-.91,1.13-2.01.38-2.07-1.07-.27-5.6-1.21-10.98-.62-16.55l-.13-2.35c2.45-.14,5.14-.29,8.01-.49h.03l.16,2.29c.78,4.79,2.28,5.98,4.03,10.77a28.057,28.057,0,0,1,1.64,7.35,40.841,40.841,0,0,1-.34,6.76,9.685,9.685,0,0,1-2.17,4.48,3.091,3.091,0,0,1-4.04.42c-.39-.21-.59-1.29-.62-2.7C97.567,196.976,97.587,196.666,97.147,191.756Z"/><path class="b" d="M8.292,203.111c.089-.042.177-.087.265-.135.38-.21.58-1.29.62-2.7a83.5,83.5,0,0,1,.5-8.52c.13-1.54.26-1.95.55-4.24.56.57,2.39,3.31,2.83,3.85.9,1.13,2,.38,2.07-1.07.26-5.6,1.2-10.98.62-16.55l.053-2.385c-2.385-.145-4.986-.291-7.758-.483l-.3,1.838c-.75,5.2-2.29,6.31-4.1,11.25A28.464,28.464,0,0,0,2,191.316a39.808,39.808,0,0,0,.35,6.76,9.669,9.669,0,0,0,2.16,4.48A3.016,3.016,0,0,0,8.292,203.111Z"/><path class="b" d="M67.687,274.626c-1.3,0-10.44-.21-13.31-.24l26.59-.18C77.777,274.276,70.927,274.626,67.687,274.626Z"/><path class="b" d="M52.357,274.386c-2.89.03-12.02.24-13.31.24-3.24,0-10.08-.35-13.27-.42Z"/><path class="d" d="M32.258,284.954a20.1,20.1,0,0,1-.551,2.351q-.166.549-.365,1.086c-.143.39-.323.77-.454,1.163a2,2,0,1,0,3.857,1.064c.127-.381.3-.75.44-1.127s.265-.744.379-1.122a20.2,20.2,0,0,0,.551-2.351,2.16,2.16,0,0,0-.2-1.541,2,2,0,0,0-2.737-.718,1.96,1.96,0,0,0-.919,1.195Z"/><path class="d" d="M51.137,288.25l-.03-3.35a2.073,2.073,0,0,0-.586-1.414,2,2,0,0,0-2.829,0,2.064,2.064,0,0,0-.585,1.414l.03,3.35a2.072,2.072,0,0,0,.585,1.415,2,2,0,0,0,2.829,0,2.067,2.067,0,0,0,.586-1.415Z"/><path class="d" d="M50.551,289.66c.426-.351.834-.715,1.23-1.1l-3.414-1.414c-.012,2.439.008,4.878.005,7.318a13.7,13.7,0,0,1-.151,3.644,4.221,4.221,0,0,1-1.9,2.167,34.016,34.016,0,0,0-5.815,4.474c-1.622,1.7-3.025,3.581-4.552,5.359-3.221,3.75-7.349,6.607-12.547,5.546-2.227-.455-5.074-1.559-5.475-4.1-.414-2.628,1.34-5.054,2.79-7.061,1.983-2.743,4.074-5.409,6.234-8.015,1.012-1.22,2.03-2.441,3.091-3.62a6.4,6.4,0,0,1,3.22-2.3l-2.46-2.461a4.882,4.882,0,0,0,2.3,5.169c1.849,1.119,4.247,1.147,6.331.942a21.17,21.17,0,0,0,11.113-4.545,2.011,2.011,0,0,0,0-2.828,2.05,2.05,0,0,0-2.829,0,16.759,16.759,0,0,1-6.686,3.1,14.6,14.6,0,0,1-4.025.339c-.491-.029-2.509-.222-2.346-1.115a2.028,2.028,0,0,0-2.46-2.461c-3.164.736-5.2,3.525-7.18,5.877Q21.56,296.686,18.349,301c-1.99,2.671-4.023,5.423-4.4,8.832a8.084,8.084,0,0,0,4,7.964c5.473,3.35,12.609,2.417,17.482-1.516,4.31-3.48,6.813-8.711,11.569-11.7a15.746,15.746,0,0,0,3.582-2.715,7.419,7.419,0,0,0,1.779-4.839c.137-3.286-.006-6.6.01-9.887a2.023,2.023,0,0,0-3.415-1.414c-.395.385-.8.749-1.23,1.1C45.734,288.469,48.578,291.285,50.551,289.66Z"/><path class="d" d="M71.208,285.958a24.41,24.41,0,0,0,1.3,4.64,2.2,2.2,0,0,0,.919,1.195,2,2,0,0,0,2.737-.718,1.936,1.936,0,0,0,.2-1.541,24.442,24.442,0,0,1-1.3-4.64,2.017,2.017,0,0,0-.919-1.195,2.044,2.044,0,0,0-1.541-.2,2.022,2.022,0,0,0-1.2.92,2.228,2.228,0,0,0-.2,1.541Z"/><path class="d" d="M56.187,285.07c0,1.054-.01,2.107-.02,3.16a2.059,2.059,0,0,0,.585,1.415,2,2,0,0,0,2.829,0,2.1,2.1,0,0,0,.586-1.415c.01-1.053.019-2.106.02-3.16a2.064,2.064,0,0,0-.586-1.414,2,2,0,0,0-2.829,0,2.079,2.079,0,0,0-.585,1.414Z"/><path class="d" d="M59.581,286.812c-.42-.344-.821-.7-1.21-1.08a2.022,2.022,0,0,0-3.414,1.414c.013,2.866-.013,5.731,0,8.6a10.418,10.418,0,0,0,.747,4.608,8.7,8.7,0,0,0,2.992,3.179c1.021.726,2.145,1.3,3.143,2.063a22.135,22.135,0,0,1,3.146,3.074c1.825,2.082,3.448,4.344,5.429,6.287,4.445,4.357,10.946,6.248,16.881,3.859,3.131-1.26,5.668-3.488,6.077-7,.379-3.257-1.118-6.24-2.943-8.827-2.268-3.216-4.721-6.317-7.231-9.345C81,291,78.676,287.524,75.118,286.7a2.029,2.029,0,0,0-2.46,2.461c.176,1.034-2.223,1.117-2.771,1.128A15.284,15.284,0,0,1,66,289.867a16.658,16.658,0,0,1-6.417-3.055,2.064,2.064,0,0,0-2.829,0,2.014,2.014,0,0,0,0,2.828,21.125,21.125,0,0,0,10.771,4.525,11.484,11.484,0,0,0,6.316-.7,4.914,4.914,0,0,0,2.676-5.373l-2.46,2.461c2.454.57,4.194,3.39,5.715,5.2q2.826,3.372,5.472,6.89c1.611,2.151,3.751,4.564,4.145,7.321.373,2.608-1.225,4.239-3.533,5.132-4.923,1.9-9.78.027-13.255-3.628-3.355-3.528-5.9-7.6-10.1-10.247a10.9,10.9,0,0,1-2.923-2.184c-.814-1.038-.616-2.514-.62-3.748-.009-2.717.016-5.433,0-8.149l-3.415,1.414c.39.379.79.736,1.21,1.08C58.728,291.259,61.574,288.445,59.581,286.812Z"/><path class="d" d="M83.217,172.746c0,14.407-.8,28.8-.994,43.21-.207,15.53-.781,31.057-1.43,46.575-.307,7.332-.6,14.67-1.046,22l1.468-1.929a21.328,21.328,0,0,1-5.214.662c-2.437.126-4.88.139-7.319.1a80.963,80.963,0,0,1-14.654-1.184c-2.513-.5-3.589,3.351-1.063,3.858a86.913,86.913,0,0,0,15.717,1.326c2.511.038,5.026.023,7.533-.114a25.29,25.29,0,0,0,6.063-.792,2.072,2.072,0,0,0,1.469-1.929c.86-13.972,1.333-27.98,1.805-41.97.491-14.568.562-29.143,1.041-43.709.286-8.7.625-17.4.624-26.1,0-2.574-4-2.578-4,0Z"/><path class="d" d="M20.177,171.476c0,13.976.071,27.97.606,41.938.621,16.2,1.126,32.4,1.652,48.6.243,7.5.348,15.021.8,22.51a2.074,2.074,0,0,0,1.468,1.929,24.545,24.545,0,0,0,5.824.772c2.707.154,5.424.176,8.135.13a84.747,84.747,0,0,0,15.364-1.322c2.521-.514,1.454-4.37-1.063-3.858a78.8,78.8,0,0,1-14.3,1.18c-2.5.042-5,.024-7.49-.1a21.8,21.8,0,0,1-5.406-.663l1.469,1.929c-.4-6.621-.5-13.269-.717-19.9q-.385-11.823-.77-23.646c-.485-14.653-1.147-29.3-1.371-43.961q-.2-12.771-.2-25.544c0-2.574-4-2.578-4,0Z"/><path class="d" d="M51.667,193.356c0,12.271-.184,24.541-.2,36.812-.021,12.325-.068,24.65-.077,36.975q0,5.136.006,10.271c.005,1.685.01,3.37.039,5.054a5.924,5.924,0,0,0,.34,2.647c1.211,2.273,4.665.255,3.454-2.018.045.085.158,1.24.244.77a2.177,2.177,0,0,0-.017-.433c-.015-.443-.021-.886-.027-1.33-.023-1.563-.029-3.126-.033-4.69q-.014-4.557-.007-9.113,0-9.42.032-18.839c.027-11.206.012-22.413.1-33.619.057-7.495.151-14.991.153-22.487,0-2.574-4-2.578-4,0Z"/><path class="d" d="M62.887,69.846c.157,1.642.355,3.283.617,4.911a10.551,10.551,0,0,0,1.075,3.769,7.5,7.5,0,0,0,3.37,2.8,34.506,34.506,0,0,0,3.706,1.728,2.014,2.014,0,0,0,2.46-1.4,2.049,2.049,0,0,0-1.4-2.461c.756.259-.046-.034-.25-.13l-.783-.37q-.831-.4-1.659-.8c-.5-.242-.965-.52-1.446-.793-.12-.086-.093-.062.083.071-.059-.047-.116-.1-.172-.147-.107-.1-.2-.2-.3-.3-.046-.05-.091-.1-.134-.154q.243.324.117.144a3.4,3.4,0,0,0-.2-.323c-.034-.06-.079-.237-.138-.275.12.291.142.336.066.137l-.04-.116a7.42,7.42,0,0,1-.19-.721c-.123-.571-.216-1.152-.309-1.729-.062-.385-.118-.772-.172-1.158.049.352-.019-.153-.03-.238-.024-.186-.046-.373-.069-.559q-.113-.945-.2-1.893a2.045,2.045,0,0,0-2-2,2.022,2.022,0,0,0-2,2Z"/><path class="d" d="M40.7,69.976c-.078.83-.137,1.662-.233,2.491-.014.119-.028.238-.044.357.032-.225.03-.216,0,.028-.042.264-.084.528-.128.792-.052.316-.1.633-.145.95-.046.3-.095.6-.167.9-.027.107-.055.214-.089.319-.161.512.166-.268,0,.031-.071.129-.144.255-.219.382-.161.271.326-.339-.057.041-.059.058-.12.114-.182.167.238-.177.267-.2.089-.075-.169.1-.337.2-.507.292-.449.254.393-.15-.151.064-.184.072-.366.151-.547.232-.135.06-.268.122-.4.184q-.651.3-1.3.61c-.781.368-1.555.758-2.347,1.1a2.006,2.006,0,0,0-.717,2.736,2.061,2.061,0,0,0,2.736.718c1.326-.575,2.625-1.226,3.932-1.843.449-.212-.554.217-.2.083a8.46,8.46,0,0,0,1.278-.574,5.531,5.531,0,0,0,1.761-1.625,7.184,7.184,0,0,0,1.018-3.206c.26-1.716.458-3.424.619-5.152a2.008,2.008,0,0,0-2-2,2.053,2.053,0,0,0-2,2Z"/><path class="d" d="M22.177,171.476c17.088.283,34.183.144,51.273.234,4.059.022,8.118.049,12.177.116,2.575.043,2.575-3.957,0-4-17.089-.283-34.184-.144-51.274-.235-4.059-.021-8.118-.048-12.176-.115-2.575-.043-2.576,3.957,0,4Z"/><path class="d" d="M54.377,276.386c4.181.047,8.361.172,12.542.232,4.683.066,9.367-.3,14.048-.412,2.569-.06,2.579-4.06,0-4-4.681.109-9.365.479-14.048.412-4.181-.06-8.361-.185-12.542-.232-2.575-.029-2.577,3.971,0,4Z"/><path class="d" d="M52.357,272.386c-4.183.046-8.364.172-12.546.232-4.679.067-9.358-.3-14.034-.412-2.575-.06-2.574,3.94,0,4,4.676.109,9.355.479,14.034.412,4.182-.061,8.363-.186,12.546-.232,2.572-.029,2.579-4.029,0-4Z"/><path class="d" d="M17.837,109.676c.006,7.488.363,14.98.626,22.462.26,7.4.275,14.808.524,22.21.193,5.739.37,11.475.37,17.218,0,2.574,4,2.578,4,0,0-9.978-.5-19.948-.6-29.926-.066-6.767-.445-13.536-.659-20.3-.123-3.886-.255-7.775-.258-11.664,0-2.574-4-2.578-4,0Z"/><path class="d" d="M85.137,109.676c-.007,7.439-.361,14.883-.622,22.316-.256,7.318-.273,14.636-.518,21.954-.2,5.873-.378,11.743-.38,17.62,0,2.574,4,2.578,4,0,0-10,.5-19.985.6-29.98.072-6.749.446-13.5.659-20.246.123-3.886.255-7.775.259-11.664,0-2.574-4-2.578-4,0Z"/><path class="d" d="M89.077,173.746a50.447,50.447,0,0,0,.022,8.734c.112,1.494.252,2.986.373,4.479a25.046,25.046,0,0,0,.381,4.414c.764,2.826,3.937,3.256,5.641,1,.854-1.13,1.63-2.483,2.517-3.445L94.6,187.516c.423,3.287.832,6.459.97,9.856a32.167,32.167,0,0,0,.294,5.073c.418,2.067,2.336,3.1,4.368,3.08,4.324-.052,6.115-5.328,6.433-8.889a30.31,30.31,0,0,0-.868-11.088c-1.3-4.612-4.09-8.573-4.789-13.364a2.013,2.013,0,0,0-2.46-1.4,2.053,2.053,0,0,0-1.4,2.461c.505,3.46,2.018,6.323,3.4,9.479a24.884,24.884,0,0,1,2.3,10.109c-.034,2.826.08,5.572-1.655,7.928-.29.395-.559.784-1.087.768-.148,0-.355-.151-.5-.134-.471.06.216.014.154.306a5.416,5.416,0,0,0-.1-.971c-.069-1.225-.053-2.455-.11-3.68-.148-3.2-.548-6.363-.956-9.537-.2-1.571-2.115-2.824-3.415-1.414a29.67,29.67,0,0,0-2.288,3.066,3.834,3.834,0,0,0-.575.812c-.067.094-.135.187-.2.28l1.566.033c.281-.23-.154-2.658-.189-3.1-.358-4.482-.856-8.954-.414-13.45a2.014,2.014,0,0,0-2-2,2.043,2.043,0,0,0-2,2Z"/><path class="d" d="M13.747,173.746c.434,4.5-.066,8.968-.419,13.45-.044.555-.085,1.109-.121,1.665-.015.229-.205,1.269-.075,1.433q.663-.2,1.339-.342c.178.232.188.242.03.028a3.539,3.539,0,0,0-.5-.7,31.127,31.127,0,0,0-2.363-3.179c-1.306-1.419-3.211-.16-3.414,1.414-.377,2.919-.745,5.823-.923,8.765-.065,1.075-.089,2.152-.111,3.23-.006.242-.188,2.174-.163,2.185.165.078.264-.479.346-.352,0,0-.456.142-.5.148a.973.973,0,0,1-.619-.041c-1.193-.549-1.8-2.929-2.019-4.071a31.127,31.127,0,0,1-.253-3.662A25.228,25.228,0,0,1,5.96,183.469c1.39-3.45,3.136-6.481,3.7-10.221a2.065,2.065,0,0,0-1.4-2.461,2.015,2.015,0,0,0-2.46,1.4,19.714,19.714,0,0,1-1.514,5.381c-.836,1.806-1.719,3.58-2.427,5.443A29.18,29.18,0,0,0,.05,195.133c.192,3.5,1,8.291,4.572,9.95,1.732.8,4.762.517,5.835-1.28.934-1.564.715-3.688.761-5.445a104.874,104.874,0,0,1,1.009-10.842L8.812,188.93c.786.854,1.707,2.424,2.6,3.551a3.075,3.075,0,0,0,5.557-1.108,23.25,23.25,0,0,0,.361-4.177c.118-1.494.257-2.987.371-4.481a51.964,51.964,0,0,0,.048-8.969,2.056,2.056,0,0,0-2-2,2.013,2.013,0,0,0-2,2Z"/><path class="d" d="M71.835,82.785c7,2.734,14.931,5.828,19.383,12.257,3.851,5.56,4.872,12.867,5.754,19.449,1.718,12.814,2.532,25.852,3.475,38.776.421,5.757.786,11.525,1.37,17.269l2-2c-5.308.446-10.628.687-15.94,1.06-2.554.179-2.574,4.181,0,4,5.312-.373,10.632-.614,15.94-1.06.991-.083,2.116-.852,2-2-1.224-12.039-1.813-24.145-2.823-36.2-.551-6.583-1.143-13.169-2.006-19.719-.9-6.84-1.919-14.184-5.446-20.222C90.7,86.1,81.426,82.257,72.9,78.927a2.015,2.015,0,0,0-2.46,1.4,2.048,2.048,0,0,0,1.4,2.461Z"/><path class="d" d="M33.725,78.927c-8.084,3.16-16.65,6.7-21.774,14.1-2.738,3.952-4.027,8.758-4.995,13.407-.7,3.379-1.158,6.811-1.577,10.235-1.836,15.008-2.689,30.128-3.835,45.2q-.186,2.429-.385,4.856c-.168,2-.283,4.015,1.647,5.255a7.8,7.8,0,0,0,3.781.8c1.438.11,2.876.205,4.316.294,2.884.18,5.77.334,8.654.531,2.569.176,2.558-3.825,0-4-2.36-.162-4.721-.292-7.082-.434a69.206,69.206,0,0,1-7.189-.492c-.083-.014-.275.023-.336-.057.018.022.1.13.05.02a2.064,2.064,0,0,1,.054-.686q.079-.906.153-1.813.171-2.065.326-4.131c.527-6.923,1.007-13.849,1.544-20.771C7.638,134,8.235,126.76,9.042,119.547c.324-2.894.679-5.787,1.146-8.662a49.289,49.289,0,0,1,3.269-12.379c3.926-8.66,13-12.464,21.331-15.721a2.06,2.06,0,0,0,1.4-2.461,2.014,2.014,0,0,0-2.46-1.4Z"/><path class="d" d="M35.447,82.553a28.53,28.53,0,0,0,7.206,3.435A36.271,36.271,0,0,0,55.084,88,37.8,37.8,0,0,0,66.967,85.96a17.652,17.652,0,0,0,6.664-3.65c1.822-1.822-1-4.652-2.829-2.828-.157.157-.317.3-.488.446.361-.3-.043.027-.132.084-.405.262-.81.518-1.234.75A21.346,21.346,0,0,1,65.6,82.208a34.5,34.5,0,0,1-10.982,1.8c-5.789.03-12.357-1.5-17.154-4.906a2.016,2.016,0,0,0-2.736.718,2.042,2.042,0,0,0,.717,2.736Z"/><path class="e" d="M82.445,25.335a27.081,27.081,0,0,0-3.656-9.965,26.641,26.641,0,0,0-3.7-4.676c-.563-.569-1.418-1.4-2-1.907a33.289,33.289,0,0,0-4.865-3.226,28.69,28.69,0,0,0-4.248-1.9A30.245,30.245,0,0,0,53.907,2.005,28.756,28.756,0,0,0,36.845,7.256,27.417,27.417,0,0,0,25.01,28.886a47.687,47.687,0,0,0,.615,7.939l.018.157a3.748,3.748,0,0,1,2.791.906,9.093,9.093,0,0,0,1.119.009,3.659,3.659,0,0,0,3.177-2.405c3.45-7.166,9.047-12.813,18.34-15.138a3.681,3.681,0,0,1,2.657.061c1.087.647.715,2.089,1.628,2.884.964.84,2.71.5,4.029.052a47.692,47.692,0,0,0,5.84-2.443l.411.126a11.432,11.432,0,0,1,4.178,3.254,24.276,24.276,0,0,1,5.229,11.293,3.269,3.269,0,0,0,1.249,2.461,3.14,3.14,0,0,0,3.348-.154,3.77,3.77,0,0,1,2.651-.921l.024-.144a37.375,37.375,0,0,0,.493-7.937A30.554,30.554,0,0,0,82.445,25.335Z"/><path class="d" d="M84.242,37.354c1.272-7.837.54-16.122-3.726-22.993A30.777,30.777,0,0,0,62.5,1.107C48.978-2.532,33.947,2.965,26.867,15.224c-3.937,6.818-4.4,14.51-3.171,22.133a2.015,2.015,0,0,0,2.46,1.4,2.049,2.049,0,0,0,1.4-2.461c-.937-5.812-.764-11.833,1.811-17.231A26.679,26.679,0,0,1,39.076,8.155C50.572.818,66.8,3.432,75.388,14.007c5.05,6.221,6.252,14.549,5,22.284a2.062,2.062,0,0,0,1.4,2.46,2.015,2.015,0,0,0,2.46-1.4Z"/><path class="d" d="M65.878,18.306a44.342,44.342,0,0,1-5.287,2.483,21.666,21.666,0,0,1-2.609.889,4.588,4.588,0,0,1-.924.134c-.158.006-.453-.1-.363-.011-.365-.356-.416-1.37-.7-1.845a3.739,3.739,0,0,0-2.07-1.623c-1.708-.541-3.658.113-5.3.633A28.709,28.709,0,0,0,33.776,29.755,31.727,31.727,0,0,0,31.3,33.88c-.395.783-1.218,2.514-2.238,1.974-2.274-1.2-4.3,2.247-2.019,3.453a5.248,5.248,0,0,0,4.651.068A7.126,7.126,0,0,0,34.83,35.75a27.355,27.355,0,0,1,5.31-7.327,23.516,23.516,0,0,1,7.751-4.965c.776-.3,1.565-.57,2.364-.807.456-.135,1.981-.8,2.463-.509-.175-.107.4,1.434.459,1.539a3.831,3.831,0,0,0,1.949,1.773c2,.823,4.192.07,6.1-.644A51.959,51.959,0,0,0,67.9,21.76c2.26-1.235.243-4.69-2.019-3.454Z"/><path class="d" d="M65.1,22.962a7.759,7.759,0,0,1,2.049,1.447A14.775,14.775,0,0,1,69.1,26.626a22.969,22.969,0,0,1,3.2,6.17c.676,2.064.634,4.549,2.119,6.247,1.587,1.813,4.3,1.638,6.233.572,2.255-1.242.239-4.7-2.019-3.454a1.749,1.749,0,0,1-.96.288c.314.028-.239-.073-.287-.09.216.077-.012,0-.122-.069s-.058-.027.182.14c-.114-.127-.129-.134-.043-.021.027.217-.094-.148-.144-.237a4.068,4.068,0,0,1-.285-1.122,24.279,24.279,0,0,0-2.089-6.483c-1.735-3.694-4.663-8.074-8.715-9.462A2,2,0,1,0,65.1,22.962Z"/><path class="d" d="M81.007,39.309a1.755,1.755,0,0,1,2.429.322,4.05,4.05,0,0,1,.372,2.024,12.515,12.515,0,0,1-.171,2.565c-.555,3.044-2.065,6.72-5.454,7.328a2.017,2.017,0,0,0-1.4,2.46,2.044,2.044,0,0,0,2.46,1.4c5.481-.983,8.1-7.153,8.514-12.122.218-2.614-.046-5.521-2.3-7.2a5.839,5.839,0,0,0-7.283.4,2.015,2.015,0,0,0,0,2.828,2.044,2.044,0,0,0,2.829,0Z"/><path class="d" d="M76.675,50.641a14.08,14.08,0,0,1-.826,3.8c-.064.2-.479,1.232-.176.577-.125.269-.245.539-.378.8a32.738,32.738,0,0,1-2.816,4.525c-2.382,3.268-5.765,6.824-9.8,7.769-2.505.588-1.445,4.446,1.063,3.857,5.1-1.2,9.049-5.357,12.049-9.419,2.584-3.5,4.7-7.465,4.88-11.909.1-2.574-3.9-2.569-4,0Z"/><path class="d" d="M29.9,36.481a5.842,5.842,0,0,0-7.284-.4c-2.255,1.673-2.515,4.593-2.3,7.2.413,4.968,3.034,11.139,8.515,12.122a2.055,2.055,0,0,0,2.46-1.4,2.017,2.017,0,0,0-1.4-2.46c-3.389-.608-4.9-4.284-5.454-7.328a12.3,12.3,0,0,1-.173-2.417,4.779,4.779,0,0,1,.311-2.071,1.737,1.737,0,0,1,2.492-.423,2.055,2.055,0,0,0,2.829,0,2.017,2.017,0,0,0,0-2.828Z"/><path class="d" d="M27.583,50.5a29.907,29.907,0,0,0,6.388,14.314,21.441,21.441,0,0,0,14.006,7.93,2.014,2.014,0,0,0,2-2,2.045,2.045,0,0,0-2-2c-4.64-.5-8.546-3.522-11.41-7.038A26.358,26.358,0,0,1,31.44,49.439a2.017,2.017,0,0,0-2.46-1.4,2.046,2.046,0,0,0-1.4,2.46Z"/><path class="d" d="M49.166,59.081a10.979,10.979,0,0,0,5.284,1.237,8.756,8.756,0,0,0,5.474-1.675,2,2,0,0,0,.586-1.415,2.036,2.036,0,0,0-.586-1.414,2.012,2.012,0,0,0-1.414-.586,2.346,2.346,0,0,0-1.414.586c.7-.544.045-.057-.171.056-.17.089-.594.224.06-.008-.14.05-.277.107-.419.152-.387.125-.784.169-1.174.268.186-.047.4-.047.08-.016-.115.012-.23.021-.346.029-.278.018-.556.025-.835.023q-.373,0-.747-.027c-.114-.008-.228-.017-.342-.028l-.2-.022q-.238-.028.222.03c-.327-.135-.752-.141-1.1-.244-.154-.046-.3-.1-.455-.153-.424-.146.451.213.065.031-.188-.088-.373-.181-.557-.278a2,2,0,0,0-2.019,3.454Z"/><path class="d" d="M53.1,47.061a23.236,23.236,0,0,1,.543,2.486l-.072-.532a1.515,1.515,0,0,1,.01.343l.071-.532a.816.816,0,0,1-.038.155l.2-.478a.634.634,0,0,1-.054.1l.312-.4a.472.472,0,0,1-.081.08l.405-.312a1.609,1.609,0,0,1-.2.1l.478-.2a1.421,1.421,0,0,1-.332.1l.532-.071a1.357,1.357,0,0,1-.312,0l.532.071c-.117-.016-.233-.044-.35-.06a1.506,1.506,0,0,0-.8-.036,1.486,1.486,0,0,0-.743.237,2,2,0,0,0-.718,2.737l.313.4a2,2,0,0,0,.882.515c.332.045.654.127.992.142a3.291,3.291,0,0,0,1.543-.379A2.39,2.39,0,0,0,57.5,49.969a3.576,3.576,0,0,0-.012-1.591c-.135-.8-.32-1.595-.526-2.38a2.065,2.065,0,0,0-.919-1.2,2,2,0,0,0-2.737.717,2.1,2.1,0,0,0-.2,1.541Z"/><path class="d" d="M40.662,39.83c-.415,1.348-.145,4.451,2.41,4.715,3.378-.02,3.557-3.771,2.42-5.535C44.562,37.566,41.825,36.965,40.662,39.83Z"/><path class="d" d="M67.707,39.83c.415,1.349.145,4.451-2.41,4.715-3.378-.02-3.558-3.771-2.421-5.535C63.807,37.566,66.544,36.965,67.707,39.83Z"/></svg>' },
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
  // 解析SVG viewBox，获取原始宽高
  let parser = new DOMParser();
  let doc = parser.parseFromString(svgData.svgCode, 'image/svg+xml');
  let svgEl = doc.querySelector('svg');
  let vb = svgEl?.getAttribute('viewBox');
  let vbArr = vb ? vb.split(/\s|,/) : [0,0,100,100];
  let vbW = parseFloat(vbArr[2] || 100);
  let vbH = parseFloat(vbArr[3] || 100);
  // 画布尺寸
  const canvasW = canvas.width;
  const canvasH = canvas.height;
  // 设定初始缩放，最大边100px，保持比例
  let scale = 1;
  if (vbW > vbH) {
    scale = 100 / vbW;
  } else {
    scale = 100 / vbH;
  }
  const width = vbW * scale;
  const height = vbH * scale;
  // 居中，x/y为左上角
  const left = (canvasW - width) / 2;
  const top = (canvasH - height) / 2;
  const element = {
    id: Date.now(),
    type: 'svg',
    svgCode: svgData.svgCode,
    name: svgData.name,
    x: left,
    y: top,
    width,
    height,
    originalWidth: vbW,  // 保存SVG原始宽度
    originalHeight: vbH, // 保存SVG原始高度
    aspectRatio: vbW / vbH, // 保存宽高比
    color: currentColor.value,
    rotation: 0,
    opacity: 1,
    zIndex: collageElements.value.length
  }
  collageElements.value.push(element)
  selectedElement.value = element
  hasDrawing.value = true

  // 在拼贴模式下保存状态到撤回栈
  saveCollageState()

  redrawCollageElements()
}

// 图片处理相关的状态
const isImageUploaded = ref(false)
const hasDrawing = ref(false)
const hasSavedImage = ref(false)  // 追踪是否已保存过图片
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

  // 初始化光标样式
  updateCursor()
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
  isDragReady.value = false
  isScaling.value = false
  isRotating.value = false

  // 如果正在拖拽拼贴元素，结束拖拽并进行最终重绘
  if (dragType !== null) {
    dragType = null
    dragStart = null
    // 拖拽结束时进行最终重绘，确保画面准确
    if (currentMode.value === 'collage') {
      redrawCollageElements()
      // 拖拽完成后保存状态
      saveCollageState()
    }
  }
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
  // 更新光标样式
  updateCursor()
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
  // 保存当前绘画内容（在切换到拼贴模式之前）
  if (mode === 'collage' && currentMode.value === 'draw') {
    backupDrawingContent()
  }

  currentMode.value = mode
  showDynamicToolbar.value = true
  selectedElement.value = null

  // 如果有拼贴元素，需要重绘以清除选择边框
  if (collageElements.value.length > 0) {
    // 临时切换到拼贴模式进行重绘，然后再切回目标模式
    const targetMode = mode
    currentMode.value = 'collage'
    redrawCollageElements()
    currentMode.value = targetMode
  }

  if (mode === 'collage') {
    redrawCollageElements()
    // 在拼贴模式下设置默认光标
    if (canvasRef.value) {
      canvasRef.value.style.cursor = 'default'
    }
  }
  if (mode === 'draw') {
    currentTool.value = 'pen'
    changeColor(currentColor.value)
    // 切换到绘画模式时恢复工具光标
    updateCursor()

    // 如果从拼贴模式切换回绘画模式，需要恢复绘画内容并添加拼贴元素到撤回栈
    if (collageElements.value.length > 0) {
      restoreDrawingWithCollageElements()
    }
  }
}

// 更新光标样式
const updateCursor = () => {
  if (!canvasRef.value) return

  if (currentMode.value === 'draw') {
    // 在绘画模式下，根据当前工具设置光标
    if (currentTool.value === 'pen') {
      canvasRef.value.style.cursor = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1024 1024' width='32' height='32'><path d='M314.88 626.133333l96.213333 94.933334a130.346667 130.346667 0 0 1-108.16 54.826666 104.32 104.32 0 0 1-73.386666-27.52 102.4 102.4 0 0 0 42.666666-26.88 110.933333 110.933333 0 0 0 25.386667-64v-2.346666a59.52 59.52 0 0 1 7.893333-26.88 31.146667 31.146667 0 0 1 10.026667-2.56m14.08-64c-64 0-85.333333 27.733333-95.146667 85.333333v2.773333c-2.986667 18.773333-5.12 25.386667-8.533333 29.013334a39.68 39.68 0 0 1-8.746667 7.04 33.493333 33.493333 0 0 1-18.133333 5.12 29.866667 29.866667 0 0 1-8.746667-1.066667h-1.92a29.013333 29.013333 0 0 0-10.24-1.92A27.946667 27.946667 0 0 0 149.333333 717.013333c8.96 81.28 78.72 122.88 153.386667 122.88A189.226667 189.226667 0 0 0 481.28 725.333333a27.946667 27.946667 0 0 0-6.4-30.293333l-126.293333-125.653333a28.16 28.16 0 0 0-19.626667-8.106667l0.64 0.426667zM808.32 234.666667H810.666667c0 10.453333-9.386667 49.066667-97.493334 158.72-15.36 18.986667-31.146667 37.76-47.146666 56.106666-31.146667 35.84-147.626667 157.44-147.626667 157.44l-80.853333-81.493333s117.12-114.346667 154.24-147.413333c19.84-17.493333 40.32-34.56 60.586666-50.986667 100.053333-80.426667 140.8-92.373333 155.946667-92.373333m0-64c-47.146667 0-111.786667 38.826667-196.053333 106.666666-21.333333 17.066667-42.666667 34.773333-62.72 52.906667-38.677333 34.133333-76.373333 69.269333-113.066667 105.386667-14.72 14.72-29.653333 29.653333-44.16 44.586666l-3.413333 3.626667a60.8 60.8 0 0 0 0 85.333333l85.333333 86.4c11.306667 11.306667 26.666667 17.706667 42.666667 17.706667a60.586667 60.586667 0 0 0 42.666666-17.706667l3.2-3.2 9.813334-9.813333 34.773333-35.413333c35.84-37.12 71.893333-76.16 105.386667-114.773334 16.64-18.986667 32.853333-38.4 48.64-58.026666 102.186667-126.08 142.72-208 89.173333-249.813334a66.56 66.56 0 0 0-42.666667-13.866666h0.426667z' fill='%233D424D'/></svg>") 8 24, crosshair`
    } else if (currentTool.value === 'eraser') {
      canvasRef.value.style.cursor = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1029 1024' width='32' height='32'><path d='M968.96 387.2l-302.4-302.4c-17.76-17.76-41.28-27.36-65.76-27.36s-48 9.6-65.28 26.88l-476.16 476.16c-17.76 17.76-27.36 41.28-27.36 65.76s9.6 48 26.88 65.28l0.96 1.92h0.96l205.44 205.44c43.2 43.2 100.8 67.2 161.76 67.2 60.96 0 118.56-23.52 161.76-67.2l379.68-379.68c17.76-17.76 27.36-41.28 27.36-66.24-0.48-24.48-10.08-48-27.84-65.76z m-432.96 469.92c-29.76 26.88-68.16 41.76-108.48 41.76-43.2 0-83.52-16.8-114.24-47.04l-206.88-206.88c-10.08-10.08-10.08-26.88 0-36.96l90.24-90.24 339.36 339.36z m385.44-385.44l-337.92 337.92-339.36-339.36 337.92-337.92c4.8-4.8 11.52-7.68 18.24-7.68 7.2 0 13.44 2.88 18.24 7.68l302.4 302.4c10.56 10.08 10.56 26.88 0.48 36.96z' fill='%233D424D'/></svg>") 2 26, crosshair`
    }
  } else if (currentMode.value === 'collage') {
    // 在拼贴模式下设置默认光标
    canvasRef.value.style.cursor = 'default'
  }
}

// 辅助函数：计算点相对于旋转元素的本地坐标
const getLocalCoordinates = (x, y, element) => {
  if (!element.rotation || element.rotation === 0) {
    return { x, y };
  }

  // 元素中心点
  const centerX = element.x + element.width / 2;
  const centerY = element.y + element.height / 2;

  // 将点转换为相对于中心的坐标
  const relativeX = x - centerX;
  const relativeY = y - centerY;

  // 应用反向旋转（因为我们要将旋转后的坐标转换回原始坐标）
  const angle = -element.rotation * Math.PI / 180;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);

  // 旋转变换
  const rotatedX = relativeX * cos - relativeY * sin;
  const rotatedY = relativeX * sin + relativeY * cos;

  // 转换回绝对坐标
  return {
    x: rotatedX + centerX,
    y: rotatedY + centerY
  };
}

// 处理拼接模式的点击
const handleCollageClick = (e) => {
  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  // 检查是否点击了控制点或边框
  if (selectedElement.value) {
    const el = selectedElement.value;

    // 控制点定义
    const points = [
      { x: el.x - 4, y: el.y - 4, type: 'nw' },
      { x: el.x + el.width / 2 - 4, y: el.y - 4, type: 'n' },
      { x: el.x + el.width - 4, y: el.y - 4, type: 'ne' },
      { x: el.x - 4, y: el.y + el.height / 2 - 4, type: 'w' },
      { x: el.x + el.width - 4, y: el.y + el.height / 2 - 4, type: 'e' },
      { x: el.x - 4, y: el.y + el.height - 4, type: 'sw' },
      { x: el.x + el.width / 2 - 4, y: el.y + el.height - 4, type: 's' },
      { x: el.x + el.width - 4, y: el.y + el.height - 4, type: 'se' }
    ];

    // 检查旋转控制点（使用本地坐标系统）
    const localCoords = getLocalCoordinates(x, y, el);
    const rotatePoint = {
      x: el.x + el.width / 2 - 5,
      y: el.y - 20 - 5,
      width: 10,
      height: 10
    };

    if (localCoords.x >= rotatePoint.x && localCoords.x <= rotatePoint.x + rotatePoint.width &&
        localCoords.y >= rotatePoint.y && localCoords.y <= rotatePoint.y + rotatePoint.height) {
      isRotating.value = true;
      isDragReady.value = true;
      dragType = 'rotate';
      dragStart = {
        mouseX: x,
        mouseY: y,
        x: el.x,
        y: el.y,
        width: el.width,
        height: el.height,
        rotation: el.rotation
      };
      return;
    }

    // 检查控制点（使用本地坐标系统）
    for (const point of points) {
      if (localCoords.x >= point.x && localCoords.x <= point.x + 8 &&
          localCoords.y >= point.y && localCoords.y <= point.y + 8) {
        isDragReady.value = true;
        dragType = point.type;
        dragStart = {
          mouseX: x,
          mouseY: y,
          x: el.x,
          y: el.y,
          width: el.width,
          height: el.height,
          originalWidth: el.originalWidth,
          originalHeight: el.originalHeight,
          aspectRatio: el.aspectRatio,
          rotation: el.rotation
        };
        return;
      }
    }

    // 检查是否点击在元素边框附近
    const borderThreshold = 5;
    if (x >= el.x - borderThreshold && x <= el.x + el.width + borderThreshold &&
        y >= el.y - borderThreshold && y <= el.y + el.height + borderThreshold) {
      // 检查具体在哪个边
      if (Math.abs(x - el.x) <= borderThreshold) {
        dragType = 'w'; // 左边
      } else if (Math.abs(x - (el.x + el.width)) <= borderThreshold) {
        dragType = 'e'; // 右边
      } else if (Math.abs(y - el.y) <= borderThreshold) {
        dragType = 'n'; // 上边
      } else if (Math.abs(y - (el.y + el.height)) <= borderThreshold) {
        dragType = 's'; // 下边
      } else if (x > el.x && x < el.x + el.width && y > el.y && y < el.y + el.height) {
        dragType = 'move'; // 移动
        isDragReady.value = true;
        dragStartX = x - el.x;
        dragStartY = y - el.y;
      }
      if (dragType) {
        isDragReady.value = true;
        // 重要：确保dragStart正确记录初始状态
        // 分别设置鼠标位置和元素初始状态，避免属性冲突
        dragStart = {
          mouseX: x,
          mouseY: y,
          x: el.x,
          y: el.y,
          width: el.width,
          height: el.height,
          originalWidth: el.originalWidth,
          originalHeight: el.originalHeight,
          aspectRatio: el.aspectRatio
        };
      }
      return;
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
    // 记录拖拽起始位置
    isDragReady.value = true;
    dragStartX = x - foundElement.x
    dragStartY = y - foundElement.y
    dragType = 'move'
    dragStart = {
      mouseX: x,
      mouseY: y,
      x: foundElement.x,
      y: foundElement.y,
      width: foundElement.width,
      height: foundElement.height
    }
  } else {
    selectedElement.value = null
    dragType = null
    dragStart = null
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

// 节流版本的重绘函数，用于拖拽过程中
const redrawCollageElementsThrottled = () => {
  const now = Date.now()
  if (now - lastRedrawTime >= redrawThrottle) {
    lastRedrawTime = now
    redrawCollageElements()
  }
}

// 重绘拼接元素
const redrawCollageElements = () => {
  if (currentMode.value !== 'collage' || !ctx) return

  // 首先恢复绘画内容作为背景
  if (drawingCanvasBackup.value) {
    const img = new Image()
    img.onload = () => {
      // 清空画布
      ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
      // 绘制备份的绘画内容
      ctx.drawImage(img, 0, 0)
      // 然后绘制拼贴元素
      drawCollageElementsOnTop()
    }
    img.src = drawingCanvasBackup.value
  } else {
    // 如果没有绘画内容备份，直接清空画布并填充白色背景
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    // 绘制拼贴元素
    drawCollageElementsOnTop()
  }
}

// 在现有画布上绘制拼贴元素
const drawCollageElementsOnTop = () => {
  // 按z-index排序绘制元素
  const sortedElements = [...collageElements.value].sort((a, b) => a.zIndex - b.zIndex)

  // 同步绘制所有元素
  const drawPromises = sortedElements.map(element => {
    return new Promise((resolve) => {
      ctx.save()
      ctx.globalAlpha = element.opacity

      if (element.type === 'svg') {
        // 同步绘制SVG
        drawSvgElement(element).then(() => {
          ctx.restore()
          resolve()
        })
      } else {
        // 其他类型元素的绘制逻辑
        ctx.translate(element.x + element.width / 2, element.y + element.height / 2)
        ctx.rotate(element.rotation * Math.PI / 180)

        if (element.type === 'image') {
          drawImage(element)
        }

        ctx.restore()
        resolve()
      }
    })
  })

  // 等待所有元素绘制完成后绘制选中状态
  Promise.all(drawPromises).then(() => {
    sortedElements.forEach(element => {
      // 绘制选中状态的边框和控制点
      if (selectedElement.value && selectedElement.value.id === element.id) {
        drawSelectionBorder(element)

        // 绘制旋转控制点（现代化设计）
        ctx.save()

        // 如果元素有旋转，应用相同的旋转变换
        if (element.rotation && element.rotation !== 0) {
          const centerX = element.x + element.width / 2;
          const centerY = element.y + element.height / 2;

          // 移动到元素中心点
          ctx.translate(centerX, centerY);
          // 应用旋转
          ctx.rotate(element.rotation * Math.PI / 180);
          // 移回原点（相对于旋转后的坐标系）
          ctx.translate(-centerX, -centerY);
        }

        const rotateX = element.x + element.width / 2;
        const rotateY = element.y - 20;

        // 绘制连接线（从元素顶部到旋转控制点）
        ctx.save();
        ctx.strokeStyle = 'rgba(100, 100, 100, 0.4)';
        ctx.lineWidth = 1;
        ctx.setLineDash([2, 2]);
        ctx.beginPath();
        ctx.moveTo(element.x + element.width / 2, element.y);
        ctx.lineTo(rotateX, rotateY);
        ctx.stroke();
        ctx.restore();

        // 绘制旋转控制点（简洁样式，无阴影）
        ctx.save();

        // 外圈（灰色边框）
        ctx.strokeStyle = '#666666';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(rotateX, rotateY, 8, 0, 2 * Math.PI);
        ctx.stroke();

        // 内圈（白色填充）
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(rotateX, rotateY, 7, 0, 2 * Math.PI);
        ctx.fill();

        // 旋转图标（简化版：小箭头）
        ctx.strokeStyle = '#666666';
        ctx.lineWidth = 1;
        ctx.beginPath();
        // 绘制简化的旋转箭头
        const arrowSize = 3;
        ctx.moveTo(rotateX - arrowSize, rotateY - arrowSize);
        ctx.lineTo(rotateX + arrowSize, rotateY - arrowSize);
        ctx.lineTo(rotateX, rotateY + arrowSize);
        ctx.closePath();
        ctx.stroke();

        ctx.restore()
      }
    })
  })
}

// 备份当前绘画内容
const backupDrawingContent = () => {
  if (canvasRef.value) {
    drawingCanvasBackup.value = canvasRef.value.toDataURL()
  }
}

// 为拼贴模式保存状态到撤回栈
const saveCollageState = () => {
  if (currentMode.value === 'collage' && canvasRef.value) {
    // 在拼贴模式下，我们需要保存包含绘画背景和拼贴元素的完整画布状态
    setTimeout(() => {
      // 使用setTimeout确保redrawCollageElements已经完成
      const currentState = canvasRef.value.toDataURL();
      undoStack.value.push(currentState);
      // 清空取消撤回栈
      redoStack.value = [];
      hasDrawing.value = true;
    }, 10);
  }
}

// 恢复绘画内容并添加拼贴元素到撤回栈
const restoreDrawingWithCollageElements = () => {
  if (!canvasRef.value || !drawingCanvasBackup.value) return

  // 创建图片对象来恢复绘画内容
  const img = new Image()
  img.onload = () => {
    // 清空画布
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    // 绘制备份的绘画内容
    ctx.drawImage(img, 0, 0)

    // 绘制所有拼贴元素到画布上（不是拼贴模式，所以不显示选中状态）
    const sortedElements = [...collageElements.value].sort((a, b) => a.zIndex - b.zIndex)

    const drawPromises = sortedElements.map(element => {
      return new Promise((resolve) => {
        ctx.save()
        ctx.globalAlpha = element.opacity

        if (element.type === 'svg') {
          drawSvgElement(element).then(() => {
            ctx.restore()
            resolve()
          })
        } else {
          ctx.translate(element.x + element.width / 2, element.y + element.height / 2)
          ctx.rotate(element.rotation * Math.PI / 180)

          if (element.type === 'image') {
            drawImage(element)
          }

          ctx.restore()
          resolve()
        }
      })
    })

    // 等待所有元素绘制完成后保存到撤回栈
    Promise.all(drawPromises).then(() => {
      // 将合并后的画布状态保存到撤回栈
      saveCanvasState()
      // 清空拼贴元素数组，因为它们已经被"烘焙"到画布上
      collageElements.value = []
    })
  }
  img.src = drawingCanvasBackup.value
}

// 绘制SVG元素
const drawSvgElement = (element) => {
  return new Promise((resolve) => {
    // 直接解析SVG并绘制，不使用异步图片加载
    let parser = new DOMParser();
    let doc = parser.parseFromString(element.svgCode, 'image/svg+xml');
    let svgEl = doc.querySelector('svg');

    if (svgEl) {
      // 设置SVG以非比例模式拉伸填满容器
      svgEl.setAttribute('width', element.width);
      svgEl.setAttribute('height', element.height);

      // 关键：设置preserveAspectRatio为none，让SVG内容自由拉伸
      svgEl.setAttribute('preserveAspectRatio', 'none');

      // 如果没有viewBox，从原始尺寸创建一个
      if (!svgEl.getAttribute('viewBox')) {
        const originalWidth = element.originalWidth || 100;
        const originalHeight = element.originalHeight || 100;
        svgEl.setAttribute('viewBox', `0 0 ${originalWidth} ${originalHeight}`);
      }

      // 创建新的SVG字符串
      const serializer = new XMLSerializer();
      const svgString = serializer.serializeToString(svgEl);

      // 创建图片并绘制
      const img = new Image();
      img.onload = () => {
        ctx.save()
        ctx.translate(element.x + element.width / 2, element.y + element.height / 2)
        ctx.rotate(element.rotation * Math.PI / 180)
        // 直接绘制SVG，填满整个容器
        ctx.drawImage(img, -element.width / 2, -element.height / 2, element.width, element.height);
        ctx.restore()
        resolve()
      };
      img.onerror = () => {
        // 如果SVG加载失败，绘制占位符
        ctx.save()
        ctx.translate(element.x + element.width / 2, element.y + element.height / 2)
        ctx.rotate(element.rotation * Math.PI / 180)
        ctx.fillStyle = '#f0f0f0'
        ctx.fillRect(-element.width / 2, -element.height / 2, element.width, element.height)
        ctx.strokeStyle = '#ccc'
        ctx.strokeRect(-element.width / 2, -element.height / 2, element.width, element.height)
        ctx.fillStyle = '#666'
        ctx.font = '12px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('SVG', 0, 0)
        ctx.restore()
        resolve()
      }
      img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgString)}`;
    } else {
      resolve()
    }
  })
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

  // 如果元素有旋转，应用旋转变换
  if (element.rotation && element.rotation !== 0) {
    const centerX = element.x + element.width / 2;
    const centerY = element.y + element.height / 2;

    // 移动到元素中心点
    ctx.translate(centerX, centerY);
    // 应用旋转
    ctx.rotate(element.rotation * Math.PI / 180);
    // 移回原点（相对于旋转后的坐标系）
    ctx.translate(-centerX, -centerY);
  }

  // 绘制主边框（简洁样式）
  ctx.strokeStyle = '#666666';
  ctx.lineWidth = 1;
  ctx.setLineDash([6, 3]);
  ctx.lineDashOffset = 0;
  ctx.strokeRect(element.x, element.y, element.width, element.height);

  // 8个缩放点坐标（四角+四边中点）
  const points = [
    // 四角
    { x: element.x - 4, y: element.y - 4 }, // 左上
    { x: element.x + element.width, y: element.y - 4 }, // 右上
    { x: element.x - 4, y: element.y + element.height }, // 左下
    { x: element.x + element.width, y: element.y + element.height }, // 右下
    // 四边中点
    { x: element.x + element.width / 2 - 2, y: element.y - 4 }, // 上中
    { x: element.x + element.width / 2 - 2, y: element.y + element.height }, // 下中
    { x: element.x - 4, y: element.y + element.height / 2 - 2 }, // 左中
    { x: element.x + element.width, y: element.y + element.height / 2 - 2 }, // 右中
  ];

  // 绘制缩放点（简洁样式：小方块）
  points.forEach(pt => {
    ctx.save();

    // 绘制白色背景（无阴影）
    ctx.fillStyle = '#ffffff';
    ctx.strokeStyle = '#666666';
    ctx.lineWidth = 1;

    const rectWidth = 6;
    const rectHeight = 6;

    ctx.fillRect(pt.x, pt.y, rectWidth, rectHeight);
    ctx.strokeRect(pt.x, pt.y, rectWidth, rectHeight);
    ctx.restore();
  });

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
      hasSavedImage.value = true  // 标记已保存过图片
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

// 前往分析方法
const goToAnalysis = () => {
  if (!hasSavedImage.value) {
    ElMessage.warning('请先保存图片后再进行分析')
    return
  }
  // 可以在这里添加跳转到分析页面的逻辑
  // 例如：router.push('/analysis')
  // 或者调用现有的分析功能
  analyzeDrawing()
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
  border-radius: 16px 0 0 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 999;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow-y: auto;
  animation: slide-in 0.28s cubic-bezier(.4, 1.4, .6, 1);
}

.selection-sidebar::-webkit-scrollbar {

  width: 4px;
  background: transparent;
}

.selection-sidebar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 4px;
}

.selection-sidebar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

.selection-sidebar::-webkit-scrollbar-track {
  background: transparent;
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
