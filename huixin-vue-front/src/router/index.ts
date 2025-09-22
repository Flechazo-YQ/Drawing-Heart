import { createRouter, createWebHistory } from 'vue-router'

// === 导入组件 ===
// 主页
import HomeView from '../views/HomeView.vue'
// 认证页面
import LoginView from '../views/auth/LoginView.vue'
// 功能页面
import ChatView from '../views/features/ChatView.vue'
import DrawView from '../views/features/DrawView.vue'

// === 路由配置 ===
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // === 主页 ===
    {
      path: '/',
      name: 'home',
      component: HomeView
    },

    // === 公共页面 ===
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/public/AboutView.vue')
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('../views/public/TermsOfServiceView.vue')
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('../views/public/PrivacyPolicyView.vue')
    },

    // === 认证页面 ===
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue')
    },
    {
      path: '/forget',
      name: 'forget',
      component: () => import('../views/auth/ForgetPasswordView.vue')
    },

    // === 管理员认证 ===
    {
      path: '/admin-login',
      name: 'adminLogin',
      component: () => import('../views/admin/AdminLoginView.vue')
    },

    // === 用户功能页面 ===
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
      path:'/map',
      name: 'map',
      component: () => import('../views/features/MapSearchView.vue'),
      meta: { requiresAuth: true }
    },

    // === 用户中心 ===
    {
      path: '/user',
      name: 'user',
      component: () => import('../views/user/UserView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/records',
      name: 'records',
      component: () => import('../views/user/DrawingRecords.vue'),
      meta: { requiresAuth: true }
    },

    // === 管理员页面 ===
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/AdminView.vue'),
      meta: { requiresAdminAuth: true }
    }
  ]
})

// === 全局路由守卫 ===
router.beforeEach((to, from, next) => {
  // 检查管理员权限
  if (to.matched.some(record => record.meta.requiresAdminAuth)) {
    if (!localStorage.getItem('isAdminLoggedIn')) {
      next({
        path: '/admin-login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }

  // 检查用户权限
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!localStorage.getItem('isLoggedIn')) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }

  next()
})

export default router
