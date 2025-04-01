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
      pushing_to_plotter: null as string | null,
      dragging_queue: false,
      /* Raster Images Panel */
      window: window, // Expose window to the template,
      showRasterPanel: false,
      previewImage: null as string | null, // b64
      vectorialization_method: 'trace' as 'trace' | 'hatch',
      /* Curve Fitting */
      filter_speckle: 64,
      curve_fitting: 'polygon' as 'polygon' | 'spline' | 'none',
      corner_threshold: 180,
      segment_length: 0,
      splice_threshold: 0,
      /* Hatching */
      interpolation: 'linear' as 'linear' | 'nearest',
      blur_radius: 1,
      hatch_pitch: 5,
      hatch_angle: 45,
      levels: 0,
      invert: false,
      circular: false,
      center: {
        x: 0.5,
        y: 0.5,
      },
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
        // (this.$refs.fileInput as HTMLInputElement).files?.item(0);
        const formData = new FormData();
        formData.append('file', file);

        if ((file.type !== 'image/svg+xml') && (file.type !== 'text/x.gcode')) {
          this.showRasterPanel = true;
          formData.append('vectorialization_method', this.vectorialization_method);
          if (this.vectorialization_method === 'hatch') {
            formData.append('interpolation', this.interpolation);
            formData.append('blur_radius', this.blur_radius.toString());
            formData.append('hatch_pitch', this.hatch_pitch.toString());
            formData.append('hatch_angle', this.hatch_angle.toString());
            formData.append('levels', this.levels.toString());
            formData.append('invert', this.invert.toString());
            formData.append('circular', this.circular.toString());
            if (this.circular) {
              formData.append('center_x', this.center.x.toString());
              formData.append('center_y', this.center.y.toString());
            }
            else {
              formData.append('hatch_angle', this.hatch_angle.toString());
            }
          }
          else {
            formData.append('filter_speckle', this.filter_speckle.toString());
            formData.append('curve_fitting', this.curve_fitting);
            formData.append('corner_threshold', this.corner_threshold.toString());
            formData.append('segment_length', this.segment_length.toString());
            formData.append('splice_threshold', this.splice_threshold.toString());
          }
          if (!final_if_raster) {
            formData.append('tmp', 'true');
          }
          else {
            this.uploading = file.name;
            this.showRasterPanel = false;
          }
        }
        else {
          this.uploading = file.name;
        }

        fetch(`${this.serverURL}/queue`, {
          method: 'POST',
          body: formData,
        })
          .then(response => {
            if (!response.ok) {
              // Try to rename the file if it already exists
              // doesn't work rn
              // if (response.status === 405) {
              //   console.log(file);
              //   const fileName = file.name || '';
              //   const baseName = fileName.split('.').slice(0, -1).join('.');
              //   const extension = fileName.split('.').pop();
              //   const match = baseName.match(/__(\d+)$/);
              //   let newname;
              //   if (match) {
              //     const number = parseInt(match[1], 10) + 1;
              //     newname = `${baseName.replace(/__(\d+)$/, `__${number}`)}.${extension}`;
              //   } else {
              //     newname = `${baseName}__1.${extension}`;
              //   }
              //   formData.delete('file');
              //   formData.append('file', new File([file], newname));
              //   return fetch(`${this.serverURL}/queue`, {
              //     method: 'POST',
              //     body: formData,
              //   });
              // }
              if (response.status === 405) {
                // File already exists
                alert('File already exists, please rename it and try again');
                this.showRasterPanel = false;
              }
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(async (data) => {
            // console.log('File uploaded successfully:', data);
            this.previewImage = await this.fetchPreview(file.name.split('.').slice(0, -1).join('.'));
            this.fetchQueue();
            this.fetchState();
            this.uploading = null;
          })
          .catch(error => {
            console.error('There has been a problem with the file upload:', error);
            this.fetchQueue();
            this.fetchState();
            this.uploading = null;
            if (final_if_raster)
              this.showRasterPanel = false;
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
            if (response.status === 404) {
              // File already exists
              this.fetchQueue();
              this.fetchState();
            }
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
      this.pushing_to_plotter = job;
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
          this.pushing_to_plotter = null;
          this.fetchState();
        })
        .catch(error => {
          console.error('There has been a problem with the job upload:', error);
        });
    },
    async fetchPreview(job: string) {
      return fetch(`${this.serverURL}/queue/${job}/preview`, {
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
          // this.previewImage = `data:image/jpeg;base64,${data.preview}`;
          return `data:image/jpeg;base64,${data.preview}`;
        })
        .catch(error => {
          console.error('There has been a problem with the job preview:', error);
        });
    }
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
            :reset="resetJob" :upload="uploadJob" :uploading="pushing_to_plotter === job" :not_default="false"
            :fetchPreview="fetchPreview" />
          <JobCard v-for="job in jobs" :key="job" :job="job" :uploaded="uploaded === job"
            :running="running && (uploaded === job)" :start="startJob" :pause="pauseJob" :remove="removeJob"
            :reset="resetJob" :upload="uploadJob" :uploading="pushing_to_plotter === job" :not_default="true"
            :fetchPreview="fetchPreview" />
        </div>
      </div>
      <div v-if="uploading"
        class="animated-gradient grow items-center justify-center text-center w-full align-middle border-2 px-4 py-2.5 text-black gap-4 h-fit md:w-3/4 lg:w-1/2">
        Uploading {{ uploading }}...</div>
      <form v-else @submit.prevent="() => handleFileUpload(false)"
        class="w-full h-40 md:h-60 flex flex-col items-center justify-center gap-4">
        <div class="flex flex-col grow justify-center items-center text-center cursor-pointer w-full align-middle
          border-dashed border-2 border-neutral-300 dark:border-neutral-700 px-4 py-2 gap-4 rounded-lg h-fit md:w-3/4
          lg:w-1/2 hover:border-sky-500 hover:text-sky-500 transition-all"
          :class="{ 'border-sky-500 text-sky-500': dragging_queue }" @mousedown.prevent @selectstart.prevent
          @dragenter="() => dragging_queue = true" @dragexit="() => dragging_queue = false"
          @drop.prevent="handleFileDrop" @click="triggerFileInput">
          <input type="file" ref="fileInput" accept=".png,.jpg,.jpeg,.gif,.svg,.txt,.gcode" class="hidden"
            @change="() => handleFileUpload(false)" />
          <CloudUpload :size="36" />
          <p class="capitalize md:hidden">Click here to upload a file</p>
          <p class="capitalize opacity-0 md:opacity-100">Drag a file here or click to upload</p>
        </div>
      </form>
    </div>
    <div v-show="showRasterPanel" class="modal" @click="() => { showRasterPanel = false }">
      <div class="modal-content" @click.stop>
        <h3 class="font-medium">Uploading a raster image</h3>
        <div class="tabgroup">
          <div class="inputGroup" @change="() => { handleFileUpload(false) }">
            <div class="tabgroup-header flex items-center justify-evenly">
              <div class="toggle-button">
                <div @click="(() => { vectorialization_method = 'trace'; handleFileUpload(false) })"
                  :class="{ active: vectorialization_method === 'trace' }">
                  Trace</div>
                <div @click="(() => { vectorialization_method = 'hatch'; handleFileUpload(false) })"
                  :class="{ active: vectorialization_method === 'hatch' }">
                  Hatch</div>
              </div>
            </div>
            <div v-if="vectorialization_method === 'trace'">
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
            <div v-else-if="vectorialization_method === 'hatch'">
              <label>
                <span>Interpolation</span>
                <select v-model="interpolation" class="input-field">
                  <option value="linear">Linear</option>
                  <option value="nearest">Nearest</option>
                </select>
              </label>
              <label>
                <span>Blur Radius</span>
                <div class="slider-container">
                  <input type="range" v-model="blur_radius" min="0" max="10" class="slider" />
                  <span>{{ blur_radius }}</span>
                </div>
              </label>
              <label>
                <span>Hatch Pitch</span>
                <div class="slider-container">
                  <input type="range" v-model="hatch_pitch" min="1" max="10" step="0.1" class="slider" />
                  <span>{{ hatch_pitch }}</span>
                </div>
              </label>
              <label>
                <span>Levels</span>
                <div class="slider-container">
                  <input disabled type="range" v-model="levels" min="0" max="255" class="slider" />
                  <span>{{ levels }}</span>
                </div>
              </label>
              <label>
                <span>Invert</span>
                <input type="checkbox" v-model="invert" />
              </label>
              <label class="switch">
                <span v-if="circular">Circular</span>
                <span v-else>Diagonal</span>
                <input type="checkbox" v-model="circular" />
              </label>
              <label v-if="circular">
                <span>Center</span>
                <div class="flex flex-col gap-2 items-center">
                  <label>
                    <span>X:</span>
                    <input type="range" min="0" max="1" step="0.01" class="slider" v-model="center.x" />
                  </label>
                  <label>
                    <span>Y:</span>
                    <input type="range" min="0" max="1" step="0.01" class="slider" v-model="center.y" />
                  </label>
                </div>
              </label>
              <label v-else>
                <span>Hatch Angle</span>
                <div class="slider-container">
                  <input type="range" v-model="hatch_angle" min="0" max="360" class="slider" />
                  <span>{{ hatch_angle }}</span>
                </div>
              </label>
            </div>
          </div>
          <div class="images-preview">
            <img v-if="($refs.fileInput as HTMLInputElement)?.files?.[0]"
              :src="window.URL.createObjectURL(($refs.fileInput as HTMLInputElement).files[0])" alt="Preview"
              class="w-1/3 h-auto max-h-56 object-contain" />
            <ArrowRight :size="24" />
            <img v-if="previewImage" :src="previewImage" alt="Preview"
              class="previewImage w-1/3 h-auto max-h-56 object-contain" />
          </div>
          <div class="modal-actions">
            <button class="confirm-button" @click="() => handleFileUpload(true)">Confirm</button>
            <button class="cancel-button" @click="() => { showRasterPanel = false }">Cancel</button>
          </div>
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

.toggle-button {
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: fit-content;
  background-color: var(--color-background);
  gap: 8px;
  padding: 8px;
}

.toggle-button div {
  flex-wrap: nowrap;
  text-align: center;
  border-radius: 8px;
  padding: 2px 8px;
  transition: all 0.2s ease-in-out;
}

.toggle-button .active {
  background-color: var(--vt-c-brand);
}

.toggle-button div:not(.active) {
  cursor: pointer;
  background-color: var(--color-background);
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

/* .animated-gradient { // Only animate the border, but doesn't work in chromium
  border: 2px solid #fff0;
  margin: 10px;
  border-radius: 10px;
  background: linear-gradient(var(--color-background)), linear-gradient(to left,
      var(--color-sky-500),
      25%,
      var(--vt-c-brand),
      75%,
      var(--color-sky-500));
  background-clip: padding-box, border-box;
  background-size: 200% 100%;
  background-position: 200%;
  animation: 2s move linear infinite;
} */

.animated-gradient {
  border: 2px solid #0000;
  border-radius: 10px;
  background: linear-gradient(to left,
      var(--color-sky-500),
      25%,
      var(--vt-c-brand),
      75%,
      var(--color-sky-500)) padding-box;
  background-size: 200% 100%;
  background-position: 200%;
  animation: 2s move linear infinite;
}

@keyframes move {
  0% {
    background-position: 200%;
  }

  100% {
    background-position: 0%;
  }
}
</style>
