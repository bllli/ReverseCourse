<template>
  <div class="ui container">
    <h2 class="ui dividing header">{{ title }}<span class="ui right">by {{ author }}</span></h2>
    {{ content_md }}
  </div>
</template>

<script>
  export default {
    name: 'article',
    data () {
      return {
        id: 0,
        title: 'nope',
        content_md: 'nope',
        author: 'nope',
        belong: null
      }
    },
    mounted: function () {
      const self = this
      this.axios.get('/api/articles/' + self.$route.params.id + '/', {
      }).then(function (response) {
        console.log(response)
        self.id = response.data.id
        self.title = response.data.title
        self.content_md = response.data.content_md
        self.author = response.data.author
        self.belong = response.data.belong
      }).catch(function (error) {
        console.log(error)
      })
    }
  }
</script>
