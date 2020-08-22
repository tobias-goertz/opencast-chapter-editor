<template>
  <b-row>
    <b-col cols="12" :class="{ 'col-xl': !dualPlayer }">
      <b-container>
        <Video
          :segments="segments.map((segment) => segment.time)"
          :play-segment-time="playSegmentTime"
          @add-segment="addSegment"
          @dual-player="UpdateDualPlayer"
        />
      </b-container>
    </b-col>
    <b-col>
      <b-container>
        <TimeStamps
          :initial-segments="segments"
          @delete-segment="deleteSegment"
          @play-segment="playSegment"
        />
      </b-container>
    </b-col>
  </b-row>
</template>
<script>
import axios from 'axios';
import Video from '../components/Video.vue';
import TimeStamps from '../components/TimeStamps.vue';

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
    };
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
    UpdateDualPlayer(state) {
      this.dualPlayer = state;
    },
    playSegment(index) {
      this.playSegmentTime = this.segments[index].time;
    },
    getSegments() {
      const path = `${this.url}${this.location}/segments?id=${this.$route.params.id}`;
      axios.get(path)
        .then((res) => {
          this.segments = res.data.segment.map((s) => ({
            duration: Math.round(s.duration / 1000),
            time: Math.round(s.time / 1000),
          }));
          this.videoDuration = Math.round(
            (this.segments[this.segments.length - 1].time
            + this.segments[this.segments.length - 1].duration) / 1000,
          );
        })
        .catch((error) => {
          console.log(error) //eslint-disable-line
          this.flashMessage.warning({
            message: 'No segments available, create your own ones',
          });
        });
    },
  },
  created() {
    this.getSegments();
  },
};
</script>
