import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'

// 移动设备兼容性检测和处理
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
if (isMobile) {
    // 移动设备特定设置
    document.addEventListener('DOMContentLoaded', () => {
        // 防止双击缩放
        document.addEventListener('touchstart', (event) => {
            if (event.touches.length > 1) {
                event.preventDefault();
            }
        }, { passive: false });

        // 修复iOS点击延迟问题
        document.body.addEventListener('touchstart', () => { }, { passive: true });
    });
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
    size: isMobile ? 'large' : 'default', // 在移动设备上使用更大的UI组件
})

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
    console.error('全局错误:', err);
    console.error('错误信息:', info);
};

app.mount('#app')
