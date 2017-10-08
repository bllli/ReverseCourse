import Vue from 'vue'
import VueRouter from 'vue-router'
import CourseSet from './components/CourseSet.vue'
import hello from './components/Hello.vue'
import login from './views/login.vue'
import store from './store/store'
import * as types from './store/types'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: '/',
    component: hello
  },
  {
    path: '/courses',
    name: 'courses',
    meta: {
      requireAuth: true
    },
    component: CourseSet
  },
  {
    path: '/login',
    name: 'login',
    component: login
  }
]

// 页面刷新时，重新赋值token
if (window.localStorage.getItem('username')) {
  store.commit(types.LOGIN, {
    username: window.localStorage.getItem('username'),
    password: window.localStorage.getItem('password')
  })
}

const router = new VueRouter({
  routes
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(r => r.meta.requireAuth)) {
    if (store.state.username) {
      next()
    } else {
      next({
        path: '/login',
        query: {redirect: to.fullPath}
      })
    }
  } else {
    next()
  }
})

export default router
