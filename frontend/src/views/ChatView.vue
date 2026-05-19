<template>
  <div class="chat-container">
    <header class="chat-header">
      <select v-model="selectedPersona" class="persona-select">
        <option v-for="p in personas" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
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
      <div v-if="messages.length === 0" class="empty-hint">选择一个角色，开始聊天吧～</div>
      <div
        v-for="(m, i) in messages"
        :key="i"
        :class="['msg', m.role === 'user' ? 'msg-user' : 'msg-ai']"
      >
        <div class="msg-bubble">{{ m.content }}</div>
      </div>
      <div v-if="loading" class="msg msg-ai">
        <div class="msg-bubble typing">猪猪正在输入...</div>
      </div>
    </div>

    <div class="input-area">
      <input
        v-model="input"
        @keyup.enter="send"
        placeholder="说点什么..."
        :disabled="loading"
      />
      <button @click="send" :disabled="loading || !input.trim()">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from "vue";
import http from "../api/http.js";

const personas = ref([]);
const selectedPersona = ref(null);
const conversations = ref([]);
const conversationId = ref(null);
const messages = ref([]);
const input = ref("");
const loading = ref(false);
const msgBox = ref(null);

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
    messages.value.push({ role: "assistant", content: "呜呜呜网络好像出问题了，你等等再试试嘛！[大哭]" });
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
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fff;
}

.chat-header {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  background: #ff6b81;
  align-items: center;
}

.persona-select {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
}

.btn-new {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: #fff;
  color: #ff6b81;
  font-weight: bold;
  cursor: pointer;
  white-space: nowrap;
}

.conv-list {
  display: flex;
  gap: 6px;
  padding: 8px 16px;
  background: #ffeef0;
  overflow-x: auto;
}

.conv-item {
  padding: 4px 12px;
  border-radius: 12px;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  border: 1px solid #ffcdd5;
}

.conv-item.active {
  background: #ff6b81;
  color: #fff;
  border-color: #ff6b81;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-hint {
  text-align: center;
  color: #aaa;
  margin-top: 40px;
  font-size: 15px;
}

.msg {
  display: flex;
}

.msg-user {
  justify-content: flex-end;
}

.msg-ai {
  justify-content: flex-start;
}

.msg-bubble {
  max-width: 75%;
  padding: 10px 16px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg-user .msg-bubble {
  background: #ff6b81;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg-ai .msg-bubble {
  background: #f0f0f0;
  color: #333;
  border-bottom-left-radius: 4px;
}

.typing {
  color: #999;
  font-style: italic;
}

.input-area {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid #eee;
}

.input-area input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 15px;
  outline: none;
}

.input-area input:focus {
  border-color: #ff6b81;
}

.input-area button {
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  background: #ff6b81;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}

.input-area button:disabled {
  background: #ffcdd5;
  cursor: not-allowed;
}
</style>
