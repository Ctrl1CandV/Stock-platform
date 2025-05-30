<template>
    <div class="watchlisted-container">
        <!-- 页面头部 -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">
                    <i class="icon-star">⭐</i>
                    我的自选股
                </h1>
                <div class="header-stats" v-if="favoriteStocksList.length > 0">
                    <div class="stat-item">
                        <span class="stat-label">总数</span>
                        <span class="stat-value">{{ favoriteStocksList.length }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">上涨</span>
                        <span class="stat-value up">{{ upCount }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">下跌</span>
                        <span class="stat-value down">{{ downCount }}</span>
                    </div>
                </div>
            </div>
            <button class="refresh-btn" @click="refreshData" :disabled="isRefreshing">
                <i class="refresh-icon" :class="{ 'spinning': isRefreshing }">🔄</i>
                刷新数据
            </button>
        </div>

        <!-- 加载状态 -->
        <div class="loading-container" v-if="isLoading">
            <div class="loading-spinner"></div>
            <p>正在加载自选股数据...</p>
        </div>

        <!-- 股票列表 -->
        <div class="table-container" v-else-if="favoriteStocksList.length > 0">
            <div class="table-wrapper">
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th class="stock-code-col">股票代码</th>
                            <th class="stock-name-col">股票名称</th>
                            <th class="industry-col">行业</th>
                            <th class="area-col">地区</th>
                            <th class="price-col">昨收价</th>
                            <th class="price-col">当前价</th>
                            <th class="price-col">最高价</th>
                            <th class="price-col">最低价</th>
                            <th class="change-col">涨跌幅</th>
                            <th class="action-col">操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(stock, index) in favoriteStocksList" 
                            :key="stock.stock_code" 
                            class="stock-row"
                            :class="{ 'even-row': index % 2 === 0 }">
                            <td class="stock-code">
                                <span class="code-text">{{ stock.stock_code }}</span>
                            </td>
                            <td class="stock-name">
                                <div class="name-container">
                                    <span class="name-text">{{ stock.stock_name }}</span>
                                </div>
                            </td>
                            <td class="industry">
                                <span class="industry-tag">{{ stock.industry || '-' }}</span>
                            </td>
                            <td class="area">
                                <span class="area-tag">{{ stock.area || '-' }}</span>
                            </td>
                            <td class="price">
                                <span class="price-value">{{ formatPrice(stock.preClosePrice) }}</span>
                            </td>
                            <td class="price" :class="getPriceClass(stock.currentPrice, stock.preClosePrice)">
                                <span class="price-value">{{ formatPrice(stock.currentPrice) }}</span>
                                <span class="price-arrow" v-if="getPriceDirection(stock.currentPrice, stock.preClosePrice)">
                                    {{ getPriceDirection(stock.currentPrice, stock.preClosePrice) }}
                                </span>
                            </td>
                            <td class="price">
                                <span class="price-value">{{ formatPrice(stock.highPrice) }}</span>
                            </td>
                            <td class="price">
                                <span class="price-value">{{ formatPrice(stock.lowPrice) }}</span>
                            </td>
                            <td class="change" :class="getPriceClass(stock.currentPrice, stock.preClosePrice)">
                                <div class="change-container">
                                    <span class="change-percent">{{ calculateChangePercent(stock.currentPrice, stock.preClosePrice) }}</span>
                                    <span class="change-amount">{{ calculateChangeAmount(stock.currentPrice, stock.preClosePrice) }}</span>
                                </div>
                            </td>
                            <td class="actions">
                                <div class="action-buttons">
                                    <button class="action-btn detail-btn" @click="toStock(stock)" title="查看详情">
                                        <i class="btn-icon">📊</i>
                                        <span>详情</span>
                                    </button>
                                    <button class="action-btn remove-btn" @click="removeFromWatchlist(stock)" title="移除自选">
                                        <i class="btn-icon">🗑️</i>
                                        <span>移除</span>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 空状态 -->
        <div class="empty-state" v-else>
            <div class="empty-icon">📈</div>
            <h3 class="empty-title">暂无自选股</h3>
            <p class="empty-description">您还没有添加任何自选股，快去市场挑选心仪的股票吧！</p>
            <button class="add-btn" @click="goToMarket">
                <i class="btn-icon">➕</i>
                去市场添加
            </button>
        </div>
    </div>
</template>

<script>
import '@/css/WatchlistedPage.css';

export default {
    name: 'WatchlistedPage',
    data() {
        return {
            userID: localStorage.getItem('userID'),
            favoriteStocksList: [],
            isLoading: true,
            isRefreshing: false,
        };
    },
    computed: {
        upCount() {
            return this.favoriteStocksList.filter(stock => 
                parseFloat(stock.currentPrice) > parseFloat(stock.preClosePrice)
            ).length;
        },
        downCount() {
            return this.favoriteStocksList.filter(stock => 
                parseFloat(stock.currentPrice) < parseFloat(stock.preClosePrice)
            ).length;
        }
    },
    async mounted() {
        await this.getFavoriteStocks();
    },
    methods: {
        async getFavoriteStocks() {
            this.isLoading = true;
            try {
                const response = await this.$axios.get('/user/getFavoriteStocksInformation', {
                    params: { userID: this.userID },
                });

                if (response.data.status === 'SUCCESS') {
                    this.favoriteStocksList = response.data.favoriteStocksList || [];
                } else {
                    this.$message?.error('获取自选股信息失败: ' + response.data.errorMessage) || 
                    alert('获取自选股信息失败: ' + response.data.errorMessage);
                }
            } catch (error) {
                console.error('获取自选股失败:', error);
                alert('请求失败: ' + error.message);
            } finally {
                this.isLoading = false;
            }
        },
        async refreshData() {
            if (this.isRefreshing) return;
            this.isRefreshing = true;
            try {
                await this.getFavoriteStocks();
                this.$message?.success('数据刷新成功') || alert('数据刷新成功');
            } finally {
                this.isRefreshing = false;
            }
        },
        getPriceClass(currentPrice, preClosePrice) {
            if (!currentPrice || !preClosePrice) return '';
            const current = parseFloat(currentPrice);
            const preClose = parseFloat(preClosePrice);
            if (current > preClose) return 'price-up';
            if (current < preClose) return 'price-down';
            return 'price-equal';
        },
        getPriceDirection(currentPrice, preClosePrice) {
            if (!currentPrice || !preClosePrice) return '';
            const current = parseFloat(currentPrice);
            const preClose = parseFloat(preClosePrice);
            if (current > preClose) return '↗';
            if (current < preClose) return '↘';
            return '';
        },
        calculateChangePercent(currentPrice, preClosePrice) {
            if (!currentPrice || !preClosePrice) return '0.00%';
            const current = parseFloat(currentPrice);
            const preClose = parseFloat(preClosePrice);
            const change = ((current - preClose) / preClose * 100).toFixed(2);
            return change > 0 ? `+${change}%` : `${change}%`;
        },
        calculateChangeAmount(currentPrice, preClosePrice) {
            if (!currentPrice || !preClosePrice) return '0.00';
            const current = parseFloat(currentPrice);
            const preClose = parseFloat(preClosePrice);
            const change = (current - preClose).toFixed(2);
            return change > 0 ? `+${change}` : `${change}`;
        },
        formatPrice(price) {
            if (!price) return '-';
            return parseFloat(price).toFixed(2);
        },
        async removeFromWatchlist(stock) {
            if (!confirm(`确定要移除 ${stock.stock_name} 吗？`)) return;
            
            try {
                const response = await this.$axios.post('/platform/removeFavoriteStock', {
                    userID: this.userID,
                    stockCode: stock.stock_code
                });

                if (response.data.status === 'SUCCESS') {
                    this.$message?.success(`${stock.stock_name} 已从自选股中移除`) || 
                    alert(`${stock.stock_name} 已从自选股中移除`);
                    await this.getFavoriteStocks();
                } else {
                    this.$message?.error('移除自选股失败: ' + response.data.errorMessage) || 
                    alert('移除自选股失败: ' + response.data.errorMessage);
                }
            } catch (error) {
                console.error('移除自选股失败:', error);
                alert('请求失败: ' + error.message);
            }
        },
        goToMarket() {
            this.$router.push('/user');
        },
        async toStock(stock) {
            try {
                const response = await this.$axios.post('/platform/updateAnnualDailyQuotes', { 
                    stockCode: stock.stock_code 
                });
                if (response.data.status === 'SUCCESS') {
                    localStorage.setItem('stockCode', stock.stock_code);
                    localStorage.setItem('stockName', stock.stock_name);
                    this.$router.push('/user/stock');
                } else {
                    this.$message?.error('跳转失败: ' + response.data.errorMessage) || 
                    alert('跳转失败: ' + response.data.errorMessage);
                }
            } catch (error) {
                console.error('跳转失败:', error);
                alert('请求失败: ' + error.message);
            }
        },
    },
}
</script>