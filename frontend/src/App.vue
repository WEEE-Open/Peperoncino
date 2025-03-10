<script lang="ts">
import SettingsPanel from './components/SettingsPanel.vue'
import SerialPortPanel from './components/SerialPortPanel.vue'
import Queue from './components/Queue.vue'
import { Unplug } from 'lucide-vue-next';

export default {
    components: {
        SettingsPanel,
        SerialPortPanel,
        Unplug,
        Queue
    },
    data() {
        return {
            serverURL: 'http://localhost:8000',
            connectionOk: false,
            serialPorts: [] as string[],
            settingsPanelVisible: false,
            serialPortPanelVisible: false
        }
    },
    methods: {
        toggleSettingsPanel() {
            this.settingsPanelVisible = !this.settingsPanelVisible;
        },
        toggleSerialPortPanel() {
            this.serialPortPanelVisible = !this.serialPortPanelVisible;
        },
        checkConnection() {
            fetch(`${this.serverURL}`)
                .then(response => {
                    if (!response.ok) {
                        console.log(response);
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    this.connectionOk = true;
                })
                .catch(error => {
                    this.connectionOk = false;
                    console.error('There has been a problem with the connection:', error);
                });
        },
        fetchSerialPorts() {
            fetch(`${this.serverURL}/ports`)
                .then(response => {
                    if (!response.ok) {
                        console.log(response);
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    this.serialPorts = data.map((obj: any) => obj.device);
                })
                .catch(error => {
                    console.error('There has been a problem with the connection:', error);
                });
        }
    },
    watch: {
        serverURL(newURL: string, oldURL: string) {
            if (newURL.endsWith('/')) {
                this.serverURL = newURL.slice(0, -1);
            }
            this.checkConnection();
        },
        connectionOk(newStatus: boolean, oldStatus: boolean) {
            if (newStatus) {
                this.fetchSerialPorts();
            }
        }
    },

}
</script>

<template>
    <header class="header">
        <div class="flex flex-row items-center w-full justify-between md:px-4 pb-4">
            <div class="flex items-center gap-2 md:gap-4 cursor-default" @mousedown.prevent @selectstart.prevent>
                <!-- <img alt="Peperoncino logo" class="logo" src="./assets/logo.svg" width="24" height="24" /> -->
                <h1 class="text-2xl md:text-3xl pb-1">🌶️</h1>
                <h1 class="text-xl md:text-2xl font-medium tracking-widest">PEPERONCINO</h1>
            </div>
            <div class="flex items-center gap-2 md:gap-4">
                <button id="serial-port-icon" class="w-8 h-8 cursor-pointer" @click="toggleSerialPortPanel">
                    <Unplug
                        :class="{ 'text-green-500 dark:text-green-600': connectionOk, 'text-red-500 dark:text-red-600': !connectionOk }" />
                </button>
                <button id="settings-icon" class="w-8 h-8 cursor-pointer hover:text-[var(--vt-c-brand)]"
                    @click="() => { toggleSettingsPanel() }">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    </svg>
                </button>
            </div>
        </div>
    </header>
    <main class="main h-full">
        <SettingsPanel v-show="settingsPanelVisible" :toggleSettingsPanel="toggleSettingsPanel" :serverURL="serverURL"
            :setServerURL="(url) => { serverURL = url }" />
        <SerialPortPanel v-show="serialPortPanelVisible" :toggleSerialPortPanel="toggleSerialPortPanel"
            :fetchSerialPorts="fetchSerialPorts" :options="serialPorts" :serverURL="serverURL"
            :connectionOk="connectionOk" />
        <Queue :connectionOk="connectionOk" :serverURL="serverURL" />
    </main>
</template>

<style scoped>
#settings-icon:hover {
    transform: rotate(45deg);
    transition: transform 0.3s;
}
</style>
