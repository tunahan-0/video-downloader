import os
from pathlib import Path
import sys
import customtkinter as ctk
from tkinter import messagebox, filedialog
import subprocess
import json
import threading
import urllib.request
import zipfile

kayit_dizini = ""
cookies_yolu = ""          # TikTok cookie yolu
cookies_yolu_yt = ""       # YouTube cookie yolu
secili_platform = "tiktok"  # Varsayılan platform
ayarlar_klasoru = os.path.join(os.getenv('LOCALAPPDATA'), 'VideoDownloader')
os.makedirs(ayarlar_klasoru, exist_ok=True)
ayarlar_dosyasi = os.path.join(ayarlar_klasoru, 'settings.json')

def ayarlari_yukle():
    global kayit_dizini, cookies_yolu, cookies_yolu_yt
    try:
        if os.path.exists(ayarlar_dosyasi):
            with open(ayarlar_dosyasi, 'r', encoding='utf-8') as f:
                ayarlar = json.load(f)
                kayit_dizini = ayarlar.get('kayit_dizini', '')
                cookies_yolu = ayarlar.get('cookies_yolu', '')
                cookies_yolu_yt = ayarlar.get('cookies_yolu_yt', '')

                if kayit_dizini:
                    klasor_label.configure(text=f"📁 {kayit_dizini[-40:]}")
                if cookies_yolu and os.path.exists(cookies_yolu):
                    cookies_label_tt.configure(text=f"🍪 {os.path.basename(cookies_yolu)}", text_color="#4CAF50")
                else:
                    cookies_yolu = ""
                if cookies_yolu_yt and os.path.exists(cookies_yolu_yt):
                    cookies_label_yt.configure(text=f"🍪 {os.path.basename(cookies_yolu_yt)}", text_color="#4CAF50")
                else:
                    cookies_yolu_yt = ""
    except Exception as e:
        print(f"Ayarlar yüklenemedi: {e}")

def ayarlari_kaydet():
    try:
        ayarlar = {
            'kayit_dizini': kayit_dizini,
            'cookies_yolu': cookies_yolu,
            'cookies_yolu_yt': cookies_yolu_yt
        }
        with open(ayarlar_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(ayarlar, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ayarlar kaydedilemedi: {e}")

def klasör_sec():
    global kayit_dizini
    secilen_yol = filedialog.askdirectory()
    if secilen_yol:
        kayit_dizini = secilen_yol
        klasor_label.configure(text=f"📁 {secilen_yol[-40:]}")
        ayarlari_kaydet()

def cookies_sec_tt():
    global cookies_yolu
    secilen_dosya = filedialog.askopenfilename(
        title="TikTok Cookies Dosyası Seç",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if secilen_dosya:
        cookies_yolu = secilen_dosya
        cookies_label_tt.configure(text=f"🍪 {os.path.basename(secilen_dosya)}", text_color="#4CAF50")
        ayarlari_kaydet()

def cookies_sec_yt():
    global cookies_yolu_yt
    secilen_dosya = filedialog.askopenfilename(
        title="YouTube Cookies Dosyası Seç",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if secilen_dosya:
        cookies_yolu_yt = secilen_dosya
        cookies_label_yt.configure(text=f"🍪 {os.path.basename(secilen_dosya)}", text_color="#4CAF50")
        ayarlari_kaydet()

def appdata_yolu(dosya_adi):
    return os.path.join(ayarlar_klasoru, dosya_adi)

def dosya_yolu_bul(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def araci_indir(url, hedef_yol, aciklama):
    try:
        durum_label.configure(text=f"Indiriliyor: {aciklama}...", text_color="#FFC107")
        window.update()
        urllib.request.urlretrieve(url, hedef_yol)
        return True
    except Exception as e:
        print(f"{aciklama} indirilemedi: {e}")
        return False

def baslangic_kurulum():
    ytdlp_yolu = appdata_yolu("yt-dlp.exe")
    deno_yolu = appdata_yolu("deno.exe")

    ilk_kurulum = False

    if not os.path.exists(ytdlp_yolu):
        ilk_kurulum = True
        araci_indir(
            "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
            ytdlp_yolu,
            "yt-dlp"
        )

    if not os.path.exists(deno_yolu):
        ilk_kurulum = True
        zip_yolu = appdata_yolu("deno.zip")
        if araci_indir(
            "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip",
            zip_yolu,
            "Deno"
        ):
            try:
                with zipfile.ZipFile(zip_yolu, "r") as z:
                    z.extract("deno.exe", ayarlar_klasoru)
                os.remove(zip_yolu)
            except Exception as e:
                print(f"Deno zip acilamadi: {e}")

    if os.path.exists(ytdlp_yolu) and os.path.exists(deno_yolu):
        if not ilk_kurulum:
            durum_label.configure(text="Guncelleme kontrol ediliyor...", text_color="#888888")
            window.update()

        def sessiz_guncelle():
            try:
                if sys.platform == "win32":
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    si.wShowWindow = subprocess.SW_HIDE
                    subprocess.run([ytdlp_yolu, "-U"], startupinfo=si, timeout=30)
                    subprocess.run([deno_yolu, "upgrade"], startupinfo=si, timeout=60)
                else:
                    subprocess.run([ytdlp_yolu, "-U"], timeout=30)
                    subprocess.run([deno_yolu, "upgrade"], timeout=60)
            except Exception as e:
                print(f"Guncelleme hatasi: {e}")
            finally:
                durum_label.configure(text="", text_color="white")

        threading.Thread(target=sessiz_guncelle, daemon=True).start()
    else:
        durum_label.configure(text="", text_color="white")

def platform_sec(platform):
    """Platform seçimini günceller ve buton görünümlerini ayarlar."""
    global secili_platform
    secili_platform = platform

    if platform == "tiktok":
        tiktok_btn.configure(
            fg_color="#FF2D55",
            hover_color="#E0002A",
            text_color="white"
        )
        youtube_btn.configure(
            fg_color="#2a2a2a",
            hover_color="#333333",
            text_color="#888888"
        )
        platform_badge.configure(text="● TikTok", text_color="#FF2D55")
    else:
        youtube_btn.configure(
            fg_color="#FF0000",
            hover_color="#CC0000",
            text_color="white"
        )
        tiktok_btn.configure(
            fg_color="#2a2a2a",
            hover_color="#333333",
            text_color="#888888"
        )
        platform_badge.configure(text="● YouTube", text_color="#FF0000")

def video_indir():
    link = link_box.get().strip()
    if not link:
        messagebox.showwarning("Uyarı", "Lütfen bir video linki girin.")
        return
    if not link.startswith(('http://', 'https://')):
        messagebox.showwarning("Uyarı", "Geçerli bir URL girin (http:// veya https://).")
        return
    
    indir_butonu.configure(state="disabled", text="İndiriliyor...")
    hedef_yol = kayit_dizini if kayit_dizini else os.path.abspath(".")
    ffmpeg_konum = dosya_yolu_bul("ffmpeg_bin")
    ytdlp_exe = appdata_yolu("yt-dlp.exe")

    if secili_platform == "tiktok":
        # TikTok: mevcut çalışan ayarlar
        komut = [
            ytdlp_exe,
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--ffmpeg-location', ffmpeg_konum,
            '--merge-output-format', 'mp4',
            '-o', os.path.join(hedef_yol, '%(id)s.%(ext)s'),
            '--no-check-certificate',
            '--socket-timeout', '180',
            '--newline',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            '--add-header', 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            '--add-header', 'Accept-Language:en-US,en;q=0.9',
            '--add-header', 'Accept-Encoding:gzip, deflate, br',
            '--add-header', 'DNT:1',
            '--add-header', 'Connection:keep-alive',
            '--add-header', 'Upgrade-Insecure-Requests:1',
            '--referer', 'https://www.tiktok.com/',
        ]
    else:
        # YouTube: 1080p60fps öncelikli, fallback zinciri ile
        komut = [
            ytdlp_exe,
            '-f', (
                'bestvideo[height<=1080][fps<=60][vcodec^=avc][ext=mp4]+bestaudio[ext=m4a]/'
                'bestvideo[height<=1080][fps<=60][ext=mp4]+bestaudio[ext=m4a]/'
                'bestvideo[height<=1080][fps<=60]+bestaudio/'
                'bestvideo[height<=1080]+bestaudio/'
                'best'
            ),
            '--ffmpeg-location', ffmpeg_konum,
            '--merge-output-format', 'mp4',
            '-o', os.path.join(hedef_yol, '%(title)s.%(ext)s'),  # YouTube'da başlık daha kullanışlı
            '--no-check-certificate',
            '--socket-timeout', '180',
            '--newline',
            '--legacy-server-connect',
            '--js-runtimes', f'deno:{appdata_yolu("deno.exe")}',
        ]

    if secili_platform == "tiktok":
        if cookies_yolu and os.path.exists(cookies_yolu):
            komut.extend(['--cookies', cookies_yolu])
    else:
        if cookies_yolu_yt and os.path.exists(cookies_yolu_yt):
            komut.extend(['--cookies', cookies_yolu_yt])
        else:
            indir_butonu.configure(state="normal", text="🎬 Videoyu İndir")
            messagebox.showwarning(
                "Cookie Gerekli",
                "YouTube indirmesi için cookie dosyası gerekli.\n\n"
                "Tarayıcınızdan cookies.txt export edip\n"
                "Ayarlar bölümünden YouTube Cookies seçin."
            )
            return

    komut.append(link)
    
    try:
        durum_label.configure(text="⏳ İndirme başlatılıyor...", text_color="#FFC107")
        progress_bar.set(0)
        window.update()
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, startupinfo=startupinfo)
        else:
            process = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        cikti_satirlari = []
        for line in process.stdout:
            cikti_satirlari.append(line)
            if '[download]' in line and '%' in line:
                try:
                    yuzde_str = line.split('%')[0].split()[-1]
                    yuzde = float(yuzde_str)
                    progress_bar.set(yuzde / 100)
                    durum_label.configure(text=f"⬇️ İndiriliyor: %{yuzde:.1f}", text_color="#2196F3")
                except:
                    durum_label.configure(text="⬇️ İndiriliyor...", text_color="#2196F3")
                window.update()
        process.wait()

        # Tüm çıktıyı log dosyasına yaz
        log_yolu = os.path.join(ayarlar_klasoru, 'latest.log')
        with open(log_yolu, 'w', encoding='utf-8') as lf:
            lf.write(f"Platform: {secili_platform}\n")
            lf.write(f"Link: {link}\n\n")
            lf.write(''.join(cikti_satirlari))

        if process.returncode == 0:
            progress_bar.set(1)
            durum_label.configure(text="✅ Başarıyla İndirildi!", text_color="#4CAF50")
            link_box.delete(0, 'end')

            def klasore_git():
                if sys.platform == 'win32':
                    os.startfile(hedef_yol)
                basari_pencere.destroy()
            
            basari_pencere = ctk.CTkToplevel(window)
            basari_pencere.title("Başarılı")
            basari_pencere.geometry("400x180")
            basari_pencere.resizable(False, False)
            basari_pencere.transient(window)
            basari_pencere.grab_set()
            
            basari_pencere.update_idletasks()
            x = (basari_pencere.winfo_screenwidth() // 2) - (400 // 2)
            y = (basari_pencere.winfo_screenheight() // 2) - (180 // 2)
            basari_pencere.geometry(f"400x180+{x}+{y}")
            
            ctk.CTkLabel(
                basari_pencere,
                text="✅ Video başarıyla indirildi!",
                font=("Arial Bold", 16),
                text_color="#4CAF50"
            ).pack(pady=(20, 10))
            
            ctk.CTkLabel(
                basari_pencere,
                text=f"Konum: {hedef_yol}",
                font=("Arial", 10),
                wraplength=360
            ).pack(pady=(0, 20))
            
            buton_frame = ctk.CTkFrame(basari_pencere, fg_color="transparent")
            buton_frame.pack(pady=10)
            
            ctk.CTkButton(
                buton_frame,
                text="📁 Klasöre Git",
                command=klasore_git,
                width=150,
                height=35,
                fg_color="#2196F3",
                hover_color="#1976D2",
                font=("Arial Bold", 12)
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                buton_frame,
                text="Tamam",
                command=basari_pencere.destroy,
                width=100,
                height=35,
                fg_color="#455A64",
                hover_color="#37474F",
                font=("Arial", 12)
            ).pack(side="left", padx=5)  
        else:
            tam_cikti = ''.join(cikti_satirlari)
            raise Exception(f"Hata kodu: {process.returncode}\n\nDetay:\n{tam_cikti[-1000:]}")
            
    except Exception as hata:
        progress_bar.set(0)
        durum_label.configure(text="❌ İndirme başarısız!", text_color="#F44336")
        log_yolu = os.path.join(ayarlar_klasoru, 'latest.log')
        messagebox.showerror("Hata", f"Bir sorun oluştu:\n\n{str(hata)[:600]}\n\nTam log: {log_yolu}")
    
    finally:
        indir_butonu.configure(state="normal", text="🎬 Videoyu İndir")

# ------------------ Arayüz Tasarımı ------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.title("Video İndirici")
window.geometry("640x640")  # Yüksekliği biraz artırdık (platform butonları için)
window.resizable(False, False)
try:
    icon_path = dosya_yolu_bul('icon.ico')
    window.iconbitmap(icon_path)
except:
    pass

# Ana container
main_frame = ctk.CTkFrame(window, fg_color="transparent")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Başlık
title_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15)
title_frame.pack(fill="x", pady=(0, 15))

baslik = ctk.CTkLabel(
    title_frame,
    text="🎥 Video İndirici",
    font=("Arial Bold", 24),
    text_color="#2196F3"
)
baslik.pack(pady=(20, 10))

# --- Platform Seçim Butonları ---
platform_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
platform_frame.pack(pady=(0, 15))

tiktok_btn = ctk.CTkButton(
    platform_frame,
    text="TikTok",
    command=lambda: platform_sec("tiktok"),
    width=130,
    height=38,
    corner_radius=10,
    fg_color="#FF2D55",       # Başlangıçta TikTok seçili
    hover_color="#E0002A",
    text_color="white",
    font=("Arial Bold", 13)
)
tiktok_btn.pack(side="left", padx=(0, 8))

youtube_btn = ctk.CTkButton(
    platform_frame,
    text="YouTube",
    command=lambda: platform_sec("youtube"),
    width=130,
    height=38,
    corner_radius=10,
    fg_color="#2a2a2a",       # Başlangıçta pasif
    hover_color="#333333",
    text_color="#888888",
    font=("Arial Bold", 13)
)
youtube_btn.pack(side="left", padx=(8, 0))

# Aktif platform göstergesi
platform_badge = ctk.CTkLabel(
    title_frame,
    text="● TikTok",
    font=("Arial", 10),
    text_color="#FF2D55"
)
platform_badge.pack(pady=(0, 5))

# Link bölümü
link_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15)
link_frame.pack(fill="x", pady=(0, 15))

link_label = ctk.CTkLabel(
    link_frame,
    text="📎 Video Linki",
    font=("Arial", 12),
    anchor="w"
)
link_label.pack(padx=20, pady=(15, 5), anchor="w")

link_box = ctk.CTkEntry(
    link_frame,
    width=540,
    height=40,
    placeholder_text="Video linkini yapıştır...",
    font=("Arial", 12),
    corner_radius=10
)
link_box.pack(padx=20, pady=(0, 15))

# İndir butonu
indir_butonu = ctk.CTkButton(
    main_frame,
    text="🎬 Videoyu İndir",
    command=video_indir,
    height=45,
    font=("Arial Bold", 14),
    corner_radius=10,
    fg_color="#2196F3",
    hover_color="#1976D2"
)
indir_butonu.pack(fill="x", pady=(0, 15))

# Progress bar
progress_bar = ctk.CTkProgressBar(main_frame, height=8, corner_radius=5)
progress_bar.pack(fill="x", pady=(0, 10))
progress_bar.set(0)

# Durum bilgisi
durum_label = ctk.CTkLabel(
    main_frame,
    text="",
    font=("Arial", 11),
    height=25
)
durum_label.pack(pady=(0, 15))

# Ayarlar bölümü
ayarlar_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15)
ayarlar_frame.pack(fill="x")

ayarlar_baslik = ctk.CTkLabel(
    ayarlar_frame,
    text="⚙️ Ayarlar",
    font=("Arial Bold", 13),
    anchor="w"
)
ayarlar_baslik.pack(padx=20, pady=(15, 10), anchor="w")

# Klasör seçimi
klasor_frame = ctk.CTkFrame(ayarlar_frame, fg_color="transparent")
klasor_frame.pack(fill="x", padx=20, pady=(0, 10))

klasor_btn = ctk.CTkButton(
    klasor_frame,
    text="📁 Kayıt Yeri Seç",
    command=klasör_sec,
    width=150,
    height=35,
    corner_radius=8,
    fg_color="#455A64",
    hover_color="#37474F"
)
klasor_btn.pack(side="left")

klasor_label = ctk.CTkLabel(
    klasor_frame,
    text="📁 Varsayılan (Program Klasörü)",
    font=("Arial", 10),
    anchor="w"
)
klasor_label.pack(side="left", padx=10)

# TikTok Cookies seçimi
cookies_frame_tt = ctk.CTkFrame(ayarlar_frame, fg_color="transparent")
cookies_frame_tt.pack(fill="x", padx=20, pady=(0, 8))

ctk.CTkButton(
    cookies_frame_tt,
    text="🍪 TikTok Cookies",
    command=cookies_sec_tt,
    width=150,
    height=35,
    corner_radius=8,
    fg_color="#FF2D55",
    hover_color="#E0002A"
).pack(side="left")

cookies_label_tt = ctk.CTkLabel(
    cookies_frame_tt,
    text="🍪 Yüklenmedi",
    font=("Arial", 10),
    text_color="#9E9E9E",
    anchor="w"
)
cookies_label_tt.pack(side="left", padx=10)

# YouTube Cookies seçimi
cookies_frame_yt = ctk.CTkFrame(ayarlar_frame, fg_color="transparent")
cookies_frame_yt.pack(fill="x", padx=20, pady=(0, 15))

ctk.CTkButton(
    cookies_frame_yt,
    text="🍪 YouTube Cookies",
    command=cookies_sec_yt,
    width=150,
    height=35,
    corner_radius=8,
    fg_color="#FF0000",
    hover_color="#CC0000"
).pack(side="left")

cookies_label_yt = ctk.CTkLabel(
    cookies_frame_yt,
    text="🍪 Yüklenmedi",
    font=("Arial", 10),
    text_color="#9E9E9E",
    anchor="w"
)
cookies_label_yt.pack(side="left", padx=10)

# Ayarları yükle
ayarlari_yukle()

# Açılış kurulum kontrolü
window.after(500, baslangic_kurulum)

window.mainloop()