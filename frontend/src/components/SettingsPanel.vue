<script lang="ts">
import type { PropType } from 'vue';

export default {
    props: {
        toggleSettingsPanel: {
            type: Function as PropType<(payload: MouseEvent) => void>,
            required: true
        },
        serverURL: String,
        setServerURL: {
            type: Function as PropType<(payload: string) => void>,
            required: true
        },
    },
}
</script>

<template>
    <div>
        <button class="flex fixed inset-0 bg-black opacity-35 z-10" @click="toggleSettingsPanel" />
        <div id="settingsPanel"
            class="flex flex-col fixed place-self-center bg-[var(--color-background-soft)] inset-0 h-fit z-20 px-4 pb-4 pt-2 rounded-lg shadow-md transition-all w-fit gap-4">
            <h3 class="text-lg font-bold">Server URL</h3>
            <div>
                <div class="flex gap-2">
                    <input id="serverURLInput" class="w-50 px-2 py-1.5 rounded-lg bg-[var(--color-background-mute)]"
                        :value="serverURL"
                        @change="(e: Event) => { setServerURL((e.target as HTMLInputElement).value) }">
                    <!-- <button id="saveServerBtn"
                        class="cursor-pointer bg-blue-500 text-white px-4 rounded hover:bg-blue-600 transition-colors">Save</button> -->
                </div>
                <div id="ipError" class="text-red-500 mt-1"></div>
            </div>
        </div>
    </div>
</template>