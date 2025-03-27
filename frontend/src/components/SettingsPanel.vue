<script lang="ts">
import type { PropType } from 'vue';

export default {
    props: {
        toggleSettingsPanel: {
            type: Function as PropType<(payload: MouseEvent) => void>,
            required: true
        },
        setServerURL: {
            type: Function as PropType<(payload: string) => void>,
            required: true
        },
        fetchSerialPorts: {
            type: Function as PropType<() => void>,
            required: true
        },
        options: {
            type: Array as PropType<string[]>,
            required: true
        },
        serverURL: { type: String, required: true },
        connectionOk: { type: Boolean, required: true }
    },
    data() {
        return {
            selectedPort: '' as string,
            speed: 100 as number
        }
    },
    methods: {
        fetchSelectedPort() {
            fetch(`${this.serverURL}/ports/selected`)
                .then(response => {
                    if (!response.ok) {
                        console.log(response);
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    this.selectedPort = data.port ?? '';
                })
                .catch(error => {
                    console.error('There has been a problem with the connection:', error);
                });

        },
        setSelectedPort(port: string) {
            fetch(`${this.serverURL}/ports/selected`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ port: port })
            }).then(
                response => {
                    if (!response.ok) {
                        console.log(response);
                        throw new Error('Network response was not ok');
                    }
                    this.selectedPort = port;
                    return response.json();
                }
            ).then(() => { }).catch(error => {
                console.error('There has been a problem with the connection:', error);
            }
            );
        },
        setSpeed(speed: number) {
            fetch(`${this.serverURL}/speed`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ speed: speed })
            }).then(
                response => {
                    if (!response.ok) {
                        console.log(response);
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                }
            ).then(() => { }).catch(error => {
                console.error('There has been a problem with the connection:', error);
            }
            );
        }
    },
    mounted() {
        if (this.connectionOk)
            this.fetchSelectedPort();
    },
    watch: {
        connectionOk(newValue) {
            if (newValue)
                this.fetchSelectedPort();
            else
                this.selectedPort = '';
        }
    }
}
</script>

<template>
    <div>
        <button class="flex fixed inset-0 bg-black opacity-35 z-10" @click="toggleSettingsPanel" />
        <div id="settingsPanel"
            class="flex flex-col fixed place-self-center bg-[var(--color-background-soft)] inset-0 h-fit z-20 px-4 pb-4 pt-2 rounded-lg shadow-md transition-all w-fit gap-4">
            <h3 class="text-lg font-bold">Settings</h3>
            <div>
                <label for="serverURLInput">Server URL</label>
                <div class="flex gap-2">
                    <input id="serverURLInput" class="w-full px-2 py-1.5 rounded-lg bg-[var(--color-background-mute)]"
                        :value="serverURL"
                        @change="(e: Event) => { setServerURL((e.target as HTMLInputElement).value) }">
                </div>
                <div id="ipError" class="text-red-500 mt-1"></div>
            </div>
            <div>
                <label for="ports">Plotter Serial Port</label>
                <select id="ports" :disabled="!connectionOk"
                    class="block w-full text-sm rounded-lg px-2 py-1.5 cursor-pointer bg-[var(--color-background-mute)] disabled:opacity-50"
                    :class="{ 'border border-red-500': selectedPort === '' }" v-model="selectedPort"
                    @change="() => selectedPort !== '' && setSelectedPort(selectedPort)">
                    <option :key="option" v-for="option in options" :value="option">
                        {{ option }}
                    </option>
                </select>
            </div>
            <div>
                <label for="speedSlider">Plotter Speed</label>
                <div class="flex items-center justify-center cursor-pointer disabled:opacity-50" @selectstart.prevent>
                    <input id="speedSlider" type="range" :min="1" :max="200" :step="1" :disabled="!connectionOk"
                        v-model.number="speed" @change="() => setSpeed(speed)" />
                    <span class="pl-3 pb-0.5 min-w-[4em] text-right text-sm"
                        @dblclick="() => { speed = 100; setSpeed(100); }">{{ speed
                        }}%</span>
                </div>
            </div>
        </div>
    </div>
</template>