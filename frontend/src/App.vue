<template>
  <div id="chat-app">
    <ChatView />
  </div>
</template>

<script setup>
import ChatView from "./views/ChatView.vue";
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  background: #f5f5f5;
  color: #333;
}

#chat-app {
  max-width: 800px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
