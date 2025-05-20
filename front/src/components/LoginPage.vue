<template>
  <div class="video-container">
    <video autoplay loop muted preload="auto" class="background-video">
      <source src="@/assets/loginBackground.mp4" type="video/mp4">
    </video>
    <div class="overlay"></div>
    <div class="auth-container">
      <h2 class="auth-title">{{ activeTab === 'login' ? '登录' : '注册' }}</h2>

      <!-- 登录表单 -->
      <div v-if="activeTab === 'login'" class="form-container">
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="username">账号名</label>
            <input type="text" id="username" v-model="loginForm.username" required />
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input type="password" id="password" v-model="loginForm.password" required />
          </div>
          <div class="form-group">
            <label for="role">选择角色</label>
            <select id="role" v-model="loginForm.role" required>
              <option value="user">用户</option>
              <option value="manager">管理员</option>
            </select>
          </div>
          <button type="submit" class="btn-primary">登录</button>
        </form>
        <p class="switch-text">还没有账号？<span class="link" @click="activeTab = 'register'">立即注册</span></p>
      </div>

      <!-- 注册表单 -->
      <div v-if="activeTab === 'register'" class="form-container">
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label for="userEmail">用户邮箱</label>
            <input type="email" id="userEmail" v-model="registerForm.userEmail" required />
          </div>
          <div class="form-group">
            <label for="userName">用户名</label>
            <input type="text" id="userName" v-model="registerForm.userName" required />
          </div>
          <div class="form-group">
            <label for="registerPassword">密码</label>
            <input type="password" id="registerPassword" v-model="registerForm.password" required />
          </div>
          <div class="form-group">
            <label for="confirm-password">确认密码</label>
            <input type="password" id="confirm-password" v-model="registerForm.confirmPassword"
              :class="{ 'input-error': passwordMismatch }" required />
              <span v-if="passwordMismatch" class="error-message">密码不一致</span>
          </div>
          <button type="submit" class="btn-secondary">注册</button>
        </form>
        <p class="switch-text">已经有账号了？<span class="link" @click="activeTab = 'login'">立即登录</span></p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  data() {
    return {
      activeTab: 'login',
      loginForm: {
        username: '',
        password: '',
        role: 'user'
      },
      registerForm: {
        userEmail: '',
        userName: '',
        password: '',
        confirmPassword: '',
      }
    };
  },
  computed: {
    passwordMismatch() {
      return this.registerForm.password && this.registerForm.confirmPassword && this.registerForm.password !== this.registerForm.confirmPassword;
    }
  },
  methods: {
    async handleLogin() {
      try {
        if (this.loginForm.role === 'user') {
          const response = await this.$axios.post('/user/login', {
            userAccount: this.loginForm.username,
            password: this.loginForm.password,
          });
          if (response.data.status === 'SUCCESS') {
            // 跳转到用户界面，并保留userID
            const userID = response.data.user.user_id;
            const userName = response.data.user.user_name;
            localStorage.setItem('userID', userID);
            localStorage.setItem('userName', userName);
            this.$message.success(`用户${userName}登录成功`);
            this.$router.push('/user')
          } else if (response.data.status === 'ERROR') {
            this.$message.error("登录失败:" + response.data.errorMessage);
          }
        } else if (this.loginForm.role === 'manager') {
          const response = await this.$axios.post('/manager/login', {
            userAccount: this.loginForm.username,
            password: this.loginForm.password,
          });
          if (response.data.status === 'SUCCESS') {
            this.$message.success('管理员登录成功');

            // 跳转到管理员界面
            this.$router.push('/manager')
          } else if (response.data.status === 'ERROR') {
            this.$message.error("登录失败:" + response.data.errorMessage);
          }
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async handleRegister() {
      try {
        const response = await this.$axios.post('/user/register', {
          userEmail: this.registerForm.userEmail,
          userName: this.registerForm.userName,
          password: this.registerForm.password
        });
        if (response.data.status === 'SUCCESS') {
          this.$message.success(`用户${this.registerForm.userName}注册成功`);
          this.activeTab = 'login';

          // 自动填充用户名，方便用户登录
          this.loginForm.username = this.registerForm.userName;
        } else if (response.data.status === 'ERROR') {
          this.$message.error("注册失败:" + response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    }
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.video-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.background-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.3);
}

.auth-container {
  width: 100%;
  max-width: 450px;
  padding: 30px;
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  text-align: center;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
}

.auth-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 25px;
  text-align: center;
}

.form-container {
  padding: 0;
}

.form-container {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  display: block;
}

input,
select {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  color: #333;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  outline: none;
  transition: all 0.3s;
}

input:focus,
select:focus {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.btn-primary {
  background-color: #409EFF;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-secondary {
  background-color: #42b983;
  color: white;
}

.btn-secondary:hover {
  background-color: #5dc596;
}

.switch-text {
  margin-top: 20px;
  font-size: 14px;
  color: #606266;
}

.link {
  color: #409EFF;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .auth-container {
    max-width: 90%;
  }
}

.input-error {
  border-color: #f56c6c !important;
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2) !important;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 5px;
  display: block;
  text-align: left;
}
</style>