import os
import re
import ast
import fnmatch
from codetree.skeleton import tokenize_js

# Default lists of directories and files to ignore
DEFAULT_IGNORED_DIRS = {
    'node_modules', '.git', 'venv', '.venv', '__pycache__', 'dist', 'build',
    '.egg-info', '.pytest_cache', '.idea', '.vscode'
}
DEFAULT_IGNORED_FILES = {
    'package-lock.json', 'poetry.lock', 'yarn.lock', 'pnpm-lock.yaml', 'Cargo.lock',
    'composer.lock', 'go.sum', 'report*.md', '*_test.md', '*_llm.md'
}

class GitignoreRules:
    """
    Parses and matches file paths against gitignore rules for a specific directory.
    """
    def __init__(self, base_dir, lines):
        self.base_dir = os.path.abspath(base_dir)
        self.rules = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            negate = False
            if line.startswith('!'):
                negate = True
                line = line[1:]
            
            is_dir_only = False
            if line.endswith('/'):
                is_dir_only = True
                line = line[:-1]
            
            # Translate glob pattern to regex using a custom translator
            is_root_relative = line.startswith('/')
            if is_root_relative:
                line = line[1:]
            
            parts = line.split('/')
            regex_parts = []
            for part in parts:
                if part == '**':
                    regex_parts.append('.*')
                else:
                    # Translate glob to regex segment by segment
                    seg_regex = []
                    idx = 0
                    part_len = len(part)
                    while idx < part_len:
                        char = part[idx]
                        if char == '*':
                            if idx + 1 < part_len and part[idx+1] == '*':
                                seg_regex.append('.*')
                                idx += 2
                            else:
                                seg_regex.append('[^/]*')
                                idx += 1
                        elif char == '?':
                            seg_regex.append('[^/]')
                            idx += 1
                        elif char in '.+^$()[]{}|\\':
                            seg_regex.append('\\' + char)
                            idx += 1
                        else:
                            seg_regex.append(char)
                            idx += 1
                    regex_parts.append("".join(seg_regex))
            
            pattern = "/".join(regex_parts)
            if is_root_relative:
                pattern = '^' + pattern
            else:
                pattern = '(^|.*/)' + pattern
            
            if is_dir_only:
                pattern = pattern + '(/|$)'
            else:
                pattern = pattern + '(/|$)'
            
            try:
                compiled = re.compile(pattern)
                self.rules.append((compiled, negate))
            except re.error:
                pass

    def matches(self, full_path, is_dir=False):
        # Calculate path relative to the base directory of the gitignore file
        try:
            rel_path = os.path.relpath(full_path, self.base_dir)
        except ValueError:
            return False
            
        rel_path = rel_path.replace('\\', '/')
        if is_dir and not rel_path.endswith('/'):
            rel_path += '/'
            
        matched = False
        for compiled, negate in self.rules:
            if compiled.search(rel_path):
                matched = not negate
        return matched


class GitignoreScanner:
    """
    Collects gitignore files as it walks down directories and checks path ignores.
    """
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        self.rules_by_dir = {}  # dir_path -> GitignoreRules

    def load_gitignore(self, dir_path):
        git_path = os.path.join(dir_path, '.gitignore')
        if os.path.isfile(git_path):
            try:
                with open(git_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                self.rules_by_dir[dir_path] = GitignoreRules(dir_path, lines)
            except Exception:
                pass

    def is_ignored(self, full_path, is_dir=False):
        full_path = os.path.abspath(full_path)
        
        # Check hardcoded defaults first
        basename = os.path.basename(full_path)
        if is_dir:
            if basename in DEFAULT_IGNORED_DIRS:
                return True
        else:
            if any(fnmatch.fnmatch(basename, pattern) for pattern in DEFAULT_IGNORED_FILES):
                return True
            
        # Walk up from full_path to root_dir checking all gitignores along the way
        current = full_path if is_dir else os.path.dirname(full_path)
        while True:
            # Ensure we've loaded this directory's gitignore if we haven't already
            if current not in self.rules_by_dir:
                self.load_gitignore(current)
                
            rules = self.rules_by_dir.get(current)
            if rules and rules.matches(full_path, is_dir):
                return True
                
            if current == self.root_dir:
                break
                
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
            
        return False


def count_lines(content: str) -> int:
    """
    Counts the number of non-empty, non-whitespace-only lines.
    """
    lines = content.splitlines()
    return sum(1 for line in lines if line.strip())


def count_functions_and_classes(file_path: str, content: str) -> int:
    """
    Counts the number of function and class declarations in the file.
    Uses AST for Python, JS/TS parser for JS/TS, and regex patterns for Go/Rust/etc.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.py':
        try:
            tree = ast.parse(content)
            count = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    count += 1
            return count
        except Exception:
            return 0
            
    elif ext in ('.js', '.jsx', '.ts', '.tsx'):
        try:
            from codetree.skeleton import extract_js_skeleton
            # We can run our tokenized parser. Every time we replace a body with '{ ... }'
            # we found a function or method. Every time we see 'class' at balance 0 we found a class.
            tokens = tokenize_js(content)
            count = 0
            
            # Re-use skeleton logic to count functions/methods
            # and count class occurrences.
            CONTROL_FLOW = {'if', 'for', 'while', 'switch', 'catch', 'with', 'foreach'}
            
            # We will walk the tokens and run the same classification
            i = 0
            n = len(tokens)
            while i < n:
                t = tokens[i]
                t_type, t_val = t[0], t[1]
                if t_val == 'class':
                    count += 1
                elif t_type == '{':
                    # Check if it starts a function/method
                    # We inline the skeleton's is_function_body logic
                    paren_balance = 0
                    bracket_balance = 0
                    j = i - 1
                    has_arrow = False
                    has_function_kw = False
                    has_control_flow = False
                    is_method = False
                    
                    while j >= 0:
                        st = tokens[j]
                        st_type, st_val = st[0], st[1]
                        if st_type == 'SPACE' or st_type in ('COMMENT_LINE', 'COMMENT_BLOCK'):
                            j -= 1
                            continue
                        if st_val == ')':
                            paren_balance += 1
                        elif st_val == '(':
                            paren_balance -= 1
                            if paren_balance < 0:
                                break
                            if paren_balance == 0:
                                prev_idx = j - 1
                                while prev_idx >= 0 and (tokens[prev_idx][0] == 'SPACE' or tokens[prev_idx][0] in ('COMMENT_LINE', 'COMMENT_BLOCK')):
                                    prev_idx -= 1
                                if prev_idx >= 0:
                                    before_paren = tokens[prev_idx][1]
                                    if before_paren == '>':
                                        angle_depth = 0
                                        m = prev_idx
                                        while m >= 0:
                                            v = tokens[m][1]
                                            if v == '>':
                                                angle_depth += 1
                                            elif v == '<':
                                                angle_depth -= 1
                                                if angle_depth == 0:
                                                    prev_idx = m - 1
                                                    while prev_idx >= 0 and (tokens[prev_idx][0] == 'SPACE' or tokens[prev_idx][0] in ('COMMENT_LINE', 'COMMENT_BLOCK')):
                                                        prev_idx -= 1
                                                    if prev_idx >= 0:
                                                        before_paren = tokens[prev_idx][1]
                                                    break
                                            m -= 1
                                    
                                    if before_paren in CONTROL_FLOW:
                                        has_control_flow = True
                                    elif before_paren.isidentifier():
                                        is_method = True
                        elif st_val == ']':
                            bracket_balance += 1
                        elif st_val == '[':
                            bracket_balance -= 1
                            if bracket_balance < 0:
                                break
                        elif st_val == '=>' and paren_balance == 0 and bracket_balance == 0:
                            has_arrow = True
                        elif st_val == 'function' and paren_balance == 0 and bracket_balance == 0:
                            has_function_kw = True
                        elif st_val == 'class' and paren_balance == 0 and bracket_balance == 0:
                            break
                        elif st_val in (';', '}', '{') and paren_balance == 0 and bracket_balance == 0:
                            break
                        j -= 1
                    
                    if not has_control_flow and (has_function_kw or has_arrow or is_method):
                        count += 1
                        # skip this block
                        depth = 1
                        i += 1
                        while i < n and depth > 0:
                            sub_t = tokens[i]
                            if sub_t[0] == '{':
                                depth += 1
                            elif sub_t[0] == '}':
                                depth -= 1
                            i += 1
                        continue
                i += 1
            return count
        except Exception:
            return 0
            
    elif ext in ('.go', '.rs'):
        # Go or Rust: count functions/structs/impls/enums using regex
        fn_pattern = re.compile(r'\b(fn|func|struct|impl|enum)\s+[a-zA-Z_]')
        return len(fn_pattern.findall(content))
        
    return 0


def scan_project(root_dir: str):
    """
    Recursively scans the root directory, returning a list of dictionaries with file metadata:
    {
        'path': absolute path,
        'rel_path': path relative to root_dir,
        'ext': file extension,
        'lines': non-empty line count,
        'declarations': functions/classes count,
        'content': full text content
    }
    """
    root_dir = os.path.abspath(root_dir)
    scanner = GitignoreScanner(root_dir)
    files_metadata = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # Filter directories in-place to prevent os.walk from scanning ignored dirs
        i = len(dirnames) - 1
        while i >= 0:
            d_path = os.path.join(dirpath, dirnames[i])
            if scanner.is_ignored(d_path, is_dir=True):
                del dirnames[i]
            i -= 1
            
        for fname in filenames:
            f_path = os.path.join(dirpath, fname)
            if scanner.is_ignored(f_path, is_dir=False):
                continue
                
            try:
                # Read content
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue
                
            rel_path = os.path.relpath(f_path, root_dir)
            lines_count = count_lines(content)
            decls_count = count_functions_and_classes(f_path, content)
            ext = os.path.splitext(fname)[1].lower()
            
            files_metadata.append({
                'path': f_path,
                'rel_path': rel_path,
                'ext': ext,
                'lines': lines_count,
                'declarations': decls_count,
                'content': content
            })
            
    return files_metadata
