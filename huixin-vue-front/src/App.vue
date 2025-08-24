<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  // 移除自动清除登录状态的逻辑
  // 登录状态将使用 localStorage 持久化保存
  // 只有用户主动退出登录时才会清除
})
</script>

<template>
  <router-view></router-view>
</template>

<style>
@import '@/assets/styles/base.css';
  @import '@/assets/styles/responsive-4k.css';
@import '@/assets/styles/utilities-4k.css';
@import '@/assets/styles/fix-width-issue.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  line-height: 1.6;
}

a {
  text-decoration: none;
  color: inherit;
}

ul {
  list-style: none;
}
</style>
