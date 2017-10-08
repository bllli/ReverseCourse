/**
 * Created by superman on 17/2/16.
 */
import Vuex from 'vuex'
import Vue from 'vue'
import * as types from './types'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: {},
    username: null,
    password: null,
    title: ''
  },
  mutations: {
    [types.LOGIN]: (state, user) => {
      // console.log('username: ' + user.username + ' password: ' + user.password)
      localStorage.username = user.username
      localStorage.password = user.password
      state.username = user.username
      state.password = user.password
      // console.log('state: ')
      // console.log(state)
    },
    [types.LOGOUT]: (state) => {
      localStorage.removeItem('username')
      localStorage.removeItem('password')
      state.username = null
      state.password = null
    },
    [types.TITLE]: (state, data) => {
      state.title = data
    }
  }
})
