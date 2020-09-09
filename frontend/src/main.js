import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'vue-tour/dist/vue-tour.css';
import Vue from 'vue';
import FlashMessage from '@smartweb/vue-flash-message';
import VueTour from 'vue-tour';
import { BootstrapVue } from 'bootstrap-vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faTrash, faPlay, faPause, faStepForward,
  faStepBackward, faFastForward, faFastBackward,
  faVolumeUp, faQuestionCircle, faPlayCircle,
} from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import VueI18n from 'vue-i18n';
import messages from './i18n';
import router from './router';
import App from './App.vue';

library.add(
  faTrash, faPlay, faPause, faStepForward,
  faStepBackward, faFastForward, faFastBackward,
  faVolumeUp, faQuestionCircle, faPlayCircle,
);
Vue.component('font-awesome-icon', FontAwesomeIcon);

Vue.use(BootstrapVue);
Vue.use(VueI18n);
Vue.use(FlashMessage, {
  time: 3000,
  strategy: 'multiple',
});
Vue.use(VueTour);

// eslint-disable-next-line
const i18n = new VueI18n({
  locale: localStorage.Lang || navigator.language.split('-')[0] || process.env.VUE_APP_I18N_LOCALE,
  fallbackLocale: process.env.VUE_APP_I18N_FALLBACK_LOCALE || 'en',
  messages,
});

Vue.config.productionTip = false;

new Vue({
  router,
  i18n,
  render: (h) => h(App),
}).$mount('#app');
