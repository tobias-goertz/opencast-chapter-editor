<template>
  <b-container fluid="sm">
    <b-row>
      <b-col cols="7">
        <div>
          <b-button-group>
            <b-button
              variant="danger"
              @click="deleteAllSegments"
              :disabled="tableBusy"
              class="space-around"
              id="delete-all-reload"
            >
              {{ $t('controls.deleteAll') }}
            </b-button>
            <b-button
              variant="secondary"
              @click="reloadSegments"
              :disabled="tableBusy"
              class="space-around"
            >
              {{ $t('controls.reload') }}
            </b-button>
          </b-button-group>
          <b-button-group>
            <b-button
              variant="info"
              @click="publishSegments('save')"
              :disabled="tableBusy"
              class="space-around"
            >
              {{ $t('controls.save') }}
            </b-button>
            <b-button
              variant="success"
              @click="publishSegments('publish')"
              :disabled="tableBusy"
              class="space-around"
              id="save-publish"
            >
              {{ $t('controls.publish') }}
            </b-button>
          </b-button-group>
        </div>
      </b-col>
      <b-col cols="5">
        <b-pagination
          v-model="currentPage"
          :total-rows="rows"
          :per-page="perPage"
          aria-controls="segments"
          align="right"
          class="pagination"
        >
        </b-pagination>
      </b-col>
    </b-row>
    <b-table
      id="segments"
      :items="segments"
      :v-bind="segments"
      :fields="fields"
      :per-page="perPage"
      :current-page="currentPage"
      :busy="tableBusy"
      :tbody-transition-props="transProps"
      striped
      responsive
      small
      fixed
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
        <b-form-spinbutton
          v-model="data.item.time"
          class="center"
          :max="maxTimePerRow(data)"
          :min="minTimePerRow(data)"
          :formatter-fn="formatTime"
          @change="changeTime">
        </b-form-spinbutton>
      </template>
      <template v-slot:cell(duration)="data">
        {{ data.item.duration | formatTime }}
      </template>
      <template v-slot:cell(title)="data">
        <b-form-input
          v-model="data.item.title"
          class="mb-2 mr-sm-2 mb-sm-0">
        </b-form-input>
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
    <b-popover
      target="delete-all-reload"
      :title="$t('help.deleteAll.title')"
      placement="leftbottom"
      fallback-placement="clockwise"
    >
      {{ $t('help.deleteAll.message') }}
    </b-popover>
    <b-popover
      target="save-publish"
      :title="$t('help.saveAndPublish.title')"
      placement="bottomright"
    >
      {{ $t('help.saveAndPublish.message') }}
    </b-popover>
    <b-popover
      target="segments"
      :title="$t('help.table.title')"
      placement="leftbottom"
    >
      {{ $t('help.table.message') }}
    </b-popover>
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

.center{
  text-align: center;
}

.space-around{
  margin: 3px 3px;
}

.pagination{
  margin-top: 0.5rem;
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
      segments: this.initialSegments,
      videoDuration: 0,
      location: process.env.VUE_APP_BACKEND_PROXY_PASS_LOCATION || '',
      url: process.env.VUE_APP_BACKEND_URL || '',
      id: this.$route.params.id,
    };
  },
  computed: {
    rows() {
      return this.segments.length
    },
    fields() {
      return [
        { key: 'index', label: this.$t('table.index') },
        { key: 'time',  label: this.$t('table.time') },
        { key: 'duration', label: this.$t('table.duration') },
        { key: 'title', label: this.$t('table.chapterTitle') },
        { key: 'actions', label: this.$t('table.actions') },
      ]
    }
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
    close() {
      this.popoverShow = false
    },
    maxTimePerRow(data) {
      if(this.segments.length === data.index + 1){
        return this.videoDuration;
      } else {
        return this.segments[data.index + 1].time - 1;
      }
    },
    minTimePerRow(data) {
      if(data.index > 0){
        return this.segments[data.index - 1].time + 1;
      } else {
        return 0;
      }
    },
    changeTime(value) {
      this.$parent.updateClosestSegment(value);
    },
    formatTime(value) {
      return this.$options.filters.formatTime(value);
    },
    reloadSegments() {
      this.$parent.getSegments();
    },
    deleteAllSegments() {
      this.segments.length = 1
      this.$set(this.segments, 0, {
        ...this.segments[0],
        duration: this.videoDuration,
      });
    },
    publishSegments(type) {
      const path = `${this.url}${this.location}/publish?id=${this.id}&type=${type}`;
      axios.post(path, {
        segments: this.segments,
        videoUrl: this.videoUrl,
        videoDuration: this.videoDuration,
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
    EventBus.$on('VIDEO_SRC', (payload) => {
      this.videoUrl = payload;
    });
    EventBus.$on('DURATION_UPDATE', (payload) => {
      this.videoDuration = payload;
    });
  },
};
</script>
