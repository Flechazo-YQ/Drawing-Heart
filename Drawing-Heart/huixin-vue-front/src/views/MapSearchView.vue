<template>
  <div class="map-search-container" ref="mapContainerRef" :class="{ 'is-fullscreen': isFullscreen }">
    <NavBarUser v-if="!isFullscreen" />

    <!-- 地图区域 -->
    <div class="map-section" ref="mapSectionRef">
      <!-- 新增一个包装器，用于应用视觉样式 -->
      <div class="map-wrapper" :class="{'is-sticky': isSticky}">
        <div id="amap-container" class="map-container"></div>
        <div v-if="loading" class="map-loading">
          <div class="loading-spinner"></div>
          <div>正在定位和搜索...</div>
        </div>
        <div v-if="error" class="map-error">{{ error }}</div>
        <button @click="toggleFullScreen" class="fullscreen-btn">
          {{ isFullscreen ? '退出全屏' : '全屏浏览' }}
        </button>
      </div>
    </div>

    <!-- 新增：内容区域包装器，用于Flex布局 -->
    <div class="content-wrapper">
      <!-- 搜索框区域 -->
      <div class="search-section" v-if="!isFullscreen">
        <input
          type="text"
          v-model="searchAddress"
          placeholder="定位失败？请在此输入您的地址"
          class="address-input"
          @input="getSuggestions"
          @focus="isSuggestionsVisible = true"
          @blur="hideSuggestions"
          @keyup.enter="handleAddressSearch"
          autocomplete="off"
        />
        <ul v-if="isSuggestionsVisible && suggestions.length > 0" class="suggestions-list">
          <li
            v-for="(suggestion, index) in suggestions"
            :key="index"
            @mousedown="selectSuggestion(suggestion)"
            class="suggestion-item"
          >
            {{ suggestion }}
          </li>
        </ul>
        <button @click="handleAddressSearch" class="search-button">搜索</button>
      </div>

      <!-- 店铺列表区域 -->
      <div class="shops-section" v-if="!isFullscreen">
        <div class="shops-header">
          <h3>附近心理咨询机构</h3>
          <span class="shops-count">{{ results.length }}家机构</span>
        </div>

        <div v-if="results.length > 0" class="shops-grid">
          <div v-for="item in results" :key="item.id" class="shop-card" @click="centerMap(item)">
            <div class="shop-image">
              <img
                :src="getShopImage(item)"
                :alt="item.name"
                @error="handleImageError"
                loading="lazy"
              />
              <div class="distance-badge">{{ formatDistance(item.distance) }}</div>
            </div>
            <div class="shop-info">
              <h4 class="shop-name">{{ item.name }}</h4>
              <p class="shop-address">{{ item.address }}</p>
              <div class="shop-meta">
                <span class="rating" v-if="item.rating">
                  ⭐ {{ item.rating }}
                </span>
                <span class="price" v-if="item.avgPrice">
                  ¥{{ item.avgPrice }}/次
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!loading && results.length === 0 && !error" class="empty-state">
          <div class="empty-icon">🏥</div>
          <div class="empty-text">附近暂无心理咨询机构</div>
          <div class="empty-hint">尝试扩大搜索范围或输入更详细的地址</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import NavBarUser from '@/components/NavBarUser.vue'

const loading = ref(false)
const error = ref('')
const results = ref([])
const searchAddress = ref('')
const suggestions = ref([])
const isSuggestionsVisible = ref(false)
const isFullscreen = ref(false)
const mapContainerRef = ref(null) // 用于获取根元素的引用
const mapSectionRef = ref(null) // 用于直接获取地图区域元素的引用
const isSticky = ref(false) // 新增：追踪地图是否已吸顶
let debounceTimer = null
let map = null
let userLocationMarker = null // 新增：用于存储用户位置标记
let markers = []

// 页面加载时自动开始搜索
onMounted(async () => {
  await initMap()
  await getLocation()

  // 添加全屏事件监听
  document.addEventListener('fullscreenchange', handleFullscreenChange)

  // 添加滚动监听 - 确保在DOM更新后添加
  nextTick(() => {
    // 立即执行一次，处理初始状态
    handleScroll()

    // 添加事件监听
    window.addEventListener('scroll', handleScroll)
    console.log('已添加滚动监听器')
  })
})

onUnmounted(() => {
  // 移除全屏事件监听
  document.removeEventListener('fullscreenchange', handleFullscreenChange)

  // 移除滚动监听
  window.removeEventListener('scroll', handleScroll)
})

// 处理滚动事件，检测地图是否处于吸顶状态
const handleScroll = () => {
  if (!mapSectionRef.value) return

  // 使用 ref 直接获取元素，更可靠
  const mapRect = mapSectionRef.value.getBoundingClientRect()
  const newStickyState = mapRect.top <= 64  // 64px是导航栏高度

  // 只有在状态变化时才更新和打印日志，减少不必要的重渲染
  if (isSticky.value !== newStickyState) {
    isSticky.value = newStickyState
    console.log('粘性状态变化 - mapRect.top:', mapRect.top, 'isSticky:', isSticky.value)
  }
}

// 初始化高德地图
const initMap = async () => {
  return new Promise((resolve) => {
    // 动态加载高德地图API
    if (!window.AMap) {
      const script = document.createElement('script')
      script.src = 'https://webapi.amap.com/maps?v=1.4.15&key=1253afe42c5a16a5c4764fc2086f3f62'
      script.onload = () => {
        createMap()
        resolve()
      }
      document.head.appendChild(script)
    } else {
      createMap()
      resolve()
    }
  })
}

// 创建地图实例
const createMap = () => {
  map = new AMap.Map('amap-container', {
    zoom: 15,
    center: [120.03385, 30.293636], // 默认浙江科技大学
    mapStyle: 'amap://styles/normal'
  })
}

// 自动开始定位和搜索
const getLocation = async () => {
  loading.value = true
  error.value = ''
  results.value = []
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude
        const lng = pos.coords.longitude
        await searchNearby(lat, lng)
      },
      async () => {
        // 浏览器定位失败，尝试IP定位
        error.value = '浏览器定位失败，正在尝试IP定位...'
        await getIpLocation()
      }
    )
  } else {
    error.value = '浏览器不支持定位，正在尝试IP定位...'
    await getIpLocation()
  }
}

// IP定位作为备用方案
const getIpLocation = async () => {
  try {
    const res = await fetch('/api/map/location_by_ip')
    const data = await res.json()
    if (data.code === 0) {
      error.value = 'IP定位成功，结果可能存在误差' // 提示用户
      const { latitude, longitude } = data.data
      await searchNearby(latitude, longitude)
    } else {
      error.value = '所有定位方式均失败，无法获取位置'
      loading.value = false
    }
  } catch (e) {
    error.value = 'IP定位服务请求失败'
    loading.value = false
  }
}

// 新增：处理手动地址搜索
const handleAddressSearch = async () => {
  if (!searchAddress.value.trim()) {
    error.value = '请输入地址'
    return
  }
  loading.value = true
  error.value = ''
  results.value = []

  try {
    const res = await fetch('/api/map/geocode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address: searchAddress.value })
    })
    const data = await res.json()

    if (data.code === 0) {
      const { latitude, longitude } = data.data
      // 手动搜索时，半径设置为10km
      await searchNearby(latitude, longitude, 10000)
    } else {
      error.value = data.message || '地址解析失败'
      loading.value = false
    }
  } catch (e) {
    error.value = '地址搜索服务请求失败'
    loading.value = false
  }
}

// 新增：获取输入建议
const getSuggestions = () => {
  clearTimeout(debounceTimer)
  if (!searchAddress.value.trim()) {
    suggestions.value = []
    return
  }
  // 防抖处理
  debounceTimer = setTimeout(async () => {
    try {
      const res = await fetch('/api/map/autocomplete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keywords: searchAddress.value })
      })
      const data = await res.json()
      if (data.code === 0 && data.data.length > 0) {
        suggestions.value = data.data
        isSuggestionsVisible.value = true
      } else {
        suggestions.value = []
      }
    } catch (e) {
      suggestions.value = []
    }
  }, 300) // 300ms的延迟
}

// 新增：选择一个建议
const selectSuggestion = (suggestion) => {
  searchAddress.value = suggestion
  isSuggestionsVisible.value = false
  // 使用nextTick确保DOM更新后再执行搜索
  nextTick(() => {
    handleAddressSearch()
  })
}

// 新增：延迟隐藏建议列表，以便点击事件可以触发
const hideSuggestions = () => {
  setTimeout(() => {
    isSuggestionsVisible.value = false
  }, 200) // 延迟200ms
}

const searchNearby = async (latitude, longitude, radius = null) => {
  try {
    // 更新地图中心点
    if (map) {
      map.setCenter([longitude, latitude])

      // 更新用户位置蓝标：先移除旧的
      if (userLocationMarker) {
        userLocationMarker.setMap(null)
      }

      // 添加新的当前位置标记，并保存起来
      userLocationMarker = new AMap.Marker({
        position: [longitude, latitude],
        icon: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
        title: '我的位置'
      })
      userLocationMarker.setMap(map)
    }

    const payload = { latitude, longitude }
    if (radius) {
      payload.radius = radius
    }

    const res = await fetch('/api/map/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()

    if (data.code === 0) {
      results.value = data.data.sort((a, b) => a.distance - b.distance)
      addMarkers(data.data)
      if (data.data.length === 0) {
        error.value = '该位置附近未找到相关机构'
      }
    } else {
      error.value = '未找到相关机构'
    }
  } catch (e) {
    error.value = '搜索失败'
  }
  loading.value = false
}

// 在地图上添加红旗标记
const addMarkers = (places) => {
  // 清除之前的标记
  markers.forEach(marker => marker.setMap(null))
  markers = []

  places.forEach((place, index) => {
    const marker = new AMap.Marker({
      position: [place.longitude, place.latitude],
      icon: new AMap.Icon({
        size: new AMap.Size(25, 34),
        image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png',
        imageOffset: new AMap.Pixel(0, 0),
        imageSize: new AMap.Size(25, 34)
      }),
      title: place.name,
      label: {
        content: (index + 1).toString(),
        offset: new AMap.Pixel(0, -10)
      }
    })

    marker.setMap(map)
    markers.push(marker)

    // 点击标记显示信息窗口
    marker.on('click', () => {
      const infoWindow = new AMap.InfoWindow({
        content: `
          <div style="padding: 8px;">
            <h4>${place.name}</h4>
            <p>${place.address}</p>
            <p>距离: ${place.distance}米</p>
          </div>
        `
      })
      infoWindow.open(map, marker.getPosition())
    })
  })
}

// 点击店铺卡片时居中地图
const centerMap = (item) => {
  if (map && item.longitude && item.latitude) {
    map.setCenter([item.longitude, item.latitude])
    map.setZoom(17)
  }
}

// 获取店铺图片，带有回退机制
const getShopImage = (item) => {
  // 优先使用API返回的图片
  if (item.image && item.image !== '/default-clinic.jpg') {
    return item.image
  }

  // 如果有多张照片，使用第一张
  if (item.photos && item.photos.length > 0) {
    return item.photos[0]
  }

  // 使用占位图片服务
  return `https://picsum.photos/400/300?random=${item.id || Math.random()}`
}

// 图片加载失败时的处理
const handleImageError = (event) => {
  event.target.src = '/images/default-clinic.jpg'
}

// 新增：格式化距离显示
const formatDistance = (distance) => {
  if (distance < 1000) {
    return `${distance}m`
  }
  return `${(distance / 1000).toFixed(1)}km`
}

// 切换全屏模式
const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    // 进入全屏
    mapContainerRef.value?.requestFullscreen()
  } else {
    // 退出全屏
    if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }
}

// 监听全屏状态变化（例如用户按 ESC 键）
const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
  // 状态变化后，需要重置地图尺寸以适应新的容器大小
  if (map) {
    nextTick(() => {
      map.resize()
    })
  }
}
</script>

<style scoped>
.map-search-container {
  min-height: 100vh;
  background: #f8fafc;
  /* 移除 flex 布局 */
  padding-bottom: 60px;
}

/* 新增：内容包装器样式 */
.content-wrapper {
  display: flex;
  flex-direction: column;
}

/* 地图区域 - 仅负责定位 */
.map-section {
  height: 40vh;
  position: sticky;
  top: 64px; /* 导航栏高度 */
  z-index: 10;
  margin-top: 64px;
}

/* 新增：地图内容的包装器，负责视觉样式 */
.map-wrapper {
  width: 100%;
  height: 100%;
  background: #f8fafc;
  transition: transform 0.3s ease, border-radius 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden; /* 确保内容不溢出，特别是圆角 */
  border-radius: 0; /* 默认无圆角 */
}

/* 吸顶时的动画效果，应用在包装器上 */
.map-wrapper.is-sticky {
  transform: translateY(-5px); /* 轻微上浮效果 */
  border-radius: 0 0 20px 20px; /* 底部圆角 */
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); /* 明显的阴影 */
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.9);
  padding: 1rem 2rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.map-error {
  position: absolute;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: #fee2e2;
  color: #dc2626;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

/* 搜索框样式 */
.search-section {
  position: relative; /* 新增此行 */
  padding: 1rem 1.5rem;
  background: #ffffff;
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.address-input {
  flex-grow: 1;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.address-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.search-button {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-button:hover {
  background: #2563eb;
}

.suggestions-list {
  position: absolute;
  top: calc(1rem + 46px); /* 计算位置：padding-top + input的高度 */
  left: 1.5rem; /* 与父元素的padding-left对齐 */
  /* 通过计算宽度，使其与输入框大致对齐 */
  width: calc(100% - 3rem - 100px); /* 100% - 左右padding - 按钮宽度 - gap */
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  list-style: none;
  padding: 0;
  margin: 0;
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.suggestion-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  text-align: left;
}

.suggestion-item:hover {
  background-color: #f9fafb;
}

/* 店铺列表区域 - 60%高度 */
.shops-section {
  flex: 1;
  background: #ffffff;
  padding: 1.5rem;
  overflow-y: auto;
}

.shops-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.shops-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.shops-count {
  color: #6b7280;
  font-size: 0.875rem;
}

/* 美团风格的网格布局 */
.shops-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.shop-card {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  cursor: pointer;
  border: 1px solid #f3f4f6;
}

.shop-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.shop-image {
  position: relative;
  height: 120px;
  overflow: hidden;
}

.shop-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.distance-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  min-width: 50px; /* 给距离标签一个最小宽度，防止km/m切换时跳动 */
  text-align: center;
}

.shop-info {
  padding: 1rem;
}

.shop-name {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  line-clamp: 1;
  overflow: hidden;
}

.shop-address {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  color: #6b7280;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  overflow: hidden;
  line-height: 1.4;
}

.shop-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.rating {
  color: #f59e0b;
  font-weight: 500;
}

.price {
  color: #ef4444;
  font-weight: 600;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.empty-hint {
  font-size: 0.875rem;
}

/* 全屏按钮样式 */
.fullscreen-btn {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  z-index: 1000;
  padding: 0.5rem 1rem;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* 全屏模式下的样式调整 */
.map-search-container.is-fullscreen .map-section {
  height: 100vh; /* 地图高度占满全屏 */
  margin-top: 0; /* 移除导航栏的间距 */
}

.map-search-container.is-fullscreen .fullscreen-btn {
  /* 在全屏模式下也可以微调按钮位置 */
  bottom: 2rem;
  right: 2rem;
}

/* 响应式布局 */
@media (max-width: 1024px) {
  .shops-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .map-section {
    height: 35vh;
  }

  .shops-grid {
    grid-template-columns: 1fr;
  }

  .shops-section {
    padding: 1rem;
  }

  .shop-image {
    height: 100px;
  }

  .search-section {
    padding: 1rem;
    flex-direction: column;
  }
}
</style>
