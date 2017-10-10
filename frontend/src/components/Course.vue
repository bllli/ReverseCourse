<template>
  <div class="ui container">
    <h2 class="ui dividing header">{{ title }}<span class="ui right">by {{ author }}</span></h2>
    <p>{{ detail.content_md }}</p>
    <div class="ui items">
      <div class="item" v-for="article in article_set">
        <div class="middle aligned content">
          <div class="header">
            {{ article.title }}
          </div>
          <div class="description">
            {{ article.content_md }}
          </div>
          <div class="extra">
            <div class="ui right floated button" v-on:click="to_article(article.id)">
              文章详情
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'Course',
    data () {
      return {
        url: 'nope',
        title: 'nope',
        author: 'nope',
        detail: {content_md: 'nope'},
        article_set: []
      }
    },
    mounted: function () {
      const self = this
      console.log('ready to axios!', '/api/courses/' + self.$route.params.id + '/')
      this.axios({
        method: 'get',
        url: '/api/courses/' + self.$route.params.id + '/'
      }).then(function (response) {
        console.log('got course detail!', response)
        self.url = response.data.url
        self.title = response.data.title
        self.detail = response.data.detail
        self.author = response.data.author
        self.article_set = response.data.article_set
      }).catch(function (error) {
        console.log('error when getting course detail', error)
      })
    },
    methods: {
      to_article (id) {
        const self = this
        let redirect = decodeURIComponent('/article/' + id + '/')
        self.$router.push({
          path: redirect
        })
      }
    }
  }
</script>
