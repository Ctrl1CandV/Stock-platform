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
                    <span>{{ msg.content }}</span>
                </div>
            </div>
            <!-- 思考内容单独展示 -->
            <div v-if="thinking" class="message assistant">
                <div class="avatar">
                    <i class="el-icon-cpu"></i>
                </div>
                <div class="bubble thinking-bubble">
                    <span>思考中：{{ thinking }}</span>
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
export default {
    name: "ModelDialogue",
    data() {
        return {
            messages: [],
            inputText: '',
            thinking: '', // 新增：用于存储思考内容
            loading: false,
        }
    },
    methods: {
        async handleSend() {
            if (!this.inputText.trim()) return;

            // 添加用户消息
            this.messages.push({ role: 'user', content: this.inputText });

            // 清空思考内容
            this.thinking = '';
            this.loading = true;

            // 使用 Fetch 发送 POST 请求
            const response = await fetch('http://192.168.1.67:8000/user/dialogueLocalModel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content: this.inputText })
            });

            if (!response.ok) {
                this.messages.push({ role: 'assistant', content: 'Error: ' + response.statusText });
                this.loading = false;
                return;
            }

            // 读取流式数据
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let done = false;
            let buffer = '';
            let reply = '';

            while (!done) {
                const { value, done: doneReading } = await reader.read();
                done = doneReading;
                if (value) {
                    buffer += decoder.decode(value, { stream: true });
                    let eventEnd = buffer.indexOf('\n\n');
                    while (eventEnd !== -1) {
                        const event = buffer.slice(0, eventEnd);
                        buffer = buffer.slice(eventEnd + 2);
                        if (event.startsWith('data: ')) {
                            const data = event.slice(6).trim();
                            if (data) {
                                // 这里假设流式内容就是思考内容，最后一次为回复
                                this.thinking += data;
                                this.$nextTick(() => {
                                    const content = this.$refs.dialogueContent;
                                    content.scrollTop = content.scrollHeight;
                                });
                            }
                        }
                        eventEnd = buffer.indexOf('\n\n');
                    }
                }
            }

            // 流式结束后，将思考内容作为最终回复，清空思考内容
            reply = this.thinking;
            this.thinking = '';
            this.messages.push({ role: 'assistant', content: reply });
            this.inputText = '';
            this.loading = false;
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
</style>