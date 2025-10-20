<template>
  <div class="records-page">
    <NavBarUser />

    <main class="records-main">
      <section class="page-header">
        <div class="header-text">
          <p class="subtitle">心理绘画档案馆</p>
          <h1 class="title">我的绘画记录</h1>
          <p class="description">记录每一次情绪表达，随时回顾你的心灵旅程。</p>
          <div class="header-actions">
            <router-link to="/draw" class="primary-button">继续创作</router-link>
            <button type="button" class="secondary-button" @click="fetchDrawingRecords">刷新列表</button>
          </div>
          <div class="stats-panel">
            <div class="stat-card">
              <span class="stat-label">已保存作品</span>
              <span class="stat-value">{{ recordCount }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">最近更新</span>
              <span class="stat-value">{{ lastUpdatedText }}</span>
            </div>
          </div>
        </div>
        <div class="header-visual" aria-hidden="true">
          <div class="visual-glow"></div>
          <img src="@/assets/images/others/HTP.png" alt="心灵绘画" />
        </div>
      </section>

      <section class="records-section">
        <div v-if="isLoading" class="state-card loading-state">
          <div class="spinner"></div>
          <p>正在整理您的作品故事...</p>
        </div>

        <div v-else-if="error" class="state-card error-state">
          <h2>加载失败</h2>
          <p>{{ error }}</p>
          <button type="button" class="primary-button ghost" @click="fetchDrawingRecords">重试</button>
        </div>

        <div v-else-if="!hasRecords" class="state-card empty-state">
          <h2>暂无绘画记录</h2>
          <p>首次创作将自动保存在这里，为自己留下一份心灵档案。</p>
          <router-link to="/draw" class="primary-button">开始首次创作</router-link>
        </div>

        <div v-else class="records-grid">
          <div
            v-for="(record, index) in drawingRecords"
            :key="record.fileName"
            class="record-card"
            :class="{ 'record-card--latest': index === 0 }"
          >
            <div class="image-wrapper" @click="viewImage(record.url)">
              <img :src="record.url" :alt="record.fileName" class="drawing-image" />
              <div class="image-overlay">
                <span>{{ index === 0 ? '最新作品 · 点击查看' : '点击查看大图' }}</span>
              </div>
            </div>
            <div class="card-body">
              <div class="card-caption">
                <span class="caption-title">{{ index === 0 ? '最新心灵手稿' : '心理绘画手稿' }}</span>
                <span class="caption-note">守护自我表达的每一刻</span>
              </div>
              <a :href="record.url" :download="record.fileName" class="ghost-button">下载作品</a>
            </div>
          </div>
        </div>
      </section>
    </main>

    <transition name="fade">
      <div v-if="isViewerOpen" class="image-viewer-modal" @click="closeViewer">
        <div class="viewer-content" @click.stop>
          <button type="button" class="viewer-close" @click="closeViewer" aria-label="关闭预览">×</button>
          <img :src="viewerImageUrl" class="viewer-image" alt="绘画大图预览" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useUserStore } from '@/stores/user';
import config from '@/config';
import NavBarUser from '@/components/NavBarUser.vue';

// --- 状态管理 ---
const drawingRecords = ref([]);
const isLoading = ref(true);
const error = ref(null);
const isViewerOpen = ref(false);
const viewerImageUrl = ref('');
const userStore = useUserStore();
const lastUpdated = ref(null);

// --- API 调用 ---
const fetchDrawingRecords = async () => {
  // Final safeguard: Do not proceed if id is null or undefined.
  if (!userStore.id) {
    error.value = '用户 ID 无效，无法加载绘画记录。';
    isLoading.value = false;
    return;
  }

  isLoading.value = true;
  error.value = null;
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('认证失败，请重新登录。');
    }

    const response = await fetch(`${config.baseURL}/api/drawings/${userStore.id}`, {
      headers: {
        'Authorization': `${token}`
      }
    });

    if (!response.ok) {
      if (response.status === 404) {
        drawingRecords.value = []; // 用户没有记录，是正常情况
      } else {
        throw new Error(`服务器错误: ${response.statusText}`);
      }
    } else {
      const fileNames = await response.json();
      const sortedNames = [...fileNames].sort((a, b) =>
        b.localeCompare(a, 'zh-CN', { numeric: true, sensitivity: 'base' })
      );
      drawingRecords.value = sortedNames.map(fileName => ({
        fileName,
        url: `${config.baseURL}/uploads/saved_drawings/${userStore.id}/${fileName}`
      }));
    }
    lastUpdated.value = new Date();
  } catch (e) {
    error.value = e.message || '获取绘画记录时发生未知错误。';
    console.error(e);
  } finally {
    isLoading.value = false;
  }
};

const recordCount = computed(() => drawingRecords.value.length);
const hasRecords = computed(() => recordCount.value > 0);
const lastUpdatedText = computed(() => {
  if (!lastUpdated.value) {
    return '尚未更新';
  }
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(lastUpdated.value);
});

// --- 事件处理 ---
const viewImage = (url) => {
  viewerImageUrl.value = url;
  isViewerOpen.value = true;
};

const closeViewer = () => {
  isViewerOpen.value = false;
  viewerImageUrl.value = '';
};

// --- 生命周期钩子 ---
watch(() => userStore.id, (newId) => {
  if (newId) {
    fetchDrawingRecords();
  } else {
    // Handle case where user logs out while on the page
    isLoading.value = false;
    error.value = '用户未登录，无法加载绘画记录。';
    drawingRecords.value = [];
  }
}, { immediate: true });
</script>

<style scoped>
.records-page {
  min-height: 100vh;
  background-color: #ffffff;
}

.records-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 96px 32px 64px;
}

.page-header {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 48px;
  background-color: #ffffff;
  border-radius: 28px;
  padding: 48px 56px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 24px 48px rgba(211, 142, 160, 0.08);
}

.page-header::after {
  content: '';
  position: absolute;
  inset: 1.5px;
  border-radius: 26px;
  border: 1px solid rgba(247, 222, 228, 0.7);
  pointer-events: none;
}

.page-header:hover {
  transform: translateY(-6px);
  box-shadow: 0 32px 64px rgba(211, 142, 160, 0.14);
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 20px;
  color: #1a1a1a;
}

.subtitle {
  font-size: 0.95rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(26, 26, 26, 0.6);
  margin: 0;
}

.title {
  font-size: 3rem;
  line-height: 1.1;
  margin: 0;
  font-weight: 700;
  color: #1f3f38;
}

.description {
  font-size: 1.15rem;
  line-height: 1.6;
  color: rgba(41, 53, 52, 0.75);
  max-width: 520px;
  margin: 0;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.85rem 2.4rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #42b983, #34a06e);
  color: #ffffff;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(66, 185, 131, 0.28);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.primary-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 32px rgba(66, 185, 131, 0.35);
}

.primary-button.ghost {
  background: rgba(255, 255, 255, 0.9);
  color: #34a06e;
  box-shadow: none;
  border: 1px solid rgba(52, 160, 110, 0.2);
}

.primary-button.ghost:hover {
  background: rgba(52, 160, 110, 0.08);
  box-shadow: none;
}

.secondary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.85rem 2.2rem;
  border-radius: 999px;
  background: transparent;
  border: 1px solid rgba(52, 160, 110, 0.35);
  color: #2f6f5b;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.secondary-button:hover {
  background: rgba(52, 160, 110, 0.1);
  color: #1f4f41;
}

.stats-panel {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.stat-card {
  min-width: 160px;
  padding: 16px 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 206, 215, 0.4);
  box-shadow: 0 12px 24px rgba(211, 142, 160, 0.12);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(108, 82, 88, 0.6);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #6c5258;
}

.header-visual {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-visual img {
  max-width: 240px;
  filter: drop-shadow(0 18px 32px rgba(211, 142, 160, 0.2));
  transform: translateY(0);
  transition: transform 0.4s ease;
}

.header-visual:hover img {
  transform: translateY(-6px);
}

.visual-glow {
  position: absolute;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(circle at center, rgba(255, 196, 206, 0.55), rgba(255, 196, 206, 0));
  filter: blur(12px);
  z-index: -1;
}

.records-section {
  margin-top: 56px;
}

.state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 16px;
  padding: 72px 24px;
  border-radius: 24px;
  background: #ffffff;
  box-shadow: 0 16px 40px rgba(31, 82, 63, 0.08);
  color: rgba(26, 26, 26, 0.68);
}

.state-card h2 {
  margin: 0;
  font-size: 1.6rem;
  color: #114c40;
}

.state-card p {
  max-width: 420px;
  margin: 0;
  line-height: 1.6;
}

.spinner {
  border: 4px solid rgba(66, 185, 131, 0.2);
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border-top-color: #42b983;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 28px;
}

.record-card {
  background: #ffffff;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 18px 36px rgba(31, 82, 63, 0.12);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  display: flex;
  flex-direction: column;
}

.record-card--latest {
  border: 1.5px solid rgba(66, 185, 131, 0.4);
  box-shadow: 0 24px 44px rgba(31, 82, 63, 0.2);
}

.record-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 24px 42px rgba(31, 82, 63, 0.16);
}

.image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 72%;
  overflow: hidden;
  cursor: pointer;
}

.drawing-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.35s ease;
}

.image-wrapper:hover .drawing-image {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(17, 76, 64, 0) 40%, rgba(17, 76, 64, 0.65) 100%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 20px;
  color: #ffffff;
  font-weight: 600;
  font-size: 0.95rem;
  opacity: 0;
  transition: opacity 0.25s ease;
  letter-spacing: 0.05em;
}

.image-wrapper:hover .image-overlay {
  opacity: 1;
}

.card-body {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.card-caption {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.caption-title {
  font-size: 1rem;
  font-weight: 600;
  color: #214d40;
}

.caption-note {
  font-size: 0.82rem;
  color: rgba(33, 77, 64, 0.68);
  letter-spacing: 0.04em;
}

.ghost-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 1.2rem;
  border-radius: 999px;
  border: 1px solid rgba(52, 160, 110, 0.4);
  color: #2f6f5b;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.85rem;
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.ghost-button:hover {
  background: rgba(52, 160, 110, 0.12);
  border-color: rgba(52, 160, 110, 0.6);
  color: #1f4f41;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.image-viewer-modal {
  position: fixed;
  inset: 0;
  backdrop-filter: blur(12px);
  background: rgba(15, 30, 24, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 32px;
}

.viewer-content {
  position: relative;
  max-width: min(900px, 90vw);
  max-height: 90vh;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 28px 48px rgba(0, 0, 0, 0.35);
  background: #0d1c18;
}

.viewer-image {
  display: block;
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
}

.viewer-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.viewer-close:hover {
  background: rgba(0, 0, 0, 0.7);
  transform: scale(1.05);
}

@media (max-width: 1024px) {
  .records-main {
    padding: 88px 24px 56px;
  }

  .page-header {
    padding: 40px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 36px 28px;
  }

  .title {
    font-size: 2.4rem;
  }

  .description {
    font-size: 1.05rem;
  }

  .records-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }

  .card-body {
    flex-direction: column;
    align-items: flex-start;
  }

  .ghost-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 560px) {
  .records-main {
    padding: 80px 20px 48px;
  }

  .page-header {
    gap: 32px;
  }

  .header-actions {
    flex-direction: column;
  }

  .stat-card {
    width: 100%;
  }

  .records-grid {
    gap: 20px;
  }
}
</style>
