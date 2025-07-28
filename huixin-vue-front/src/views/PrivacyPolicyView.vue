<template>
  <div class="privacy-policy">
    <div class="modern-nav">
      <div class="nav-content">
        <router-link to="/" class="nav-logo">
          <span>绘心同学</span>
        </router-link>
        <div class="nav-actions">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/login" class="nav-link">登录</router-link>
        </div>
      </div>
    </div>

    <div class="privacy-content">
      <h1>隐私政策</h1>
      <div class="policy-section">
        <h2>1. 引言</h2>
        <p>欢迎使用绘心同学（"我们"、"我们的"或"本应用"）。我们非常重视您的隐私，并承诺保护您的个人信息安全。本隐私政策旨在帮助您了解我们如何收集、使用、披露和保护您的个人信息。</p>
      </div>

      <div class="policy-section">
        <h2>2. 我们收集的信息</h2>
        <p>我们可能收集以下类型的信息：</p>
        <ul>
          <li><strong>账户信息：</strong>当您注册账户时，我们会收集您的姓名、电子邮件地址、密码和性别等信息。</li>
          <li><strong>用户内容：</strong>包括您创建的绘画、聊天记录以及其他您主动提供的内容。</li>
          <li><strong>使用数据：</strong>关于您如何使用我们的服务的信息，如访问时间、页面浏览和功能使用等。</li>
          <li><strong>设备信息：</strong>包括IP地址、浏览器类型、操作系统版本等技术数据。</li>
        </ul>
      </div>

      <div class="policy-section">
        <h2>3. 我们如何使用您的信息</h2>
        <p>我们使用收集的信息用于：</p>
        <ul>
          <li>提供、维护和改进我们的服务</li>
          <li>处理您的心理分析请求</li>
          <li>回应您的咨询和请求</li>
          <li>保护我们的用户和公众的安全</li>
          <li>遵守法律义务</li>
        </ul>
      </div>

      <div class="policy-section">
        <h2>4. 信息共享与披露</h2>
        <p>我们不会出售您的个人信息。我们可能在以下情况下共享您的信息：</p>
        <ul>
          <li>征得您的同意</li>
          <li>与我们的服务提供商共享</li>
          <li>遵守法律要求</li>
          <li>保护我们的合法权益和用户安全</li>
        </ul>
      </div>

      <div class="policy-section">
        <h2>5. 数据安全</h2>
        <p>我们实施了适当的技术和组织措施来保护您的个人数据不受意外损失、未授权访问、使用或披露的影响。</p>
      </div>

      <div class="policy-section">
        <h2>6. 您的权利</h2>
        <p>根据适用的数据保护法律，您可能拥有以下权利：</p>
        <ul>
          <li>访问您的个人信息</li>
          <li>更正不准确的个人信息</li>
          <li>删除您的个人信息</li>
          <li>限制或反对我们处理您的个人信息</li>
          <li>数据可携带性</li>
        </ul>
      </div>

      <div class="policy-section">
        <h2>7. 儿童隐私</h2>
        <p>我们的服务不面向13岁以下的儿童。如果您是父母或监护人，并且您认为您的孩子向我们提供了个人信息，请联系我们，我们将采取措施删除这些信息。</p>
      </div>

      <div class="policy-section">
        <h2>8. 隐私政策的变更</h2>
        <p>我们可能会不时更新本隐私政策。当我们进行重大更改时，我们将通过在应用中发布更新的隐私政策通知您。</p>
      </div>

      <div class="policy-section">
        <h2>9. 联系我们</h2>
        <p>如果您对本隐私政策有任何疑问或关切，请通过以下方式联系我们：</p>
        <p>电子邮件：support@huixin.edu.cn</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// 隐私政策页面不需要特殊的交互逻辑
</script>

<style scoped>
.privacy-policy {
  min-height: 100vh;
  background-color: var(--color-background);
}

.modern-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.nav-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  color: #1a1a1a;
  font-size: 1.5rem;
  font-weight: 600;
  text-decoration: none;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: #4a4a4a;
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #42b983;
}

.privacy-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 84px 2rem 3rem;
}

h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 2rem;
  text-align: center;
}

.policy-section {
  margin-bottom: 2rem;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1rem;
}

p {
  margin-bottom: 1rem;
  line-height: 1.6;
  color: #4a4a4a;
}

ul {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

li {
  margin-bottom: 0.5rem;
  line-height: 1.6;
  color: #4a4a4a;
}
</style>