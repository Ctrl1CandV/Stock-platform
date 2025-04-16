<template>
  <el-container style="height: 100vh;">
    <!-- 左侧功能栏 -->
    <el-aside width="200px" style="background-color: #304156;">
      <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical-demo"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
      >
        <el-menu-item index="1" @click="goToHomePage">
          <i class="el-icon-menu"></i>
          <span slot="title">股票查询</span>
        </el-menu-item>
        <el-menu-item index="2" @click="goToUserManagement">
          <i class="el-icon-user"></i>
          <span slot="title">用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航栏 -->
      <el-header style="text-align: right; font-size: 12px; border-bottom: 1px solid #e6e6e6;">
        <div class="brand-area">
          <div class="logo"></div>
          <span class="brand-text">管理员控制台</span>
        </div>
        <el-dropdown>
          <i class="el-icon-user" style="margin-right: 15px; cursor: pointer;"></i>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </el-header>

      <!-- 主内容区域 -->
      <el-main>
        <component :is="currentComponent"></component>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import HomePage from './HomePage.vue';
import UserManagement from './UserManagement.vue';

export default {
  name: 'ManagerPage',
  components: {
    HomePage,
    UserManagement
  },
  data() {
    return {
      activeMenu: '1',
      currentComponent: 'HomePage'
    };
  },
  methods: {
    handleLogout() {
      localStorage.removeItem('managerID');
      this.$router.push('/login');
    },
    goToHomePage() {
      this.currentComponent = 'HomePage';
      this.activeMenu = '1';
    },
    goToUserManagement() {
      this.currentComponent = 'UserManagement';
      this.activeMenu = '2';
    }
  }
};
</script>

<style scoped>
.el-container {
  font-family: 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.el-aside {
  background: linear-gradient(135deg, #304156 0%, #2b3947 100%) !important;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.el-menu {
  border-right: none !important;
}

/* 菜单项悬停/激活效果 */
.el-menu-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  margin: 40px 8px !important;
  border-radius: 6px !important;
}

.el-menu-item:hover {
  background-color: rgba(64, 158, 255, 0.08) !important;
  transform: translateX(4px);
}

.el-menu-item.is-active {
  background-color: rgba(64, 158, 255, 0.15) !important;
  font-weight: 500;
}

.el-menu-item i {
  color: #a8b5c5;
  transition: color 0.3s;
}

.el-menu-item.is-active i {
  color: #409EFF;
}

.el-header {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(6px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px !important;
}

/* 用户图标样式 */
.el-icon-user {
  padding: 8px;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF !important;
  transition: all 0.3s;
}

.el-icon-user:hover {
  background: rgba(64, 158, 255, 0.2);
  transform: scale(1.05);
}

.el-main {
  background: #f8fafc !important;
  padding: 24px !important;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 32px;
  height: 32px;
  background: #409EFF;
  border-radius: 6px;
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.el-dropdown-menu {
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
  padding: 6px 0 !important;
}

.el-dropdown-menu__item {
  padding: 10px 16px !important;
  transition: all 0.2s !important;
}

.el-dropdown-menu__item:hover {
  background: #f5f7fa !important;
  color: #409EFF !important;
  transform: translateX(2px);
}
</style>