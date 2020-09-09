<template>
  <b-navbar fixed="top" sticky toggleable="lg" type="dark" variant="dark">
    <b-navbar-brand id="title" href="/">{{ $t('nav.title') }}</b-navbar-brand>
    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-text>{{ title }}</b-nav-text>
      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-nav-item
          :href="this.opencastUrl + '/engage/theodul/ui/core.html?id=' + this.$route.params.id"
          target="_blank"
        >
          <font-awesome-icon icon="play-circle" class="fa-2x help"/>
        </b-nav-item>
        <b-nav-item @click="startTour">
          <font-awesome-icon icon="question-circle" class="fa-2x help"/>
        </b-nav-item>
        <b-nav-item>
          <img class="country-flag"
            :src="`${opencastUrl}/admin-ng/img/lang/${this.$t('countryCode')}.svg`"/>
        </b-nav-item>
        <b-nav-item-dropdown :text="$t('nav.language')" v-model="$root.$i18n.locale" right>
          <b-dropdown-item v-for="(lang, i) in langs"
                        :key="`Lang${i}`"
                        :value="lang.value"
                        @click="langChanged(lang.value)"
          >
            {{ lang.text }}
          </b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
</template>

<style media="screen">
.country-flag{
  height: 15px;
}
.help{
  color: #f8f9fa;
  font-size: 25px;
}
</style>

<script>
import EventBus from '../util/EventBus';

export default {
  data() {
    return {
      title: '',
      opencastUrl: process.env.VUE_APP_OPENCAST_URL,
      langs: [
        { value: 'en', text: 'English' },
        { value: 'de', text: 'Deutsch' },
        { value: 'es', text: 'Español' },
      ],
      countryCode: 'de_DE',
      help: false,
    };
  },
  mounted() {
    EventBus.$on('UPDATE_TITLE', (payload) => {
      this.title = payload;
    });
    if (localStorage.Lang != null) {
      this.$i18n.locale = localStorage.Lang;
    }
  },
  methods: {
    langChanged(lang) {
      localStorage.Lang = lang;
      this.$root.$i18n.locale = lang;
    },
    startTour() {
      this.$tours.introduction.start();
    },
  },
};
</script>
