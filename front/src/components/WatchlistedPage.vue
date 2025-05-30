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

<style scoped>
/* 全局样式重置 */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

/* 主容器样式 - 改用清爽的蓝白渐变 */
.watchlisted-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 50%, #e8f5e8 100%);
    padding: 20px;
    font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
}

/* 页面头部样式 */
.page-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
    border: 1px solid rgba(33, 150, 243, 0.1);
}

.header-content {
    display: flex;
    align-items: center;
    gap: 40px;
    flex-wrap: wrap;
}

.page-title {
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(135deg, #2196f3, #1976d2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0;
}

.icon-star {
    font-size: 28px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.header-stats {
    display: flex;
    gap: 24px;
}

.stat-item {
    text-align: center;
    padding: 12px 20px;
    background: rgba(33, 150, 243, 0.05);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.1);
    transition: transform 0.3s ease;
    border: 1px solid rgba(33, 150, 243, 0.1);
}

.stat-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(33, 150, 243, 0.15);
}

.stat-label {
    display: block;
    font-size: 12px;
    color: #666;
    margin-bottom: 4px;
    font-weight: 500;
}

.stat-value {
    display: block;
    font-size: 20px;
    font-weight: 700;
    color: #333;
}

.stat-value.up {
    color: #f44336;
}

.stat-value.down {
    color: #4caf50;
}

.refresh-btn {
    background: linear-gradient(135deg, #2196f3, #1976d2);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 12px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
}

.refresh-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
    background: linear-gradient(135deg, #1976d2, #1565c0);
}

.refresh-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.refresh-icon {
    font-size: 16px;
    transition: transform 0.3s ease;
}

.refresh-icon.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* 加载状态样式 */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(33, 150, 243, 0.1);
}

.loading-spinner {
    width: 60px;
    height: 60px;
    border: 4px solid rgba(33, 150, 243, 0.2);
    border-top: 4px solid #2196f3;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
}

.loading-container p {
    color: #666;
    font-size: 16px;
    font-weight: 500;
}

/* 表格容器样式 */
.table-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease;
    border: 1px solid rgba(33, 150, 243, 0.1);
}

.table-container:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.table-wrapper {
    overflow-x: auto;
}

/* 表格样式 */
.stock-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.stock-table th {
    background: linear-gradient(135deg, #2196f3, #1976d2);
    color: white;
    padding: 20px 15px;
    text-align: center;
    font-weight: 600;
    font-size: 14px;
    position: sticky;
    top: 0;
    z-index: 10;
    border: none;
}

.stock-table td {
    padding: 18px 15px;
    text-align: center;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    vertical-align: middle;
}

.stock-row {
    transition: all 0.3s ease;
    background: white;
}

.stock-row:hover {
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.03), rgba(25, 118, 210, 0.03));
    transform: scale(1.005);
}

.even-row {
    background: rgba(248, 249, 250, 0.5);
}

.even-row:hover {
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.05), rgba(25, 118, 210, 0.05));
}

/* 股票代码样式 - 优化为小标签样式 */
.stock-code .code-text {
    font-family: 'Courier New', monospace;
    font-weight: 600;
    color: white;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
    border: 1px solid rgba(33, 150, 243, 0.2);
    display: inline-block;
    min-width: 80px;
}

/* 股票名称样式 */
.name-container {
    display: flex;
    align-items: center;
    justify-content: center;
}

.name-text {
    font-weight: 600;
    color: #333;
    font-size: 14px;
}

/* 行业和地区标签 */
.industry-tag,
.area-tag {
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(56, 142, 60, 0.08));
    color: #388e3c;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid rgba(76, 175, 80, 0.2);
}

/* 价格样式 */
.price-value {
    font-family: 'Courier New', monospace;
    font-weight: 600;
    font-size: 14px;
}

.price-arrow {
    margin-left: 6px;
    font-size: 12px;
}

.price-up {
    color: #f44336;
}

.price-up .price-value {
    color: #f44336;
}

.price-down {
    color: #4caf50;
}

.price-down .price-value {
    color: #4caf50;
}

.price-equal .price-value {
    color: #757575;
}

/* 涨跌幅样式 */
.change-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
}

.change-percent {
    font-weight: 700;
    font-size: 14px;
}

.change-amount {
    font-size: 11px;
    opacity: 0.8;
}

/* 操作按钮样式 */
.action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
}

.action-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 12px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    color: white;
}

.detail-btn {
    background: linear-gradient(135deg, #2196f3, #1976d2);
    box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.detail-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
    background: linear-gradient(135deg, #1976d2, #1565c0);
}

.remove-btn {
    background: linear-gradient(135deg, #f44336, #d32f2f);
    box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.remove-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(244, 67, 54, 0.4);
    background: linear-gradient(135deg, #d32f2f, #c62828);
}

.btn-icon {
    font-size: 14px;
}

/* 空状态样式 */
.empty-state {
    text-align: center;
    padding: 80px 40px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(33, 150, 243, 0.1);
}

.empty-icon {
    font-size: 80px;
    margin-bottom: 20px;
    opacity: 0.6;
}

.empty-title {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
}

.empty-description {
    color: #666;
    font-size: 16px;
    margin-bottom: 30px;
    line-height: 1.6;
}

.add-btn {
    background: linear-gradient(135deg, #4caf50, #388e3c);
    color: white;
    border: none;
    padding: 15px 30px;
    border-radius: 12px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.add-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
    background: linear-gradient(135deg, #388e3c, #2e7d32);
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .header-stats {
        gap: 16px;
    }
    
    .stat-item {
        padding: 10px 16px;
    }
}

@media (max-width: 768px) {
    .watchlisted-container {
        padding: 15px;
    }
    
    .page-header {
        padding: 20px;
        flex-direction: column;
        text-align: center;
    }
    
    .header-content {
        flex-direction: column;
        gap: 20px;
    }
    
    .page-title {
        font-size: 24px;
    }
    
    .header-stats {
        gap: 12px;
    }
    
    .stat-item {
        padding: 8px 12px;
    }
    
    .stock-table {
        font-size: 12px;
    }
    
    .stock-table th,
    .stock-table td {
        padding: 12px 8px;
    }
    
    .action-buttons {
        flex-direction: column;
        gap: 4px;
    }
    
    .action-btn {
        padding: 6px 10px;
        font-size: 11px;
    }
}

@media (max-width: 576px) {
    .table-wrapper {
        overflow-x: scroll;
    }
    
    .stock-table {
        min-width: 800px;
    }
    
    .empty-state {
        padding: 60px 20px;
    }
    
    .empty-icon {
        font-size: 60px;
    }
    
    .empty-title {
        font-size: 20px;
    }
    
    .empty-description {
        font-size: 14px;
    }
}

/* 动画效果 */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.table-container,
.empty-state,
.page-header {
    animation: fadeInUp 0.6s ease-out;
}

/* 滚动条样式 */
.table-wrapper::-webkit-scrollbar {
    height: 8px;
}

.table-wrapper::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #2196f3, #1976d2);
    border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #1976d2, #1565c0);
}
</style>