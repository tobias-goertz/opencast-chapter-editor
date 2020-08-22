<template>
  <b-container fluid="sm">
    <b-row class="space">
      <b-col>
        <h1>Chapter</h1>
      </b-col>
      <b-col>
        <b-button
          variant="success"
          @click="publishSegments"
          align="right"
        >
          Publish
        </b-button>
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
      striped
      responsive="sm"
      small
    >
      <template v-slot:cell(index)="data">
        {{ data.index }}
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
            @click="$emit('delete-segment', data.index)"
            >
              <font-awesome-icon icon="trash"/>
            </b-button>
            <b-button
              variant="success"
              @click="$emit('play-segment', data.index)"
            >
              <font-awesome-icon icon="play"/>
            </b-button>
        </b-button-group>
      </template>
    </b-table>
  </b-container>
</template>

<script>
/* eslint-disable */
import axios from 'axios';

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
      fields: ['index', 'time', 'duration', 'actions'],
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
    publishSegments() {
      const path = `${this.url}${this.location}/publish?id=${this.$route.params.id}`;
      axios.post(path, {
        segments: this.segments
      })
      .then((res) => {
        this.flashMessage.success({
            title: 'Segments Uploaded',
            message: "The segments are successfully uploaded and will be published soon!",
            time: 10000
        });
      })
      .catch((error) => {
        console.error(error);
        debugger;
        this.flashMessage.error({
            title: 'Segments not Uploaded',
            message: error.response.data,
            time: 10000,
        });
      });
    },
  },
};
</script>
