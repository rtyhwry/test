<template>
  <div class="not-found">
    <div class="error-code">404</div>
    <div class="error-message">页面不存在</div>
    <p class="error-description">抱歉，您访问的页面不存在或已被删除</p>
    <el-button type="primary" @click="$router.push('/')">
      返回首页
    </el-button>
  </div>
</template>

<style lang="scss" scoped>
.not-found {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  .error-code {
    font-size: 120px;
    font-weight: bold;
    color: #409eff;
    line-height: 1;
  }
  
  .error-message {
    font-size: 24px;
    color: #333;
    margin: 20px 0 10px;
  }
  
  .error-description {
    color: #999;
    margin-bottom: 30px;
  }
}
</style>
