<template>
  <b-row>
    <b-col cols="12" :class="{ 'col-xl': !dualPlayer }">
      <b-container>
        <Video
          :segments="segments.map((segment) => segment.time)"
          :play-segment-time="playSegmentTime"
          @add-segment="addSegment"
          @update-closest-segment="updateClosestSegment"
          @delete-closest-segment="deleteClosestSegment"
          @dual-player="UpdateDualPlayer"
        />
      </b-container>
    </b-col>
    <b-col>
      <b-container>
        <TimeStamps
          :initial-segments="segments"
          :video-duration="videoDuration"
          @delete-segment="deleteSegment"
          @play-segment="playSegment"
        />
      </b-container>
    </b-col>
    <v-tour
      name="introduction"
      :steps="steps"
      :options="tourOptions"
      :callbacks="tourCallbacks"
    ></v-tour>
  </b-row>
</template>
<script>
import axios from 'axios';
import Video from '../components/Video.vue';
import TimeStamps from '../components/TimeStamps.vue';
import EventBus from '../util/EventBus';

export default {
  components: {
    Video,
    TimeStamps,
  },
  data() {
    return {
      segments: [],
      videoDuration: 0,
      playSegmentTime: 0,
      dualPlayer: false,
      location: process.env.VUE_APP_BACKEND_PROXY_PASS_LOCATION || '',
      url: process.env.VUE_APP_BACKEND_URL || '',
      id: this.$route.params.id,
      tourCallbacks: {
        onFinish: this.disableTour,
        onSkip: this.disableTour,
      },
    };
  },
  computed: {
    tourOptions() {
      return {
        useKeyboardNavigation: true,
        startTimeout: 1000,
        highlight: true,
        labels: {
          buttonSkip: this.$t('tour.skip'),
          buttonPrevious: this.$t('tour.previous'),
          buttonNext: this.$t('tour.next'),
          buttonStop: this.$t('tour.finish'),
        },
      };
    },
    steps() {
      return [
        {
          target: '#title',
          header: { title: this.$t('help.editor.title') },
          content: this.$t('help.editor.message'),
          params: {
            highlight: false,
            placement: 'top',
          },
        },
        {
          target: '#timeline',
          header: { title: this.$t('help.timeline.title') },
          content: this.$t('help.timeline.message'),
          params: {
            placement: 'top-end',
          },
        },
        {
          target: '#add-marker',
          header: { title: this.$t('help.addMarker.title') },
          content: this.$t('help.addMarker.message'),
          params: {
            placement: 'top-end',
          },
        },
        {
          target: '#update',
          header: { title: this.$t('help.update.title') },
          content: this.$t('help.update.message'),
          params: {
            placement: 'top-end',
          },
        },
        {
          target: '#delete-all-reload',
          header: { title: this.$t('help.deleteAll.title') },
          content: this.$t('help.editor.message'),
          params: {
            placement: 'top',
          },
        },
        {
          target: '#save-publish',
          header: { title: this.$t('help.saveAndPublish.title') },
          content: this.$t('help.saveAndPublish.message'),
        },
        {
          target: '#segments',
          header: { title: this.$t('help.table.title') },
          content: this.$t('help.table.message'),
          params: {
            placement: 'bottom-start',
          },
        },
      ];
    },
  },
  methods: {
    addSegment(time) {
      let segments = [...this.segments];
      const newSegment = { time };
      segments.push(newSegment);
      segments = segments.sort((a, b) => a.time - b.time);
      const index = segments.indexOf(newSegment);

      let previousSegment = segments[index - 1];
      const nextSegment = segments[index + 1];

      const duration = (nextSegment?.time || this.videoDuration) - time;
      const previousDuration = time - (previousSegment?.time || 0);

      previousSegment = this.segments[index - 1];
      this.$set(this.segments, index - 1, { ...previousSegment, duration: previousDuration });
      this.segments.push({
        time,
        duration,
      });
      this.segments = this.segments.sort((a, b) => a.time - b.time);
    },
    deleteSegment(index) {
      const nextSegment = this.segments[index + 1];
      const previousSegment = this.segments[index - 1];

      if (previousSegment && nextSegment) {
        const previousDuration = nextSegment.time - previousSegment.time;

        this.$set(this.segments, index - 1, { ...previousSegment, duration: previousDuration });
      } else if (nextSegment) {
        this.$set(this.segments, index + 1, {
          ...this.segments[index + 1],
          time: 0,
          duration: this.segments[index].duration + nextSegment.duration,
        });
      } else {
        this.$set(this.segments, index - 1, {
          ...previousSegment,
          duration: this.segments[index - 1].duration + this.segments[index].duration,
        });
      }
      this.segments.splice(index, 1);
    },
    updateClosestSegment(time) {
      const index = this.indexOfClosestSegment(time);
      const nextSegment = this.segments[index + 1];
      const previousSegment = this.segments[index - 1];
      if (previousSegment) {
        this.$set(this.segments, index - 1, {
          ...previousSegment,
          duration: time - previousSegment.time,
        });
        const duration = (nextSegment?.time || this.videoDuration) - time;
        this.$set(this.segments, index, {
          ...this.segments[index],
          time,
          duration,
        });
      }
    },
    deleteClosestSegment(time) {
      const index = this.indexOfClosestSegment(time);
      this.deleteSegment(index);
    },
    indexOfClosestSegment(time) {
      const closestArr = [...this.segments];
      closestArr.sort((a, b) => Math.abs(time - a.time) - Math.abs(time - b.time));
      const closest = closestArr[0];
      return this.segments.indexOf(closest);
    },
    UpdateDualPlayer(state) {
      this.dualPlayer = state;
    },
    playSegment(index) {
      this.playSegmentTime = this.segments[index].time;
    },
    loadSegments() {
      // load segments from local storage if available
      if (localStorage.getItem(this.id)) {
        try {
          this.segments = JSON.parse(localStorage.getItem(this.id));
          setTimeout(() => { EventBus.$emit('TABLE_BUSY', false); }, 100);
        } catch (e) {
          localStorage.removeItem(this.id);
        }
      } else {
        this.getSegments();
      }
    },
    getSegments() {
      EventBus.$emit('TABLE_BUSY', true);
      const path = `${this.url}${this.location}/segments?id=${this.id}`;
      axios.get(path)
        .then((res) => {
          this.segments = res.data.segments.map((s) => ({
            duration: Math.round(s.duration),
            time: Math.round(s.time),
            title: s.title,
          }));
          this.videoDuration = Math.round(res.data.duration);
          EventBus.$emit('TABLE_BUSY', false);
        })
        .catch((error) => {
          console.log(error) //eslint-disable-line
          this.$set(this.segments, 0, {
            time: 0,
            duration: this.videoDuration,
          });
          this.flashMessage.warning({
            message: this.$t('flash.error.segments.loading.message'),
          });
          EventBus.$emit('TABLE_BUSY', false);
        });
    },
    disableTour() {
      localStorage.setItem('showTour', false);
    },
  },
  created() {
    this.loadSegments();
    if (localStorage.Lang != null) {
      this.$i18n.locale = localStorage.Lang;
    }
  },
  mounted() {
    EventBus.$on('DURATION_UPDATE', (payload) => {
      this.videoDuration = payload;
      if (this.segments.length === 1) {
        this.segments[0].duration = payload;
      }
    });
    if (localStorage.showTour === undefined) {
      this.$tours.introduction.start();
    }
  },
  watch: {
    segments(segments) {
      // save in localstorage under video-ID
      const parsed = JSON.stringify(segments);
      localStorage.setItem(this.id, parsed);
    },
  },
};
</script>
