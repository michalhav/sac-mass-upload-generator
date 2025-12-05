import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export const useProjectStore = defineStore('project', () => {
  // State
  const projects = ref([])
  const currentProject = ref(localStorage.getItem('currentProject') || '')
  const settings = ref({})
  const dimensions = ref([])
  const templates = ref([])
  const csvFiles = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const hasProject = computed(() => !!currentProject.value)
  const dimensionNames = computed(() => dimensions.value.map(d => d.name))

  // Actions
  async function loadProjects() {
    try {
      const { data } = await api.getProjects()
      projects.value = data.projects
      
      // Auto-select if only one project
      if (projects.value.length === 1 && !currentProject.value) {
        await selectProject(projects.value[0])
      }
    } catch (e) {
      error.value = e.message
    }
  }

  async function createProject(name) {
    loading.value = true
    try {
      await api.createProject(name)
      await loadProjects()
      await selectProject(name)
    } finally {
      loading.value = false
    }
  }

  async function deleteProject(name) {
    loading.value = true
    try {
      await api.deleteProject(name)
      if (currentProject.value === name) {
        currentProject.value = ''
        localStorage.removeItem('currentProject')
      }
      await loadProjects()
    } finally {
      loading.value = false
    }
  }

  async function selectProject(name) {
    currentProject.value = name
    localStorage.setItem('currentProject', name)
    await loadProjectData()
  }

  async function loadProjectData() {
    if (!currentProject.value) return
    
    loading.value = true
    error.value = null
    
    try {
      const [settingsRes, dimsRes, tplsRes, csvRes] = await Promise.all([
        api.getSettings(currentProject.value),
        api.getDimensions(currentProject.value),
        api.getTemplates(currentProject.value),
        api.getCsvFiles(currentProject.value)
      ])
      
      settings.value = settingsRes.data || {}
      dimensions.value = dimsRes.data.dimensions || []
      templates.value = tplsRes.data.templates || []
      csvFiles.value = csvRes.data.files || []
    } catch (e) {
      error.value = e.response?.data?.error || e.message
    } finally {
      loading.value = false
    }
  }

  async function saveSettings(data) {
    loading.value = true
    try {
      await api.saveSettings(currentProject.value, data)
      settings.value = data
    } finally {
      loading.value = false
    }
  }

  async function saveDimension(dimension) {
    loading.value = true
    try {
      await api.saveDimension(currentProject.value, dimension.name, dimension)
      const idx = dimensions.value.findIndex(d => d.name === dimension.name)
      if (idx >= 0) {
        dimensions.value[idx] = dimension
      } else {
        dimensions.value.push(dimension)
      }
    } finally {
      loading.value = false
    }
  }

  async function deleteDimension(name) {
    loading.value = true
    try {
      await api.deleteDimension(currentProject.value, name)
      dimensions.value = dimensions.value.filter(d => d.name !== name)
    } finally {
      loading.value = false
    }
  }

  async function saveTemplate(template) {
    loading.value = true
    try {
      await api.saveTemplate(currentProject.value, template.name, template)
      const idx = templates.value.findIndex(t => t.name === template.name)
      if (idx >= 0) {
        templates.value[idx] = template
      } else {
        templates.value.push(template)
      }
    } finally {
      loading.value = false
    }
  }

  async function deleteTemplate(name) {
    loading.value = true
    try {
      await api.deleteTemplate(currentProject.value, name)
      templates.value = templates.value.filter(t => t.name !== name)
    } finally {
      loading.value = false
    }
  }

  async function uploadCsvFiles(files) {
    loading.value = true
    try {
      await api.uploadCsv(currentProject.value, files)
      const { data } = await api.getCsvFiles(currentProject.value)
      csvFiles.value = data.files || []
    } finally {
      loading.value = false
    }
  }

  async function deleteCsvFile(filename) {
    loading.value = true
    try {
      await api.deleteCsv(currentProject.value, filename)
      csvFiles.value = csvFiles.value.filter(f => f.filename !== filename)
    } finally {
      loading.value = false
    }
  }

  async function refreshCsvFiles() {
    const { data } = await api.getCsvFiles(currentProject.value)
    csvFiles.value = data.files || []
  }

  return {
    // State
    projects,
    currentProject,
    settings,
    dimensions,
    templates,
    csvFiles,
    loading,
    error,
    
    // Getters
    hasProject,
    dimensionNames,
    
    // Actions
    loadProjects,
    createProject,
    deleteProject,
    selectProject,
    loadProjectData,
    saveSettings,
    saveDimension,
    deleteDimension,
    saveTemplate,
    deleteTemplate,
    uploadCsvFiles,
    deleteCsvFile,
    refreshCsvFiles
  }
})
