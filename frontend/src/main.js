import 'bootstrap/dist/css/bootstrap.css';
import Vue from 'vue';
import FlashMessage from '@smartweb/vue-flash-message';
import { BootstrapVue } from 'bootstrap-vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faTrash, faPlay, faPause, faStepForward,
  faStepBackward, faFastForward, faFastBackward,
  faVolumeUp,
} from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import VueI18n from 'vue-i18n';
import messages from './i18n';
import router from './router';
import App from './App.vue';

library.add(
  faTrash, faPlay, faPause, faStepForward,
  faStepBackward, faFastForward, faFastBackward,
  faVolumeUp,
);
Vue.component('font-awesome-icon', FontAwesomeIcon);

Vue.use(BootstrapVue);
Vue.use(VueI18n);
Vue.use(FlashMessage, {
  time: 3000,
  strategy: 'multiple',
});

// eslint-disable-next-line
const i18n = new VueI18n({
  locale: 'de',
  fallbackLocale: 'de',
  messages,
});

Vue.config.productionTip = false;

new Vue({
  router,
  i18n,
  render: (h) => h(App),
}).$mount('#app');