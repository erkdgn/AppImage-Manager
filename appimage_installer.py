#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
import gi
import urllib.request
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class AppImageInstaller:
    LOBEHUB_ICONS = [
        # (isim, url)
        ("openai", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/openai.png"),
        ("claude", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/claude.png"),
        ("gemini", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/gemini.png"),
        ("ollama", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/ollama.png"),
        ("microsoft", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/microsoft.png"),
        ("meta", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/meta.png"),
        ("midjourney", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/midjourney.png"),
        ("mistral", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/mistral.png"),
        ("stability", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/stability.png"),
        ("huggingface", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/huggingface.png"),
        ("dalle", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/dalle.png"),
        ("copilot", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/copilot.png"),
        ("perplexity", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/perplexity.png"),
        ("google", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/google.png"),
        ("grok", "https://cdn.jsdelivr.net/gh/lobehub/assets@main/icons/ai/grok.png"),
    ]

    LANGS = {
        'tr': {
            'title': 'AppImage Yönetim',
            'installed_apps': 'Kurulu Uygulamalar',
            'edit': 'Düzenle',
            'delete': 'Sil',
            'new': 'Yeni',
            'app_name': 'Uygulama Adı:',
            'appimage_file': 'AppImage Dosyası:',
            'icon_file': 'İkon Dosyası:',
            'select': 'Seç',
            'install': 'Kur',
            'cancel': 'İptal',
            'save': 'Kaydet',
            'fill_all': 'Lütfen tüm alanları doldurun!',
            'install_success': 'Kurulum başarıyla tamamlandı!',
            'delete_success': 'Uygulama başarıyla silindi!',
            'delete_error': 'Silme sırasında hata oluştu:',
            'install_error': 'Kurulum sırasında hata oluştu:',
            'edit_title': 'Uygulama Düzenle',
            'new_title': 'Yeni AppImage Ekle',
        },
        'en': {
            'title': 'AppImage Manager',
            'installed_apps': 'Installed Applications',
            'edit': 'Edit',
            'delete': 'Delete',
            'new': 'New',
            'app_name': 'Application Name:',
            'appimage_file': 'AppImage File:',
            'icon_file': 'Icon File:',
            'select': 'Select',
            'install': 'Install',
            'cancel': 'Cancel',
            'save': 'Save',
            'fill_all': 'Please fill all fields!',
            'install_success': 'Installation completed successfully!',
            'delete_success': 'Application deleted successfully!',
            'delete_error': 'Error while deleting:',
            'install_error': 'Error during installation:',
            'edit_title': 'Edit Application',
            'new_title': 'Add New AppImage',
        }
    }

    def __init__(self):
        import locale
        try:
            sys_lang = locale.getlocale()[0]
        except Exception:
            sys_lang = None
        self.lang = 'tr' if sys_lang and sys_lang.startswith('tr') else 'en'
        self.t = self.LANGS[self.lang]
        self.ensure_lobehub_icons()
        self.window = Gtk.Window(title=self.t['title'])
        self.window.set_default_size(600, 400)
        self.window.connect("destroy", Gtk.main_quit)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        self.window.add(vbox)

        # Uygulama listesi (tek seçimli)
        self.app_liststore = Gtk.ListStore(str, str)  # (Uygulama Adı, Desktop Dosyası Yolu)
        self.load_applications()
        self.treeview = Gtk.TreeView(model=self.app_liststore)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        renderer = Gtk.CellRendererText()
        self.column = Gtk.TreeViewColumn(self.t['installed_apps'], renderer, text=0)
        self.treeview.append_column(self.column)
        self.treeview.get_selection().connect("changed", self.on_app_selected)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(200)
        scrolled.add(self.treeview)
        vbox.pack_start(scrolled, True, True, 0)

        # Butonlar
        button_box = Gtk.Box(spacing=10)
        self.edit_button = Gtk.Button(label=self.t['edit'])
        self.edit_button.set_sensitive(False)
        self.edit_button.connect("clicked", self.edit_selected_app)
        button_box.pack_start(self.edit_button, False, True, 0)
        self.delete_button = Gtk.Button(label=self.t['delete'])
        self.delete_button.set_sensitive(False)
        self.delete_button.connect("clicked", self.delete_selected_app)
        button_box.pack_start(self.delete_button, False, True, 0)
        self.new_button = Gtk.Button(label=self.t['new'])
        self.new_button.connect("clicked", self.new_appimage_dialog)
        button_box.pack_start(self.new_button, False, True, 0)
        vbox.pack_start(button_box, False, True, 0)

        # Dil seçici sağ alt
        lang_align = Gtk.Alignment.new(1.0, 1.0, 0, 0)  # sağ alt
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lang_label = Gtk.Label(label="Dil / Language:")
        lang_box.pack_start(lang_label, False, True, 0)
        self.lang_combo = Gtk.ComboBoxText()
        self.lang_combo.append('tr', 'Türkçe')
        self.lang_combo.append('en', 'English')
        self.lang_combo.set_active(0 if self.lang == 'tr' else 1)
        self.lang_combo.connect("changed", self.on_lang_changed)
        lang_box.pack_start(self.lang_combo, False, True, 0)
        lang_align.add(lang_box)
        vbox.pack_end(lang_align, False, False, 0)

        self.selected_app = None
        self.window.show_all()
    
    def on_lang_changed(self, combo):
        self.lang = combo.get_active_id()
        self.t = self.LANGS[self.lang]
        self.window.set_title(self.t['title'])
        self.column.set_title(self.t['installed_apps'])
        self.edit_button.set_label(self.t['edit'])
        self.delete_button.set_label(self.t['delete'])
        self.new_button.set_label(self.t['new'])
        # Arayüzdeki diğer metinler dialog açıldığında güncellenecek

    def on_app_selected(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter:
            self.edit_button.set_sensitive(True)
            self.delete_button.set_sensitive(True)
            self.selected_app = model[treeiter][1]
        else:
            self.edit_button.set_sensitive(False)
            self.delete_button.set_sensitive(False)
            self.selected_app = None

    def new_appimage_dialog(self, widget):
        dialog = Gtk.Dialog(title=self.t['new_title'], parent=self.window, flags=0)
        dialog.set_default_size(400, 300)
        box = dialog.get_content_area()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        box.add(vbox)
        # Uygulama adı
        name_box = Gtk.Box(spacing=10)
        name_label = Gtk.Label(label=self.t['app_name'])
        name_box.pack_start(name_label, False, True, 0)
        name_entry = Gtk.Entry()
        name_box.pack_start(name_entry, True, True, 0)
        vbox.pack_start(name_box, False, True, 0)
        # AppImage seçimi
        appimage_box = Gtk.Box(spacing=10)
        appimage_label = Gtk.Label(label=self.t['appimage_file'])
        appimage_box.pack_start(appimage_label, False, True, 0)
        appimage_entry = Gtk.Entry()
        appimage_entry.set_editable(False)
        appimage_box.pack_start(appimage_entry, True, True, 0)
        appimage_button = Gtk.Button(label=self.t['select'])
        appimage_box.pack_start(appimage_button, False, True, 0)
        vbox.pack_start(appimage_box, False, True, 0)
        # İkon seçimi
        icon_box = Gtk.Box(spacing=10)
        icon_label = Gtk.Label(label=self.t['icon_file'])
        icon_box.pack_start(icon_label, False, True, 0)
        icon_entry = Gtk.Entry()
        icon_entry.set_editable(False)
        icon_box.pack_start(icon_entry, True, True, 0)
        icon_button = Gtk.Button(label=self.t['select'])
        icon_box.pack_start(icon_button, False, True, 0)
        vbox.pack_start(icon_box, False, True, 0)
        # Hedef klasör seçimi
        folder_box = Gtk.Box(spacing=10)
        folder_label = Gtk.Label(label="Klasör:")
        folder_box.pack_start(folder_label, False, True, 0)
        folder_entry = Gtk.Entry()
        folder_entry.set_editable(False)
        default_folder = os.path.expanduser("~/App")
        folder_entry.set_text(default_folder)
        folder_box.pack_start(folder_entry, True, True, 0)
        folder_button = Gtk.Button(label="Klasör Seç")
        folder_box.pack_start(folder_button, False, True, 0)
        vbox.pack_start(folder_box, False, True, 0)
        def select_folder(btn):
            file_dialog = Gtk.FileChooserDialog(title="Klasör Seç", parent=dialog, action=Gtk.FileChooserAction.SELECT_FOLDER)
            file_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            response = file_dialog.run()
            if response == Gtk.ResponseType.OK:
                folder_entry.set_text(file_dialog.get_filename())
            file_dialog.destroy()
        folder_button.connect("clicked", select_folder)
        # Seçim fonksiyonları
        def select_appimage(btn):
            file_dialog = Gtk.FileChooserDialog(title="AppImage Dosyası Seç", parent=dialog, action=Gtk.FileChooserAction.OPEN)
            file_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            filter_appimage = Gtk.FileFilter()
            filter_appimage.set_name("AppImage dosyaları")
            filter_appimage.add_pattern("*.AppImage")
            file_dialog.add_filter(filter_appimage)
            response = file_dialog.run()
            if response == Gtk.ResponseType.OK:
                appimage_entry.set_text(file_dialog.get_filename())
            file_dialog.destroy()
        def select_icon(btn):
            file_dialog = Gtk.FileChooserDialog(title="İkon Dosyası Seç", parent=dialog, action=Gtk.FileChooserAction.OPEN)
            file_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            filter_image = Gtk.FileFilter()
            filter_image.set_name("Resim dosyaları")
            filter_image.add_pattern("*.png")
            filter_image.add_pattern("*.svg")
            file_dialog.add_filter(filter_image)
            response = file_dialog.run()
            if response == Gtk.ResponseType.OK:
                icon_entry.set_text(file_dialog.get_filename())
            file_dialog.destroy()
        appimage_button.connect("clicked", select_appimage)
        icon_button.connect("clicked", select_icon)
        # Kur butonu
        dialog.add_button(self.t['install'], Gtk.ResponseType.OK)
        dialog.add_button(self.t['cancel'], Gtk.ResponseType.CANCEL)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            app_name = name_entry.get_text().strip()
            appimage_path = appimage_entry.get_text()
            icon_path = icon_entry.get_text()
            target_folder = folder_entry.get_text().strip()
            if not app_name or not appimage_path or not icon_path or not target_folder:
                error = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=self.t['fill_all'])
                error.run()
                error.destroy()
            else:
                self.install_appimage_paths(appimage_path, icon_path, app_name, target_folder)
        dialog.destroy()

    def install_appimage_paths(self, appimage_path, icon_path, app_name=None, install_dir=None):
        if not app_name:
            app_name = os.path.splitext(os.path.basename(appimage_path))[0]
        if not install_dir:
            home_dir = os.path.expanduser("~")
            install_dir = os.path.join(home_dir, "App")
        desktop_dir = os.path.expanduser("~/.local/share/applications")
        try:
            os.makedirs(install_dir, exist_ok=True)
            appimage_dest = os.path.join(install_dir, f"{app_name}.AppImage")
            shutil.copy2(appimage_path, appimage_dest)
            os.chmod(appimage_dest, 0o755)
            icon_ext = os.path.splitext(icon_path)[1]
            icon_dest = os.path.join(install_dir, f"{app_name}{icon_ext}")
            shutil.copy2(icon_path, icon_dest)
            desktop_content = f"""[Desktop Entry]\nName={app_name}\nExec={appimage_dest}\nIcon={icon_dest}\nType=Application\nCategories=Development;\n"""
            desktop_file = os.path.join(desktop_dir, f"{app_name}.desktop")
            os.makedirs(desktop_dir, exist_ok=True)
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            os.chmod(desktop_file, 0o755)
            self.load_applications()
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=self.t['install_success'])
            dialog.run()
            dialog.destroy()
        except Exception as e:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=f"{self.t['install_error']} {str(e)}")
            dialog.run()
            dialog.destroy()

    def load_applications(self):
        self.app_liststore.clear()
        desktop_dir = os.path.expanduser("~/.local/share/applications")
        if not os.path.exists(desktop_dir):
            return
        for fname in os.listdir(desktop_dir):
            if fname.endswith(".desktop"):
                path = os.path.join(desktop_dir, fname)
                try:
                    with open(path, 'r') as f:
                        for line in f:
                            if line.startswith("Name="):
                                app_name = line.strip().split('=', 1)[1]
                                self.app_liststore.append([app_name, path])
                                break
                except Exception:
                    continue

    def delete_selected_app(self, widget):
        if not hasattr(self, 'selected_app') or not self.selected_app:
            return
        # .desktop dosyasını oku, ilgili AppImage ve ikon dosyasını bul
        appimage_path = None
        icon_path = None
        try:
            with open(self.selected_app, 'r') as f:
                for line in f:
                    if line.startswith('Exec='):
                        appimage_path = line.strip().split('=', 1)[1]
                    if line.startswith('Icon='):
                        icon_path = line.strip().split('=', 1)[1]
            # Dosyaları sil
            if appimage_path and os.path.exists(appimage_path):
                os.remove(appimage_path)
            if icon_path and os.path.exists(icon_path):
                os.remove(icon_path)
            os.remove(self.selected_app)
            self.load_applications()
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=self.t['delete_success']
            )
            dialog.run()
            dialog.destroy()
        except Exception as e:
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"{self.t['delete_error']} {str(e)}"
            )
            dialog.run()
            dialog.destroy()

    def edit_selected_app(self, widget):
        if not hasattr(self, 'selected_app') or not self.selected_app:
            return
        # .desktop dosyasını oku, mevcut AppImage, ikon ve isim bilgisini bul
        appimage_path = None
        icon_path = None
        app_name = None
        app_folder = None
        try:
            with open(self.selected_app, 'r') as f:
                for line in f:
                    if line.startswith('Exec='):
                        appimage_path = line.strip().split('=', 1)[1]
                        app_folder = os.path.dirname(appimage_path)
                    if line.startswith('Icon='):
                        icon_path = line.strip().split('=', 1)[1]
                    if line.startswith('Name='):
                        app_name = line.strip().split('=', 1)[1]
        except Exception:
            return
        # Düzenleme penceresi
        dialog = Gtk.Dialog(title=self.t['edit_title'], parent=self.window, flags=0)
        dialog.set_default_size(400, 300)
        box = dialog.get_content_area()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        box.add(vbox)
        # Uygulama adı
        name_box = Gtk.Box(spacing=10)
        name_label = Gtk.Label(label=self.t['app_name'])
        name_box.pack_start(name_label, False, True, 0)
        name_entry = Gtk.Entry()
        name_entry.set_text(app_name or "")
        name_box.pack_start(name_entry, True, True, 0)
        vbox.pack_start(name_box, False, True, 0)
        # AppImage seçimi
        appimage_box = Gtk.Box(spacing=10)
        appimage_label = Gtk.Label(label=self.t['appimage_file'])
        appimage_box.pack_start(appimage_label, False, True, 0)
        appimage_entry = Gtk.Entry()
        appimage_entry.set_editable(False)
        appimage_entry.set_text(appimage_path or "")
        appimage_box.pack_start(appimage_entry, True, True, 0)
        appimage_button = Gtk.Button(label=self.t['select'])
        appimage_box.pack_start(appimage_button, False, True, 0)
        vbox.pack_start(appimage_box, False, True, 0)
        # İkon seçimi
        icon_box = Gtk.Box(spacing=10)
        icon_label = Gtk.Label(label=self.t['icon_file'])
        icon_box.pack_start(icon_label, False, True, 0)
        icon_entry = Gtk.Entry()
        icon_entry.set_editable(False)
        icon_entry.set_text(icon_path or "")
        icon_box.pack_start(icon_entry, True, True, 0)
        icon_button = Gtk.Button(label=self.t['select'])
        icon_box.pack_start(icon_button, False, True, 0)
        vbox.pack_start(icon_box, False, True, 0)
        # Hedef klasör seçimi
        folder_box = Gtk.Box(spacing=10)
        folder_label = Gtk.Label(label="Klasör:")
        folder_box.pack_start(folder_label, False, True, 0)
        folder_entry = Gtk.Entry()
        folder_entry.set_editable(False)
        folder_entry.set_text(app_folder or os.path.expanduser("~/App"))
        folder_box.pack_start(folder_entry, True, True, 0)
        folder_button = Gtk.Button(label="Klasör Seç")
        folder_box.pack_start(folder_button, False, True, 0)
        vbox.pack_start(folder_box, False, True, 0)
        def select_folder(btn):
            file_dialog = Gtk.FileChooserDialog(title="Klasör Seç", parent=dialog, action=Gtk.FileChooserAction.SELECT_FOLDER)
            file_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            response = file_dialog.run()
            if response == Gtk.ResponseType.OK:
                folder_entry.set_text(file_dialog.get_filename())
            file_dialog.destroy()
        folder_button.connect("clicked", select_folder)
        # Seçim fonksiyonları
        def select_appimage(btn):
            file_dialog = Gtk.FileChooserDialog(title="AppImage Dosyası Seç", parent=dialog, action=Gtk.FileChooserAction.OPEN)
            file_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            filter_appimage = Gtk.FileFilter()
            filter_appimage.set_name("AppImage dosyaları")
            filter_appimage.add_pattern("*.AppImage")
            file_dialog.add_filter(filter_appimage)
            response = file_dialog.run()
            if response == Gtk.ResponseType.OK:
                appimage_entry.set_text(file_dialog.get_filename())
            file_dialog.destroy()
        def select_icon(btn):
            file_dialog = Gtk.FileChooserDialog(title="İkon Dosyası Seç", parent=dialog, action=Gtk.FileChooserAction.OPEN)
            file_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            filter_image = Gtk.FileFilter()
            filter_image.set_name("Resim dosyaları")
            filter_image.add_pattern("*.png")
            filter_image.add_pattern("*.svg")
            file_dialog.add_filter(filter_image)
            response = file_dialog.run()
            if response == Gtk.ResponseType.OK:
                icon_entry.set_text(file_dialog.get_filename())
            file_dialog.destroy()
        appimage_button.connect("clicked", select_appimage)
        icon_button.connect("clicked", select_icon)
        # Kaydet butonu
        dialog.add_button(self.t['save'], Gtk.ResponseType.OK)
        dialog.add_button(self.t['cancel'], Gtk.ResponseType.CANCEL)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_name = name_entry.get_text().strip()
            new_appimage = appimage_entry.get_text().strip()
            new_icon = icon_entry.get_text().strip()
            new_folder = folder_entry.get_text().strip()
            if not new_name or not new_appimage or not new_icon or not new_folder:
                error = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=self.t['fill_all'])
                error.run()
                error.destroy()
            else:
                # Dosyaları kopyala ve .desktop dosyasını güncelle
                install_dir = new_folder
                os.makedirs(install_dir, exist_ok=True)
                appimage_dest = os.path.join(install_dir, f"{new_name}.AppImage")
                shutil.copy2(new_appimage, appimage_dest)
                os.chmod(appimage_dest, 0o755)
                icon_ext = os.path.splitext(new_icon)[1]
                icon_dest = os.path.join(install_dir, f"{new_name}{icon_ext}")
                shutil.copy2(new_icon, icon_dest)
                # .desktop dosyasını güncelle
                desktop_content = f"""[Desktop Entry]\nName={new_name}\nExec={appimage_dest}\nIcon={icon_dest}\nType=Application\nCategories=Development;\n"""
                desktop_file = os.path.join(os.path.expanduser("~/.local/share/applications"), f"{new_name}.desktop")
                with open(desktop_file, 'w') as f:
                    f.write(desktop_content)
                os.chmod(desktop_file, 0o755)
                # Eski .desktop ve dosyaları sil (isim değiştiyse)
                if os.path.abspath(desktop_file) != os.path.abspath(self.selected_app):
                    try:
                        os.remove(self.selected_app)
                    except Exception:
                        pass
                    # Eski AppImage ve ikon dosyalarını sil
                    old_appimage = appimage_path
                    old_icon = icon_path
                    if old_appimage and os.path.exists(old_appimage):
                        try:
                            os.remove(old_appimage)
                        except Exception:
                            pass
                    if old_icon and os.path.exists(old_icon):
                        try:
                            os.remove(old_icon)
                        except Exception:
                            pass
                self.load_applications()
        dialog.destroy()

    def ensure_lobehub_icons(self):
        self.icons_dir = os.path.expanduser("~/.local/share/appimage_installer/icons")
        os.makedirs(self.icons_dir, exist_ok=True)
        for name, url in self.LOBEHUB_ICONS:
            icon_path = os.path.join(self.icons_dir, f"{name}.png")
            if not os.path.exists(icon_path):
                try:
                    urllib.request.urlretrieve(url, icon_path)
                except Exception:
                    pass

if __name__ == "__main__":
    installer = AppImageInstaller()
    Gtk.main() 