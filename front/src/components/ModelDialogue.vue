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

<style scoped>
/* 主容器 - 更现代化的设计 */
.model-dialogue-container {
    width: 90vw;
    max-width: 1200px;
    height: 80vh;
    margin: 3vh auto;
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 24px;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.08),
        0 8px 25px rgba(0, 0, 0, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    padding: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 增强的头部设计 */
.dialogue-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 32px;
    background: linear-gradient(135deg, 
        #667eea 0%, 
        #764ba2 50%, 
        #f093fb 100%);
    border-radius: 24px 24px 0 0;
    position: relative;
    overflow: hidden;
}

.dialogue-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, 
        rgba(255, 255, 255, 0.1) 0%, 
        transparent 50%, 
        rgba(255, 255, 255, 0.05) 100%);
    pointer-events: none;
}

.header-left {
    display: flex;
    align-items: center;
    z-index: 1;
}

.header-icon-wrapper {
    width: 48px;
    height: 48px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.header-icon {
    font-size: 24px;
    color: #fff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.header-info {
    display: flex;
    flex-direction: column;
}

.header-title {
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 4px;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    letter-spacing: 0.5px;
}

.header-subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 400;
}

.header-right {
    display: flex;
    align-items: center;
    z-index: 1;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse-status 2s infinite;
}

.status-indicator.online {
    background: #4ade80;
    box-shadow: 0 0 0 4px rgba(74, 222, 128, 0.3);
}

@keyframes pulse-status {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.status-text {
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
    font-weight: 500;
}

/* 对话内容区域 */
.dialogue-content {
    flex: 1;
    overflow-y: auto;
    padding: 32px;
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    position: relative;
}

.dialogue-content::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 20px;
    background: linear-gradient(180deg, rgba(248, 250, 252, 0.8) 0%, transparent 100%);
    pointer-events: none;
    z-index: 1;
}

/* 自定义滚动条 */
.dialogue-content::-webkit-scrollbar {
    width: 8px;
}

.dialogue-content::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 10px;
}

.dialogue-content::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #cbd5e1 0%, #94a3b8 100%);
    border-radius: 10px;
    border: 2px solid transparent;
    background-clip: content-box;
}

.dialogue-content::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #94a3b8 0%, #64748b 100%);
    background-clip: content-box;
}

/* 消息样式 */
.message {
    display: flex;
    align-items: flex-start;
    margin-bottom: 32px;
    animation: slideIn 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.message.user {
    flex-direction: row-reverse;
}

/* 头像样式 */
.message .avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 16px;
    font-size: 20px;
    position: relative;
    flex-shrink: 0;
}

.message.user .avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.message.assistant .avatar {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: #fff;
    box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
}

.message .avatar::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 50%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    z-index: -1;
}

/* 消息气泡 */
.bubble {
    max-width: 75%;
    position: relative;
    animation: bubbleIn 0.3s ease;
}

@keyframes bubbleIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.message.user .bubble {
    margin-right: 8px;
}

.message.assistant .bubble {
    margin-left: 8px;
}

/* 思考内容样式 */
.thinking-content {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    padding: 20px 24px;
    margin-bottom: 16px;
    border-radius: 16px;
    border: 1px solid rgba(251, 191, 36, 0.2);
    box-shadow: 0 4px 20px rgba(251, 191, 36, 0.1);
    position: relative;
    overflow: hidden;
}

.thinking-content::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
}

.thinking-header {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
}

.thinking-icon {
    font-size: 16px;
    color: #d97706;
    margin-right: 8px;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.thinking-label {
    font-weight: 600;
    color: #92400e;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.thinking-text {
    color: #78350f;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
}

/* 回复内容样式 */
.response-content {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    padding: 20px 24px;
    border-radius: 16px;
    border: 1px solid rgba(14, 165, 233, 0.1);
    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.08);
    color: #1e293b;
    font-size: 15px;
    line-height: 1.7;
    position: relative;
    overflow: hidden;
}

.response-content::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%);
}

/* 用户消息样式 */
.message.user .bubble {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    padding: 16px 20px;
    border-radius: 20px 20px 4px 20px;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    font-size: 15px;
    line-height: 1.6;
}

/* 时间戳 */
.message-time {
    font-size: 12px;
    color: #64748b;
    text-align: right;
    margin-top: 8px;
    opacity: 0.7;
}

.message.user .message-time {
    color: rgba(255, 255, 255, 0.7);
}

/* 输入区域 */
.dialogue-input-area {
    padding: 24px 32px;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    backdrop-filter: blur(10px);
}

.input-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 16px;
    background: #fff;
    border-radius: 20px;
    padding: 16px 20px;
    box-shadow: 
        0 10px 40px rgba(0, 0, 0, 0.08),
        0 4px 12px rgba(0, 0, 0, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
}

.input-wrapper:focus-within {
    box-shadow: 
        0 15px 50px rgba(102, 126, 234, 0.15),
        0 6px 20px rgba(102, 126, 234, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    border-color: rgba(102, 126, 234, 0.3);
    transform: translateY(-2px);
}

.dialogue-input {
    flex: 1;
}

.dialogue-input :deep(.el-textarea__inner) {
    border: none;
    padding: 0;
    font-size: 15px;
    line-height: 1.6;
    resize: none;
    background: transparent;
    color: #1e293b;
}

.dialogue-input :deep(.el-textarea__inner:focus) {
    box-shadow: none;
}

.dialogue-input :deep(.el-textarea__inner::placeholder) {
    color: #94a3b8;
}

/* 发送按钮 */
.send-btn {
    min-width: 80px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: #fff;
    font-weight: 600;
    font-size: 14px;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
    overflow: hidden;
}

.send-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
}

.send-btn:hover::before {
    left: 100%;
}

.send-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.send-btn:active {
    transform: translateY(0);
}

.send-btn:disabled {
    background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
    color: #64748b;
    box-shadow: none;
    cursor: not-allowed;
    transform: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .model-dialogue-container {
        width: 95vw;
        height: 85vh;
        margin: 2vh auto;
        border-radius: 16px;
    }
    
    .dialogue-header {
        padding: 16px 20px;
        border-radius: 16px 16px 0 0;
    }
    
    .header-title {
        font-size: 20px;
    }
    
    .header-subtitle {
        font-size: 12px;
    }
    
    .dialogue-content {
        padding: 20px 16px;
    }
    
    .dialogue-input-area {
        padding: 16px 20px;
    }
    
    .bubble {
        max-width: 85%;
    }
    
    .message .avatar {
        width: 40px;
        height: 40px;
        margin: 0 12px;
        font-size: 18px;
    }
}

/* Markdown内容样式 */
.response-content :deep(h1),
.response-content :deep(h2),
.response-content :deep(h3) {
    color: #1e293b;
    margin: 16px 0 8px 0;
    font-weight: 600;
}

.response-content :deep(p) {
    margin: 8px 0;
}

.response-content :deep(pre) {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: #e2e8f0;
    padding: 16px;
    border-radius: 12px;
    overflow-x: auto;
    margin: 12px 0;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
}

.response-content :deep(code) {
    background: rgba(14, 165, 233, 0.1);
    color: #0ea5e9;
    padding: 2px 6px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 13px;
}

.response-content :deep(blockquote) {
    border-left: 4px solid #0ea5e9;
    padding: 12px 16px;
    margin: 12px 0;
    background: rgba(14, 165, 233, 0.05);
    border-radius: 0 8px 8px 0;
    color: #475569;
}

.response-content :deep(ul),
.response-content :deep(ol) {
    padding-left: 20px;
    margin: 8px 0;
}

.response-content :deep(li) {
    margin: 4px 0;
}

.response-content :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.response-content :deep(th),
.response-content :deep(td) {
    border: 1px solid #e2e8f0;
    padding: 12px;
    text-align: left;
}

.response-content :deep(th) {
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    color: #475569;
    font-weight: 600;
}
</style>