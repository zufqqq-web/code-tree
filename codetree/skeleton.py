import ast

def tokenize_js(code):
    """
    Tokenizes JS/TS code, keeping track of strings, comments, and braces.
    Correctly handles template literal interpolations ${...}.
    Yields (token_type, value, start_pos, end_pos)
    """
    i = 0
    n = len(code)
    state_stack = ['NORMAL']  # NORMAL, SQ, DQ, TICK
    tick_braces_stack = []    # Tracks curly brace depth within template literal interpolations
    
    current_token = []
    token_start = 0
    
    def flush(t_type, end_idx):
        nonlocal current_token, token_start
        val = "".join(current_token)
        current_token = []
        start = token_start
        token_start = end_idx
        return (t_type, val, start, end_idx)

    tokens = []
    while i < n:
        char = code[i]
        curr_state = state_stack[-1]
        
        if curr_state == 'NORMAL':
            if char == '/' and i + 1 < n and code[i+1] == '/':
                if current_token:
                    tokens.append(flush('OTHER', i))
                current_token.append('//')
                i += 2
                while i < n and code[i] != '\n':
                    current_token.append(code[i])
                    i += 1
                if i < n:
                    current_token.append('\n')
                    i += 1
                tokens.append(flush('COMMENT_LINE', i))
                token_start = i
                continue
            elif char == '/' and i + 1 < n and code[i+1] == '*':
                if current_token:
                    tokens.append(flush('OTHER', i))
                current_token.append('/*')
                i += 2
                while i < n and not (code[i] == '*' and i + 1 < n and code[i+1] == '/'):
                    current_token.append(code[i])
                    i += 1
                if i < n:
                    current_token.append('*/')
                    i += 2
                tokens.append(flush('COMMENT_BLOCK', i))
                token_start = i
                continue
            elif char == "'":
                if current_token:
                    tokens.append(flush('OTHER', i))
                state_stack.append('SQ')
                current_token.append("'")
                i += 1
                continue
            elif char == '"':
                if current_token:
                    tokens.append(flush('OTHER', i))
                state_stack.append('DQ')
                current_token.append('"')
                i += 1
                continue
            elif char == '`':
                if current_token:
                    tokens.append(flush('OTHER', i))
                state_stack.append('TICK')
                current_token.append('`')
                i += 1
                continue
            elif char in '{}()[]:;,':
                if current_token:
                    tokens.append(flush('OTHER', i))
                
                # Check for brace depth when inside template interpolation
                if char == '{' and tick_braces_stack:
                    tick_braces_stack[-1] += 1
                elif char == '}' and tick_braces_stack:
                    tick_braces_stack[-1] -= 1
                    if tick_braces_stack[-1] == 0:
                        # Exiting ${} interpolation
                        tokens.append(('}', '}', i, i+1))
                        state_stack.pop()  # pop 'NORMAL'
                        tick_braces_stack.pop()
                        token_start = i + 1
                        i += 1
                        continue
                
                tokens.append((char, char, i, i+1))
                token_start = i + 1
                i += 1
                continue
            elif char.isspace():
                if current_token:
                    tokens.append(flush('OTHER', i))
                tokens.append(('SPACE', char, i, i+1))
                token_start = i + 1
                i += 1
                continue
            else:
                current_token.append(char)
                i += 1
                continue
                
        elif curr_state == 'SQ':
            if char == '\\':
                current_token.append(char)
                if i + 1 < n:
                    current_token.append(code[i+1])
                    i += 2
                else:
                    i += 1
                continue
            elif char == "'":
                current_token.append(char)
                tokens.append(flush('STRING', i+1))
                state_stack.pop()
                i += 1
                continue
            else:
                current_token.append(char)
                i += 1
                continue
                
        elif curr_state == 'DQ':
            if char == '\\':
                current_token.append(char)
                if i + 1 < n:
                    current_token.append(code[i+1])
                    i += 2
                else:
                    i += 1
                continue
            elif char == '"':
                current_token.append(char)
                tokens.append(flush('STRING', i+1))
                state_stack.pop()
                i += 1
                continue
            else:
                current_token.append(char)
                i += 1
                continue
                
        elif curr_state == 'TICK':
            if char == '\\':
                current_token.append(char)
                if i + 1 < n:
                    current_token.append(code[i+1])
                    i += 2
                else:
                    i += 1
                continue
            elif char == '$' and i + 1 < n and code[i+1] == '{':
                current_token.append('${')
                tokens.append(flush('STRING', i+2))
                state_stack.append('NORMAL')
                tick_braces_stack.append(1)
                i += 2
                continue
            elif char == '`':
                current_token.append(char)
                tokens.append(flush('STRING', i+1))
                state_stack.pop()
                i += 1
                continue
            else:
                current_token.append(char)
                i += 1
                continue

    if current_token:
        tokens.append(flush('OTHER', n))
    return tokens


def extract_js_skeleton(code: str) -> str:
    """
    Parses JS/TS code and extracts its structure (functions, classes, interfaces)
    while stripping method and function bodies, replacing them with '{ ... }'.
    """
    tokens = tokenize_js(code)
    output = []
    i = 0
    n = len(tokens)
    
    CONTROL_FLOW = {'if', 'for', 'while', 'switch', 'catch', 'with', 'foreach'}
    
    def is_function_body(token_idx):
        paren_balance = 0
        bracket_balance = 0
        
        j = token_idx - 1
        has_arrow = False
        has_function_kw = False
        has_control_flow = False
        is_method = False
        
        while j >= 0:
            t = tokens[j]
            t_type, t_val = t[0], t[1]
            
            if t_type == 'SPACE' or t_type in ('COMMENT_LINE', 'COMMENT_BLOCK'):
                j -= 1
                continue
                
            if t_val == ')':
                paren_balance += 1
            elif t_val == '(':
                paren_balance -= 1
                if paren_balance < 0:
                    return False
                if paren_balance == 0:
                    # Look at token before '('
                    prev_idx = j - 1
                    while prev_idx >= 0 and (tokens[prev_idx][0] == 'SPACE' or tokens[prev_idx][0] in ('COMMENT_LINE', 'COMMENT_BLOCK')):
                        prev_idx -= 1
                    if prev_idx >= 0:
                        before_paren = tokens[prev_idx][1]
                        if before_paren == '>':
                            # Scan back to matching <
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
            elif t_val == ']':
                bracket_balance += 1
            elif t_val == '[':
                bracket_balance -= 1
                if bracket_balance < 0:
                    return False
            elif t_val == '=>' and paren_balance == 0 and bracket_balance == 0:
                has_arrow = True
            elif t_val == 'function' and paren_balance == 0 and bracket_balance == 0:
                has_function_kw = True
            elif t_val == 'class' and paren_balance == 0 and bracket_balance == 0:
                return False
            elif t_val in (';', '}', '{') and paren_balance == 0 and bracket_balance == 0:
                break
                
            j -= 1
            
        if has_control_flow:
            return False
        if has_function_kw or has_arrow or is_method:
            return True
            
        return False

    while i < n:
        t = tokens[i]
        t_type, t_val = t[0], t[1]
        
        if t_type == '{':
            if is_function_body(i):
                output.append('{ ... }')
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
            else:
                output.append(t_val)
                i += 1
        else:
            output.append(t_val)
            i += 1
            
    return "".join(output)


def extract_python_skeleton(code: str) -> str:
    """
    Parses Python code using AST and returns function/class signatures and docstrings.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "# [Syntax Error in Python File]"
        
    lines = []
    
    def format_func_sig(node):
        if hasattr(ast, "unparse"):
            args_str = ast.unparse(node.args)
            prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
            return f"{prefix}def {node.name}({args_str}):"
        else:
            args = []
            for arg in node.args.args:
                args.append(arg.arg)
            if node.args.vararg:
                args.append(f"*{node.args.vararg.arg}")
            if node.args.kwarg:
                args.append(f"**{node.args.kwarg.arg}")
            args_str = ", ".join(args)
            prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
            return f"{prefix}def {node.name}({args_str}):"

    module_doc = ast.get_docstring(tree)
    if module_doc:
        lines.append(f'"""\n{module_doc}\n"""')

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = format_func_sig(node)
            lines.append(sig)
            doc = ast.get_docstring(node)
            if doc:
                lines.append(f'    """\n    {doc}\n    """')
            lines.append("    ...")
            lines.append("")
        elif isinstance(node, ast.ClassDef):
            if hasattr(ast, "unparse"):
                bases = [ast.unparse(b) for b in node.bases]
            else:
                bases = [getattr(b, "id", "") for b in node.bases]
            bases_str = f"({', '.join(bases)})" if bases else ""
            lines.append(f"class {node.name}{bases_str}:")
            class_doc = ast.get_docstring(node)
            if class_doc:
                lines.append(f'    """\n    {class_doc}\n    """')
            
            has_methods = False
            for sub_node in node.body:
                if isinstance(sub_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    has_methods = True
                    sig = format_func_sig(sub_node)
                    indented_sig = "\n".join("    " + l for l in sig.splitlines())
                    lines.append(indented_sig)
                    doc = ast.get_docstring(sub_node)
                    if doc:
                        lines.append(f'        """\n        {doc}\n        """')
                    lines.append("        ...")
                    lines.append("")
            if not has_methods and not class_doc:
                lines.append("    ...")
            lines.append("")
            
    return "\n".join(lines)


def extract_skeleton(file_path: str, content: str) -> str:
    """
    Dispatches skeleton extraction based on file path extension.
    """
    if file_path.endswith('.py'):
        return extract_python_skeleton(content)
    elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
        return extract_js_skeleton(content)
    return ""
