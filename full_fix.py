"""
autocad_connector.py tam indentation duzeltici.
Keyword tabanli state-machine: her blok acici 4 space arttirir.
Multi-line string iclerini dokunmadan birakir.
"""
import os, shutil, py_compile, re

SRC   = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\autocad_connector.py".replace("INS AAT", "\u0130N\u015eAAT")
WORK  = r"E:\INS AAT METRAJ PRO\autocad_connector_fullfix.py".replace("INS AAT", "\u0130N\u015eAAT")
OUT   = r"E:\INS AAT METRAJ PRO\fullfix_result.txt".replace("INS AAT", "\u0130N\u015eAAT")

UNIT = 4   # 4 spaces per indent level

OPENERS  = ('def ', 'async def ', 'class ', 'if ', 'elif ', 'else:',
            'for ', 'async for ', 'while ', 'try:', 'except', 'finally:',
            'with ', 'async with ')
CLOSERS  = ('else:', 'elif ', 'except:', 'except ', 'finally:')
METHOD_LEVEL_RESET = ('def ', 'async def ', '@')   # signals: back to class body

def is_opener(s):
    if not s.endswith(':') or s.startswith('#'):
        return False
    return any(s.startswith(kw) for kw in OPENERS) or s in ('else:', 'try:', 'finally:')

def is_closer(s):
    return any(s.startswith(kw) for kw in CLOSERS)

def is_method_reset(s):
    return any(s.startswith(kw) for kw in METHOD_LEVEL_RESET)

def fix_source(source_text):
    lines = source_text.split('\n')
    result = []

    # State
    indent_stack   = [0]           # stack of indent levels (in spaces)
    context_stack  = ['module']    # 'module', 'class_body', 'method_body', 'inner_block'
    in_class       = False
    class_level    = 0
    in_triple      = False
    triple_char    = None

    # Track class body indent (def statements go here)
    class_body_indent = UNIT   # defs are at 1 * UNIT = 4 spaces

    for raw_line in lines:
        s = raw_line.strip()

        # ── Empty line ─────────────────────────────────────────────────────
        if not s:
            result.append('')
            continue

        # ── Inside a multi-line string: emit raw, check for end ────────────
        if in_triple:
            result.append(raw_line)
            # Check if this line ENDS the triple quote
            # (count occurrences of the quote char, odd = still open)
            temp = s.replace('\\' + triple_char[0], '')   # skip escaped
            count_here = temp.count(triple_char)
            if count_here % 2 == 1:   # odd = closes the string
                in_triple = False
                triple_char = None
            continue

        # ── Check if this line STARTS a multi-line string ──────────────────
        # A line starts a multiline string if it has an ODD number of triple-quotes
        # AND the first occurrence is an opener (not inside a regular string).
        for q in ('"""', "'''"):
            cnt = s.count(q)
            if cnt % 2 == 1:  # odd = opens a multiline
                in_triple = True
                triple_char = q
                break

        # ── Determine indent level ──────────────────────────────────────────
        current = indent_stack[-1]

        # Block closer (else/elif/except/finally): pop one level FIRST
        if is_closer(s):
            if len(indent_stack) > 1:
                indent_stack.pop()
            current = indent_stack[-1]
            ctx = context_stack[-1] if context_stack else 'inner_block'
        # Method-level reset: def / async def / @decorator
        elif in_class and is_method_reset(s):
            # Pop back to class_body level
            while len(indent_stack) > 1 and indent_stack[-1] > class_body_indent:
                indent_stack.pop()
            # Decorators: stay at class body level (indent stays)
            # def: class body level, will open method body after
            current = class_body_indent
        else:
            current = indent_stack[-1]

        # ── Detect entering a class ─────────────────────────────────────────
        if s.startswith('class ') and current == 0:
            in_class = True
            class_body_indent = UNIT

        # ── Output the line ────────────────────────────────────────────────
        result.append(' ' * current + s)

        # ── If this opens a block, push new level ─────────────────────────
        if in_triple:
            pass  # don't push for multiline string openers
        elif is_opener(s):
            # Special: class body after class definition = class_body_indent
            if s.startswith('class ') and current == 0:
                indent_stack.append(class_body_indent)
            else:
                indent_stack.append(current + UNIT)

    return '\n'.join(result)


# ── Read source ────────────────────────────────────────────────────────────────
with open(SRC, 'r', encoding='utf-8') as f:
    source = f.read()

fixed = fix_source(source)

with open(WORK, 'w', encoding='utf-8') as f:
    f.write(fixed)

report = [f"Yazildi: {WORK}\n"]

# ── Verify syntax ──────────────────────────────────────────────────────────────
try:
    py_compile.compile(WORK, doraise=True)
    report.append("SYNTAX CHECK: OK!\n")
    # Get indent levels
    with open(WORK, 'r', encoding='utf-8') as f:
        wlines = f.readlines()
    levels = set()
    for l in wlines:
        sp = len(l) - len(l.lstrip(' '))
        if l.strip():
            levels.add(sp)
    report.append(f"Girinti seviyeleri: {sorted(levels)[:20]}\n")
    report.append(f"Toplam satir: {len(wlines)}\n")

    # Copy to final
    shutil.copy2(WORK, SRC)
    report.append(f"FINAL: {SRC} guncellendi.\n")

except py_compile.PyCompileError as e:
    report.append(f"SYNTAX ERROR: {e}\n")
    err_str = str(e)
    m = re.search(r'line (\d+)', err_str)
    if m:
        err_line = int(m.group(1))
        with open(WORK, 'r', encoding='utf-8') as f:
            wlines = f.readlines()
        report.append(f"Hata L{err_line} cevresi:\n")
        for li in range(max(0, err_line-4), min(len(wlines), err_line+3)):
            sp = len(wlines[li]) - len(wlines[li].lstrip())
            report.append(f"  L{li+1:4d} sp={sp}: {wlines[li].rstrip()[:80]}\n")

with open(OUT, 'w', encoding='utf-8') as f:
    f.writelines(report)
print("Done")
