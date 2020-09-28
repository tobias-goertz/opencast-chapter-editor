<template>
  <b-container fluid>
    <b-overlay :show="loadVideo" rounded="sm">
      <b-row>
        <b-col>
          <video-player  class="vjs-custom-skin"
                         ref="videoPlayer1"
                         :options="playerOptions"
                         :playsinline="true"
                         @play="onPlayerPlay"
                         @pause="onPlayerPause"
                         @timeupdate="onPlayerTimeupdate"
                         @ready="playerReadied"
                         />
        </b-col>
        <b-col v-if="dualPlayer">
          <video-player  class="vjs-custom-skin"
                        ref="videoPlayer2"
                        :options="playerOptions"
                        :playsinline="true"
                        @play="onPlayerPlay"
                        @pause="onPlayerPause"
                        @timeupdate="onPlayerTimeupdate"
                        @ready="playerReadied"
                        />
        </b-col>
      </b-row>
    </b-overlay>
    <b-container class="space slider-box">
      <div class="vol-slider">
        <font-awesome-icon icon="volume-up"/>
        <vue-slider
          v-model="volume"
          :max="100"
          :tooltip-formatter="volFormatter"
          @change="volumeChange"
        />
      </div>
      <div>
        <button type="button" @click="stopVideo">
          <font-awesome-icon icon="fast-backward" class="control fa-sm"/>
        </button>
        <button type="button" @click="seekBackward">
          <font-awesome-icon icon="step-backward" class="control fa-sm"/>
        </button>
        <button type="button" @click="togglePlayPause(playerIsPlaying)">
          <font-awesome-icon :icon="playerIsPlaying ? 'pause' : 'play'" class="control"/>
        </button>
        <button type="button" @click="seekForward">
          <font-awesome-icon icon="step-forward" class="control fa-sm"/>
        </button>
        <button type="button" @click="endVideo">
          <font-awesome-icon icon="fast-forward" class="control fa-sm"/>
        </button>
      </div>
      <p>{{ sliderVal | formatTime }} / {{ this.sliderOptions.max | formatTime }}</p>
      <b-container class="slider" id="timeline">
        <vue-slider
          v-model="sliderVal"
          v-bind="sliderOptions"
          @change="sliderChange"
        />
      </b-container>
      <b-button-group class="slider-buttons">
        <b-button
          variant="outline-success"
          @click="$emit('add-segment', sliderVal)"
          id="add-marker"
        >
            {{ $t('controls.addMarker') }}
        </b-button>
        <b-button
          variant="outline-secondary"
          @click="$emit('update-closest-segment', sliderVal)"
          @mouseenter="markerHoverIn"
          @mouseleave="markerHoverOut"
        >
          {{ $t('controls.updateClosest') }}
        </b-button>
        <b-button
          variant="outline-danger"
          @click="$emit('delete-closest-segment', sliderVal)"
          @mouseenter="markerHoverIn"
          @mouseleave="markerHoverOut"
          id="update"
        >
          {{ $t('controls.deleteClosest') }}
        </b-button>
      </b-button-group>
    </b-container>
  </b-container>
</template>

<style media="screen">
.control{
  font-size: 50px;
  opacity: 0.8;
  margin-top: 10px;
  margin-bottom: 5px;
}
.fa-sm{
  font-size: 35px;
}
.slider{
  display: block;
  margin: 0;
}
.slider-box{
  text-align: center;
  background-color: #f5f5f5;
  border-radius: 8px;
  height: 220px;
}
.slider-buttons{
  margin-top: 20px;
}
.vue-slider-mark{
  width: 2px;
}
.vue-slider-ltr .vue-slider-mark-step{
  width: 2px;
  right: 0;
  margin: 0 auto;
  border-radius: 0;
  box-shadow: none;
  background-color: #525252;
}
.vue-slider-mark:last-child .vue-slider-mark-step{
  display: block;
}
.highlight-marker{
  background-color: #ffc107;
  border-radius: 3px;
  opacity: 0.7;
}
.vol-slider{
  width: 15%;
  margin: 0 auto;
  position: absolute;
  text-align: left;
}
</style>

<script>
// custom skin css
import axios from 'axios';
import 'video.js/dist/video-js.css';
import { videoPlayer } from 'vue-video-player';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/default.css';
import EventBus from '../util/EventBus';

export default {
  components: {
    videoPlayer,
    VueSlider,
  },
  props: {
    segments: {
      type: Array,
      required: true,
    },
    playSegmentTime: {
      type: Number,
      required: false,
    },
  },
  data() {
    return {
      // videojs options
      currentTime: 0,
      sliderVal: 0,
      playerIsPlaying: false,
      dualPlayer: false,
      volume: 80,
      volFormatter: '{value}%',
      video_src: [],
      loadVideo: true,
      playerOptions: {
        controls: false,
        fluid: true,
        width: '100%',
        height: '100%',
        autoplay: true,
        muted: false,
        language: 'en',
        playbackRates: [0.7, 1.0, 1.5, 2.0],
        sources: [{
          type: 'video/mp4',
          src: '',
        }],
        poster: '',
      },
      sliderOptions: {
        dotSize: 14,
        width: 'auto',
        height: 12,
        direction: 'ltr',
        min: 0,
        max: 10800,
        clickable: true,
        dragOnClick: true,
        marks: this.segments,
        tooltip: 'none',
        railStyle: {
          backgroundColor: '#6bc295',
        },
        processStyle: {
          borderRadius: '0',
          backgroundColor: 'black',
          opacity: '0.3',
        },
        dotOptions: {
          style: {
            display: 'none',
          },
        },
        hideLabel: true,
        markOptions: {
          style: {
            backgroundColor: '#6bc295',
          },
        },
      },
      location: process.env.VUE_APP_BACKEND_PROXY_PASS_LOCATION || '',
      url: process.env.VUE_APP_BACKEND_URL || '',
    };
  },
  computed: {
    player() {
      if (this.dualPlayer) {
        return [this.$refs.videoPlayer1.player, this.$refs.videoPlayer2.player];
      }
      return [this.$refs.videoPlayer1.player];
    },
  },
  methods: {
    sliderChange(slider) {
      this.player.forEach((player) => {
        player.currentTime(slider);
      });
    },
    findClosestMarker() {
      let time = 0;
      this.player.forEach((player) => {
        time = player.currentTime();
      });
      return this.$parent.indexOfClosestSegment(time);
    },
    markerHoverIn() {
      const index = this.findClosestMarker();
      document.getElementsByClassName('vue-slider-mark')[index].classList.add('highlight-marker');
    },
    markerHoverOut() {
      const index = this.findClosestMarker();
      document.getElementsByClassName('vue-slider-mark')[index].classList.remove('highlight-marker');
    },
    togglePlayPause(state) {
      this.player.forEach((player) => {
        if (state) {
          player.pause();
        } else {
          player.play();
        }
      });
    },
    stopVideo() {
      this.player.forEach((player) => {
        player.pause();
        player.currentTime(0);
      });
    },
    seekBackward() {
      this.player.forEach((player) => {
        player.pause();
        player.currentTime(player.currentTime() - 1);
      });
    },
    seekForward() {
      this.player.forEach((player) => {
        player.currentTime(player.currentTime() + 1);
        player.pause();
      });
    },
    endVideo() {
      this.player.forEach((player) => {
        player.currentTime(player.duration());
        player.pause();
      });
    },
    onPlayerPlay() {
      this.playerIsPlaying = true;
    },
    onPlayerPause() {
      this.playerIsPlaying = false;
    },
    onPlayerTimeupdate() {
      this.player.forEach((player) => {
        this.sliderVal = Number(player.currentTime().toFixed());
      });
    },
    // player is ready
    playerReadied() {
      this.player.forEach((player, index) => {
        player.pause();
        player.volume(0.8);
        if (this.dualPlayer && index === 1) {
          player.muted(true);
        }
      });
    },
    volumeChange(vol) {
      this.player.forEach((player) => {
        player.volume(vol / 100);
      });
    },
    async getVideo() {
      const path = `${this.url}${this.location}/media?id=${this.$route.params.id}`;
      try {
        let { data } = await axios.get(path);
        if (data) { data = data.message; }
        if (data.presentation.length > 0 && data.presenter.length > 0) {
          this.dualPlayer = true;
          this.$emit('dual-player', true); // emit to index
          const track1 = data.presentation[data.presentation.length - 1];
          const track2 = data.presenter[data.presenter.length - 1];
          await this.$nextTick(); // await dualPlayer DOM update
          this.player[0].src(track1.url);
          this.player[1].src(track2.url);
          this.sliderOptions.max = Number((track1.duration).toFixed());
          EventBus.$emit('DURATION_UPDATE', Number((track1.duration).toFixed()));
          EventBus.$emit('VIDEO_SRC', track1.url);
        } else if (data.presentation.length > 0) {
          const track1 = data.presentation[data.presentation.length - 1];
          this.player[0].src(track1.url);
          this.sliderOptions.max = Number((track1.duration).toFixed());
          EventBus.$emit('DURATION_UPDATE', Number((track1.duration).toFixed()));
          EventBus.$emit('VIDEO_SRC', track1.url);
        } else {
          const track1 = data.presenter[data.presenter.length - 1];
          this.player[0].src(track1.url);
          this.sliderOptions.max = Number((track1.duration).toFixed());
          EventBus.$emit('DURATION_UPDATE', Number((track1.duration).toFixed()));
          EventBus.$emit('VIDEO_SRC', track1.url);
        }
        EventBus.$emit('UPDATE_TITLE', data.title);
        this.loadVideo = false;
      } catch (error) {
        this.flashMessage.error({
          title: 'Video Error',
          message: error.message,
          time: 10000,
        });
      }
    },
  },
  created() {
    this.getVideo();
  },
  watch: {
    segments(segments) {
      this.$set(this.sliderOptions, 'marks', segments);
    },
    playSegmentTime(time) {
      this.player.forEach((player) => {
        player.currentTime(time);
        player.play();
      });
    },
  },
  filters: {
    formatTime(value) {
      if (value == null) {
        return '-:--:--';
      }
      const seconds = Math.floor(value % 60);
      value /= 60; //eslint-disable-line
      const minutes = Math.floor(value % 60);
      value /= 60; //eslint-disable-line
      const hours = Math.floor(value % 60);
      const result = [minutes, seconds].map((unit) => (unit < 10 ? '0' : '') + unit);
      if (hours) {
        result.unshift(hours);
      }
      return result.join(':');
    },
  },
};
</script>
