<script lang="ts">
import SettingsPanel from './components/SettingsPanel.vue'
import Queue from './components/JobsList.vue'
import { Unplug } from 'lucide-vue-next';

export default {
  components: {
    SettingsPanel,
    Unplug,
    Queue
  },
  data() {
    return {
      serverURL: 'http://localhost:3000',
      connectionOk: false,
      serialPorts: [] as string[],
      settingsPanelVisible: false,
      serialPortPanelVisible: false,
      uploaded: null as string | null,
      running: false,
      showFullTitle: false
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
        .then(() => {
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
          this.serialPorts = data.map((obj: { device: string }) => obj.device);
        })
        .catch(error => {
          console.error('There has been a problem with the connection:', error);
        });
    },
    fetchState() {
      fetch(`${this.serverURL}/state`)
        .then(response => {
          if (!response.ok) {
            console.log(response);
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // uploaded: string
          // running: boolean
          this.uploaded = data.uploaded;
          this.running = data.running;
        }).catch(error => {
          console.error('There has been a problem with the connection:', error

          );
        });
    }
  },
  watch: {
    serverURL(newURL: string) {
      if (newURL.endsWith('/')) {
        this.serverURL = newURL.slice(0, -1);
      }
      this.checkConnection();
    },
    connectionOk(newStatus: boolean) {
      if (newStatus) {
        this.fetchSerialPorts();
        this.fetchState();
      }
      else {
        this.serialPorts = [];
        this.uploaded = null;
        this.running = false;
      }
    }
  },
  mounted() {
    setInterval(() => {
      this.checkConnection();
      if (this.connectionOk) {
        this.fetchState();
        // this.fetchSerialPorts();
      }
    }, 2000);
  }

}
</script>

<template>
  <header class="header" @dragover.prevent @drop.prevent>
    <div class="flex flex-row items-center w-full justify-between pb-4 md:px-4 lg:px-8">
      <div class="flex items-center gap-2 md:gap-4 cursor-default" @mousedown.prevent @selectstart.prevent>
        <h1 class="pb-1 text-3xl md:text-3xl cursor-pointer" @click="() => { showFullTitle = !showFullTitle }">🌶️</h1>
        <h1 class="font-medium tracking-widest text-4xl md:text-3xl md:pl-1 lg:pl-3">
          <span v-if="!showFullTitle">PEPERONCINO</span>
          <span v-else class="text-sm md:text-base">Plotter Estremamente Preciso E Reattivo Ottimizzato Nel Controllo
            Istantaneo Non Ostruibile</span>
        </h1>
      </div>
      <div class="flex items-center gap-1 md:gap-2 lg:gap-4">
        <button id="serial-port-icon">
          <Unplug :size="30"
            :class="{ 'text-green-500 dark:text-green-600': connectionOk, 'text-red-500 dark:text-red-600': !connectionOk }" />
        </button>
        <button id="settings-icon" class="w-10 h-10 cursor-pointer hover:text-[var(--vt-c-brand)]"
          @click="() => { toggleSettingsPanel() }">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          </svg>
        </button>
      </div>
    </div>
  </header>
  <main class="main h-full" @dragover.prevent @drop.prevent>
    <SettingsPanel v-show="settingsPanelVisible" :toggleSettingsPanel="toggleSettingsPanel" :serverURL="serverURL"
      :setServerURL="(url) => { serverURL = url }" :connectionOk="connectionOk" :options="serialPorts"
      :fetchSerialPorts="fetchSerialPorts" />
    <Queue :connectionOk="connectionOk" :serverURL="serverURL" :uploaded="uploaded" :running="running"
      :fetchState="fetchState" />
  </main>
</template>

<style scoped>
#settings-icon:hover {
  transform: rotate(45deg);
    transition: transform 0.3s;
}
</style>
