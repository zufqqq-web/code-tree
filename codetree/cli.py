import os
import sys
import argparse

from codetree.scanner import scan_project
from codetree.languages import calculate_language_stats, EXTENSION_MAP
from codetree.frameworks import detect_frameworks
from codetree.prioritization import (
    build_import_graph,
    calculate_importance_scores,
    prioritize_files,
    get_file_role,
    get_cheap_description
)
from codetree.skeleton import extract_skeleton
from codetree.llm_client import LLMClient
from codetree.reporter import generate_report

def main():
    parser = argparse.ArgumentParser(
        description="Smart tree CLI tool with semantic code understanding."
    )
    parser.add_argument(
        "--dir", "-d",
        default=".",
        help="Project directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--output", "-o",
        default="codetree_report.md",
        help="Report output file name (default: codetree_report.md)"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=15.0,
        help="File importance score threshold for detailed analysis (default: 15.0)"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:1234/v1",
        help="OpenAI-compatible API base URL (default: http://localhost:1234/v1)"
    )
    parser.add_argument(
        "--api-key",
        default="lm-studio",
        help="API authorization key (default: lm-studio)"
    )
    parser.add_argument(
        "--model",
        default="local-model",
        help="LLM model name (default: local-model)"
    )
    parser.add_argument(
        "--exclude-configs",
        action="store_true",
        help="Exclude JSON, YAML, TOML, and XML files from language statistics"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Run offline without sending requests to the LLM (heuristic/cheap modes only)"
    )
    
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.dir)
    if not os.path.isdir(root_dir):
        print(f"Error: Directory '{root_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Scanning directory: {root_dir}...", file=sys.stderr)
    files_metadata = scan_project(root_dir)
    
    if not files_metadata:
        print("No files found in the project directory.", file=sys.stderr)
        sys.exit(0)
        
    print(f"Found {len(files_metadata)} source files.", file=sys.stderr)
    
    # Build import graph and calculate importance scores
    print("Building import reference graph...", file=sys.stderr)
    import_graph = build_import_graph(files_metadata)
    scores = calculate_importance_scores(files_metadata, import_graph)
    
    # Classify files
    categories, batch_groups = prioritize_files(files_metadata, scores, args.threshold)
    
    summaries = {}
    
    # 1. Process offline/cheap summaries first
    for f in files_metadata:
        rel_path = f['rel_path']
        cat = categories.get(rel_path)
        role = get_file_role(rel_path)
        
        if cat == 'cheap' or cat == 'ignored':
            summaries[rel_path] = get_cheap_description(
                role,
                os.path.basename(rel_path),
                lines=f['lines'],
                content=f['content']
            )
            
    # 2. Process detailed and batch files
    if args.no_llm:
        print("Running in offline mode (--no-llm). Skipping LLM queries.", file=sys.stderr)
        for f in files_metadata:
            rel_path = f['rel_path']
            cat = categories.get(rel_path)
            if cat in ('detailed', 'batch'):
                role = get_file_role(rel_path)
                score = scores.get(rel_path, 0)
                if score > args.threshold:
                    summaries[rel_path] = f"Файл важен (score {score:.1f}), но детальный анализ недоступен без LLM (запустите без --no-llm)"
                else:
                    summaries[rel_path] = get_cheap_description(
                        role,
                        os.path.basename(rel_path),
                        lines=f['lines'],
                        content=f['content']
                    )
    else:
        llm_client = LLMClient(api_url=args.api_url, api_key=args.api_key, model=args.model)
        
        # Process batch groups
        for group in batch_groups:
            files_to_send = []
            for rel_path in group:
                f_meta = next(f for f in files_metadata if f['rel_path'] == rel_path)
                skeleton = extract_skeleton(f_meta['path'], f_meta['content'])
                ext = f_meta['ext']
                lang = EXTENSION_MAP.get(ext, ext[1:].upper() if ext else 'Other')
                files_to_send.append((rel_path, lang, skeleton))
                
            print(f"Analyzing batch of {len(group)} similar files...", file=sys.stderr)
            batch_results = llm_client.get_batch_summaries(files_to_send)
            
            if batch_results:
                # Successfully received and parsed batch JSON
                for rel_path, desc in batch_results.items():
                    summaries[rel_path] = desc
            else:
                # Fallback: Query individually
                print(f"Batch analysis failed. Falling back to individual queries for group...", file=sys.stderr)
                for rel_path, lang, skeleton in files_to_send:
                    filename = os.path.basename(rel_path)
                    print(f"Querying {filename} individually...", file=sys.stderr)
                    desc = llm_client.get_file_summary(filename, lang, skeleton)
                    if desc:
                        summaries[rel_path] = desc
                    else:
                        # Final cheap fallback
                        folder = os.path.dirname(rel_path)
                        summaries[rel_path] = f"Часть группы похожих компонентов в папке {folder}."
                        
        # Process detailed files
        detailed_files = [f for f in files_metadata if categories.get(f['rel_path']) == 'detailed']
        if detailed_files:
            print(f"Analyzing {len(detailed_files)} important files individually...", file=sys.stderr)
            for f_meta in detailed_files:
                rel_path = f_meta['rel_path']
                skeleton = extract_skeleton(f_meta['path'], f_meta['content'])
                ext = f_meta['ext']
                lang = EXTENSION_MAP.get(ext, ext[1:].upper() if ext else 'Other')
                filename = os.path.basename(rel_path)
                
                print(f"Querying LLM for {filename}...", file=sys.stderr)
                desc = llm_client.get_file_summary(filename, lang, skeleton)
                if desc:
                    summaries[rel_path] = desc
                else:
                    role = get_file_role(rel_path)
                    summaries[rel_path] = get_cheap_description(role, filename)
                    
    # Generate stats and frameworks
    lang_stats = calculate_language_stats(files_metadata, args.exclude_configs)
    frameworks = detect_frameworks(files_metadata)
    
    # Build the report
    report_content = generate_report(
        files_metadata=files_metadata,
        lang_stats=lang_stats,
        frameworks=frameworks,
        file_categories=categories,
        scores=scores,
        summaries=summaries,
        exclude_configs=args.exclude_configs
    )
    
    # Save the report
    output_path = os.path.abspath(args.output)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\nSuccess! Smart tree report generated and saved to: {output_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving report to {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
