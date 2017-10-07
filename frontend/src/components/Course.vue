<template>
  <div id="course" class="item">
    <h4 class="ui top attached block header">
      {{ title }}
    </h4>
    <div class="ui bottom attached segment">
      {{ content_md }}
    </div>
  </div>
</template>

<script>
  export default {
    name: 'course',
    props: ['title', 'author', 'content_md']
  }
</script>

<style>

</style>
