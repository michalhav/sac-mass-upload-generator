<script setup>
import { ref, onMounted, watch } from 'vue'
import { useProjectStore } from '@/stores/project'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'
import { Save } from 'lucide-vue-next'

const store = useProjectStore()

const form = ref({
  sac_connection: {
    base_url: '',
    model_id: '',
    version_model_id: ''
  },
  version: {
    version_id: 'public.RF_CURRENT',
    start_column: 'StartMonth',
    end_column: 'EndMonth'
  },
  date_range: {
    start_month: '',
    end_month: ''
  },
  settings: {
    data_rows: 200
  },
  colors: {
    dim_header: '#c6e0b4',
    date_header: '#bdd7ee',
    dim_cell: '#e2efda'
  }
})

const saving = ref(false)

onMounted(() => {
  loadSettings()
})

watch(() => store.settings, loadSettings, { deep: true })

function loadSettings() {
  if (store.settings) {
    form.value = {
      sac_connection: {
        base_url: store.settings.sac_connection?.base_url || '',
        model_id: store.settings.sac_connection?.model_id || '',
        version_model_id: store.settings.sac_connection?.version_model_id || ''
      },
      version: {
        version_id: store.settings.version?.version_id || 'public.RF_CURRENT',
        start_column: store.settings.version?.start_column || 'StartMonth',
        end_column: store.settings.version?.end_column || 'EndMonth'
      },
      date_range: {
        start_month: store.settings.date_range?.start_month || '',
        end_month: store.settings.date_range?.end_month || ''
      },
      settings: {
        data_rows: store.settings.settings?.data_rows || 200
      },
      colors: {
        dim_header: store.settings.colors?.dim_header || '#c6e0b4',
        date_header: store.settings.colors?.date_header || '#bdd7ee',
        dim_cell: store.settings.colors?.dim_cell || '#e2efda'
      }
    }
  }
}

async function save() {
  saving.value = true
  try {
    await store.saveSettings(form.value)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl">
    <h2 class="text-2xl font-bold mb-6">Project Settings</h2>
    
    <Card class="p-6 mb-6">
      <h3 class="text-lg font-semibold mb-4">SAC Connection</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Base URL</label>
          <Input v-model="form.sac_connection.base_url" placeholder="https://your-tenant.eu20.analytics.cloud.sap" />
          <p class="text-xs text-muted-foreground mt-1">Your SAC tenant URL (without trailing slash)</p>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Model ID</label>
            <Input v-model="form.sac_connection.model_id" placeholder="e.g., C6ustb1qd2rgiicfcl8b6c6pa39" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Version Model ID</label>
            <Input v-model="form.sac_connection.version_model_id" placeholder="For date range" />
          </div>
        </div>
      </div>
    </Card>
    
    <Card class="p-6 mb-6">
      <h3 class="text-lg font-semibold mb-4">Version Settings</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Version ID</label>
          <Input v-model="form.version.version_id" placeholder="public.RF_CURRENT" />
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Start Column</label>
            <Input v-model="form.version.start_column" placeholder="StartMonth" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">End Column</label>
            <Input v-model="form.version.end_column" placeholder="EndMonth" />
          </div>
        </div>
      </div>
    </Card>
    
    <Card class="p-6 mb-6">
      <h3 class="text-lg font-semibold mb-4">Manual Date Range (Optional)</h3>
      <p class="text-sm text-muted-foreground mb-4">Leave empty to use Version from CSV</p>
      
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Start Month</label>
          <Input v-model="form.date_range.start_month" placeholder="202501" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">End Month</label>
          <Input v-model="form.date_range.end_month" placeholder="202512" />
        </div>
      </div>
    </Card>
    
    <Card class="p-6 mb-6">
      <h3 class="text-lg font-semibold mb-4">Excel Settings</h3>
      
      <div class="mb-4">
        <label class="block text-sm font-medium mb-1">Data Rows</label>
        <Input v-model.number="form.settings.data_rows" type="number" class="w-32" />
      </div>
      
      <h4 class="font-medium mb-3">Colors</h4>
      <div class="flex gap-6">
        <div>
          <label class="block text-sm mb-1">Dimension Headers</label>
          <input type="color" v-model="form.colors.dim_header" class="w-12 h-8 rounded cursor-pointer" />
        </div>
        <div>
          <label class="block text-sm mb-1">Date Headers</label>
          <input type="color" v-model="form.colors.date_header" class="w-12 h-8 rounded cursor-pointer" />
        </div>
        <div>
          <label class="block text-sm mb-1">Dimension Cells</label>
          <input type="color" v-model="form.colors.dim_cell" class="w-12 h-8 rounded cursor-pointer" />
        </div>
      </div>
    </Card>
    
    <Button @click="save" :loading="saving">
      <Save class="mr-2 h-4 w-4" />
      Save Settings
    </Button>
  </div>
</template>
