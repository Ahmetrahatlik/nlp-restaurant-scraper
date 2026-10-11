import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import csv
import os
import urllib.parse
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# --- TÜRKİYE'NİN 81 İLİ VE TÜM İLÇELERİ ---
il_ilce_verisi = {
    "Adana": ["Aladağ", "Ceyhan", "Çukurova", "Feke", "İmamoğlu", "Karaisalı", "Karataş", "Kozan", "Pozantı", "Saimbeyli", "Sarıçam", "Seyhan", "Tufanbeyli", "Yumurtalık", "Yüreğir"],
    "Adıyaman": ["Besni", "Çelikhan", "Gerger", "Gölbaşı", "Kahta", "Merkez", "Samsat", "Sincik", "Tut"],
    "Afyonkarahisar": ["Başmakçı", "Bayat", "Bolvadin", "Çay", "Çobanlar", "Dazkırı", "Dinar", "Emirdağ", "Evciler", "Hocalar", "İhsaniye", "İscehisar", "Kızılören", "Merkez", "Sandıklı", "Sinanpaşa", "Sultandağı", "Şuhut"],
    "Ağrı": ["Diyadin", "Doğubayazıt", "Eleşkirt", "Hamur", "Merkez", "Patnos", "Taşlıçay", "Tutak"],
    "Amasya": ["Göynücek", "Gümüşhacıköy", "Hamamözü", "Merkez", "Merzifon", "Suluova", "Taşova"],
    "Ankara": ["Akyurt", "Altındağ", "Ayaş", "Bala", "Beypazarı", "Çamlıdere", "Çankaya", "Çubuk", "Elmadağ", "Etimesgut", "Evren", "Gölbaşı", "Güdül", "Haymana", "Kahramankazan", "Kalecik", "Keçiören", "Kızılcahamam", "Mamak", "Nallıhan", "Polatlı", "Pursaklar", "Sincan", "Şereflikoçhisar", "Yenimahalle"],
    "Antalya": ["Akseki", "Aksu", "Alanya", "Demre", "Döşemealtı", "Elmalı", "Finike", "Gazipaşa", "Gündoğmuş", "İbradı", "Kaş", "Kemer", "Kepez", "Konyaaltı", "Korkuteli", "Kumluca", "Manavgat", "Muratpaşa", "Serik"],
    "Artvin": ["Ardanuç", "Arhavi", "Borçka", "Hopa", "Kemalpaşa", "Merkez", "Murgul", "Şavşat", "Yusufeli"],
    "Aydın": ["Bozdoğan", "Buharkent", "Çine", "Didim", "Efeler", "Germencik", "İncirliova", "Karacasu", "Karpuzlu", "Koçarlı", "Köşk", "Kuşadası", "Kuyucak", "Nazilli", "Söke", "Sultanhisar", "Yenipazar"],
    "Balıkesir": ["Altıeylül", "Ayvalık", "Balya", "Bandırma", "Bigadiç", "Burhaniye", "Dursunbey", "Edremit", "Erdek", "Gömeç", "Gönen", "Havran", "İvrindi", "Karesi", "Kepsut", "Manyas", "Marmara", "Savaştepe", "Sındırgı", "Susurluk"],
    "Bilecik": ["Bozüyük", "Gölpazarı", "İnhisar", "Merkez", "Osmaneli", "Pazaryeri", "Söğüt", "Yenipazar"],
    "Bingöl": ["Adaklı", "Genç", "Karlıova", "Kiğı", "Merkez", "Solhan", "Yayladere", "Yedisu"],
    "Bitlis": ["Adilcevaz", "Ahlat", "Güroymak", "Hizan", "Merkez", "Mutki", "Tatvan"],
    "Bolu": ["Dörtdivan", "Gerede", "Göynük", "Kıbrıscık", "Mengen", "Merkez", "Mudurnu", "Seben", "Yeniçağa"],
    "Burdur": ["Ağlasun", "Altınyayla", "Bucak", "Çavdır", "Çeltikçi", "Gölhisar", "Karamanlı", "Kemer", "Merkez", "Tefenni", "Yeşilova"],
    "Bursa": ["Büyükorhan", "Gemlik", "Gürsu", "Harmancık", "İnegöl", "İznik", "Karacabey", "Keles", "Kestel", "Mudanya", "Mustafakemalpaşa", "Nilüfer", "Orhaneli", "Orhangazi", "Osmangazi", "Yenişehir", "Yıldırım"],
    "Çanakkale": ["Ayvacık", "Bayramiç", "Biga", "Bozcaada", "Çan", "Eceabat", "Ezine", "Gelibolu", "Gökçeada", "Lapseki", "Merkez", "Yenice"],
    "Çankırı": ["Atkaracalar", "Bayramören", "Çerkeş", "Eldivan", "Ilgaz", "Kızılırmak", "Korgun", "Kurşunlu", "Merkez", "Orta", "Şabanözü", "Yapraklı"],
    "Çorum": ["Alaca", "Bayat", "Boğazkale", "Dodurga", "İskilip", "Kargı", "Laçin", "Mecitözü", "Merkez", "Oğuzlar", "Ortaköy", "Osmancık", "Sungurlu", "Uğurludağ"],
    "Denizli": ["Acıpayam", "Babadağ", "Baklan", "Bekilli", "Beyağaç", "Bozkurt", "Buldan", "Çal", "Çameli", "Çardak", "Çivril", "Güney", "Honaz", "Kale", "Merkezefendi", "Pamukkale", "Sarayköy", "Serinhisar", "Tavas"],
    "Diyarbakır": ["Bağlar", "Bismil", "Çermik", "Çınar", "Çüngüş", "Dicle", "Eğil", "Ergani", "Hani", "Hazro", "Kayapınar", "Kocaköy", "Kulp", "Lice", "Silvan", "Sur", "Yenişehir"],
    "Edirne": ["Enez", "Havsa", "İpsala", "Keşan", "Lalapaşa", "Meriç", "Merkez", "Süloğlu", "Uzunköprü"],
    "Elazığ": ["Ağın", "Alacakaya", "Arıcak", "Baskil", "Karakoçan", "Keban", "Kovancılar", "Maden", "Merkez", "Palu", "Sivrice"],
    "Erzincan": ["Çayırlı", "İliç", "Kemah", "Kemaliye", "Merkez", "Otlukbeli", "Refahiye", "Tercan", "Üzümlü"],
    "Erzurum": ["Aşkale", "Aziziye", "Çat", "Hınıs", "Horasan", "İspir", "Karaçoban", "Karayazı", "Köprüköy", "Narman", "Oltu", "Olur", "Palandöken", "Pasinler", "Pazaryolu", "Şenkaya", "Tekman", "Tortum", "Uzundere", "Yakutiye"],
    "Eskişehir": ["Alpu", "Beylikova", "Çifteler", "Günyüzü", "Han", "İnönü", "Mahmudiye", "Mihalgazi", "Mihalıççık", "Odunpazarı", "Sarıcakaya", "Seyitgazi", "Sivrihisar", "Tepebaşı"],
    "Gaziantep": ["Araban", "İslahiye", "Karkamış", "Nizip", "Nurdağı", "Oğuzeli", "Şahinbey", "Şehitkamil", "Yavuzeli"],
    "Giresun": ["Alucra", "Bulancak", "Çamoluk", "Çanakçı", "Dereli", "Doğankent", "Espiye", "Eynesil", "Görele", "Güce", "Keşap", "Merkez", "Piraziz", "Şebinkarahisar", "Tirebolu", "Yağlıdere"],
    "Gümüşhane": ["Kelkit", "Köse", "Kürtün", "Merkez", "Şiran", "Torul"],
    "Hakkari": ["Çukurca", "Derecik", "Merkez", "Şemdinli", "Yüksekova"],
    "Hatay": ["Altınözü", "Antakya", "Arsuz", "Belen", "Defne", "Dörtyol", "Erzin", "Hassa", "İskenderun", "Kırıkhan", "Kumlu", "Payas", "Reyhanlı", "Samandağ", "Yayladağı"],
    "Isparta": ["Aksu", "Atabey", "Eğirdir", "Gelendost", "Gönen", "Keçiborlu", "Merkez", "Senirkent", "Sütçüler", "Şarkikaraağaç", "Uluborlu", "Yalvaç", "Yenişarbademli"],
    "Mersin": ["Akdeniz", "Anamur", "Aydıncık", "Bozyazı", "Çamlıyayla", "Erdemli", "Gülnar", "Mezitli", "Mut", "Silifke", "Tarsus", "Toroslar", "Yenişehir"],
    "İstanbul": ["Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler", "Bakırköy", "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü", "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy", "Esenler", "Esenyurt", "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kadıköy", "Kağıthane", "Kartal", "Küçükçekmece", "Maltepe", "Pendik", "Sancaktepe", "Sarıyer", "Silivri", "Sultanbeyli", "Sultangazi", "Şile", "Şişli", "Tuzla", "Ümraniye", "Üsküdar", "Zeytinburnu"],
    "İzmir": ["Aliağa", "Balçova", "Bayındır", "Bayraklı", "Bergama", "Beydağ", "Bornova", "Buca", "Çeşme", "Çiğli", "Dikili", "Foça", "Gaziemir", "Güzelbahçe", "Karabağlar", "Karaburun", "Karşıyaka", "Kemalpaşa", "Kınık", "Kiraz", "Konak", "Menderes", "Menemen", "Narlıdere", "Ödemiş", "Seferihisar", "Selçuk", "Tire", "Torbalı", "Urla"],
    "Kars": ["Akyaka", "Arpaçay", "Digor", "Kağızman", "Merkez", "Sarıkamış", "Selim", "Susuz"],
    "Kastamonu": ["Abana", "Ağlı", "Araç", "Azdavay", "Bozkurt", "Cide", "Çatalzeytin", "Daday", "Devrekani", "Doğanyurt", "Hanönü", "İhsangazi", "İnebolu", "Küre", "Merkez", "Pınarbaşı", "Seydiler", "Şenpazar", "Taşköprü", "Tosya"],
    "Kayseri": ["Akkışla", "Bünyan", "Develi", "Felahiye", "Hacılar", "İncesu", "Kocasinan", "Melikgazi", "Özvatan", "Pınarbaşı", "Sarıoğlan", "Sarız", "Talas", "Tomarza", "Yahyalı", "Yeşilhisar"],
    "Kırklareli": ["Babaeski", "Demirköy", "Kofçaz", "Lüleburgaz", "Merkez", "Pehlivanköy", "Pınarhisar", "Vize"],
    "Kırşehir": ["Akçakent", "Akpınar", "Boztepe", "Çiçekdağı", "Kaman", "Merkez", "Mucur"],
    "Kocaeli": ["Başiskele", "Çayırova", "Darıca", "Derince", "Dilovası", "Gebze", "Gölcük", "İzmit", "Kandıra", "Karamürsel", "Kartepe", "Körfez"],
    "Konya": ["Ahırlı", "Akören", "Akşehir", "Altınekin", "Beyşehir", "Bozkır", "Cihanbeyli", "Çeltik", "Çumra", "Derbent", "Derebucak", "Doğanhisar", "Emirgazi", "Ereğli", "Güneysınır", "Hadim", "Halkapınar", "Hüyük", "Ilgın", "Kadınhanı", "Karapınar", "Karatay", "Kulu", "Meram", "Sarayönü", "Selçuklu", "Seydişehir", "Taşkent", "Tuzlukçu", "Yalıhüyük", "Yunak"],
    "Kütahya": ["Altıntaş", "Aslanapa", "Çavdarhisar", "Domaniç", "Dumlupınar", "Emet", "Gediz", "Hisarcık", "Merkez", "Pazarlar", "Şaphane", "Simav", "Tavşanlı"],
    "Malatya": ["Akçadağ", "Arapgir", "Arguvan", "Battalgazi", "Darende", "Doğanşehir", "Doğanyol", "Hekimhan", "Kale", "Kuluncak", "Pütürge", "Yazıhan", "Yeşilyurt"],
    "Manisa": ["Ahmetli", "Akhisar", "Alaşehir", "Demirci", "Gölmarmara", "Gördes", "Kırkağaç", "Köprübaşı", "Kula", "Salihli", "Sarıgöl", "Saruhanlı", "Selendi", "Soma", "Şehzadeler", "Turgutlu", "Yunusemre"],
    "Kahramanmaraş": ["Afşin", "Andırın", "Çağlayancerit", "Dulkadiroğlu", "Ekinözü", "Elbistan", "Göksun", "Nurhak", "Onikişubat", "Pazarcık", "Türkoğlu"],
    "Mardin": ["Artuklu", "Dargeçit", "Derik", "Kızıltepe", "Mazıdağı", "Midyat", "Nusaybin", "Ömerli", "Savur", "Yeşilli"],
    "Muğla": ["Bodrum", "Dalaman", "Datça", "Fethiye", "Kavaklıdere", "Köyceğiz", "Marmaris", "Menteşe", "Milas", "Ortaca", "Seydikemer", "Ula", "Yatağan"],
    "Muş": ["Bulanık", "Hasköy", "Korkut", "Malazgirt", "Merkez", "Varto"],
    "Nevşehir": ["Acıgöl", "Avanos", "Derinkuyu", "Gülşehir", "Hacıbektaş", "Kozaklı", "Merkez", "Ürgüp"],
    "Niğde": ["Altunhisar", "Bor", "Çamardı", "Çiftlik", "Merkez", "Ulukışla"],
    "Ordu": ["Akkuş", "Altınordu", "Aybastı", "Çamaş", "Çatalpınar", "Çaybaşı", "Fatsa", "Gölköy", "Gülyalı", "Gürgentepe", "İkizce", "Kabadüz", "Kabataş", "Korgan", "Kumru", "Mesudiye", "Perşembe", "Ulubey", "Ünye"],
    "Rize": ["Ardeşen", "Çamlıhemşin", "Çayeli", "Derepazarı", "Fındıklı", "Güneysu", "Hemşin", "İkizdere", "İyidere", "Kalkandere", "Merkez", "Pazar"],
    "Sakarya": ["Adapazarı", "Akyazı", "Arifiye", "Erenler", "Ferizli", "Geyve", "Hendek", "Karapürçek", "Karasu", "Kaynarca", "Kocaali", "Pamukova", "Sapanca", "Serdivan", "Söğütlü", "Taraklı"],
    "Samsun": ["19 Mayıs", "Alaçam", "Asarcık", "Atakum", "Ayvacık", "Bafra", "Canik", "Çarşamba", "Havza", "İlkadım", "Kavak", "Ladik", "Salıpazarı", "Tekkeköy", "Terme", "Vezirköprü", "Yakakent"],
    "Siirt": ["Baykan", "Eruh", "Kurtalan", "Merkez", "Pervari", "Şirvan", "Tillo"],
    "Sinop": ["Ayancık", "Boyabat", "Dikmen", "Durağan", "Erfelek", "Gerze", "Merkez", "Saraydüzü", "Türkeli"],
    "Sivas": ["Akıncılar", "Altınyayla", "Divriği", "Doğanşar", "Gemerek", "Gölova", "Gürün", "Hafik", "İmranlı", "Kangal", "Koyulhisar", "Merkez", "Suşehri", "Şarkışla", "Ulaş", "Yıldızeli", "Zara"],
    "Tekirdağ": ["Çerkezköy", "Çorlu", "Ergene", "Hayrabolu", "Kapaklı", "Malkara", "Marmaraereğlisi", "Muratlı", "Saray", "Süleymanpaşa", "Şarköy"],
    "Tokat": ["Almus", "Artova", "Başçiftlik", "Erbaa", "Merkez", "Niksar", "Pazar", "Reşadiye", "Sulusaray", "Turhal", "Yeşilyurt", "Zile"],
    "Trabzon": ["Akçaabat", "Araklı", "Arsin", "Beşikdüzü", "Çarşıbaşı", "Çaykara", "Dernekpazarı", "Düzköy", "Hayrat", "Köprübaşı", "Maçka", "Of", "Ortahisar", "Sürmene", "Şalpazarı", "Tonya", "Vakfıkebir", "Yomra"],
    "Tunceli": ["Çemişgezek", "Hozat", "Mazgirt", "Merkez", "Nazımiye", "Ovacık", "Pertek", "Pülümür"],
    "Şanlıurfa": ["Akçakale", "Birecik", "Bozova", "Ceylanpınar", "Eyyübiye", "Halfeti", "Haliliye", "Harran", "Hilvan", "Karaköprü", "Siverek", "Suruç", "Viranşehir"],
    "Uşak": ["Banaz", "Eşme", "Karahallı", "Merkez", "Sivaslı", "Ulubey"],
    "Van": ["Bahçesaray", "Başkale", "Çaldıran", "Çatak", "Edremit", "Erciş", "Gevaş", "Gürpınar", "İpekyolu", "Muradiye", "Özalp", "Saray", "Tuşba"],
    "Yozgat": ["Akdağmadeni", "Aydıncık", "Boğazlıyan", "Çandır", "Çayıralan", "Çekerek", "Kadışehri", "Merkez", "Saraykent", "Sarıkaya", "Sorgun", "Şefaatli", "Yenifakılı", "Yerköy"],
    "Zonguldak": ["Alaplı", "Çaycuma", "Devrek", "Ereğli", "Gökçebey", "Kilimli", "Kozlu", "Merkez"],
    "Aksaray": ["Ağaçören", "Eskil", "Gülağaç", "Güzelyurt", "Merkez", "Ortaköy", "Sarıyahşi", "Sultanhanı"],
    "Bayburt": ["Aydıntepe", "Demirözü", "Merkez"],
    "Karaman": ["Ayrancı", "Başyayla", "Ermenek", "Kazımkarabekir", "Merkez", "Sarıveliler"],
    "Kırıkkale": ["Bahşılı", "Balışeyh", "Çelebi", "Delice", "Karakeçili", "Keskin", "Merkez", "Sulakyurt", "Yahşihan"],
    "Batman": ["Beşiri", "Gercüş", "Hasankeyf", "Kozluk", "Merkez", "Sason"],
    "Şırnak": ["Beytüşşebap", "Cizre", "Güçlükonak", "İdil", "Merkez", "Silopi", "Uludere"],
    "Bartın": ["Amasra", "Kurucaşile", "Merkez", "Ulus"],
    "Ardahan": ["Çıldır", "Damal", "Göle", "Hanak", "Merkez", "Posof"],
    "Iğdır": ["Aralık", "Karakoyunlu", "Merkez", "Tuzluca"],
    "Yalova": ["Altınova", "Armutlu", "Çınarcık", "Çiftlikköy", "Merkez", "Termal"],
    "Karabük": ["Eflani", "Eskipazar", "Merkez", "Ovacık", "Safranbolu", "Yenice"],
    "Kilis": ["Elbeyli", "Merkez", "Musabeyli", "Polateli"],
    "Osmaniye": ["Bahçe", "Düziçi", "Hasanbeyli", "Kadirli", "Merkez", "Sumbas", "Toprakkale"],
    "Düzce": ["Akçakoca", "Cumayeri", "Çilimli", "Gölyaka", "Gümüşova", "Kaynaşlı", "Merkez", "Yığılca"]
}

# Genişletilmiş Kategoriler
kategoriler = [
    "Kebap & Et", "Dönerci", "Pide & Lahmacun", "Fast Food", "Pizza", 
    "Ev Yemekleri & Lokanta", "Çorbacı", "Tatlı & Pastane", 
    "Kafe & Kahvaltı", "Deniz Ürünleri", "Çiğ Köfteci", 
    "Börekçi", "Meyhane & Eğlence", "Uzak Doğu & Sushi"
]

def ilce_guncelle(event):
    secilen_il = il_var.get()
    ilce_cb['values'] = il_ilce_verisi.get(secilen_il, [])
    ilce_cb.set('') 

def arayuze_yaz(metin):
    app.after(0, lambda: durum_label.config(text=metin))

def verileri_cek_motoru(il, ilce, kategori, hedef_sayi):
    arayuze_yaz(">> Tarayıcı arka planda (sessiz mod) başlatılıyor...")
    
    edge_options = Options()
    edge_options.add_argument("--headless=new") 
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--window-size=1920,1080")
    edge_options.add_argument("--lang=tr-TR") 
    edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    toplanan_veriler = []
    driver = None
    
    try:
        driver = webdriver.Edge(options=edge_options)
        wait = WebDriverWait(driver, 15)
        
        arama_metni = f"{il} {ilce} {kategori} restoranları"
        url = f"https://www.google.com/maps/search/{urllib.parse.quote(arama_metni)}"
        
        arayuze_yaz(f">> Google'da aranıyor: {arama_metni}")
        driver.get(url)
        
        arayuze_yaz(">> Restoranlar listesi bekleniyor...")
        ilk_restoran = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/maps/place/']")))
        restoran_adi = ilk_restoran.get_attribute("aria-label") or "Bilinmeyen Restoran"
        
        arayuze_yaz(f">> Hedef Bulundu: {restoran_adi} | Giriş yapılıyor...")
        ilk_restoran.click()
        time.sleep(4) 
        
        arayuze_yaz(">> Yorumlar sekmesi taranıyor...")
        try:
            yorum_sekmesi = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Yorumlar') or contains(@aria-label, 'Değerlendirmeler') or contains(., 'Yorumlar')]")))
            driver.execute_script("arguments[0].click();", yorum_sekmesi) 
        except:
            arayuze_yaz("[!] Hata: Bu mekanın yorum sekmesi bulunamadı.")
            return False, 0
            
        time.sleep(3)
        arayuze_yaz(">> Gerçek yorumlar çekiliyor, lütfen bekleyin...")
        
        cekilen = 0
        deneme_sayisi = 0
        
        while cekilen < hedef_sayi and deneme_sayisi < 30:
            yorum_elementleri = driver.find_elements(By.CLASS_NAME, "wiI7pd")
            
            for yorum in yorum_elementleri[cekilen:]: 
                metin = yorum.text.strip()
                if metin: 
                    cekilen += 1
                    toplanan_veriler.append([cekilen, restoran_adi, metin])
                    arayuze_yaz(f"İndirilen Yorum: [{cekilen}/{hedef_sayi}]")
                    
                if cekilen >= hedef_sayi:
                    break
                    
            if cekilen >= hedef_sayi:
                break
                
            try:
                aktif_alan = driver.switch_to.active_element
                aktif_alan.send_keys(Keys.PAGE_DOWN)
                aktif_alan.send_keys(Keys.PAGE_DOWN)
                time.sleep(1.5)
            except:
                pass
                
            deneme_sayisi += 1

        if toplanan_veriler:
            arayuze_yaz(">> Veriler Excel formatına dönüştürülüyor...")
            dosya_adi = f"Yorumlar_{il}_{ilce}_{kategori.replace(' ', '_')}.csv"
            with open(dosya_adi, mode='w', newline='', encoding='utf-8-sig') as f:
                yazici = csv.writer(f, delimiter=';')
                yazici.writerow(["Yorum No", "Restoran Adı", "Yorum Metni"])
                yazici.writerows(toplanan_veriler)
            return True, len(toplanan_veriler)
        else:
            return False, 0
            
    except Exception as e:
        arayuze_yaz(f"[!] Hata oluştu veya Google bağlantıyı kesti.")
        return False, 0
    finally:
        if driver:
            driver.quit()

def baslat():
    il, ilce, kat, sayi_str = il_var.get(), ilce_var.get(), kategori_var.get(), yorum_var.get()

    if not all([il, ilce, kat, sayi_str]):
        messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun!")
        return
        
    try:
        hedef_sayi = int(sayi_str)
    except ValueError:
        messagebox.showerror("Hata", "Yorum sayısına geçerli bir rakam giriniz!")
        return

    def calistir():
        buton.config(state=tk.DISABLED, bg="#4CAF50", text="VERİ ÇEKİMİ DEVAM EDİYOR...")
        basari, adet = verileri_cek_motoru(il, ilce, kat, hedef_sayi)
        
        if basari:
            klasor_yolu = os.getcwd()
            arayuze_yaz(f"✔ İŞLEM TAMAM: {adet} adet yorum Excel'e kaydedildi.")
            messagebox.showinfo("Görev Başarılı!", f"{adet} adet veri klasörünüze kaydedildi.\nKonum: {klasor_yolu}")
        else:
            arayuze_yaz("✖ İŞLEM BAŞARISIZ OLDU.")
            messagebox.showerror("Hata", "İşlem tamamlanamadı. Mekan bulunamamış veya internet kopmuş olabilir.")
            
        buton.config(state=tk.NORMAL, bg="#00E676", text="VERİLERİ ÇEK")

    threading.Thread(target=calistir, daemon=True).start()

# ==========================================
# --- ARAYÜZ (GUI) - PREMIUM TASARIM ---
# ==========================================
app = tk.Tk()
app.title("PRO Yorum Botu v6.0")
app.geometry("450x650")
app.configure(bg="#1E1E2E") # Modern Dark Theme Arka Plan

# Fontlar ve Renkler
RENK_BG = "#1E1E2E"
RENK_KART = "#313244"
RENK_YAZI = "#CDD6F4"
RENK_VURGU = "#89B4FA"
FONT_BASLIK = ("Segoe UI", 16, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_GIRDI = ("Segoe UI", 11)

# Tkinter'ın içindeki Combobox'ları dark moda uyumlu yapmak için ufak bir stil ayarı
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground="#45475A", background="#313244", foreground="white", bordercolor="#1E1E2E")
style.configure("TEntry", fieldbackground="#45475A", foreground="white", bordercolor="#1E1E2E")

# Üst Başlık Bölümü
header_frame = tk.Frame(app, bg=RENK_BG, pady=15)
header_frame.pack(fill="x")
tk.Label(header_frame, text="📍 GOOGLE HARİTALAR BOTU", font=FONT_BASLIK, bg=RENK_BG, fg="#F5C2E7").pack()
tk.Label(header_frame, text="Tüm Türkiye - Otomatik Veri Çekici", font=("Segoe UI", 9), bg=RENK_BG, fg="#A6ADC8").pack()

# Form Kartı (Koyu Gri Alan)
form_frame = tk.Frame(app, bg=RENK_KART, padx=25, pady=20, highlightthickness=1, highlightbackground="#45475A")
form_frame.pack(fill="x", padx=25, pady=10)

tk.Label(form_frame, text="Şehir:", font=FONT_LABEL, bg=RENK_KART, fg=RENK_VURGU).pack(anchor="w")
il_var = tk.StringVar()
il_cb = ttk.Combobox(form_frame, textvariable=il_var, values=sorted(list(il_ilce_verisi.keys())), state="readonly", font=FONT_GIRDI)
il_cb.pack(fill="x", pady=(5, 15))
il_cb.bind("<<ComboboxSelected>>", ilce_guncelle)

tk.Label(form_frame, text="İlçe:", font=FONT_LABEL, bg=RENK_KART, fg=RENK_VURGU).pack(anchor="w")
ilce_var = tk.StringVar()
ilce_cb = ttk.Combobox(form_frame, textvariable=ilce_var, state="readonly", font=FONT_GIRDI)
ilce_cb.pack(fill="x", pady=(5, 15))

tk.Label(form_frame, text="Kategori:", font=FONT_LABEL, bg=RENK_KART, fg=RENK_VURGU).pack(anchor="w")
kategori_var = tk.StringVar()
kategori_cb = ttk.Combobox(form_frame, textvariable=kategori_var, values=kategoriler, state="readonly", font=FONT_GIRDI)
kategori_cb.pack(fill="x", pady=(5, 15))

tk.Label(form_frame, text="Çekilecek Yorum Sayısı (Örn: 50):", font=FONT_LABEL, bg=RENK_KART, fg=RENK_VURGU).pack(anchor="w")
yorum_var = tk.StringVar()
ttk.Entry(form_frame, textvariable=yorum_var, font=FONT_GIRDI).pack(fill="x", pady=(5, 10))

# Aksiyon Butonu
buton = tk.Button(app, text="VERİLERİ ÇEK", bg="#00E676", fg="#11111B", font=("Segoe UI", 12, "bold"), height=2, bd=0, activebackground="#B5E8B0", command=baslat)
buton.pack(fill="x", padx=25, pady=(10, 20))

# Konsol / Durum Paneli (En Alt Siyah Alan)
status_frame = tk.Frame(app, bg="#11111B", padx=15, pady=15)
status_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))

tk.Label(status_frame, text="SİSTEM DURUMU", font=("Consolas", 10, "bold"), bg="#11111B", fg="#F38BA8").pack(anchor="w")
durum_label = tk.Label(status_frame, text="[OK] Motor Hazır. 81 İl Yüklendi.", font=("Consolas", 10), bg="#11111B", fg="#A6E3A1", wraplength=350, justify="left")
durum_label.pack(anchor="w", pady=(10, 0))

app.mainloop()