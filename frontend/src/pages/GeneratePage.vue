<script setup>
import { ref, computed } from 'vue'
import { useProjectStore } from '@/stores/project'
import api from '@/api/client'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { Rocket, CheckCircle, AlertCircle, Download, RefreshCw } from 'lucide-vue-next'

const store = useProjectStore()

const selected = ref([])
const selectAll = ref(true)
const validation = ref(null)
const generating = ref(false)
const results = ref(null)

const allSelected = computed({
  get: () => selected.value.length === store.templates.length,
  set: (val) => {
    selected.value = val ? store.templates.map(t => t.name) : []
  }
})

// Initialize selection
if (store.templates.length) {
  selected.value = store.templates.map(t => t.name)
}

async function validate() {
  validation.value = null
  try {
    const { data } = await api.validate(store.currentProject)
    validation.value = data
  } catch (e) {
    validation.value = { valid: false, errors: [e.message], warnings: [] }
  }
}

async function generate() {
  if (!selected.value.length) return
  
  generating.value = true
  results.value = null
  
  try {
    const { data } = await api.generate(store.currentProject, selected.value)
    results.value = data.results
  } catch (e) {
    results.value = { success: [], failed: [{ name: 'Error', error: e.message }] }
  } finally {
    generating.value = false
  }
}

function downloadFile(filename) {
  window.open(api.downloadUrl(store.currentProject, filename), '_blank')
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Generate Excel Files</h2>
    
    <!-- Validation -->
    <div v-if="validation" class="mb-6">
      <Card v-if="validation.errors?.length" class="p-4 bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800 mb-4">
        <div class="flex items-start gap-2">
          <AlertCircle class="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h4 class="font-semibold text-red-700 dark:text-red-300">Errors</h4>
            <ul class="text-sm text-red-600 dark:text-red-400 list-disc list-inside mt-1">
              <li v-for="err in validation.errors" :key="err">{{ err }}</li>
            </ul>
          </div>
        </div>
      </Card>
      
      <Card v-if="validation.warnings?.length" class="p-4 bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800 mb-4">
        <div class="flex items-start gap-2">
          <AlertCircle class="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
          <div>
            <h4 class="font-semibold text-yellow-700 dark:text-yellow-300">Warnings</h4>
            <ul class="text-sm text-yellow-600 dark:text-yellow-400 list-disc list-inside mt-1">
              <li v-for="warn in validation.warnings" :key="warn">{{ warn }}</li>
            </ul>
          </div>
        </div>
      </Card>
      
      <Card v-if="validation.valid && !validation.errors?.length && !validation.warnings?.length" class="p-4 bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800">
        <div class="flex items-center gap-2">
          <CheckCircle class="h-5 w-5 text-green-500" />
          <span class="text-green-700 dark:text-green-300 font-medium">All validations passed! Ready to generate.</span>
        </div>
      </Card>
    </div>
    
    <!-- Template Selection -->
    <Card class="p-4 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold">Select Templates to Generate</h3>
        <Button variant="outline" size="sm" @click="validate">
          <RefreshCw class="mr-2 h-4 w-4" />
          Validate
        </Button>
      </div>
      
      <div v-if="!store.templates.length" class="text-muted-foreground py-4">
        No templates configured. Create one in the Builder tab.
      </div>
      
      <div v-else>
        <label class="flex items-center gap-2 mb-3 font-medium">
          <input type="checkbox" v-model="allSelected" class="rounded" />
          Select All
        </label>
        
        <div class="space-y-2 ml-6">
          <label v-for="tpl in store.templates" :key="tpl.name" class="flex items-center gap-2">
            <input type="checkbox" :value="tpl.name" v-model="selected" class="rounded" />
            <span>{{ tpl.name }}</span>
            <span class="text-muted-foreground">→ {{ tpl.output_file }}</span>
          </label>
        </div>
      </div>
    </Card>
    
    <Button @click="generate" :loading="generating" :disabled="!selected.length" size="lg">
      <Rocket class="mr-2 h-5 w-5" />
      Generate Selected Templates
    </Button>
    
    <!-- Results -->
    <div v-if="results" class="mt-6">
      <Card v-if="results.success?.length" class="p-4 bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800 mb-4">
        <h4 class="font-semibold text-green-700 dark:text-green-300 mb-3">
          <CheckCircle class="inline h-5 w-5 mr-1" />
          Generated {{ results.success.length }} file(s)
        </h4>
        <div class="space-y-2">
          <div v-for="item in results.success" :key="item.name" class="flex items-center gap-2">
            <span>{{ item.file }}</span>
            <Button size="sm" variant="outline" @click="downloadFile(item.file)">
              <Download class="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
      
      <Card v-if="results.failed?.length" class="p-4 bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800">
        <h4 class="font-semibold text-red-700 dark:text-red-300 mb-2">
          <AlertCircle class="inline h-5 w-5 mr-1" />
          Failed
        </h4>
        <ul class="text-sm text-red-600 dark:text-red-400 list-disc list-inside">
          <li v-for="item in results.failed" :key="item.name">
            {{ item.name }}: {{ item.error }}
          </li>
        </ul>
      </Card>
    </div>
  </div>
</template>
