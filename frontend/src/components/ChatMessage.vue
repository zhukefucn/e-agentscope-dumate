<template>
  <div :class="['chat-message', `message-${message.role}`]">
    <div class="message-avatar">
      <el-avatar
        v-if="message.role === 'user'"
        :size="36"
        :icon="UserFilled"
      />
      <el-avatar
        v-else
        :size="36"
        class="assistant-avatar"
      >
        <el-icon><Monitor /></el-icon>
      </el-avatar>
    </div>
    <div class="message-content">
      <div class="message-header">
        <span class="message-role">{{ roleLabel }}</span>
        <span class="message-time">{{ formattedTime }}</span>
      </div>
      <div class="message-body" v-html="renderedContent"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import type { Message } from '@/types/chat'
import { UserFilled, Monitor } from '@element-plus/icons-vue'

const props = defineProps<{
  message: Message
}>()

// 角色标签
const roleLabel = computed(() => {
  switch (props.message.role) {
    case 'user':
      return '我'
    case 'assistant':
      return 'Agent'
    case 'system':
      return '系统'
    default:
      return props.message.role
  }
})

// 格式化时间
const formattedTime = computed(() => {
  const date = new Date(props.message.created_at)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 一天内显示相对时间
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    // 超过一天显示具体时间
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    
    if (year === now.getFullYear()) {
      return `${month}-${day} ${hours}:${minutes}`
    }
    return `${year}-${month}-${day} ${hours}:${minutes}`
  }
})

// 配置 marked
marked.setOptions({
  highlight: (code: string, lang: string) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch {
        // ignore
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  const content = props.message.content
  
  // 处理代码块，添加复制按钮容器
  let html = marked.parse(content) as string
  
  // 为代码块添加包装器
  html = html.replace(
    /<pre><code class="language-(\w+)">/g,
    '<pre class="code-block"><code class="language-$1 hljs">'
  )
  
  return html
})
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: background-color 0.2s;
}

.message-user {
  background: #f0f7ff;
}

.message-assistant {
  background: #fff;
  border: 1px solid #e8e8e8;
}

.message-system {
  background: #fff7e6;
  border: 1px solid #ffd591;
}

.message-avatar {
  flex-shrink: 0;
}

.assistant-avatar {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.message-role {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.message-body {
  font-size: 14px;
  line-height: 1.7;
  color: #333;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message-body :deep(p) {
  margin: 0 0 12px 0;
}

.message-body :deep(p:last-child) {
  margin-bottom: 0;
}

.message-body :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}

.message-body :deep(.code-block) {
  position: relative;
  background: #282c34;
  border-radius: 6px;
  padding: 16px;
  margin: 12px 0;
  overflow-x: auto;
}

.message-body :deep(.code-block code) {
  background: transparent;
  padding: 0;
  color: #abb2bf;
  font-size: 13px;
  line-height: 1.6;
}

.message-body :deep(ul),
.message-body :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

.message-body :deep(li) {
  margin: 4px 0;
}

.message-body :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 12px;
  margin: 12px 0;
  color: #666;
}

.message-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.message-body :deep(th),
.message-body :deep(td) {
  border: 1px solid #e8e8e8;
  padding: 8px 12px;
  text-align: left;
}

.message-body :deep(th) {
  background: #fafafa;
  font-weight: 600;
}

.message-body :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.message-body :deep(a:hover) {
  text-decoration: underline;
}

.message-body :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}
</style>
