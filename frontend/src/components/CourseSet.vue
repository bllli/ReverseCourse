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
        courses: [
          {
            title: '测试1',
            content_md: '123123',
            author: 'bllli'
          },
          {
            title: '测试2',
            content_md: '123123',
            author: 'bllli'
          },
          {
            title: '测试3',
            content_md: '123123',
            author: 'teacher'
          }
        ]
      }
    },
    components: {
      Course
    }
  }
</script>
