<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
    </div>
    
    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.totalTasks }}</div>
          <div class="stat-label">总任务数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card success">
          <div class="stat-value">{{ stats.completedTasks }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card warning">
          <div class="stat-value">{{ stats.runningTasks }}</div>
          <div class="stat-label">执行中</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.passRate }}%</div>
          <div class="stat-label">平均通过率</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.totalEnvironments }}</div>
          <div class="stat-label">测试环境</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card success">
          <div class="stat-value">{{ stats.availableEnvironments }}</div>
          <div class="stat-label">可用环境</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.totalHosts }}</div>
          <div class="stat-label">测试主机</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.totalDevices }}</div>
          <div class="stat-label">测试设备</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Charts -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>执行趋势 (最近30天)</span>
          </template>
          <div class="chart-container">
            <v-chart :option="trendChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>任务状态分布</span>
          </template>
          <div class="chart-container">
            <v-chart :option="statusChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Recent Executions -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近执行</span>
          <el-button type="primary" link @click="$router.push('/executions')">
            查看更多
          </el-button>
        </div>
      </template>
      
      <el-table :data="recentExecutions" style="width: 100%">
        <el-table-column prop="task_name" label="任务名称" />
        <el-table-column prop="environment_name" label="环境" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :class="'status-tag ' + row.status" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="100">
          <template #default="{ row }">
            {{ row.pass_rate }}%
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewExecution(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'
import api from '@/api'

const router = useRouter()

const stats = reactive({
  totalTasks: 0,
  completedTasks: 0,
  runningTasks: 0,
  passRate: 0,
  totalEnvironments: 0,
  availableEnvironments: 0,
  totalHosts: 0,
  totalDevices: 0
})

const recentExecutions = ref([])

const trendChartOption = ref({
  tooltip: { trigger: 'axis' },
  legend: { data: ['执行数', '通过数', '失败数'] },
  xAxis: { type: 'category', data: [] },
  yAxis: { type: 'value' },
  series: [
    { name: '执行数', type: 'line', data: [] },
    { name: '通过数', type: 'line', data: [] },
    { name: '失败数', type: 'line', data: [] }
  ]
})

const statusChartOption = ref({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: [
      { value: 0, name: '已完成', itemStyle: { color: '#67c23a' } },
      { value: 0, name: '失败', itemStyle: { color: '#f56c6c' } },
      { value: 0, name: '执行中', itemStyle: { color: '#409eff' } },
      { value: 0, name: '待执行', itemStyle: { color: '#909399' } }
    ]
  }]
})

const formatTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const viewExecution = (row) => {
  router.push(`/tasks/${row.task}`)
}

const fetchData = async () => {
  try {
    // Fetch statistics
    const [tasksRes, envsRes, hostsRes, devicesRes, execStatsRes, execListRes] = await Promise.all([
      api.tasks.list({ page_size: 1 }),
      api.environments.list({ page_size: 1 }),
      api.hosts.list({ page_size: 1 }),
      api.devices.list({ page_size: 1 }),
      api.executions.statistics(),
      api.executions.list({ page_size: 10 })
    ])
    
    stats.totalTasks = tasksRes.data.count || 0
    stats.totalEnvironments = envsRes.data.count || 0
    stats.totalHosts = hostsRes.data.count || 0
    stats.totalDevices = devicesRes.data.count || 0
    
    stats.completedTasks = execStatsRes.data.completed || 0
    stats.passRate = execStatsRes.data.success_rate || 0
    
    recentExecutions.value = execListRes.data.results || []
    
    // Update charts with mock data for demo
    const days = []
    const execData = []
    const passData = []
    const failData = []
    
    for (let i = 29; i >= 0; i--) {
      days.push(dayjs().subtract(i, 'day').format('MM-DD'))
      const total = Math.floor(Math.random() * 20) + 5
      const pass = Math.floor(total * (0.7 + Math.random() * 0.25))
      execData.push(total)
      passData.push(pass)
      failData.push(total - pass)
    }
    
    trendChartOption.value.xAxis.data = days
    trendChartOption.value.series[0].data = execData
    trendChartOption.value.series[1].data = passData
    trendChartOption.value.series[2].data = failData
    
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-cards {
    .stat-card {
      text-align: center;
      
      .stat-value {
        font-size: 36px;
        font-weight: bold;
        color: #409eff;
        margin: 10px 0;
      }
      
      .stat-label {
        color: #909399;
        font-size: 14px;
      }
      
      &.success .stat-value {
        color: #67c23a;
      }
      
      &.warning .stat-value {
        color: #e6a23c;
      }
      
      &.danger .stat-value {
        color: #f56c6c;
      }
    }
  }
  
  .chart-container {
    height: 300px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
