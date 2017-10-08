<template>
  <div id="CourseSet" class="ui middle aligned animated list">
    <div class="item" v-for="c in courses">
      <course
        :title=c.title
        :author=c.author
        :content_md=c.content_md>
      </course>
    </div>
  </div>
</template>

<script>
  import Course from '../components/Course.vue'

  export default {
    name: 'CourseSet',
    data () {
      return {
        courses: []
      }
    },
    components: {
      Course
    },
    mounted: function () {
      const self = this
      this.$http.get('/api/courses/', {
//        params: {
//          ID: 12345
//        }
        auth: {
          username: 'superman',
          password: 'qwer1234'
        }
      })
      .then(function (response) {
        console.log(response)
        self.courses = response.data.results
      })
      .catch(function (error) {
        console.log(error)
      })
    }
  }
</script>
