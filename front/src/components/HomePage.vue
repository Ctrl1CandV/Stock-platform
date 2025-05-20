<template>
  <div class="stock-page">
    <!-- 搜索区域 -->
    <div class="search-container">
      <div class="search-section">
        <select v-model="searchType">
          <option value="code">股票代码</option>
          <option value="name">股票名称</option>
        </select>
        <input type="text" v-model="searchKeyword" placeholder="输入搜索关键词">
        <button @click="searchStocks">搜索</button>
      </div>
    </div>

    <!-- 股票列表 -->
    <div class="stock-list">
      <div v-for="stock in paginatedStocks" :key="stock.code" class="stock-item">
        <div class="stock-info">
          <p v-if="stock.stockCode && stock.stockName">名称:{{ stock.stockName }} 代码:{{ stock.stockCode }}</p>
          <p v-if="stock.industry && stock.area">行业:{{ stock.industry }} 地域:{{ stock.area }}</p>
          <p v-if="stock.listDate">上市时间:{{ stock.listDate }} <button v-if="!isManager"
              @click="addFavoriteStock(stock.stockCode)" class="favorite-btn">加入自选股</button></p>
        </div>
        <div class="stock-actions">
          <button v-if="!isManager" @click="openBuyModal(stock)">买入</button>
          <button @click="toStock(stock)">详情</button>
        </div>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="currentPage === 1" @click="currentPage--"
        :class="{ 'disabled': currentPage === 1 }">上一页</button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage === totalPages" @click="currentPage++"
        :class="{ 'disabled': currentPage === totalPages }">下一页</button>
    </div>

    <!-- 市场数据展示区域 -->
    <div class="market-data-container" v-if="Object.keys(significantIndex).length > 0">
      <!-- 指数信息 -->
      <div class="index-container">
        <h3>市场指数</h3>
        <div class="index-list">
          <div v-for="(value, name) in significantIndex" :key="name" class="index-item"
            :class="{ 'positive': value > 0, 'negative': value < 0 }">
            <span class="index-name">{{ name }}</span>
            <span class="index-value">{{ value > 0 ? '+' : '' }}{{ value }}%</span>
          </div>
        </div>
      </div>

      <!-- 交易前十 -->
      <div class="top-stocks-container"
        v-if="Object.keys(ShanghaiTop10).length > 0 && Object.keys(ShenzhenTop10).length > 0">
        <div class="top-stocks-section">
          <h3>沪市交易前十</h3>
          <div class="top-stocks-list">
            <div v-for="(amount, name) in ShanghaiTop10" :key="name" class="top-stock-item">
              <span class="stock-name">{{ name }}</span>
              <span class="stock-amount">{{ amount }}</span>
            </div>
          </div>
        </div>
        <div class="top-stocks-section">
          <h3>深市交易前十</h3>
          <div class="top-stocks-list">
            <div v-for="(amount, name) in ShenzhenTop10" :key="name" class="top-stock-item">
              <span class="stock-name">{{ name }}</span>
              <span class="stock-amount">{{ amount }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 新闻信息 -->
      <div class="news-container">
        <h3>最新财经动态</h3>
        <div class="news-list">
          <div v-for="(content, datetime) in newsInformation" :key="datetime" class="news-item">
            <div class="news-time">{{ datetime }}</div>
            <div class="news-content">{{ content }}</div>
          </div>
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
      buyQuantity: 0,
      currentPage: 1,
      itemsPerPage: 9,
      ShanghaiTop10: {},
      ShenzhenTop10: {},
      newsInformation: {},
      significantIndex: {},
      isManager: false,
    }
  },
  async mounted() {
    this.loadHomePageData();
    this.checkUserRole();
  },
  computed: {
    // 计算当前页显示的股票
    paginatedStocks() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.stockList.slice(start, end);
    },
    // 计算总页数
    totalPages() {
      return Math.ceil(this.stockList.length / this.itemsPerPage);
    }
  },
  methods: {
    checkUserRole() {
      const currentPath = this.$route.path;
      const managerID = localStorage.getItem('managerID');
      this.isManager = currentPath.startsWith('/manager') || (managerID != null);
    },
    async loadHomePageData() {
      try {
        const response = await this.$axios.get('/platform/loadHomePageData');

        if (response.data.status === 'SUCCESS') {
          this.ShanghaiTop10 = response.data.ShanghaiTop10;
          this.ShenzhenTop10 = response.data.ShenzhenTop10;
          this.newsInformation = response.data.newsInformation;
          this.significantIndex = response.data.significantIndex;
        } else {
          this.$message.error('搜索页面加载失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    async addFavoriteStock(stockCode) {
      try {
        const response = await this.$axios.post('/platform/addFavoriteStock', {
          userID: localStorage.getItem('userID'),
          stockCode: stockCode
        });

        if (response.data.status === 'SUCCESS') {
          this.$message.success('添加自选股成功');
        } else {
          this.$message.error('添加自选股失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    async toStock(stock) {
      // 更新数据
      try {
        const response = await this.$axios.post('/platform/updateAnnualDailyQuotes', { stockCode: stock.stockCode });
        if (response.data.status === 'SUCCESS') {
          if (this.$route.path !== '/user/stock') {
            this.$router.push('/user/stock');
          }
          localStorage.setItem('stockCode', stock.stockCode);
          localStorage.setItem('stockName', stock.stockName);
        } else {
          this.$message.error('跳转失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    async searchStocks() {
      try {
        if (!this.searchKeyword) {
          this.$message.warning("关键词不得为空");
          return null;
        }

        if (this.searchType === 'code') {
          const response = await this.$axios.get('/platform/queryStockByCode', {
            params: { stockCode: this.searchKeyword }
          });
          if (response.data.status === 'SUCCESS') {
            this.stockList = response.data.stockInformation;
            this.currentPage = 1;
          } else if (response.data.status === 'ERROR') {
            this.$message.error("查询失败:" + response.data.errorMessage);
          }
        } else if (this.searchType === 'name') {
          const response = await this.$axios.get('/platform/queryStockByName', {
            params: { stockName: this.searchKeyword }
          });
          if (response.data.status === 'SUCCESS') {
            this.stockList = response.data.stockInformationList;
            this.currentPage = 1;
          } else if (response.data.status === 'ERROR') {
            this.$message.error("查询失败:" + response.data.errorMessage);
          }
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async openBuyModal(stock) {
      try {
        const response = await this.$axios.get('/platform/isTrading', {
          params: { stockCode: stock.stockCode }
        });
        if (response.data.status === 'SUCCESS') {
          this.currentStock = stock;
          this.currentPrice = response.data.perPrice;
          this.showBuyModal = true;
        } else if (response.data.status === 'ERROR') {
          this.$message.warning(response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async confirmBuy() {
      const userID = localStorage.getItem('userID');
      if (!userID) {
        this.$message.warning('当前身份信息错误，无法购买');
        return null;
      }

      if (this.buyQuantity <= 0) {
        this.$message.warning('无效的买入金额');
        return null;
      }

      try {
        await this.$confirm(
          `确认买入${this.currentStock.stockName}股票${this.buyQuantity}支吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        );
      } catch { return null; }

      try {
        const response = await this.$axios.post('/platform/buyStock', {
          userID: userID,
          stockCode: this.currentStock.stockCode,
          buyNumber: this.buyQuantity
        });
        if (response.data.status === 'SUCCESS') {
          this.$message.success('买入成功，购买金额为' + response.data.amountSpent);
          this.showBuyModal = false;
        } else if (response.data.status === 'ERROR') {
          this.$message.error('买入失败:' + response.data.errorMessage);
        }
      } catch (error) {
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
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

.stock-page {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-container {
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 20px 0 30px;
  margin-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

/* 市场数据展示区域样式 */
.market-data-container {
  margin-bottom: 40px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 25px;
}

.section-title {
  margin-bottom: 20px;
  color: #333;
  font-size: 22px;
  font-weight: 600;
  border-bottom: 2px solid #eee;
  padding-bottom: 12px;
}

/* 指数信息样式 */
.index-container {
  background-color: #f9f9f9;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.index-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.index-container h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  padding-bottom: 12px;
}

.index-list {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
}

.index-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 20px;
  border-radius: 10px;
  min-width: 150px;
  margin: 8px;
  background-color: #fff;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease;
}

.index-item:hover {
  transform: scale(1.05);
}

.index-name {
  font-weight: bold;
  margin-bottom: 10px;
  font-size: 16px;
}

.index-value {
  font-size: 22px;
  font-weight: 600;
}

.positive {
  color: #f56c6c;
}

.negative {
  color: #67c23a;
}

/* 交易前十样式 */
.top-stocks-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

.top-stocks-section {
  background-color: #f9f9f9;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.top-stocks-section:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.top-stocks-section h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  padding-bottom: 12px;
}

.top-stocks-list {
  display: flex;
  flex-direction: column;
}

.top-stock-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 15px;
  border-bottom: 1px dashed #eee;
  transition: background-color 0.2s ease;
}

.top-stock-item:hover {
  background-color: #f0f7ff;
}

.top-stock-item:last-child {
  border-bottom: none;
}

.stock-name {
  font-weight: bold;
  font-size: 15px;
}

.stock-amount {
  color: #409eff;
  font-weight: 600;
  font-size: 15px;
}

/* 新闻信息样式 */
.news-container {
  background-color: #f9f9f9;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.news-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.news-container h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  padding-bottom: 12px;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.news-item {
  background-color: #fff;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.news-item:hover {
  transform: translateX(5px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.news-time {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.news-content {
  font-size: 15px;
  line-height: 1.6;
  color: #333;
}

.favorite-btn {
  padding: 6px 12px;
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.favorite-btn:hover {
  background-color: #f57c00;
  transform: scale(1.05);
}

.favorite-btn:active {
  transform: scale(0.95);
}

.search-section {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 60%;
  max-width: 800px;
}

.search-section select {
  width: 150px;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: border-color 0.3s;
}

.search-section select:focus {
  border-color: #409eff;
  outline: none;
}

.search-section input {
  flex: 1;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: border-color 0.3s;
}

.search-section input:focus {
  border-color: #409eff;
  outline: none;
}

.search-section button {
  width: 120px;
  padding: 12px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
}

.search-section button:hover {
  background-color: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(64, 158, 255, 0.4);
}

.search-section button:active {
  transform: translateY(0);
}

.stock-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  margin-top: 20px;
}

.stock-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stock-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stock-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.stock-info p {
  width: 100%;
  font-size: 15px;
  color: #555;
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}

.stock-info p:last-child {
  border-bottom: none;
}

.stock-info p span {
  font-weight: bold;
}

.stock-actions {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  margin-top: 15px;
}

.stock-actions button {
  flex: 1;
  padding: 10px 14px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(40, 167, 69, 0.3);
}

.stock-actions button:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(40, 167, 69, 0.4);
}

.stock-actions button:active {
  transform: translateY(0);
}

.stock-actions button:last-child {
  background-color: #007bff;
  box-shadow: 0 3px 8px rgba(0, 123, 255, 0.3);
}

.stock-actions button:last-child:hover {
  background-color: #0056b3;
  box-shadow: 0 5px 12px rgba(0, 123, 255, 0.4);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  gap: 20px;
}

.pagination button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(0, 123, 255, 0.3);
}

.pagination button:hover:not(.disabled) {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(0, 123, 255, 0.4);
}

.pagination button:active:not(.disabled) {
  transform: translateY(0);
}

.pagination button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  box-shadow: none;
}

.page-info {
  font-size: 16px;
  font-weight: bold;
  color: #555;
}

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
}

.modal-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 12px;
  width: 450px;
  max-width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-content h3 {
  font-size: 20px;
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

.modal-content p {
  font-size: 18px;
  margin-bottom: 20px;
  text-align: center;
  color: #555;
}

.modal-content input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 16px;
  margin-bottom: 25px;
  transition: border-color 0.3s;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.modal-content input:focus {
  border-color: #409eff;
  outline: none;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.modal-actions button {
  flex: 1;
  padding: 12px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.3s;
}

.modal-actions button:first-child {
  background-color: #28a745;
  color: white;
  box-shadow: 0 3px 8px rgba(40, 167, 69, 0.3);
}

.modal-actions button:first-child:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(40, 167, 69, 0.4);
}

.modal-actions button:first-child:active {
  transform: translateY(0);
}

.modal-actions button:last-child {
  background-color: #f56c6c;
  color: white;
  box-shadow: 0 3px 8px rgba(245, 108, 108, 0.3);
}

.modal-actions button:last-child:hover {
  background-color: #e64242;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(245, 108, 108, 0.4);
}

.modal-actions button:last-child:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .search-section {
    width: 95%;
    flex-direction: column;
  }

  .search-section select,
  .search-section input,
  .search-section button {
    width: 100%;
  }

  .stock-list {
    grid-template-columns: 1fr;
  }

  .stock-item {
    padding: 15px;
  }

  .top-stocks-container {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 90%;
    padding: 20px;
  }
}
</style>