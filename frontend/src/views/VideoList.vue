<template>
  <b-container>
    <h1>Videos</h1>
    <hr><br><br>
    <ul>
      <li v-for="(video, index) in videos" :key="index">
        <router-link :to="{ name: 'editor-index', params: { id: video.identifier }}">
          {{ video.title }}
        </router-link>
      </li>
    </ul>
  </b-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      videos: [],
      location: process.env.VUE_APP_BACKEND_PROXY_PASS_LOCATION || '',
      url: process.env.VUE_APP_BACKEND_URL || '',
    };
  },
  methods: {
    getVideos() {
      const path = `${this.url}${this.location}/videos`;
      axios.get(path)
        .then((res) => {
          this.videos = res.data;
        })
        .catch((error) => {
          this.flashMessage.error({
            title: error.message,
            message: 'Videos not loaded',
          });
        });
    },
  },
  created() {
    this.getVideos();
  },
};
</script>
