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

// 定义登录接口
export const login = async ( credentials: { userAccount: string; password: string; role: string }) => {
    try {
        const { userAccount, password } = credentials;
        const url = credentials.role === 'manager' ? 'api/manage/login' : 'api/user/login';
        const response = await apiClient.post(url, { userAccount, password});
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义注册接口
export const register = async ( credentials: { userEmail: string; userName: string; userPassword: string } ) => {
    try {
        const response = await apiClient.post('api/user/register', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义获取用户个人信息接口
export const gainUserInformation = async ( credentials: { userID: number } ) => {
    try {
        const response = await apiClient.get('api/user/gainUserInformation', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义补充用户个人信息接口
export const updateProfile = async ( credentials: { userData: Map<string, any> ; userID: number } ) => {
    try {
        const response = await apiClient.post('api/user/updateProfile', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义更新用户余额接口
export const updateBalance = async ( credentials: { userID: number ; newBalance: number } ) => {
    try {
        const response = await apiClient.post('api/user/updateBalance', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义修改用户密码接口
export const changePassword = async ( credentials: { userID: number ; newPassword: string; oldPassword: string } ) => {
    try {
        const response = await apiClient.post('api/user/changePassword', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义查询用户股票持仓接口
export const getStockOwnership = async ( credentials: { userID: number } ) => {
    try {
        const response = await apiClient.get('api/user/getStockOwnership', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义查询用户交易记录接口
export const getTransactionRecords = async ( credentials: { userID: number } ) => {
    try {
        const response = await apiClient.get('api/user/getTransactionRecords', { params: credentials });
        return response.data;
    } catch (error) {
        return null;
    }
};

// 以下为管理员接口
// 定义伪删除用户账户接口
export const deleteUser = async ( credentials: { userID: number } ) => {
    try {
        const response = await apiClient.post('api/manage/deleteUser', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义更改用户的余额接口
export const editUserBalance = async ( credentials: { userID: number; newBalance: number } ) => {
    try {
        const response = await apiClient.post('api/manage/editUserBalance', credentials);
        return response.data;
    } catch (error) {
        return null;
    }
};

// 定义查询用户账户接口
export const queryUsers = async () => {
    try {
        const response = await apiClient.get('api/manage/queryUsers');
        return response.data;
    } catch (error) {
        return null;
    }
};