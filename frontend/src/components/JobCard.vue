<script lang="ts">
import { Trash2, Play, Pause, Upload, RotateCcw } from 'lucide-vue-next';
import type { PropType } from 'vue';

export default {
  components: {
    Trash2,
    Play,
    Pause,
    Upload,
    RotateCcw
  },
  props: {
    job: { type: String, required: true },
    running: Boolean,
    uploaded: Boolean,
    start: { type: Function as PropType<(job: string) => void>, required: true },
    pause: { type: Function as PropType<(job: string) => void>, required: true },
    remove: { type: Function as PropType<(job: string) => void>, required: true },
    reset: { type: Function as PropType<(job: string) => void>, required: true },
    upload: { type: Function as PropType<(job: string) => void>, required: true },
    uploading: Boolean,
    not_default: { type: Boolean, default: true },
    fetchPreview: {
      type: Function as PropType<(job: string) => Promise<string>>,
      required: true
    },
  },
  data() {
    return {
      preview: '',
    };
  },
  mounted() {
    this.fetchPreview(this.job)
      .then((preview) => {
        this.preview = preview;
      })
      .catch((error) => {
        console.error('Error fetching preview:', error);
      });
  },
}
</script>

<template>
  <div
    class="flex bg-[var(--color-background-soft)] p-2 pr-5 rounded-lg w-full justify-between align-middle items-center">
    <div class="flex flex-row items-center">
      <div class="w-14 h-14 flex flex-row justify-center align-middle rounded-lg bg-[var(--color-background)] p-2">
        <img v-if="preview" :src="preview" alt="Preview" class="previewImage w-auto h-auto rounded-lg object-cover" />
      </div>
      <h2 class="pl-3 text-xl">{{ job }}</h2>
    </div>
    <div class="flex gap-3 items-center align-middle">
      <button v-if="running" @click="() => pause(job as string)" class="cursor-pointer">
        <Pause :size="24" class="hover:text-neutral-600 dark:hover:text-neutral-400 transition-colors" />
      </button>
      <div v-else-if="uploaded" class="flex gap-3 items-center align-middle">
        <button @click="() => start(job as string)" class="cursor-pointer">
          <Play :size="24"
            class="text-green-500 dark:text-green-600 hover:text-green-600 dark:hover:text-green-700 transition-colors" />
        </button>
        <button @click="() => reset(job as string)" class="cursor-pointer">
          <RotateCcw :size="24" class="hover:text-neutral-600 dark:hover:text-neutral-400 transition-colors" />
        </button>
      </div>
      <div v-else class="flex justify-center">
        <div v-if="uploading" class="flex justify-center">
          <svg class="animate-spin h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none"
            viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="var(--vt-c-brand)"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <button v-else @click="() => upload(job as string)"
          class="cursor-pointer hover:text-neutral-600 dark:hover:text-neutral-400 transition-colors">
          <Upload :size="24" />
        </button>
      </div>
      <button v-if="not_default" @click="() => remove(job as string)" class="cursor-pointer">
        <Trash2 :size="24"
          class="text-red-500 dark:text-red-600 transition-colors hover:text-red-600 hover:dark:text-red-700" />
      </button>
    </div>
  </div>
</template>

