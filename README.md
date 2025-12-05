# SAC Template Generator v2.1

Modern web application for generating Excel templates for SAP Analytics Cloud mass uploads.

## Tech Stack

- **Backend:** Python/Flask REST API
- **Frontend:** Vue 3 + Vite + Tailwind CSS + shadcn-vue
- **State:** Pinia

## Quick Start

### Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### Production

```bash
docker-compose up -d
```

## Project Structure

```
sac-generator/
├── backend/
│   ├── app.py              # Flask API
│   ├── sac_generator.py    # Core generation logic
│   ├── requirements.txt
│   └── projects/           # Project data
├── frontend/
│   ├── src/
│   │   ├── components/ui/  # shadcn-vue components
│   │   ├── pages/          # Route pages
│   │   ├── stores/         # Pinia stores
│   │   └── api/            # API client
│   ├── package.json
│   └── vite.config.js
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/projects` | List projects |
| POST | `/api/projects` | Create project |
| DELETE | `/api/projects/:name` | Delete project |
| GET/PUT | `/api/projects/:name/settings` | Project settings |
| GET/PUT | `/api/projects/:name/dimensions` | Dimensions config |
| GET/PUT | `/api/projects/:name/templates` | Templates config |
| GET | `/api/projects/:name/csv` | List CSV files |
| POST | `/api/projects/:name/csv/upload` | Upload CSVs |
| GET | `/api/projects/:name/urls` | Generate SAC URLs |
| GET | `/api/projects/:name/preview/:template` | Preview template |
| POST | `/api/projects/:name/generate` | Generate Excel files |
| GET | `/api/projects/:name/validate` | Validate config |
| GET | `/api/projects/:name/export` | Export project ZIP |
| POST | `/api/projects/import` | Import project ZIP |

## Features

- Multi-project support
- Automatic dimension hierarchy filtering
- Configurable filters (parent, exclude, id_list)
- Excel data validation with dropdowns
- Dark mode support
- Export/import projects
- Real-time template preview

## Configuration

### project.json
```json
{
  "sac_connection": {
    "base_url": "https://tenant.analytics.cloud.sap",
    "model_id": "MODEL_ID",
    "version_model_id": "VERSION_MODEL_ID"
  },
  "version": {
    "version_id": "public.RF_CURRENT"
  },
  "settings": {
    "data_rows": 200
  },
  "colors": {
    "dim_header": "#c6e0b4",
    "date_header": "#bdd7ee",
    "dim_cell": "#e2efda"
  }
}
```

### dimensions.json
```json
{
  "dimensions": [
    {
      "name": "Company Code",
      "sac_name": "COL_Co_Code",
      "has_hierarchy": true,
      "table_name": "tbl_company",
      "filters": {
        "exclude_description": ["DUMMY"],
        "parent_filter": "Parent_ID"
      }
    }
  ]
}
```

### templates.json
```json
{
  "templates": [
    {
      "name": "FTE_Planning",
      "output_file": "FTE_Planning.xlsx",
      "columns": ["Company Code", "Cost Center", "Account"],
      "dimension_overrides": {
        "Account": {
          "id_list": ["ACC1", "ACC2"]
        }
      }
    }
  ]
}
```
