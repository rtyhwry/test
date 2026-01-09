<template>
  <div class="task-detail" v-loading="loading">
    <div class="page-header">
      <div>
        <el-button @click="$router.back()" :icon="ArrowLeft" />
        <h1 class="page-title" style="display: inline; margin-left: 10px;">
          {{ task?.name || '任务详情' }}
        </h1>
        <el-tag :class="'status-tag ' + task?.status" style="margin-left: 10px;">
          {{ task?.status_display }}
        </el-tag>
      </div>
      <div>
        <el-button type="primary" @click="executeTask" :disabled="task?.status === 'running'">
          <el-icon><VideoPlay /></el-icon>执行任务
        </el-button>
      </div>
    </div>
    
    <!-- Task Info -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>基本信息</template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="任务名称">{{ task?.name }}</el-descriptions-item>
            <el-descriptions-item label="所属项目">{{ task?.project_name }}</el-descriptions-item>
            <el-descriptions-item label="测试环境">{{ task?.environment_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="调度类型">{{ task?.schedule_type_display }}</el-descriptions-item>
            <el-descriptions-item label="需要升级">{{ task?.need_upgrade ? '是' : '否' }}</el-descriptions-item>
            <el-descriptions-item label="创建人">{{ task?.created_by_name }}</el-descriptions-item>
            <el-descriptions-item label="Git仓库" :span="2">{{ task?.git_repo_url || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Git分支">{{ task?.git_branch }}</el-descriptions-item>
            <el-descriptions-item label="超时时间">{{ task?.timeout_minutes }} 分钟</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ task?.description || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <!-- Execution History -->
        <el-card style="margin-top: 20px;">
          <template #header>执行历史</template>
          <el-table :data="executions" style="width: 100%">
            <el-table-column prop="execution_number" label="#" width="60" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :class="'status-tag ' + row.status" size="small">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="用例统计" width="150">
              <template #default="{ row }">
                <span class="text-success">{{ row.passed_cases }}</span> /
                <span class="text-danger">{{ row.failed_cases }}</span> /
                {{ row.total_cases }}
              </template>
            </el-table-column>
            <el-table-column prop="pass_rate" label="通过率" width="100">
              <template #default="{ row }">
                <el-progress :percentage="row.pass_rate" :status="row.pass_rate >= 80 ? 'success' : row.pass_rate >= 60 ? 'warning' : 'exception'" />
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="duration_seconds" label="执行时长" width="100">
              <template #default="{ row }">
                {{ formatDuration(row.duration_seconds) }}
              </template>
            </el-table-column>
            <el-table-column prop="triggered_by_display" label="触发方式" width="100" />
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <!-- Statistics -->
        <el-card>
          <template #header>执行统计</template>
          <div class="stat-item">
            <span class="stat-label">总执行次数</span>
            <span class="stat-value">{{ task?.execution_count || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">最近通过率</span>
            <span class="stat-value">{{ task?.last_execution_info?.pass_rate || 0 }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">最近执行</span>
            <span class="stat-value">{{ formatTime(task?.last_execution_info?.start_time) || '-' }}</span>
          </div>
        </el-card>
        
        <!-- Test Cases -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>测试用例</span>
              <el-button type="primary" link size="small">管理用例</el-button>
            </div>
          </template>
          <el-table :data="testCases" max-height="300">
            <el-table-column prop="case_code" label="编号" width="80" />
            <el-table-column prop="name" label="名称" show-overflow-tooltip />
            <el-table-column prop="priority" label="优先级" width="70">
              <template #default="{ row }">
                <el-tag size="small" :type="priorityType(row.priority)">
                  {{ row.priority }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, VideoPlay } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import api from '@/api'

const route = useRoute()
const taskId = route.params.id

const loading = ref(false)
const task = ref(null)
const executions = ref([])
const testCases = ref([])

const formatTime = (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}m ${secs}s`
}

const priorityType = (priority) => {
  const map = { critical: 'danger', high: 'warning', medium: '', low: 'info' }
  return map[priority] || ''
}

const fetchTask = async () => {
  loading.value = true
  try {
    const response = await api.tasks.get(taskId)
    task.value = response.data
  } catch (error) {
    console.error('Failed to fetch task:', error)
  } finally {
    loading.value = false
  }
}

const fetchExecutions = async () => {
  try {
    const response = await api.tasks.executions(taskId)
    executions.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch executions:', error)
  }
}

const fetchTestCases = async () => {
  try {
    const response = await api.testcases.list({ task: taskId, page_size: 100 })
    testCases.value = response.data.results || []
  } catch (error) {
    console.error('Failed to fetch test cases:', error)
  }
}

const executeTask = async () => {
  try {
    await api.tasks.execute(taskId, {})
    ElMessage.success('任务已开始执行')
    fetchTask()
    fetchExecutions()
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

onMounted(() => {
  fetchTask()
  fetchExecutions()
  fetchTestCases()
})
</script>

<style lang="scss" scoped>
.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  
  &:last-child {
    border-bottom: none;
  }
  
  .stat-label {
    color: #909399;
  }
  
  .stat-value {
    font-weight: bold;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}
</style>
