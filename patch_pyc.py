"""
Pyc header patch: mevcut kaynak dosyasinin mtime+size'ini pyc'ye yazar.
Python, pyc header kaynak ile eslesince kaynagi derlemeden pyc'yi yukler.
"""
import os, struct, glob, sys

src = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\autocad_connector.py"
cache_dir = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\__pycache__"

# Turkce karakter olmayan yol kullan
src = src.replace("INS AAT", "\u0130N\u015eAAT")
cache_dir = cache_dir.replace("INS AAT", "\u0130N\u015eAAT")

pyc_files = glob.glob(os.path.join(cache_dir, "autocad_connector.cpython-*.pyc"))

result_lines = []
result_lines.append(f"Python: {sys.version}\n")
result_lines.append(f"Pyc dosyalari: {pyc_files}\n")

if not pyc_files:
    result_lines.append("HATA: Pyc bulunamadi!\n")
else:
    pyc_path = pyc_files[0]
    src_mtime = os.path.getmtime(src)
    src_size  = os.path.getsize(src)
    result_lines.append(f"Kaynak mtime: {src_mtime}\n")
    result_lines.append(f"Kaynak size:  {src_size}\n")
    result_lines.append(f"Pyc yolu: {pyc_path}\n")

    with open(pyc_path, 'rb') as f:
        magic   = f.read(4)
        flags_b = f.read(4)
        flags   = struct.unpack('<I', flags_b)[0]
        old_mtime = struct.unpack('<I', f.read(4))[0]
        old_size  = struct.unpack('<I', f.read(4))[0]

    result_lines.append(f"Pyc magic:      {magic.hex()}\n")
    result_lines.append(f"Pyc flags:      {flags}\n")
    result_lines.append(f"Pyc eski mtime: {old_mtime}\n")
    result_lines.append(f"Pyc eski size:  {old_size}\n")

    if flags != 0:
        result_lines.append("UYARI: flags!=0 (hash-based). Patch calismayabilir.\n")
    else:
        # Patch: offset 8=mtime, offset 12=source size
        with open(pyc_path, 'r+b') as f:
            f.seek(8)
            f.write(struct.pack('<I', int(src_mtime)))
            f.write(struct.pack('<I', src_size))
        result_lines.append(f"PATCH OK: mtime={int(src_mtime)}, size={src_size}\n")

        # Verify import via pyc
        import importlib.util, importlib.machinery
        try:
            loader = importlib.machinery.SourcelessFileLoader("_ac_test", pyc_path)
            spec   = importlib.util.spec_from_loader("_ac_test", loader)
            mod    = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            result_lines.append("IMPORT BASARILI\n")
        except Exception as e:
            result_lines.append(f"Import hatasi: {e}\n")

out = r"E:\INS AAT METRAJ PRO\patch_result.txt".replace("INS AAT", "\u0130N\u015eAAT")
with open(out, 'w', encoding='utf-8') as f:
    f.writelines(result_lines)
print("Done")
