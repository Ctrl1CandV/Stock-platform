<template>
  <div class="auth-container">
    <h2>注册</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="userEmail">用户邮箱</label>
        <input type="text" id="userEmail" v-model="userEmail" required />
      </div>
      <div class="form-group">
        <label for="userName">用户名</label>
        <input type="text" id="userName" v-model="userName" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <div class="form-group">
        <label for="confirm-password">确认密码</label>
        <input type="password" id="confirm-password" v-model="confirmPassword" required />
      </div>
      <button type="submit">注册</button>
    </form>
    <p>已经有账号了？<router-link to="/login">登录</router-link></p>
  </div>
</template>

<script>
export default {
  name: 'RegisterPage',
  data() {
    return {
      userEmail: '',
      userName: '',
      password: '',
      confirmPassword: '',
    };
  },
  methods: {
    async handleRegister() {
      if (this.password !== this.confirmPassword) {
        alert('两次输入的密码不一致');
        return;
      }
      try {
        const response = await this.$axios.post('/user/register', {
          userEmail: this.userEmail,
          userName: this.userName,
          password: this.password
        });
        if (response.data.status === 'SUCCESS'){
          alert(`用户注册成功，用户名: ${this.userName}`);
          this.$router.push('/login');
        }else if (response.data.status === 'ERROR'){
          alert("HTTP状态码为:" + response.status + "\n错误信息为:" + response.data.errorMessage);
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

input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

input:focus {
  border-color: #42b983;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #42b983;
  color: white;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #369f6e;
}

p {
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

router-link {
  color: #42b983;
  text-decoration: none;
}

router-link:hover {
  text-decoration: underline;
}
</style>