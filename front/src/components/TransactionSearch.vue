<template>
  <div class="transaction-page">
    <!-- 搜索区域 -->
    <div class="search-section">
      <select v-model="searchType">
        <option value="type">交易类型</option>
        <option value="code">股票代码</option>
        <option value="name">股票名称</option>
      </select>
      <input
          v-if="searchType !== 'type'"
          type="text"
          v-model="searchKeyword"
          placeholder="输入搜索关键词"
      />
      <select v-else v-model="searchKeyword">
        <option value="">全部</option>
        <option value="0">买入</option>
        <option value="1">卖出</option>
      </select>
      <button @click="searchTransactions">搜索</button>
    </div>

    <!-- 交易记录列表 -->
    <div class="transaction-list">
      <div
          v-for="transaction in filteredTransactions"
          :key="transaction.stock_code + transaction.transaction_type"
          class="transaction-item"
      >
        <div class="transaction-info">
          <p>交易类型: {{ transaction.transaction_type === 0 ? '买入' : '卖出' }}</p>
          <p>股票代码: {{ transaction.stock_code }}</p>
          <p>股票名称: {{ transaction.stock_name }}</p>
          <p>交易数量: {{ transaction.transaction_number }}</p>
          <p>交易单价: {{ transaction.per_price }} 元</p>
          <p>收益: {{ transaction.gains }} 元</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TransactionPage',
  data() {
    return {
      searchType: 'type', // 搜索类型：type（交易类型）、code（股票代码）、name（股票名称）
      searchKeyword: '', // 搜索关键词
      transactionList: [], // 存储从后端获取的交易记录
      filteredTransactions: [], // 过滤后的交易记录
    };
  },
  async mounted() {
    await this.fetchTransactionData();
  },
  methods: {
    // 获取交易记录数据
    async fetchTransactionData() {
      const userID = localStorage.getItem('userID');
      if (!userID) {
        alert('无法获取用户ID，请重新登录');
        return;
      }

      try {
        const response = await this.$axios.get('/user/getTransactionRecords', {
          params: { userID: userID },
        });

        if (response.data.status === 'SUCCESS') {
          this.transactionList = response.data.stockTransactionList;
          this.filteredTransactions = this.transactionList; // 初始显示全部数据
        } else {
          alert('获取交易记录失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },

    // 根据搜索条件过滤交易记录
    searchTransactions() {
      if (!this.searchKeyword) {
        this.filteredTransactions = this.transactionList;
        return;
      }

      this.filteredTransactions = this.transactionList.filter((transaction) => {
        if (this.searchType === 'type') {
          return transaction.transaction_type.toString() === this.searchKeyword;
        } else if (this.searchType === 'code') {
          return transaction.stock_code.includes(this.searchKeyword);
        } else if (this.searchType === 'name') {
          return transaction.stock_name.includes(this.searchKeyword);
        }
      });
    },
  },
};
</script>

<style scoped>
/* 页面基础样式 */
.transaction-page {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

/* 搜索区域样式 */
.search-section {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.search-section select,
.search-section input {
  padding: 8px;
  margin-right: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.search-section button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-section button:hover {
  background-color: #0056b3;
}

/* 交易记录列表样式 */
.transaction-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.transaction-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
}

.transaction-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #555;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-section select,
  .search-section input,
  .search-section button {
    width: 100%;
    margin-bottom: 10px;
  }

  .transaction-list {
    grid-template-columns: 1fr;
  }
}
</style>