<script lang="ts">
import type { PropType } from 'vue';
import JobCard from './JobCard.vue';
import { CloudUpload } from 'lucide-vue-next';

export default {
  components: {
    JobCard,
    CloudUpload,
  },
  data() {
    return {
      jobs: [],
      default_jobs: [],
      uploading: null as string | null,
      dragging_queue: false,
    }
  },
  props: {
    serverURL: String,
    connectionOk: Boolean,
    running: Boolean,
    uploaded: { type: Object as PropType<string | null>, default: null },
    fetchState: { type: Function as PropType<() => void>, required: true },
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
            this.jobs = data['jobs'];
            this.default_jobs = data['default_jobs'];
          })
          .catch(error => {
            console.error('There has been a problem with the connection:', error);
          });
      }
    },
    triggerFileInput() {
      (this.$refs.fileInput as HTMLInputElement).click();
    },
    handleFileUpload() {
      const file = (this.$refs.fileInput as HTMLInputElement).files![0];
      if (file) {
        (this.$refs.fileInput as HTMLInputElement).files?.item(0);
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
          .then(() => {
            this.fetchQueue();
          })
          .catch(error => {
            console.error('There has been a problem with the file upload:', error);
          });
      }
    },
    handleFileDrop(event: Event) {
      const files = (event as DragEvent).dataTransfer?.files;
      this.dragging_queue = false;
      if (files) {
        (this.$refs.fileInput as HTMLInputElement).files = files;
        Array.from(files).forEach(() => this.handleFileUpload());
      }
    },
    startJob() {
      fetch(`${this.serverURL}/start`, {
        method: 'POST',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(() => {
          this.fetchState();
        })
        .catch(error => {
          console.error('There has been a problem with the job start:', error);
        });
    },
    pauseJob() {
      fetch(`${this.serverURL}/pause`, {
        method: 'POST',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(() => {
          this.fetchState();
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
        .then(() => {
          this.fetchQueue();
          this.fetchState();
        })
        .catch(error => {
          console.error('There has been a problem with the job removal:', error);
        });
    },
    resetJob() {
      fetch(`${this.serverURL}/reset`, {
        method: 'POST',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(() => {
          this.fetchQueue();
          this.fetchState();
        })
        .catch(error => {
          console.error('There has been a problem with the job reset:', error);
        });
    },
    uploadJob(job: string) {
      this.uploading = job;
      fetch(`${this.serverURL}/queue/${job}`, {
        method: 'POST',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(() => {
          this.uploading = null;
          this.fetchState();
        })
        .catch(error => {
          console.error('There has been a problem with the job upload:', error);
        });
    },
  },
  mounted() {
  },
  watch: {
    connectionOk() {
      if (this.connectionOk)
        this.fetchQueue();
      else {
        this.jobs = [];
        this.default_jobs = [];
      }
    },
  },
}
</script>

<template>
  <div class="w-full h-full flex flex-col justify-start items-center gap-4 pb-16">
    <h2 v-if="!connectionOk" class="items-center text-center">Not connected to server</h2>
    <div v-else class="flex flex-col w-full items-center justify-center gap-4">
      <h2 v-if="(jobs.length + default_jobs.length) === 0" class="items-center text-center">Queue is empty</h2>
      <div v-else class="flex flex-col w-full items-center justify-center gap-4">
        <div class="flex flex-col w-full md:w-3/4 lg:w-1/2 justify-center gap-2">
          <JobCard v-for="job in default_jobs" :key="job" :job="job" :uploaded="uploaded === job"
            :running="running && (uploaded === job)" :start="startJob" :pause="pauseJob" :remove="removeJob"
            :reset="resetJob" :upload="uploadJob" :uploading="uploading === job" :not_default="false"/>
          <JobCard v-for="job in jobs" :key="job" :job="job" :uploaded="uploaded === job"
            :running="running && (uploaded === job)" :start="startJob" :pause="pauseJob" :remove="removeJob"
            :reset="resetJob" :upload="uploadJob" :uploading="uploading === job" :not_default="true"/>
        </div>
      </div>
      <form @submit.prevent="handleFileUpload" class="w-full h-40 md:h-60 flex flex-col items-center">
        <input type="file" ref="fileInput" accept=".png,.jpg,.jpeg,.gif,.svg,.txt,.gcode" class="hidden"
          @change="handleFileUpload" />
        <div
          class="flex flex-col grow justify-center items-center text-center cursor-pointer w-full align-middle border-dashed border-2 border-neutral-300 dark:border-neutral-700 hover:border- px-4 py-2 gap-4 rounded-lg h-fit md:w-3/4 lg:w-1/2 hover:border-sky-500 hover:text-sky-500 transition-all"
          :class="{ 'border-sky-500 text-sky-500': dragging_queue }" @mousedown.prevent @selectstart.prevent
          @dragenter="() => dragging_queue = true" @dragexit="() => dragging_queue = false"
          @drop.prevent="handleFileDrop" @click="triggerFileInput">
          <CloudUpload :size="36" />
          <p class="capitalize md:hidden">Click here to upload a file</p>
          <p class="capitalize opacity-0 md:opacity-100">Drag a file here or click to upload</p>
        </div>
      </form>
    </div>
  </div>
</template>
