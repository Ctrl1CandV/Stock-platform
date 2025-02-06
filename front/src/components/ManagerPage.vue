<template>
  <div class="admin-page">
    <!-- 搜索区域 -->
    <div class="search-section">
      <input
          v-model="searchKeyword"
          type="text"
          placeholder="输入用户名搜索"
      />
      <button @click="searchUsers">搜索</button>
    </div>

    <!-- 用户信息展示区域 -->
    <div class="user-list">
      <div
          v-for="user in filteredUsers"
          :key="user.userID"
          class="user-item"
      >
        <div class="user-info">
          <p>用户ID: {{ user.userID }}</p>
          <p>用户名: {{ user.userName }}</p>
          <p>邮箱: {{ user.userEmail }}</p>
          <p>余额:
            <input
                v-model.number="user.userBalance"
                type="number"
                :disabled="user.status === false"
                placeholder="输入新余额"
            />
            <button
                :disabled="user.status === false"
                @click="updateBalance(user.userID, user.userBalance)"
            >修改余额</button>
          </p>
          <p>
            账号状态: {{ user.status ? '启用' : '禁用' }}
            <button
                :disabled="user.status === false"
                @click="deleteUser(user.userID)"
            >删除用户</button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPage',
  data() {
    return {
      searchKeyword: '', // 搜索关键词
      userList: [], // 存储所有用户数据
      filteredUsers: [], // 根据搜索条件过滤后的用户数据
    };
  },
  async mounted() {
    await this.fetchUserData();
  },
  methods: {
    // 获取用户数据
    async fetchUserData() {
      try {
        const response = await this.$axios.get('/manager/queryUsers');
        if (response.data.status === 'SUCCESS') {
          this.userList = response.data.userList;
          this.filteredUsers = this.userList; // 初始显示全部数据
        } else {
          alert('获取用户数据失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },

    // 根据用户名搜索用户
    searchUsers() {
      if (!this.searchKeyword) {
        this.filteredUsers = this.userList;
        return;
      }

      this.filteredUsers = this.userList.filter((user) =>
          user.userName.includes(this.searchKeyword)
      );
    },

    // 修改用户余额
    async updateBalance(userID, newBalance) {
      try {
        const response = await this.$axios.post('/manager/editUserBalance', {
          userID: userID,
          newBalance: newBalance,
        });

        if (response.data.status === 'SUCCESS') {
          alert('余额修改成功');
        } else {
          alert('余额修改失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },

    // 删除用户
    async deleteUser(userID) {
      if (confirm('确定要删除此用户吗？')) {
        try {
          const response = await this.$axios.post('/manager/deleteUser', { userID });
          if (response.data.status === 'SUCCESS') {
            alert('删除成功');
            this.fetchUserData(); // 刷新用户列表
          } else {
            alert('删除失败: ' + response.data.errorMessage);
          }
        } catch (error) {
          alert('请求失败: ' + error.message);
        }
      }
    },
  },
};
</script>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.search-section input {
  flex: 1;
  padding: 0.8rem 1.2rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.search-section input:focus {
  outline: none;
  border-color: #4a90e2;
}

.search-section button {
  padding: 0.8rem 1.5rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.search-section button:hover {
  background: #357abd;
}

.user-list {
  display: grid;
  gap: 1.5rem;
}

.user-item {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.user-item:hover {
  transform: translateY(-2px);
}

.user-info p {
  margin: 0.8rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info input[type="number"] {
  padding: 0.6rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  width: 120px;
  transition: border-color 0.3s ease;
}

.user-info input[type="number"]:focus {
  border-color: #4a90e2;
  outline: none;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

button:disabled {
  background: #f0f0f0 !important;
  color: #a0a0a0 !important;
  cursor: not-allowed;
}

button[disabled] {
  opacity: 0.6;
}

/* 不同操作按钮颜色 */
button {
  margin-left: 0.5rem;
}

button:not([disabled]):hover {
  transform: translateY(-1px);
}

/* 修改余额按钮 */
button:nth-of-type(1) {
  background: #00c853;
  color: white;
}

/* 删除用户按钮 */
button:nth-of-type(2) {
  background: #ff5252;
  color: white;
}

/* 状态标签样式 */
.user-info p:last-child {
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-info p {
    flex-wrap: wrap;
  }

  .user-info input {
    width: 100%;
  }

  button {
    width: 100%;
    margin-top: 0.5rem;
  }
}

/* 斑马条纹效果 */
.user-item:nth-child(odd) {
  background: #f8f9ff;
}

/* 数字输入框箭头样式 */
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type=number] {
  -moz-appearance: textfield;
}
</style>
