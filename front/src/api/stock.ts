import axios from "axios";

const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': "application/json",     // 以JSON形式发送
    },
});

apiClient.interceptors.response.use(
    (response) => {
        const data = response.data;
        if (data.status == 'ERROR') {
            alert(data.errorMessage);
            return null;
        }
        return data
    },
    (error) => {
        alert(error.message);
        return null
    }
)

// 定义判断当前是否可以交易接口
export const isTrading = async () => {
    try {
        const response = await apiClient.get('api/platform/isTrading');
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义根据股票名称查询接口
export const queryStockByName = async ( credentials: { stockName: string } ) => {
    try {
        const response = await apiClient.get('api/platform/queryStockByName', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义根据股票代码查询接口
export const queryStockByCode = async (credentials: { stockCode: string }) => {
    try {
        const response = await apiClient.get('api/platform/queryStockByCode', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义买入股票接口
export const buyStock = async (credentials: { userID: number; stockCode: string; buyNumber: number }) => {
    try {
        const response = await apiClient.post('api/platform/buyStock', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义卖出股票接口
export const sellStock = async (credentials: { ownershipID: number; sellNumber: number }) => {
    try {
        const response = await apiClient.post('api/platform/sellStock', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义更新年度日线行情并保存到本地接口
export const updateAnnualDailyQuotes = async (credentials: { stockCode: string }) => {
    try {
        const response = await apiClient.post('api/platform/updateAnnualDailyQuotes', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义显示股票的日、周、月行情图接口
export const showStockQurve = async (credentials: { stockCode: string; timeSpan: string; type: number }) => {
    try {
        const response = await apiClient.get('api/platform/showStockQurve', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义显示股票的技术指标变化图接口
export const showTechnicalIndicator = async (credentials: { stockCode: string }) => {
    try {
        const response = await apiClient.get('api/platform/showTechnicalIndicator', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义获取公司的财务指标数据接口
export const getFinancialMetric = async (credentials: { stockCode: string }) => {
    try {
        const response = await apiClient.get('api/platform/getFinancialMetric', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义显示股票的估值比率变化图接口
export const showValuationRatio = async (credentials: { stockCode: string }) => {
    try {
        const response = await apiClient.get('api/platform/showValuationRatio', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义使用Transformer模型预测股票收盘价接口
export const forecastStock = async (credentials: { stockCode: string }) => {
    try {
        const response = await apiClient.get('api/analyse/forecastStock', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义展示股票的Z分模型得分接口
export const showZScore = async (credentials: { stockCode: string }) => {
    try {
        const response = await apiClient.get('api/analyse/showZScore', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义展示股票的夏普比率和当前的国债利率接口
export const showSharpeRatio = async (credentials: { stockCode: string }) => {
    try {
        const response = await apiClient.get('api/analyse/showSharpeRatio', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

