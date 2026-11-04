# İnşaat & Yazılım Baş Danışmanı Protokolü

> Rev geçmişinin tamamı: `PROGRAM_OZELLIKLERI.txt` + `git log`. Eski uzun CLAUDE.md git geçmişinde (2026-11-03 öncesi commit). Bu dosya sadece **geçerli kurallar + açık işler** içerir.

## 1. Çalışma Protokolü
- **Önce inşaat mantığı, sonra kod:** (1) Mühendis: metraj/statik/hakediş/kalıp mantığını ve saha gerçeğini analiz et. (2) Yazılımcı: OOP, modüler, test edilebilir Python'a aktar.
- **Sorgula:** Yönetmeliğe, matematiğe veya yazılım standardına aykırı talimatta uyar ve "Neden?" diye sor; daha iyi alternatif sun. Talep gerçekte uygulanabilir değilse açıkça söyle — kurgu/işlevsiz modül ekleme. Objektif ol.
- **Onay sorma:** Tüm işlemler önceden onaylı; best practice'i seç ve uygula. Hataları sormadan çöz, yaptığın her işlemi sormadan test et. Fikir almak için soru sorulabilir.
- **Yeniden yazma > yama:** Modülü yeniden yazmak hata ayıklamaktan ucuzsa yeniden yaz. Token'ı verimli kullan.
- **Kayıt:** Her eklenen/güncellenen özelliği `PROGRAM_OZELLIKLERI.txt`'ye yeni Rev olarak ekle. Her hatadan çıkan GENEL kuralı bu dosyaya (ilgili başlığa, kısa) ekle. Her işlemden sonra bu dosyayı güncelle.
- **"claude md oku" dendiğinde:** memory'deki açık işleri hatırlat.
- Yeni/güncellenen modülde: amaca uygun mu, kullanım kolaylığı nasıl artar — birlikte değerlendir.
- Ticari ürün bakışı: müteahhit/taşerona maliyet, zaman, ROI argümanı üret; rakip ve sektör darboğazlarını göz önünde tut. Arayüz/rapor dili profesyonel ve güven verici olsun.
- İş m² ve iş kolları için Çevre ve Şehircilik Bakanlığı verilerini kullan.
- Kullanıcı tercihi: plan için güçlü model, uygulama için hızlı model; uygun işlerde birden fazla ajan.

## 2. Kod Standartları
- **4 boşluk**, PEP 8, tab yok. Her fonksiyon/sınıf: "Neyi çözüyoruz?" + "Nasıl test ederiz?".
- Ondalık/birim dönüşümü tek noktada yapılır (cm→m bir kez).
- `py_compile` sadece syntax yakalar → kritik modülde gerçek import testi de yap.
- Kod yazarken sahadaki karşılığını ve ekonomik etkisini de açıkla.

## 3. Arayüz Dili — Kesinlikle Türkçe
| YASAK | ZORUNLU |
|---|---|
| Baseline | Referans Plan |
| What-If | Senaryo Analizi |
| S-Curve | S-Eğrisi |
| Milestone | Kilometre Taşı |
| Dashboard | Kontrol Paneli |
| Export / Import | Dışa Aktar / İçe Aktar |
| Save / Load | Kaydet / Yükle |
| Settings | Ayarlar |
| Report / Summary / Analysis | Rapor / Özet / Analiz |
| Filter | Filtrele |
| Resource | Kaynak |
| Task | Görev / İş Kalemi |
| Drag & Drop | Sürükle-Bırak |
| Critical Path | Kritik Yol |
| Duration / Dependency | Süre / Bağımlılık |

**Kılavuz zorunlu:** Her programda "?"/"Yardım" butonu, adım adım Türkçe sade kılavuz, her sekme/panelde tooltip.

---

## 4. Ortam ve Proje Yapısı
- Ana kod: `yeni_proje/` (`app/core` motorlar, `app/ui` PyQt6). Kullanıcı programı **sistem Python 3.11 (WindowsApps)** ile çalıştırır; `.venv` de var → COM testlerini ikisinde koş.
- Programı başlatma (harness): `cmd /c start "" /D "<yeni_proje>" pythonw main.py` — doğrudan Start-Process konsolla birlikte öldürülür (0xC000013A).
- Program değişiklikten önce açıksa log satır numaraları koddan farklı olur → yeniden başlat. `dist/QuantixPro.exe` eski olabilir; gerçek testte `main.py`.
- PowerShell'de satır içi Python'da `del x[i]` → harness "Remove-Item" sanıp engeller; betiği dosyaya yaz. `Remove-Item ... "data\*"` deseni engellenir.
- Testlerde `QUANTIX_DATA_DIR`'i geçici klasöre yönlendir (gerçek `data/` kirlenmesin). Test betikleri `yeni_proje/scratchpad/`.

### Git / Yedek (KRİTİK)
- Üst depo `burhan741/in-aat-uygulamas-` (ÖZEL, dal **master**; `main` dalı eski — klonlarken `-b master`). `yeni_proje` = alt modül, ayrı depo `burhan741/InsaatMetrajPro` (main, **HERKESE AÇIK**). Üstte `git add -A` alt modülün dosyalarını yedeklemez.
- Stop kancası → `yedekle.ps1` (önce yeni_proje commit+push, sonra üst, sonra veri zip → OneDrive\QuantixPro_Yedek). Geri yükleme: `GERI_YUKLEME.md`.
- API anahtarı (`data/claude_config.json`), DB'ler, müşteri verisi ASLA `yeni_proje`'ye commit'lenmez.
- Özellik belgesi/rapor üretmeden önce `git log` ve son değişen `.py` tarihlerini `PROGRAM_OZELLIKLERI.txt` ile karşılaştır.

### EXE
- Spec `yeni_proje/InsaatMetrajPro.spec`, hook `runtime_hook_db.py`, derleme `build_exe.bat`, çıktı `dist/QuantixPro.exe`.
- EXE'de yazılabilir dosyalar `%APPDATA%\QuantixPro\` (`QUANTIX_DATA_DIR`, `QUANTIX_LOG_DIR`).
- `database.py`'ye Edit ile kod ekleme (geçmişte SyntaxError) — path değişikliklerini `main.py`'de yap.
- `on_tab_changed()` except bloklarında `raise` yok; matplotlib importunda `except Exception`.

---

## 5. Genel Teknik Kurallar

### Python / Windows
- `strftime()` format string'ine emoji koyma (Windows locale → UnicodeEncodeError).
- Eski dosyalarda 1-space girinti olabilir: `.pyc` silmeden önce kaynağı `py_compile` et; SyntaxError varsa pyc'yi silme.
- `AttributeError: no attribute` → önce kaynakta metod var mı bak; varsa sebep stale `.pyc`.
- Import zincirinde `except (ImportError, Exception)`.
- `math.ceil`'e giden her oranı önce `round(x, 9)` (1.10*100 = 110.00000000000001 → +1 adet).
- Kullanıcıya gösterilen metraj: `tek_hane` (Decimal yarım-yukarı); `format(x, ".1f")` yarımı çifte yuvarlar. Excel'de tek hane = sayı BİÇİMİ, değeri yuvarlama.
- Gösterimi yuvarlanan hücreden değer geri okunuyorsa tam değeri `UserRole`'de sakla.
- Bir hatayı monkey-patch ile düzeltip sonra çekirdeği düzeltirsen patch'i aynı anda kaldır (2x çarpan iki kez uygulanmıştı). Beklenmedik sonuçta paket `__init__.py`'sine de bak.

### PyQt Arayüz
- Yerel QSS'te `background` veren her kural `color`'u da açıkça versin (global koyu temadan beyaz metin miras → görünmez yazı); `QComboBox QAbstractItemView` dahil.
- Uzayabilen paneller dış `QScrollArea` içinde olsun (yoksa iç kutular sessizce sıkışır).
- `setFixedWidth` → `setMinimumWidth` çevirirken aynı sütundaki tüm etiketleri birlikte, ortak değerle çevir.
- Başka metodların eriştiği `self.x` widget'ını arayüzden kaldırırken nesneyi silme; layout'a eklemeden oluştur.
- Sekme ipucunu `addTab`'ın döndürdüğü indeksle ver (`count()-1` değil).
- `open_X_window()` metodları singleton olmalı (`isVisible()` + `try/except RuntimeError`); yoksa aktarılan veri kaybolur.
- Benzer isimli butonları (ör. "EXCEL'E AKTAR" ikilisi) isim/renk/tooltip ile ayrıştır.
- Önceki adıma bağlı olmayan butonu kendi guard'ıyla aktif bırak ("tıklanmıyor" algısı).
- Tablo doldururken `blockSignals(True/False)`; `model().item(idx)` None olabilir.
- Veri tutan her döngü `QDialog`'u `reject()` override etsin (Esc/X = sessiz kayıp) → Evet/Hayır/Vazgeç.
- Kopya üzerinde çalışan panelde iç içe liste varsa `copy.deepcopy`.
- Tekrar basılabilen toplu okuma araçları: anahtar (kat + eleman adı / handle) ile registry → aynı anahtar GÜNCELLER, birikmez.
- Formülü kopyalama: özet/rapor her sekmenin kendi hesap fonksiyonunu çağırsın; aynı eleman iki araçtan girilebiliyorsa tek fonksiyon.

### Headless Test Tuzakları
- `QMessageBox.warning/information/question` ve modal dialog `exec`'lerini yamala (yoksa test sonsuza bloke).
- `QTimer.singleShot(0, panel._dongu)` olan panellerde singleShot'ı no-op yap (çift döngü).
- `isVisible()` için pencere `show()` + doğru sekme gerekir; alternatif `isHidden()`.
- Görsel sorunları (hiza, kesik metin, görünmez yazı) `widget.grab()` ekran görüntüsüyle doğrula.
- Sahte connector'lar yeni imzaları içermeli (`doseme_nokta_al(..., anahtarlar="")`, `obje_rengi_ayarla`).
- `win.aktif_kat_adi` doğrudan atanırsa kiriş/döşeme listesi o katınkine döner (property).
- Bir sekmeyi değiştirince o sekmenin TÜM test dosyalarını koş.
- Sentetik tablo grid'inde en az 2 veri satırı ve küçük koordinat jitter'ı kullan.

### AutoCAD COM
- COM mesaj filtresi `app/core/com_mesaj_filtresi.py` (ctypes; pywin32'de `CoRegisterMessageFilter` yok), `baglan()`'da kaydedilir. Kendi retry döngüsü olan yerde azami beklemeyi kısalt (`kisa_bekleme`) — beklemeler çarpılır.
- Retry'da `com_error` + `AttributeError` ikisini yakala (dinamik dispatch meşgulken `AttributeError("Add.SelectOnScreen")` fırlatır — nesne yanlış değil, AutoCAD meşgul). `_mesgul_retry`'i sadece var olduğu kesin özelliklerde kullan.
- Retry lambda'sı zincirin tamamını içersin: `lambda: self.aktif_cizim.Utility.GetPoint()`.
- RPC_E_CALL_REJECTED / AttributeError asla ESC/iptal sayılmaz.
- COM referansını (aktif_cizim/model_space) bir kez alıp sonsuza dek kullanma: DWG kapanınca RPC_E_DISCONNECTED (-2147417848). Her araç başında `cizim_baglantisini_tazele()` (öne getirme içinde) — yeni araç öne getirme yapmıyorsa bunu açıkça çağır (Rev-170).
- OSMODE gibi geçici sistem değişkeni: orijinali dosyaya yaz, `finally`'de geri yükle; context manager'ı elle açtıysan geri almayı en dış `finally`'ye koy.
- SendCommand/seçim içeren her metod AutoCAD'i öne getirsin; etkileşimli döngülerde öne getirme oturumda bir kez (`_autocad_one_getir_hafif`), geri bildirim komut satırına (`Prompt`), sayı `GetReal`, tam Regen yok. `komut_satiri_mesaj` metne ">>>" kendisi ekler.
- Bağımlı LISP ifadelerini tek `SendCommand` + `(progn (load ...) (c:komut))` ile gönder (iki komut + sleep güvenilmez). Sayısal LISP değişkeni tırnaksız (`sayisal_degisken_set`).
- Ortak COM yardımcılarına koşulsuz log ekleme (binlerce satır) — teşhis bayrağına bağla.
- Explode() ModelSpace'e kopya ekler → her turda `finally`'de sil.
- Handle sadece bir DWG içinde benzersiz → registry anahtarına kat da girsin.
- Geometriden ölçü: `Length`/`Area` çizim biriminde; birim kullanıcıya seçtirilir, ilk okuma teyit edilir; alan çarpanının KARESİ. 1/50 + mm çizimde geometriden boyut çıkarma — yazı etiketini oku.
- DIMENSION: görünen = `Measurement × LinearScaleFactor`; `TextOverride` farklıysa sor; açısal ölçü radyandır.
- Kapalı eğri alanı: `vlax-curve-getArea` başarısızsa `vla-get-Area`; ikisi de başarısızsa sessizce atlama, bildir.
- Eleman adlandırması projeye göre değişir (SBH/TK/TB...) → kullanıcının tek tek seçtiği yazıda ad SERBEST olsun, sabit ön eke bağlama; gevşetirken donatı (Ø/%%c) ve komşu eleman (kolon) yazılarını ayıkla (Rev-169).
- Kutu seçimli araçlarda ilgisiz objeleri sessizce atla (boyama/log yok); regex sıkı olsun (ör. kolon boyutu zorunlu parantez). Tek harf ön ek kuralları uzun ön ekleri yutmasın (S→kolon, SBH hariç).
- Kullanıcı tek ENTER'da birden fazla öğe seçebilir / birden fazla tabloyu kutulayabilir → geometriyle ayır veya sıralı seçim; ayıramazsan açık hata.
- Elle girilen sayıda çizim birimi ≠ alan birimi ise büyük değer teyidi (cm/m 100 kat hatası).
- Renk geri alma: her boyamada önceki program rengini sakla, ters sırayla geri al; paylaşılan handle varsa referans sayımı; zaten boyanmışı tekrar boyama (orijinal renk kaydı ezilir).
- **Renk düzeni:** YEŞİL okundu · KIRMIZI geçersiz / okunamayan S-P adı · SARI atlandı · GRİ tanımsız · MACENTA döşeme · TURUNCU (ACI 30) iç kiriş · MAVİ kenar kiriş · CAMGÖBEĞİ (ACI 4) perde · KEHRİBAR (ACI 40) saçak. Yeni araçta çakıştırma.
- Gen_py önbelleği bozuksa `%LOCALAPPDATA%\Temp\gen_py\` silinip yeniden başlatılır.

### Metraj Hesap Kararları (kullanıcı onaylı)
- Kolon kalıbı tam kat, kiriş birleşim düşümü YOK — tekrar önerme. Kolon tam kat / perde net yükseklik (`perde_hesapla`, uzun/kısa ≥ 6 → perde, TBDY 2018).
- Kiriş h tam (döşeme düşülmez), L kolon yüzleri arası; döşeme alanı kiriş iç yüzleri arası. Bölünmüş kenar: yan kalıp DOLU, beton/alt KAPSAM.
- Perde kalıbında döşeme kalınlığı otomatik (hakim kalınlık; eşitlikte ince); saçaklar sayılmaz. Döşeme mükerrer denetimi saçakları hariç tutar.
- Aralıklı donatı adedi `ceil(mesafe/aralık)+1`. "2x8Ø12" = 16 adet.
- Kesim: standart boyu aşan parça kırmızı "STANDART DIŞI" uyarı (bindirme otomatik değil); kullanılabilir artık eşiği 50 cm; kesim aracı bindirme eklemez.
- Formüllü Excel'de alt satır ana satırla aynı sütundaysa toplam = ana satır listesi (`SUM(F7,F10)`), aralık değil.

### Mevzuat / Birim Sabitleri
- Gecikme cezası (4735 md.20) günlük `0.005`; fesih %30. Geçici teminat %3, kesin %6. Damga %0.948, stopaj %3, KDV %20.
- Verimlilik (CŞB): demir bağlama 333 kg/gün/usta, nervürlü 250; kalıp döşeme 4.00 m²/gün, kiriş 2.86, kolon 1.82, sökme 8.00; iç sıva 25, dış 20; iç boya 45, dış 30; seramik 8, mermer 4, laminat 25.
- CŞB poz seed fiyatları yaklaşık — kesin fiyat için resmi listeden CSV import.

### Gantt
- `Task(task_id=int, ad, sure_gun, ..., kaynak="")` — `id`/`oncul_ids` parametresi yok; bağımlılık `task.predecessors.append((id, "FS", 0))`. Kod yazmadan önce `Task.__init__`'i oku.
- CPM backward pass: önce `proje_bitis = max(early_finish)`, terminal LF = proje_bitis. `move_task` datetime alır. S-eğrisinde tatil günü ilerleme yok.

### Claude API
- Tool `input_schema` property key'leri ASCII (`^[a-zA-Z0-9_.-]{1,64}$`); açıklamalar Türkçe olabilir.

### Puantaj Flask (`yeni_proje/pythonanywhere/`) — Şantiye ana programı (Rev-171+)
- Plan ve onaylı kararlar: `pythonanywhere/ANA_PROGRAM_PLANI.md` (tekrar sorma). Modüler: `app.py` (ana menü `/` + Blueprint kaydı) · `ortak.py` · `puantaj.py` (DEĞİŞMEZ, `/puantaj`) · `vinc.py` · `cari.py`. Tek DB `puantaj.db`, yeni tablolar `CREATE TABLE IF NOT EXISTS`.
- Kullanıcı tüm `.py` dosyalarını `/home/burhan852/` altına elle yükler + Reload; her teslimde dosya listesi ver. YENİ dosya eklenen adımda bunu ⚠️ ile vurgula: `app.py` yüklenip yeni modül yüklenmezse tüm site (puantaj dahil) "Unhandled Exception" ile çöker (Rev-173'te yaşandı). Geri dönüş: `eski/app_tek_dosya.py` → `app.py` olarak yükle.
- Test: `.venv_test\Scripts\python -m pytest` (conftest DB'yi geçici dosyaya yönlendirir). Puantaj regresyonu eski/yeni uygulamayı aynı DB'de birebir karşılaştırır; gerçek veri için `GERCEK_DB=<indirilen puantaj.db>`.
- HTML şablonları `r'''`. Inline onclick'te string argüman yerine sıfır argümanlı fonksiyon. Gömülü JS testte `node --check`.
- Yeni modül sayfaları `ortak.ORTAK_HEAD/CSS/JS`'i kullanır (açık tema, `satirHtml`+`kaydirmaKur` sola kaydır Düzenle/Sil, `onayla()`, `fmtTL`); stil/davranış tek yerde değişir.
- Cari: etiket/birim sadece `cari.TURLER`'de; açık türler `AKTIF_TURLER`. Fiyat kilidi sunucuda (yeni satırda istemci fiyatı yok sayılır). Ad tekrar denetimi `ortak.tr_kucuk` (SQLite lower/casefold Türkçe I'yi bozar).
- Sunucu saati UTC → kullanıcıya görünen saat/varsayılan gün `ortak.simdi_tr()/bugun_tr()`.
- Yeni modüllerin para/miktar gösterimi `ortak.para_tl/miktar_tr` (Decimal yarım-yukarı). Kalan eksiyse "Fazla ödeme" (sıfırlama yok) — puantajda eski davranış kalır.
- Opsiyonel kütüphaneler (openpyxl, reportlab…) route İÇİNDE `try/except ImportError` → 503; dosya tepesinde değil (tüm site çöker).
- İşlem anındaki oran (ücret, birim fiyat) satıra kilitlenir; hesap `SUM(miktar * COALESCE(satir.oran, parent.oran))`.
- Hızlı aksiyon butonları göndermediği alanları sıfırla ezmesin (`COALESCE(?, kolon)`).
- Mesai = `(gunluk_ucret/8) × saat` (çarpansız). Bakiye/kalan alanları tüm zamanlar kümülatif, sadece ödemeyle düşer. "Yevmiye" = `kalan_gun`, "Ödenecek Para" = `kalan`. Haftalık görünüm rolling son 7 gün. Bu Haftaki Toplam'da çivi `civi_toplam`.
- `prompt()/confirm()` öncesi scroll konumunu yakala.
- Test: izole `.venv_test`; gerçek `puantaj.db`'ye asla dokunma (sadece kopyası).

---

## 6. Açık İşler (2026-11-03)
- **Kullanıcı denemesi bekliyor:** Rev-170 DWG değişince otomatik bağlantı tazeleme · Rev-169 temel kirişi serbest ad (TK/TB... projede) · Rev-168 proje Kaydet/Aç + otomatik kayıt · Rev-166 Excel tek hane + SBH/Aralıklı Esc-X · Rev-164 Saçak (gerçek AutoCAD) · Rev-155 perde ideCAD · Rev-142 aralıklı donatı DIMENSION · demir kesim 5 dosya birleştirme.
- **Şantiye ana programı (PythonAnywhere):** ANA_PROGRAM_PLANI.md 6 adımın hepsi bitti (Rev-171..176), kullanıcının sunucuda uçtan uca denemesi bekleniyor. Test sitesi: yeni hesap `burhan741.pythonanywhere.com` (canlı puantaj hâlâ `burhan852`'de). Son geçişte güncel `puantaj.db` tekrar kopyalanmalı.
- **Karar bekliyor:** CŞB Poz + Malzeme Formül (Seçenek B) · İnce İşler Hızlı Hesap paneli (mevcut üzerine mi, sıfırdan mı).
- **Bilinen açık:** Demir Metrajı'nda kat silinince o katın perde/kolon kayıtları silinmiyor. Eski `_create_kiris_group` ölü kod — bağlanırsa `kiris_table`/`kiris_h_spin` adı çakışır.
- **Güvenlik:** `InsaatMetrajPro` deposunu özel yap; `in-aat-uygulamas-` `main` dalında eski API anahtarı var.
- **Silinmiş modüller (önermeden önce varlığını doğrula):** EKAP API, Gayrimenkul Değerleme, sahibinden scraper (Rev-121), dxf_engine (Rev-64).
