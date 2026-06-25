EXTENSION_MAP = {
    '.py': 'Python',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.css': 'CSS',
    '.json': 'JSON',
    '.html': 'HTML',
    '.go': 'Go',
    '.rs': 'Rust',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.hpp': 'C/C++ Header',
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
}

CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.toml', '.xml', '.ini', '.cfg'}

def calculate_language_stats(files_metadata, exclude_configs=False):
    """
    Calculates the percentage of code lines used by each programming language.
    Returns a sorted list of tuples: [('Language', percentage), ...]
    """
    lang_lines = {}
    total_lines = 0
    
    for f in files_metadata:
        ext = f['ext']
        
        # Check if configuration/manifest file needs to be excluded
        if exclude_configs and ext in CONFIG_EXTENSIONS:
            continue
            
        lang = EXTENSION_MAP.get(ext)
        if not lang:
            # If not in the map, label as Other or ignore?
            # Standard is mapping known ones. Let's group unrecognized as "Other"
            # but only if they have code lines.
            if ext:
                # E.g. '.md' -> 'Markdown', let's label unrecognized as the extension in uppercase
                lang = ext[1:].upper()
            else:
                lang = 'Other'
                
        lines = f['lines']
        if lines > 0:
            lang_lines[lang] = lang_lines.get(lang, 0) + lines
            total_lines += lines
            
    if total_lines == 0:
        return {}
        
    stats = {}
    for lang, lines in lang_lines.items():
        # Calculate percentage rounded to 1 decimal place
        percentage = round((lines / total_lines) * 100, 1)
        stats[lang] = percentage
        
    # Sort by percentage descending
    sorted_stats = dict(sorted(stats.items(), key=lambda item: item[1], reverse=True))
    return sorted_stats
