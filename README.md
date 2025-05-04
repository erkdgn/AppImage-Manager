# AppImage Manager / AppImage Yönetim

A modern, multilingual graphical interface to easily install, manage, edit, and remove AppImage applications.  
AppImage uygulamalarını kolayca kurmak, yönetmek, düzenlemek ve kaldırmak için modern, çok dilli bir grafik arayüz.

GitHub: [https://github.com/erkdgn/AppImage-Manager](https://github.com/erkdgn/AppImage-Manager)

## English

**AppImage Installer** is a simple graphical tool to install, manage, edit, and remove AppImage applications on your Linux system. It allows you to:

- Add new AppImage applications with custom name and icon
- List all installed applications
- Edit (rename, change AppImage or icon) any installed application
- Remove applications and their files
- Choose interface language (English/Türkçe)

### Features
- No root required (everything is installed in your home directory)
- Simple and modern GTK arayüz
- Multi-language support (English & Turkish)

### Installation

1. Install dependencies:
   ```bash
   sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0
   ```
2. Make the script executable:
   ```bash
   chmod +x appimage_installer.py
   ```
3. Run the application:
   ```bash
   ./appimage_installer.py
   ```

### Usage
- Click **New** to add an AppImage (choose file, icon, and name)
- Select an app and click **Edit** to change its name, AppImage, or icon
- Select an app and click **Delete** to remove it
- Change language from the bottom-right corner

---

## Türkçe

**AppImage Kurulum Aracı**, Linux sisteminizde AppImage uygulamalarını kolayca kurmanızı, düzenlemenizi ve kaldırmanızı sağlayan basit bir grafik arayüzdür. Özellikler:

- Yeni AppImage uygulaması ekleme (isim ve ikon seçimiyle)
- Kurulu uygulamaları listeleme
- Uygulama düzenleme (isim, AppImage veya ikon değiştirme)
- Uygulama ve dosyalarını kaldırma
- Arayüz dilini seçme (Türkçe/English)

### Özellikler
- Root yetkisi gerekmez (her şey ev dizininize kurulur)
- Basit ve modern GTK arayüz
- Çoklu dil desteği (Türkçe & İngilizce)

### Kurulum

1. Gerekli paketleri yükleyin:
   ```bash
   sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0
   ```
2. Scripti çalıştırılabilir yapın:
   ```bash
   chmod +x appimage_installer.py
   ```
3. Uygulamayı başlatın:
   ```bash
   ./appimage_installer.py
   ```

### Kullanım
- **Yeni** ile AppImage ekleyin (dosya, ikon ve isim seçin)
- Bir uygulamayı seçip **Düzenle** ile adını, AppImage veya ikonunu değiştirin
- Bir uygulamayı seçip **Sil** ile kaldırın
- Sağ alt köşeden dili değiştirin

---

**Not:**
- AppImage ve ikon dosyaları `~/App` klasörüne, kısayollar ise `~/.local/share/applications` dizinine kaydedilir.
- Uygulama tamamen açık kaynak ve özgürdür. 