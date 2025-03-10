<script lang="ts">
import type { PropType } from 'vue';

export default {
    data() {
        return {
            selectedPort: ''
        }
    },
    props: {
        toggleSerialPortPanel: {
            type: Function as PropType<(payload: MouseEvent) => void>,
            required: true
        },
        fetchSerialPorts: {
            type: Function as PropType<() => string[]>,
            required: true
        },
        options: {
            type: Array as PropType<string[]>,
            required: true
        },
        serverURL: { type: String, required: true },
        connectionOk: { type: Boolean, required: true }
    },
    methods: {
        fetchSelectedPort() {
            if (this.connectionOk) {
                fetch(`${this.serverURL}/ports/selected`)
                    .then(response => {
                        if (!response.ok) {
                            console.log(response);
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        this.selectedPort = data;
                    })
                    .catch(error => {
                        console.error('There has been a problem with the connection:', error);
                    });
            }
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
                    return response.json();
                }
            ).then(data => { }).catch(error => {
                console.error('There has been a problem with the connection:', error);
            }
            );
        },
    },
    mounted() {
        if (this.connectionOk)
            this.fetchSelectedPort();
    },
    watch: {
        selectedPort: function (newVal: string) {
            this.setSelectedPort(newVal);
        }
    }
}
</script>

<template>
    <div>
        <button class="flex fixed inset-0 bg-black opacity-35 z-10" @click="toggleSerialPortPanel" />
        <div id="portPanel"
            class="flex flex-col fixed place-self-center bg-[var(--color-background-soft)] inset-0 h-fit z-20 px-4 pb-4 pt-2 rounded-lg shadow-md transition-all w-fit gap-2">
            <h3 class="text-lg font-bold">Plotter Serial Port</h3>
                <select id="ports"
                    class="block w-full text-sm rounded-lg bg-[var(--color-background-mute)] px-2 py-1.5 cursor-pointer"
                    v-model="selectedPort">
                    <option :key="option" v-for="option in options" :value="option">
                        {{ option }}
                    </option>
                </select>
        </div>
    </div>
</template>