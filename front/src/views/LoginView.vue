<template>
  <div class="login-container">
    <el-tabs v-model="activeTab">
      <!-- 登录标签页 -->
      <el-tab-pane label="登录" name="login">
        <el-select v-model="role" placeholder="选择角色">
          <el-option label="用户" value="user" />
          <el-option label="管理员" value="manager" />
        </el-select>
        <el-input v-model="userAccount" placeholder="账号" />
        <el-input v-model="password" type="password" placeholder="密码" />
        <el-button @click="handleLogin">登录</el-button>
      </el-tab-pane>

      <!-- 注册标签页 -->
      <el-tab-pane label="注册" name="register">
        <el-input v-model="form.userEmail" placeholder="邮箱" />
        <el-input v-model="form.userName" placeholder="用户名" />
        <el-input v-model="form.userPassword" type="password" placeholder="密码" />
        <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" />
        <el-button @click="handleRegister">注册</el-button>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore.ts';
import { login, register } from "../api/user.ts";

const authStore = useAuthStore();
const router = useRouter();
const activeTab = ref<'login' | 'register'>('login');
const role = ref<'user' | 'manager'>('user');
const userAccount = ref('');
const password = ref('');
const form = ref({
  userEmail: '',
  userName: '',
  userPassword: '',
  confirmPassword: ''
});

const handleLogin = async () => {
  // 表单验证
  if (!userAccount.value || !password.value){
    alert('请输入账号和密码');
    return null;
  }

  // 调用登录接口
  const credentials = {
    userAccount: userAccount.value,
    password: password.value,
    role: role.value
  };

  // 错误处理已在接口完成
  const response = await login(credentials);
  if (role.value == 'manager') {
    authStore.setAuthData(null, 'manager');
    router.push('/main/manager');
  }else {
    const user = response.user;
    const userData: User = {
      userID: user.user_id,
      userName: user.user_name,
      userEmail: user.user_email,
      userPassword: user.user_password,
      userBalance: user.user_balance
    };
    authStore.setAuthData(userData, 'user');
    router.push('/main');
  }
};

const handleRegister = async () => {
  if (!form.value.userEmail) {
    alert('邮箱不得为空');
    return null;
  }
  if (!form.value.userName) {
    alert('用户名不得为空');
    return null;
  }
  if (!form.value.userPassword) {
    alert('密码不得为空');
    return null;
  }
  if (!form.value.confirmPassword) {
    alert('确认密码不得为空');
    return null;
  }

  if (form.value.confirmPassword !== form.value.userPassword){
    alert('两次输入的密码不一致');
    return null;
  }

  // 调用注册接口
  const response = await register(form.value);
  if (response) {
    activeTab.value = 'login'; // 注册后跳转到登录
    alert('注册成功，请登录');
  }
};
</script>