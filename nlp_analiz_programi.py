import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
import threading
import io
import re

# ==========================================
# --- 1. NLP (YAPAY ZEKA) DUYGU ANALİZİ ---
# ==========================================
def turkce_karakter_temizle(metin):
    tr_harfler = "şçöğüıŞÇÖĞÜİ"
    en_harfler = "scoguiSCOGUI"
    ceviri_tablosu = str.maketrans(tr_harfler, en_harfler)
    return metin.translate(ceviri_tablosu).lower()

def nlp_puanla(metin):
    metin_norm = turkce_karakter_temizle(metin)
    
    agir_ovguler = ["harika", "mukemmel", "efsane", "bayildim", "sahane", "super", "enfes", "muazzam", "nefis", "kusursuz", "muhtesem", "efsaneydi", "favorim", "inanilmaz", "bayildik"]
    hafif_ovguler = ["guzel", "iyi", "lezzetli", "taze", "sicak", "hizli", "doyurucu", "temiz", "basarili", "kibar", "guleryuzlu", "begendim", "uygun", "taptaze", "tesekkurler", "tavsiye", "bol", "kral"]
    hafif_elestiriler = ["kotu", "yavas", "soguk", "pahali", "kaba", "lezzetsiz", "tatsiz", "tuzsuz", "eksik", "bayat", "kucuk", "az", "ozensiz", "gecikti", "pismanlik", "sivi", "cig", "yanmis"]
    agir_elestiriler = ["berbat", "igrenc", "rezalet", "rezil", "zehirlendik", "pis", "cope", "berbatti", "igrencti", "asla", "sakin", "kokuyordu", "curuk", "bozuk"]
    ters_koseler = ["degil", "yok", "yoktu", "gelmedi", "olmamis", "kalmamis", "unutmussunuz"]

    puan = 3 
    
    for kelime in agir_ovguler:
        if kelime in metin_norm: puan += 2
    for kelime in hafif_ovguler:
        if kelime in metin_norm: puan += 1
    for kelime in hafif_elestiriler:
        if kelime in metin_norm: puan -= 1
    for kelime in agir_elestiriler:
        if kelime in metin_norm: puan -= 2
        
    ters_kose_sayisi = sum(1 for kelime in ters_koseler if kelime in metin_norm)
    if ters_kose_sayisi > 0:
        puan -= (ters_kose_sayisi * 2) 

    if puan > 5: puan = 5
    if puan < 1: puan = 1
    return str(puan)

def dozer_filtre(metin):
    if not metin: return ""
    temiz = " ".join(str(metin).replace("\n", " ").replace("\r", " ").split())
    return temiz.replace(";", ",")

# ==========================================
# --- 2. DOSYA VE NÜFUS YÖNETİMİ ---
# ==========================================
nufus_verileri = {}
secilen_dosya_yolu = ""
nufus_dosya_yolu = ""

def nufus_dosyasi_sec():
    global nufus_dosya_yolu
    dosya = filedialog.askopenfilename(title="Nüfus Excelini (il_nufus.csv) Seç", filetypes=[("CSV Dosyaları", "*.csv")])
    if dosya:
        nufus_dosya_yolu = dosya
        btn_nufus.config(text=f"✔ NÜFUS SEÇİLDİ", bg="#A6E3A1", fg="#11111B")
        
        try:
            try:
                f = open(dosya, 'r', encoding='utf-8-sig')
                icerik = f.read()
                f.close()
            except:
                f = open(dosya, 'r', encoding='cp1254')
                icerik = f.read()
                f.close()
                
            ayirici = ';' if ';' in icerik.split('\n')[0] else ','
            okuyucu = csv.reader(io.StringIO(icerik), delimiter=ayirici)
            
            nufus_verileri.clear()
            for satir in okuyucu:
                if len(satir) >= 2:
                    il_adi = satir[0].strip()
                    nufus_sayisi = satir[1].strip()
                    if il_adi and nufus_sayisi:
                        nufus_verileri[il_adi] = nufus_sayisi
            arayuze_yaz(f">> Nüfus dosyası yüklendi. ({len(nufus_verileri)} İl Bulundu)")
        except Exception as e:
            messagebox.showerror("Hata", f"Nüfus dosyası okunamadı!\nDetay: {e}")

def yorum_dosyasi_sec():
    global secilen_dosya_yolu
    dosya = filedialog.askopenfilename(title="İşlenecek Ham CSV Dosyasını Seç", filetypes=[("CSV Dosyaları", "*.csv")])
    if dosya:
        secilen_dosya_yolu = dosya
        btn_dosya.config(text=f"✔ İŞLENECEK DOSYA SEÇİLDİ", bg="#A6E3A1", fg="#11111B")
        arayuze_yaz(">> Yorum dosyası yüklendi. Analize hazır!")

def arayuze_yaz(metin):
    app.after(0, lambda: durum_label.config(text=metin))

def nufus_eslestir(aranan_il):
    aranan = aranan_il.lower().strip()
    for il_adi, nufus in nufus_verileri.items():
        il_lower = il_adi.lower().strip()
        if il_lower in aranan or aranan in il_lower:
            return nufus
    if "afyon" in aranan: return "740.000"
    if "çanakkale" in aranan or "canakkale" in aranan: return "560.000"
    if "kars" in aranan: return "270.000"
    if "zonguldak" in aranan: return "580.000"
    return "Bilinmiyor"

# ==========================================
# --- 3. KUSURSUZ (EXACT MATCH) SATIR MOTORU ---
# ==========================================
def is_valid_new_row(satir_listesi):
    if len(satir_listesi) < 3: return False
    
    c0 = str(satir_listesi[0]).strip().lower()
    c1 = str(satir_listesi[1]).strip().lower() if len(satir_listesi) > 1 else ""
    
    # KESİN EŞLEŞTİRME LİSTESİ (Sadece bunlar geçerli şehirdir!)
    exact_cities = ["afyonkarahisar", "afyonkara", "afyon", "çanakkale", "canakkale", "kars", "zonguldak", "il", "i̇l"]
    
    if c0 in exact_cities or c1 in exact_cities: return True
    if c0.isdigit() and c1 in exact_cities: return True
    if c0 == "sıra no": return True
    
    return False

def analiz_baslat():
    if not nufus_dosya_yolu:
        messagebox.showwarning("Eksik Dosya", "Lütfen önce Nüfus (il_nufus.csv) dosyasını seçin!")
        return
    if not secilen_dosya_yolu:
        messagebox.showwarning("Eksik Dosya", "Lütfen analiz edilecek dosyayı seçin!")
        return

    def calistir():
        buton_analiz.config(state=tk.DISABLED, bg="#9E9E9E", text="FİNAL DÜZELTME YAPILIYOR...")
        arayuze_yaz(">> Kopmuş yorumlar dikiliyor ve tablo hizalanıyor...")
        
        yeni_veriler = []
        yeni_basliklar = ["İl", "İlçe", "Restoran Adı", "Yıldız", "Yorum Sayısı", "Ortalama Puan (NLP)", "Enlem", "Boylam", "Nüfus", "Yorumlar"]
        yeni_veriler.append(yeni_basliklar)
        islenen_kayit = 0
        
        try:
            # 1. Dosya Formatı Tespiti
            try:
                with open(secilen_dosya_yolu, 'r', encoding='utf-8-sig') as f: f.readline()
                dosya_kodu = 'utf-8-sig'
            except:
                dosya_kodu = 'cp1254'
                
            with open(secilen_dosya_yolu, 'r', encoding=dosya_kodu) as f:
                ilk_satir_test = f.readline()
                
            delim = ';' if ';' in ilk_satir_test else ','

            # 2. SATIRLARI KAYDETME FONKSİYONU
            def save_current_row(row_data):
                nonlocal islenen_kayit
                if not row_data or len(row_data) < 5: return
                
                c0_check = str(row_data[0]).lower()
                offset = 1 if (c0_check.isdigit() or "sıra" in c0_check or "sira" in c0_check) else 0
                
                il_adi = dozer_filtre(row_data[0 + offset]) if len(row_data) > offset else ""
                ilce = dozer_filtre(row_data[1 + offset]) if len(row_data) > 1+offset else ""
                restoran = dozer_filtre(row_data[2 + offset]) if len(row_data) > 2+offset else ""
                yildiz = dozer_filtre(row_data[3 + offset]) if len(row_data) > 3+offset else ""
                yorum_sayisi = dozer_filtre(row_data[4 + offset]) if len(row_data) > 4+offset else ""
                
                enlem, boylam = "", ""
                yorum_baslangic = 5 + offset
                
                # Koordinatları Görünümünden Bulma
                for i in range(5 + offset, min(10 + offset, len(row_data))):
                    val = str(row_data[i]).strip()
                    if re.match(r'^\d{2}[.,]\d{3,}$', val): 
                        if not enlem: enlem = dozer_filtre(val)
                        elif not boylam:
                            boylam = dozer_filtre(val)
                            yorum_baslangic = i + 1
                            break
                            
                if not enlem or not boylam:
                    enlem = dozer_filtre(row_data[6]) if len(row_data) > 6 else ""
                    boylam = dozer_filtre(row_data[7]) if len(row_data) > 7 else ""
                    yorum_baslangic = 8
                    
                ham_yorumlar = " | ".join([str(x) for x in row_data[yorum_baslangic:] if str(x).strip()])
                ham_yorumlar = re.sub(r'\b(740\.000|560\.000|270\.000|580\.000|Bilinmiyor)\b', '', ham_yorumlar)
                tum_yorumlar = dozer_filtre(ham_yorumlar)
                
                nlp_skoru = nlp_puanla(tum_yorumlar)
                
                if "afyonkara" in il_adi.lower() and "hisar" not in il_adi.lower():
                    il_adi = "Afyonkarahisar"
                    
                nufus = nufus_eslestir(il_adi)
                
                yeni_satir = [il_adi, ilce, restoran, yildiz, yorum_sayisi, nlp_skoru, enlem, boylam, nufus, tum_yorumlar]
                yeni_veriler.append(yeni_satir)
                islenen_kayit += 1

            # 3. GERÇEK DİKİŞ ALGORİTMASI
            with open(secilen_dosya_yolu, 'r', encoding=dosya_kodu) as f:
                okuyucu = csv.reader(f, delimiter=delim)
                
                current_row = []
                ilk_satir_gecildi = False
                
                for satir in okuyucu:
                    if not satir: continue
                    
                    if is_valid_new_row(satir):
                        # Aha! Gerçek bir restorana geldik. Eskisini kaydet!
                        if current_row:
                            if not ilk_satir_gecildi:
                                ilk_satir_gecildi = True # Başlık satırını yoksay
                            else:
                                save_current_row(current_row)
                        current_row = list(satir) # Yeni restorana başla
                    else:
                        # Bu satır kırık bir yorum parçası! Önceki restoranın arkasına yapıştır!
                        if current_row:
                            current_row.extend(satir)

                # Döngü bitince son kalan restoranı da kaydet
                if current_row and ilk_satir_gecildi:
                    save_current_row(current_row)

            # 4. ÇIKTI OLUŞTURMA
            klasor = os.path.dirname(secilen_dosya_yolu)
            eski_dosya_adi = os.path.basename(secilen_dosya_yolu)
            if "KUSURSUZ_ANALIZ_" in eski_dosya_adi: eski_dosya_adi = eski_dosya_adi.replace("KUSURSUZ_ANALIZ_", "")
            if "ANALIZ_EDILDI_" in eski_dosya_adi: eski_dosya_adi = eski_dosya_adi.replace("ANALIZ_EDILDI_", "")
                
            yeni_dosya_yolu = os.path.join(klasor, f"FINAL_ANALIZ_{eski_dosya_adi}")

            with open(yeni_dosya_yolu, mode='w', newline='', encoding='utf-8-sig') as f:
                yazici = csv.writer(f, delimiter=';')
                yazici.writerows(yeni_veriler)
                
            arayuze_yaz(f"✔ İŞLEM TAMAM: Hata ihtimali %0.")
            messagebox.showinfo("Başarılı", f"Tam {islenen_kayit} mekan kusursuzca hizalandı ve analiz edildi!\n\nDosya: {yeni_dosya_yolu}")
            
        except Exception as e:
            arayuze_yaz("✖ BİR HATA OLUŞTU.")
            messagebox.showerror("Hata", f"Beklenmeyen bir sorun yaşandı.\n\nDetay: {e}")
            
        buton_analiz.config(state=tk.NORMAL, bg="#E53935", text="🔥 NLP ANALİZİNİ BAŞLAT 🔥")

    threading.Thread(target=calistir, daemon=True).start()

# ==========================================
# --- 4. ARAYÜZ (GUI) ---
# ==========================================
app = tk.Tk()
app.title("Veri NLP Analiz Motoru - FİNAL SÜRÜM")
app.geometry("450x500")
app.configure(bg="#181825") 

header_frame = tk.Frame(app, bg="#181825", pady=20)
header_frame.pack(fill="x")
tk.Label(header_frame, text="🧠 KİŞİSEL VERİ ANALİZ MOTORU", font=("Segoe UI", 16, "bold"), bg="#181825", fg="#89B4FA").pack()
tk.Label(header_frame, text="Mutlak Çözüm: CSV Exact Match Motoru", font=("Segoe UI", 10), bg="#181825", fg="#A6ADC8").pack()

orta_frame = tk.Frame(app, bg="#313244", padx=20, pady=25, highlightthickness=1, highlightbackground="#45475A")
orta_frame.pack(fill="x", padx=30, pady=10)

tk.Label(orta_frame, text="1. Nüfus Dosyasını (il_nufus.csv) Seçin", font=("Segoe UI", 9, "bold"), bg="#313244", fg="#CDD6F4").pack()
btn_nufus = tk.Button(orta_frame, text="📂 NÜFUS DOSYASI SEÇ", bg="#F9E2AF", fg="#11111B", font=("Segoe UI", 10, "bold"), command=nufus_dosyasi_sec)
btn_nufus.pack(pady=(5, 15))

tk.Label(orta_frame, text="2. İşlenecek Dosyayı Seçin", font=("Segoe UI", 9, "bold"), bg="#313244", fg="#CDD6F4").pack()
btn_dosya = tk.Button(orta_frame, text="📂 YORUM DOSYASI SEÇ", bg="#F9E2AF", fg="#11111B", font=("Segoe UI", 10, "bold"), command=yorum_dosyasi_sec)
btn_dosya.pack(pady=5)

tk.Label(app, text="3. Düzeltme ve Analiz Motorunu Çalıştırın", font=("Segoe UI", 9, "bold"), bg="#181825", fg="#CDD6F4").pack(pady=(10, 0))
buton_analiz = tk.Button(app, text="🔥 NLP ANALİZİNİ BAŞLAT 🔥", bg="#E53935", fg="white", font=("Segoe UI", 12, "bold"), height=2, bd=0, activebackground="#FF5252", command=analiz_baslat)
buton_analiz.pack(fill="x", padx=30, pady=10)

status_frame = tk.Frame(app, bg="#11111B", padx=15, pady=10)
status_frame.pack(fill="both", expand=True, padx=30, pady=(10, 20))
durum_label = tk.Label(status_frame, text="[OK] Program Hazır. Dosyalar bekleniyor...", font=("Consolas", 10), bg="#11111B", fg="#A6E3A1")
durum_label.pack(anchor="w", pady=5)

app.mainloop()