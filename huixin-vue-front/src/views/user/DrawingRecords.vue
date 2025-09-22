<template>
  <div class="drawing-records-container">
    <h1 class="title">我的绘画记录</h1>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载您的作品...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>加载失败：{{ error }}</p>
      <button @click="fetchDrawingRecords" class="retry-button">重试</button>
    </div>

    <div v-else-if="drawingRecords.length === 0" class="empty-state">
      <p>您还没有任何绘画记录，快去创作吧！</p>
    </div>

    <div v-else class="records-grid">
      <div v-for="record in drawingRecords" :key="record.fileName" class="record-card">
        <img :src="record.url" :alt="record.fileName" class="drawing-image" @click="viewImage(record.url)" />
        <div class="card-footer">
          <span class="file-name">{{ record.fileName }}</span>
          <a :href="record.url" :download="record.fileName" class="download-button">下载</a>
        </div>
      </div>
    </div>

    <!-- Modal for viewing image -->
    <div v-if="isViewerOpen" class="image-viewer-modal" @click="closeViewer">
      <img :src="viewerImageUrl" class="viewer-image" @click.stop />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import config from '@/config';

// --- 状态管理 ---
const drawingRecords = ref([]);
const isLoading = ref(true);
const error = ref(null);
const isViewerOpen = ref(false);
const viewerImageUrl = ref('');
const userStore = useUserStore();

// --- API 调用 ---
const fetchDrawingRecords = async () => {
  // The check for userStore.id is now implicitly handled by the watcher
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
      drawingRecords.value = fileNames.map(fileName => ({
        fileName,
        url: `${config.baseURL}/uploads/saved_drawings/${userStore.id}/${fileName}`
      }));
    }
  } catch (e) {
    error.value = e.message || '获取绘画记录时发生未知错误。';
    console.error(e);
  } finally {
    isLoading.value = false;
  }
};

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
.drawing-records-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #333;
}

/* 加载、错误和空状态 */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: #666;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #09f;
  animation: spin 1s ease infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-button {
  padding: 0.5rem 1rem;
  border: 1px solid #09f;
  background-color: #fff;
  color: #09f;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.retry-button:hover {
  background-color: #09f;
  color: #fff;
}

/* 记录网格 */
.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.record-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.record-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.drawing-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  cursor: pointer;
  background-color: #f0f0f0;
}

.card-footer {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eee;
}

.file-name {
  font-size: 0.9rem;
  color: #555;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 1rem;
}

.download-button {
  font-size: 0.8rem;
  padding: 0.4rem 0.8rem;
  background-color: #eef;
  color: #337ab7;
  border-radius: 20px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.download-button:hover {
  background-color: #d9edf7;
}

/* 图片查看器 Modal */
.image-viewer-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  cursor: pointer;
}

.viewer-image {
  max-width: 90%;
  max-height: 90%;
  border-radius: 4px;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
  cursor: default;
}
</style>
