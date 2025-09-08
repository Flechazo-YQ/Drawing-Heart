// 应用配置文件

// 获取当前环境
const isDevelopment = import.meta.env.DEV;

// 检测是否为移动设备
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

// 域名配置 - 支持内网穿透
const getApiDomain = () => {
  if (!isDevelopment) return '';

  const currentHost = window.location.hostname;
  const currentProtocol = window.location.protocol;

  // 检测是否为内网穿透域名（如ngrok、cpolar等）
  const isTunnelDomain = currentHost.includes('.ngrok') ||
                        currentHost.includes('.cpolar') ||
                        currentHost.includes('.frp') ||
                        currentHost.includes('.r15.cpolar.top') ||
                        currentHost.includes('4v22948452.eicp.vip') ||
                        currentHost.includes('1075oj69wr205.vicp.fun') ||
                        currentHost === 'huixintongxue.com' ||
                        currentHost === 'www.huixintongxue.com' ||
                        currentHost === '101.132.253.65'; // 您的frp服务器

  if (isTunnelDomain) {
    // 针对自己的域名，使用API子域名
    if (currentHost === 'huixintongxue.com' || currentHost === 'www.huixintongxue.com') {
      return 'http://api.huixintongxue.com';
    }
    // 其他内网穿透情况下，使用代理而不是直接访问后端
    // 这样可以避免CORS问题
    return ''; // 使用相对路径，通过Vite代理转发
  } else if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    return ''; // 本地开发时也使用代理
  } else {
    // 局域网IP访问
    return `http://${currentHost}:5000`;
  }
};

const apiDomain = getApiDomain();

// 协议配置
const protocol = ''; // API请求使用相对路径，协议由浏览器自动处理
const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

// 导出配置对象
export default {
    // API基础URL - 始终为空字符串，使所有API请求都成为相对路径请求。
    baseURL: apiDomain,

    // WebSocket URL - 始终连接到当前页面的主机。
    socketUrl: `${wsProtocol}${window.location.host}`,

    // 其他配置项 - 确保API路径与后端路由匹配
    uploadPath: '/api/save',          // 使用与后端匹配的路径
    loginPath: '/api/login',          // 使用与后端匹配的路径
    registerPath: '/api/register',     // 使用与后端匹配的路径
    sendCodePath: '/api/code/register', // 发送注册验证码
    sendResetCodePath: '/api/code/reset', // 发送重置密码验证码
    resetPasswordDirectPath: '/api/password/reset/direct', // 直接重置密码
    chatPath: '/api/chats/stream',     // 修改为与后端匹配的路径，去掉/api
    clearChatContextPath: '/api/clear/chat/context', // 修改为与后端匹配的路径，去掉/api
    userInfoPath: '/api/info',   // 修改为与后端匹配的路径
    chatsPath: '/api/chats',      // 这个路径在后端已经有/api前缀，保持不变
    mapsearchPath: '/api/map/search', // 使用与后端匹配的路径

    // 超时设置 - 移动设备使用更长的超时时间
    requestTimeout: isMobile ? 60000 : 30000,

    // 版本信息
    appVersion: '1.0.0',

    // 添加移动设备标志
    isMobile: isMobile
};
