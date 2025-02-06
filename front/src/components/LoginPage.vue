<template>
  <div class="auth-container">
    <h2>登录</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">账号名</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <div class="form-group">
        <label for="role">选择角色</label>
        <select id="role" v-model="role" required>
          <option value="user">用户</option>
          <option value="manager">管理员</option>
        </select>
      </div>
      <button type="submit">登录</button>
    </form>
    <p>还没有账号？<router-link to="/register">注册</router-link></p>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  data() {
    return {
      username: '',
      password: '',
      role: 'user'
    };
  },
  methods: {
    async handleLogin() {
      try{
        if (this.role === 'user'){
          const response = await this.$axios.post('/user/login', {
            userAccount: this.username,
            password: this.password,
          });
          if (response.data.status === 'SUCCESS'){
            alert(`用户登录成功，账号名: ${this.username}`);
            // 跳转到用户界面，并保留userID
            const userID = response.data.user.user_id;
            localStorage.setItem('userID', userID);
            this.$router.push('/user')
          }else if (response.data.status === 'ERROR'){
            alert("错误信息为:" + response.data.errorMessage);
          }
        }else if (this.role === 'manager'){
          const response = await this.$axios.post('/manager/login', {
            userAccount: this.username,
            password: this.password,
          });
          if (response.data.status === 'SUCCESS'){
            alert(`管理员登录成功，账号名: ${this.username}`);
            // 跳转到管理员界面
            this.$router.push('/manager')
          }else if (response.data.status === 'ERROR'){
            alert("错误信息为:" + response.data.errorMessage);
          }
        }
      }catch (error) {
        alert(error.message);
      }
    },
  },
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #f5f5f5;
  font-family: Arial, sans-serif;
}

.auth-container {
  width: 100%;
  max-width: 400px;
  margin: 100px auto;
  padding: 30px;
  background-color: #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  text-align: center;
}

h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  display: block;
}

input,
select {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

input:focus,
select:focus {
  border-color: #007bff;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #0056b3;
}

p {
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

router-link {
  color: #007bff;
  text-decoration: none;
}

router-link:hover {
  text-decoration: underline;
}
</style>