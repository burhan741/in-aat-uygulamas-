# DEVLET İHALESİ MODÜLÜ — GELİŞTİRME PLANI

Ana Kategori : Devlet İhalesi
Yasal Dayanak: 4734 Kamu İhale Kanunu + 4735 Kamu İhale Sözleşmeleri Kanunu
Hedef Kullanıcı: Belediye / Bakanlık ihalelerine giren müteahhit ve taşeronlar

================================================================================

## ALT ARAÇLAR

### ARAÇ 1 — Yaklaşık Maliyet ve Keşif Özeti  [ TAMAMLANDI ✓ ]
Dosyalar:
  core  : app/core/yaklasik_maliyet_engine.py
  ui    : app/ui/yaklasik_maliyet_window.py

Ne yapar:
  - ÇŞB / DSİ / KGM / İller Bankası resmi birim fiyat listesi seçimi
  - Poz no → miktar → birim fiyat → tutar zinciri
  - KDV dahil / hariç hesap
  - Aşırı düşük teklif sınır değeri otomatik hesabı
  - Resmi keşif özeti formatında Excel + PDF export

### ARAÇ 2 — Hakediş Kesinti ve Mahsup Hesabı  [ TAMAMLANDI ✓ ]
Dosyalar:
  core  : app/core/hakedis_kesinti_engine.py
  ui    : app/ui/hakedis_kesinti_window.py
  kap   : app/ui/devlet_ihalesi_widget.py    (tüm araçların container'ı)

Ne yapar:
  - Avans mahsubu (avans oranı × hakediş tutarı)
  - Kesin teminat kesintisi (%6)
  - Damga vergisi (%0.948)
  - Gelir vergisi stopajı (%3)
  - SGK prim kesintisi
  - Gecikme cezası mahsubu
  - Net ödenecek tutar + resmi hakediş belgesi PDF

### ARAÇ 3 — SGK Asgari İşçilik Hesabı  [ TAMAMLANDI ✓ ]
Dosyalar:
  core  : app/core/sgk_iscilik_engine.py
  ui    : app/ui/sgk_iscilik_window.py

Ne yapar:
  - İş kolu kodu seçimi (inşaat=45, altyapı=42 vb.)
  - Sözleşme bedeli × asgari işçilik oranı = zorunlu işçilik
  - Zorunlu sigortalı gün sayısı hesabı
  - Yıllık prim takvimi
  - SGK e-bildirge uyumlu çıktı

### ARAÇ 4 — Fiyat Farkı Hesabı  [ TAMAMLANDI ✓ ]
Dosyalar:
  core  : app/core/fiyat_farki_engine.py
  ui    : app/ui/fiyat_farki_window.py

Ne yapar:
  - TÜİK D1/D2/D3 endeks katsayıları
  - Temel endeks vs. uygulama endeksi farkı
  - Poz bazlı fiyat farkı hesabı
  - Aylık fiyat farkı talebi belgesi
  - Enflasyon modülüyle entegrasyon

### ARAÇ 5 — Birim Fiyat Analiz Cetveli  [ TAMAMLANDI ✓ ]
Dosyalar:
  core  : app/core/birim_fiyat_analiz_engine.py
  ui    : app/ui/birim_fiyat_analiz_window.py

Ne yapar:
  - Poz başına: malzeme + işçilik + makine + genel gider + kâr
  - Nakil mesafesi hesabı (ocak → şantiye km × birim fiyat)
  - Resmi analiz formu PDF (A4 bakanlık formatı)

### ARAÇ 6 — Gecikme Cezası ve Süre Uzatımı  [ TAMAMLANDI ✓ ]
Dosyalar:
  core  : app/core/gecikme_ceza_engine.py
  ui    : app/ui/gecikme_ceza_window.py

Ne yapar:
  - Günlük gecikme cezası = sözleşme bedeli × %0.06
  - Toplam ceza üst sınırı (%30 → fesih eşiği)
  - Mücbir sebep günleri (Gantt modülüyle entegre)
  - Süre uzatım talebi belgesi

### ARAÇ 7 — Teminat Yönetimi  [ TAMAMLANDI ✓ ]
Dosyalar:
  core  : app/core/teminat_engine.py
  ui    : app/ui/teminat_window.py

Ne yapar:
  - Geçici teminat: ihale bedelinin %3'ü
  - Kesin teminat: sözleşme bedelinin %6'sı
  - Ek kesin teminat (aşırı düşük teklif farkı)
  - Teminat mektubu takip tablosu (banka, vade, tutar)
  - İade tarihleri ve şartları

================================================================================

## ANA PENCEREYE ENTEGRASYON

MainWindow'da yeni sekme: "Devlet İhalesi"
  └── Yaklaşık Maliyet
  └── Hakediş Kesintileri
  └── SGK Asgari İşçilik
  └── Fiyat Farkı
  └── Birim Fiyat Analizi
  └── Gecikme Cezası
  └── Teminat Yönetimi

================================================================================

## GELİŞTİRME SIRASI (ROI Önceliği)

1. Yaklaşık Maliyet + Keşif Özeti   — ihale öncesi zorunlu, en yüksek ROI
2. Hakediş Kesinti Güçlendirme       — her iş sonrası tekrarlı kullanım
3. SGK Asgari İşçilik                — hukuki zorunluluk
4. Fiyat Farkı Hesabı                — nakit akışı etkisi
5. Birim Fiyat Analiz Cetveli        — şartname gerekirse zorunlu
6. Gecikme Cezası / Süre Uzatımı     — savunma aracı
7. Teminat Yönetimi                  — takip kolaylığı

================================================================================
Son güncelleme: 2026-02-19 (TÜM 7 ARAÇ TAMAMLANDI ✓ — main_window entegrasyonu yapıldı)
