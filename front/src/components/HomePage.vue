<template>
  <div class="stock-page">
    <!-- 搜索区域 -->
    <div class="search-section">
      <select v-model="searchType">
        <option value="code">股票代码</option>
        <option value="name">股票名称</option>
      </select>
      <input type="text" v-model="searchKeyword" placeholder="输入搜索关键词">
      <button @click="searchStocks">搜索</button>
    </div>

    <!-- 股票列表 -->
    <div class="stock-list">
      <div v-for="stock in stockList" :key="stock.code" class="stock-item">
        <div class="stock-info">
          <p v-if="stock.stockCode">代码:{{ stock.stockCode }}</p>
          <p v-if="stock.stockName">名称:{{ stock.stockName }}</p>
          <p v-if="stock.industry">行业:{{ stock.industry }}</p>
          <p v-if="stock.area">地域:{{ stock.area }}</p>
          <p v-if="stock.listDate">上市时间:{{ stock.listDate }}</p>
        </div>
        <div class="stock-actions">
          <button @click="openBuyModal(stock)">买入</button>
          <button @click="toStock(stock)">详情</button>
        </div>
      </div>
    </div>

    <!-- 买入模态窗口 -->
    <div v-if="showBuyModal" class="modal-mask">
      <div class="modal-content">
        <h3>{{ currentStock.stockName }} ({{ currentStock.stockCode }})</h3>
        <p>最新价格:{{ currentPrice }}</p>
        <input type="number" v-model.number="buyQuantity" placeholder="输入购买数量">
        <div class="modal-actions">
          <button @click="confirmBuy">确认</button>
          <button @click="showBuyModal = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StockPage',
  data() {
    return {
      searchType: 'code',
      searchKeyword: '',
      stockList: [],
      showBuyModal: false,
      currentStock: {},
      currentPrice: null,
      buyQuantity: 0
    }
  },
  methods: {
    async toStock(stock) {
      // 更新数据
      try {
        const response = await this.$axios.post('/platform/updateAnnualDailyQuotes', { stockCode: stock.stockCode});
        if (response.data.status === 'SUCCESS') {
          this.$router.push('/user/stock');
          localStorage.setItem('stockCode', stock.stockCode);
          localStorage.setItem('stockName', stock.stockName);
        } else {
          alert('跳转失败: ' + response.data.errorMessage);
        }
      }catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    async searchStocks() {
      try {
        if (!this.searchKeyword){
          alert("关键词不得为空");
          return null;
        }

        if (this.searchType === 'code'){
          const response = await this.$axios.get('/platform/queryStockByCode', {
            params: { stockCode: this.searchKeyword }
          });
          if (response.data.status === 'SUCCESS'){
            this.stockList = response.data.stockInformation;
            alert('查询成功');
          }else if (response.data.status === 'ERROR'){
            alert("查询失败:" + response.data.errorMessage);
          }
        }else if (this.searchType === 'name'){
          const response = await this.$axios.get('/platform/queryStockByName', {
            params: { stockName: this.searchKeyword }
          });
          if (response.data.status === 'SUCCESS'){
            this.stockList = response.data.stockInformationList;
            alert('查询成功');
          }else if (response.data.status === 'ERROR'){
            alert("查询失败:" + response.data.errorMessage);
          }
        }
      }catch (error) {
        alert(error.message);
      }
    },
    async openBuyModal(stock) {
      try{
        const response = await this.$axios.get('/platform/isTrading', {
          params: { stockCode: stock.stockCode }
        });
        if (response.data.status === 'SUCCESS'){
          this.currentStock = stock;
          this.currentPrice = response.data.perPrice;
          this.showBuyModal = true;
        }else if (response.data.status === 'ERROR'){
          alert(response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    async confirmBuy() {
      const userID = localStorage.getItem('userID');
      if (!userID){
        alert('当前身份信息错误，无法购买');
        return null;
      }

      if (this.buyQuantity < 0){
        alert('无效的买入金额');
        return null;
      }

      try {
        const response = await this.$axios.post('/platform/buyStock', {
          userID: userID,
          stockCode: this.currentStock.stockCode,
          buyNumber: this.buyQuantity
        });
        if (response.data.status === 'SUCCESS'){
          alert('买入成功，购买金额为' + response.data.amountSpent);
          this.showBuyModal = false;
        }else if (response.data.status === 'ERROR'){
          alert('买入失败:' + response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    }
  }
}
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

.stock-page {
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

/* 股票列表样式 */
.stock-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.stock-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
}

.stock-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.stock-info p {
  width: 100%;
  font-size: 14px;
  color: #555;
  display: flex;
  justify-content: space-between;
}

.stock-info p span {
  font-weight: bold;
}

.stock-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.stock-actions button {
  padding: 8px 14px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.stock-actions button:hover {
  background-color: #218838;
}

.stock-actions button:last-child {
  background-color: #007bff;
}

.stock-actions button:last-child:hover {
  background-color: #0056b3;
}

/* 买入模态窗口 */
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

.modal-content p {
  font-size: 16px;
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

  .stock-list {
    grid-template-columns: 1fr;
  }

  .stock-item {
    padding: 15px;
  }
}
</style>