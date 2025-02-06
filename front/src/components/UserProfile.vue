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
.user-profile {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: 600;
}

.profile-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.user-info,
.password-section,
.other-info-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid #eee;
  border-radius: 8px;
}

h2 {
  color: #34495e;
  font-size: 1.3rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.info-item strong {
  width: 120px;
  color: #666;
}

.input-field {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.input-field:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.balance-input {
  width: 200px;
  margin-right: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.form-row label {
  color: #666;
  text-align: right;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.primary-btn {
  background-color: #3498db;
  color: white;
}

.primary-btn:hover {
  background-color: #2980b9;
}

.success-btn {
  background-color: #27ae60;
  color: white;
}

.success-btn:hover {
  background-color: #219a52;
}

.loading {
  text-align: center;
  color: #7f8c8d;
  font-size: 1.2rem;
}

.password-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    text-align: left;
  }

  .form-row label {
    text-align: left;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .balance-input {
    width: 100%;
    margin-right: 0;
    margin-bottom: 1rem;
  }
}
</style>