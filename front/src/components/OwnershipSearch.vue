<template>
  <div class="ownership-page">
    <!-- 搜索区域 -->
    <div class="search-section">
      <select v-model="searchType">
        <option value="code">股票代码</option>
        <option value="name">股票名称</option>
      </select>
      <input type="text" v-model="searchKeyword" placeholder="输入搜索关键词">
      <button @click="searchOwnerships">搜索</button>
    </div>

    <!-- 持有股列表 -->
    <div class="ownership-list">
      <div v-for="ownership in filteredOwnerships" :key="ownership.stock_code" class="ownership-item">
        <div class="ownership-info">
          <p v-if="ownership.stock_code">代码: {{ ownership.stock_code }}</p>
          <p v-if="ownership.stock_name">名称: {{ ownership.stock_name }}</p>
          <p v-if="ownership.hold_number">持有数量: {{ ownership.hold_number }}</p>
          <p v-if="ownership.purchase_per_price">购入价格: {{ ownership.purchase_per_price }}</p>
        </div>
        <div class="ownership-actions">
          <button @click="openSellModal(ownership)">卖出</button>
          <button @click="toStock(ownership)">详情</button>
        </div>
      </div>
    </div>

    <!-- 卖出模态窗口 -->
    <div v-if="showSellModal" class="modal-mask">
      <div class="modal-content">
        <h3>{{ currentOwnership.stock_name }} ({{ currentOwnership.stock_code }})</h3>
        <p>当前持有: {{ currentOwnership.hold_number }} 股</p>
        <p>购入价格: {{ currentOwnership.purchase_per_price }} 元</p>
        <p>最新价格:{{ currentPrice }}</p>
        <input type="number" v-model.number="sellQuantity" placeholder="输入卖出数量" min="1" :max="currentOwnership.hold_number">
        <div class="modal-actions">
          <button @click="confirmSell">确认</button>
          <button @click="showSellModal = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  name: 'OwnershipPage',
  data() {
    return {
      searchType: 'code',
      searchKeyword: '',
      ownershipList: [], // 存储持有股记录
      filteredOwnerships: [], // 用于过滤后的持有股数据
      showSellModal: false,
      currentOwnership: {},
      currentPrice: null,
      sellQuantity: 0
    };
  },
  mounted() {
    this.fetchOwnershipData();
  },
  methods: {
    async toStock(ownership) {
      // 更新数据
      try {
        const response = await this.$axios.post('/platform/updateAnnualDailyQuotes', { stockCode: ownership.stock_code});
        if (response.data.status === 'SUCCESS') {
          this.$router.push('/user/stock');
          localStorage.setItem('stockCode', ownership.stock_code);
          localStorage.setItem('stockName', ownership.stock_name);
        } else {
          alert('跳转失败: ' + response.data.errorMessage);
        }
      }catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    async fetchOwnershipData() {
      const userID = localStorage.getItem('userID');
      if (!userID) {
        alert('无法获取用户ID，请重新登录');
        return;
      }

      try {
        const response = await this.$axios.get('/user/getStockOwnership', {
          params: { userID: userID }
        });

        if (response.data.status === 'SUCCESS') {
          this.ownershipList = response.data.stockOwnershipList;
          this.filteredOwnerships = this.ownershipList; // 初始时不进行过滤，显示全部
        } else {
          alert('获取持有股失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    searchOwnerships() {
      if (!this.searchKeyword) {
        this.filteredOwnerships = this.ownershipList;
        return;
      }

      this.filteredOwnerships = this.ownershipList.filter(ownership => {
        if (this.searchType === 'code') {
          return ownership.stock_code.includes(this.searchKeyword);
        } else if (this.searchType === 'name') {
          return ownership.stock_name.includes(this.searchKeyword);
        }
      });
    },
    async openSellModal(ownership) {
      try{
        const response = await this.$axios.get('/platform/isTrading', {
          params: { stockCode: ownership.stock_code }
        });
        if (response.data.status === 'SUCCESS'){
          this.currentOwnership = ownership;
          this.currentPrice = response.data.perPrice;
          this.showSellModal = true;
        }else if (response.data.status === 'ERROR'){
          alert(response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    async confirmSell() {
      if (this.sellQuantity <= 0 || this.sellQuantity > this.currentOwnership.hold_number) {
        alert('无效的卖出数量');
        return;
      }

      const userID = localStorage.getItem('userID');
      if (!userID) {
        alert('当前身份信息错误，无法卖出');
        return;
      }

      try {
        const response = await this.$axios.post('/platform/sellStock', {
          ownershipID: this.currentOwnership.ownership_id,
          sellNumber: this.sellQuantity
        });

        if (response.data.status === 'SUCCESS') {
          alert('卖出成功，卖出收益为 ' + response.data.gain);
          this.showSellModal = false;
          this.fetchOwnershipData(); // 更新持有股数据
        } else {
          alert('卖出失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    }
  }
};
</script>

<style scoped>
/* 样式基础 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

.ownership-page {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

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

/* 持有股列表样式 */
.ownership-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.ownership-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
}

.ownership-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.ownership-info p {
  width: 100%;
  font-size: 14px;
  color: #555;
  display: flex;
  justify-content: space-between;
}

.ownership-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.ownership-actions button {
  padding: 8px 14px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.ownership-actions button:hover {
  background-color: #218838;
}

.ownership-actions button:last-child {
  background-color: #007bff;
}

.ownership-actions button:last-child:hover {
  background-color: #0056b3;
}

/* 卖出模态窗口 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  max-width: 100%;
}

.modal-content h3 {
  font-size: 18px;
  margin-bottom: 15px;
  text-align: center;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
}

.modal-actions button {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.modal-actions button:first-child {
  background-color: #28a745;
  color: white;
}

.modal-actions button:first-child:hover {
  background-color: #218838;
}

.modal-actions button:last-child {
  background-color: #ccc;
}

.modal-actions button:last-child:hover {
  background-color: #999;
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

  .ownership-list {
    grid-template-columns: 1fr;
  }

  .ownership-item {
    padding: 15px;
  }
}
</style>
