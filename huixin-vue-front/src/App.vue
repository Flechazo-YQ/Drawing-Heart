<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <router-view></router-view>
</template>

<style>
@import '@/assets/styles/base.css';

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
