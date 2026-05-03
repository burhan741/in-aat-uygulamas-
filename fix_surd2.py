"""
surdurulebilirlik_window.py - satır 663+ re-indent
Tüm method body'leri ve nested blokları doğru girintiye taşır.
Strateji: her satırdaki keyword'e göre indent stack'i yönet,
blank satırları nested block sonu sinyali olarak kullan.
"""
import re

filepath = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\surdurulebilirlik_window.py"

with open(filepath, 'rb') as f:
    content = f.read()

sep = b'\r\n' if b'\r\n' in content else b'\n'
raw_lines = content.split(sep)

# Satır 663'ten itibaren tüm satırları al (0-indexed: 662)
FIX_FROM = 663  # 1-indexed

prefix_lines = raw_lines[:FIX_FROM - 1]   # 1..662 → index 0..661
tail_lines   = raw_lines[FIX_FROM - 1:]   # 663.. → index 662..

COMPOUND = {'if', 'elif', 'else', 'for', 'while', 'try', 'except',
            'finally', 'with', 'def', 'class', 'async'}
DEDENT_KW = {'else', 'elif', 'except', 'finally'}

def first_word(s):
    """Satırın ilk keyword'ünü döndür."""
    s = s.strip()
    if not s:
        return ''
    m = re.match(r'^([A-Za-z_]\w*)', s)
    return m.group(1) if m else ''

def ends_with_colon(s):
    """String olmayan, kolon ile biten compound statement mi?"""
    s = s.strip()
    if not s.endswith(':'):
        return False
    # Tek tırnaktan ya da üçlü tırnaktan oluşan satır değilse
    fw = first_word(s)
    return fw in COMPOUND

def fix_indent(lines_bytes):
    """
    lines_bytes: her eleman bir satırın byte içeriği.
    Tüm leading space'i sil, keyword'e göre yeniden girintle.
    """
    indent = 1        # başlangıç: class method seviyesi (1 sp)
    stack  = [1]      # indent stack

    result = []
    prev_blank = False

    for raw in lines_bytes:
        # Decode için utf-8 dene, başarısız olursa latin-1
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('latin-1')

        stripped = text.strip()

        # --- Boş satır ---
        if not stripped:
            result.append(b'')
            # Blank satır: eğer derin bir nested block içindeysek çık
            if len(stack) > 2 and prev_blank is False:
                # Tek bir seviye geri al (derin bloktan çık)
                pass  # gerçek dedent'i sonraki keyword halleder
            prev_blank = True
            continue

        fw = first_word(stripped)

        # --- def → class method seviyesine resetle ---
        if fw == 'def':
            indent = 1
            stack  = [1]
            result.append((' ' * indent + stripped).encode('utf-8'))
            stack.append(indent)
            indent += 1
            prev_blank = False
            continue

        # --- Sınıf seviyesindeki yorum satırları ---
        if stripped.startswith('#') and prev_blank and indent <= 2:
            result.append((' ' + stripped).encode('utf-8'))
            prev_blank = False
            continue

        # --- Dedent keyword'ler (else, elif, except, finally) ---
        if fw in DEDENT_KW:
            if len(stack) > 1:
                stack.pop()
            indent = stack[-1]
            result.append((' ' * indent + stripped).encode('utf-8'))
            if ends_with_colon(stripped):
                stack.append(indent)
                indent += 1
            prev_blank = False
            continue

        # --- Boş satır sonrası potansiyel dedent ---
        # Blank geldi, şimdi non-blank geldi: üst bloktan çıkmış olabiliriz.
        # Heuristik: blank sonrası gelen non-compound satır için
        # mevcut indent stack'ten bir level geri al (en fazla method body'ye kadar).
        if prev_blank and len(stack) > 2 and fw not in COMPOUND:
            # Geri al — ama method body seviyesinin altına düşme
            stack.pop()
            indent = stack[-1]

        # --- Normal satır ---
        result.append((' ' * indent + stripped).encode('utf-8'))

        if ends_with_colon(stripped):
            stack.append(indent)
            indent += 1

        prev_blank = False

    return result

fixed_tail = fix_indent(tail_lines)

new_lines = prefix_lines + fixed_tail
new_content = sep.join(new_lines)

with open(filepath, 'wb') as f:
    f.write(new_content)

print(f"prefix: {len(prefix_lines)} satır")
print(f"tail  : {len(tail_lines)} → {len(fixed_tail)} satır (fix edildi)")
print("Kaydedildi.")
