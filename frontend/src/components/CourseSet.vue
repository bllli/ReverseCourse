<template>
  <div>
    <h3 class="ui center aligned header">课程列表</h3>
    <div class="ui container">
      <div class="ui relaxed link list">
        <div class="item" v-for="c in courses">
          <div class="ui small image">
            <img src="../assets/example.png" v-on:click="to_detail(c.id)">
          </div>
          <div class="content">
            <a class="header" v-on:click="to_detail(c.id)"> {{ c.title }}</a>
            <!--<div class="meta">-->
            <!--<a>Date</a>-->
            <!--<a>Category</a>-->
            <!--</div>-->
            <div class="description">
              <p>
                讲师： {{ c.detail.content_md }}
              </p>
            </div>
            <div class="extra">
              <img src="../assets/square-image.png" class="ui circular avatar image"> {{ c.author }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'CourseSet',
    data () {
      return {
        courses: []
      }
    },
    mounted: function () {
      const self = this
      this.axios.get('/api/courses/', {
      }).then(function (response) {
        console.log(response)
        self.courses = response.data.results
      }).catch(function (error) {
        console.log(error)
      })
    },
    methods: {
      to_detail (id) {
        const self = this
        console.log('redirecting to', id)
        let redirect = decodeURIComponent('/course/' + id)
        console.log('redirecting to', redirect)
        self.$router.push({
          path: redirect
        })
      }
    }
  }
</script>
