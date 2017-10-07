<template>
  <!--<div id="app">-->
  <!--<img src="./assets/logo.png">-->
  <!--<hello></hello>-->
  <!--</div>-->
  <div id="app">
    <div class="ui menu">
      <div class="header item">反转课堂</div>
      <a class="active item">Link</a>
      <a class="item">Link</a>
      <div class="ui dropdown item" tabindex="0">
        Dropdown
        <i class="dropdown icon"></i>
        <div class="menu" tabindex="-1">
          <div class="item">Action</div>
          <div class="item">Another Action</div>
          <div class="item">Something else here</div>
          <div class="divider"></div>
          <div class="item">Separated Link</div>
          <div class="divider"></div>
          <div class="item">One more separated link</div>
        </div>
      </div>
      <div class="right menu">
        <div class="item">
          <div class="ui action left icon input">
            <i class="search icon"></i>
            <input type="text" placeholder="Search">
            <button class="ui button">提交</button>
          </div>
        </div>
        <a class="item">登录/注册</a>
      </div>
    </div>
    <course-set></course-set>
  </div>
</template>

<script>
  import $ from 'jquery'
  import CourseSet from './components/CourseSet.vue'

  const inBrowser = typeof window !== 'undefined'
  if (inBrowser) {
    /* eslint-disable no-unused-vars */
    var semantic = require('../semantic/dist/semantic.js')
  }

  export default {
    name: 'app',
    mounted: function () {
      $('.ui.dropdown').dropdown()
    },
    components: {CourseSet}
  }
</script>

<style>
  @import '../semantic/dist/semantic.css';
</style>
