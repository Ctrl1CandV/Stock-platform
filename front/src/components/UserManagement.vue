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
    name: 'UserManagement',
    data() {
      return {
        searchKeyword: '', 
        userList: [], 
        filteredUsers: [], 
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
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.search-section:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.search-section input {
  flex: 1;
  padding: 0.8rem 1.2rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
}

.search-section input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.search-section button {
  padding: 0.8rem 1.5rem;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
}

.search-section button:hover {
  background: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(64, 158, 255, 0.4);
}

.search-section button:active {
  transform: translateY(0);
}

.user-list {
  display: grid;
  gap: 1.5rem;
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

.user-item {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.user-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #409eff;
}

.user-info p {
  margin: 0.8rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #f0f0f0;
}

.user-info p:last-child {
  border-bottom: none;
  padding-top: 1rem;
  margin-top: 0.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info p strong {
  min-width: 80px;
  color: #606266;
  font-weight: 600;
}

.user-info input[type="number"] {
  padding: 0.6rem 0.8rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  width: 150px;
  transition: all 0.3s ease;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
}

.user-info input[type="number"]:focus {
  border-color: #409eff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  margin-left: 0.8rem;
}

button:disabled {
  background: #f0f0f0 !important;
  color: #a0a0a0 !important;
  cursor: not-allowed;
  box-shadow: none;
}

button[disabled] {
  opacity: 0.6;
}

button:not([disabled]):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

button:not([disabled]):active {
  transform: translateY(0);
}

/* 修改余额按钮 */
button:nth-of-type(1) {
  background: #67c23a;
  color: white;
  box-shadow: 0 2px 5px rgba(103, 194, 58, 0.3);
}

button:nth-of-type(1):hover {
  background: #85ce61;
  box-shadow: 0 4px 8px rgba(103, 194, 58, 0.4);
}

/* 删除用户按钮 */
button:nth-of-type(2) {
  background: #f56c6c;
  color: white;
  box-shadow: 0 2px 5px rgba(245, 108, 108, 0.3);
}

button:nth-of-type(2):hover {
  background: #f78989;
  box-shadow: 0 4px 8px rgba(245, 108, 108, 0.4);
}

/* 状态标签 */
.status-tag {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 600;
}

.status-active {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.status-inactive {
  background-color: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

/* 斑马条纹效果 */
.user-item:nth-child(odd) {
  background: #f9fafc;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-page {
    padding: 1rem;
  }
  
  .search-section {
    flex-direction: column;
    padding: 1rem;
  }
  
  .search-section input {
    width: 100%;
  }
  
  .search-section button {
    width: 100%;
  }
  
  .user-info p {
    flex-wrap: wrap;
  }
  
  .user-info p:last-child {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .user-info input {
    width: 100%;
  }
  
  button {
    width: 100%;
    margin: 0.5rem 0 0 0;
  }
}

/* 添加加载动画 */
@keyframes shimmer {
  0% {
    background-position: -468px 0;
  }
  100% {
    background-position: 468px 0;
  }
}

.loading {
  animation: shimmer 1.5s infinite linear;
  background: linear-gradient(to right, #f6f7f8 8%, #edeef1 18%, #f6f7f8 33%);
  background-size: 800px 104px;
  border-radius: 8px;
}
</style>