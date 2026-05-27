<template>
  <div class="agent-create-container">
    <div class="page-header">
      <el-page-header @back="handleBack">
        <template #content>
          <span class="page-title">{{ isEdit ? '编辑 Agent' : '创建 Agent' }}</span>
        </template>
      </el-page-header>
    </div>

    <el-card v-loading="loading" class="form-card">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        label-position="right"
        class="agent-form"
      >
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入 Agent 名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入 Agent 描述（可选）"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="系统提示词" prop="system_prompt">
          <el-input
            v-model="formData.system_prompt"
            type="textarea"
            placeholder="请输入系统提示词，定义 Agent 的行为和角色"
            :rows="5"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <el-divider content-position="left">模型配置</el-divider>

        <el-form-item label="模型提供商" prop="model_provider">
          <el-select
            v-model="formData.model_provider"
            placeholder="请选择模型提供商"
            style="width: 100%"
            @change="handleProviderChange"
          >
            <el-option
              v-for="provider in modelProviders"
              :key="provider.value"
              :label="provider.label"
              :value="provider.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="模型名称" prop="model_name">
          <el-select
            v-if="presetModels.length > 0"
            v-model="formData.model_name"
            placeholder="请选择模型"
            style="width: 100%"
            filterable
            allow-create
          >
            <el-option
              v-for="model in presetModels"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
          <el-input
            v-else
            v-model="formData.model_name"
            placeholder="请输入模型名称，如 gpt-4、qwen-max 等"
          />
        </el-form-item>

        <el-form-item label="API Key" prop="api_key">
          <el-input
            v-model="formData.api_key"
            type="password"
            placeholder="请输入 API Key（可选，留空使用系统默认）"
            show-password
          />
          <div class="form-tip">
            API Key 将被加密存储，留空则使用系统默认配置
          </div>
        </el-form-item>

        <el-divider content-position="left">工具配置</el-divider>

        <el-form-item label="可用工具" prop="tools">
          <el-checkbox-group v-model="formData.tools" class="tools-checkbox-group">
            <el-checkbox
              v-for="tool in availableTools"
              :key="tool.value"
              :label="tool.value"
              class="tool-checkbox"
            >
              <div class="tool-item">
                <span class="tool-name">{{ tool.label }}</span>
                <span class="tool-desc">{{ tool.description }}</span>
              </div>
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-divider content-position="left">高级设置</el-divider>

        <el-form-item label="Temperature">
          <div class="slider-container">
            <el-slider
              v-model="formData.temperature"
              :min="0"
              :max="2"
              :step="0.1"
              show-input
              :show-input-controls="false"
            />
            <div class="slider-tip">
              较低的值使输出更确定，较高的值使输出更随机
            </div>
          </div>
        </el-form-item>

        <el-form-item label="Max Tokens">
          <el-input-number
            v-model="formData.max_tokens"
            :min="100"
            :max="128000"
            :step="100"
            controls-position="right"
          />
          <div class="form-tip">
            限制生成的最大 token 数量，建议根据模型能力设置
          </div>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-button @click="handleBack">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '创建 Agent' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { agentApi } from '@/services/agent'
import type { Agent } from '@/types/agent'

const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)

// 判断是否为编辑模式
const isEdit = computed(() => !!route.params.id)
const agentId = computed(() => route.params.id as string)

// 模型提供商列表
const modelProviders = [
  { value: 'dashscope', label: '阿里云灵积 (DashScope)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'ollama', label: 'Ollama (本地)' },
  { value: 'custom', label: '自定义' },
]

// 预设模型列表
const providerModels: Record<string, string[]> = {
  dashscope: ['qwen-max', 'qwen-plus', 'qwen-turbo', 'qwen-long', 'qwen-vl-max'],
  openai: ['gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
  deepseek: ['deepseek-chat', 'deepseek-coder'],
  ollama: ['llama3', 'llama2', 'mistral', 'codellama', 'qwen2'],
  custom: [],
}

const presetModels = computed(() => {
  return providerModels[formData.model_provider] || []
})

// 可用工具列表
const availableTools = [
  { value: 'Bash', label: 'Bash', description: '执行 Shell 命令' },
  { value: 'Read', label: 'Read', description: '读取文件内容' },
  { value: 'Write', label: 'Write', description: '写入文件' },
  { value: 'Edit', label: 'Edit', description: '编辑文件' },
  { value: 'Grep', label: 'Grep', description: '搜索文件内容' },
  { value: 'Glob', label: 'Glob', description: '查找文件' },
]

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  system_prompt: '',
  model_provider: 'dashscope',
  model_name: '',
  api_key: '',
  tools: [] as string[],
  temperature: 0.7,
  max_tokens: 4096,
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入 Agent 名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  model_provider: [
    { required: true, message: '请选择模型提供商', trigger: 'change' },
  ],
  model_name: [
    { required: true, message: '请输入或选择模型名称', trigger: 'blur' },
  ],
  tools: [
    {
      type: 'array',
      min: 1,
      message: '请至少选择一个工具',
      trigger: 'change',
    },
  ],
}

// 处理提供商变更
function handleProviderChange() {
  const models = providerModels[formData.model_provider]
  if (models.length > 0) {
    formData.model_name = models[0]
  } else {
    formData.model_name = ''
  }
}

// 获取 Agent 详情（编辑模式）
async function fetchAgent() {
  if (!isEdit.value) return

  try {
    loading.value = true
    const agent = await agentApi.getAgent(agentId.value)
    
    formData.name = agent.name
    formData.description = agent.description || ''
    formData.system_prompt = agent.system_prompt || ''
    formData.model_name = agent.model_name
    formData.tools = agent.tools || []
    formData.temperature = agent.temperature ?? 0.7
    formData.max_tokens = agent.max_tokens ?? 4096

    // 根据模型名称推断提供商
    inferProviderFromModel(agent.model_name)
  } catch (error) {
    console.error('获取 Agent 详情失败:', error)
    ElMessage.error('获取 Agent 详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 根据模型名称推断提供商
function inferProviderFromModel(modelName: string) {
  if (modelName.includes('qwen')) {
    formData.model_provider = 'dashscope'
  } else if (modelName.includes('gpt')) {
    formData.model_provider = 'openai'
  } else if (modelName.includes('deepseek')) {
    formData.model_provider = 'deepseek'
  } else {
    formData.model_provider = 'custom'
  }
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  try {
    submitting.value = true

    // 构建请求数据
    const requestData = {
      name: formData.name,
      description: formData.description,
      system_prompt: formData.system_prompt,
      model_name: formData.model_name,
      tools: formData.tools,
      temperature: formData.temperature,
      max_tokens: formData.max_tokens,
    }

    if (isEdit.value) {
      await agentApi.updateAgent(agentId.value, requestData)
      ElMessage.success('更新成功')
    } else {
      await agentApi.createAgent(requestData)
      ElMessage.success('创建成功')
    }

    router.push('/agents')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

// 返回列表
function handleBack() {
  router.push('/agents')
}

onMounted(() => {
  // 初始化默认模型
  handleProviderChange()
  
  // 编辑模式下获取详情
  if (isEdit.value) {
    fetchAgent()
  }
})
</script>

<style scoped>
.agent-create-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.form-card {
  border-radius: 8px;
}

.agent-form {
  padding: 20px 40px 0;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.tools-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tool-checkbox {
  height: auto;
  margin-right: 0;
}

.tool-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tool-name {
  font-weight: 500;
  color: #303133;
}

.tool-desc {
  font-size: 12px;
  color: #909399;
}

.slider-container {
  width: 100%;
}

.slider-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.form-actions {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.form-actions :deep(.el-form-item__content) {
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-divider__text) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-slider) {
  padding-right: 60px;
}

:deep(.el-slider__input) {
  width: 60px;
}
</style>
