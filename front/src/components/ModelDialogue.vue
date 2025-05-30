<template>
    <div class="model-dialogue-container">
        <!-- 增强的头部设计 -->
        <div class="dialogue-header">
            <div class="header-left">
                <div class="header-icon-wrapper">
                    <i class="el-icon-chat-dot-round header-icon"></i>
                </div>
                <div class="header-info">
                    <span class="header-title">智能模型对话</span>
                    <span class="header-subtitle">AI助手为您提供专业解答</span>
                </div>
            </div>
            <div class="header-right">
                <div class="status-indicator online"></div>
                <span class="status-text">在线</span>
            </div>
        </div>
        
        <!-- 对话内容区域 -->
        <div class="dialogue-content" ref="dialogueContent">
            <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
                <div class="avatar" v-if="msg.role === 'user'">
                    <i class="el-icon-user"></i>
                </div>
                <div class="avatar" v-else>
                    <i class="el-icon-cpu"></i>
                </div>
                <div class="bubble" :class="msg.role === 'assistant' ? 'reply-bubble' : ''">
                    <div v-if="msg.thinking" class="thinking-content">
                        <div class="thinking-header">
                            <i class="el-icon-loading thinking-icon"></i>
                            <span class="thinking-label">思考过程</span>
                        </div>
                        <div class="thinking-text">{{ msg.thinking }}</div>
                    </div>
                    <div v-if="msg.content" class="response-content" v-html="renderMarkdown(msg.content)"></div>
                    <!-- 添加时间戳 -->
                    <div class="message-time">{{ formatTime(new Date()) }}</div>
                </div>
            </div>
        </div>
        
        <!-- 增强的输入区域 -->
        <div class="dialogue-input-area">
            <div class="input-wrapper">
                <el-input 
                    v-model="inputText" 
                    placeholder="请输入您的问题..." 
                    class="dialogue-input"
                    @keyup.enter.native="handleSend" 
                    clearable 
                    :disabled="loading"
                    type="textarea"
                    :autosize="{ minRows: 1, maxRows: 4 }"
                    resize="none">
                </el-input>
                <div class="input-actions">
                    <el-button 
                        type="primary" 
                        icon="el-icon-s-promotion" 
                        class="send-btn" 
                        @click="handleSend"
                        :disabled="loading || !inputText.trim()">
                        <span v-if="!loading">发送</span>
                        <span v-else>发送中...</span>
                    </el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';
import '@/css/ModelDialogue.css';

export default {
    name: "ModelDialogue",
    data() {
        return {
            userID: localStorage.getItem('userID'),
            messages: [],
            inputText: '',
            loading: false,
        }
    },
    methods: {
        renderMarkdown(text) {
            if (!text) return '';
            const md = new MarkdownIt();
            return DOMPurify.sanitize(md.render(text));
        },
        formatTime(date) {
            return date.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        },
        async handleSend() {
            if (!this.inputText.trim()) return;

            // 添加用户消息
            this.messages.push({ role: 'user', content: this.inputText });
            this.loading = true;

            try {
                // 使用 axios 发送 GET 请求
                const response = await this.$axios.get(`/dialogue/dialogueLocalModel`, {
                    params: {
                        userID: this.userID,
                        userContent: this.inputText
                    }
                });

                if (response.data.status === 'SUCCESS') {
                    // 同时添加思考内容和回复内容
                    this.messages.push({
                        role: 'assistant',
                        thinking: response.data.thinking_content,
                        content: response.data.response_content
                    });

                    this.inputText = '';

                    // 滚动到底部
                    this.$nextTick(() => {
                        const content = this.$refs.dialogueContent;
                        content.scrollTop = content.scrollHeight;
                    });
                } else {
                    this.messages.push({
                        role: 'assistant',
                        content: 'Error: ' + response.data.errorMessage
                    });
                }
            } catch (error) {
                this.messages.push({
                    role: 'assistant',
                    content: 'Error: ' + (error.message || '请求失败')
                });
            } finally {
                this.loading = false;
            }
        }
    }
}
</script>