<script setup>
import { ref } from 'vue'
import { useProjectStore } from '@/stores/project'
import api from '@/api/client'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import { Eye, Copy, Pencil, Trash2 } from 'lucide-vue-next'

const store = useProjectStore()

const preview = ref(null)
const loadingPreview = ref(false)

async function showPreview(templateName) {
  loadingPreview.value = true
  try {
    const { data } = await api.previewTemplate(store.currentProject, templateName)
    preview.value = data
  } finally {
    loadingPreview.value = false
  }
}

async function duplicateTemplate(tpl) {
  const newName = tpl.name + '_copy'
  const newTemplate = {
    ...tpl,
    name: newName,
    output_file: newName + '.xlsx'
  }
  await store.saveTemplate(newTemplate)
}

async function deleteTemplate(name) {
  if (confirm(`Delete template "${name}"?`)) {
    await store.deleteTemplate(name)
    if (preview.value?.template === name) {
      preview.value = null
    }
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Saved Templates</h2>
    
    <div v-if="!store.templates.length" class="text-center py-12 text-muted-foreground">
      No templates yet. Use the Builder tab to create one.
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      <Card v-for="tpl in store.templates" :key="tpl.name" class="p-4">
        <div class="flex items-start justify-between mb-2">
          <div>
            <h3 class="font-semibold text-primary">{{ tpl.name }}</h3>
            <Badge v-if="tpl.dimension_overrides" variant="secondary" class="mt-1">
              has overrides
            </Badge>
          </div>
        </div>
        
        <p class="text-sm text-muted-foreground mb-4">
          {{ tpl.columns.join(', ') }}
        </p>
        
        <div class="flex gap-2">
          <Button size="sm" @click="showPreview(tpl.name)" :loading="loadingPreview">
            <Eye class="h-4 w-4" />
          </Button>
          <Button size="sm" variant="outline" @click="duplicateTemplate(tpl)">
            <Copy class="h-4 w-4" />
          </Button>
          <Button size="sm" variant="outline" @click="$router.push({ path: '/builder', query: { edit: tpl.name } })">
            <Pencil class="h-4 w-4" />
          </Button>
          <Button size="sm" variant="destructive" @click="deleteTemplate(tpl.name)">
            <Trash2 class="h-4 w-4" />
          </Button>
        </div>
      </Card>
    </div>
    
    <!-- Preview -->
    <div v-if="preview">
      <h3 class="text-lg font-semibold mb-4">📋 Template Preview: {{ preview.template }}</h3>
      
      <Card class="p-4 overflow-x-auto">
        <p class="text-sm text-muted-foreground mb-4">
          Date range: {{ preview.date_range.join(', ') }}
        </p>
        
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr>
              <th 
                v-for="col in preview.columns" 
                :key="col.name"
                class="border p-2 text-left font-semibold"
                :style="{ backgroundColor: preview.colors?.dim_header || '#c6e0b4' }"
              >
                {{ col.name }}
              </th>
              <th 
                v-for="date in preview.date_range.slice(0, 3)" 
                :key="date"
                class="border p-2 text-left font-semibold"
                :style="{ backgroundColor: preview.colors?.date_header || '#bdd7ee' }"
              >
                {{ date }}
              </th>
              <th v-if="preview.date_range.length > 3" class="border p-2">...</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="i in 3" :key="i">
              <td 
                v-for="col in preview.columns" 
                :key="col.name"
                class="border p-2"
                :style="{ backgroundColor: preview.colors?.dim_cell || '#e2efda' }"
              >
                {{ col.samples[i - 1] || '' }}
              </td>
              <td v-for="date in preview.date_range.slice(0, 3)" :key="date" class="border p-2"></td>
              <td v-if="preview.date_range.length > 3" class="border p-2"></td>
            </tr>
          </tbody>
        </table>
        
        <h4 class="font-semibold mt-6 mb-3">Dimension Details</h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div v-for="col in preview.columns" :key="col.name" class="p-3 rounded bg-muted">
            <div class="font-medium">{{ col.name }}</div>
            <div class="text-sm text-muted-foreground">{{ col.count }} members</div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
