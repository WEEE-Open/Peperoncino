<script lang="ts">
import { Trash2, Play, Pause, Upload, RotateCcw } from 'lucide-vue-next';

export default {
    components: {
        Trash2,
        Play,
        Pause,
        Upload,
        RotateCcw
    },
    props: {
        job: String,
        running: Boolean,
        uploaded: Boolean,
        start: Function,
        pause: Function,
        remove: Function,
        reset: Function,
        upload: Function,
    },
}
</script>

<template>
    <div class="flex bg-[var(--color-background-soft)] px-5 py-3 rounded-lg w-full justify-between">
        <h2>{{ job }}</h2>
        <div class="flex gap-3 items-center align-middle">
            <button v-if="running" @click="() => pause(job)" class="cursor-pointer">
                <Pause :size="16" />
            </button>
            <div v-else-if="uploaded" class="flex gap-3 items-center align-middle">
                <button @click="() => start(job)" class="cursor-pointer">
                    <Play :size="16" class="text-green-500 dark:text-green-600" />
                </button>
                <button @click="() => reset(job)" class="cursor-pointer">
                    <RotateCcw :size="16" />
                </button>
            </div>
            <button v-else @click="() => upload(job)" class="cursor-pointer">
                <Upload :size="16" />
            </button>
            <button @click="() => remove(job)" class="cursor-pointer">
                <Trash2 :size="16" class="text-red-500 dark:text-red-600" />
            </button>
        </div>
    </div>
</template>