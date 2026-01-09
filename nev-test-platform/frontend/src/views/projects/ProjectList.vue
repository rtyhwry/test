<template>
  <div class="project-list">
    <div class="page-header">
      <h1 class="page-title">项目管理</h1>
      <el-button type="primary" @click="dialogVisible = true"><el-icon><Plus /></el-icon>新建项目</el-button>
    </div>
    <el-card>
      <el-table :data="projects" v-loading="loading">
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="code" label="项目代码" width="120" />
        <el-table-column prop="environment_count" label="环境数" width="100" />
        <el-table-column prop="task_count" label="任务数" width="100" />
        <el-table-column prop="owner_info.username" label="负责人" width="120" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="editProject(row)">编辑</el-button>
            <el-popconfirm title="确定删除?" @confirm="deleteProject(row)">
              <template #reference><el-button type="danger" link>删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" title="项目" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="项目名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="项目代码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="Git仓库"><el-input v-model="form.git_repo_url" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
const loading = ref(false)
const dialogVisible = ref(false)
const projects = ref([])
const form = reactive({ name: '', code: '', git_repo_url: '', description: '' })
const fetchProjects = async () => {
  loading.value = true
  try {
    const res = await api.projects.list()
    projects.value = res.data.results || []
  } finally { loading.value = false }
}
const editProject = (row) => { Object.assign(form, row); form.id = row.id; dialogVisible.value = true }
const deleteProject = async (row) => { await api.projects.delete(row.id); ElMessage.success('删除成功'); fetchProjects() }
const submitForm = async () => {
  if (form.id) await api.projects.update(form.id, form)
  else await api.projects.create(form)
  dialogVisible.value = false; fetchProjects()
}
onMounted(fetchProjects)
</script>
