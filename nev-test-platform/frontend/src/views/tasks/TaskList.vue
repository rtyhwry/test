<template>
  <div class="task-list">
    <div class="page-header">
      <h1 class="page-title">任务管理</h1>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>新建任务
      </el-button>
    </div>
    
    <!-- Search & Filter -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="项目">
          <el-select v-model="filters.project" placeholder="选择项目" clearable>
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="待执行" value="pending" />
            <el-option label="执行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="调度类型">
          <el-select v-model="filters.schedule_type" placeholder="选择类型" clearable>
            <el-option label="立即执行" value="immediate" />
            <el-option label="定时执行" value="scheduled" />
            <el-option label="周期执行" value="cron" />
            <el-option label="手动触发" value="manual" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchTasks">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- Task Table -->
    <el-card>
      <el-table :data="tasks" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="任务名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewTask(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="项目" width="150" />
        <el-table-column prop="schedule_type_display" label="调度类型" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :class="'status-tag ' + row.status" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_execution_info" label="最近执行" width="180">
          <template #default="{ row }">
            <span v-if="row.last_execution_info">
              {{ formatTime(row.last_execution_info.start_time) }}
              <el-tag size="small" :class="'status-tag ' + row.last_execution_info.status">
                {{ row.last_execution_info.pass_rate }}%
              </el-tag>
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="executeTask(row)">执行</el-button>
            <el-button type="primary" link @click="editTask(row)">编辑</el-button>
            <el-popconfirm title="确定删除此任务?" @confirm="deleteTask(row)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next"
        @change="fetchTasks"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
    
    <!-- Create/Edit Dialog -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑任务' : '新建任务'"
      width="700px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="项目" prop="project">
          <el-select v-model="form.project" placeholder="选择项目" style="width: 100%;">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试环境" prop="environment">
          <el-select v-model="form.environment" placeholder="选择环境" style="width: 100%;" clearable>
            <el-option v-for="e in environments" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="调度类型" prop="schedule_type">
          <el-select v-model="form.schedule_type" style="width: 100%;">
            <el-option label="手动触发" value="manual" />
            <el-option label="立即执行" value="immediate" />
            <el-option label="定时执行" value="scheduled" />
            <el-option label="周期执行" value="cron" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.schedule_type === 'scheduled'" label="执行时间" prop="scheduled_time">
          <el-date-picker v-model="form.scheduled_time" type="datetime" placeholder="选择执行时间" style="width: 100%;" />
        </el-form-item>
        <el-form-item v-if="form.schedule_type === 'cron'" label="Cron表达式" prop="cron_expression">
          <el-input v-model="form.cron_expression" placeholder="如: 0 2 * * *" />
        </el-form-item>
        <el-form-item label="需要升级" prop="need_upgrade">
          <el-switch v-model="form.need_upgrade" />
        </el-form-item>
        <el-form-item v-if="form.need_upgrade" label="升级制品" prop="artifact">
          <el-select v-model="form.artifact" placeholder="选择制品" style="width: 100%;">
            <el-option v-for="a in artifacts" :key="a.id" :label="`${a.name} v${a.version}`" :value="a.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Git仓库" prop="git_repo_url">
          <el-input v-model="form.git_repo_url" placeholder="Git仓库地址" />
        </el-form-item>
        <el-form-item label="Git分支" prop="git_branch">
          <el-input v-model="form.git_branch" placeholder="分支名称" />
        </el-form-item>
        <el-form-item label="测试命令" prop="test_command">
          <el-input v-model="form.test_command" type="textarea" :rows="3" placeholder="测试执行命令" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="任务描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const tasks = ref([])
const projects = ref([])
const environments = ref([])
const artifacts = ref([])

const filters = reactive({
  project: '',
  status: '',
  schedule_type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  name: '',
  project: '',
  environment: '',
  schedule_type: 'manual',
  scheduled_time: '',
  cron_expression: '',
  need_upgrade: false,
  artifact: '',
  git_repo_url: '',
  git_branch: 'main',
  test_command: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  project: [{ required: true, message: '请选择项目', trigger: 'change' }]
}

const formatTime = (time) => time ? dayjs(time).format('MM-DD HH:mm') : '-'

const fetchTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }
    const response = await api.tasks.list(params)
    tasks.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await api.projects.list({ page_size: 100 })
    projects.value = response.data.results || []
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  }
}

const fetchEnvironments = async () => {
  try {
    const response = await api.environments.available()
    environments.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch environments:', error)
  }
}

const fetchArtifacts = async () => {
  try {
    const response = await api.artifacts.list({ page_size: 100 })
    artifacts.value = response.data.results || []
  } catch (error) {
    console.error('Failed to fetch artifacts:', error)
  }
}

const resetFilters = () => {
  Object.keys(filters).forEach(key => filters[key] = '')
  fetchTasks()
}

const showCreateDialog = () => {
  isEdit.value = false
  Object.keys(form).forEach(key => {
    form[key] = key === 'schedule_type' ? 'manual' : key === 'git_branch' ? 'main' : key === 'need_upgrade' ? false : ''
  })
  dialogVisible.value = true
}

const viewTask = (row) => {
  router.push(`/tasks/${row.id}`)
}

const editTask = (row) => {
  isEdit.value = true
  Object.keys(form).forEach(key => {
    form[key] = row[key] ?? ''
  })
  form.id = row.id
  dialogVisible.value = true
}

const executeTask = async (row) => {
  try {
    await api.tasks.execute(row.id, {})
    ElMessage.success('任务已开始执行')
    fetchTasks()
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const deleteTask = async (row) => {
  try {
    await api.tasks.delete(row.id)
    ElMessage.success('删除成功')
    fetchTasks()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await api.tasks.update(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await api.tasks.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchTasks()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchTasks()
  fetchProjects()
  fetchEnvironments()
  fetchArtifacts()
})
</script>

<style lang="scss" scoped>
.filter-card {
  margin-bottom: 20px;
}

.text-muted {
  color: #909399;
}
</style>
