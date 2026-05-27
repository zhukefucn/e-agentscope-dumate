<template>
  <el-card class="agent-card" shadow="hover" @click="handleClick">
    <template #header>
      <div class="card-header">
        <div class="agent-icon">
          <el-icon :size="28"><Avatar /></el-icon>
        </div>
        <div class="agent-title">
          <h3 class="agent-name">{{ agent.name }}</h3>
          <el-tag size="small" type="info">{{ agent.model_name }}</el-tag>
        </div>
      </div>
    </template>
    
    <div class="agent-description">
      {{ agent.description || '暂无描述' }}
    </div>
    
    <div class="agent-meta">
      <div class="meta-item">
        <el-icon><Clock /></el-icon>
        <span>{{ formattedDate }}</span>
      </div>
      <div v-if="agent.tools.length > 0" class="meta-item">
        <el-icon><Tools /></el-icon>
        <span>{{ agent.tools.length }} 个工具</span>
      </div>
    </div>
    
    <div v-if="$slots.actions" class="agent-actions" @click.stop>
      <slot name="actions"></slot>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Agent } from '@/types/agent'
import { Avatar, Clock, Tools } from '@element-plus/icons-vue'

const props = defineProps<{
  agent: Agent
}>()

const router = useRouter()

// 格式化日期
const formattedDate = computed(() => {
  const date = new Date(props.agent.created_at)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})

// 点击卡片
function handleClick() {
  router.push(`/chat/${props.agent.id}`)
}
</script>

<style scoped>
.agent-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.agent-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  border-radius: 10px;
  color: #fff;
}

.agent-title {
  flex: 1;
  min-width: 0;
}

.agent-name {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-description {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 44px;
}

.agent-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.agent-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.agent-actions :deep(.el-button) {
  flex: 1;
}
</style>
