import os, time, re, urllib.parse, sys
import pandas as pd
from playwright.sync_api import sync_playwright

if len(sys.argv) < 3:
    print("HATA: Eksik parametre! Örnek: python vakum.py Kars 1")
    sys.exit()

hedef_sehir = sys.argv[1]
profil_no = sys.argv[2]

excel_dosyasi = f"{hedef_sehir}_Mekanlar_Yorumlu.xlsx" 
profil_yolu = os.path.join(os.path.expanduser("~"), "Desktop", f"google_profil_bot_{profil_no}")

def tarihi_kontrol_et(tarih_metni):
    tarih_metni = tarih_metni.lower()
    if "yıl" in tarih_metni or "sene" in tarih_metni:
        sayilar = re.findall(r'\d+', tarih_metni)
        if sayilar and int(sayilar[0]) > 5: return False
    return True

def yorumlari_cek(restoran_adi, page):
    try:
        search_query = f"{restoran_adi} {hedef_sehir}"
        url = f"https://www.google.com/maps/search/{urllib.parse.quote(search_query)}?hl=tr"
        
        page.goto(url)
        time.sleep(10) 

        try:
            yorum_sekmesi = page.locator("div[role='tab']:has-text('Yorumlar'), button[role='tab']:has-text('Yorumlar')").first
            if yorum_sekmesi.count() > 0 and yorum_sekmesi.is_visible():
                yorum_sekmesi.click(timeout=5000)
                time.sleep(5)
            else:
                ilk_sonuc = page.locator("a.hfpxzc").first
                if ilk_sonuc.count() > 0:
                    ilk_sonuc.click(timeout=10000)
                    time.sleep(6)
                
                page.locator("button[aria-label*='Yorum'], button[aria-label*='Reviews'], button:has-text('Yorumlar')").first.click(timeout=10000)
                time.sleep(6)
        except: pass

        siralama_basarili = False
        try:
            sort_btn = page.locator("button:has-text('Sırala'), button[aria-label*='Sırala']").first
            sort_btn.wait_for(state="visible", timeout=15000)
            sort_btn.click()
            time.sleep(3)
            
            newest_btn = page.locator("div[role='menuitemradio']:has-text('En yeni')").first
            newest_btn.wait_for(state="visible", timeout=10000)
            newest_btn.click()
            time.sleep(6) 
            siralama_basarili = True
        except: 
            pass

        try:
            page.wait_for_selector(".jftiEf", timeout=15000)
        except:
            return []

        cekilen_yorumlar = set()
        eski_yorum_sayaci = 0 
        bos_kaydirma = 0
        
        # =========================================================
        # İŞTE KODU UÇURAN HAFIZA (HAMALLIK BİTTİ)
        # =========================================================
        islenen_kart_sayisi = 0 
        
        for i in range(1500): 
            if eski_yorum_sayaci >= 15: 
                break
            
            kartlar = page.query_selector_all(".jftiEf")
            onceki_sayi = len(cekilen_yorumlar)
            
            # SADECE YENİ EKLENEN KARTLARI TARA! (Eskileri es geç)
            yeni_kartlar = kartlar[islenen_kart_sayisi:]
            
            for kart in yeni_kartlar:
                try:
                    btn = kart.query_selector("button.w8nwRe, button:has-text('Daha fazla')")
                    if btn: btn.evaluate("node => node.click()") 
                except: pass

                try:
                    t_el = kart.query_selector(".rsqaWe, .dehysf")
                    if t_el:
                        tarih_tamam = tarihi_kontrol_et(t_el.inner_text())
                        if not tarih_tamam:
                            eski_yorum_sayaci += 1
                            continue 
                        else:
                            eski_yorum_sayaci = 0 
                            
                    m_el = kart.query_selector(".wiI7pd, .fzWsFe")
                    if m_el:
                        metin = m_el.inner_text().replace('\n', ' ').strip()
                        if len(metin) > 3: cekilen_yorumlar.add(metin)
                except: continue

            # Hız kaybetmemek için işlenen kart sayısını güncelle
            islenen_kart_sayisi = len(kartlar)

            if len(cekilen_yorumlar) == onceki_sayi:
                bos_kaydirma += 1
            else:
                bos_kaydirma = 0 

            if kartlar:
                try:
                    son_kart = kartlar[-1]
                    son_kart.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    son_kart.hover()
                    time.sleep(0.2)
                    
                    page.mouse.wheel(0, 3000)
                    page.keyboard.press("PageDown")
                    page.keyboard.press("End")
                except: pass
            
            print(f"    -> {len(cekilen_yorumlar)} yorum çekildi... (Eski Tol: {eski_yorum_sayaci}/15)      ", end="\r")
            time.sleep(3) 
            
            if bos_kaydirma >= 6: break 
                
        return list(cekilen_yorumlar)
    except Exception:
        return []

def baslat():
    if not os.path.exists(excel_dosyasi):
        print(f"Hata: {excel_dosyasi} bulunamadı!")
        return

    df = pd.read_excel(excel_dosyasi)
    restoran_col = 'RESTORAN ADI' if 'RESTORAN ADI' in df.columns else 'RESTURAN ADI'

    dolu_sayisi = 0
    if 'Yorum_Blok_1' in df.columns:
        dolu_sayisi = df['Yorum_Blok_1'].notna().sum()
    
    print(f"\n[🛡️] BOT {profil_no} | ŞEHİR: {hedef_sehir} (IŞIK HIZI MODU) BAŞLATILDI!")
    print(f"[*] {dolu_sayisi} mekan atlanıyor...\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profil_yolu,
            headless=False,
            args=["--blink-settings=imagesEnabled=false"], 
            viewport={'width': 1000, 'height': 800}
        )
        
        def sekmeyi_oldur(yeni_sayfa):
            try: yeni_sayfa.close()
            except: pass
            
        context.on("page", sekmeyi_oldur)
        
        page = context.pages[0]
        
        for index, row in df.iterrows():
            if 'Yorum_Blok_1' in df.columns and pd.notna(row.get('Yorum_Blok_1')) and len(str(row.get('Yorum_Blok_1'))) > 20:
                continue

            mekan = str(row[restoran_col])
            print(f"[{index+1}/{len(df)}] {hedef_sehir} Vakumlanıyor: {mekan}")
            
            yorumlar = yorumlari_cek(mekan, page)
            
            if yorumlar:
                bloklar = []
                mevcut_blok = ""
                for y in yorumlar:
                    if len(mevcut_blok) + len(y) + 3 > 30000:
                        bloklar.append(mevcut_blok)
                        mevcut_blok = y
                    else:
                        mevcut_blok = y if mevcut_blok == "" else mevcut_blok + " | " + y
                if mevcut_blok: bloklar.append(mevcut_blok)

                for i, b_metni in enumerate(bloklar):
                    kolon = f'Yorum_Blok_{i+1}'
                    if kolon not in df.columns: df[kolon] = ""
                    df.at[index, kolon] = b_metni

                try:
                    df.to_excel(excel_dosyasi, index=False)
                    print(f"[*] BAŞARILI: {len(yorumlar)} yorum Excel'e çivilendi.\n")
                except:
                    print("\n[!] HATA: Excel'i kapa!\n")
            else:
                if 'Yorum_Blok_1' not in df.columns: df['Yorum_Blok_1'] = ""
                df.at[index, 'Yorum_Blok_1'] = "Yorum bulunamadı veya hepsi 5 yıldan eski."
                try:
                    df.to_excel(excel_dosyasi, index=False)
                except: pass
                print("[!] Yorum yok veya 5 yıldan eski. (Boş Damgası Vuruldu!)\n")

        context.close()
        print(f"\n[✔] {hedef_sehir.upper()} TAMAMLANDI!")

if __name__ == "__main__":
    baslat()