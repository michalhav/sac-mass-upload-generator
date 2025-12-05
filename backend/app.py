#!/usr/bin/env python3
"""
SAC Template Generator - Backend API
Flask REST API for SAC template generation.
"""

import json
import os
import shutil
import logging
import traceback
from functools import wraps
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging(log_dir: str = "logs", level: str = "INFO") -> logging.Logger:
    """Setup logging for API."""
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger("sac_api")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers = []
    
    # File handler
    log_file = os.path.join(log_dir, f"api_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# =============================================================================
# APP SETUP
# =============================================================================

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue frontend

VERCEL_ORIGIN = "https://template-generator-gamma.vercel.app"

CORS(app, resources={r"/*": {"origins": [VERCEL_ORIGIN, "http://localhost:3000"]}})

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

# =============================================================================
# ERROR HANDLING
# =============================================================================

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


def api_handler(f):
    """Decorator for API endpoints with error handling."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            logger.warning(f"API Error: {e.message}")
            return jsonify({'success': False, 'error': e.message, 'details': e.details}), e.status_code
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return jsonify({'success': False, 'error': f'Not found: {e}'}), 404
        except Exception as e:
            logger.exception(f"Unexpected error in {f.__name__}")
            return jsonify({'success': False, 'error': str(e)}), 500
    return decorated


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


# =============================================================================
# UTILITIES
# =============================================================================

def get_project_path(name: str) -> str:
    if not name:
        raise APIError("Project name required", 400)
    safe_name = "".join(c for c in name if c.isalnum() or c in ('_', '-'))
    return os.path.join(PROJECTS_DIR, safe_name)


def ensure_project_dirs(path: str):
    os.makedirs(os.path.join(path, "config"), exist_ok=True)
    os.makedirs(os.path.join(path, "downloads"), exist_ok=True)
    os.makedirs(os.path.join(path, "output"), exist_ok=True)


def load_json(path: str, default: dict = None) -> dict:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default or {}


def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'version': '2.1', 'timestamp': datetime.now().isoformat()})


# -----------------------------------------------------------------------------
# Projects
# -----------------------------------------------------------------------------

@app.route('/api/projects', methods=['GET', 'POST'])
@api_handler
def api_projects():
    if request.method == 'POST':
        name = request.json.get('name', '').strip()
        if not name:
            raise APIError("Project name required", 400)
        if not name.replace('_', '').replace('-', '').isalnum():
            raise APIError("Invalid project name", 400)
        
        path = get_project_path(name)
        if os.path.exists(path):
            raise APIError(f"Project '{name}' already exists", 409)
        
        ensure_project_dirs(path)
        logger.info(f"Created project: {name}")
        return jsonify({'success': True, 'name': name})
    
    projects = [d for d in os.listdir(PROJECTS_DIR) 
                if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    return jsonify({'projects': sorted(projects)})


@app.route('/api/projects/<name>', methods=['GET', 'DELETE'])
@api_handler
def api_project(name):
    path = get_project_path(name)
    
    if request.method == 'DELETE':
        if os.path.exists(path):
            shutil.rmtree(path)
            logger.info(f"Deleted project: {name}")
        return jsonify({'success': True})
    
    # GET - return project overview
    if not os.path.exists(path):
        raise APIError(f"Project '{name}' not found", 404)
    
    settings = load_json(os.path.join(path, 'config', 'project.json'))
    dimensions = load_json(os.path.join(path, 'config', 'dimensions.json'), {'dimensions': []})
    templates = load_json(os.path.join(path, 'config', 'templates.json'), {'templates': []})
    
    downloads_path = os.path.join(path, 'downloads')
    csv_files = []
    if os.path.exists(downloads_path):
        csv_files = [f for f in os.listdir(downloads_path) if f.endswith('.csv')]
    
    return jsonify({
        'name': name,
        'settings': settings,
        'dimensions': dimensions.get('dimensions', []),
        'templates': templates.get('templates', []),
        'csv_files': csv_files
    })


# -----------------------------------------------------------------------------
# Settings
# -----------------------------------------------------------------------------

@app.route('/api/projects/<name>/settings', methods=['GET', 'PUT'])
@api_handler
def api_settings(name):
    path = os.path.join(get_project_path(name), 'config', 'project.json')
    
    if request.method == 'PUT':
        save_json(path, request.json)
        logger.info(f"Updated settings for {name}")
        return jsonify({'success': True})
    
    return jsonify(load_json(path))


# -----------------------------------------------------------------------------
# Dimensions
# -----------------------------------------------------------------------------

@app.route('/api/projects/<name>/dimensions', methods=['GET', 'PUT'])
@api_handler
def api_dimensions(name):
    path = os.path.join(get_project_path(name), 'config', 'dimensions.json')
    
    if request.method == 'PUT':
        save_json(path, request.json)
        logger.info(f"Updated dimensions for {name}")
        return jsonify({'success': True})
    
    return jsonify(load_json(path, {'dimensions': []}))


@app.route('/api/projects/<name>/dimensions/<dim_name>', methods=['PUT', 'DELETE'])
@api_handler
def api_dimension(name, dim_name):
    path = os.path.join(get_project_path(name), 'config', 'dimensions.json')
    data = load_json(path, {'dimensions': []})
    
    if request.method == 'DELETE':
        data['dimensions'] = [d for d in data['dimensions'] if d.get('name') != dim_name]
        save_json(path, data)
        return jsonify({'success': True})
    
    # PUT - update or add
    dim_data = request.json
    existing = next((i for i, d in enumerate(data['dimensions']) if d.get('name') == dim_name), None)
    
    if existing is not None:
        data['dimensions'][existing] = dim_data
    else:
        data['dimensions'].append(dim_data)
    
    save_json(path, data)
    return jsonify({'success': True})


# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------

@app.route('/api/projects/<name>/templates', methods=['GET', 'PUT'])
@api_handler
def api_templates(name):
    path = os.path.join(get_project_path(name), 'config', 'templates.json')
    
    if request.method == 'PUT':
        save_json(path, request.json)
        logger.info(f"Updated templates for {name}")
        return jsonify({'success': True})
    
    return jsonify(load_json(path, {'templates': []}))


@app.route('/api/projects/<name>/templates/<tpl_name>', methods=['PUT', 'DELETE'])
@api_handler
def api_template(name, tpl_name):
    path = os.path.join(get_project_path(name), 'config', 'templates.json')
    data = load_json(path, {'templates': []})
    
    if request.method == 'DELETE':
        data['templates'] = [t for t in data['templates'] if t.get('name') != tpl_name]
        save_json(path, data)
        return jsonify({'success': True})
    
    # PUT
    tpl_data = request.json
    existing = next((i for i, t in enumerate(data['templates']) if t.get('name') == tpl_name), None)
    
    if existing is not None:
        data['templates'][existing] = tpl_data
    else:
        data['templates'].append(tpl_data)
    
    save_json(path, data)
    return jsonify({'success': True})


# -----------------------------------------------------------------------------
# CSV Files
# -----------------------------------------------------------------------------

@app.route('/api/projects/<name>/csv', methods=['GET'])
@api_handler
def api_csv_list(name):
    import pandas as pd
    downloads_path = os.path.join(get_project_path(name), 'downloads')
    os.makedirs(downloads_path, exist_ok=True)
    
    files = []
    for f in os.listdir(downloads_path):
        if f.endswith('.csv'):
            filepath = os.path.join(downloads_path, f)
            try:
                df = pd.read_csv(filepath, dtype=str, nrows=5)
                rows = len(pd.read_csv(filepath, dtype=str))
                files.append({
                    'filename': f,
                    'name': f.replace('MasterWithHierarchy.csv', '').replace('Master.csv', ''),
                    'rows': rows,
                    'columns': len(df.columns)
                })
            except:
                files.append({'filename': f, 'name': f, 'rows': 0, 'columns': 0, 'error': True})
    
    return jsonify({'files': files})


@app.route('/api/projects/<name>/csv/upload', methods=['POST'])
@api_handler
def api_csv_upload(name):
    import re
    downloads_path = os.path.join(get_project_path(name), 'downloads')
    os.makedirs(downloads_path, exist_ok=True)
    
    uploaded = 0
    for f in request.files.getlist('files'):
        if f.filename.endswith('.csv'):
            # Clean filename (remove duplicate suffixes like " (1).csv")
            clean_name = re.sub(r'\s*\(\d+\)\.csv$', '.csv', f.filename)
            f.save(os.path.join(downloads_path, clean_name))
            uploaded += 1
            logger.info(f"Uploaded CSV: {clean_name}")
    
    return jsonify({'success': True, 'uploaded': uploaded})


@app.route('/api/projects/<name>/csv/<filename>', methods=['GET', 'DELETE'])
@api_handler
def api_csv_file(name, filename):
    filepath = os.path.join(get_project_path(name), 'downloads', filename)
    
    if request.method == 'DELETE':
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted CSV: {filename}")
        return jsonify({'success': True})
    
    # GET - preview
    import pandas as pd
    if not os.path.exists(filepath):
        raise APIError(f"File '{filename}' not found", 404)
    
    df = pd.read_csv(filepath, dtype=str)
    return jsonify({
        'filename': filename,
        'headers': list(df.columns),
        'rows': df.head(20).values.tolist(),
        'total_rows': len(df)
    })


# -----------------------------------------------------------------------------
# Generate URLs
# -----------------------------------------------------------------------------

@app.route('/api/projects/<name>/urls', methods=['GET'])
@api_handler
def api_generate_urls(name):
    project_path = get_project_path(name)
    settings = load_json(os.path.join(project_path, 'config', 'project.json'))
    dimensions = load_json(os.path.join(project_path, 'config', 'dimensions.json'), {'dimensions': []})
    
    base_url = settings.get('sac_connection', {}).get('base_url', '')
    model_id = settings.get('sac_connection', {}).get('model_id', '')
    version_model_id = settings.get('sac_connection', {}).get('version_model_id', '')
    
    if not base_url or not model_id:
        raise APIError("SAC connection not configured", 400)
    
    urls = []
    seen = set()
    
    for dim in dimensions.get('dimensions', []):
        sac_name = dim.get('sac_name')
        has_hierarchy = dim.get('has_hierarchy', True)
        
        if not sac_name or sac_name in seen:
            continue
        seen.add(sac_name)
        
        suffix = 'MasterWithHierarchy' if has_hierarchy else 'Master'
        url = f"{base_url}/api/v1/dataexport/providers/sac/{model_id}/{sac_name}{suffix}?$format=text/csv"
        urls.append({'name': sac_name, 'url': url, 'hierarchy': has_hierarchy})
    
    # Add Version
    if version_model_id:
        urls.append({
            'name': 'Version',
            'url': f"{base_url}/api/v1/dataexport/providers/sac/{version_model_id}/VersionMaster?$format=text/csv",
            'hierarchy': False
        })
    
    return jsonify({'urls': urls})


# -----------------------------------------------------------------------------
# Preview & Generate
# -----------------------------------------------------------------------------

@app.route('/api/projects/<name>/preview/<tpl_name>', methods=['GET'])
@api_handler
def api_preview(name, tpl_name):
    project_path = get_project_path(name)
    
    from sac_generator import SACGenerator
    generator = SACGenerator(config_dir=os.path.join(project_path, 'config'))
    generator.downloads_dir = os.path.join(project_path, 'downloads')
    generator.output_dir = os.path.join(project_path, 'output')
    generator.load_date_range()
    
    templates = generator.templates_config.get('templates', [])
    template = next((t for t in templates if t['name'] == tpl_name), None)
    
    if not template:
        raise APIError(f"Template '{tpl_name}' not found", 404)
    
    dims = {d['name']: d for d in generator.dimensions_config.get('dimensions', [])}
    columns = []
    
    for col in template.get('columns', []):
        dim_config = dims.get(col, {})
        # Apply overrides
        if col in template.get('dimension_overrides', {}):
            dim_config = dim_config.copy()
            dim_config['filters'] = {**dim_config.get('filters', {}), **template['dimension_overrides'][col]}
        
        df = generator.load_dimension(dim_config)
        columns.append({
            'name': col,
            'count': len(df),
            'samples': df['ID'].head(5).tolist() if not df.empty else []
        })
    
    colors = generator.project.get('colors', {})
    
    return jsonify({
        'template': tpl_name,
        'columns': columns,
        'date_range': generator.date_range,
        'colors': colors
    })


@app.route('/api/projects/<name>/generate', methods=['POST'])
@api_handler
def api_generate(name):
    project_path = get_project_path(name)
    template_names = request.json.get('templates', [])
    
    if not template_names:
        raise APIError("No templates specified", 400)
    
    from sac_generator import SACGenerator
    generator = SACGenerator(config_dir=os.path.join(project_path, 'config'))
    generator.downloads_dir = os.path.join(project_path, 'downloads')
    generator.output_dir = os.path.join(project_path, 'output')
    os.makedirs(generator.output_dir, exist_ok=True)
    
    results = {'success': [], 'failed': []}
    
    for tpl_name in template_names:
        generator.dimension_data = {}
        generator.load_date_range()
        
        templates = generator.templates_config.get('templates', [])
        template = next((t for t in templates if t['name'] == tpl_name), None)
        
        if not template:
            results['failed'].append({'name': tpl_name, 'error': 'Template not found'})
            continue
        
        try:
            result = generator.create_excel(template)
            if result.success:
                results['success'].append({
                    'name': tpl_name,
                    'file': os.path.basename(result.data['path']),
                    'warnings': result.warnings
                })
            else:
                results['failed'].append({'name': tpl_name, 'error': result.message})
        except Exception as e:
            logger.exception(f"Failed to generate {tpl_name}")
            results['failed'].append({'name': tpl_name, 'error': str(e)})
    
    return jsonify({
        'success': len(results['failed']) == 0,
        'results': results
    })


@app.route('/api/projects/<name>/download/<filename>', methods=['GET'])
@api_handler
def api_download(name, filename):
    output_path = os.path.join(get_project_path(name), 'output', filename)
    if not os.path.exists(output_path):
        raise APIError(f"File '{filename}' not found", 404)
    return send_file(output_path, as_attachment=True)


# -----------------------------------------------------------------------------
# Validate
# -----------------------------------------------------------------------------

@app.route('/api/projects/<name>/validate', methods=['GET'])
@api_handler
def api_validate(name):
    project_path = get_project_path(name)
    errors = []
    warnings = []
    
    settings = load_json(os.path.join(project_path, 'config', 'project.json'))
    dimensions = load_json(os.path.join(project_path, 'config', 'dimensions.json'), {'dimensions': []})
    templates = load_json(os.path.join(project_path, 'config', 'templates.json'), {'templates': []})
    
    # Check settings
    base_url = settings.get('sac_connection', {}).get('base_url', '')
    if not base_url or 'YOUR-TENANT' in base_url:
        warnings.append('SAC Base URL not configured')
    
    model_id = settings.get('sac_connection', {}).get('model_id', '')
    if not model_id or 'YOUR_MODEL_ID' in model_id:
        warnings.append('Model ID not configured')
    
    # Check dimensions
    dim_names = [d['name'] for d in dimensions.get('dimensions', [])]
    if not dim_names:
        errors.append('No dimensions defined')
    
    # Check templates
    if not templates.get('templates'):
        warnings.append('No templates defined')
    
    for tpl in templates.get('templates', []):
        for col in tpl.get('columns', []):
            if col not in dim_names:
                errors.append(f"Template '{tpl['name']}': dimension '{col}' not found")
    
    # Check CSV files
    downloads_path = os.path.join(project_path, 'downloads')
    csv_files = []
    if os.path.exists(downloads_path):
        csv_files = [f for f in os.listdir(downloads_path) if f.endswith('.csv')]
    
    for dim in dimensions.get('dimensions', []):
        sac_name = dim.get('sac_name', '')
        has_hierarchy = dim.get('has_hierarchy', True)
        suffix = 'MasterWithHierarchy' if has_hierarchy else 'Master'
        expected = f"{sac_name}{suffix}.csv"
        
        if expected not in csv_files:
            warnings.append(f"CSV missing: {expected} (for '{dim['name']}')")
    
    return jsonify({
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    })


# -----------------------------------------------------------------------------
# Export/Import
# -----------------------------------------------------------------------------

@app.route('/api/projects/<name>/export', methods=['GET'])
@api_handler
def api_export(name):
    import zipfile
    import tempfile
    
    project_path = get_project_path(name)
    if not os.path.exists(project_path):
        raise APIError(f"Project '{name}' not found", 404)
    
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f'{name}.zip')
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_path)
                zipf.write(file_path, arcname)
    
    return send_file(zip_path, as_attachment=True, download_name=f'{name}.zip')


@app.route('/api/projects/import', methods=['POST'])
@api_handler
def api_import():
    import zipfile
    import tempfile
    
    file = request.files.get('file')
    if not file:
        raise APIError("No file provided", 400)
    
    project_name = file.filename.replace('.zip', '')
    project_path = get_project_path(project_name)
    
    # Handle duplicates
    counter = 1
    while os.path.exists(project_path):
        project_name = f"{file.filename.replace('.zip', '')}_{counter}"
        project_path = get_project_path(project_name)
        counter += 1
    
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, 'import.zip')
    file.save(zip_path)
    
    os.makedirs(project_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(project_path)
    
    ensure_project_dirs(project_path)
    logger.info(f"Imported project: {project_name}")
    
    return jsonify({'success': True, 'name': project_name})


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    print(f"\n{'='*50}")
    print("  SAC Template Generator API v2.1")
    print(f"{'='*50}")
    print(f"\n  API: http://localhost:{args.port}/api")
    print("  Press Ctrl+C to stop\n")
    
    app.run(debug=args.debug, port=args.port)
