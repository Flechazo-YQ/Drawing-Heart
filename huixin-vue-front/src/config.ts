// 应用配置文件

// 获取当前环境
const isDevelopment = import.meta.env.DEV;

// 域名配置
const devDomain = 'localhost:5000';  // 开发环境域名
// 检测是否为移动设备
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
// 根据设备类型设置不同的域名策略
const prodDomain = (isMobile && window.location.hostname === '101.132.253.65')
    ? '101.132.253.65:5000'  // 移动设备直接访问API服务器
    : '';  // 其他情况使用相对URL

// 协议配置
const protocol = isDevelopment || (isMobile && prodDomain) ? 'http://' : '';
const wsProtocol = isDevelopment ? 'ws://' : (window.location.protocol === 'https:' ? 'wss://' : 'ws://');

// 导出配置对象
export default {
    // API基础URL - 不要在开发环境下添加末尾斜杠，因为后端路由不带前导斜杠
    baseURL: `${protocol}${isDevelopment ? devDomain : prodDomain}`,

    // WebSocket URL
    socketUrl: `${wsProtocol}${isDevelopment ? devDomain : window.location.host}`,

    // 其他配置项 - 确保API路径与后端路由匹配
    uploadPath: '/save',          // 修改为正确的上传路径
    loginPath: '/login',          // 与后端路由匹配
    registerPath: '/register',     // 与后端路由匹配
    chatPath: '/api/stream-chat',  // 保持不变

    // 超时设置 - 移动设备使用更长的超时时间
    requestTimeout: isMobile ? 60000 : 30000,

    // 版本信息
    appVersion: '1.0.0',

    // 添加移动设备标志
    isMobile: isMobile
};