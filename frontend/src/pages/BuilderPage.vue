<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'
import { Plus, X, GripVertical, Settings, Save, Trash2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()

const templateName = ref('')
const columns = ref([])
const overrides = ref({})

const availableDimensions = computed(() => 
  store.dimensions.filter(d => !columns.value.includes(d.name))
)

onMounted(() => {
  if (route.query.edit) {
    loadTemplate(route.query.edit)
  }
})

watch(() => route.query.edit, (name) => {
  if (name) loadTemplate(name)
})

function loadTemplate(name) {
  const tpl = store.templates.find(t => t.name === name)
  if (tpl) {
    templateName.value = tpl.name
    columns.value = [...tpl.columns]
    overrides.value = tpl.dimension_overrides ? { ...tpl.dimension_overrides } : {}
  }
}

function addColumn(dimName) {
  if (!columns.value.includes(dimName)) {
    columns.value.push(dimName)
  }
}

function removeColumn(dimName) {
  columns.value = columns.value.filter(c => c !== dimName)
  delete overrides.value[dimName]
}

function moveColumn(from, to) {
  const item = columns.value.splice(from, 1)[0]
  columns.value.splice(to, 0, item)
}

async function save() {
  if (!templateName.value || columns.value.length === 0) return
  
  const template = {
    name: templateName.value,
    output_file: templateName.value + '.xlsx',
    columns: [...columns.value]
  }
  
  if (Object.keys(overrides.value).length > 0) {
    template.dimension_overrides = { ...overrides.value }
  }
  
  await store.saveTemplate(template)
  router.push('/templates')
}

function clear() {
  templateName.value = ''
  columns.value = []
  overrides.value = {}
  router.replace('/builder')
}

// Drag and drop
let dragIndex = null

function onDragStart(index) {
  dragIndex = index
}

function onDragOver(e, index) {
  e.preventDefault()
  if (dragIndex !== null && dragIndex !== index) {
    moveColumn(dragIndex, index)
    dragIndex = index
  }
}

function onDragEnd() {
  dragIndex = null
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Template Builder</h2>
    
    <div class="flex gap-4 mb-6">
      <div class="flex-1">
        <label class="block text-sm font-medium mb-1">Template Name</label>
        <Input v-model="templateName" placeholder="e.g., FTE_Planning_Template" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Load Existing</label>
        <select 
          class="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          @change="e => { if (e.target.value) loadTemplate(e.target.value); e.target.value = '' }"
        >
          <option value="">-- Select --</option>
          <option v-for="tpl in store.templates" :key="tpl.name" :value="tpl.name">
            {{ tpl.name }}
          </option>
        </select>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Available Dimensions -->
      <Card class="p-4">
        <h3 class="font-semibold text-primary mb-3">Available Dimensions</h3>
        <p class="text-sm text-muted-foreground mb-4">Click to add to template</p>
        
        <div class="flex flex-wrap gap-2 min-h-[100px] p-3 border-2 border-dashed rounded-lg">
          <button
            v-for="dim in availableDimensions"
            :key="dim.name"
            @click="addColumn(dim.name)"
            class="px-3 py-1.5 rounded-full border bg-card hover:bg-accent hover:border-primary transition-colors text-sm"
          >
            {{ dim.name }}
          </button>
          <div v-if="!availableDimensions.length" class="text-muted-foreground text-sm">
            All dimensions added
          </div>
        </div>
      </Card>
      
      <!-- Template Columns -->
      <Card class="p-4">
        <h3 class="font-semibold text-primary mb-3">Template Columns</h3>
        <p class="text-sm text-muted-foreground mb-4">Drag to reorder, click ✕ to remove</p>
        
        <div class="min-h-[100px] p-3 border-2 border-dashed border-green-300 dark:border-green-700 rounded-lg bg-green-50 dark:bg-green-950">
          <div
            v-for="(col, index) in columns"
            :key="col"
            draggable="true"
            @dragstart="onDragStart(index)"
            @dragover="e => onDragOver(e, index)"
            @dragend="onDragEnd"
            class="flex items-center gap-2 p-2 mb-2 rounded border bg-card cursor-move"
          >
            <GripVertical class="h-4 w-4 text-muted-foreground" />
            <span class="flex-1 font-medium">{{ col }}</span>
            <Button variant="ghost" size="icon" class="h-8 w-8" @click="removeColumn(col)">
              <X class="h-4 w-4" />
            </Button>
          </div>
          
          <div v-if="!columns.length" class="text-muted-foreground text-sm text-center py-4">
            Click dimensions to add them here
          </div>
        </div>
        
        <div class="mt-4 p-3 rounded bg-blue-50 dark:bg-blue-950 text-sm text-blue-600 dark:text-blue-400">
          📅 + Date columns will be added automatically (based on Version settings)
        </div>
      </Card>
    </div>
    
    <div class="mt-6 flex gap-2">
      <Button @click="save" :disabled="!templateName || !columns.length">
        <Save class="mr-2 h-4 w-4" />
        Save Template
      </Button>
      <Button variant="outline" @click="clear">
        <Trash2 class="mr-2 h-4 w-4" />
        Clear
      </Button>
    </div>
  </div>
</template>
