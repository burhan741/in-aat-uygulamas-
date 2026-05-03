# -*- coding: utf-8 -*-
"""
Rakip Analizi Word Belgesi Oluşturucu
AMP / OSKA / COM Metraj vs Quantix Pro
"""
import os
import sys

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
CIKTI_DOSYA = os.path.join(DESKTOP, "Rakip_Analizi_AMP_OSKA_COM_vs_Quantix.docx")

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

def set_hucre_renk(hucre, hex_renk):
    tc = hucre._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_renk)
    tcPr.append(shd)

def baslik_ekle(doc, metin, seviye=1):
    if seviye == 1:
        p = doc.add_heading(metin, level=1)
        p.runs[0].font.color.rgb = RGBColor(0x1F, 0x35, 0x64)
    elif seviye == 2:
        p = doc.add_heading(metin, level=2)
        p.runs[0].font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
    else:
        p = doc.add_heading(metin, level=3)

def tablo_olustur(doc, basliklar, satirlar, baslik_renk="1F3564"):
    tablo = doc.add_table(rows=1, cols=len(basliklar))
    tablo.style = 'Table Grid'
    tablo.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Başlık satırı
    baslik_satiri = tablo.rows[0].cells
    for i, baslik in enumerate(basliklar):
        baslik_satiri[i].text = baslik
        set_hucre_renk(baslik_satiri[i], baslik_renk)
        p = baslik_satiri[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)

    # Veri satırları
    for idx, satir in enumerate(satirlar):
        row = tablo.add_row().cells
        renk = "D9E1F2" if idx % 2 == 0 else "FFFFFF"
        for i, deger in enumerate(satir):
            row[i].text = deger
            set_hucre_renk(row[i], renk)
            p = row[i].paragraphs[0]
            run = p.runs[0]
            run.font.size = Pt(9)

    return tablo

def belge_olustur():
    doc = Document()

    # Sayfa ayarları
    section = doc.sections[0]
    section.page_width = Cm(29.7)
    section.page_height = Cm(21.0)
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)

    # ================================================================
    # KAPAK
    # ================================================================
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("RAKIP YAZILIM ANALİZİ")
    run.bold = True
    run.font.size = Pt(24)
    run.font.color.rgb = RGBColor(0x1F, 0x35, 0x64)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("AMP Yazılım  |  OSKA Yazılım  |  COM Metraj (CB Yazılım)")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("vs")
    run.bold = True
    run.font.size = Pt(16)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Quantix Pro (İnşaat Metraj Pro)")
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Hazırlayan: Claude AI Analiz | Nisan 2026")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    doc.add_page_break()

    # ================================================================
    # 1. AMP YAZILIM
    # ================================================================
    baslik_ekle(doc, "1. AMP YAZILIM", 1)

    p = doc.add_paragraph()
    run = p.add_run("Şirket Profili")
    run.bold = True
    run.font.size = Pt(11)
    doc.add_paragraph("• Kuruluş: 1993 | İstanbul | 2 inşaat mühendisi tarafından kuruldu")
    doc.add_paragraph("• 32+ yıl sektör deneyimi | 10.000+ aktif kullanıcı")
    doc.add_paragraph("• Veritabanı: 140.000+ poz (birim fiyat ve analiz)")
    doc.add_paragraph("• Referanslar: Sağlık Bakanlığı, Çevre ve Şehircilik Bakanlığı, Türk Silahlı Kuvvetleri")
    doc.add_paragraph("• Web: www.amp.com.tr | Tel: 0850 255 60 60")
    doc.add_paragraph()

    baslik_ekle(doc, "1.1 Ana Ürünler ve Özellikler", 2)

    baslik_ekle(doc, "A) Kurumsal Hakediş ve Yaklaşık Maliyet Programı", 3)
    ozellikler = [
        ("Yaklaşık Maliyet", "Resmi kamu yaklaşık maliyet hesabı, 4734 sayılı Kanun uyumlu"),
        ("Hakediş İşlemleri", "3 sözleşme tipi: Turnkey sabit fiyat, birim fiyat ihale, hibrit projeler"),
        ("Fiyat Farkı", "Katsayı otomatik hesabı, konum önerme"),
        ("Çoklu Kullanıcı", "1'den 1.000'e kadar eşzamanlı kullanıcı desteği"),
        ("Departman Kontrolü", "İnşaat, Elektrik, Mekanik departman bazlı erişim"),
        ("Entegrasyon", "Active Directory, LDAP, Microsoft SQL Server"),
        ("Çıktılar", "Word, Excel, PDF formatlarında resmi belgeler"),
    ]
    tablo_olustur(doc, ["Özellik", "Açıklama"], ozellikler)
    doc.add_paragraph()

    baslik_ekle(doc, "B) Kolay Metraj Yazılımı", 3)
    ozellikler2 = [
        ("Dosya Desteği", "AutoCAD DWG, PDF ve resim dosyalarından metraj"),
        ("Fare ile Metraj", "Mouse tıklaması ile uzunluk, alan, hacim otomatik hesabı"),
        ("Donatı Kütüphanesi", "150+ hazır donatı şekli"),
        ("Proje Karşılaştırma", "İki proje arasındaki değişiklikleri gösterir"),
        ("Bağımsız Kullanım", "CAD programı gerektirmez, tek başına çalışır"),
        ("Entegrasyon", "AMP Hakediş modülü ile birlikte kullanılabilir"),
    ]
    tablo_olustur(doc, ["Özellik", "Açıklama"], ozellikler2)
    doc.add_paragraph()

    baslik_ekle(doc, "C) Kolay Metraj Donatı Modülü", 3)
    doc.add_paragraph("• DWG projelerinden otomatik demir metrajı çıkarır")
    doc.add_paragraph("• TS500 ve Deprem Yönetmeliği uyumlu")
    doc.add_paragraph("• Kesim listesi ve sipariş formları oluşturur")
    doc.add_paragraph()

    baslik_ekle(doc, "D) Diğer Modüller", 3)
    moduller = [
        ("AMP Planner", "İş programı (Gantt) modülü — ayrı ücretli"),
        ("Birim Fiyat Otomasyonu", "Birim fiyat güncelleme ve analiz"),
        ("Hizmet Hakediş", "Temizlik, güvenlik, yemek hizmeti ödemeleri"),
        ("Piyasa Fiyat Araştırması", "Piyasa fiyatı karşılaştırma"),
        ("Sözleşme Yönetimi", "Sözleşme takip ve yönetim"),
        ("Muayene ve Kabul", "İş kabulü işlemleri"),
        ("AMP Akademi", "Eğitim platformu (www.ampakademi.com)"),
    ]
    tablo_olustur(doc, ["Modül", "Açıklama"], moduller)
    doc.add_paragraph()

    baslik_ekle(doc, "1.2 Fiyatlandırma", 2)
    fiyatlar = [
        ("Kurumsal Hakediş — Kalıcı Lisans", "132.500 ₺"),
        ("Kurumsal Hakediş — Yıllık Kiralama", "89.775 ₺/yıl"),
        ("Kurumsal Hakediş — Bulut (5GB)", "106.100 ₺/yıl"),
        ("Genel ürün yelpazesi", "36.445 ₺ — 2.700.000 ₺"),
        ("Eğitim (kişi başı)", "2.000 ₺ — 10.000 ₺"),
        ("Seminerler", "750 ₺ — 9.500 ₺"),
    ]
    tablo_olustur(doc, ["Ürün / Hizmet", "Fiyat"], fiyatlar, "C00000")
    doc.add_paragraph()

    doc.add_page_break()

    # ================================================================
    # 2. OSKA YAZILIM
    # ================================================================
    baslik_ekle(doc, "2. OSKA YAZILIM", 1)

    p = doc.add_paragraph()
    run = p.add_run("Şirket Profili")
    run.bold = True
    run.font.size = Pt(11)
    doc.add_paragraph("• Kuruluş: 1990 | 35+ yıl sektör deneyimi")
    doc.add_paragraph("• Odak: Teklif dosyası, ihale düzenleme, maliyet hesabı, hakediş, kesin hesap")
    doc.add_paragraph("• Referanslar: DSİ, Vakıflar Genel Müdürlüğü, Belediyeler, Üniversiteler")
    doc.add_paragraph("• Web: www.oska.com.tr")
    doc.add_paragraph()

    baslik_ekle(doc, "2.1 Ana Ürünler ve Özellikler", 2)

    baslik_ekle(doc, "A) HakedişPlus+", 3)
    hp_ozellikler = [
        ("Mevzuat Uyumu", "4734 Kanununa tam uyumlu, mevzuat değişikliklerine anlık güncelleme"),
        ("Poz Veritabanı", "100.000+ poz, 12 farklı kamu kurumu verisi (DSİ, KGM, TOKİ vb.)"),
        ("Mahal Listesi", "Mahal bazlı metraj ve malzeme takibi"),
        ("Poz Yönetimi", "Kurum pozları ile ilişkilendirme, özel poz ekleme"),
        ("Veri Aktarımı", "Excel import/export desteği"),
        ("Çıktı Formatları", "Word, Excel, PDF — resmi belge formatları"),
        ("Veritabanı", "PostgreSQL (çoklu kullanıcı desteği)"),
        ("Aşırı Düşük", "Aşırı düşük sorgulama mevzuatına uyum"),
        ("BIM Entegrasyon", "Allplan entegrasyonu"),
    ]
    tablo_olustur(doc, ["Özellik", "Açıklama"], hp_ozellikler)
    doc.add_paragraph()

    baslik_ekle(doc, "B) OskaGPT — Yapay Zeka Asistanı", 3)
    doc.add_paragraph("• HakedişPlus ana ekranında entegre çalışır")
    doc.add_paragraph("• 24/7 yaklaşık maliyet ve hakediş sorularına cevap verir")
    doc.add_paragraph("• NOT: Çok sınırlı — sadece temel soru-cevap, gerçek hesaplama yapmıyor")
    doc.add_paragraph()

    baslik_ekle(doc, "C) Diğer Ürünler", 3)
    diger = [
        ("OSKABULUT", "Web tabanlı bulut uygulama — tarayıcıdan erişim"),
        ("HM-Hakediş", "Hizmet alımı ödeme sertifikası (temizlik, yemek, güvenlik)"),
        ("e-DoğrudanTemin", "Kamu yönetimleri doğrudan temin kontrolü"),
        ("e-kikNet", "Kamu kurumları ihale yönetimi"),
        ("BirimFiyat.com", "Birim fiyat arama motoru (ücretsiz web servisi)"),
        ("MaliyetBul.com", "İnşaat maliyeti hesaplama web servisi"),
        ("OSEM", "Oska Eğitim Merkezi"),
    ]
    tablo_olustur(doc, ["Ürün", "Açıklama"], diger)
    doc.add_paragraph()

    doc.add_page_break()

    # ================================================================
    # 3. COM METRAJ (CB YAZILIM)
    # ================================================================
    baslik_ekle(doc, "3. COM METRAJ — CB YAZILIM", 1)

    p = doc.add_paragraph()
    run = p.add_run("Şirket Profili")
    run.bold = True
    run.font.size = Pt(11)
    doc.add_paragraph("• Kuruluş: 2010 | 15+ yıl | Metraj yazılımlarına odaklı")
    doc.add_paragraph("• Referanslar: Rönesans Holding, TOKİ, Çevre ve Şehircilik Bakanlığı, Artaş İnşaat")
    doc.add_paragraph("• Web: www.cbyazilim.com | Tel: 0850 304 12 66")
    doc.add_paragraph("• Fiyat: Teklif üzerine (30 dk ücretsiz online demo sunuyor)")
    doc.add_paragraph()

    baslik_ekle(doc, "3.1 Ana Ürünler ve Özellikler", 2)

    baslik_ekle(doc, "A) COM Donatı — Demir Metraj Yazılımı", 3)
    donati = [
        ("DWG Okuma", "Statik projelerden otomatik demir metrajı — AutoCAD 2010-2027 uyumlu"),
        ("Mevzuat", "TS500 ve Deprem Yönetmeliği uyumlu"),
        ("Akıllı Hesap", "Projelerde donatı adeti yazılmasa bile hesaplama yapabiliyor"),
        ("Yapı Elemanları", "Kolon, kiriş, döşeme, temel, duvar, perde — tümü destekleniyor"),
        ("Çıktılar", "Yeşil defter, keşif özeti, donatı sipariş listesi, kesim listesi"),
        ("Kamu Formatları", "TOKİ ve diğer kamu rapor formatları"),
        ("Multi-User", "COM Server ile çoklu kullanıcı desteği"),
        ("AMP Entegrasyon", "AMP Software KHYM ile entegrasyon"),
        ("CAD Desteği", "AutoCAD, GstarCAD 2026"),
        ("Kesim Optimizasyonu", "Fire minimizasyonu ile kesim listesi"),
    ]
    tablo_olustur(doc, ["Özellik", "Açıklama"], donati)
    doc.add_paragraph()

    baslik_ekle(doc, "B) COM Standard / COM Kaba — Beton, Kalıp, İskele Metrajı", 3)
    kaba = [
        ("Otomatik Hesap", "Tek tıkla tüm beton, kalıp, iskele metrajı"),
        ("Döşeme Tipleri", "Plak, kaset, mantar, asmolen, tünel kalıp"),
        ("Yapı Elemanları", "Temel, kolon, kiriş, perde duvar, döşeme"),
        ("Çıktılar", "Yeşil defter, keşif özeti, kalıp takımlama listeleri"),
        ("CAD Desteği", "AutoCAD, BricsCAD, ZWCAD, G-Star CAD"),
        ("BIM Okuma", "ideCAD, Sta4CAD, Probina formatları okunabiliyor"),
        ("Hız", "1 ayda yapılan işi 1 günde bitiriyor (firma iddiası)"),
    ]
    tablo_olustur(doc, ["Özellik", "Açıklama"], kaba)
    doc.add_paragraph()

    baslik_ekle(doc, "C) COM Mimari — İnce Metraj ve Keşif", 3)
    doc.add_paragraph("• Akıllı poz atama sistemi — 1-2 tıkla otomatik poz atama")
    doc.add_paragraph("• Benzer mahaller için hızlı toplu işlem")
    doc.add_paragraph("• Keşif özeti ve ince işler raporları")
    doc.add_paragraph()

    baslik_ekle(doc, "D) Teknik Altyapı", 3)
    teknik = [
        ("İşletim Sistemi", "Windows 10 ve üstü"),
        ("Veritabanı", "Microsoft SQL Server 2016"),
        ("Lisans", "Online lisanslama, cihaz değişiklikte ücretsiz taşıma"),
        ("Lisans Modeli", "Kalıcı lisans (sınırsız kullanım süresi)"),
        ("Multi-User", "COM Server ürünü ile kurumsal kullanım"),
    ]
    tablo_olustur(doc, ["Parametre", "Değer"], teknik)
    doc.add_paragraph()

    doc.add_page_break()

    # ================================================================
    # 4. KARŞILAŞTIRMA ANALİZİ
    # ================================================================
    baslik_ekle(doc, "4. DETAYLI KARŞILAŞTIRMA: Quantix Pro vs Rakipler", 1)

    baslik_ekle(doc, "4.1 Rakiplerde Var — Bizde YOK (Eksiklerimiz)", 2)

    p = doc.add_paragraph()
    run = p.add_run("⚠️  Bu eksikler kullanıcıların ikinci bir programa para ödemesine yol açıyor.")
    run.bold = True
    run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    run.font.size = Pt(11)

    eksikler = [
        ("Yaklaşık Maliyet Modülü", "AMP, OSKA", "KRİTİK",
         "4734 uyumlu resmi kamu yaklaşık maliyet. Piyasanın omurgası. Olmadan müteahhit ikinci bir programa para ödüyor."),
        ("Hakediş Modülü (Resmi)", "AMP, OSKA", "KRİTİK",
         "4734/4735 uyumlu resmi hakediş belgesi. Bizde AI asistanla kısmi destek var ama resmi çıktı yok."),
        ("100.000+ Poz Veritabanı", "AMP (140k), OSKA (100k+)", "KRİTİK",
         "DSİ, KGM, TOKİ, Sağlık Bakanlığı vb. kamu kurumu birim fiyatları. Bizde manuel/sınırlı poz girişi."),
        ("PDF'den Fare ile Metraj", "AMP Kolay Metraj", "YÜKSEK",
         "Çoğu kullanıcı DWG yerine PDF ile çalışıyor. Mouse tıklamasıyla uzunluk/alan/hacim. Çok talep gören özellik."),
        ("Kesim Listesi (Demir)", "COM Donatı", "YÜKSEK",
         "Fire minimizasyonu ile demir kesim optimizasyonu ve sipariş listesi. Demir metrajının doğal uzantısı."),
        ("Kalıp İskelesi Metrajı", "COM Kaba", "ORTA",
         "Beton + kalıp + iskele tek metrajda. Büyük projelerde kritik iş kalemi."),
        ("ideCAD/Sta4CAD Okuma", "COM Standard", "ORTA",
         "Türkiye'de yaygın kullanılan statik programlardan direkt okuma. Bizde sadece DWG/DXF var."),
        ("Multi-User (Çoklu Kullanıcı)", "AMP (SQL Server), COM", "ORTA",
         "Kurumsal kullanım için şart. Aynı projeye birden fazla kişi aynı anda erişebilmeli."),
        ("Bulut Versiyon", "AMP Bulut, OSKA Bulut", "DÜŞÜK",
         "Tarayıcıdan erişim. Uzak saha çalışması için faydalı ama kurulum gerektirmiyor."),
        ("Aşırı Düşük Sorgulama", "OSKA", "DÜŞÜK",
         "İhale mevzuatında zorunlu süreç. Otomatik aşırı düşük teklif tespiti."),
    ]

    tablo = doc.add_table(rows=1, cols=4)
    tablo.style = 'Table Grid'
    baslik_satiri = tablo.rows[0].cells
    for i, b in enumerate(["Eksik Özellik", "Kimde Var", "Öncelik", "Neden Önemli"]):
        baslik_satiri[i].text = b
        set_hucre_renk(baslik_satiri[i], "C00000")
        p = baslik_satiri[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)

    renk_map = {"KRİTİK": "FFD7D7", "YÜKSEK": "FFE8CC", "ORTA": "FFFACC", "DÜŞÜK": "E2EFDA"}
    for satir in eksikler:
        row = tablo.add_row().cells
        row[0].text = satir[0]
        row[1].text = satir[1]
        row[2].text = satir[2]
        row[3].text = satir[3]
        renk = renk_map.get(satir[2], "FFFFFF")
        for hucre in row:
            set_hucre_renk(hucre, renk)
            hucre.paragraphs[0].runs[0].font.size = Pt(9)
        row[2].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_page_break()

    baslik_ekle(doc, "4.2 Bizde Var — Rakiplerde YOK (Avantajlarımız)", 2)

    p = doc.add_paragraph()
    run = p.add_run("✅  Bu özellikler Quantix Pro'yu piyasada farklılaştırıyor.")
    run.bold = True
    run.font.color.rgb = RGBColor(0x37, 0x86, 0x1E)
    run.font.size = Pt(11)

    avantajlar = [
        ("Yapay Zeka Asistanı (7 Mod)", "Yok / OskaGPT çok sınırlı",
         "Claude API entegrasyonu: Metraj üretimi, hesap asistanı, Gantt planlama, hakediş, saha çözüm, gayrimenkul değerleme. Gerçek AI, sadece chatbot değil."),
        ("Gayrimenkul Değerleme Modu", "Yok",
         "SPK dışı hızlı değerleme: MIN-MAKS fiyat, kira getirisi, yatırım puanı, mülk tipi (daire/arsa/dükkan), Vision API ile ilan fotoğrafı analizi."),
        ("Gantt / İş Programı Entegre", "AMP Planner ayrı ücretli",
         "CPM hesabı, kritik yol, S-eğrisi, baseline karşılaştırma, tatil takvimi, senaryo analizi — hepsi ana yazılımda dahil."),
        ("EKAP Entegrasyonu", "Yok",
         "e-Kamu Alım Platformu'ndan ihale sorgulama, IKN ile arama, 10 yıllık istatistik, Excel aktarım."),
        ("TCMB Enflasyon Motoru", "Yok",
         "TCMB EVDS API ile gerçek zamanlı enflasyon verileri. Fiyat farkı hesabında otomatik güncelleme."),
        ("3D İnce İşler Görselleştirme", "Yok",
         "Oda bazlı 3D görsel modelleme ile ince işler metrajı kontrolü."),
        ("AutoCAD 2x/3x Çarpan Tespiti", "Yok",
         "2x8Ø12 gibi perde çarpanlarını otomatik tanıyan özel regex motoru."),
        ("Tüm Modüller Tek Yazılımda", "Parça parça satış",
         "AMP ve COM her modülü ayrı ücretlendiriyor. Quantix Pro: metraj + gantt + AI + EKAP + enflasyon hepsi bir arada."),
        ("Türkçe Terminoloji", "Kısmen İngilizce terimler",
         "Tüm arayüz saha diline uygun Türkçe — müteahhit ve taşeron için anlaşılır."),
        ("Offline Çalışma (EXE)", "Bulut bağımlılığı var",
         "İnternet gerektirmeyen tek dosya EXE dağıtım. Şantiyede internet olmasa da çalışır."),
    ]

    tablo = doc.add_table(rows=1, cols=3)
    tablo.style = 'Table Grid'
    baslik_satiri = tablo.rows[0].cells
    for i, b in enumerate(["Quantix Pro Özelliği", "Rakip Durum", "Açıklama"]):
        baslik_satiri[i].text = b
        set_hucre_renk(baslik_satiri[i], "375F1E")
        p = baslik_satiri[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)

    for idx, satir in enumerate(avantajlar):
        row = tablo.add_row().cells
        renk = "E2EFDA" if idx % 2 == 0 else "F4FCF0"
        row[0].text = satir[0]
        row[1].text = satir[1]
        row[2].text = satir[2]
        for hucre in row:
            set_hucre_renk(hucre, renk)
            hucre.paragraphs[0].runs[0].font.size = Pt(9)
        row[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_page_break()

    # ================================================================
    # 5. GENEL KARŞILAŞTIRMA TABLOSU
    # ================================================================
    baslik_ekle(doc, "5. Genel Özellik Karşılaştırma Tablosu", 1)

    basliklar = ["Özellik", "AMP", "OSKA", "COM Metraj", "Quantix Pro"]
    satirlar = [
        ["DWG'den Metraj", "✅", "❌", "✅", "✅"],
        ["PDF'den Metraj", "✅", "❌", "❌", "❌ (eksik)"],
        ["Demir Metrajı (Otomatik)", "✅", "❌", "✅", "✅"],
        ["Beton/Kalıp Metrajı", "✅", "❌", "✅", "Kısmi"],
        ["Kesim Listesi", "✅", "❌", "✅", "❌ (eksik)"],
        ["Yaklaşık Maliyet (4734)", "✅", "✅", "❌", "❌ (kritik eksik)"],
        ["Hakediş Modülü", "✅", "✅", "❌", "AI destekli (kısmi)"],
        ["Poz Veritabanı (100k+)", "✅", "✅", "❌", "❌ (eksik)"],
        ["İş Programı / Gantt", "Ayrı ücret", "❌", "❌", "✅ Dahil"],
        ["Yapay Zeka Asistanı", "❌", "Çok sınırlı", "❌", "✅ (7 mod, Claude API)"],
        ["EKAP Entegrasyonu", "❌", "❌", "❌", "✅"],
        ["Enflasyon Motoru", "❌", "❌", "❌", "✅ (TCMB EVDS)"],
        ["Gayrimenkul Değerleme", "❌", "❌", "❌", "✅"],
        ["3D Görselleştirme", "❌", "❌", "❌", "✅"],
        ["Çoklu Kullanıcı", "✅", "✅", "✅", "❌ (tek kullanıcı)"],
        ["Bulut Versiyon", "✅", "✅", "❌", "❌"],
        ["ideCAD / Sta4CAD Okuma", "❌", "❌", "✅", "❌"],
        ["BIM Entegrasyonu", "❌", "Allplan", "ideCAD", "❌"],
        ["Offline EXE Çalışma", "❌", "❌", "❌", "✅"],
        ["Fiyat (yaklaşık)", "89k-132k ₺/yıl", "Teklif üzeri", "Teklif üzeri", "Çok daha uygun"],
    ]

    tablo = doc.add_table(rows=1, cols=5)
    tablo.style = 'Table Grid'
    bs = tablo.rows[0].cells
    renkler_baslik = ["1F3564", "1F6191", "375F1E", "8B4513", "C00000"]
    for i, (b, r) in enumerate(zip(basliklar, renkler_baslik)):
        bs[i].text = b
        set_hucre_renk(bs[i], r)
        p = bs[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(9)

    for idx, satir in enumerate(satirlar):
        row = tablo.add_row().cells
        for i, deger in enumerate(satir):
            row[i].text = deger
            renk = "F2F2F2" if idx % 2 == 0 else "FFFFFF"
            if "✅" in deger and i > 0:
                renk = "E2EFDA"
            elif "❌" in deger and i > 0:
                renk = "FFE8E8"
            elif "Kısmi" in deger or "kısmi" in deger or "sınırlı" in deger:
                renk = "FFF3CC"
            set_hucre_renk(row[i], renk)
            row[i].paragraphs[0].runs[0].font.size = Pt(8)
            row[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT

    doc.add_paragraph()
    doc.add_page_break()

    # ================================================================
    # 6. STRATEJİK YATIRIM ÖNCELİKLERİ
    # ================================================================
    baslik_ekle(doc, "6. Stratejik Geliştirme Öncelikleri", 1)

    baslik_ekle(doc, "6.1 Kısa Vadeli (1-3 Ay) — Hızlı Kazanım", 2)
    doc.add_paragraph("Bu özellikler teknik açıdan görece hızlı eklenebilir ve rakiplerle farkı kapatır:")
    kisavade = [
        ("PDF'den Fare Metrajı", "2-4 hafta",
         "PyMuPDF + koordinat tıklama sistemi. AMP'ın en çok satan özelliği. Kullanıcı DWG olmadan da çalışabilir hale gelir."),
        ("Demir Kesim Listesi", "1-2 hafta",
         "Mevcut demir metraj motoruna ek. Fire minimizasyonu algoritması. Sipariş ve depolama optimizasyonu."),
        ("Temel Poz Veritabanı", "2-3 hafta",
         "En azından CŞB 2026 birim fiyat ve analizleri. Tam 100k poz yerine kullanım sıklığı yüksek 5-10k poz ile başlanabilir."),
    ]
    for item in kisavade:
        p = doc.add_paragraph(style='List Bullet')
        run = p.add_run(f"{item[0]} ")
        run.bold = True
        run = p.add_run(f"(~{item[1]}): ")
        run.italic = True
        p.add_run(item[2])

    doc.add_paragraph()
    baslik_ekle(doc, "6.2 Orta Vadeli (3-6 Ay) — Pazar Açıcı", 2)
    doc.add_paragraph("Bu özellikler yeni müşteri segmentlerine kapı açar (kamu ihalecileri):")
    ortavade = [
        ("Yaklaşık Maliyet Modülü", "3-5 ay",
         "En kritik eksik. 4734 uyumlu, kamu poz veritabanı bağlantılı. Tek başına yeni bir ürün olarak da satılabilir. İnşaat mühendisleri olmadan çok satış yapılamıyor."),
        ("Resmi Hakediş Çıktısı", "2-3 ay",
         "Mevcut AI hakediş asistanını resmi Word/PDF belge üretimine bağlamak. 4735 mad.29 formatına uyum."),
        ("ideCAD / Sta4CAD Okuma", "2-4 hafta",
         "COM'un farkı bu. Türkiye'deki en yaygın statik programlardan direkt okuma. Teknik açıdan ezdxf'e benzer bir parser yazılabilir."),
    ]
    for item in ortavade:
        p = doc.add_paragraph(style='List Bullet')
        run = p.add_run(f"{item[0]} ")
        run.bold = True
        run = p.add_run(f"(~{item[1]}): ")
        run.italic = True
        p.add_run(item[2])

    doc.add_paragraph()
    baslik_ekle(doc, "6.3 Uzun Vadeli (6+ Ay) — Kurumsal Sıçrama", 2)
    doc.add_paragraph("Bu özellikler kurumsal satışı ve hacimli kullanıcı kazanımını sağlar:")
    uzunvade = [
        ("Multi-User Altyapısı", "4-6 ay",
         "SQL Server backend + kullanıcı yönetimi. Büyük müteahhit firmalarına satış için şart. Şu an en büyük kurumsal engel."),
        ("Bulut Versiyon", "3-4 ay (multi-user sonrası)",
         "Şantiyeden telefon/tablet ile erişim. Özellikle saha mühendisleri için değerli."),
        ("Kalıp İskelesi Metrajı", "2-3 ay",
         "COM Kaba'nın ana özelliği. Büyük müteahhitlerde kritik iş kalemi."),
    ]
    for item in uzunvade:
        p = doc.add_paragraph(style='List Bullet')
        run = p.add_run(f"{item[0]} ")
        run.bold = True
        run = p.add_run(f"(~{item[1]}): ")
        run.italic = True
        p.add_run(item[2])

    doc.add_paragraph()
    doc.add_page_break()

    # ================================================================
    # 7. SONUÇ
    # ================================================================
    baslik_ekle(doc, "7. Sonuç ve Özet Değerlendirme", 1)

    p = doc.add_paragraph()
    run = p.add_run("Quantix Pro'nun Güçlü Yönleri:")
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0x37, 0x86, 0x1E)
    doc.add_paragraph("Piyasadaki rakipler teknolojik açıdan Quantix Pro'nun gerisinde kalıyor. Yapay zeka entegrasyonu, EKAP bağlantısı, enflasyon motoru, gayrimenkul değerleme ve Gantt gibi özelliklerin HİÇBİRİ AMP, OSKA veya COM Metraj'da yok. Bu özellikler önemli bir farklılaşma avantajı yaratıyor.")

    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run("Quantix Pro'nun Kritik Zayıflıkları:")
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    doc.add_paragraph("Yaklaşık Maliyet + Hakediş modülü olmadan Türkiye kamu inşaat sektörüne tam girilemiyor. Bu segment AMP ve OSKA'nın temel gelir kaynağı. Kullanıcılar şu an hem Quantix Pro hem AMP/OSKA kullanmak zorunda — bu birleştirilmeli.")

    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run("Stratejik Öneri:")
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0x1F, 0x35, 0x64)
    doc.add_paragraph("1. Kısa vadede: PDF metraj + Kesim Listesi (hızlı kazanım, 1-4 hafta)")
    doc.add_paragraph("2. Orta vadede: Yaklaşık Maliyet modülü (pazar açıcı, 3-5 ay, öncelik #1)")
    doc.add_paragraph("3. Uzun vadede: Multi-User altyapısı (kurumsal satış için şart)")
    doc.add_paragraph("Öncelik sırası bu şekilde olmalı — Yaklaşık Maliyet olmadan kamu ihalecilerine tam satış yapılamıyor.")

    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run("Fiyat Avantajı:")
    run.bold = True
    run.font.size = Pt(12)
    doc.add_paragraph("AMP yıllık abonelik 89.775 ₺ + AMP Planner (Gantt) ayrı ücret. Quantix Pro bu fiyatın çok altında tüm modülleri sunuyor. Fiyat/performans açısından ciddi avantaj var — pazarlama mesajında ön plana çıkarılmalı.")

    # Kaydet
    doc.save(CIKTI_DOSYA)
    print(f"BASARILI: {CIKTI_DOSYA}")
    return True

# ================================================================
# ÇALIŞTIRIC
# ================================================================
if __name__ == "__main__":
    if not DOCX_OK:
        print("HATA: python-docx kurulu degil.")
        print("Kurmak icin: pip install python-docx")
        sys.exit(1)

    print("Word belgesi olusturuluyor...")
    try:
        belge_olustur()
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
