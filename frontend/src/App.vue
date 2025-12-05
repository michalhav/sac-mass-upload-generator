<script setup>
import { onMounted, ref, computed } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { useDark, useToggle } from '@vueuse/core'
import Button from '@/components/ui/Button.vue'
import Select from '@/components/ui/Select.vue'
import { 
  Settings, FolderOpen, FileSpreadsheet, Hammer, 
  FileText, Rocket, Moon, Sun, Plus, Download, Upload, Trash2 
} from 'lucide-vue-next'

const RENDER_BASE_URL = 'https://sac-mass-upload-generator.onrender.com'

const router = useRouter()
const store = useProjectStore()
const isDark = useDark()
const toggleDark = useToggle(isDark)

const showNewProject = ref(false)
const newProjectName = ref('')
const importInput = ref(null)

const navItems = [
  { name: 'Settings', path: '/settings', icon: Settings },
  { name: 'Dimensions', path: '/dimensions', icon: FolderOpen },
  { name: 'CSV Files', path: '/csv', icon: FileSpreadsheet },
  { name: 'Builder', path: '/builder', icon: Hammer },
  { name: 'Templates', path: '/templates', icon: FileText },
  { name: 'Generate', path: '/generate', icon: Rocket }
]

onMounted(async () => {
  await store.loadProjects()
  if (store.currentProject) {
    await store.loadProjectData()
  }
})

async function createProject() {
  if (!newProjectName.value.trim()) return
  await store.createProject(newProjectName.value.trim())
  newProjectName.value = ''
  showNewProject.value = false
}

async function handleProjectChange(name) {
  await store.selectProject(name)
}

async function handleDeleteProject() {
  if (!store.currentProject) return
  if (confirm(`Delete project "${store.currentProject}"?`)) {
    await store.deleteProject(store.currentProject)
  }
}

function handleExport() {
  if (!store.currentProject) return
  window.open(`${RENDER_BASE_URL}/api/projects/${store.currentProject}/export`, '_blank')
}

async function handleImport(event) {
  const file = event.target.files?.[0]
  if (!file) return
  
  try {
    const { data } = await import('@/api/client').then(m => m.default.importProject(file))
    await store.loadProjects()
    await store.selectProject(data.name)
  } catch (e) {
    alert('Import failed: ' + e.message)
  }
  
  event.target.value = ''
}

const projectOptions = computed(() => 
  store.projects.map(p => ({ value: p, label: p }))
)
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-primary">📊 SAC Template Generator</h1>
            <p class="text-sm text-muted-foreground">Create Excel templates for SAP Analytics Cloud</p>
          </div>
          
          <div class="flex items-center gap-4">
            <!-- Project Selector -->
            <div class="flex items-center gap-2 rounded-lg border bg-card p-2">
              <FolderOpen class="h-4 w-4 text-muted-foreground" />
              <Select
                :modelValue="store.currentProject"
                @update:modelValue="handleProjectChange"
                :options="projectOptions"
                placeholder="Select Project"
                class="w-40"
              />
              <Button size="sm" @click="showNewProject = true">
                <Plus class="h-4 w-4" />
              </Button>
              <Button size="sm" variant="outline" @click="handleExport" :disabled="!store.currentProject">
                <Download class="h-4 w-4" />
              </Button>
              <Button size="sm" variant="outline" @click="importInput?.click()">
                <Upload class="h-4 w-4" />
              </Button>
              <input ref="importInput" type="file" accept=".zip" class="hidden" @change="handleImport" />
              <Button size="sm" variant="destructive" @click="handleDeleteProject" :disabled="!store.currentProject">
                <Trash2 class="h-4 w-4" />
              </Button>
            </div>
            
            <!-- Dark mode toggle -->
            <Button variant="outline" size="icon" @click="toggleDark()">
              <Sun v-if="isDark" class="h-4 w-4" />
              <Moon v-else class="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        <!-- Navigation -->
        <nav class="mt-4 flex gap-2">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            custom
            v-slot="{ isActive, navigate }"
          >
            <Button
              :variant="isActive ? 'default' : 'ghost'"
              @click="navigate"
              :disabled="!store.hasProject"
            >
              <component :is="item.icon" class="mr-2 h-4 w-4" />
              {{ item.name }}
            </Button>
          </router-link>
        </nav>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
      <div v-if="!store.hasProject" class="text-center py-20">
        <h2 class="text-xl font-semibold mb-2">No Project Selected</h2>
        <p class="text-muted-foreground mb-4">Create or select a project to get started.</p>
        <Button @click="showNewProject = true">
          <Plus class="mr-2 h-4 w-4" />
          New Project
        </Button>
      </div>
      
      <div v-else-if="store.loading" class="text-center py-20">
        <div class="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto"></div>
        <p class="mt-4 text-muted-foreground">Loading...</p>
      </div>
      
      <RouterView v-else />
    </main>
    
    <!-- New Project Modal -->
    <div v-if="showNewProject" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-card rounded-lg p-6 w-full max-w-md shadow-lg">
        <h3 class="text-lg font-semibold mb-4">New Project</h3>
        <input
          v-model="newProjectName"
          type="text"
          placeholder="Project name"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mb-4"
          @keyup.enter="createProject"
        />
        <div class="flex gap-2 justify-end">
          <Button variant="outline" @click="showNewProject = false">Cancel</Button>
          <Button @click="createProject" :disabled="!newProjectName.trim()">Create</Button>
        </div>
      </div>
    </div>
  </div>
</template>
