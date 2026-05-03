"""
Fix indentation issues in calculator.py.

The Calculator class has all method bodies at 1-space indent (same as def line).
We need to fix this by properly re-indenting method bodies to be inside the def.

The problem: in the class, everything including method bodies is at 1-space.
Python requires method bodies to be MORE indented than the def line.

Strategy for the Calculator class:
- Lines at 1-space that are `def`/`@staticmethod` = class members (keep at 1-space)
- All other lines at 1-space AFTER a def = method body (shift to 4-space)
- For lines that were already at higher indentation (loops, if-else inside methods),
  keep their relative offset

Wait - actually ALL non-def lines in the class are at 1-space.
For-loop bodies, if-else bodies inside methods are ALSO at 1-space.

This means the for loop body also has no indent relative to the for statement.
BUT we already confirmed the error is only about method bodies, not for loops.
Let me check if for loop bodies inside the class are actually missing indent too.

Looking at calculate_project_total:
Line 577: ' for item in metraj_items:'  (1-space)
Line 578: ' quantity = ...'  (1-space = SAME as for = broken!)

So ALL method bodies AND control structures inside those methods are at 1-space.
The entire class body after each `def` line needs to be re-indented.

The fix: detect which lines are "method body" lines vs "class member" lines,
and re-indent them properly.

Actually the simplest fix: rewrite the entire Calculator class from scratch
with proper 4-space indentation.
"""

file_path = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\core\calculator.py'
out_file = open(r'C:\Users\USER\fix_indent2_result.txt', 'w', encoding='utf-8')

def log(msg):
    print(msg)
    out_file.write(msg + '\n')
    out_file.flush()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Find the Calculator class start
class_start = None
for i, line in enumerate(lines):
    if line.startswith('class Calculator:'):
        class_start = i
        log(f'Found Calculator class at line {i+1}')
        break

# Find the end of the Calculator class (next class or end of file)
class_end = len(lines)
for i in range(class_start + 1, len(lines)):
    line = lines[i]
    # If we hit a non-indented, non-blank line that's not inside the class
    if line and not line[0].isspace() and line.strip():
        class_end = i
        log(f'Calculator class ends at line {i} (before line {i+1}: {line[:50]})')
        break

log(f'Calculator class: lines {class_start+1} to {class_end}')

# Extract class lines
class_lines = lines[class_start:class_end]
log(f'Total class lines: {len(class_lines)}')

# Now fix the class: convert 1-space indent to 4-space for the class,
# and properly re-indent method bodies.
#
# The structure in the file (all at 1-space):
#   class Calculator:      <- 0-space
#    """ docstring """     <- 1-space (class docstring - OK)
#    @staticmethod         <- 1-space (class member - OK)
#    def method():         <- 1-space (class member - OK)
#    """ docstring """     <- 1-space (method body - WRONG, should be 2+)
#    code                  <- 1-space (method body - WRONG, should be 2+)
#    for x in y:           <- 1-space (method body - WRONG, should be 2+)
#    body                  <- 1-space (for body - WRONG, should be 3+)
#
# Since ALL non-blank lines inside the class are at exactly 1-space,
# we can't distinguish method bodies from loop bodies by indent level.
#
# We need to use Python's tokenize or AST to properly re-indent.
# OR: We can write the class completely from scratch.
#
# Let me try using Python's tokenize + rewrite approach:
# Use compile() to detect errors, then fix by examining structure.

# Actually the cleanest approach is to write a new properly-indented version.
# Let me parse each method manually and rewrite.

# Check what's actually happening with the for loop body:
log('\n--- For loop area in calculate_project_total ---')
for i in range(class_start, class_end):
    if 'for item' in lines[i] or ('quantity' in lines[i] and i > class_start+30):
        for j in range(max(0, i-1), min(len(lines), i+5)):
            indent = len(lines[j]) - len(lines[j].lstrip()) if lines[j].strip() else -1
            log(f'  Line {j+1} indent={indent}: {repr(lines[j][:70])}')
        break

out_file.close()
