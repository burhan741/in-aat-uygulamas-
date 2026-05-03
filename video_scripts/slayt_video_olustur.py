"""
Otomatik Slayt Video Oluşturucu — İnşaat Metraj Pro
=====================================================
Pillow ile slaytlar çizilir, imageio ile MP4 birleştirilir.

Kurulum:
    pip install pillow imageio imageio[ffmpeg]

Çalıştırma:
    python slayt_video_olustur.py
Çıktı:
    tanitim_slayt.mp4  (bu klasörde)
"""

from PIL import Image, ImageDraw, ImageFont
import imageio
import numpy as np
import os
import math

# ── Ayarlar ──────────────────────────────────────────────────────────────────
GENISLIK     = 1280
YUKSEKLIK    = 720
FPS          = 30
SLAYT_SURESI = 4        # her slayt kaç saniye
GECIS_KARE   = 20       # fade-in/out kare sayısı
CIKTI_DOSYA  = os.path.join(os.path.dirname(__file__), "tanitim_slayt.mp4")

# Renkler (program teması)
DARK_BG     = (26,  26,  46)
CARD_BG     = (22,  33,  62)
ACCENT      = (0,   191, 255)
TEXT_WHITE  = (224, 224, 224)
TEXT_GRAY   = (160, 160, 176)
GREEN       = (39,  174, 96)
ORANGE      = (243, 156, 18)
RED         = (231, 76,  60)

# Font — Windows sistem fontları
def _font(boyut, kalin=False):
    yollar = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if kalin else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for yol in yollar:
        try:
            return ImageFont.truetype(yol, boyut)
        except Exception:
            continue
    return ImageFont.load_default()

# ── Slayt içerikleri ─────────────────────────────────────────────────────────
SLAYLAR = [
    {
        "baslik":   "İnşaat Metraj Pro",
        "alt":      "Kamu İhaleleri için Profesyonel Hesap Platformu",
        "icerik":   [],
        "renk":     ACCENT,
        "logo":     True,
    },
    {
        "baslik":   "Yaklaşık Maliyet & Keşif Cetveli",
        "alt":      "4734 Sayılı KİK — ÇŞB Birim Fiyatları ile",
        "icerik":   [
            "✓  ÇŞB 2026 birim fiyat listesi entegre",
            "✓  Kategori filtresi & anlık poz arama",
            "✓  Poz seçin → miktar girin → tutar otomatik",
            "✓  Metraj modülünden tek tıkla aktarım",
        ],
        "renk":     GREEN,
    },
    {
        "baslik":   "Aşırı Düşük Teklif Analizi",
        "alt":      "KİK md.38 — İhaleye girmeden önce test edin",
        "icerik":   [
            "✓  Rakip teklif simülasyonu",
            "✓  Eşik değer otomatik hesaplama",
            "✓  Güvenli / riskli bölge görselleştirmesi",
            "✓  İhale öncesi stratejik analiz",
        ],
        "renk":     ORANGE,
    },
    {
        "baslik":   "İhale Değerlendirme Asistanı",
        "alt":      "Bu ihaleye girmeli miyim?",
        "icerik":   [
            "✓  Kendi maliyetinizi girin",
            "✓  Damga Vergisi, GV Stopajı, SGK — tüm kesintiler",
            "✓  Net kâr & risk skoru (1-5)",
            "✓  PDF fizibilite raporu",
        ],
        "renk":     ACCENT,
    },
    {
        "baslik":   "Teminat Yönetimi",
        "alt":      "Geçici & Kesin Teminat Takibi",
        "icerik":   [
            "✓  Geçici Teminat: İhale bedelinin %3'ü",
            "✓  Kesin Teminat: Sözleşme bedelinin %6'sı",
            "✓  Vade tarihi uyarıları",
            "✓  Teminat mektubu takip tablosu",
        ],
        "renk":     (142, 68, 173),
    },
    {
        "baslik":   "Hakediş Kesinti Hesabı",
        "alt":      "4735 md.8 — Tüm kesintiler otomatik",
        "icerik":   [
            "✓  Avans mahsubu & KİK kesintisi",
            "✓  SGK borcu kontrolü",
            "✓  Gecikme cezası hesabı",
            "✓  Excel & PDF çıktısı",
        ],
        "renk":     GREEN,
    },
    {
        "baslik":   "İnşaat Metraj Pro",
        "alt":      "Zaman kazanın • Hata yapmayın • Kazanın",
        "icerik":   [
            "",
            "    Detaylı bilgi ve demo için iletişime geçin.",
            "",
            "    burhan741@outlook.com",
        ],
        "renk":     ACCENT,
        "kapani":   True,
    },
]


# ── Çizim fonksiyonları ───────────────────────────────────────────────────────

def _arka_plan(draw: ImageDraw.Draw, renk_vurgu):
    """Degrade arka plan + sol şerit"""
    draw.rectangle([0, 0, GENISLIK, YUKSEKLIK], fill=DARK_BG)
    # Sol dikey şerit (vurgu rengi)
    draw.rectangle([0, 0, 6, YUKSEKLIK], fill=renk_vurgu)
    # Üst ince çizgi
    draw.rectangle([0, 0, GENISLIK, 2], fill=renk_vurgu)
    # Alt ince çizgi
    draw.rectangle([0, YUKSEKLIK - 2, GENISLIK, YUKSEKLIK], fill=renk_vurgu)

def _logo_ciz(draw: ImageDraw.Draw):
    """Sol üst köşe — basit logo kutusu"""
    draw.rectangle([30, 20, 120, 60], fill=ACCENT, outline=ACCENT)
    f = _font(16, kalin=True)
    draw.text((36, 30), "IMP", fill=DARK_BG, font=f)

def _baslik_ciz(draw: ImageDraw.Draw, baslik: str, alt: str, renk):
    f_buyuk = _font(52, kalin=True)
    f_kucuk = _font(22)
    draw.text((60, 120), baslik, fill=renk, font=f_buyuk)
    draw.line([(60, 195), (GENISLIK - 60, 195)], fill=renk, width=2)
    draw.text((62, 210), alt, fill=TEXT_GRAY, font=f_kucuk)

def _icerik_ciz(draw: ImageDraw.Draw, satirlar: list):
    f = _font(28)
    y = 280
    for satir in satirlar:
        renk = TEXT_WHITE if satir.startswith("✓") else TEXT_GRAY
        draw.text((80, y), satir, fill=renk, font=f)
        y += 56

def _sayfa_no_ciz(draw: ImageDraw.Draw, no: int, toplam: int):
    f = _font(16)
    metin = f"{no} / {toplam}"
    draw.text((GENISLIK - 80, YUKSEKLIK - 30), metin, fill=TEXT_GRAY, font=f)


def slayt_olustur(slayt: dict, no: int, toplam: int) -> Image.Image:
    img = Image.new("RGB", (GENISLIK, YUKSEKLIK), DARK_BG)
    draw = ImageDraw.Draw(img)
    renk = slayt.get("renk", ACCENT)

    _arka_plan(draw, renk)
    _logo_ciz(draw)

    if slayt.get("logo"):
        # Açılış slaydı — büyük ortalı başlık
        f1 = _font(72, kalin=True)
        f2 = _font(26)
        w1 = draw.textlength(slayt["baslik"], font=f1)
        draw.text(((GENISLIK - w1) // 2, 220), slayt["baslik"], fill=renk, font=f1)
        w2 = draw.textlength(slayt["alt"], font=f2)
        draw.text(((GENISLIK - w2) // 2, 330), slayt["alt"], fill=TEXT_GRAY, font=f2)
    elif slayt.get("kapani"):
        f1 = _font(60, kalin=True)
        f2 = _font(28)
        f3 = _font(22)
        w1 = draw.textlength(slayt["baslik"], font=f1)
        draw.text(((GENISLIK - w1) // 2, 160), slayt["baslik"], fill=renk, font=f1)
        draw.line([(60, 260), (GENISLIK - 60, 260)], fill=renk, width=2)
        w2 = draw.textlength(slayt["alt"], font=f2)
        draw.text(((GENISLIK - w2) // 2, 285), slayt["alt"], fill=TEXT_WHITE, font=f2)
        y = 370
        for satir in slayt.get("icerik", []):
            if satir.strip():
                draw.text((60, y), satir, fill=TEXT_GRAY, font=f3)
            y += 44
    else:
        _baslik_ciz(draw, slayt["baslik"], slayt["alt"], renk)
        _icerik_ciz(draw, slayt.get("icerik", []))

    _sayfa_no_ciz(draw, no, toplam)
    return img


def fade(img_a: Image.Image, img_b: Image.Image, adim: int, toplam: int) -> Image.Image:
    """İki kare arasında alpha blend (fade)"""
    oran = adim / toplam
    return Image.blend(img_a, img_b, oran)


# ── Video oluştur ─────────────────────────────────────────────────────────────

def video_olustur():
    print("Slaytlar oluşturuluyor...")
    kare_listesi = []
    toplam = len(SLAYLAR)
    slayt_kareler = FPS * SLAYT_SURESI

    onceki = None
    for i, slayt in enumerate(SLAYLAR, 1):
        img = slayt_olustur(slayt, i, toplam)
        print(f"  Slayt {i}/{toplam}: {slayt['baslik']}")

        if onceki is not None:
            # Fade-in geçişi (onceki → şimdiki)
            for j in range(GECIS_KARE):
                gecis = fade(onceki, img, j, GECIS_KARE)
                kare_listesi.append(gecis)

        # Slayt kareleri
        for _ in range(slayt_kareler - GECIS_KARE):
            kare_listesi.append(img)

        onceki = img

    print(f"\nVideo yazılıyor: {CIKTI_DOSYA}")
    print(f"  Toplam kare: {len(kare_listesi)} | FPS: {FPS} | Süre: {len(kare_listesi)/FPS:.1f}s")

    with imageio.get_writer(CIKTI_DOSYA, fps=FPS, codec="libx264",
                            quality=8, macro_block_size=1) as writer:
        for idx, kare in enumerate(kare_listesi):
            if idx % (FPS * 2) == 0:
                print(f"  {idx}/{len(kare_listesi)} kare ({idx/FPS:.0f}s)...")
            writer.append_data(np.array(kare))

    print(f"\nTamamlandi! → {CIKTI_DOSYA}")
    print("\n--- FARK ---")
    print("Bu video: Düz metin slaytlar, ses yok, animasyon yok.")
    print("OBS kaydı: Gerçek program görüntüsü, kullanım anlatımı, profesyonel.")


if __name__ == "__main__":
    video_olustur()
