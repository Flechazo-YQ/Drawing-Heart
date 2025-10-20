<template>
  <div class="map-search-container" ref="mapContainerRef" :class="{ 'is-fullscreen': isFullscreen }">
    <NavBarUser v-if="!isFullscreen" />

    <section class="map-hero" :class="{ 'is-fullscreen': isFullscreen }">
      <div class="hero-content">
        <div class="hero-copy">
          <p class="hero-tag">心理陪伴导航</p>
          <h1 class="hero-title">找到离你最近的心理咨询支持</h1>
          <p class="hero-subtitle">
            我们通过定位和关键词检索，为你筛选附近值得信赖的心理咨询机构。无论你身在何处，都能获得专业的陪伴与关怀。
          </p>
          <div class="hero-search">
            <label class="search-label" for="address-search">想要更精准的位置？</label>
            <div class="search-controls">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M11 2a7 7 0 0 1 7 7c0 4.2-5 11-6.5 12.7a.7.7 0 0 1-1 0C9 20 4 13.2 4 9a7 7 0 0 1 7-7Zm0 3a4 4 0 1 0 0 8a4 4 0 0 0 0-8Z"
                  />
                </svg>
                <input
                  id="address-search"
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
              </div>
              <button @click="handleAddressSearch" class="search-button">开始搜索</button>
            </div>
            <p class="search-hint">支持手动输入小区、街道或地标名称，我们将扩大范围为你查找。</p>
            <div class="hero-status">
              <span class="status-chip">
                <strong>{{ resultsCount }}</strong> 家机构
              </span>
              <span class="status-chip">
                {{ loading ? '定位中…' : (error ? '需手动输入' : '定位成功') }}
              </span>
              <span class="status-chip">地图导航 · 地址搜索</span>
            </div>
          </div>
        </div>
        <div
          class="hero-map-wrapper"
          ref="mapSectionRef"
          :class="{ 'is-sticky': isSticky }"
        >
          <div class="hero-map">
            <div class="hero-map-shell">
              <div id="amap-container" class="map-container" :class="{ 'is-dimmed': loading }"></div>
              <div v-if="loading" class="hero-map-overlay">
                <div class="radar">
                  <div class="radar-circle">
                    <div class="radar-grid"></div>
                    <div class="radar-sweep"></div>
                    <div class="radar-center"></div>
                    <transition-group name="radar-heart" tag="div" class="radar-hearts">
                      <span
                        v-for="heart in radarHearts"
                        :key="heart.id"
                        class="radar-heart"
                        :style="{ left: `${heart.x}%`, top: `${heart.y}%` }"
                      >
                        ❤
                      </span>
                    </transition-group>
                  </div>
                </div>
                <div class="map-loading-text">
                  <div class="loading-spinner"></div>
                  <span>正在定位和搜索...</span>
                </div>
              </div>
            </div>
            <div v-if="error" class="map-error">{{ error }}</div>
            <button @click="toggleFullScreen" class="fullscreen-btn">
              {{ isFullscreen ? '退出全屏' : '全屏浏览' }}
            </button>
          </div>
        </div>
      </div>
    </section>

  <div ref="stickySentinelRef" class="sticky-sentinel" aria-hidden="true"></div>

    <div class="content-wrapper">
      <div class="shops-section" v-if="!isFullscreen">
        <div class="shops-header">
          <div>
            <h3>附近心理咨询机构</h3>
            <p class="shops-subtitle">按距离排序，优先呈现更靠近你的选择</p>
          </div>
          <span class="shops-count">{{ resultsCount }} 家机构</span>
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
                <span class="rating" v-if="hasPositiveRating(item.rating)">⭐ {{ item.rating }}</span>
                <span class="price" v-if="getPriceLabel(item.avgPrice)">{{ getPriceLabel(item.avgPrice) }}</span>
              </div>
            </div>
            <div class="shop-footer">
              <span>点击居中至地图</span>
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="m9.5 6.5l5 5l-5 5l1.5 1.5l6.5-6.5l-6.5-6.5z"
                />
              </svg>
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
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
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
const stickySentinelRef = ref(null)
const isSticky = ref(false) // 新增：追踪地图是否已吸顶
let scrollContainer = null
let debounceTimer = null
let map = null
let userLocationMarker = null // 新增：用于存储用户位置标记
let markers = []
let stickyObserver = null
let lastScrollTop = 0
let hasStoredScrollPosition = false
let lastScrollLeft = 0
let scrollEl = null
let unfreezeBodyScroll = null
let prevScrollRestoration = null
let lastFocusedElement = null
// 粘性进入/退出阈值（加入迟滞，防止在临界点来回抖动）
const STICKY_ENTER_OFFSET = 360
const STICKY_EXIT_OFFSET = 420
const USE_NATIVE_FULLSCREEN = false
const DEBUG = false

const resultsCount = computed(() => results.value.length)

const radarHearts = ref([])
let radarInterval = null
let heartIdCounter = 0

watch(isSticky, (value) => {
  if (DEBUG) console.log('[MapSearch] sticky 状态更新:', value)
})

// 页面加载时自动开始搜索
onMounted(async () => {
  await initMap()
  await getLocation()

  // 添加全屏事件监听（仅原生全屏时）
  if (USE_NATIVE_FULLSCREEN) {
    document.addEventListener('fullscreenchange', handleFullscreenChange)
  }
  // 监听 ESC 退出（用于 CSS 全屏）
  window.addEventListener('keydown', onKeydown)

  // 添加滚动监听 - 确保在DOM更新后添加
  nextTick(() => {
    // 立即执行一次，处理初始状态
    handleScroll()

    // 添加事件监听
    window.addEventListener('scroll', handleScroll)
    const containerEl = mapContainerRef.value
    if (containerEl) {
      scrollContainer = containerEl
      scrollContainer.addEventListener('scroll', handleScroll)
    }
    setupStickyObserver()
    if (DEBUG) console.log('已添加滚动监听器')
  })
  startRadarAnimation()
  // 避免浏览器介入滚动恢复
  try {
    prevScrollRestoration = history.scrollRestoration
    history.scrollRestoration = 'manual'
  } catch {}
})

onUnmounted(() => {
  // 移除全屏事件监听
  if (USE_NATIVE_FULLSCREEN) {
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }
  window.removeEventListener('keydown', onKeydown)

  // 移除滚动监听
  window.removeEventListener('scroll', handleScroll)
  if (scrollContainer) {
    scrollContainer.removeEventListener('scroll', handleScroll)
    scrollContainer = null
  }

  if (stickyObserver) {
    stickyObserver.disconnect()
    stickyObserver = null
  }

  if (radarInterval) {
    clearInterval(radarInterval)
    radarInterval = null
  }
  // 还原标题行为
  try {
    if (prevScrollRestoration) history.scrollRestoration = prevScrollRestoration
  } catch {}
})

// 处理滚动事件，检测地图是否处于吸顶状态
const handleScroll = () => {
  if (!stickySentinelRef.value) return

  const sentinelRect = stickySentinelRef.value.getBoundingClientRect()
  let shouldStick = isSticky.value
  if (!isSticky.value && sentinelRect.top <= STICKY_ENTER_OFFSET) {
    shouldStick = true
  } else if (isSticky.value && sentinelRect.top >= STICKY_EXIT_OFFSET) {
    shouldStick = false
  }

  if (isSticky.value !== shouldStick) {
    isSticky.value = shouldStick
    if (DEBUG) console.log('粘性状态变化 - sentinel.top:', sentinelRect.top, 'isSticky:', isSticky.value)
    nextTick(() => {
      if (map && typeof map.resize === 'function') {
        map.resize()
      }
    })
  }
}

const setupStickyObserver = () => {
  if (!stickySentinelRef.value) return

  stickyObserver = new IntersectionObserver(
    ([entry]) => {
      const top = entry.boundingClientRect.top
      let shouldStick = isSticky.value
      if (!isSticky.value && top <= STICKY_ENTER_OFFSET) {
        shouldStick = true
      } else if (isSticky.value && top >= STICKY_EXIT_OFFSET) {
        shouldStick = false
      }
      if (isSticky.value !== shouldStick) {
        isSticky.value = shouldStick
        if (DEBUG) console.log('[MapSearch] IntersectionObserver -> sticky:', shouldStick, 'rectTop:', top)
        nextTick(() => {
          if (map && typeof map.resize === 'function') {
            map.resize()
          }
        })
      }
    },
    {
      root: null,
      threshold: [0, 1],
      rootMargin: `-${STICKY_ENTER_OFFSET}px 0px 0px 0px`
    }
  )

  stickyObserver.observe(stickySentinelRef.value)
}

const getScroller = () => {
  return document.scrollingElement || document.documentElement || document.body
}

const storeScrollPosition = (force = false) => {
  if (!force && hasStoredScrollPosition) return
  const se = getScroller()
  scrollEl = se
  lastScrollTop = (se && typeof se.scrollTop === 'number') ? se.scrollTop : (window.scrollY || window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0)
  lastScrollLeft = (se && typeof se.scrollLeft === 'number') ? se.scrollLeft : (window.scrollX || window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft || 0)
  hasStoredScrollPosition = true
}

// 退出全屏时，禁用平滑滚动以避免浏览器动画导致的偏移
const disableSmoothScrollTemporarily = () => {
  const html = document.documentElement
  const body = document.body
  const prevHtml = html.style.scrollBehavior
  const prevBody = body.style.scrollBehavior
  const prevAnchorHtml = html.style.overflowAnchor
  const prevAnchorBody = body.style.overflowAnchor
  html.style.scrollBehavior = 'auto'
  body.style.scrollBehavior = 'auto'
  // 禁用滚动锚点，避免浏览器根据内容变化自动调整滚动
  html.style.overflowAnchor = 'none'
  body.style.overflowAnchor = 'none'
  return () => {
    html.style.scrollBehavior = prevHtml
    body.style.scrollBehavior = prevBody
    html.style.overflowAnchor = prevAnchorHtml
    body.style.overflowAnchor = prevAnchorBody
  }
}

const restoreScrollPosition = () => {
  const se = scrollEl || getScroller()
  if (se) {
    se.scrollTop = lastScrollTop
    se.scrollLeft = lastScrollLeft
  }
  // 同步调用 window.scrollTo，兼容部分浏览器
  window.scrollTo(lastScrollLeft || 0, lastScrollTop || 0)
}

// 进入全屏前冻结页面滚动，避免布局变化带来的自动滚动
const freezeBodyScroll = () => {
  const body = document.body
  const html = document.documentElement
  const prev = {
    position: body.style.position,
    top: body.style.top,
    left: body.style.left,
    width: body.style.width,
    overflow: body.style.overflow,
  }
  const top = window.scrollY || html.scrollTop || body.scrollTop || 0
  const left = window.scrollX || html.scrollLeft || body.scrollLeft || 0
  body.style.position = 'fixed'
  body.style.top = `-${top}px`
  body.style.left = `-${left}px`
  body.style.width = '100%'
  body.style.overflow = 'hidden'
  return () => {
    body.style.position = prev.position
    body.style.top = prev.top
    body.style.left = prev.left
    body.style.width = prev.width
    body.style.overflow = prev.overflow
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

const createMap = () => {
  map = new AMap.Map('amap-container', {
    zoom: 13,
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
    map.setZoom(15)
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

const getPriceLabel = (price) => {
  if (price === null || price === undefined) return ''

  let numeric = null

  if (typeof price === 'number') {
    numeric = price
  } else if (typeof price === 'string') {
    const digits = price.replace(/[^\d.]/g, '')
    if (digits) {
      numeric = Number(digits)
    }
  }

  if (numeric === null || Number.isNaN(numeric)) {
    return typeof price === 'string' ? price : ''
  }

  if (numeric <= 0) {
    return ''
  }

  const formatted = Number.isInteger(numeric) ? numeric : numeric.toFixed(1)
  return `¥${formatted}/次`
}

// 仅显示大于 0 的评分，过滤 0 或无效值
const hasPositiveRating = (rating) => {
  if (rating === null || rating === undefined) return false
  // 支持字符串和数字，例如 '0'、'4.5'
  const n = typeof rating === 'number' ? rating : Number(String(rating).trim())
  return Number.isFinite(n) && n > 0
}

// 切换全屏模式
const toggleFullScreen = () => {
  if (USE_NATIVE_FULLSCREEN) {
    if (!document.fullscreenElement) {
      // 进入全屏前记录当前位置
      storeScrollPosition(true)
      // 记录并暂时移除焦点，防止浏览器自动滚动到聚焦元素
      lastFocusedElement = document.activeElement instanceof HTMLElement ? document.activeElement : null
      if (lastFocusedElement && typeof lastFocusedElement.blur === 'function') {
        try { lastFocusedElement.blur() } catch (e) {}
      }
      // 冻结页面滚动，避免全屏切换引发布局滚动
      unfreezeBodyScroll = freezeBodyScroll()
      mapContainerRef.value?.requestFullscreen()
    } else if (document.exitFullscreen) {
      document.exitFullscreen()
    }
    return
  }

  // CSS 全屏路径
  if (!isFullscreen.value) {
    // 进入 CSS 全屏
    storeScrollPosition(true)
    lastFocusedElement = document.activeElement instanceof HTMLElement ? document.activeElement : null
    if (lastFocusedElement && typeof lastFocusedElement.blur === 'function') {
      try { lastFocusedElement.blur() } catch (e) {}
    }
    unfreezeBodyScroll = freezeBodyScroll()
    isSticky.value = false
    isFullscreen.value = true
    nextTick(() => {
      if (map && typeof map.resize === 'function') {
        try { map.resize() } catch (e) {}
      }
    })
  } else {
    // 退出 CSS 全屏
    const restoreSmooth = disableSmoothScrollTemporarily()
    if (typeof unfreezeBodyScroll === 'function') {
      try { unfreezeBodyScroll() } catch (e) {} finally { unfreezeBodyScroll = null }
    }
    // 先切换状态再恢复滚动，避免样式变化影响计算
    isFullscreen.value = false
    requestAnimationFrame(() => {
      // 稳定恢复
      const se = scrollEl || document.scrollingElement || document.documentElement
      const targetTop = lastScrollTop || 0
      const tryRestore = () => {
        if (se) se.scrollTop = targetTop
        window.scrollTo(0, targetTop)
      }
      tryRestore()
      setTimeout(tryRestore, 50)
      setTimeout(() => {
        tryRestore()
        handleScroll()
        restoreSmooth()
        hasStoredScrollPosition = false
        scrollEl = null
        if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
          try { lastFocusedElement.focus({ preventScroll: true }) } catch (e) {}
        }
        lastFocusedElement = null
        if (map && typeof map.resize === 'function') {
          setTimeout(() => { try { map.resize() } catch (e) {} }, 50)
        }
      }, 120)
    })
  }
}

// 监听全屏状态变化（例如用户按 ESC 键）
const handleFullscreenChange = () => {
  if (!USE_NATIVE_FULLSCREEN) return
  const nowFullscreen = !!document.fullscreenElement
  if (nowFullscreen) {
    // 确保无论如何进入全屏都会记录当前位置
    storeScrollPosition()
    isSticky.value = false
  } else {
    // 恢复滚动位置，等待浏览器退出全屏后的布局稳定，并多次重试以应对布局/渲染竞争
    const restoreSmooth = disableSmoothScrollTemporarily()
    const restore = () => restoreScrollPosition()
    requestAnimationFrame(() => {
      // 先解除冻结，再恢复滚动
      if (typeof unfreezeBodyScroll === 'function') {
        try { unfreezeBodyScroll() } catch (e) {} finally { unfreezeBodyScroll = null }
      }
      restore()
      setTimeout(restore, 50)
      setTimeout(() => {
        restore()
        handleScroll()
        restoreSmooth()
        hasStoredScrollPosition = false
        scrollEl = null
        // 恢复原焦点，但不触发滚动
        if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
          try { lastFocusedElement.focus({ preventScroll: true }) } catch (e) {}
        }
        lastFocusedElement = null
        // 退出全屏稍后再 resize 地图，避免影响滚动恢复
        if (map && typeof map.resize === 'function') {
          setTimeout(() => {
            try { map.resize() } catch (e) {}
          }, 50)
        }
      }, 120)
    })
  }

  isFullscreen.value = nowFullscreen

  // 进入全屏时，尽快重置地图尺寸以适应新容器大小
  if (nowFullscreen && map && typeof map.resize === 'function') {
    nextTick(() => {
      try { map.resize() } catch (e) {}
    })
  }
}

const onKeydown = (e) => {
  if (e.key === 'Escape' && isFullscreen.value && !USE_NATIVE_FULLSCREEN) {
    // 模拟 ESC 退出 CSS 全屏
    toggleFullScreen()
  }
}

const startRadarAnimation = () => {
  const createHeart = () => {
    const angle = Math.random() * Math.PI * 2
    const radius = Math.random() * 38 + 8 // 保证爱心不贴边
    const center = 50
    const x = center + radius * Math.cos(angle)
    const y = center + radius * Math.sin(angle)
    const id = heartIdCounter++
    radarHearts.value.push({ id, x, y })
    setTimeout(() => {
      radarHearts.value = radarHearts.value.filter((heart) => heart.id !== id)
    }, 2400)
  }

  createHeart()
  radarInterval = setInterval(createHeart, 900)
}
</script>

<style scoped>
.map-search-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #fefbff 0%, #ffffff 40%, #f8fafc 100%);
  padding-bottom: 72px;
}


.sticky-sentinel {
  height: 1px;
  margin-top: 48px;
}

.map-hero {
  padding: 88px 32px 0;
}

.hero-content {
  max-width: 1280px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 32px;
  padding: 48px 56px;
  box-shadow: 0 28px 60px rgba(211, 142, 160, 0.12);
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
  gap: 32px;
  position: relative;
  overflow: hidden;
}

.hero-content::after {
  content: '';
  position: absolute;
  inset: 14px;
  border-radius: 26px;
  border: 1px solid rgba(247, 222, 228, 0.5);
  pointer-events: none;
}

.hero-copy {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: #1f2937;
}

.hero-tag {
  font-size: 0.95rem;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: rgba(108, 82, 88, 0.6);
  margin: 0;
  -webkit-user-select: none;
  user-select: none;
}

.hero-title {
  font-size: 2.8rem;
  line-height: 1.1;
  margin: 0;
  color: #1f3f38;
  font-weight: 700;
  -webkit-user-select: none;
  user-select: none;
}

.hero-subtitle {
  margin: 0;
  font-size: 1.08rem;
  line-height: 1.7;
  color: rgba(48, 52, 63, 0.8);
  -webkit-user-select: none;
  user-select: none;
}

.hero-search {
  margin-top: 26px;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  border: 1px solid rgba(247, 222, 228, 0.6);
  padding: 22px 24px 26px;
  box-shadow: 0 20px 52px rgba(211, 142, 160, 0.14);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero-status {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.55rem 1.1rem;
  border-radius: 999px;
  background: rgba(211, 142, 160, 0.12);
  color: #c06b85;
  font-weight: 600;
  font-size: 0.92rem;
  -webkit-user-select: none;
  user-select: none;
}

.status-chip strong {
  font-size: 1.05rem;
}

.hero-map-wrapper {
  position: relative;
  height: clamp(260px, 30vw, 360px);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: padding 0.35s ease;
}

.hero-map {
  position: relative;
  width: clamp(260px, 30vw, 360px);
  aspect-ratio: 1;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 28px 60px rgba(31, 82, 63, 0.14);
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.35s ease, top 0.35s ease, right 0.35s ease, width 0.35s ease;
}

.hero-map-shell {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  background: radial-gradient(circle at center, rgba(255, 214, 221, 0.32) 0%, rgba(255, 214, 221, 0.12) 55%, rgba(255, 214, 221, 0) 90%);
  border: 10px solid rgba(211, 142, 160, 0.45);
  box-shadow: inset 0 0 40px rgba(192, 107, 133, 0.2);
}

.hero-map-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  padding: 24px;
  background: transparent; /* 仅显示圆形雷达，不要方形半透明遮罩 */
  backdrop-filter: none;
  pointer-events: none; /* 避免遮挡交互，如需阻止交互可改为 auto */
}

/* 圆形雷达样式（加载时显示） */
.radar-circle {
  position: relative;
  width: 88%;
  aspect-ratio: 1;
  border-radius: 50%;
  /* 原始粉色系背景 */
  background: radial-gradient(circle at center, rgba(211, 142, 160, 0.08) 0%, rgba(211, 142, 160, 0.04) 50%, rgba(211, 142, 160, 0.02) 75%, transparent 100%);
  box-shadow: inset 0 0 32px rgba(192, 107, 133, 0.18);
  overflow: hidden;
}

.radar-grid {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at center, rgba(208, 56, 94, 0.18) 1px, transparent 1px),
    radial-gradient(circle at center, rgba(208, 56, 94, 0.12) 1px, transparent 1px),
    radial-gradient(circle at center, rgba(208, 56, 94, 0.08) 1px, transparent 1px);
  background-size: 12% 12%, 24% 24%, 36% 36%;
  background-position: center;
  opacity: 0.35;
}

.radar-sweep {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  /* 粉色扇形楔面，前锋更亮，尾部渐隐 */
  background: conic-gradient(
    from 0deg,
    rgba(208, 56, 94, 0.65) 0deg,
    rgba(208, 56, 94, 0.35) 12deg,
    rgba(208, 56, 94, 0.12) 28deg,
    transparent 35deg
  );
  filter: drop-shadow(0 0 8px rgba(208, 56, 94, 0.45));
  transform-origin: center;
  animation: radar-wedge 3s linear infinite;
}

@keyframes radar-wedge {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.map-loading-text {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: #1f3f38;
}

.map-container {
  width: 100%;
  height: 100%;
  transition: opacity 0.3s ease;
}

.map-container.is-dimmed {
  opacity: 0;
  pointer-events: none;
}

.hero-map-wrapper.is-sticky .hero-map {
  position: fixed;
  top: 96px;
  right: 56px;
  transform: translateY(-32px) scale(0.82);
  z-index: 40;
}

.radar {
  width: min(340px, 100%);
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  overflow: hidden; /* 避免圆外溢出，看起来始终是圆 */

}

@keyframes radar-spin {
  from {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

.radar-hearts {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.radar-center {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 10px;
  height: 10px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: radial-gradient(circle, #d0385e 0%, #d38ea0 60%, rgba(211, 142, 160, 0) 70%);
  box-shadow: 0 0 8px rgba(208, 56, 94, 0.6);
}

.radar-heart {
  position: absolute;
  transform: translate(-50%, -50%);
  color: #c06b85; /* 显示原始❤字符 */
  font-size: 1.1rem;
  opacity: 0.9;
  text-shadow: 0 6px 12px rgba(192, 107, 133, 0.45);
}

.radar-heart::before { content: none !important; }

.radar-heart-enter-active,
.radar-heart-leave-active {
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.radar-heart-enter-from,
.radar-heart-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.6);
}

.loading-spinner {
  width: 22px;
  height: 22px;
  border: 3px solid rgba(211, 142, 160, 0.25);
  border-top-color: #d38ea0;
  border-radius: 50%;
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

.map-error {
  position: absolute;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 245, 247, 0.96);
  color: #d0385e;
  padding: 0.75rem 1.6rem;
  border-radius: 999px;
  border: 1px solid rgba(208, 56, 94, 0.18);
  font-weight: 500;
  backdrop-filter: blur(8px);
  white-space: nowrap;
}

.fullscreen-btn {
  position: absolute;
  bottom: 18px;
  right: 18px;
  padding: 0.65rem 1.3rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(31, 82, 63, 0.15);
  color: #1f3f38;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(31, 82, 63, 0.16);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.fullscreen-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 32px rgba(31, 82, 63, 0.2);
}

.map-search-container.is-fullscreen {
  padding-bottom: 0;
  position: fixed;
  inset: 0;
  z-index: 10000;
  overflow: hidden;
}

.map-search-container.is-fullscreen .map-hero {
  padding: 0;
}

.map-search-container.is-fullscreen .hero-content {
  max-width: 100%;
  margin: 0;
  padding: 0;
  border-radius: 0;
  box-shadow: none;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-search-container.is-fullscreen .hero-content::after {
  display: none;
}

.map-search-container.is-fullscreen .hero-copy {
  display: none;
}

.map-search-container.is-fullscreen .hero-map-wrapper {
  width: 100%;
  height: 100vh;
  align-items: stretch;
  justify-content: stretch;
}

.map-search-container.is-fullscreen .hero-map {
  position: relative !important;
  top: auto;
  right: auto;
  transform: none;
  width: 100vw;
  height: 100vh;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
  background: #000000;
}

.map-search-container.is-fullscreen .fullscreen-btn {
  top: clamp(24px, 4vh, 48px);
  right: clamp(24px, 4vh, 48px);
  bottom: auto;
}

.map-search-container.is-fullscreen .content-wrapper {
  display: none;
}

.map-search-container.is-fullscreen .hero-map-shell {
  border-radius: 0;
  border: none;
  background: transparent; /* 全屏加载时不显示白色矩形底，保留圆形雷达视觉 */
  box-shadow: none;
}

.map-search-container.is-fullscreen .hero-map-overlay {
  background: transparent; /* 全屏时也保持透明，不要方形透视镜效果 */
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 32px;
  margin-top: 42px;
  padding: 0 32px;
}

.search-label {
  font-size: 1rem;
  font-weight: 600;
  color: #1f3f38;
  -webkit-user-select: none;
  user-select: none;
}

.search-controls {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.input-wrapper {
  position: relative;
  flex: 1;
}

.input-icon {
  position: absolute;
  top: 50%;
  left: 18px;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: rgba(31, 63, 56, 0.45);
}

.address-input {
  width: 100%;
  padding: 0.95rem 1rem 0.95rem 3.4rem;
  border-radius: 18px;
  border: 1.5px solid rgba(31, 63, 56, 0.15);
  font-size: 1rem;
  background: rgba(248, 250, 252, 0.9);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.address-input:focus {
  outline: none;
  border-color: rgba(211, 142, 160, 0.65);
  box-shadow: 0 0 0 4px rgba(211, 142, 160, 0.2);
  background: #ffffff;
}

.suggestions-list {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 100%;
  background: #ffffff;
  border-radius: 18px;
  border: 1px solid rgba(31, 63, 56, 0.12);
  list-style: none;
  margin: 0;
  padding: 8px 0;
  box-shadow: 0 24px 48px rgba(17, 24, 39, 0.12);
  max-height: 260px;
  overflow-y: auto;
  z-index: 30;
}

.suggestion-item {
  padding: 0.85rem 1.4rem;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
  color: #1f3f38;
  -webkit-user-select: none;
  user-select: none;
}

.suggestion-item:hover {
  background: rgba(211, 142, 160, 0.08);
}

.search-button {
  padding: 0.9rem 1.8rem;
  border-radius: 18px;
  border: none;
  background: linear-gradient(135deg, #d38ea0, #c06b85);
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 18px 32px rgba(192, 107, 133, 0.25);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  -webkit-user-select: none;
  user-select: none;
}

.search-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 40px rgba(192, 107, 133, 0.3);
}

.search-hint {
  margin: 0;
  font-size: 0.92rem;
  color: rgba(31, 51, 57, 0.6);
}

.shops-section {
  background: #ffffff;
  border-radius: 28px;
  box-shadow: 0 28px 60px rgba(17, 24, 39, 0.1);
  padding: 32px;
}

.shops-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.shops-header h3 {
  margin: 0;
  font-size: 1.55rem;
  font-weight: 700;
  color: #1f3f38;
  -webkit-user-select: none;
  user-select: none;
}

.shops-subtitle {
  margin: 6px 0 0;
  color: rgba(31, 51, 57, 0.6);
  font-size: 0.95rem;
  -webkit-user-select: none;
  user-select: none;
}

.shops-count {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  background: rgba(211, 142, 160, 0.12);
  color: #c06b85;
  font-weight: 600;
  -webkit-user-select: none;
  user-select: none;
}

.shops-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.shop-card {
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(31, 63, 56, 0.05);
  box-shadow: 0 14px 28px rgba(17, 24, 39, 0.12);
  display: flex;
  flex-direction: column;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  cursor: pointer;
  -webkit-user-select: none;
  user-select: none;
}

.shop-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 22px 40px rgba(17, 24, 39, 0.18);
}

.shop-image {
  position: relative;
  height: 140px;
  overflow: hidden;
}

.shop-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.shop-card:hover .shop-image img {
  transform: scale(1.05);
}

.distance-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(31, 63, 56, 0.8);
  color: #ffffff;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  min-width: 60px;
  text-align: center;
}

.shop-info {
  padding: 20px 22px 16px;
  flex: 1;
}

.shop-name {
  margin: 0 0 8px;
  font-size: 1.05rem;
  font-weight: 700;
  color: #1f3f38;
  display: -webkit-box;
  line-clamp: 1;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  -webkit-user-select: none;
  user-select: none;
}

.shop-address {
  margin: 0 0 12px;
  font-size: 0.92rem;
  color: rgba(31, 51, 57, 0.65);
  line-height: 1.45;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  -webkit-user-select: none;
  user-select: none;
}

.shop-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: rgba(31, 51, 57, 0.75);
}

.rating {
  color: #f59e0b;
  font-weight: 600;
}

.price {
  color: #ef5350;
  font-weight: 600;
}

.shop-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-top: 1px solid rgba(17, 24, 39, 0.08);
  font-size: 0.88rem;
  color: rgba(31, 51, 57, 0.65);
  -webkit-user-select: none;
  user-select: none;
}

.shop-footer svg {
  width: 18px;
  height: 18px;
}

.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: rgba(31, 51, 57, 0.7);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f3f38;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.95rem;
}

@media (max-width: 1200px) {
  .hero-content {
    grid-template-columns: 1fr;
  }

  .hero-map-wrapper {
    height: auto;
    margin-top: 24px;
  }

  .hero-map {
    width: min(320px, 90%);
  }

  .shops-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-map-wrapper.is-sticky .hero-map {
    position: relative;
    top: auto;
    right: auto;
    transform: none;
  }
}

@media (max-width: 900px) {
  .map-hero {
    padding: 72px 24px 0;
  }

  .content-wrapper {
    padding: 0 24px;
  }

  .search-controls {
    flex-direction: column;
  }

  .search-button {
    width: 100%;
    justify-content: center;
  }

  .hero-map-wrapper {
    height: auto;
  }

  .hero-map {
    width: min(300px, 100%);
    padding: 10px;
  }
}

@media (max-width: 640px) {
  .shops-grid {
    grid-template-columns: 1fr;
  }

  .shops-section {
    padding: 24px;
  }

  .shop-image {
    height: 120px;
  }
}
</style>
