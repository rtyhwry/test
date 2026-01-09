import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// Create axios instance
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  response => {
    return response
  },
  error => {
    const { response } = error
    
    if (response) {
      switch (response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        default:
          ElMessage.error(response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

// API modules
const api = {
  // Auth
  auth: {
    login: (data) => request.post('/auth/login/', data),
    logout: () => request.post('/auth/logout/'),
    register: (data) => request.post('/auth/register/', data),
    refreshToken: (data) => request.post('/auth/token/refresh/', data)
  },
  
  // Users
  users: {
    me: () => request.get('/users/me/'),
    list: (params) => request.get('/users/', { params }),
    get: (id) => request.get(`/users/${id}/`),
    create: (data) => request.post('/users/', data),
    update: (id, data) => request.patch(`/users/${id}/`, data),
    delete: (id) => request.delete(`/users/${id}/`),
    changePassword: (data) => request.post('/users/change_password/', data)
  },
  
  // Projects
  projects: {
    list: (params) => request.get('/projects/', { params }),
    get: (id) => request.get(`/projects/${id}/`),
    create: (data) => request.post('/projects/', data),
    update: (id, data) => request.patch(`/projects/${id}/`, data),
    delete: (id) => request.delete(`/projects/${id}/`),
    statistics: (id) => request.get(`/projects/${id}/statistics/`)
  },
  
  // Hosts
  hosts: {
    list: (params) => request.get('/hosts/', { params }),
    get: (id) => request.get(`/hosts/${id}/`),
    create: (data) => request.post('/hosts/', data),
    update: (id, data) => request.patch(`/hosts/${id}/`, data),
    delete: (id) => request.delete(`/hosts/${id}/`),
    testConnection: (id) => request.post(`/hosts/${id}/test_connection/`),
    status: (id) => request.get(`/hosts/${id}/status_info/`),
    checkAll: () => request.post('/hosts/check_all/')
  },
  
  // Devices
  devices: {
    list: (params) => request.get('/devices/', { params }),
    get: (id) => request.get(`/devices/${id}/`),
    create: (data) => request.post('/devices/', data),
    update: (id, data) => request.patch(`/devices/${id}/`, data),
    delete: (id) => request.delete(`/devices/${id}/`),
    upgrade: (id, data) => request.post(`/devices/${id}/upgrade/`, data),
    upgradeHistory: (id) => request.get(`/devices/${id}/upgrade_history/`),
    available: () => request.get('/devices/available/')
  },
  
  // Environments
  environments: {
    list: (params) => request.get('/environments/', { params }),
    get: (id) => request.get(`/environments/${id}/`),
    create: (data) => request.post('/environments/', data),
    update: (id, data) => request.patch(`/environments/${id}/`, data),
    delete: (id) => request.delete(`/environments/${id}/`),
    lock: (id, data) => request.post(`/environments/${id}/lock/`, data),
    unlock: (id, data) => request.post(`/environments/${id}/unlock/`, data),
    available: (params) => request.get('/environments/available/', { params }),
    myLocked: () => request.get('/environments/my_locked/')
  },
  
  // Artifacts
  artifacts: {
    list: (params) => request.get('/artifacts/', { params }),
    get: (id) => request.get(`/artifacts/${id}/`),
    create: (data) => request.post('/artifacts/', data),
    update: (id, data) => request.patch(`/artifacts/${id}/`, data),
    delete: (id) => request.delete(`/artifacts/${id}/`),
    syncFromRepo: (data) => request.post('/artifacts/sync_from_repo/', data),
    byDeviceType: (deviceType) => request.get('/artifacts/by_device_type/', { params: { device_type: deviceType } }),
    latest: (name) => request.get('/artifacts/latest/', { params: { name } })
  },
  
  // Tasks
  tasks: {
    list: (params) => request.get('/tasks/', { params }),
    get: (id) => request.get(`/tasks/${id}/`),
    create: (data) => request.post('/tasks/', data),
    update: (id, data) => request.patch(`/tasks/${id}/`, data),
    delete: (id) => request.delete(`/tasks/${id}/`),
    execute: (id, data) => request.post(`/tasks/${id}/execute/`, data),
    cancel: (id) => request.post(`/tasks/${id}/cancel/`),
    executions: (id) => request.get(`/tasks/${id}/executions/`),
    enable: (id) => request.post(`/tasks/${id}/enable/`),
    disable: (id) => request.post(`/tasks/${id}/disable/`)
  },
  
  // Executions
  executions: {
    list: (params) => request.get('/tasks/executions/', { params }),
    get: (id) => request.get(`/tasks/executions/${id}/`),
    logs: (id) => request.get(`/tasks/executions/${id}/logs/`),
    statistics: () => request.get('/tasks/executions/statistics/')
  },
  
  // Test Cases
  testcases: {
    list: (params) => request.get('/testcases/', { params }),
    get: (id) => request.get(`/testcases/${id}/`),
    create: (data) => request.post('/testcases/', data),
    update: (id, data) => request.patch(`/testcases/${id}/`, data),
    delete: (id) => request.delete(`/testcases/${id}/`),
    batchCreate: (data) => request.post('/testcases/batch_create/', data),
    results: (id) => request.get(`/testcases/${id}/results/`)
  },
  
  // Reports
  reports: {
    list: (params) => request.get('/reports/', { params }),
    get: (id) => request.get(`/reports/${id}/`),
    downloadHtml: (id) => request.get(`/reports/${id}/download_html/`, { responseType: 'blob' }),
    downloadPdf: (id) => request.get(`/reports/${id}/download_pdf/`, { responseType: 'blob' }),
    downloadExcel: (id) => request.get(`/reports/${id}/download_excel/`, { responseType: 'blob' }),
    regenerate: (id, data) => request.post(`/reports/${id}/regenerate/`, data),
    statistics: (params) => request.get('/reports/statistics/', { params }),
    syncToAlm: (id) => request.post(`/reports/${id}/sync_to_alm/`)
  },
  
  // Integrations
  integrations: {
    gitlabTest: () => request.get('/integrations/gitlab/'),
    gitlabProjects: (params) => request.get('/integrations/gitlab/projects/', { params }),
    gitlabBranches: (projectId) => request.get(`/integrations/gitlab/projects/${projectId}/branches/`),
    gitlabTags: (projectId) => request.get(`/integrations/gitlab/projects/${projectId}/tags/`),
    almTest: () => request.get('/integrations/alm/'),
    almTestSets: (projectId) => request.get(`/integrations/alm/projects/${projectId}/test-sets/`),
    almTestCases: (testSetId) => request.get(`/integrations/alm/test-sets/${testSetId}/cases/`),
    almSync: (data) => request.post('/integrations/alm/sync/', data),
    artifactTest: () => request.get('/integrations/artifacts/'),
    artifactSearch: (params) => request.get('/integrations/artifacts/search/', { params }),
    artifactVersions: (params) => request.get('/integrations/artifacts/versions/', { params })
  }
}

export default api
