<script lang="ts">
import JobCard from './JobCard.vue';
import { CloudUpload } from 'lucide-vue-next';

export default {
  components: {
    JobCard,
    CloudUpload,
  },
  data() {
    return {
      queue: [],
      uploaded: '',
      running: '',
    }
  },
  props: {
    serverURL: String,
    connectionOk: Boolean,
  },
  methods: {
    fetchQueue() {
      if (this.connectionOk) {
        fetch(`${this.serverURL}/queue`)
          .then(response => {
            if (!response.ok) {
              console.log(response);
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            this.queue = data['jobs'];
          })
          .catch(error => {
            console.error('There has been a problem with the connection:', error);
          });
      }
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event: Event) {
      const file = this.$refs.fileInput.files[0];
      // console.log(file);
      if (file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch(`${this.serverURL}/queue`, {
          method: 'POST',
          body: formData,
        })
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            // console.log('File uploaded successfully:', data);
            this.fetchQueue();
          })
          .catch(error => {
            console.error('There has been a problem with the file upload:', error);
          });
      }
    },
    startJob(job: string) {
      fetch(`${this.serverURL}/start`, {
        method: 'POST',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // console.log('Job started successfully:', data);
          this.running = job;
        })
        .catch(error => {
          console.error('There has been a problem with the job start:', error);
        });
    },
    pauseJob(job: string) {
      fetch(`${this.serverURL}/pause`, {
        method: 'POST',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // console.log('Job paused successfully:', data);
          this.running = '';
        })
        .catch(error => {
          console.error('There has been a problem with the job pause:', error);
        });
    },
    removeJob(job: string) {
      fetch(`${this.serverURL}/queue/${job}`, {
        method: 'DELETE',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // console.log('Job removed successfully:', data);
          this.fetchQueue();
        })
        .catch(error => {
          console.error('There has been a problem with the job removal:', error);
        });
    },
    resetJob(job: string) {
      fetch(`${this.serverURL}/reset`, {
        method: 'POST',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.fetchQueue();
          // console.log('Job reset successfully:', data);
          this.running = '';
        })
        .catch(error => {
          console.error('There has been a problem with the job reset:', error);
        });
    },
    uploadJob(job: string) {
      fetch(`${this.serverURL}/queue/${job}`, {
        method: 'POST',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // console.log('Job uploaded successfully:', data);
          this.uploaded = job;
        })
        .catch(error => {
          console.error('There has been a problem with the job upload:', error);
        });
    },
  },
  mounted() {
    this.fetchQueue();
  },
  watch: {
    connectionOk() {
      if (this.connectionOk)
        this.fetchQueue();
      else
        this.queue = [];
    },
  },
}
</script>

<template>
  <div class="w-full h-full flex flex-col justify-start items-center gap-4 pb-16">
    <h2 v-if="!connectionOk" class="items-center text-center">Not connected to server</h2>
    <div v-else class="flex flex-col w-full items-center justify-center gap-4">
      <h2 v-if="queue.length === 0" class="items-center text-center">Queue is empty</h2>
      <div v-else class="flex flex-col w-full items-center justify-center gap-4">
        <div class="flex flex-col w-full md:w-3/4 lg:w-1/2 justify-center gap-2">
          <JobCard v-for="job in queue" :key="job" :job="job" :uploaded="uploaded === job" :running="running === job"
            :start="startJob" :pause="pauseJob" :remove="removeJob" :reset="resetJob" :upload="uploadJob" />
        </div>
      </div>
      <form @submit.prevent="handleFileUpload" class="w-full h-40 md:h-60 flex flex-col items-center">
        <input type="file" ref="fileInput" accept=".png,.jpg,.jpeg,.gif,.svg,.txt,.gcode" class="hidden" @change="handleFileUpload" />
        <div
          class="flex flex-col grow justify-center items-center text-center cursor-pointer w-full align-middle border border-[var(--color-border)] px-4 py-2 gap-4 rounded-lg h-fit md:w-3/4 lg:w-1/2 "
          @mousedown.prevent @selectstart.prevent @dragover.prevent @drop.prevent="handleFileDrop"
          @click="triggerFileInput">
          <CloudUpload :size="36" />
          <p>Drag a file here or click to upload</p>
          <!-- <button type="submit" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded">Upload</button> -->
        </div>
      </form>
    </div>
  </div>
</template>
