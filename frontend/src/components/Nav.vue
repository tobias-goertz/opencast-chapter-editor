<template>
  <b-navbar fixed="top" sticky toggleable="lg" type="dark" variant="dark">
    <b-navbar-brand href="/">{{ $t('nav.title') }}</b-navbar-brand>
    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-text>{{ title }}</b-nav-text>
      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-nav-text>
          <img class="country-flag"
            :src="`${opencast_url}/admin-ng/img/lang/${this.$t('countryCode')}.svg`"/>
        </b-nav-text>
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
</style>

<script>
import EventBus from '../util/EventBus';

export default {
  data() {
    return {
      title: '',
      opencast_url: process.env.VUE_APP_OPENCAST_URL,
      langs: [
        { value: 'en', text: 'English' },
        { value: 'de', text: 'Deutsch' },
        { value: 'es', text: 'Español' },
      ],
      countryCode: 'de_DE',
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
  },
};
</script>
