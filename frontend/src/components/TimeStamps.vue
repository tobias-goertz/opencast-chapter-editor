<template>
  <b-container fluid="sm">
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
      </b-button-group>
      <b-button-group>
        <b-button
          variant="success"
          @click="publishSegments('save')"
          :disabled="tableBusy"
          class="space-around"
          id="save-publish"
        >
          {{ $t('controls.save') }}
        </b-button>
        <b-button
          variant="success"
          @click="showPublishModal"
          :disabled="tableBusy"
          class="space-around"
          id="save-publish"
        >
          {{ $t('controls.publish.button') }}
        </b-button>
      </b-button-group>
    </div>
    <b-table
      id="segments"
      :items="segments"
      :v-bind="segments"
      :fields="fields"
      :busy="tableBusy"
      :tbody-transition-props="transProps"
      striped
      responsive
      small
      borderless
      sticky-header="75vh"
    >
      <template v-slot:table-busy>
        <div class="text-center text-danger my-2">
          <b-spinner class="align-middle"></b-spinner>
          <strong>Loading...</strong>
        </div>
      </template>
      <template v-slot:cell(index)="data">
        {{ data.index }}
      </template>
      <template v-slot:cell(time)="data">
        <b-form-spinbutton
          v-model="data.item.time"
          class="center"
          :disabled="segments.length === 1 || data.index === 0"
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
            class="table-button"
            variant="outline-danger"
            @click="$emit('delete-segment', data.index)"
            >
              <font-awesome-icon icon="trash"/>
            </b-button>
            <b-button
              class="table-button"
              variant="outline-success"
              @click="$emit('play-segment', data.index)"
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
    deleteAllSegments() {
      this.segments.length = 1
      this.$set(this.segments, 0, {
        ...this.segments[0],
        duration: this.videoDuration,
      });
    },
    showReloadModal() {
      this.$bvModal.msgBoxConfirm(this.$t('controls.reload.message'), {
        title: this.$t('controls.reload.title'),
        okTitle: this.$t('controls.ok'),
        cancelTitle: this.$t('controls.no'),
        okVariant: 'success',
      })
        .then(value => {
          if(value === true) {
            this.$parent.getSegments();
          }
        })
    },
    showPublishModal() {
      this.$bvModal.msgBoxConfirm(this.$t('controls.publish.message'), {
        title: this.$t('controls.publish.title'),
        okTitle: this.$t('controls.ok'),
        cancelTitle: this.$t('controls.no'),
        okVariant: 'success',
      })
        .then(value => {
          if(value === true) {
            this.publishSegments('publish');
          }
        })
    },
    publishSegments(type) {
      const path = `${this.url}${this.location}/upload?id=${this.id}&type=${type}`;
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
