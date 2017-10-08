/**
 * Created by superman on 17/2/16.
 * http配置
 */

import axios from 'axios'
import store from './store/store'
import * as types from './store/types'
import router from './router'

// axios 配置
axios.defaults.timeout = 5000
axios.defaults.baseURL = 'http://127.0.0.1:8000'

// http request 拦截器
axios.interceptors.request.use(
  config => {
    if (store.state.username) {
      config.headers.Authorization = 'Basic ' + btoa(`${store.state.username}:${store.state.password}`)
    }
    // console.log('config: ')
    // console.log(config)
    return config
  },
  err => {
    // console.log('err: ')
    // console.log(err)
    return Promise.reject(err)
  })

// http response 拦截器
axios.interceptors.response.use(
  response => {
    // console.log('response: ')
    // console.log(response)
    return response
  },
  error => {
    // console.log('err: ')
    // console.log(error)
    if (error.response) {
      switch (error.response.status) {
        case 401:
        case 403:
          // 401 清除token信息并跳转到登录页面
          store.commit(types.LOGOUT)
          router.replace({
            path: 'login',
            query: {redirect: router.currentRoute.fullPath}
          })
      }
    }
    // console.log(JSON.stringify(error));//console : Error: Request failed with status code 402
    return Promise.reject(error.response.data)
  })

export default axios
