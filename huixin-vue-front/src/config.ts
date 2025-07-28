// 应用配置文件

// 获取当前环境
const isDevelopment = import.meta.env.DEV;

// 域名配置
// 在开发和生产环境中，我们都希望API请求发往当前域名，
// 所以API相关的域名配置应该为空字符串，以形成相对路径。
const apiDomain = '';

// 协议配置
const protocol = ''; // API请求使用相对路径，协议由浏览器自动处理
const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

// 检测是否为移动设备
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

// 导出配置对象
export default {
    // API基础URL - 始终为空字符串，使所有API请求都成为相对路径请求。
    baseURL: apiDomain,

    // WebSocket URL - 始终连接到当前页面的主机。
    socketUrl: `${wsProtocol}${window.location.host}`,

    // 其他配置项 - 确保API路径与后端路由匹配
    uploadPath: '/save',          // 使用与后端匹配的路径
    loginPath: '/login',          // 使用与后端匹配的路径
    registerPath: '/register',     // 使用与后端匹配的路径
    sendCodePath: '/api/send-code', // 发送注册验证码
    sendResetCodePath: '/api/send-reset-code', // 发送重置密码验证码
    resetPasswordDirectPath: '/api/reset-password-direct', // 直接重置密码
    chatPath: '/stream-chat',     // 修改为与后端匹配的路径，去掉/api
    clearChatContextPath: '/clear-chat-context', // 修改为与后端匹配的路径，去掉/api
    userInfoPath: '/user/info',   // 修改为与后端匹配的路径，去掉/api
    chatsPath: '/api/chats',      // 这个路径在后端已经有/api前缀，保持不变

    // 超时设置 - 移动设备使用更长的超时时间
    requestTimeout: isMobile ? 60000 : 30000,

    // 版本信息
    appVersion: '1.0.0',

    // 添加移动设备标志
    isMobile: isMobile
};
