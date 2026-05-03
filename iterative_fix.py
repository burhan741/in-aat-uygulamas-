"""
autocad_connector.py kalici indentation duzeltici.
Her py_compile hatasini tek tek bulup duzeltir.
Greedy blok tespit + multiline string koruma.
"""
import py_compile, re, os, shutil

SRC   = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\autocad_connector.py".replace("INS AAT", "\u0130N\u015eAAT")
WORK  = r"E:\INS AAT METRAJ PRO\autocad_connector_work.py".replace("INS AAT", "\u0130N\u015eAAT")
FINAL = SRC  # overwrite in place at the end
OUT   = r"E:\INS AAT METRAJ PRO\iterative_result.txt".replace("INS AAT", "\u0130N\u015eAAT")
INDENT = 4   # 4 spaces per level

shutil.copy2(SRC, WORK)
report = []

def get_syntax_error(path):
    try:
        py_compile.compile(path, doraise=True)
        return None
    except py_compile.PyCompileError as e:
        m = re.search(r'line (\d+)', str(e))
        return int(m.group(1)) if m else None

def in_multiline_str(lines, line_idx):
    """Return True if line_idx is inside a triple-quote string."""
    triple_count = 0
    for i in range(line_idx):
        s = lines[i]
        triple_count += s.count('"""') + s.count("'''")
    return (triple_count % 2) == 1

def leading_spaces(line):
    return len(line) - len(line.lstrip(' '))

def is_block_opener(stripped):
    """True if stripped line ends with : and is a block opener."""
    if not stripped.endswith(':') or stripped.startswith('#'):
        return False
    keywords = ('def ', 'async def ', 'class ', 'if ', 'elif ', 'else:',
                'for ', 'async for ', 'while ', 'try:', 'except', 'finally:',
                'with ', 'async with ', 'else ', '@')
    return any(stripped.startswith(k) for k in keywords) or stripped in ('else:', 'try:', 'finally:')

def is_block_closer(stripped):
    """else/elif/except/finally at same level as opener."""
    return any(stripped.startswith(k) for k in
               ('else:', 'elif ', 'except:', 'except ', 'finally:'))

def find_block_body_range(lines, def_line_idx):
    """
    Given index of a block-opening line (def/if/for/try etc.),
    return (start, end) of the body lines (exclusive end).
    Body = lines from def_line_idx+1 until:
      - a line at SAME or LESS indentation (block closer or sibling)
      - or a dedent back to module level
      - or end of file
    """
    if def_line_idx >= len(lines) - 1:
        return (def_line_idx + 1, def_line_idx + 1)

    opener_indent = leading_spaces(lines[def_line_idx])
    start = def_line_idx + 1
    end = start

    for i in range(start, len(lines)):
        line = lines[i]
        stripped = line.strip()
        if not stripped:  # blank line: include in body
            end = i + 1
            continue
        sp = leading_spaces(line)
        if sp <= opener_indent:
            # This line is at same or less indent = body ended
            break
        end = i + 1

    return (start, end)

def add_indent_to_range(lines, start, end, extra=INDENT):
    """Add `extra` spaces to all non-empty lines in [start, end)."""
    for i in range(start, end):
        if lines[i].strip():  # non-empty
            lines[i] = ' ' * extra + lines[i]

MAX_ITER = 600
prev_err_line = -1
stuck_count = 0

for iteration in range(MAX_ITER):
    err_line = get_syntax_error(WORK)

    if err_line is None:
        report.append(f"[iter {iteration}] SYNTAX OK! Basarili.\n")
        break

    if err_line == prev_err_line:
        stuck_count += 1
        if stuck_count >= 5:
            report.append(f"[iter {iteration}] STUCK at line {err_line} - durdu.\n")
            break
    else:
        stuck_count = 0

    prev_err_line = err_line

    with open(WORK, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Convert to list without trailing newlines for processing
    raw = [l.rstrip('\r\n') for l in lines]

    err_idx = err_line - 1  # 0-based

    # Find the block opener: the line with `:` that triggered the error
    # Usually it's err_idx-1 (the line before the error)
    opener_idx = err_idx - 1
    while opener_idx >= 0:
        s = raw[opener_idx].strip()
        if s and not s.startswith('#'):
            break
        opener_idx -= 1

    if opener_idx < 0:
        report.append(f"[iter {iteration}] L{err_line}: opener bulunamadi, atlandi.\n")
        # Add 4 spaces to err_idx line directly
        raw[err_idx] = ' ' * INDENT + raw[err_idx]
    else:
        # Check if opener is in a multiline string
        opener_line = raw[opener_idx]
        opener_stripped = opener_line.strip()

        if in_multiline_str(raw, opener_idx):
            report.append(f"[iter {iteration}] L{err_line}: opener multiline icinde, err satira space ekle.\n")
            raw[err_idx] = ' ' * INDENT + raw[err_idx]
        else:
            # Find the body range of this opener
            body_start, body_end = find_block_body_range(raw, opener_idx)
            report.append(f"[iter {iteration}] L{err_line}: opener L{opener_idx+1} body=[{body_start+1},{body_end}]\n")

            # Add INDENT spaces to body
            for i in range(body_start, body_end):
                if raw[i].strip():
                    raw[i] = ' ' * INDENT + raw[i]

    # Write back
    with open(WORK, 'w', encoding='utf-8') as f:
        for line in raw:
            f.write(line + '\n')

    if iteration % 50 == 0:
        report.append(f"  [checkpoint {iteration}] devam ediyor...\n")
else:
    report.append(f"MAX_ITER ({MAX_ITER}) doldu.\n")

# Final check
final_err = get_syntax_error(WORK)
if final_err is None:
    report.append("FINAL: Syntax OK!\n")
    # Check indent levels
    with open(WORK, 'r', encoding='utf-8') as f:
        wlines = f.readlines()
    levels = set()
    for l in wlines:
        s = l.lstrip(' ')
        if s.strip():
            levels.add(len(l) - len(s))
    report.append(f"Girinti seviyeleri: {sorted(levels)[:20]}\n")

    # Copy to final destination
    shutil.copy2(WORK, FINAL)
    report.append(f"Dosya guncellendi: {FINAL}\n")
else:
    report.append(f"FINAL: Hata hala var (L{final_err}).\n")

report.append(f"Toplam iterasyon: {iteration+1}\n")

with open(OUT, 'w', encoding='utf-8') as f:
    f.writelines(report)
print("Done")
