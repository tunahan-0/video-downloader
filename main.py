import os
from pathlib import Path
import sys
import customtkinter as ctk
from tkinter import messagebox, filedialog
import subprocess
import json

kayit_dizini = ""
cookies_yolu = ""
ayarlar_klasoru = os.path.join(os.getenv('LOCALAPPDATA'), 'VideoIndirici')
os.makedirs(ayarlar_klasoru, exist_ok=True)  # Klasör yoksa oluştur
ayarlar_dosyasi = os.path.join(ayarlar_klasoru, 'ayarlar.json')

def ayarlari_yukle():
    global kayit_dizini, cookies_yolu
    try:
        if os.path.exists(ayarlar_dosyasi):
            with open(ayarlar_dosyasi, 'r', encoding='utf-8') as f:
                ayarlar = json.load(f)
                kayit_dizini = ayarlar.get('kayit_dizini', '')
                cookies_yolu = ayarlar.get('cookies_yolu', '')
                
                if kayit_dizini:
                    klasor_label.configure(text=f"📁 {kayit_dizini[-40:]}")
                if cookies_yolu and os.path.exists(cookies_yolu):
                    cookies_label.configure(text=f"🍪 {os.path.basename(cookies_yolu)}", text_color="#4CAF50")
                else:
                    cookies_yolu = ""
    except Exception as e:
        print(f"Ayarlar yüklenemedi: {e}")

def ayarlari_kaydet():
    try:
        ayarlar = {
            'kayit_dizini': kayit_dizini,
            'cookies_yolu': cookies_yolu
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

def cookies_sec():
    global cookies_yolu
    secilen_dosya = filedialog.askopenfilename(
        title="Cookies Dosyası Seç",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if secilen_dosya:
        cookies_yolu = secilen_dosya
        cookies_label.configure(text=f"🍪 {os.path.basename(secilen_dosya)}", text_color="#4CAF50")
        ayarlari_kaydet()

def dosya_yolu_bul(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def video_indir():
    link = link_box.get().strip()
    if not link:
        messagebox.showwarning("Uyarı", "Lütfen bir video linki girin.")
        return
    if not link.startswith(('http://', 'https://')):
        messagebox.showwarning("Uyarı", "Geçerli bir URL girin (http:// veya https://).")
        return
    
    indir_butonu.configure(state="disabled", text="İndiriliyor...") # Butonu devre dışı bırak
    hedef_yol = kayit_dizini if kayit_dizini else os.path.abspath(".")
    ffmpeg_konum = dosya_yolu_bul("ffmpeg_bin")
    ytdlp_exe = dosya_yolu_bul("yt-dlp.exe")
    
    komut = [
        ytdlp_exe,
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '--ffmpeg-location', ffmpeg_konum,
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
    
    if cookies_yolu and os.path.exists(cookies_yolu):
        komut.extend(['--cookies', cookies_yolu])

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
                    # Yüzdeyi çıkar ve progress bar'ı güncelle
                    yuzde_str = line.split('%')[0].split()[-1]
                    yuzde = float(yuzde_str)
                    progress_bar.set(yuzde / 100)
                    durum_label.configure(text=f"⬇️ İndiriliyor: %{yuzde:.1f}", text_color="#2196F3")
                except:
                    durum_label.configure(text="⬇️ İndiriliyor...", text_color="#2196F3")
                window.update()
        process.wait()
        
        if process.returncode == 0:
            progress_bar.set(1)
            durum_label.configure(text="✅ Başarıyla İndirildi!", text_color="#4CAF50")
            link_box.delete(0, 'end')  # Link kutusunu temizle

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
            
            # Pencereyi ortala
            basari_pencere.update_idletasks()
            x = (basari_pencere.winfo_screenwidth() // 2) - (400 // 2)
            y = (basari_pencere.winfo_screenheight() // 2) - (180 // 2)
            basari_pencere.geometry(f"400x180+{x}+{y}")
            
            # İçerik
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
            
            # Butonlar
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
            raise Exception(f"Hata kodu: {process.returncode}\n\nDetay:\n{tam_cikti[-500:]}")
            
    except Exception as hata:
        progress_bar.set(0)
        durum_label.configure(text="❌ İndirme başarısız!", text_color="#F44336")
        messagebox.showerror("Hata", f"Bir sorun oluştu:\n\n{str(hata)[:300]}")
    
    finally:
        # Butonu tekrar aktif et
        indir_butonu.configure(state="normal", text="🎬 Videoyu İndir")

# ------------------ Arayüz Tasarımı ------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.title("Video İndirici")
window.geometry("600x520")
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
title_frame.pack(fill="x", pady=(0, 20))

baslik = ctk.CTkLabel(
    title_frame, 
    text="🎥 Video İndirici", 
    font=("Arial Bold", 24),
    text_color="#2196F3"
)
baslik.pack(pady=20)

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
    placeholder_text="Buraya video linkini yapıştır...",
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

# Cookies seçimi
cookies_frame = ctk.CTkFrame(ayarlar_frame, fg_color="transparent")
cookies_frame.pack(fill="x", padx=20, pady=(0, 15))

cookies_btn = ctk.CTkButton(
    cookies_frame,
    text="🍪 Cookies Seç",
    command=cookies_sec,
    width=150,
    height=35,
    corner_radius=8,
    fg_color="#FF9800",
    hover_color="#F57C00"
)
cookies_btn.pack(side="left")

cookies_label = ctk.CTkLabel(
    cookies_frame,
    text="🍪 Yüklenmedi",
    font=("Arial", 10),
    text_color="#9E9E9E",
    anchor="w"
)
cookies_label.pack(side="left", padx=10)

# Alt bilgi
footer = ctk.CTkLabel(
    main_frame,
    text="TikTok, YouTube ve daha fazlası için destekler",
    font=("Arial", 9),
    text_color="#666666"
)
footer.pack(pady=(15, 0))

# Ayarları yükle
ayarlari_yukle()

window.mainloop()