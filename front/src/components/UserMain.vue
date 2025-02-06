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
        <el-menu-item index="2" @click="goToOwnershipSearch">
          <i class="el-icon-document"></i>
          <span slot="title">持有股查询</span>
        </el-menu-item>
        <el-menu-item index="3" @click="goToTransactionSearch">
          <i class="el-icon-setting"></i>
          <span slot="title">交易记录查询</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航栏 -->
      <el-header style="text-align: right; font-size: 12px; border-bottom: 1px solid #e6e6e6;">
        <div class="brand-area">
          <div class="logo"></div>
          <span class="brand-text">Admin Pro</span>
        </div>
        <el-dropdown>
          <i class="el-icon-user" style="margin-right: 15px; cursor: pointer;"></i>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="$router.push('/user/profile')">个人信息</el-dropdown-item>
            <el-dropdown-item @click.native="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </el-header>

      <!-- 主内容区域 -->
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
export default {
  name: 'UserMain',
  data() {
    return {
      userID: localStorage.getItem('userID'),
      activeMenu: '1',
    };
  },
  methods: {
    handleLogout() {
      console.log(this.userID);
      localStorage.removeItem('userID');
      this.$router.push('/login');
    },
    goToHomePage() {
      this.$router.push('/user');
      this.activeMenu = '1';
    },
    goToOwnershipSearch() {
      this.$router.push('/user/ownership');
      this.activeMenu = '2';
    },
    goToTransactionSearch() {
      this.$router.push('/user/transaction');
      this.activeMenu = '3';
    }
  },
  watch: {
    '$route': function (to) {
      // 监听路由变化，动态更新菜单项
      if (to.path === '/user') {
        this.activeMenu = '1';
      } else if (to.path === '/user/ownership') {
        this.activeMenu = '2';
      } else if (to.path === '/user/transaction') {
        this.activeMenu = '3';
      }
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