import axios from 'axios'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const RENDER_BASE_URL = import.meta.env.VITE_API_BASE_URL 
  ? import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '') 
  : '';

const api = axios.create({
baseURL: API_BASE_URL, 
timeout: 30000,
headers: {
  'Content-Type': 'application/json'
}
})

// Response interceptor for error handling
api.interceptors.response.use(
response => response,
error => {
  const message = error.response?.data?.error || error.message || 'Unknown error'
  console.error('API Error:', message)
  return Promise.reject(error)
}
)

export default {
// Projects
getProjects: () => api.get('/api/projects'),
createProject: (name) => api.post('/api/projects', { name }),
deleteProject: (name) => api.delete(`/api/projects/${name}`),
getProject: (name) => api.get(`/api/projects/${name}`),
exportProject: (name) => `${RENDER_BASE_URL}/projects/${name}/export`, // Zde je /api nutné, pokud backend neodebírá prefix
importProject: (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/projects/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
},

// Settings
getSettings: (project) => api.get(`/api/projects/${project}/settings`),
saveSettings: (project, data) => api.put(`/api/projects/${project}/settings`, data),

// Dimensions
getDimensions: (project) => api.get(`/projects/${project}/dimensions`),
saveDimensions: (project, data) => api.put(`/projects/${project}/dimensions`, data),
saveDimension: (project, name, data) => api.put(`/projects/${project}/dimensions/${name}`, data),
deleteDimension: (project, name) => api.delete(`/projects/${project}/dimensions/${name}`),

// Templates
getTemplates: (project) => api.get(`/projects/${project}/templates`),
saveTemplates: (project, data) => api.put(`/projects/${project}/templates`, data),
saveTemplate: (project, name, data) => api.put(`/projects/${project}/templates/${name}`, data),
deleteTemplate: (project, name) => api.delete(`/projects/${project}/templates/${name}`),

// CSV Files
getCsvFiles: (project) => api.get(`/projects/${project}/csv`),
uploadCsv: (project, files) => {
  const formData = new FormData()
  files.forEach(f => formData.append('files', f))
  return api.post(`/projects/${project}/csv/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
},
deleteCsv: (project, filename) => api.delete(`/projects/${project}/csv/${filename}`),
previewCsv: (project, filename) => api.get(`/projects/${project}/csv/${filename}`),

// URLs
getUrls: (project) => api.get(`/projects/${project}/urls`),

// Generate
previewTemplate: (project, templateName) => api.get(`/projects/${project}/preview/${templateName}`),
generate: (project, templates) => api.post(`/projects/${project}/generate`, { templates }),
downloadUrl: (project, filename) => `${RENDER_BASE_URL}/projects/${project}/download/${filename}`,

// Validate
validate: (project) => api.get(`/projects/${project}/validate`),

// Health
health: () => api.get('/api/health')
}
