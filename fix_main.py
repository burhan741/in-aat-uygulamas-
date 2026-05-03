"""
main_window.py + surdurulebilirlik_window.py tam re-indent.
• Type-aware stack: else/elif -> if/for/while, except/finally -> try
• Paren-depth tracking: çok-satırlı def/call içinde satırları continuation olarak işler
• Çok-satırlı def kapanışı ') -> ...:'  stack'e push eder
"""
import re

COMPOUND_KW    = frozenset({'if','elif','else','for','while','try','except',
                             'finally','with','async','class','def'})
ELSE_MATCHES   = frozenset({'if','for','while','elif','else','async'})
EXCEPT_MATCHES = frozenset({'try','except'})


def first_word(s):
    m = re.match(r'([A-Za-z_]\w*)', s.lstrip())
    return m.group(1) if m else ''


def count_structural_parens(s):
    """String literalleri saymazdan önce net açık-kapama paren sayısı."""
    depth = 0
    in_sq = in_dq = False
    for c in s:
        if c == "'" and not in_dq: in_sq = not in_sq
        elif c == '"' and not in_sq: in_dq = not in_dq
        elif not in_sq and not in_dq:
            if c in '([{': depth += 1
            elif c in ')]}': depth -= 1
    return depth


def is_compound(s):
    st = s.strip()
    if not st.endswith(':'):
        return False
    fw = first_word(st)
    return fw in COMPOUND_KW or st.startswith(')')   # ')' -> multiline def/call kapanışı


def reindent(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read()

    sep   = b'\r\n' if b'\r\n' in raw else b'\n'
    lines = raw.split(sep)

    # Stack: [(emit_level, type_kw)]
    stack       = []
    class_depth = -1
    paren_depth = 0        # açık parantez derinliği (çok-satırlı ifade takibi)
    pending_def_level = None   # çok-satırlı def için bekleyen seviye

    def cur_indent():
        return (stack[-1][0] + 1) if stack else 0

    result = []

    for raw_line in lines:
        try:
            text = raw_line.decode('utf-8')
        except UnicodeDecodeError:
            text = raw_line.decode('latin-1')

        stripped = text.strip()

        # ── boş satır ──────────────────────────────────────────────────────
        if not stripped:
            result.append(b'')
            continue

        # ── PAREN içi süreklilik satırı (çok-satırlı ifade) ───────────────
        if paren_depth > 0:
            # Çok-satırlı def/call içindeyiz; bu satırı continuation olarak işle
            # Girinti: def seviyesiyle aynı (pending_def_level) veya cur_indent
            indent = pending_def_level if pending_def_level is not None else cur_indent()
            result.append((' ' * indent + stripped).encode('utf-8'))
            paren_depth += count_structural_parens(stripped)
            # Eğer bu satır çok-satırlı def'i kapattıysa (' -> None:' gibi)
            if paren_depth <= 0:
                paren_depth = 0
                if stripped.rstrip().endswith(':') and pending_def_level is not None:
                    # Def tamamlandı, stack'e ekle
                    stack.append((pending_def_level, 'def'))
                    pending_def_level = None
                else:
                    pending_def_level = None
            continue

        fw = first_word(stripped)

        # ── class ──────────────────────────────────────────────────────────
        if fw == 'class':
            stack.clear()
            class_depth = 0
            result.append(stripped.encode('utf-8'))
            if is_compound(stripped):
                stack.append((0, 'class'))
            paren_depth += count_structural_parens(stripped)
            continue

        # ── def ────────────────────────────────────────────────────────────
        if fw == 'def':
            while stack and stack[-1][1] != 'class':
                stack.pop()
            level = (class_depth + 1) if class_depth >= 0 else 0
            result.append((' ' * level + stripped).encode('utf-8'))
            net = count_structural_parens(stripped)
            if net > 0:
                # Çok-satırlı def: kapanışı bekle
                paren_depth       = net
                pending_def_level = level
            elif stripped.rstrip().endswith(':'):
                # Tek satırlı def
                stack.append((level, 'def'))
            continue

        # ── else / elif ────────────────────────────────────────────────────
        if fw in ('else', 'elif'):
            while stack and stack[-1][1] not in ELSE_MATCHES \
                  and stack[-1][1] not in ('def', 'class'):
                stack.pop()
            if stack and stack[-1][1] in ELSE_MATCHES:
                level = stack[-1][0]
                stack.pop()
            else:
                level = max(cur_indent() - 1, 0)
            result.append((' ' * level + stripped).encode('utf-8'))
            if stripped.rstrip().endswith(':'):
                stack.append((level, fw))
            continue

        # ── except / finally ───────────────────────────────────────────────
        if fw in ('except', 'finally'):
            while stack and stack[-1][1] not in EXCEPT_MATCHES \
                  and stack[-1][1] not in ('def', 'class'):
                stack.pop()
            if stack and stack[-1][1] in EXCEPT_MATCHES:
                level = stack[-1][0]
                stack.pop()
            else:
                level = max(cur_indent() - 1, 0)
            result.append((' ' * level + stripped).encode('utf-8'))
            if stripped.rstrip().endswith(':'):
                stack.append((level, fw))
            continue

        # ── normal satır ───────────────────────────────────────────────────
        level = cur_indent()
        result.append((' ' * level + stripped).encode('utf-8'))
        if is_compound(stripped) and fw in COMPOUND_KW:
            stack.append((level, fw))
        paren_depth += count_structural_parens(stripped)
        if paren_depth < 0:
            paren_depth = 0

    new_content = sep.join(result)
    with open(filepath, 'wb') as f:
        f.write(new_content)
    print(f"OK {filepath}")


if __name__ == '__main__':
    import py_compile

    targets = [
        r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py",
        r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\surdurulebilirlik_window.py",
    ]

    for fp in targets:
        print(f"\nIslem: {fp}")
        reindent(fp)
        try:
            py_compile.compile(fp, doraise=True)
            print("  Syntax OK")
        except py_compile.PyCompileError as e:
            print(f"  Syntax HATA: {e}")
