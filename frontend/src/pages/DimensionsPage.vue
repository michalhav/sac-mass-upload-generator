<script setup>
import { ref } from 'vue'
import { useProjectStore } from '@/stores/project'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import { Plus, Pencil, Trash2, X, Save } from 'lucide-vue-next'

const store = useProjectStore()

const showModal = ref(false)
const editingDimension = ref(null)

const form = ref({
  name: '',
  sac_name: '',
  table_name: '',
  has_hierarchy: true,
  extract_column: '',
  numeric_sort: false,
  filters: {
    parent_filter: '',
    exclude_description: '',
    id_list: ''
  }
})

function openAdd() {
  editingDimension.value = null
  form.value = {
    name: '',
    sac_name: '',
    table_name: '',
    has_hierarchy: true,
    extract_column: '',
    numeric_sort: false,
    filters: { parent_filter: '', exclude_description: '', id_list: '' }
  }
  showModal.value = true
}

function openEdit(dim) {
  editingDimension.value = dim.name
  form.value = {
    name: dim.name,
    sac_name: dim.sac_name || '',
    table_name: dim.table_name || '',
    has_hierarchy: dim.has_hierarchy !== false,
    extract_column: dim.extract_column || '',
    numeric_sort: dim.numeric_sort || false,
    filters: {
      parent_filter: dim.filters?.parent_filter || '',
      exclude_description: Array.isArray(dim.filters?.exclude_description) 
        ? dim.filters.exclude_description.join(', ') 
        : dim.filters?.exclude_description || '',
      id_list: Array.isArray(dim.filters?.id_list)
        ? dim.filters.id_list.join(', ')
        : dim.filters?.id_list || ''
    }
  }
  showModal.value = true
}

async function save() {
  const dimension = {
    name: form.value.name,
    sac_name: form.value.sac_name,
    table_name: form.value.table_name || `tbl_${form.value.name.toLowerCase().replace(/\s+/g, '_')}`,
    has_hierarchy: form.value.has_hierarchy
  }
  
  if (form.value.extract_column) {
    dimension.extract_column = form.value.extract_column
  }
  if (form.value.numeric_sort) {
    dimension.numeric_sort = true
  }
  
  // Build filters
  const filters = {}
  if (form.value.filters.parent_filter) {
    filters.parent_filter = form.value.filters.parent_filter
  }
  if (form.value.filters.exclude_description) {
    filters.exclude_description = form.value.filters.exclude_description.split(',').map(s => s.trim()).filter(Boolean)
  }
  if (form.value.filters.id_list) {
    filters.id_list = form.value.filters.id_list.split(',').map(s => s.trim()).filter(Boolean)
  }
  
  if (Object.keys(filters).length > 0) {
    dimension.filters = filters
  }
  
  await store.saveDimension(dimension)
  showModal.value = false
}

async function deleteDimension(name) {
  if (confirm(`Delete dimension "${name}"?`)) {
    await store.deleteDimension(name)
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold">Dimensions</h2>
      <Button @click="openAdd">
        <Plus class="mr-2 h-4 w-4" />
        Add Dimension
      </Button>
    </div>
    
    <div v-if="store.dimensions.length === 0" class="text-center py-12 text-muted-foreground">
      No dimensions defined yet. Click "Add Dimension" to create one.
    </div>
    
    <div class="grid gap-4">
      <Card v-for="dim in store.dimensions" :key="dim.name" class="p-4">
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <h3 class="font-semibold">{{ dim.name }}</h3>
              <Badge :variant="dim.has_hierarchy ? 'success' : 'secondary'">
                {{ dim.has_hierarchy ? 'Hierarchy' : 'Flat' }}
              </Badge>
            </div>
            <p class="text-sm text-muted-foreground font-mono">{{ dim.sac_name }}</p>
            
            <div v-if="dim.filters" class="mt-2 text-xs text-muted-foreground">
              <span v-if="dim.filters.parent_filter" class="mr-3">
                Parent: {{ dim.filters.parent_filter }}
              </span>
              <span v-if="dim.filters.exclude_description?.length" class="mr-3">
                Excludes: {{ dim.filters.exclude_description.join(', ') }}
              </span>
              <span v-if="dim.filters.id_list?.length">
                IDs: {{ dim.filters.id_list.length }} items
              </span>
            </div>
          </div>
          
          <div class="flex gap-2">
            <Button variant="ghost" size="icon" @click="openEdit(dim)">
              <Pencil class="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" @click="deleteDimension(dim.name)">
              <Trash2 class="h-4 w-4 text-destructive" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
    
    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-card rounded-lg p-6 w-full max-w-lg shadow-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">
            {{ editingDimension ? 'Edit Dimension' : 'Add Dimension' }}
          </h3>
          <Button variant="ghost" size="icon" @click="showModal = false">
            <X class="h-4 w-4" />
          </Button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Display Name *</label>
            <Input v-model="form.name" placeholder="e.g., Company Code" />
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">SAC Dimension Name *</label>
            <Input v-model="form.sac_name" placeholder="e.g., COL_Co_Code" />
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">Table Name</label>
            <Input v-model="form.table_name" placeholder="e.g., tbl_company" />
            <p class="text-xs text-muted-foreground mt-1">Excel table name (auto-generated if empty)</p>
          </div>
          
          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="form.has_hierarchy" class="rounded" />
              <span class="text-sm">Has Hierarchy</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="form.numeric_sort" class="rounded" />
              <span class="text-sm">Numeric Sort</span>
            </label>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">Extract Column (Optional)</label>
            <Input v-model="form.extract_column" placeholder="e.g., PayGrade" />
            <p class="text-xs text-muted-foreground mt-1">Extract unique values from this column instead of ID</p>
          </div>
          
          <hr class="my-4" />
          <h4 class="font-medium">Filters</h4>
          
          <div>
            <label class="block text-sm font-medium mb-1">Parent Filter</label>
            <Input v-model="form.filters.parent_filter" placeholder="e.g., CoL_Total" />
            <p class="text-xs text-muted-foreground mt-1">Only include leaf members under this parent</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">Exclude Description Contains</label>
            <Input v-model="form.filters.exclude_description" placeholder="e.g., DUMMY, Test, Midpoint" />
            <p class="text-xs text-muted-foreground mt-1">Comma-separated list</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">Include Only IDs</label>
            <Input v-model="form.filters.id_list" placeholder="e.g., ID1, ID2, ID3" />
            <p class="text-xs text-muted-foreground mt-1">Comma-separated list (in order)</p>
          </div>
        </div>
        
        <div class="flex gap-2 justify-end mt-6">
          <Button variant="outline" @click="showModal = false">Cancel</Button>
          <Button @click="save" :disabled="!form.name || !form.sac_name">
            <Save class="mr-2 h-4 w-4" />
            Save
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
