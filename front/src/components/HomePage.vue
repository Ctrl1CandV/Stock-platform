<template>
  <div class="stock-platform">
    <!-- 顶部导航栏 -->
    <div class="top-header">
      <div class="header-content">
        <div class="platform-title">
          <h1>智能股票交易平台</h1>
          <span class="subtitle">专业 · 安全 · 高效</span>
        </div>
        <div class="market-status">
          <div class="status-indicator active"></div>
          <span>市场开放中</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-container">
      <!-- 左侧面板 -->
      <div class="left-panel">
        <!-- 搜索区域 -->
        <div class="search-panel">
          <div class="panel-header">
            <h3>股票搜索</h3>
            <div class="header-line"></div>
          </div>
          <div class="search-form">
            <div class="search-type-selector">
              <button :class="['type-btn', { active: searchType === 'code' }]" @click="searchType = 'code'">
                <i class="icon-code"></i>
                股票代码
              </button>
              <button :class="['type-btn', { active: searchType === 'name' }]" @click="searchType = 'name'">
                <i class="icon-name"></i>
                股票名称
              </button>
            </div>
            <div class="search-input-group">
              <input type="text" v-model="searchKeyword" :placeholder="searchType === 'code' ? '请输入股票代码' : '请输入股票名称'"
                class="search-input" @keyup.enter="searchStocks">
              <button @click="searchStocks" class="search-btn">
                <i class="icon-search"></i>
                搜索
              </button>
            </div>
          </div>
        </div>

        <!-- 市场指数面板 -->
        <div class="index-panel" v-if="Object.keys(significantIndex).length > 0">
          <div class="panel-header">
            <h3>市场指数</h3>
            <div class="header-line"></div>
          </div>
          <div class="index-grid">
            <div v-for="(value, name) in significantIndex" :key="name" class="index-card"
              :class="{ 'positive': value > 0, 'negative': value < 0 }">
              <div class="index-name">{{ name }}</div>
              <div class="index-value">
                <span class="value-number">{{ Math.abs(value).toFixed(2) }}%</span>
                <i :class="value > 0 ? 'icon-up' : 'icon-down'"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- 财经资讯 -->
        <div class="news-panel" v-if="Object.keys(newsInformation).length > 0">
          <div class="panel-header">
            <h3>财经资讯</h3>
            <div class="header-line"></div>
          </div>

          <div class="news-list">
            <div v-for="(content, datetime) in newsInformation" :key="datetime" class="news-item">
              <div class="news-time">
                <i class="icon-time"></i>
                {{ datetime }}
              </div>
              <div class="news-content">{{ content }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间主内容区 -->
      <div class="center-panel">
        <!-- 股票列表 -->
        <div class="stock-list-panel">
          <div class="panel-header">
            <h3>股票列表</h3>
            <div class="header-actions">
              <span class="result-count" v-if="stockList.length > 0">
                共找到 {{ stockList.length }} 只股票
              </span>
            </div>
          </div>

          <div class="stock-grid" v-if="stockList.length > 0">
            <div v-for="stock in paginatedStocks" :key="stock.stockCode" class="stock-card">
              <div class="stock-header">
                <div class="stock-basic-info">
                  <h4 class="stock-name">{{ stock.stockName }}</h4>
                  <span class="stock-code">{{ stock.stockCode }}</span>
                </div>
                <div class="stock-actions">
                  <button v-if="!isManager" @click="addFavoriteStock(stock.stockCode)" class="action-btn favorite-btn"
                    title="加入自选股">
                    <i class="icon-star"></i>
                  </button>
                </div>
              </div>

              <div class="stock-details">
                <div class="detail-row" v-if="stock.industry">
                  <span class="label">行业:</span>
                  <span class="value">{{ stock.industry }}</span>
                </div>
                <div class="detail-row" v-if="stock.area">
                  <span class="label">地域:</span>
                  <span class="value">{{ stock.area }}</span>
                </div>
                <div class="detail-row" v-if="stock.listDate">
                  <span class="label">上市:</span>
                  <span class="value">{{ stock.listDate }}</span>
                </div>
              </div>

              <div class="stock-footer">
                <button v-if="!isManager" @click="openBuyModal(stock)" class="primary-btn buy-btn">
                  <i class="icon-buy"></i>
                  买入
                </button>
                <button @click="toStock(stock)" class="secondary-btn detail-btn">
                  <i class="icon-chart"></i>
                  详情
                </button>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <div class="empty-icon">
              <i class="icon-empty"></i>
            </div>
            <h4>暂无股票数据</h4>
            <p>请使用上方搜索功能查找股票</p>
          </div>

          <!-- 分页器 -->
          <div class="pagination-wrapper" v-if="totalPages > 1">
            <div class="pagination">
              <button :disabled="currentPage === 1" @click="currentPage--" class="page-btn"
                :class="{ disabled: currentPage === 1 }">
                <i class="icon-prev"></i>
                上一页
              </button>

              <div class="page-numbers">
                <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
              </div>

              <button :disabled="currentPage === totalPages" @click="currentPage++" class="page-btn"
                :class="{ disabled: currentPage === totalPages }">
                下一页
                <i class="icon-next"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧信息面板 -->
      <div class="right-panel">
        <!-- 交易排行榜 -->
        <div class="ranking-panel"
          v-if="Object.keys(ShanghaiTop10).length > 0 || Object.keys(ShenzhenTop10).length > 0">
          <div class="panel-header">
            <h3>交易排行</h3>
            <div class="header-line"></div>
          </div>

          <div class="ranking-tabs">
            <button :class="['tab-btn', { active: activeRankingTab === 'shanghai' }]"
              @click="activeRankingTab = 'shanghai'">
              沪市TOP10
            </button>
            <button :class="['tab-btn', { active: activeRankingTab === 'shenzhen' }]"
              @click="activeRankingTab = 'shenzhen'">
              深市TOP10
            </button>
          </div>

          <div class="ranking-list">
            <div v-for="(amount, name, index) in (activeRankingTab === 'shanghai' ? ShanghaiTop10 : ShenzhenTop10)"
              :key="name" class="ranking-item">
              <div class="rank-number" :class="`rank-${index + 1}`">
                {{ index + 1 }}
              </div>
              <div class="stock-info">
                <div class="stock-name">{{ name }}</div>
                <div class="trade-amount">{{ amount }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 买入模态窗口 -->
    <div v-if="showBuyModal" class="modal-overlay" @click="showBuyModal = false">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h3>股票买入</h3>
          <button @click="showBuyModal = false" class="close-btn">
            <i class="icon-close"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="stock-info-display">
            <div class="stock-name-code">
              <h4>{{ currentStock.stockName }}</h4>
              <span class="code">({{ currentStock.stockCode }})</span>
            </div>
            <div class="current-price">
              <span class="price-label">最新价格:</span>
              <span class="price-value">¥{{ currentPrice }}</span>
            </div>
          </div>

          <div class="buy-form">
            <div class="form-group">
              <label>购买数量</label>
              <div class="input-with-unit">
                <input type="number" v-model.number="buyQuantity" placeholder="请输入购买数量" class="quantity-input" min="1">
                <span class="unit">股</span>
              </div>
            </div>

            <div class="estimated-cost" v-if="buyQuantity > 0 && currentPrice">
              <span class="cost-label">预估金额:</span>
              <span class="cost-value">¥{{ (buyQuantity * currentPrice).toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="showBuyModal = false" class="cancel-btn">
            取消
          </button>
          <button @click="confirmBuy" class="confirm-btn">
            <i class="icon-buy"></i>
            确认买入
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import '@/css/HomePage.css';

export default {
  name: 'StockHomePage',
  data() {
    return {
      // 搜索相关
      searchType: 'code',
      searchKeyword: '',

      // 股票数据
      stockList: [],

      // 分页相关
      currentPage: 1,
      itemsPerPage: 12,

      // 买入模态窗口
      showBuyModal: false,
      currentStock: {},
      currentPrice: null,
      buyQuantity: 1,

      // 市场数据
      ShanghaiTop10: {},
      ShenzhenTop10: {},
      newsInformation: {},
      significantIndex: {},

      // UI状态
      activeRankingTab: 'shanghai',
      isManager: false,

      // 加载状态
      isLoading: false,
      searchLoading: false
    }
  },

  async mounted() {
    await this.initializePage();
  },

  computed: {
    // 分页计算
    paginatedStocks() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.stockList.slice(start, end);
    },

    // 总页数
    totalPages() {
      return Math.ceil(this.stockList.length / this.itemsPerPage);
    },

    // 搜索占位符
    searchPlaceholder() {
      return this.searchType === 'code' ? '请输入股票代码，如：000001' : '请输入股票名称，如：平安银行';
    }
  },

  watch: {
    // 监听搜索类型变化，清空搜索关键词
    searchType() {
      this.searchKeyword = '';
    },

    // 监听股票列表变化，重置到第一页
    stockList() {
      this.currentPage = 1;
    }
  },

  methods: {
    // 页面初始化
    async initializePage() {
      this.isLoading = true;
      try {
        await Promise.all([
          this.loadHomePageData(),
          this.checkUserRole()
        ]);
      } catch (error) {
        console.error('页面初始化失败:', error);
        this.$message.error('页面加载失败，请刷新重试');
      } finally {
        this.isLoading = false;
      }
    },

    // 检查用户角色
    checkUserRole() {
      const currentPath = this.$route.path;
      const managerID = localStorage.getItem('managerID');
      this.isManager = currentPath.startsWith('/manager') || (managerID != null);
    },

    // 加载首页数据
    async loadHomePageData() {
      try {
        const response = await this.$axios.get('/platform/loadHomePageData');

        if (response.data.status === 'SUCCESS') {
          this.ShanghaiTop10 = response.data.ShanghaiTop10 || {};
          this.ShenzhenTop10 = response.data.ShenzhenTop10 || {};
          this.newsInformation = response.data.newsInformation || {};
          this.significantIndex = response.data.significantIndex || {};
          console.log("new:" + this.newsInformation);
        } else {
          throw new Error(response.data.errorMessage || '数据加载失败');
        }
      } catch (error) {
        console.error('加载首页数据失败:', error);
        this.$message.error('市场数据加载失败: ' + error.message);
      }
    },

    // 搜索股票
    async searchStocks() {
      if (!this.searchKeyword.trim()) {
        this.$message.warning('请输入搜索关键词');
        return;
      }

      this.searchLoading = true;

      try {
        let response;

        if (this.searchType === 'code') {
          response = await this.$axios.get('/platform/queryStockByCode', {
            params: { stockCode: this.searchKeyword.trim() }
          });

          if (response.data.status === 'SUCCESS') {
            // 单个股票结果转换为数组
            this.stockList = response.data.stockInformation ? [response.data.stockInformation] : [];
          } else {
            throw new Error(response.data.errorMessage || '查询失败');
          }
        } else if (this.searchType === 'name') {
          response = await this.$axios.get('/platform/queryStockByName', {
            params: { stockName: this.searchKeyword.trim() }
          });

          if (response.data.status === 'SUCCESS') {
            this.stockList = response.data.stockInformationList || [];
          } else {
            throw new Error(response.data.errorMessage || '查询失败');
          }
        }

        if (this.stockList.length === 0) {
          this.$message.info('未找到相关股票，请尝试其他关键词');
        } else {
          this.$message.success(`找到 ${this.stockList.length} 只相关股票`);
        }

      } catch (error) {
        console.error('搜索失败:', error);
        this.$message.error('搜索失败: ' + error.message);
        this.stockList = [];
      } finally {
        this.searchLoading = false;
      }
    },

    // 添加自选股
    async addFavoriteStock(stockCode) {
      const userID = localStorage.getItem('userID');
      if (!userID) {
        this.$message.warning('请先登录');
        return;
      }

      try {
        const response = await this.$axios.post('/platform/addFavoriteStock', {
          userID: userID,
          stockCode: stockCode
        });

        if (response.data.status === 'SUCCESS') {
          this.$message.success('已添加到自选股');
        } else {
          throw new Error(response.data.errorMessage || '添加失败');
        }
      } catch (error) {
        console.error('添加自选股失败:', error);
        this.$message.error('添加自选股失败: ' + error.message);
      }
    },

    // 跳转到股票详情
    async toStock(stock) {
      try {
        // 更新股票数据
        const response = await this.$axios.post('/platform/updateAnnualDailyQuotes', {
          stockCode: stock.stockCode
        });

        if (response.data.status === 'SUCCESS') {
          // 保存股票信息到本地存储
          localStorage.setItem('stockCode', stock.stockCode);
          localStorage.setItem('stockName', stock.stockName);

          // 跳转到股票详情页
          if (this.$route.path !== '/user/stock') {
            this.$router.push('/user/stock');
          }
        } else {
          throw new Error(response.data.errorMessage || '跳转失败');
        }
      } catch (error) {
        console.error('跳转失败:', error);
        this.$message.error('跳转失败: ' + error.message);
      }
    },

    // 打开买入模态窗口
    async openBuyModal(stock) {
      try {
        const response = await this.$axios.get('/platform/isTrading', {
          params: { stockCode: stock.stockCode }
        });

        if (response.data.status === 'SUCCESS') {
          this.currentStock = stock;
          this.currentPrice = response.data.perPrice;
          this.buyQuantity = 1;
          this.showBuyModal = true;
        } else {
          this.$message.warning(response.data.errorMessage || '当前不可交易');
        }
      } catch (error) {
        console.error('获取交易信息失败:', error);
        this.$message.error('获取交易信息失败: ' + error.message);
      }
    },

    // 确认买入
    async confirmBuy() {
      const userID = localStorage.getItem('userID');
      if (!userID) {
        this.$message.warning('请先登录');
        return;
      }

      if (!this.buyQuantity || this.buyQuantity <= 0) {
        this.$message.warning('请输入有效的购买数量');
        return;
      }

      try {
        // 确认对话框
        await this.$confirm(
          `确认买入 ${this.currentStock.stockName} ${this.buyQuantity} 股？\n预估金额：¥${(this.buyQuantity * this.currentPrice).toFixed(2)}`,
          '确认买入',
          {
            confirmButtonText: '确认买入',
            cancelButtonText: '取消',
            type: 'warning'
          }
        );

        // 执行买入
        const response = await this.$axios.post('/platform/buyStock', {
          userID: userID,
          stockCode: this.currentStock.stockCode,
          buyNumber: this.buyQuantity
        });

        if (response.data.status === 'SUCCESS') {
          this.$message.success(`买入成功！实际金额：¥${response.data.amountSpent}`);
          this.showBuyModal = false;
          this.resetBuyForm();
        } else {
          throw new Error(response.data.errorMessage || '买入失败');
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('买入失败:', error);
          this.$message.error('买入失败: ' + error.message);
        }
      }
    },

    // 重置买入表单
    resetBuyForm() {
      this.currentStock = {};
      this.currentPrice = null;
      this.buyQuantity = 1;
    },

    // 格式化数字
    formatNumber(num) {
      if (num >= 100000000) {
        return (num / 100000000).toFixed(1) + '亿';
      } else if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万';
      }
      return num.toString();
    },

    // 格式化日期
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString('zh-CN');
    }
  }
}
</script>