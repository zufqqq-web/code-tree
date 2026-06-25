import os
from codetree.prioritization import get_file_role

def generate_tree_lines(files_metadata, descriptions):
    """
    Constructs a tree visualization of the project structure with inline file summaries.
    """
    rel_paths = sorted([f['rel_path'].replace('\\', '/') for f in files_metadata])
    
    # Build hierarchical tree dict
    tree = {}
    for path in rel_paths:
        parts = path.split('/')
        curr = tree
        for part in parts:
            curr = curr.setdefault(part, {})
            
    lines = []
    
    def walk(node, path_parts, prefix=""):
        keys = list(node.keys())
        
        # Sort: directories first, then files alphabetically
        def sort_key(k):
            is_child_dir = len(node[k]) > 0
            return (0 if is_child_dir else 1, k.lower())
            
        keys.sort(key=sort_key)
        
        for idx, key in enumerate(keys):
            child_node = node[key]
            is_child_dir = len(child_node) > 0
            is_last_item = (idx == len(keys) - 1)
            
            connector = "└── " if is_last_item else "├── "
            child_path_parts = path_parts + [key]
            rel_path = "/".join(child_path_parts)
            
            # Format Windows paths back to project format if needed
            lookup_path = rel_path.replace('/', os.sep)
            
            desc = ""
            if not is_child_dir:
                desc = descriptions.get(lookup_path, "")
                if desc:
                    desc = f" # {desc}"
                    
            display_name = key + "/" if is_child_dir else key
            tree_part = f"{prefix}{connector}{display_name}"
            
            if desc:
                # Column alignment for comments
                padding = max(45 - len(tree_part), 2)
                lines.append(f"{tree_part}{' ' * padding}{desc}")
            else:
                lines.append(tree_part)
                
            if is_child_dir:
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                walk(child_node, child_path_parts, next_prefix)
                
    lines.append(".")
    walk(tree, [])
    return "\n".join(lines)


def generate_language_bar_chart(lang_stats):
    """
    Generates a visually stunning ASCII bar chart representing programming language distribution.
    """
    if not lang_stats:
        return "No code lines scanned."
        
    max_len_lang = max((len(lang) for lang in lang_stats), default=10)
    lines = []
    for lang, pct in lang_stats.items():
        bar_len = int(pct / 100 * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        lines.append(f"  - **{lang:<{max_len_lang}}** : `{bar}` **{pct}%**")
    return "\n".join(lines)


def generate_report(files_metadata, lang_stats, frameworks, file_categories, scores, summaries, exclude_configs=False):
    """
    Assembles the final Markdown report.
    """
    report = []
    report.append("# Project Structure and Codebase Analysis Report\n")
    
    # 1. Project structure tree
    report.append("## Project Structure Tree")
    report.append("```text")
    # Build standard display descriptions (truncate to 70 chars for inline view)
    inline_descriptions = {}
    for f in files_metadata:
        rel_path = f['rel_path']
        desc = summaries.get(rel_path, "")
        if desc:
            # Inline tree comments should be short
            if len(desc) > 65:
                desc = desc[:62] + "..."
            inline_descriptions[rel_path] = desc
            
    tree_text = generate_tree_lines(files_metadata, inline_descriptions)
    report.append(tree_text)
    report.append("```\n")
    
    # 2. Language Stats
    report.append("## Programming Language Distribution")
    chart = generate_language_bar_chart(lang_stats)
    report.append(chart)
    if exclude_configs:
        report.append("\n*Note: Configurations and manifest files (.json, .yaml, .toml, etc.) are excluded from stats.*")
    report.append("\n")
    
    # 3. Frameworks
    report.append("## Detected Frameworks and Libraries")
    if frameworks:
        for fw, src in sorted(frameworks.items()):
            report.append(f"  - **{fw}** (detected via `{src}`)")
    else:
        report.append("  - *No framework signatures detected.*")
    report.append("\n")
    
    # 4. Detailed File Summaries
    report.append("## Detailed Module Analysis")
    detailed_files = [f for f in files_metadata if file_categories.get(f['rel_path']) == 'detailed']
    
    if detailed_files:
        # Sort by importance score descending
        detailed_files.sort(key=lambda x: scores.get(x['rel_path'], 0), reverse=True)
        
        for f in detailed_files:
            rel_path = f['rel_path']
            score = scores.get(rel_path, 0)
            role = get_file_role(rel_path) or "General Module"
            summary = summaries.get(rel_path, "No detailed analysis available.")
            
            report.append(f"### `{rel_path}`")
            report.append(f"  - **File Size**: {f['lines']} code lines")
            report.append(f"  - **Declarations**: {f['declarations']} classes/functions")
            report.append(f"  - **Role**: `{role}`")
            report.append(f"  - **Importance Score**: {score:.1f}")
            report.append("  - **Purpose**:")
            # Indent LLM summary block
            formatted_summary = "\n".join("    " + line for line in summary.splitlines())
            report.append(formatted_summary)
            report.append("")
    else:
        report.append("  - *No files qualified for detailed analysis.*")
        
    return "\n".join(report)
