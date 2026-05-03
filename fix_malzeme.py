# -*- coding: utf-8 -*-
"""
Malzeme Listesi modülü — satır numarasına dayalı değiştirme.
Dosya tek-space girintileme kullandığından pattern matching yerine
line range replacement kullanılıyor.
"""
import re, sys

# ─────────────────────────────────────────────────────────────
# YARDIMCI: Satır aralığını değiştir
# ─────────────────────────────────────────────────────────────
def replace_lines(lines, start_line, end_line, new_code_str):
    """1-tabanlı satır numarası ile replace."""
    s = start_line - 1   # 0-tabanlı
    e = end_line         # 0-tabanlı exclusive
    # Dosyadaki mevcut satır sonu karakterini koru
    line_ending = b'\r\n' if lines and lines[0].endswith(b'\r\n') else b'\n'
    new_lines = [(l + line_ending) for l in new_code_str.encode('utf-8').splitlines()]
    return lines[:s] + new_lines + lines[e:]

# ─────────────────────────────────────────────────────────────
# 1) material_calculator.py — calculate_materials_for_project
# ─────────────────────────────────────────────────────────────
mat_path = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\core\material_calculator.py"
with open(mat_path, 'rb') as f:
    mat_lines = f.read().splitlines(keepends=True)

# Satır bul
calc_start = calc_end = None
next_def = None
for i, l in enumerate(mat_lines):
    stripped = l.strip()
    if b'def calculate_materials_for_project' in l:
        calc_start = i + 1  # 1-tabanlı
    elif calc_start and stripped.startswith(b'def ') and i > calc_start:
        next_def = i + 1
        break

if calc_start and next_def:
    calc_end = next_def - 1
    print(f"calculate_materials_for_project: satır {calc_start}-{calc_end}")

    # Girintileme: orijinaldeki gibi 1-space
    NEW_MAT_METHOD = """ def calculate_materials_for_project(self, proje_id: int,
                                         fire_orani_override: Optional[float] = None) -> List[Dict[str, Any]]:
  \"\"\"
  Proje için toplam malzeme ihtiyacını hesapla.
  Poz bazlı ve serbest piyasa kalemlerini birlikte işler.
  \"\"\"
  from app.data.malzeme_formulleri import BASIC_MATERIALS
  _fiyat_map = {m['ad']: m['birim_fiyat'] for m in BASIC_MATERIALS}
  _kat_map   = {m['ad']: m.get('kategori', 'Diğer') for m in BASIC_MATERIALS}

  metraj_kalemleri = self.db.get_project_metraj(proje_id)
  if not metraj_kalemleri:
   return []

  all_materials: list = []
  sp_fiyat_tablosu: dict = {}

  for kalem in metraj_kalemleri:
   poz_no = kalem.get('poz_no')
   miktar = kalem.get('miktar', 0)
   if miktar <= 0:
    continue
   if not poz_no:
    fire_orani = fire_orani_override if fire_orani_override is not None else 0.0
    birim_fiyat = float(kalem.get('birim_fiyat', 0) or 0)
    tanim = kalem.get('tanim', '') or 'Bilinmeyen Kalem'
    kategori = kalem.get('kategori', '') or 'Serbest Piyasa'
    miktar_fire = round(miktar * (1.0 + fire_orani), 2)
    sp_fiyat_tablosu[tanim] = birim_fiyat
    all_materials.append([{
     'malzeme_id': None,
     'malzeme_adi': tanim,
     'miktar': miktar_fire,
     'birim': kalem.get('birim', 'adet'),
     'birim_fiyat': birim_fiyat,
     'formul_tipi': 'serbest_piyasa',
     'poz_no': None,
     'poz_tanim': tanim,
     'poz_miktar': miktar,
     'poz_birim': kalem.get('birim', ''),
     'poz_fire_orani': fire_orani,
     'malzeme_kategori': kategori,
    }])
    continue
   poz = self.db.get_poz(poz_no)
   if not poz:
    continue
   poz_id = poz['id']
   fire_orani = fire_orani_override if fire_orani_override is not None else poz.get('fire_orani', 0.05)
   formuller = self.db.get_poz_formulleri(poz_id)
   if not formuller:
    continue
   materials = self.calculator.calculate_materials_for_poz(miktar, formuller, fire_orani)
   for material in materials:
    material['poz_no'] = poz_no
    material['poz_tanim'] = kalem.get('tanim', '')
    material['poz_miktar'] = miktar
    material['poz_birim'] = kalem.get('birim', '')
    material['poz_fire_orani'] = fire_orani
    adi = material.get('malzeme_adi', '')
    material['malzeme_kategori'] = _kat_map.get(adi, 'Diğer')
   all_materials.append(materials)

  aggregated = self.calculator.aggregate_materials(all_materials)

  for m in aggregated:
   adi = m.get('malzeme_adi', '')
   if adi in sp_fiyat_tablosu:
    m['birim_fiyat'] = sp_fiyat_tablosu[adi]
   else:
    m.setdefault('birim_fiyat', _fiyat_map.get(adi, 0.0))
   m.setdefault('malzeme_kategori', _kat_map.get(adi, 'Diğer'))
   m['toplam_maliyet'] = round(m.get('miktar', 0) * m.get('birim_fiyat', 0.0), 2)

  return aggregated
"""
    line_ending = b'\r\n' if mat_lines[0].endswith(b'\r\n') else b'\n'
    new_lines = [(l.encode('utf-8') + line_ending) for l in NEW_MAT_METHOD.splitlines()]
    mat_lines = mat_lines[:calc_start-1] + new_lines + mat_lines[calc_end:]
    with open(mat_path, 'wb') as f:
        f.writelines(mat_lines)
    print("OK [1/5] material_calculator.py güncellendi")
else:
    print(f"HATA [1/5] material_calculator.py — satır bulunamadı (start={calc_start}, next={next_def})")

# ─────────────────────────────────────────────────────────────
# 2+3+4+5) main_window.py değişiklikleri
# ─────────────────────────────────────────────────────────────
mw_path = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py"
with open(mw_path, 'rb') as f:
    mw_lines = f.read().splitlines(keepends=True)

line_ending = b'\r\n' if mw_lines[0].endswith(b'\r\n') else b'\n'

# Fonksiyon sınırlarını bul
func_positions = {}
for i, l in enumerate(mw_lines):
    for name in [b'def create_malzeme_tab', b'def on_fire_mode_changed',
                 b'def calculate_materials(self)', b'def export_materials_excel',
                 b'def export_materials_supplier', b'def on_tab_changed']:
        if name in l:
            func_positions[name] = i + 1  # 1-tabanlı

print("Bulunan fonksiyon satırları:", {k.decode(): v for k, v in func_positions.items()})

# ── 2) create_malzeme_tab (satır 1324 -> on_fire_mode_changed başına) ──
tab_start = func_positions.get(b'def create_malzeme_tab')
tab_end   = func_positions.get(b'def on_fire_mode_changed', 0) - 1
if tab_start and tab_end > tab_start:
    NEW_TAB = """ def create_malzeme_tab(self, add_to_tabs: bool = True) -> None:
  \"\"\"Malzeme Listesi sekmesini oluştur\"\"\"
  tab = QWidget()
  layout = QVBoxLayout(tab)
  layout.setContentsMargins(10, 10, 10, 10)

  control_group = QGroupBox("Hesaplama Ayarları")
  control_layout = QFormLayout()

  self.fire_mode_combo = QComboBox()
  self.fire_mode_combo.addItems([
   "Otomatik (Poz Bazlı - Literatür Değerleri)",
   "Manuel (Tüm Pozlar İçin Aynı)"
  ])
  self.fire_mode_combo.currentIndexChanged.connect(self.on_fire_mode_changed)
  control_layout.addRow("Fire Oranı Modu:", self.fire_mode_combo)

  self.fire_spin = QDoubleSpinBox()
  self.fire_spin.setMinimum(0.0)
  self.fire_spin.setMaximum(50.0)
  self.fire_spin.setValue(5.0)
  self.fire_spin.setSuffix(" %")
  self.fire_spin.setDecimals(2)
  self.fire_spin.setEnabled(False)
  control_layout.addRow("Manuel Fire/Atık Oranı:", self.fire_spin)

  self.fire_info_label = QLabel("ℹ Otomatik mod: Her poz için Literatür/Kitap değerlerine göre fire oranı kullanılır.")
  self.fire_info_label.setWordWrap(True)
  self.fire_info_label.setStyleSheet("color: #666; font-size: 9pt;")
  control_layout.addRow("", self.fire_info_label)

  btn_calculate = QPushButton("Malzemeleri Hesapla")
  btn_calculate.clicked.connect(self.calculate_materials)
  control_layout.addRow("", btn_calculate)

  control_group.setLayout(control_layout)
  layout.addWidget(control_group)

  export_group = QGroupBox("Export İşlemleri")
  export_layout = QHBoxLayout()
  btn_export_excel = QPushButton("Excel'e Aktar")
  btn_export_excel.clicked.connect(self.export_materials_excel)
  export_layout.addWidget(btn_export_excel)
  btn_export_pdf = QPushButton("PDF'e Aktar")
  btn_export_pdf.clicked.connect(self.export_materials_pdf)
  export_layout.addWidget(btn_export_pdf)
  btn_export_supplier = QPushButton("Tedarikçi Formatı")
  btn_export_supplier.clicked.connect(self.export_materials_supplier)
  export_layout.addWidget(btn_export_supplier)
  export_group.setLayout(export_layout)
  layout.addWidget(export_group)

  arama_layout = QHBoxLayout()
  arama_layout.addWidget(QLabel("🔍 Ara:"))
  self.malzeme_search = QLineEdit()
  self.malzeme_search.setPlaceholderText("Malzeme adına göre filtrele...")
  self.malzeme_search.textChanged.connect(self._filter_malzeme_table)
  arama_layout.addWidget(self.malzeme_search)
  arama_layout.addStretch()
  self.malzeme_toplam_label = QLabel("Toplam: —")
  self.malzeme_toplam_label.setStyleSheet("font-weight: bold; color: #00BFFF; padding: 4px;")
  arama_layout.addWidget(self.malzeme_toplam_label)
  layout.addLayout(arama_layout)

  self.material_summary_label = QLabel("Proje seçiniz ve 'Malzemeleri Hesapla' butonuna tıklayınız.")
  self.material_summary_label.setFont(QFont("Arial", 10))
  self.material_summary_label.setWordWrap(True)
  layout.addWidget(self.material_summary_label)

  self.material_table = QTableWidget()
  self.material_table.setColumnCount(6)
  self.material_table.setHorizontalHeaderLabels([
   "Malzeme Adı", "Miktar", "Birim", "Birim Fiyat (₺)", "Toplam (₺)", "Kaynak"
  ])
  self.material_table.setAlternatingRowColors(True)
  self.material_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
  self.material_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
  self.material_table.horizontalHeader().setStretchLastSection(True)
  self.material_table.setColumnWidth(0, 240)
  self.material_table.setColumnWidth(1, 90)
  self.material_table.setColumnWidth(2, 70)
  self.material_table.setColumnWidth(3, 110)
  self.material_table.setColumnWidth(4, 110)
  self.material_table.cellChanged.connect(self._malzeme_birim_fiyat_degisti)
  layout.addWidget(self.material_table)

  self.malzeme_widget = tab
  if add_to_tabs:
   self.tabs.addTab(tab, " Malzeme Listesi")

"""
    new_lines = [(l.encode('utf-8') + line_ending) for l in NEW_TAB.splitlines()]
    mw_lines = mw_lines[:tab_start-1] + new_lines + mw_lines[tab_end:]
    # Pozisyonları güncelle
    offset = len(new_lines) - (tab_end - tab_start + 1)
    for k in list(func_positions.keys()):
        if func_positions[k] > tab_end:
            func_positions[k] += offset
    print(f"OK [2/5] create_malzeme_tab güncellendi ({tab_start}-{tab_end})")
else:
    print(f"HATA [2/5] create_malzeme_tab — ({tab_start}, {tab_end})")

# ── 3) calculate_materials (satır ~1426 -> export_materials_excel başına) ──
calc_start = func_positions.get(b'def calculate_materials(self)')
calc_end   = func_positions.get(b'def export_materials_excel', 0) - 1
if calc_start and calc_end > calc_start:
    NEW_CALC = """ def calculate_materials(self) -> None:
  \"\"\"Proje için malzeme listesini hesapla, kategoriye göre gruplandır ve göster.\"\"\"
  if not self.current_project_id:
   QMessageBox.warning(self, "Uyarı", "Lütfen önce bir proje seçiniz.")
   return
  try:
   fire_mode = self.fire_mode_combo.currentIndex()
   fire_orani_override = (self.fire_spin.value() / 100.0) if fire_mode == 1 else None
   materials = self.material_calculator.calculate_materials_for_project(
    self.current_project_id, fire_orani_override
   )
   self.material_table.blockSignals(True)
   self.material_table.clearContents()
   self.material_table.setRowCount(0)
   if not materials:
    self.material_table.blockSignals(False)
    self.material_summary_label.setText("Bu proje için malzeme formülü bulunamadı.")
    self.malzeme_toplam_label.setText("Toplam: 0.00 ₺")
    return
   from collections import OrderedDict
   grouped: dict = OrderedDict()
   for m in materials:
    cat = m.get('malzeme_kategori') or m.get('formul_tipi', 'Diğer')
    grouped.setdefault(cat, []).append(m)
   toplam_satir = len(materials) + len(grouped)
   self.material_table.setRowCount(toplam_satir)
   CAT_BG  = QColor("#1e3a5f")
   CAT_FG  = QColor("#a8d4ff")
   EDIT_BG = QColor("#16213e")
   row = 0
   genel_toplam = 0.0
   for kategori, items in grouped.items():
    kat_item = QTableWidgetItem(f"  {kategori}  ({len(items)} kalem)")
    kat_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    kat_item.setBackground(CAT_BG)
    kat_item.setForeground(CAT_FG)
    kat_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
    self.material_table.setItem(row, 0, kat_item)
    self.material_table.setSpan(row, 0, 1, 6)
    self.material_table.setRowHeight(row, 22)
    row += 1
    for m in items:
     miktar      = m.get('miktar', 0)
     birim_fiyat = m.get('birim_fiyat', 0.0)
     toplam      = m.get('toplam_maliyet', round(miktar * birim_fiyat, 2))
     genel_toplam += toplam
     ad_item = QTableWidgetItem(m.get('malzeme_adi', ''))
     ad_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
     self.material_table.setItem(row, 0, ad_item)
     mkt_item = QTableWidgetItem(f"{miktar:,.2f}")
     mkt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
     mkt_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
     self.material_table.setItem(row, 1, mkt_item)
     br_item = QTableWidgetItem(m.get('birim', ''))
     br_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
     br_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
     self.material_table.setItem(row, 2, br_item)
     fiyat_item = QTableWidgetItem(f"{birim_fiyat:,.2f}" if birim_fiyat else "")
     fiyat_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
     fiyat_item.setBackground(EDIT_BG)
     fiyat_item.setToolTip("Çift tıklayarak fiyatı düzenleyebilirsiniz")
     self.material_table.setItem(row, 3, fiyat_item)
     top_item = QTableWidgetItem(f"{toplam:,.2f}" if toplam else "")
     top_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
     top_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
     if toplam > 0:
      top_item.setForeground(QColor("#4CAF50"))
     self.material_table.setItem(row, 4, top_item)
     poz_no = m.get('poz_no', '')
     if poz_no:
      kaynak = f"{poz_no} — {m.get('poz_tanim', '')[:25]}"
     elif m.get('formul_tipi') == 'serbest_piyasa':
      kaynak = "Serbest Piyasa"
     else:
      kaynak = m.get('formul_tipi', '')
     kaynak_item = QTableWidgetItem(kaynak)
     kaynak_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
     self.material_table.setItem(row, 5, kaynak_item)
     row += 1
   self.material_table.blockSignals(False)
   self.current_materials = materials
   self.update_proje_ozet()
   fire_bilgi = "Otomatik (poz bazlı)" if fire_mode == 0 else f"Manuel %{fire_orani_override*100:.2f}"
   self.material_summary_label.setText(f"{len(materials)} malzeme çeşidi  |  Fire: {fire_bilgi}")
   self.malzeme_toplam_label.setText(f"Toplam: {genel_toplam:,.2f} ₺")
   self.statusBar().showMessage(f"Malzeme listesi hesaplandı: {len(materials)} çeşit")
  except Exception as e:
   if hasattr(self, 'material_table'):
    self.material_table.blockSignals(False)
   QMessageBox.critical(self, "Hata", f"Malzeme hesaplanırken bir hata oluştu:\\n{str(e)}")
   import traceback; traceback.print_exc()

"""
    new_lines = [(l.encode('utf-8') + line_ending) for l in NEW_CALC.splitlines()]
    mw_lines = mw_lines[:calc_start-1] + new_lines + mw_lines[calc_end:]
    offset = len(new_lines) - (calc_end - calc_start + 1)
    for k in list(func_positions.keys()):
        if func_positions[k] > calc_end:
            func_positions[k] += offset
    print(f"OK [3/5] calculate_materials güncellendi ({calc_start}-{calc_end})")
else:
    print(f"HATA [3/5] calculate_materials — ({calc_start}, {calc_end})")

# ── 4) Yeni metodları export_materials_supplier'ın ARKASINA ekle ──
supplier_start = func_positions.get(b'def export_materials_supplier')
# export_materials_supplier'dan sonraki def'i bul
supplier_end = None
if supplier_start:
    for i in range(supplier_start, len(mw_lines)):
        l = mw_lines[i]
        stripped = l.strip()
        if stripped.startswith(b'def ') and i + 1 > supplier_start:
            supplier_end = i  # bu satır bir önceki fonksiyon biter
            break

if supplier_end:
    # Eklenecek metodlar
    NEW_HELPERS = """
 def _filter_malzeme_table(self, text: str) -> None:
  \"\"\"Arama kutusuna göre malzeme tablosunu filtrele.\"\"\"
  if not hasattr(self, 'material_table'):
   return
  text_lower = text.lower().strip()
  for row in range(self.material_table.rowCount()):
   if not text_lower:
    self.material_table.setRowHidden(row, False)
    continue
   if self.material_table.columnSpan(row, 0) > 1:
    self.material_table.setRowHidden(row, False)
    continue
   item = self.material_table.item(row, 0)
   adi = item.text().lower() if item else ''
   self.material_table.setRowHidden(row, text_lower not in adi)

 def _malzeme_birim_fiyat_degisti(self, row: int, col: int) -> None:
  \"\"\"Birim fiyat (sütun 3) düzenlenince Toplam (sütun 4) otomatik güncelle.\"\"\"
  if col != 3 or not hasattr(self, 'material_table'):
   return
  try:
   miktar_item = self.material_table.item(row, 1)
   fiyat_item  = self.material_table.item(row, 3)
   if not miktar_item or not fiyat_item:
    return
   miktar = float(miktar_item.text().replace(',', ''))
   fiyat_text = fiyat_item.text().replace(',', '').strip()
   fiyat = float(fiyat_text) if fiyat_text else 0.0
   toplam = round(miktar * fiyat, 2)
   self.material_table.blockSignals(True)
   top_item = QTableWidgetItem(f"{toplam:,.2f}")
   top_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
   top_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
   if toplam > 0:
    top_item.setForeground(QColor("#4CAF50"))
   self.material_table.setItem(row, 4, top_item)
   self.material_table.blockSignals(False)
   genel_toplam = 0.0
   for r in range(self.material_table.rowCount()):
    if self.material_table.columnSpan(r, 0) > 1:
     continue
    t = self.material_table.item(r, 4)
    if t:
     try:
      genel_toplam += float(t.text().replace(',', ''))
     except ValueError:
      pass
   if hasattr(self, 'malzeme_toplam_label'):
    self.malzeme_toplam_label.setText(f"Toplam: {genel_toplam:,.2f} ₺")
  except (ValueError, AttributeError):
   if hasattr(self, 'material_table'):
    self.material_table.blockSignals(False)

"""
    new_lines = [(l.encode('utf-8') + line_ending) for l in NEW_HELPERS.splitlines()]
    mw_lines = mw_lines[:supplier_end] + new_lines + mw_lines[supplier_end:]
    offset = len(new_lines)
    for k in list(func_positions.keys()):
        if func_positions[k] >= supplier_end:
            func_positions[k] += offset
    print(f"OK [4/5] _filter + _malzeme_birim_fiyat_degisti eklendi (satır {supplier_end})")
else:
    print(f"HATA [4/5] yeni metodlar — supplier_end={supplier_end}")

# ── 5) Proje seçince otomatik hesaplama ──
# "self.load_project_notes()" satırından önce ekle
# Orijinal satır araması
added5 = False
for i, l in enumerate(mw_lines):
    if b'self.load_project_notes()' in l and b'def ' not in l:
        # Buradan 3 satır önce "if hasattr(self, 'taseron_table'):" var mı kontrol et
        # Güvenli marker: statusBar().showMessage ile "Proje seçildi" satırından önce
        pass

for i, l in enumerate(mw_lines):
    if b"showMessage" in l and b"Proje se" in l and b'def ' not in l:
        # Bu satırdan 1 önceye ekle
        new_line = b" if self._tabs_created.get('malzeme', False) and hasattr(self, 'material_table'):\r\n" if line_ending == b'\r\n' else b" if self._tabs_created.get('malzeme', False) and hasattr(self, 'material_table'):\n"
        new_line2 = b"  self.calculate_materials()\r\n" if line_ending == b'\r\n' else b"  self.calculate_materials()\n"
        mw_lines.insert(i, new_line2)
        mw_lines.insert(i, new_line)
        added5 = True
        print(f"OK [5/5] Otomatik malzeme hesaplama eklendi (satır {i+1})")
        break

if not added5:
    print("HATA [5/5] otomatik hesaplama — marker satır bulunamadı")

# Kaydet
with open(mw_path, 'wb') as f:
    f.writelines(mw_lines)

print("\nTüm değişiklikler kaydedildi.")
