<template>
  <div class="user-profile">
    <h1 class="title">个人信息</h1>

    <div v-if="user" class="profile-container">
      <!-- 用户信息展示 -->
      <div class="user-info">
        <div class="info-item">
          <strong>邮箱:</strong>
          <span>{{ user.userEmail }}</span>
        </div>
        <div class="info-item">
          <strong>用户名:</strong>
          <span>{{ user.userName }}</span>
        </div>
        <div class="info-item">
          <strong>余额:</strong>
          <input v-model="user.userBalance" type="number" class="input-field balance-input" />
          <button @click="updateBalance" class="btn primary-btn">更新余额</button>
        </div>
      </div>

      <!-- 修改密码 -->
      <div class="password-section">
        <h2>修改密码</h2>
        <input v-model="oldPassword" type="password" class="input-field" placeholder="旧密码" />
        <input v-model="newPassword" type="password" class="input-field" placeholder="新密码" />
        <button @click="changePassword" class="btn primary-btn">修改密码</button>
      </div>

      <!-- 其他信息 -->
      <div class="other-info-section">
        <h2>其他信息</h2>
        <form @submit.prevent="updateUserInfo">
          <div class="form-row">
            <label>年龄:</label>
            <input v-model="user.userAge" type="number" class="input-field" />
          </div>
          <div class="form-row">
            <label>性别:</label>
            <select v-model="user.userSex" class="input-field">
              <option :value="0">男</option>
              <option :value="1">女</option>
            </select>
          </div>
          <div class="form-row">
            <label>电话号:</label>
            <input v-model="user.phoneNumber" type="text" class="input-field" />
          </div>
          <div class="form-row">
            <label>地址:</label>
            <input v-model="user.address" type="text" class="input-field" />
          </div>
          <div class="form-row">
            <label>备注:</label>
            <textarea v-model="user.remark" class="input-field"></textarea>
          </div>
          <button type="submit" class="btn success-btn">更新信息</button>
        </form>
      </div>
    </div>

    <p v-else class="loading">加载中...</p>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      userID: localStorage.getItem('userID'),
      user: null,
      oldPassword: '',
      newPassword: '',
    };
  },
  async created() {
    await this.fetchUserData();
  },
  methods: {
    async fetchUserData() {
      console.log(this.userID);
      try {
        const response = await this.$axios.get('/user/gainUserInformation', { params: { userID: this.userID } });
        if (response.data.status === 'SUCCESS'){
          const userAccount = response.data.user;
          this.user = {
            userEmail: userAccount.user_email,
            userName: userAccount.user_name,
            userBalance: userAccount.user_balance,
            userAge: userAccount.user_age,
            userSex: userAccount.user_sex,
            phoneNumber: userAccount.phone_number,
            address: userAccount.address,
            remark: userAccount.remark
          }
        }else if (response.data.status === 'ERROR'){
          alert("错误信息为:" + response.data.errorMessage);
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
      }
    },
    async updateBalance() {
      try {
        if (this.user.userBalance < 0){
          alert('无效的用户余额');
          return null;
        }

        const response = await this.$axios.post('/user/updateBalance', {
          userID: this.userID, newBalance: this.user.userBalance
        });
        if (response.data.status === 'SUCCESS'){
          alert('余额更新成功');
        }else if (response.data.status === 'ERROR'){
          alert("余额更新失败\n错误信息为:" + response.data.errorMessage);
        }
      } catch (error) {
        console.error('更新余额失败:', error);
      }
    },
    async changePassword() {
      try {
        const response = await this.$axios.post('/user/changePassword', {
          userID: this.userID,
          oldPassword: this.oldPassword,
          newPassword: this.newPassword
        });
        if (response.data.status === 'SUCCESS'){
          alert('密码更新成功');
          location.reload();
        }else if (response.data.status === 'ERROR'){
          alert("密码更新失败\n错误信息为:" + response.data.errorMessage);
        }
      } catch (error) {
        console.error('更新余额失败:', error);
      }
    },
    async updateUserInfo() {
      try {
        const userData = {
          user_age: this.user.userAge,
          user_sex: this.user.userSex,
          phone_number: this.user.phoneNumber,
          address: this.user.address,
          remark: this.user.remark
        };
        const response = await this.$axios.post('/user/updateProfile', {
          userData: userData,
          userID: this.userID
        });
        if (response.data.status === 'SUCCESS'){
          alert('用户信息更新成功');
          location.reload();
        }else if (response.data.status === 'ERROR'){
          alert("用户信息更新失败\n错误信息为:" + response.data.errorMessage);
        }
      } catch (error) {
        console.error('更新余额失败:', error);
      }
    },
  },
};
</script>

<style scoped>
/* 基础样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

.user-profile {
  max-width: 900px;
  margin: 30px auto;
  padding: 0 20px;
}

.title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;
  position: relative;
  padding-bottom: 15px;
}

.title:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(to right, #409eff, #67c23a);
  border-radius: 3px;
}

.profile-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 30px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-info,
.password-section,
.other-info-section {
  margin-bottom: 30px;
  padding: 25px;
  border: 1px solid #eaeaea;
  border-radius: 10px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.user-info:hover,
.password-section:hover,
.other-info-section:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #333;
  font-size: 20px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #eee;
  position: relative;
}

h2:after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 2px;
  background-color: #409eff;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
  font-size: 16px;
}

.info-item strong {
  width: 120px;
  color: #606266;
  font-weight: 600;
}

.info-item span {
  color: #333;
  font-weight: 500;
}

.input-field {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
}

.input-field:focus {
  border-color: #409eff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.balance-input {
  width: 200px;
  margin-right: 15px;
  font-weight: 600;
  color: #409eff;
}

.form-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.form-row label {
  color: #606266;
  text-align: right;
  font-weight: 600;
}

.form-row textarea {
  min-height: 100px;
  resize: vertical;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.primary-btn {
  background-color: #409eff;
  color: white;
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
}

.primary-btn:hover {
  background-color: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(64, 158, 255, 0.4);
}

.primary-btn:active {
  transform: translateY(0);
}

.success-btn {
  background-color: #67c23a;
  color: white;
  box-shadow: 0 3px 8px rgba(103, 194, 58, 0.3);
  width: 100%;
  margin-top: 10px;
}

.success-btn:hover {
  background-color: #85ce61;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(103, 194, 58, 0.4);
}

.success-btn:active {
  transform: translateY(0);
}

.loading {
  text-align: center;
  color: #909399;
  font-size: 18px;
  padding: 50px 0;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  position: relative;
}

.loading:before {
  content: '';
  display: block;
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.password-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-profile {
    padding: 0 15px;
  }
  
  .profile-container {
    padding: 20px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    text-align: left;
  }

  .form-row label {
    text-align: left;
    margin-bottom: 5px;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .info-item strong {
    width: 100%;
    margin-bottom: 5px;
  }

  .balance-input {
    width: 100%;
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .user-info,
  .password-section,
  .other-info-section {
    padding: 20px 15px;
  }
}
</style>