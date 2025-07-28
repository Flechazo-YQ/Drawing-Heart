import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ChatView from '../views/ChatView.vue'
import DrawView from '../views/DrawView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/chat',
      name: 'chat',
      component: ChatView,
      meta: { requiresAuth: true }
    },
    {
      path: '/draw',
      name: 'draw',
      component: DrawView,
      meta: { requiresAuth: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/user',
      name: 'user',
      component: () => import('../views/UserView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/forget',
      name: 'forget',
      component: () => import('../views/ForgetPasswordView.vue')
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('../views/TermsOfServiceView.vue')
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('../views/PrivacyPolicyView.vue')
    },
    {
      path: '/admin-login',
      name: 'adminLogin',
      component: () => import('../views/AdminLoginView.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAdminAuth: true }
    }
  ]
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要管理员权限
  if (to.matched.some(record => record.meta.requiresAdminAuth)) {
    // 检查是否已登录管理员
    if (!localStorage.getItem('isAdminLoggedIn')) {
      // 如果没有登录，重定向到管理员登录页
      next({
        path: '/admin-login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  }
  // 检查是否需要普通用户权限
  else if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否已登录
    if (!localStorage.getItem('isLoggedIn')) {
      // 如果没有登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
