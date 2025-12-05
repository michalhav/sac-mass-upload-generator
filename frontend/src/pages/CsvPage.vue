<script setup>
import { ref, computed } from 'vue'
import { useProjectStore } from '@/stores/project'
import api from '@/api/client'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { Upload, Link, ExternalLink, RefreshCw, Trash2, FileSpreadsheet, Check } from 'lucide-vue-next'

const store = useProjectStore()

const urls = ref([])
const loadingUrls = ref(false)
const isDragging = ref(false)
const fileInput = ref(null)

const csvFilesByName = computed(() => {
  const map = {}
  store.csvFiles.forEach(f => {
    map[f.name] = f
  })
  return map
})

async function generateUrls() {
  loadingUrls.value = true
  try {
    const { data } = await api.getUrls(store.currentProject)
    urls.value = data.urls || []
  } finally {
    loadingUrls.value = false
  }
}

function openAllUrls() {
  urls.value.forEach(u => window.open(u.url, '_blank'))
}

function handleDragOver(e) {
  e.preventDefault()
  isDragging.value = true
}

function handleDragLeave() {
  isDragging.value = false
}

async function handleDrop(e) {
  e.preventDefault()
  isDragging.value = false
  
  const files = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.csv'))
  if (files.length) {
    await store.uploadCsvFiles(files)
  }
}

async function handleFileSelect(e) {
  const files = Array.from(e.target.files).filter(f => f.name.endsWith('.csv'))
  if (files.length) {
    await store.uploadCsvFiles(files)
  }
  e.target.value = ''
}

async function deleteCsv(filename) {
  if (confirm(`Delete ${filename}?`)) {
    await store.deleteCsvFile(filename)
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">CSV Files</h2>
    
    <Card class="p-4 mb-6 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
      <h3 class="font-semibold text-blue-700 dark:text-blue-300 mb-2">📁 How to get CSV files from SAC</h3>
      <ol class="text-sm text-blue-600 dark:text-blue-400 space-y-1 list-decimal list-inside">
        <li>First add your dimensions in the Dimensions tab</li>
        <li>Click "Generate URLs" to create download links</li>
        <li>Click each link (or "Open All") to download in your browser</li>
        <li>Drag & drop downloaded files below</li>
      </ol>
    </Card>
    
    <div
      class="border-2 border-dashed rounded-lg p-8 text-center mb-6 transition-colors cursor-pointer"
      :class="isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      @click="fileInput?.click()"
    >
      <Upload class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
      <p class="font-medium">Drag & Drop CSV files here</p>
      <p class="text-sm text-muted-foreground">or click to browse</p>
      <input ref="fileInput" type="file" multiple accept=".csv" class="hidden" @change="handleFileSelect" />
    </div>
    
    <div class="flex gap-2 mb-6">
      <Button @click="generateUrls" :loading="loadingUrls">
        <Link class="mr-2 h-4 w-4" />
        Generate URLs
      </Button>
      <Button variant="secondary" @click="openAllUrls" :disabled="!urls.length">
        <ExternalLink class="mr-2 h-4 w-4" />
        Open All URLs
      </Button>
      <Button variant="outline" @click="store.refreshCsvFiles">
        <RefreshCw class="mr-2 h-4 w-4" />
        Refresh
      </Button>
    </div>
    
    <div v-if="urls.length" class="mb-6">
      <h3 class="font-semibold mb-3">Download URLs</h3>
      <div class="space-y-2">
        <div v-for="u in urls" :key="u.name" class="flex items-center gap-3 p-3 rounded-lg border bg-card">
          <Check v-if="csvFilesByName[u.name]" class="h-5 w-5 text-green-500 flex-shrink-0" />
          <FileSpreadsheet v-else class="h-5 w-5 text-muted-foreground flex-shrink-0" />
          <span class="font-medium min-w-[150px]">{{ u.name }}</span>
          <a :href="u.url" target="_blank" class="text-xs text-primary hover:underline truncate flex-1 font-mono">
            {{ u.url }}
          </a>
        </div>
      </div>
    </div>
    
    <div>
      <h3 class="font-semibold mb-3">Downloaded Files</h3>
      <div v-if="!store.csvFiles.length" class="text-muted-foreground text-center py-8">
        No CSV files uploaded yet.
      </div>
      <div class="space-y-2">
        <div v-for="file in store.csvFiles" :key="file.filename" class="flex items-center gap-3 p-3 rounded-lg border bg-card">
          <Check class="h-5 w-5 text-green-500 flex-shrink-0" />
          <span class="font-medium flex-1">{{ file.name }}</span>
          <span class="text-sm text-muted-foreground">{{ file.rows }} rows, {{ file.columns }} cols</span>
          <Button variant="ghost" size="icon" @click="deleteCsv(file.filename)">
            <Trash2 class="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
