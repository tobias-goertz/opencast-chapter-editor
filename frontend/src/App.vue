<template>
  <div id="app">
    <Nav/>
    <FlashMessage></FlashMessage>
    <div id="content">
      <router-view/>
    </div>
  </div>
</template>

<style>
#content {
  margin-top: 10px;
}
.space{
  margin-top: 25px;
}
button{
  border: none;
  outline: none !important;
  background: transparent;
}
</style>

<script>
import Nav from './components/Nav.vue';

export default {
  name: 'app',
  components: {
    Nav,
  },
};
</script>
