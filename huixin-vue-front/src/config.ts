// 应用配置文件

// 获取当前环境
const isDevelopment = import.meta.env.DEV;

<<<<<<< HEAD
// 域名配置
// 在开发和生产环境中，我们都希望API请求发往当前域名，
// 所以API相关的域名配置应该为空字符串，以形成相对路径。
const apiDomain = '';
=======
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
                        currentHost === '101.132.253.65'; // 您的frp服务器

  if (isTunnelDomain) {
    // 内网穿透情况下，需要使用对应的后端穿透地址
    if (currentHost === '101.132.253.65') {
      // 您的frp服务器配置：前端5173端口，后端5000端口
      return `${currentProtocol}//101.132.253.65:5000`;
    } else {
      // 其他穿透服务（ngrok、cpolar等）
      return `${currentProtocol}//${currentHost.replace(':5173', ':5000')}`;
    }
  } else if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    return 'http://localhost:5000';
  } else {
    // 局域网IP访问
    return `http://${currentHost}:5000`;
  }
};

const apiDomain = getApiDomain();
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845

// 协议配置
const protocol = ''; // API请求使用相对路径，协议由浏览器自动处理
const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

<<<<<<< HEAD
// 检测是否为移动设备
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

=======
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
// 导出配置对象
export default {
    // API基础URL - 始终为空字符串，使所有API请求都成为相对路径请求。
    baseURL: apiDomain,

    // WebSocket URL - 始终连接到当前页面的主机。
    socketUrl: `${wsProtocol}${window.location.host}`,

    // 其他配置项 - 确保API路径与后端路由匹配
<<<<<<< HEAD
    uploadPath: '/save',          // 修改为正确的上传路径
    loginPath: '/login',          // 与后端路由匹配
    registerPath: '/register',     // 与后端路由匹配
    chatPath: '/api/stream-chat',  // 保持不变
=======
    uploadPath: '/api/save',          // 使用与后端匹配的路径
    loginPath: '/api/login',          // 使用与后端匹配的路径
    registerPath: '/api/register',     // 使用与后端匹配的路径
    sendCodePath: '/api/send-code', // 发送注册验证码
    sendResetCodePath: '/api/send-reset-code', // 发送重置密码验证码
    resetPasswordDirectPath: '/api/reset-password-direct', // 直接重置密码
    chatPath: '/api/stream-chat',     // 修改为与后端匹配的路径，去掉/api
    clearChatContextPath: '/api/clear-chat-context', // 修改为与后端匹配的路径，去掉/api
    userInfoPath: '/api/user/info',   // 修改为与后端匹配的路径
    chatsPath: '/api/chats',      // 这个路径在后端已经有/api前缀，保持不变
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845

    // 超时设置 - 移动设备使用更长的超时时间
    requestTimeout: isMobile ? 60000 : 30000,

    // 版本信息
    appVersion: '1.0.0',

    // 添加移动设备标志
    isMobile: isMobile
};
