<template>
  <b-navbar fixed="top" sticky toggleable="lg" type="dark" variant="dark">
    <b-navbar-brand href="/">Chapter Editor</b-navbar-brand>
    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-text>{{ title }}</b-nav-text>
      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-nav-item-dropdown text="Lang" right>
          <b-dropdown-item href="#">EN</b-dropdown-item>
          <b-dropdown-item href="#">ES</b-dropdown-item>
          <b-dropdown-item href="#">RU</b-dropdown-item>
          <b-dropdown-item href="#">FA</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
</template>

<script>
import EventBus from '../util/EventBus';

export default {
  data() {
    return {
      title: '',
    };
  },
  mounted() {
    EventBus.$on('UPDATE_TITLE', (payload) => {
      this.title = payload;
    });
  },
};
</script>
