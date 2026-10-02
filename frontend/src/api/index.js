import { API_BASE_URL } from "../config/api.js"
import axios from 'axios'
import { authHeaders, publicApiError } from '../config/authSession.js'
import i18n from '../i18n'

// 创建axios实例
const service = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分钟超时（本体生成可能需要较长时间）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    config.headers['Accept-Language'] = i18n.global.locale.value
    Object.assign(config.headers, authHeaders())
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器（容错重试机制）
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果返回的状态码不是success，则抛出错误
    if (!res.success && res.success !== undefined) {
      return Promise.reject(publicApiError(response, res))
    }
    
    return res
  },
  error => {
    return Promise.reject(error.response
      ? publicApiError(error.response, error.response.data)
      : new Error('No fue posible conectar con el servicio.'))
  }
)

// 带重试的请求函数
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      
      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
