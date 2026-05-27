<template>
  <div class="agent-list-container">
    <div class="page-header">
      <h1>Agent 管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建 Agent
      </el-button>
    </div>

    <el-card v-loading="loading" class="agent-card">
      <el-empty v-if="!loading && agents.length === 0" description="暂无 Agent，点击上方按钮创建">
        <el-button type="primary" @click="handleCreate">立即创建</el-button>
      </el-empty>

      <el-table v-else :data="agents" stripe style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="150">
          <template #default="{ row }">
            <div class="agent-name">
              <el-icon class="agent-icon"><Monitor /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="description-text">{{ row.description || '暂无描述' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="模型" width="180">
          <template #default="{ row }">
            <el-tag type="info">{{ row.model_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tools" label="工具" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="tool in row.tools?.slice(0, 3)"
              :key="tool"
              size="small"
              class="tool-tag"
            >
              {{ tool }}
            </el-tag>
            <el-tag v-if="row.tools?.length > 3" size="small" type="info">
              +{{ row.tools.length - 3 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="handleChat(row)">
                <el-icon><ChatDotRound /></el-icon>
                对话
              </el-button>
              <el-button size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > pageSize" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchAgents"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Monitor, ChatDotRound, Edit, Delete } from '@element-plus/icons-vue'
import { agentApi } from '@/services/agent'
import type { Agent } from '@/types/agent'

const router = useRouter()

const loading = ref(false)
const agents = ref<Agent[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取 Agent 列表
async function fetchAgents() {
  try {
    loading.value = true
    const response = await agentApi.getAgents({
      page: currentPage.value,
      page_size: pageSize.value,
    })
    agents.value = response.agents
    total.value = response.total
  } catch (error) {
    console.error('获取 Agent 列表失败:', error)
    ElMessage.error('获取 Agent 列表失败')
  } finally {
    loading.value = false
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 创建新 Agent
function handleCreate() {
  router.push('/agents/create')
}

// 编辑 Agent
function handleEdit(agent: Agent) {
  router.push(`/agents/${agent.id}/edit`)
}

// 开始对话
function handleChat(agent: Agent) {
  router.push(`/chat/${agent.id}`)
}

// 删除 Agent
async function handleDelete(agent: Agent) {
  try {
    await ElMessageBox.confirm(
      `确定要删除 Agent "${agent.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await agentApi.deleteAgent(agent.id)
    ElMessage.success('删除成功')
    await fetchAgents()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除 Agent 失败:', error)
      ElMessage.error('删除 Agent 失败')
    }
  }
}

onMounted(() => {
  fetchAgents()
})
</script>

<style scoped>
.agent-list-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.agent-card {
  border-radius: 8px;
}

.agent-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.agent-icon {
  color: #409eff;
  font-size: 18px;
}

.description-text {
  color: #606266;
}

.tool-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

:deep(.el-button-group) {
  display: flex;
}

:deep(.el-button-group .el-button) {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
