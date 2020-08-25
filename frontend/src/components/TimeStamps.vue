<template>
  <b-container fluid="sm">
    <b-row class="space">
      <b-col>
        <h1>{{ $t('table.title') }}</h1>
      </b-col>
      <b-col>
        <b-button-group>
          <b-button
            variant="info"
            @click="publishSegments('save')"
            :disabled="tableBusy"
          >
            {{ $t('controls.save') }}
          </b-button>
          <b-button
            variant="success"
            @click="publishSegments('publish')"
            :disabled="tableBusy"
          >
            {{ $t('controls.publish') }}
          </b-button>
        </b-button-group>
        <b-pagination
          v-model="currentPage"
          :total-rows="rows"
          :per-page="perPage"
          aria-controls="segments"
          align="right"
        >
        </b-pagination>
      </b-col>
    </b-row>
    <b-table
      id="segments"
      :items="segments"
      :fields="fields"
      :per-page="perPage"
      :current-page="currentPage"
      :busy="tableBusy"
      :tbody-transition-props="transProps"
      striped
      responsive="sm"
      small
    >
      <template v-slot:table-busy>
        <div class="text-center text-danger my-2">
          <b-spinner class="align-middle"></b-spinner>
          <strong>Loading...</strong>
        </div>
      </template>
      <template v-slot:cell(index)="data">
        {{ (currentPage * perPage) - perPage + data.index }}
      </template>
      <template v-slot:cell(time)="data">
        {{ data.item.time | formatTime }}
      </template>
      <template v-slot:cell(duration)="data">
        {{ data.item.duration | formatTime }}
      </template>
      <template v-slot:cell(actions)="data">
        <b-button-group>
          <b-button
            variant="danger"
            @click="$emit('delete-segment', (currentPage * perPage) - perPage + data.index)"
            >
              <font-awesome-icon icon="trash"/>
            </b-button>
            <b-button
              variant="success"
              @click="$emit('play-segment', (currentPage * perPage) - perPage + data.index)"
            >
              <font-awesome-icon icon="play"/>
            </b-button>
        </b-button-group>
      </template>
    </b-table>
  </b-container>
</template>

<style>
/* Busy table styling */
table.b-table[aria-busy='true'] {
  opacity: 0.6;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>

<script>
/* eslint-disable */
import axios from 'axios';
import EventBus from '../util/EventBus';

export default {
  props: {
    initialSegments: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      perPage: 12,
      currentPage: 1,
      tableBusy: true,
      transProps: {
        name: 'fade',
      },
      fields: [
        { key: 'index', label: this.$t('table.index') },
        { key: 'time',  label: this.$t('table.time') },
        { key: 'duration', label: this.$t('table.duration') },
        { key: 'actions', label: this.$t('table.actions') }
      ],
      segments: this.initialSegments,
      location: process.env.VUE_APP_BACKEND_PROXY_PASS_LOCATION || '',
      url: process.env.VUE_APP_BACKEND_URL || '',
    };
  },
  computed: {
    rows() {
      return this.segments.length
    },
  },
  watch: {
    initialSegments(segments) {
      this.segments = segments;
    },
  },
  filters: {
    formatTime(value) {
      if (value == null) {
        return '-:--:--';
      }
      const seconds = Math.floor(value % 60);
      value /= 60;
      const minutes = Math.floor(value % 60);
      value /= 60;
      const hours = Math.floor(value % 60);
      let result = [minutes, seconds].map(
        unit => (unit < 10 ? '0' : '') + unit
      );
      if (hours) {
        result.unshift(hours);
      }
      return result.join(':');
    }
  },
  methods: {
    publishSegments(type) {
      const path = `${this.url}${this.location}/publish?id=${this.$route.params.id}&type=${type}`;
      axios.post(path, {
        segments: this.segments
      })
      .then((res) => {
        this.flashMessage.success({
            title: this.$t(`flash.success.segments.${type}.title`),
            message: this.$t(`flash.success.segments.${type}.message`),
            time: 10000
        });
      })
      .catch((error) => {
        this.flashMessage.error({
            title: this.$t(`flash.error.segments.${type}.title`),
            message: error.response.data,
            time: 10000,
        });
      });
    },
  },
  mounted() {
    EventBus.$on('TABLE_BUSY', (payload) => {
      this.tableBusy = payload;
    });
  },
};
</script>
