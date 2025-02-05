import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from "../stores/authStore.ts";

const routes = [
    { path: '/login', component: () => import('../views/LoginView.vue') },
    {
        path: '/main', component: () => import('../views/MainLayout.vue'),
        meta: { requiresAuth: true },       // 需要用户认证才能访问
        children: [
            { path: '/user', component: () => import('../views/UserInformation.vue') },
            { path: '/search', component: () => import('../views/StockSearch.vue') },
            { path: '/ownership', component: () => import('../views/OwnershipView.vue') },
            { path: '/transaction', component: () => import('../views/TransactionView.vue') },
            { path: '/manager', component: () => import('../views/ManageUserAccount.vue') },
        ]
    },
    { path: '/stock', component: () => import('../views/StockDetail.vue') },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
const authStore = useAuthStore()
router.beforeEach((to, from, next) => {
    // 在跳转时进行验证，如果需要认证且未认证则跳回登录界面
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next('/login')
    } else {
        next()
    }
})