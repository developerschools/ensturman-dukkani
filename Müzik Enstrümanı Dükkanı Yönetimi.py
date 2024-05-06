import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl
import sqlite3

class Enstruman:
    def __init__(self, adi, stok_miktari):
        self.adi = adi
        self.stok_miktari = stok_miktari

    def kaydet(self):
        conn = sqlite3.connect('enstruman_dukkani.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Enstruman (
                          id INTEGER PRIMARY KEY,
                          adi TEXT NOT NULL,
                          stok_miktari INTEGER NOT NULL)''')
        cursor.execute("INSERT INTO Enstruman (adi, stok_miktari) VALUES (?, ?)", (self.adi, self.stok_miktari))
        conn.commit()
        conn.close()

class Musteri:
    def __init__(self, ad, soyad, telefon, adres, email, siparis_gecmisi=None):
        self.ad = ad
        self.soyad = soyad
        self.telefon = telefon
        self.adres = adres
        self.email = email
        self.siparis_gecmisi = siparis_gecmisi if siparis_gecmisi is not None else []

    def siparis_ekle(self, siparis):
        self.siparis_gecmisi.append(siparis)

    def kaydet(self):
        conn = sqlite3.connect('enstruman_dukkani.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Musteri (
                          id INTEGER PRIMARY KEY,
                          ad TEXT NOT NULL,
                          soyad TEXT NOT NULL,
                          telefon TEXT NOT NULL,
                          adres TEXT NOT NULL,
                          email TEXT NOT NULL)''')
        cursor.execute("INSERT INTO Musteri (ad, soyad, telefon, adres, email) VALUES (?, ?, ?, ?, ?)",
                  (self.ad, self.soyad, self.telefon, self.adres, self.email))
        conn.commit()
        conn.close()

class Satis:
    def __init__(self, musteri, enstrumanlar):
        self.musteri = musteri
        self.enstrumanlar = enstrumanlar

    def kaydet(self):
        conn = sqlite3.connect('enstruman_dukkani.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Satis (
                          id INTEGER PRIMARY KEY,
                          musteri_id INTEGER NOT NULL,
                          enstruman_id INTEGER NOT NULL,
                          FOREIGN KEY (musteri_id) REFERENCES Musteri(id),
                          FOREIGN KEY (enstruman_id) REFERENCES Enstruman(id))''')
        cursor.execute("INSERT INTO Satis (musteri_id, enstruman_id) VALUES (?, ?)",
                  (self.musteri.id, self.enstruman.id))
        conn.commit()
        conn.close()

class DestekTalebi:
    def __init__(self, detaylar):
        self.detaylar = detaylar

    def kaydet(self):
        conn = sqlite3.connect('enstruman_dukkani.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS DestekTalebi (
                          id INTEGER PRIMARY KEY,
                          detaylar TEXT NOT NULL)''')
        cursor.execute("INSERT INTO DestekTalebi (detaylar) VALUES (?)", (self.detaylar,))
        conn.commit()
        conn.close()

class EnstrumanDukkani(QWidget):
    def __init__(self):
        super().__init__()
        self.enstrumanlar = []
        self.setWindowTitle("Müzik Enstrüman Dükkanı Yönetimi")
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)  # Pencere boyutunu ayarla

        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 800, 600)

        # Resmi URL'den çekme
        self.network_manager = QNetworkAccessManager()
        url = QUrl("https://www.do-re.com.tr/istanbul-kadikoy-magazasi-3ea51f7f61ebde5c1c31a6896e2b6035-505eb7f958efdb9bf3fadda8082b4552-large-sp.jpg")
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(self.on_image_download_finished)

        enstruman_ekle_button = QPushButton("Enstrüman Ekle")
        enstruman_ekle_button.clicked.connect(self.open_enstruman_ekle_arayuz)

        satis_yap_button = QPushButton("Satış Yap")
        satis_yap_button.clicked.connect(self.open_satis_yap_arayuz)

        destek_talebi_button = QPushButton("Destek Talebi Oluştur")
        destek_talebi_button.clicked.connect(self.open_destek_talebi_olustur_arayuz)

        main_layout = QHBoxLayout()
        main_layout.addWidget(enstruman_ekle_button)
        main_layout.addWidget(satis_yap_button)
        main_layout.addWidget(destek_talebi_button)

        self.setLayout(main_layout)

    def on_image_download_finished(self):
        reply = self.sender()
        if reply.error():
            print("Image download failed:", reply.errorString())
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            self.background.setPixmap(pixmap)
            self.background.setScaledContents(True)

    def open_enstruman_ekle_arayuz(self):
        self.enstruman_ekle_arayuz = EnstrumanEkleArayuz(self)
        self.enstruman_ekle_arayuz.show()

    def open_satis_yap_arayuz(self):
        self.satis_yap_arayuz = SatisYapArayuz(self)
        self.satis_yap_arayuz.show()

    def open_destek_talebi_olustur_arayuz(self):
        self.destek_talebi_olustur_arayuz = DestekTalebiOlusturArayuz(self)
        self.destek_talebi_olustur_arayuz.show()


class EnstrumanEkleArayuz(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Enstrüman Ekle")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.enstruman_adi_entry = QLineEdit()
        layout.addWidget(QLabel("Enstrüman Adı:"))
        layout.addWidget(self.enstruman_adi_entry)

        self.stok_miktari_entry = QLineEdit()
        layout.addWidget(QLabel("Stok Miktarı:"))
        layout.addWidget(self.stok_miktari_entry)

        enstruman_ekle_button = QPushButton("Enstrüman Ekle")
        enstruman_ekle_button.clicked.connect(self.enstruman_ekle)
        layout.addWidget(enstruman_ekle_button)

        self.setLayout(layout)

    def enstruman_ekle(self):
        adi = self.enstruman_adi_entry.text()
        stok_miktari = self.stok_miktari_entry.text()
        enstruman = Enstruman(adi, stok_miktari)
        enstruman.kaydet()
        QMessageBox.information(self, "Başarılı", "Enstrüman başarıyla eklendi.")


class SatisYapArayuz(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Satış Yap")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.musteri_adi_entry = QLineEdit()
        layout.addWidget(QLabel("Müşteri Adı:"))
        layout.addWidget(self.musteri_adi_entry)

        self.musteri_soyadi_entry = QLineEdit()
        layout.addWidget(QLabel("Müşteri Soyadı:"))
        layout.addWidget(self.musteri_soyadi_entry)

        self.telefon_entry = QLineEdit()
        layout.addWidget(QLabel("Telefon:"))
        layout.addWidget(self.telefon_entry)

        self.adres_entry = QLineEdit()
        layout.addWidget(QLabel("Adres:"))
        layout.addWidget(self.adres_entry)

        self.email_entry = QLineEdit()
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_entry)

        self.enstrumanlar_entry = QLineEdit()
        layout.addWidget(QLabel("Satılan Enstrümanlar:"))
        layout.addWidget(self.enstrumanlar_entry)

        satis_yap_button = QPushButton("Satış Yap")
        satis_yap_button.clicked.connect(self.satis_yap)
        layout.addWidget(satis_yap_button)

        self.setLayout(layout)

    def satis_yap(self):
        musteri_adi = self.musteri_adi_entry.text()
        musteri_soyadi = self.musteri_soyadi_entry.text()
        telefon = self.telefon_entry.text()
        adres = self.adres_entry.text()
        email = self.email_entry.text()
        enstrumanlar = self.enstrumanlar_entry.text()
        
        musteri = Musteri(musteri_adi, musteri_soyadi, telefon, adres, email)
        satis = Satis(musteri, enstrumanlar)
        
        # Müşteriye sipariş ekle
        musteri.kaydet()
        satis.kaydet()
        
        QMessageBox.information(self, "Başarılı", "Satış gerçekleştirildi.")


class DestekTalebiOlusturArayuz(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Destek Talebi Oluştur")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.detaylar_entry = QLineEdit()
        layout.addWidget(QLabel("Destek Talebi Detayları:"))
        layout.addWidget(self.detaylar_entry)

        destek_talebi_button = QPushButton("Talep Oluştur")
        destek_talebi_button.clicked.connect(self.destek_talebi_olustur)
        layout.addWidget(destek_talebi_button)

        self.setLayout(layout)

    def destek_talebi_olustur(self):
        detaylar = self.detaylar_entry.text()
        talep = DestekTalebi(detaylar)
        talep.kaydet()
        QMessageBox.information(self, "Başarılı", "Destek talebiniz oluşturuldu.")


if __name__ == "__main__":
    conn = sqlite3.connect('enstruman_dukkani.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Enstruman (
                      id INTEGER PRIMARY KEY,
                      adi TEXT NOT NULL,
                      stok_miktari INTEGER NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Musteri (
                      id INTEGER PRIMARY KEY,
                      ad TEXT NOT NULL,
                      soyad TEXT NOT NULL,
                      telefon TEXT NOT NULL,
                      adres TEXT NOT NULL,
                      email TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Satis (
                      id INTEGER PRIMARY KEY,
                      musteri_id INTEGER NOT NULL,
                      enstruman_id INTEGER NOT NULL,
                      FOREIGN KEY (musteri_id) REFERENCES Musteri(id),
                      FOREIGN KEY (enstruman_id) REFERENCES Enstruman(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS DestekTalebi (
                      id INTEGER PRIMARY KEY,
                      detaylar TEXT NOT NULL)''')
    conn.commit()
    conn.close()

    app = QApplication(sys.argv)
    pencere = EnstrumanDukkani()
    pencere.show()
    sys.exit(app.exec_())
