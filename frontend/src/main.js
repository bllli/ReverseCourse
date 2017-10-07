// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import VueRouter from 'vue-router'
import VueResource from 'vue-resource'

import App from './App'
import CourseSet from './components/CourseSet.vue'
import hello from './components/Hello.vue'

Vue.config.productionTip = false
Vue.use(VueRouter)
Vue.use(VueResource)

const router = new VueRouter({
  mode: 'history',
  base: __dirname,
  routes: [{
    path: '/courses',
    component: CourseSet
  }, {
    path: '/',
    component: hello
  }]
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  template: '<App/>',
  components: { App },
  router: router
})
