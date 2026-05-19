<template>
  <div class="chat-container">
    <header class="chat-header">
      <div class="header-left">
        <div class="avatar">🐷</div>
        <div class="header-info">
          <div class="header-name">{{ personaName }}</div>
          <div class="header-desc">ENFP射手座 · 话痨小天才</div>
        </div>
      </div>
      <button @click="newChat" class="btn-new">+ 新对话</button>
    </header>

    <div class="conv-list" v-if="conversations.length">
      <div
        v-for="c in conversations"
        :key="c.id"
        :class="['conv-item', { active: c.id === conversationId }]"
        @click="switchConv(c.id)"
      >
        {{ c.title }}
      </div>
    </div>

    <div class="messages" ref="msgBox">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-avatar">🐷</div>
        <div class="empty-text">嗨！我是猪猪～</div>
        <div class="empty-sub">发个消息开始聊天吧！</div>
      </div>
      <div
        v-for="(m, i) in messages"
        :key="i"
        :class="['msg-row', m.role === 'user' ? 'row-user' : 'row-ai']"
      >
        <div v-if="m.role === 'assistant'" class="msg-avatar">🐷</div>
        <div class="msg-content">
          <div :class="['msg-bubble', m.role === 'user' ? 'bubble-user' : 'bubble-ai']">{{ m.content }}</div>
        </div>
      </div>
      <div v-if="loading" class="msg-row row-ai">
        <div class="msg-avatar">🐷</div>
        <div class="msg-content">
          <div class="msg-bubble bubble-ai typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="input-area">
      <div class="input-wrapper">
        <input
          v-model="input"
          @keyup.enter="send"
          placeholder="说点什么..."
          :disabled="loading"
          class="input-field"
        />
        <button @click="send" :disabled="loading || !input.trim()" class="btn-send">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, computed } from "vue";
import http from "../api/http.js";

const personas = ref([]);
const selectedPersona = ref(null);
const conversations = ref([]);
const conversationId = ref(null);
const messages = ref([]);
const input = ref("");
const loading = ref(false);
const msgBox = ref(null);

const personaName = computed(() => {
  const p = personas.value.find(p => p.id === selectedPersona.value);
  return p ? p.name : "猪猪";
});

onMounted(async () => {
  const res = await http.get("/chat/personas");
  personas.value = res.data;
  if (personas.value.length) {
    selectedPersona.value = personas.value[0].id;
  }
});

watch(selectedPersona, async (pid) => {
  if (!pid) return;
  const res = await http.get("/chat/conversations", { params: { persona_id: pid } });
  conversations.value = res.data;
  conversationId.value = null;
  messages.value = [];
});

async function newChat() {
  conversationId.value = null;
  messages.value = [];
}

async function switchConv(cid) {
  conversationId.value = cid;
  const res = await http.get(`/chat/messages/${cid}`);
  messages.value = res.data;
  scrollDown();
}

async function send() {
  if (!input.value.trim() || loading.value) return;
  const msg = input.value.trim();
  const pid = selectedPersona.value;
  input.value = "";
  messages.value.push({ role: "user", content: msg });
  loading.value = true;
  scrollDown();

  try {
    const res = await http.post("/chat", {
      persona_id: pid,
      conversation_id: conversationId.value,
      message: msg,
    });
    conversationId.value = res.data.conversation_id;
    messages.value.push({ role: "assistant", content: res.data.reply });

    if (!conversations.value.find((c) => c.id === res.data.conversation_id)) {
      conversations.value.unshift({
        id: res.data.conversation_id,
        title: msg.slice(0, 30),
      });
    }
  } catch (e) {
    messages.value.push({ role: "assistant", content: "呜呜呜网络好像出问题了，你等等再试试嘛！" });
  } finally {
    loading.value = false;
    scrollDown();
  }
}

function scrollDown() {
  nextTick(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight;
  });
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(180deg, #fef0f3 0%, #f9f9f9 100%);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: linear-gradient(135deg, #ff6b81 0%, #ff8e9e 100%);
  box-shadow: 0 2px 12px rgba(255, 107, 129, 0.3);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 42px;
  height: 42px;
  background: rgba(255,255,255,0.25);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  backdrop-filter: blur(4px);
}

.header-info {
  display: flex;
  flex-direction: column;
}

.header-name {
  color: #fff;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.header-desc {
  color: rgba(255,255,255,0.8);
  font-size: 12px;
  margin-top: 1px;
}

.btn-new {
  padding: 7px 16px;
  border: 1.5px solid rgba(255,255,255,0.4);
  border-radius: 20px;
  background: rgba(255,255,255,0.15);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: all 0.2s;
}

.btn-new:hover {
  background: rgba(255,255,255,0.28);
}

.conv-list {
  display: flex;
  gap: 8px;
  padding: 10px 18px;
  background: #fff;
  overflow-x: auto;
  border-bottom: 1px solid #f0f0f0;
}

.conv-item {
  padding: 6px 14px;
  border-radius: 16px;
  background: #f5f5f5;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  color: #666;
}

.conv-item:hover {
  background: #ffe0e5;
}

.conv-item.active {
  background: #ff6b81;
  color: #fff;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  text-align: center;
  margin-top: 80px;
}

.empty-avatar {
  font-size: 64px;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.empty-text {
  font-size: 22px;
  font-weight: 700;
  color: #ff6b81;
  margin-bottom: 6px;
}

.empty-sub {
  font-size: 14px;
  color: #999;
}

.msg-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.row-user {
  justify-content: flex-end;
}

.row-ai {
  justify-content: flex-start;
}

.msg-avatar {
  width: 34px;
  height: 34px;
  min-width: 34px;
  background: linear-gradient(135deg, #ffe0e5, #ffcdd5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.msg-content {
  max-width: 78%;
  display: flex;
  flex-direction: column;
}

.msg-bubble {
  padding: 10px 16px;
  border-radius: 20px;
  font-size: 15px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
  letter-spacing: 0.3px;
}

.bubble-user {
  background: linear-gradient(135deg, #ff6b81, #ff8e9e);
  color: #fff;
  border-bottom-right-radius: 6px;
  box-shadow: 0 2px 8px rgba(255, 107, 129, 0.25);
}

.bubble-ai {
  background: #fff;
  color: #333;
  border-bottom-left-radius: 6px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.typing-dots {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 14px 20px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }
.typing-dots span:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.input-area {
  padding: 12px 18px 16px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f5f5f5;
  border-radius: 24px;
  padding: 4px 4px 4px 18px;
  transition: all 0.25s;
  border: 1.5px solid transparent;
}

.input-wrapper:focus-within {
  border-color: #ff6b81;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(255, 107, 129, 0.1);
}

.input-field {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  outline: none;
  padding: 10px 0;
  color: #333;
}

.input-field::placeholder {
  color: #bbb;
}

.btn-send {
  width: 40px;
  height: 40px;
  min-width: 40px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b81, #ff8e9e);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-send:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(255, 107, 129, 0.4);
}

.btn-send:disabled {
  background: #ffcdd5;
  cursor: not-allowed;
  transform: none;
}
</style>
