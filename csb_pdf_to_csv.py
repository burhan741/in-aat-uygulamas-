"""
CŞB Yapım İşleri Birim Fiyat Listesi — PDF → CSV Dönüştürücü
==============================================================
Kullanım:
    python csb_pdf_to_csv.py "C:/path/to/csb_birim_fiyat_2026.pdf"

Çıktı: csb_birim_fiyat_cikti.csv  (CSBPozEngine.csv_iceri_aktar ile yüklenebilir)

Gereksinim:
    pip install pdfplumber
"""

import sys
import re
import csv
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("HATA: pdfplumber kurulu değil.")
    print("Kurmak için: pip install pdfplumber")
    sys.exit(1)


# ── Kategori tespiti ─────────────────────────────────────────────────────────
# CŞB PDF'inde her bölüm bir başlık satırı ile başlar.
# Bu eşleme, başlık metnindeki anahtar kelimelere göre kategori belirler.
_KATEGORI_ESLEMESI = [
    (["TOPRAK", "HAFRİYAT", "KAZI"],                        "Toprak İşleri"),
    (["BETON", "BETONARME"],                                 "Beton İşleri"),
    (["KALIP"],                                              "Kalıp İşleri"),
    (["DEMİR", "DONAT", "ÇELİK ÇUBUK", "HASIR"],           "Demir İşleri"),
    (["DUVAR", "TUĞLA", "GAZBETON", "BRİKET"],              "Duvar İşleri"),
    (["SIVA", "ALÇI", "ŞAP"],                               "Sıva İşleri"),
    (["BOYA", "BADANA"],                                     "Boya İşleri"),
    (["DÖŞEME", "SERAMİK", "FAYANs", "MERMER", "PARKE"],    "Döşeme İşleri"),
    (["ÇATI", "KIREMIT", "OLUKLU"],                         "Çatı İşleri"),
    (["YALITIM", "MANTOLAMA", "MEMBRAN", "İZOLASYON"],      "Yalıtım İşleri"),
    (["ELEKTRİK", "KABLO", "TESİSAT"],                      "Elektrik Tesisatı"),
    (["SU TESİSATI", "BORU", "LAVABO", "KLİMA", "ISI"],     "Sıhhi Tesisat"),
    (["KAPLAMA", "GRANİT"],                                  "Kaplama İşleri"),
    (["AHŞAP", "DOĞRAMA", "KAPI", "PENCERE"],               "Ahşap/Doğrama"),
    (["DEMİR DOĞRAMA", "ALÜMİNYUM"],                        "Metal Doğrama"),
    (["YOL", "ASFALT", "STABILIZE"],                        "Yol İşleri"),
    (["PEYZAJ", "ÇEVRE", "SULAMA"],                         "Peyzaj İşleri"),
    (["YIKIM", "SÖKÜM"],                                     "Yıkım İşleri"),
]

POZ_REGEX = re.compile(
    r"^(\d{2,3}\.\d{3}(?:/\w+)?)\s+(.+?)\s+(m³|m²|m2|m3|kg|ton|adet|m|set|lt|ad)\s+([\d\s.,]+)\s*$",
    re.IGNORECASE
)

# Bazı PDF'lerde birim fiyat sütunu binlik nokta/virgül ile ayrılmış olabilir
def _fiyat_temizle(s: str) -> float:
    """'1.234,56' veya '1,234.56' → float"""
    s = s.strip().replace(" ", "")
    # Türk formatı: binlik=nokta, ondalık=virgül
    if "," in s and "." in s:
        if s.index(".") < s.index(","):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _kategori_bul(metin: str, mevcut: str) -> str:
    metin_ust = metin.upper()
    for anahtar_listesi, kategori in _KATEGORI_ESLEMESI:
        for anahtar in anahtar_listesi:
            if anahtar in metin_ust:
                return kategori
    return mevcut  # değişmez


def _analiz_no_bul(metin: str) -> str:
    m = re.search(r"Y\.(\d+\.\d+)", metin)
    return m.group(0) if m else ""


def pdf_to_csv(pdf_yolu: str, cikti_yolu: str = "csb_birim_fiyat_cikti.csv",
               yil: int = 2026) -> int:
    """
    PDF'den poz verisi çıkar, CSV'ye yaz.
    Döner: yazılan satır sayısı
    """
    satirlar = []
    mevcut_kategori = "Genel"

    print(f"Okunuyor: {pdf_yolu}")

    with pdfplumber.open(pdf_yolu) as pdf:
        toplam = len(pdf.pages)
        print(f"Toplam sayfa: {toplam}")

        for sayfa_no, sayfa in enumerate(pdf.pages, 1):
            if sayfa_no % 50 == 0:
                print(f"  ... {sayfa_no}/{toplam} sayfa işlendi, {len(satirlar)} poz bulundu")

            metin = sayfa.extract_text() or ""

            # Kategori güncelle
            for satir in metin.splitlines():
                satir = satir.strip()
                if len(satir) > 8 and satir.isupper():
                    yeni = _kategori_bul(satir, mevcut_kategori)
                    if yeni != mevcut_kategori:
                        mevcut_kategori = yeni

            # Önce tablo çıkarmayı dene (pdfplumber'ın güçlü yanı)
            tablolar = sayfa.extract_tables()
            if tablolar:
                for tablo in tablolar:
                    for satir in tablo:
                        if not satir or len(satir) < 3:
                            continue
                        poz = str(satir[0] or "").strip()
                        if not re.match(r"^\d{2,3}\.\d{3}", poz):
                            continue
                        aciklama = str(satir[1] or "").strip()
                        birim = str(satir[2] or "").strip().lower()
                        fiyat_ham = str(satir[3] if len(satir) > 3 else "0").strip()
                        fiyat = _fiyat_temizle(fiyat_ham)
                        if fiyat <= 0:
                            continue
                        analiz_no = _analiz_no_bul(aciklama)
                        satirlar.append({
                            "poz_kodu":    poz,
                            "aciklama":    aciklama,
                            "birim":       birim,
                            "birim_fiyat": round(fiyat, 2),
                            "yil":         yil,
                            "kategori":    mevcut_kategori,
                            "analiz_no":   analiz_no,
                        })
            else:
                # Tablo bulunamazsa regex ile satır satır tara
                for satir in metin.splitlines():
                    m = POZ_REGEX.match(satir.strip())
                    if not m:
                        continue
                    poz      = m.group(1).strip()
                    aciklama = m.group(2).strip()
                    birim    = m.group(3).strip().lower()
                    fiyat    = _fiyat_temizle(m.group(4))
                    if fiyat <= 0:
                        continue
                    satirlar.append({
                        "poz_kodu":    poz,
                        "aciklama":    aciklama,
                        "birim":       birim,
                        "birim_fiyat": round(fiyat, 2),
                        "yil":         yil,
                        "kategori":    mevcut_kategori,
                        "analiz_no":   _analiz_no_bul(aciklama),
                    })

    # Tekrarlı poz_kodu varsa en son bulunanı kullan (genellikle daha doğru)
    poz_dict: dict = {}
    for s in satirlar:
        poz_dict[s["poz_kodu"]] = s
    temiz = list(poz_dict.values())

    # CSV yaz
    with open(cikti_yolu, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["poz_kodu", "aciklama", "birim", "birim_fiyat",
                        "yil", "kategori", "analiz_no"]
        )
        writer.writeheader()
        writer.writerows(temiz)

    print(f"\nTamamlandi!")
    print(f"  Bulunan poz: {len(temiz)}")
    print(f"  CSV: {cikti_yolu}")
    print(f"\nSonraki adim:")
    print(f"  Programda Yaklasik Maliyet → 'CSB Listesini Guncelle (CSV)' butonu ile yukleyin.")
    return len(temiz)


# ─────────────────────────────────────────────────────────────────────────────
# Alternatif: Excel → CSV (CŞB Excel versiyonu varsa)
# ─────────────────────────────────────────────────────────────────────────────

def excel_to_csv(excel_yolu: str, cikti_yolu: str = "csb_birim_fiyat_cikti.csv",
                 yil: int = 2026,
                 poz_sutun: int = 0,
                 aciklama_sutun: int = 1,
                 birim_sutun: int = 2,
                 fiyat_sutun: int = 3,
                 baslik_satir: int = 1) -> int:
    """
    CŞB Excel dosyasını CSV'ye dönüştür.
    Sütun numaraları (0'dan başlar) ve başlık satırı özelleştirilebilir.
    """
    try:
        import openpyxl
    except ImportError:
        print("HATA: openpyxl kurulu değil. pip install openpyxl")
        return 0

    wb = openpyxl.load_workbook(excel_yolu, data_only=True)
    satirlar = []
    mevcut_kategori = "Genel"

    for ws_adi in wb.sheetnames:
        ws = wb[ws_adi]
        print(f"Sekme: '{ws_adi}'")

        for satir_no, satir in enumerate(ws.iter_rows(values_only=True), 1):
            if satir_no <= baslik_satir:
                continue
            if not satir or len(satir) <= max(poz_sutun, fiyat_sutun):
                continue

            poz = str(satir[poz_sutun] or "").strip()
            if not re.match(r"^\d{2,3}\.\d{3}", poz):
                # Kategori başlığı olabilir
                metin = " ".join(str(h or "") for h in satir[:4]).strip()
                if metin:
                    mevcut_kategori = _kategori_bul(metin, mevcut_kategori)
                continue

            aciklama = str(satir[aciklama_sutun] or "").strip()
            birim    = str(satir[birim_sutun] or "").strip().lower()
            fiyat_h  = satir[fiyat_sutun]
            try:
                fiyat = float(fiyat_h) if fiyat_h is not None else 0.0
            except (ValueError, TypeError):
                fiyat = _fiyat_temizle(str(fiyat_h or ""))

            if fiyat <= 0:
                continue

            satirlar.append({
                "poz_kodu":    poz,
                "aciklama":    aciklama,
                "birim":       birim,
                "birim_fiyat": round(fiyat, 2),
                "yil":         yil,
                "kategori":    mevcut_kategori,
                "analiz_no":   _analiz_no_bul(aciklama),
            })

    poz_dict = {s["poz_kodu"]: s for s in satirlar}
    temiz = list(poz_dict.values())

    with open(cikti_yolu, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=["poz_kodu", "aciklama", "birim", "birim_fiyat",
                           "yil", "kategori", "analiz_no"]
        )
        writer.writeheader()
        writer.writerows(temiz)

    print(f"Excel donusturme tamamlandi: {len(temiz)} poz → {cikti_yolu}")
    return len(temiz)


# ─────────────────────────────────────────────────────────────────────────────
# Komut satırı
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("Kullanim ornekleri:")
        print("  PDF icin  : python csb_pdf_to_csv.py csb2026.pdf")
        print("  Excel icin: python csb_pdf_to_csv.py csb2026.xlsx")
        sys.exit(0)

    girdi = sys.argv[1]
    cikti = sys.argv[2] if len(sys.argv) > 2 else "csb_birim_fiyat_cikti.csv"
    yil   = int(sys.argv[3]) if len(sys.argv) > 3 else 2026

    ek = Path(girdi).suffix.lower()
    if ek == ".pdf":
        adet = pdf_to_csv(girdi, cikti, yil)
    elif ek in (".xlsx", ".xls"):
        adet = excel_to_csv(girdi, cikti, yil)
    else:
        print(f"Desteklenmeyen dosya türü: {ek}")
        sys.exit(1)

    print(f"\nSonuc: {adet} poz yazildi → {cikti}")
