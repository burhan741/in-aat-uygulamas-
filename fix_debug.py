"""
İlk 20 iterasyonu izlemek için debug versiyonu.
"""
import re

DEDENT_KW = re.compile(r'^\s*(else|elif|except|finally)\b')
HEADER_KW  = re.compile(r'^\s*(if|elif|for|while|try|except|with|async)\b')


def get_indent(line_b: bytes) -> int:
    s = line_b.decode('utf-8', errors='replace')
    return len(s) - len(s.lstrip())


def count_net_parens(b: bytes) -> int:
    depth, in_sq, in_dq = 0, False, False
    for c in b.decode('utf-8', errors='replace'):
        if c == "'" and not in_dq:
            in_sq = not in_sq
        elif c == '"' and not in_sq:
            in_dq = not in_dq
        elif not in_sq and not in_dq:
            if c in '([{':
                depth += 1
            elif c in ')]}':
                depth -= 1
    return depth


def fix_dedent_syntax(lines, error_lineno):
    idx = error_lineno - 1
    N = get_indent(lines[idx])
    header_idx = -1
    for i in range(idx - 1, -1, -1):
        stripped = lines[i].strip()
        if not stripped:
            continue
        ind = get_indent(lines[i])
        if ind < N:
            break
        if ind == N:
            decoded = lines[i].decode('utf-8', errors='replace')
            if HEADER_KW.match(decoded):
                header_idx = i
                break
    if header_idx < 0:
        lines[idx] = b' ' + lines[idx]
        return
    paren_depth = 0
    changed = []
    for i in range(header_idx + 1, idx):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            continue
        ind = get_indent(line)
        if paren_depth == 0 and ind == N:
            lines[i] = b' ' + lines[i]
            changed.append(i + 1)
        paren_depth += count_net_parens(line)
        if paren_depth < 0:
            paren_depth = 0
    print(f"    fix_dedent: header={header_idx+1}, changed lines={changed}")


def fix_try_block(lines, error_lineno):
    idx = error_lineno - 1
    try_idx = -1
    try_indent = -1
    for i in range(idx - 1, -1, -1):
        stripped = lines[i].strip()
        if not stripped:
            continue
        ind = get_indent(lines[i])
        decoded = lines[i].decode('utf-8', errors='replace').strip()
        if decoded.startswith('try:') or decoded == 'try:':
            try_idx = i
            try_indent = ind
            break
    if try_idx < 0:
        lines[idx] = b' ' + lines[idx]
        return
    body_level = try_indent + 1
    paren_depth = 0
    changed = []
    for i in range(try_idx + 1, idx + 1):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            continue
        ind = get_indent(line)
        if paren_depth == 0 and ind < body_level:
            lines[i] = b' ' + lines[i]
            changed.append(i + 1)
        paren_depth += count_net_parens(line)
        if paren_depth < 0:
            paren_depth = 0
    print(f"    fix_try: try_line={try_idx+1} indent={try_indent}, changed={changed}")


filepath = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py"

with open(filepath, 'rb') as f:
    content = f.read()
sep = b'\r\n' if b'\r\n' in content else b'\n'
lines = list(content.split(sep))

for iteration in range(30):
    src = sep.join(lines)
    try:
        compile(src, filepath, 'exec')
        print(f"OK after {iteration} iterations")
        break
    except IndentationError as e:
        idx = e.lineno - 1
        line_content = lines[idx].decode('utf-8', errors='replace').strip()
        print(f"[{iteration}] IndentationError line {e.lineno}: {e.msg}")
        print(f"    Content: {line_content!r}")
        if 0 <= idx < len(lines):
            lines[idx] = b' ' + lines[idx]
    except SyntaxError as e:
        if not e.lineno:
            print(f"[{iteration}] SyntaxError (no lineno): {e.msg}")
            break
        decoded_line = lines[e.lineno - 1].decode('utf-8', errors='replace') if e.lineno <= len(lines) else ''
        stripped_dl = decoded_line.strip()
        print(f"[{iteration}] SyntaxError line {e.lineno}: {e.msg}")
        print(f"    Content: {stripped_dl!r}")

        if DEDENT_KW.match(decoded_line):
            fix_dedent_syntax(lines, e.lineno)
        elif "except" in e.msg and "finally" in e.msg:
            fix_try_block(lines, e.lineno)
        else:
            print("    => Bilinmeyen hata, duruluyor.")
            break
else:
    print("30 iterasyon tamamlandi, hala hatalar var")
