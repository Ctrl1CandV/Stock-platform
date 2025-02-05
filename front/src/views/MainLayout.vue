<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <el-aside v-if="authStore.role === 'user'" width="200px">
      <el-menu :default-active="activeMenu">
        <!-- 动态渲染菜单 -->
        <template v-for="item in userMenus" :key="item.path">
          <el-menu-item :index="item.path" @click="router.push(item.path)">
            {{ item.title }}
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <!-- 右侧内容区 -->
    <div class="content">
      <!-- 顶部导航 -->
      <el-header>
        <div class="user-info">
          <span>{{ userDisplayName }}</span>
          <el-dropdown>
            <el-icon><user /></el-icon>
            <template #dropdown>
              <el-dropdown-item @click="router.push('/user')">个人中心</el-dropdown-item>
              <el-dropdown-item @click="authStore.logout()">退出登录</el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 功能页面 -->
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElIcon } from 'element-plus';
import { User } from '@element-plus/icons-vue';
import { createApp } from 'vue';
import App from '../App.vue';
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore.ts';

const authStore = useAuthStore();
const router = useRouter();
const app = createApp(App);
app.component('ElIcon', ElIcon);  // 注册 ElIcon 组件
app.component('User', User);  // 注册 User 图标组件
app.mount('#app');

// 高亮菜单项
const activeMenu = computed(() => router.currentRoute.value.path);
const userDisplayName = computed(() => {
  return `${authStore.role === 'user' ? '用户' : '管理员'} (ID: ${authStore.ID})`;
});

// 根据角色动态生成菜单项
const userMenus = computed(() => {
  if (authStore.role === 'user') {
    return [
      { path: '/search', title: '股票搜索' },
      { path: '/ownership', title: '查询持股信息' },
      { path: '/transaction', title: '查询交易记录' },
    ];
  }
  return [];
});
</script>