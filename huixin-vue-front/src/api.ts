import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建一个 axios 实例
const apiClient = axios.create({
  // baseURL 设置为空字符串，axios 会自动使用当前页面的域名作为基础路径
  // 这能完美地处理本地开发和内网穿透等不同环境
  baseURL: '',
  timeout: 30000, // 设置请求超时时间
});

// 添加一个响应拦截器来统一处理错误
apiClient.interceptors.response.use(
  // 如果请求成功，直接返回响应中的 data 部分
  (response) => response.data,
  // 如果请求失败，进行统一的错误处理
  (error) => {
    console.error('API 请求错误:', error.response || error);

    let message = '请求失败，请稍后再试';
    if (error.response && error.response.data && error.response.data.message) {
      // 如果服务器返回了具体的错误信息，就用那个信息
      message = error.response.data.message;
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请检查您的网络连接';
    } else if (!error.response) {
      message = '网络连接失败，请检查您的网络设置';
    }

    // 使用 Element Plus 的 ElMessage 显示错误提示
    ElMessage.error(message);

    // 将错误继续抛出，以便调用方可以进行额外的处理
    return Promise.reject(error);
  }
);

export default apiClient;
