<template>
    <div class="model-dialogue-container">
        <div class="dialogue-header">
            <i class="el-icon-chat-dot-round header-icon"></i>
            <span class="header-title">智能模型对话</span>
        </div>
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
                        <div class="thinking-label">思考过程：</div>
                        <div class="thinking-text">{{ msg.thinking }}</div>
                    </div>
                    <div v-if="msg.content" class="response-content" v-html="renderMarkdown(msg.content)"></div>
                </div>
            </div>
        </div>
        <div class="dialogue-input-area">
            <el-input v-model="inputText" placeholder="请输入您的问题..." class="dialogue-input"
                @keyup.enter.native="handleSend" clearable :disabled="loading"></el-input>
            <el-button type="primary" icon="el-icon-s-promotion" class="send-btn" @click="handleSend"
                :disabled="loading">发送</el-button>
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
.model-dialogue-container {
    width: 85vw;
    height: 75vh;
    max-width: none;
    min-height: 0;
    margin: 5vh auto;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08), 0 6px 12px rgba(0, 0, 0, 0.03);
    padding: 0 0 24px 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: all 0.3s ease;
}

.dialogue-header {
    display: flex;
    align-items: center;
    padding: 20px 32px;
    background: linear-gradient(135deg, #3a8ee6 0%, #5c9ce6 50%, #7bb2ff 100%);
    border-radius: 16px 16px 0 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    position: relative;
    z-index: 2;
}

.header-icon {
    font-size: 28px;
    color: #fff;
    margin-right: 14px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-title {
    font-size: 22px;
    font-weight: 600;
    color: #fff;
    letter-spacing: 1px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dialogue-content {
    flex: 1;
    overflow-y: auto;
    padding: 28px 32px 20px;
    background: #f9fafc;
    scroll-behavior: smooth;
    position: relative;
}

.dialogue-content::-webkit-scrollbar {
    width: 6px;
}

.dialogue-content::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.1);
    border-radius: 10px;
}

.dialogue-content::-webkit-scrollbar-track {
    background: transparent;
}

.message {
    display: flex;
    align-items: flex-start;
    margin-bottom: 24px;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message.user {
    flex-direction: row-reverse;
}

.message .avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 12px;
    font-size: 22px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
}

.message.user .avatar {
    background: linear-gradient(135deg, #3a8ee6 0%, #5c9ce6 100%);
    color: #fff;
}

.message.assistant .avatar {
    background: linear-gradient(135deg, #9c27b0 0%, #ba68c8 100%);
    color: #fff;
}

.bubble {
    max-width: 70%;
    padding: 14px 20px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.7;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    word-break: break-word;
    position: relative;
    transition: all 0.3s ease;
}

.message.user .bubble {
    background: linear-gradient(135deg, #3a8ee6 0%, #5c9ce6 100%);
    color: #fff;
    border-bottom-right-radius: 4px;
    margin-right: 8px;
}

.message.assistant .bubble {
    background: #fff;
    color: #333;
    border-bottom-left-radius: 4px;
    margin-left: 8px;
}

.reply-bubble {
    background: #f0f7ff !important;
    color: #333 !important;
    border-left: 3px solid #3a8ee6;
}

.thinking-bubble {
    background: #fff8e1 !important;
    color: #795548 !important;
    border-left: 3px dashed #ffc107;
    font-style: italic;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        opacity: 0.7;
    }

    50% {
        opacity: 1;
    }

    100% {
        opacity: 0.7;
    }
}

.dialogue-input-area {
    display: flex;
    align-items: center;
    padding: 20px 32px 0;
    background: #fff;
    border-top: 1px solid #f0f0f0;
    position: relative;
    z-index: 2;
}

.dialogue-input {
    flex: 1;
    margin-right: 16px;
}

.dialogue-input :deep(.el-input__inner) {
    border-radius: 24px;
    padding: 12px 20px;
    height: 48px;
    font-size: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    border: 1px solid #e8eaec;
    transition: all 0.3s;
}

.dialogue-input :deep(.el-input__inner:focus) {
    border-color: #3a8ee6;
    box-shadow: 0 0 0 2px rgba(58, 142, 230, 0.2);
}

.send-btn {
    min-width: 100px;
    font-weight: 500;
    font-size: 15px;
    border-radius: 24px;
    height: 48px;
    background: linear-gradient(135deg, #3a8ee6 0%, #5c9ce6 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(58, 142, 230, 0.3);
    transition: all 0.3s;
}

.send-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(58, 142, 230, 0.4);
}

.send-btn:active {
    transform: translateY(0);
}

.send-btn:disabled {
    background: #e0e0e0;
    box-shadow: none;
}

.thinking-content {
    background: linear-gradient(135deg, #fff8e1 60%, #fffde7 100%);
    padding: 16px 20px;
    margin-bottom: 14px;
    border-radius: 12px;
    border-left: 4px dashed #ffc107;
    box-shadow: 0 2px 8px rgba(255, 193, 7, 0.08);
    position: relative;
    transition: box-shadow 0.3s;
}

.thinking-content::before {
    content: "💡";
    position: absolute;
    left: -32px;
    top: 16px;
    font-size: 22px;
    color: #ffc107;
}

.thinking-label {
    font-weight: bold;
    color: #b28704;
    margin-bottom: 8px;
    font-size: 16px;
    letter-spacing: 1px;
}

.thinking-text {
    font-style: italic;
    color: #795548;
    white-space: pre-wrap;
    font-size: 15px;
    line-height: 1.8;
}

.response-content {
    background: linear-gradient(135deg, #f0f7ff 60%, #e3f2fd 100%);
    color: #333;
    padding: 16px 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(58, 142, 230, 0.08);
    border-left: 4px solid #3a8ee6;
    margin-bottom: 8px;
    font-size: 15px;
    line-height: 1.8;
    position: relative;
    transition: box-shadow 0.3s;
}

.response-content::before {
    content: "🤖";
    position: absolute;
    left: -32px;
    top: 16px;
    font-size: 22px;
    color: #3a8ee6;
}

.response-content :deep(pre) {
    background: #e3f2fd;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 8px 0;
}

.response-content :deep(code) {
    background: #e1f5fe;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    color: #1976d2;
}

.response-content :deep(blockquote) {
    border-left: 4px solid #90caf9;
    padding-left: 14px;
    color: #1976d2;
    margin: 12px 0;
    background: #f1f8ff;
    border-radius: 6px;
}

.response-content :deep(ul),
.response-content :deep(ol) {
    padding-left: 24px;
}

.response-content :deep(table) {
    border-collapse: collapse;
    width: 100%;
    background: #f8fafd;
}

.response-content :deep(th),
.response-content :deep(td) {
    border: 1px solid #b3e5fc;
    padding: 8px;
}

.response-content :deep(th) {
    background-color: #b3e5fc;
    color: #1565c0;
}
</style>