import { defineStore } from "pinia";

enum Role {
    USER = 'user',
    MANAGER = 'manager'
}

interface User {
    userID: number;
    userName: string;
    userEmail: string;
    userPassword: string;
    userBalance: number;
}

// 管理用户的认证状态，确保在多级跳转的时候信息不会丢失
export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null as User,
        role: Role.USER
    }),
    getters: {
        // 用于返回用户是否已经认证
        isAuthenticated: (state) => {
            return state.role === Role.MANAGER || (state.role === Role.USER && state.user !== null);
        }
    },
    actions: {
        setAuthData(user: User, role: Role) {
            this.user = user;
            this.role = role;
        },
        logout() {
            this.user = null;
            this.role = Role.USER;
        }
    },
})