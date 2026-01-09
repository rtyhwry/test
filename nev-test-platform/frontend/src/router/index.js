import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/projects/ProjectList.vue'),
        meta: { title: '项目管理', icon: 'Folder' }
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('@/views/tasks/TaskList.vue'),
        meta: { title: '任务管理', icon: 'List' }
      },
      {
        path: 'tasks/:id',
        name: 'TaskDetail',
        component: () => import('@/views/tasks/TaskDetail.vue'),
        meta: { title: '任务详情', hidden: true }
      },
      {
        path: 'environments',
        name: 'Environments',
        component: () => import('@/views/environments/EnvironmentList.vue'),
        meta: { title: '环境管理', icon: 'Monitor' }
      },
      {
        path: 'hosts',
        name: 'Hosts',
        component: () => import('@/views/hosts/HostList.vue'),
        meta: { title: '主机管理', icon: 'Platform' }
      },
      {
        path: 'devices',
        name: 'Devices',
        component: () => import('@/views/devices/DeviceList.vue'),
        meta: { title: '设备管理', icon: 'Cpu' }
      },
      {
        path: 'artifacts',
        name: 'Artifacts',
        component: () => import('@/views/artifacts/ArtifactList.vue'),
        meta: { title: '制品管理', icon: 'Box' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/reports/ReportList.vue'),
        meta: { title: '测试报告', icon: 'Document' }
      },
      {
        path: 'reports/:id',
        name: 'ReportDetail',
        component: () => import('@/views/reports/ReportDetail.vue'),
        meta: { title: '报告详情', hidden: true }
      },
      {
        path: 'executions',
        name: 'Executions',
        component: () => import('@/views/executions/ExecutionList.vue'),
        meta: { title: '执行记录', icon: 'Timer' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/UserList.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  document.title = `${to.meta.title || '页面'} - 新能源汽车测试平台`
  
  const userStore = useUserStore()
  const isPublic = to.meta.public
  
  if (!isPublic && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
