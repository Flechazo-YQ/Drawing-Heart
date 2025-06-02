<template>
  <div class="terms-container">
    <nav class="navbar">
      <div class="navbar-content">
        <router-link to="/" class="nav-logo">绘心同学</router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/privacy" class="nav-link">隐私政策</router-link>
        </div>
      </div>
    </nav>
    
    <div class="terms-content">
      <h1>服务条款</h1>
      <div class="terms-section">
        <h2>1. 接受条款</h2>
        <p>欢迎使用绘心同学AI心理绘画治疗平台。通过访问或使用我们的服务，您同意受这些条款的约束。如果您不同意这些条款的任何部分，请不要使用我们的服务。</p>
      </div>

      <div class="terms-section">
        <h2>2. 服务描述</h2>
        <p>绘心同学是一个基于AI技术的心理绘画治疗平台，旨在通过绘画艺术帮助用户进行心理疏导和治疗。我们的服务包括但不限于：</p>
        <ul>
          <li>AI辅助绘画创作</li>
          <li>心理状态分析</li>
          <li>专业心理咨询建议</li>
          <li>社区互动功能</li>
        </ul>
      </div>

      <div class="terms-section">
        <h2>3. 用户责任</h2>
        <p>作为用户，您同意：</p>
        <ul>
          <li>提供真实、准确的个人信息</li>
          <li>保护您的账户安全</li>
          <li>遵守所有适用的法律法规</li>
          <li>尊重其他用户的权利</li>
        </ul>
      </div>

      <div class="terms-section">
        <h2>4. 隐私保护</h2>
        <p>我们重视您的隐私。我们收集、使用和保护您的个人信息的方式在我们的隐私政策中有详细说明。通过使用我们的服务，您同意我们按照隐私政策处理您的信息。</p>
      </div>

      <div class="terms-section">
        <h2>5. 知识产权</h2>
        <p>平台上的所有内容，包括但不限于文本、图像、标志、软件等，均受知识产权法保护。未经授权，不得复制、修改或分发这些内容。</p>
      </div>

      <div class="terms-section">
        <h2>6. 免责声明</h2>
        <p>我们的服务仅供参考，不构成医疗建议。对于因使用我们的服务而产生的任何直接或间接损失，我们不承担责任。</p>
      </div>

      <div class="terms-section">
        <h2>7. 条款修改</h2>
        <p>我们保留随时修改这些条款的权利。修改后的条款将在平台上公布，继续使用我们的服务即表示您接受修改后的条款。</p>
      </div>

      <div class="terms-section">
        <h2>8. 联系方式</h2>
        <p>如果您对这些条款有任何疑问，请通过以下方式联系我们：</p>
        <p>邮箱：support@huixin.com</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.terms-container {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 2rem;
}

.navbar {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  border-radius: 8px;
}

.navbar-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  font-size: 1.25rem;
  font-weight: 600;
  color: #42b983;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: #4b5563;
  text-decoration: none;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: #42b983;
}

.terms-content {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #1a1a1a;
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.terms-section {
  margin-bottom: 2rem;
}

h2 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

p {
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 1rem;
}

ul {
  list-style-type: disc;
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

li {
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
  .terms-container {
    padding: 1rem;
  }

  .navbar {
    padding: 0.75rem 1rem;
  }

  .terms-content {
    padding: 1.5rem;
  }

  h1 {
    font-size: 1.75rem;
  }

  h2 {
    font-size: 1.25rem;
  }
}
</style> 