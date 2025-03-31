<script lang="ts">
import type { PropType } from 'vue';
import JobCard from './JobCard.vue';
import { ArrowRight, CloudUpload } from 'lucide-vue-next';

export default {
  components: {
    JobCard,
    CloudUpload,
    ArrowRight,
  },
  data() {
    return {
      jobs: [],
      default_jobs: [],
      uploading: null as string | null,
      dragging_queue: false,
      /* Raster Images Panel */
      showRasterPanel: false,
      filter_speckle: 64,
      curve_fitting: 'polygon' as 'polygon' | 'spline' | 'none',
      corner_threshold: 180,
      segment_length: 0,
      splice_threshold: 0,
      window: window, // Expose window to the template,
      previewImage: null as string | null, // b64
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
    handleFileUpload(final_if_raster: boolean = false) {
      // if sending a raster image, show the panel
      // with parameters and a preview
      // If not raster, it's always final
      const file = (this.$refs.fileInput as HTMLInputElement).files![0];
      if (file) {
        (this.$refs.fileInput as HTMLInputElement).files?.item(0);
        const formData = new FormData();
        formData.append('file', file);

        if ((file.type !== 'image/svg+xml') && (file.type !== 'text/x.gcode')) {
          this.showRasterPanel = true;
          formData.append('filter_speckle', this.filter_speckle.toString());
          formData.append('curve_fitting', this.curve_fitting);
          formData.append('corner_threshold', this.corner_threshold.toString());
          formData.append('segment_length', this.segment_length.toString());
          formData.append('splice_threshold', this.splice_threshold.toString());
          if (!final_if_raster) {
            formData.append('tmp', 'true');
          }
        }

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
            this.fetchPreview(file.name.split('.').slice(0, -1).join('.'));
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
    fetchPreview(job: string) {
      fetch(`${this.serverURL}/queue/${job}/preview`, {
        method: 'GET',
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // Handle the preview data
          this.previewImage = `data:image/jpeg;base64,${data.preview}`;
        })
        .catch(error => {
          console.error('There has been a problem with the job preview:', error);
        });
    }
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
            :reset="resetJob" :upload="uploadJob" :uploading="uploading === job" :not_default="false" />
          <JobCard v-for="job in jobs" :key="job" :job="job" :uploaded="uploaded === job"
            :running="running && (uploaded === job)" :start="startJob" :pause="pauseJob" :remove="removeJob"
            :reset="resetJob" :upload="uploadJob" :uploading="uploading === job" :not_default="true" />
        </div>
      </div>
      <form @submit.prevent="() => handleFileUpload(false)" class="w-full h-40 md:h-60 flex flex-col items-center">
        <input type="file" ref="fileInput" accept=".png,.jpg,.jpeg,.gif,.svg,.txt,.gcode" class="hidden"
          @change="() => handleFileUpload(false)" />
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
    <div v-show="showRasterPanel" class="modal" @click="() => { showRasterPanel = false }">
      <div class="modal-content" @click.stop>
        <h3 class="font-medium">Uploading a raster image</h3>
        <div>
          <div class="inputGroup" @change="() => { handleFileUpload(false) }">
            <label>
              <span>Filter Speckle</span>
              <div class="slider-container">
                <input type="range" v-model="filter_speckle" min="0" max="128" class="slider" />
                <span>{{ filter_speckle }}</span>
              </div>
            </label>
            <label>
              <span>Curve Fitting</span>
              <select v-model="curve_fitting" class="input-field">
                <option value="polygon">Polygon</option>
                <option value="spline">Spline</option>
                <option value="none">Pixel</option>
              </select>
            </label>
            <div v-if="curve_fitting === 'spline'" class="flex flex-col gap-4">
              <label>
                <span>Corner Threshold</span>
                <div class="slider-container">
                  <input type="range" v-model="corner_threshold" min="0" max="360" class="slider" />
                  <span>{{ corner_threshold }}</span>
                </div>
              </label>
              <label>
                <span>Segment Length</span>
                <div class="slider-container">
                  <input type="range" v-model="segment_length" min="0" max="100" class="slider" />
                  <span>{{ segment_length }}</span>
                </div>
              </label>
              <label>
                <span>Splice Threshold</span>
                <div class="slider-container">
                  <input type="range" v-model="splice_threshold" min="0" max="100" class="slider" />
                  <span>{{ splice_threshold }}</span>
                </div>
              </label>
            </div>
          </div>
        </div>
        <div class="images-preview">
          <img v-if="($refs.fileInput as HTMLInputElement)?.files?.[0]"
            :src="window.URL.createObjectURL(($refs.fileInput as HTMLInputElement).files[0])" alt="Preview"
            class="w-1/3 h-auto max-h-56 object-contain" />
          <ArrowRight :size="24" />
          <img v-if="previewImage" :src="previewImage" alt="Preview" class="w-1/3 h-auto max-h-56 object-contain" />
        </div>
        <div class="modal-actions">
          <button class="confirm-button" @click="() => handleFileUpload(true)">Confirm</button>
          <button class="cancel-button" @click="() => { showRasterPanel = false }">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal {
  cursor: pointer;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  cursor: default;
  background: var(--color-background);
  color: var(--color-text);
  padding: 20px;
  border-radius: 8px;
  text-align: center;

}

.modal-actions {
  display: flex;
  flex: 1;
  justify-content: end;
  margin-top: 30px;
}

.modal-actions .confirm-button {
  margin: 0 10px;
  cursor: pointer;
  background-color: var(--vt-c-brand);
  color: var(--color-background);
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  transition: all 0.2s ease-in-out;
}

.modal-actions .confirm-button:hover {
  filter: brightness(1.2);
}

.modal-actions .cancel-button {
  margin: 0 10px;
  cursor: pointer;
  border: none;
  border-radius: 5px;
  transition: all 0.2s ease-in-out;
}

.modal-actions .cancel-button:hover {
  color: var(--vt-c-red);
}

.images-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}
.inputGroup {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 40px;
}

.inputGroup label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 1em;
}

/* .slider-container input[type="range"] {
            margin-right: 50px;
          } */

.slider-container span {
  width: 2em;
  text-align: right;
}
</style>
