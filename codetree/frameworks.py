import os
import re
import sys
import json

FRAMEWORK_SIGNATURES = {
    'react': 'React',
    'next': 'Next.js',
    'vue': 'Vue.js',
    '@angular/core': 'Angular',
    'express': 'Express.js',
    'tailwindcss': 'Tailwind CSS',
    'fastapi': 'FastAPI',
    'django': 'Django',
    'flask': 'Flask',
    'svelte': 'Svelte',
    'nuxt': 'Nuxt.js',
    'gin-gonic/gin': 'Gin',
    'actix-web': 'Actix Web',
    'spring-boot': 'Spring Boot',
}

# Mapping of marker file names to frameworks
MARKER_FILES = {
    'next.config.js': 'Next.js',
    'next.config.mjs': 'Next.js',
    'next.config.ts': 'Next.js',
    'manage.py': 'Django',
    'tailwind.config.js': 'Tailwind CSS',
    'tailwind.config.ts': 'Tailwind CSS',
    'tailwind.config.cjs': 'Tailwind CSS',
    'vite.config.js': 'Vite',
    'vite.config.ts': 'Vite',
    'vite.config.mjs': 'Vite',
    'svelte.config.js': 'Svelte',
    'nuxt.config.js': 'Nuxt.js',
    'nuxt.config.ts': 'Nuxt.js',
}

def parse_package_json(content):
    deps = set()
    try:
        data = json.loads(content)
        for key in ('dependencies', 'devDependencies', 'peerDependencies'):
            if key in data and isinstance(data[key], dict):
                deps.update(data[key].keys())
    except Exception:
        pass
    return deps

def parse_requirements_txt(content):
    deps = set()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Split on common requirement separators
        match = re.split(r'==|>=|<=|~=|>|<|;', line)
        if match:
            pkg = match[0].strip().lower()
            if pkg:
                deps.add(pkg)
    return deps

def parse_toml_dependencies(content):
    deps = set()
    # Lightweight regex parser for TOML dependencies
    # Matches key = "value" or key = { ... } inside dependency sections
    # or list items inside dependencies = [ ... ]
    
    # 1. Look for lists like dependencies = [ "fastapi", "uvicorn" ]
    list_matches = re.findall(r'(?:dependencies|dev-dependencies)\s*=\s*\[([^\]]*)\]', content)
    for lst in list_matches:
        for item in re.findall(r'["\']([^"\']+)["\']', lst):
            # Split version specs: e.g. "fastapi>=0.68.0"
            match = re.split(r'==|>=|<=|~=|>|<|;', item)
            if match:
                deps.add(match[0].strip().lower())
                
    # 2. Look for table style dependencies e.g. [dependencies] or [tool.poetry.dependencies]
    # We find sections and scan key-value pairs until the next section
    sections = re.split(r'(\n\s*\[[^\]]+\]\s*\n)', content)
    is_dependency_section = False
    for section in sections:
        if section.strip().startswith('[') and section.strip().endswith(']'):
            sec_name = section.strip().lower()
            is_dependency_section = any(k in sec_name for k in ('dependencies', 'dev-dependencies'))
        elif is_dependency_section:
            for line in section.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                match = re.match(r'^([a-zA-Z0-9_\-\.]+)\s*=', line)
                if match:
                    deps.add(match.group(1).strip().lower())
    return deps

def parse_go_mod(content):
    deps = set()
    # Go modules usually look like require github.com/gin-gonic/gin v1.7.0
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        if line.startswith('require'):
            parts = line.split()
            if len(parts) >= 2:
                deps.add(parts[1].lower())
        else:
            # Check lines inside block require ( ... )
            parts = line.split()
            if len(parts) >= 1 and not parts[0].startswith('(') and not parts[0].startswith(')'):
                deps.add(parts[0].lower())
    return deps

def detect_frameworks(files_metadata):
    """
    Scansmanifest/lock files and marker files to discover project frameworks.
    Returns a dictionary of { 'Framework Name': 'Detected from file_name' }
    """
    detected = {}
    
    # 1. Scan manifest files
    for f in files_metadata:
        rel_path = f['rel_path']
        basename = os.path.basename(rel_path)
        content = f['content']
        
        deps = set()
        if basename == 'package.json':
            deps = parse_package_json(content)
        elif basename == 'requirements.txt':
            deps = parse_requirements_txt(content)
        elif basename in ('pyproject.toml', 'Cargo.toml'):
            deps = parse_toml_dependencies(content)
            if basename == 'pyproject.toml':
                print(f"DEBUG: pyproject.toml dependency keys parsed: {sorted(deps)}", file=sys.stderr)
        elif basename == 'go.mod':
            deps = parse_go_mod(content)
            
        for dep in deps:
            for sig, framework in FRAMEWORK_SIGNATURES.items():
                if sig == dep or dep.endswith('/' + sig) or dep.startswith(sig + '@'):
                    detected[framework] = rel_path
                    
    # 2. Scan file markers
    for f in files_metadata:
        rel_path = f['rel_path']
        basename = os.path.basename(rel_path)
        
        if basename in MARKER_FILES:
            framework = MARKER_FILES[basename]
            # Django is confirmed if manage.py is in the root directory (or close to it)
            if framework == 'Django' and os.path.dirname(rel_path) != '':
                continue
            detected[framework] = rel_path
            
    return detected
