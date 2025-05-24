import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import threading
import time
import os

# Selenium kütüphanesinin yüklü olup olmadığını kontrol et
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    selenium_installed = True
except ImportError:
    selenium_installed = False

# Lisans notu
# Bu yazılım Shigeruya'ya aittir.

class ProxyBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy Tarayıcı")
        self.root.geometry("480x420")
        self.root.resizable(False, False)

        self.driver = None
        self.lang = "tr"  # Varsayılan dil: Türkçe

        self.texts = {
            "tr": {
                "app_title": "Proxy Tarayıcı",
                "proxy_settings": "Proxy Ayarları",
                "proxy_address": "Proxy Adresi (IP:Port):",
                "proxy_type": "Proxy Türü:",
                "username_ops": "Kullanıcı Adı (Ops.):",
                "password_ops": "Şifre (Ops.):",
                "performance_settings": "Hızlandırma",
                "headless_mode": "Tarayıcıyı Gizle (Headless Mod)",
                "no_images": "Resimleri Yükleme",
                "disable_js": "JavaScript'i Devre Dışı Bırak (UYARI: Siteleri bozabilir)",
                "ignore_cert_errors": "SSL Sertifika Hatalarını Yoksay",
                "start_browser": "Tarayıcıyı Başlat",
                "stop_browser": "Tarayıcıyı Kapat",
                "status_waiting": "Durum: Bekleniyor...",
                "status_installing": "Durum: Gerekli kütüphaneler indiriliyor...",
                "status_starting": "Durum: Tarayıcı başlatılıyor...",
                "status_started": "Durum: Tarayıcı başlatıldı. Proxy:",
                "status_stopping": "Durum: Tarayıcı kapatılıyor...",
                "status_stopped": "Durum: Tarayıcı kapatıldı.",
                "status_error": "Durum: Hata oluştu.",
                "status_already_stopped": "Durum: Tarayıcı zaten kapalı.",
                "error_title": "Hata",
                "error_proxy_address": "Lütfen bir proxy adresi girin.",
                "error_invalid_proxy_type": "Geçersiz proxy türü seçildi.",
                "error_browser_start": "Tarayıcı başlatılırken bir hata oluştu:",
                "error_driver_path": "\n\nLütfen:\n- ChromeDriver'ın güncel ve PATH'inizde veya uygulamanızla aynı klasörde olduğundan emin olun.\n- Chrome sürümünüz ile ChromeDriver sürümünün uyumlu olduğundan emin olun.\n- Proxy adresinin ve türünün doğru olduğundan emin olun.",
                "success_title": "Başarılı",
                "success_browser_started": "Tarayıcı {proxy_info} proxy üzerinden başarıyla başlatıldı.\nVarsayılan olarak DuckDuckGo açıldı.",
                "info_browser_stopped": "Tarayıcı başarıyla kapatıldı.",
                "error_browser_stop": "Tarayıcı kapatılırken hata oluştu:",
                "install_pip_error": "Hata: pip kurulumu sırasında bir sorun oluştu. Lütfen elle kurmayı deneyin:\n'pip install selenium'",
                "install_complete_restart": "Kurulum tamamlandı. Uygulama otomatik olarak yeniden başlatılıyor...",
                "install_failed_exit": "Kurulum başarısız. Uygulama kapatılıyor. Lütfen internet bağlantınızı kontrol edin veya kütüphaneyi manuel kurun.",
                "install_anim_dot": "Kütüphane indiriliyor"
            },
            "en": {
                "app_title": "Proxy Browser",
                "proxy_settings": "Proxy Settings",
                "proxy_address": "Proxy Address (IP:Port):",
                "proxy_type": "Proxy Type:",
                "username_ops": "Username (Opt.):",
                "password_ops": "Password (Opt.):",
                "performance_settings": "Performance",
                "headless_mode": "Hide Browser (Headless Mode)",
                "no_images": "Do Not Load Images",
                "disable_js": "Disable JavaScript (WARNING: May break websites)",
                "ignore_cert_errors": "Ignore SSL Certificate Errors",
                "start_browser": "Start Browser",
                "stop_browser": "Stop Browser",
                "status_waiting": "Status: Waiting...",
                "status_installing": "Status: Installing required libraries...",
                "status_starting": "Status: Starting browser...",
                "status_started": "Status: Browser started. Proxy:",
                "status_stopping": "Status: Stopping browser...",
                "status_stopped": "Status: Browser stopped.",
                "status_error": "Status: Error occurred.",
                "status_already_stopped": "Status: Browser already stopped.",
                "error_title": "Error",
                "error_proxy_address": "Please enter a proxy address.",
                "error_invalid_proxy_type": "Invalid proxy type selected.",
                "error_browser_start": "An error occurred while starting the browser:",
                "error_driver_path": "\n\nPlease ensure:\n- ChromeDriver is up-to-date and in your PATH or in the same folder as the application.\n- Your Chrome version is compatible with ChromeDriver version.\n- Proxy address and type are correct.",
                "success_title": "Success",
                "success_browser_started": "Browser successfully launched via {proxy_info} proxy.\nDuckDuckGo opened by default.",
                "info_browser_stopped": "Browser successfully closed.",
                "error_browser_stop": "An error occurred while closing the browser:",
                "install_pip_error": "Error: A problem occurred during pip installation. Please try manual installation:\n'pip install selenium'",
                "install_complete_restart": "Installation complete. Application is restarting automatically...",
                "install_failed_exit": "Installation failed. Application is closing. Please check your internet connection or install the library manually.",
                "install_anim_dot": "Installing libraries"
            }
        }

        self.install_animation_idx = 0
        self.install_animation_running = False

        if not selenium_installed:
            self.show_install_screen()
        else:
            self.create_main_widgets()

    def set_language(self, lang_code):
        self.lang = lang_code
        self.root.title(self.texts[self.lang]["app_title"])
        
        # Sekme başlıklarını güncelle
        self.notebook.tab(self.proxy_tab, text=self.texts[self.lang]["proxy_settings"])
        self.notebook.tab(self.performance_tab, text=self.texts[self.lang]["performance_settings"])

        # Label ve Button metinlerini güncelle
        self.proxy_address_label.config(text=self.texts[self.lang]["proxy_address"])
        self.proxy_type_label.config(text=self.texts[self.lang]["proxy_type"])
        self.username_label.config(text=self.texts[self.lang]["username_ops"])
        self.password_label.config(text=self.texts[self.lang]["password_ops"])

        self.headless_checkbox.config(text=self.texts[self.lang]["headless_mode"])
        self.no_images_checkbox.config(text=self.texts[self.lang]["no_images"])
        self.no_js_checkbox.config(text=self.texts[self.lang]["disable_js"])
        self.ignore_cert_errors_checkbox.config(text=self.texts[self.lang]["ignore_cert_errors"])
        
        self.start_button.config(text=self.texts[self.lang]["start_browser"])
        self.stop_button.config(text=self.texts[self.lang]["stop_browser"])
        
        self.status_label.config(text=self.texts[self.lang]["status_waiting"])

    def show_install_screen(self):
        # Ana widget'ları gizle
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("400x150")
        self.root.title(self.texts[self.lang]["app_title"])

        self.install_label = ttk.Label(self.root, text=self.texts[self.lang]["status_installing"], font=("Arial", 12))
        self.install_label.pack(pady=20)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.pack(pady=10)

        self.root.update_idletasks() # UI'ın hemen güncellenmesini sağla

        self.install_animation_running = True
        self.animate_installation()

        # Ayrı bir thread'de kurulumu başlat
        install_thread = threading.Thread(target=self.install_selenium_library)
        install_thread.daemon = True
        install_thread.start()

    def animate_installation(self):
        if not self.install_animation_running:
            return

        dots = ""
        for _ in range(self.install_animation_idx):
            dots += "."
        
        self.install_label.config(text=f"{self.texts[self.lang]['install_anim_dot']}{dots}")
        self.install_animation_idx = (self.install_animation_idx + 1) % 4
        self.root.after(500, self.animate_installation) # Her 500ms'de bir güncelle

    def install_selenium_library(self):
        self.progress_bar.start()
        try:
            # pip'i subprocess ile çalıştır
            subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
            messagebox.showinfo(self.texts[self.lang]["success_title"], self.texts[self.lang]["install_complete_restart"])
            self.restart_application()
        except subprocess.CalledProcessError as e:
            messagebox.showerror(self.texts[self.lang]["error_title"], self.texts[self.lang]["install_pip_error"])
            self.root.quit() # Hata durumunda uygulamayı kapat
        except Exception as e:
            messagebox.showerror(self.texts[self.lang]["error_title"], f"{self.texts[self.lang]['install_failed_exit']}\n{e}")
            self.root.quit()
        finally:
            self.progress_bar.stop()
            self.install_animation_running = False

    def restart_application(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def create_main_widgets(self):
        # Mevcut widget'ları temizle (eğer kurulum ekranından geliyorsa)
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("480x420")
        self.root.title(self.texts[self.lang]["app_title"])

        # Dil Seçenekleri Menüsü
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        self.language_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Dil / Language", menu=self.language_menu)
        self.language_menu.add_command(label="Türkçe", command=lambda: self.set_language("tr"))
        self.language_menu.add_command(label="English", command=lambda: self.set_language("en"))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.proxy_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.proxy_tab, text=self.texts[self.lang]["proxy_settings"])

        self.performance_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.performance_tab, text=self.texts[self.lang]["performance_settings"])

        # Proxy Ayarları İçeriği
        self.proxy_address_label = ttk.Label(self.proxy_tab, text=self.texts[self.lang]["proxy_address"])
        self.proxy_address_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.proxy_address_entry = ttk.Entry(self.proxy_tab, width=35)
        self.proxy_address_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.proxy_address_entry.insert(0, "82.223.165.28:59602")

        self.proxy_type_label = ttk.Label(self.proxy_tab, text=self.texts[self.lang]["proxy_type"])
        self.proxy_type_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.proxy_type_var = tk.StringVar(self.root)
        self.proxy_type_combobox = ttk.Combobox(self.proxy_tab, textvariable=self.proxy_type_var, width=33, state="readonly")
        self.proxy_type_combobox['values'] = ("HTTP", "HTTPS", "SOCKS4", "SOCKS5")
        self.proxy_type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.proxy_type_combobox.set("SOCKS5")

        self.username_label = ttk.Label(self.proxy_tab, text=self.texts[self.lang]["username_ops"])
        self.username_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(self.proxy_tab, width=35)
        self.username_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.password_label = ttk.Label(self.proxy_tab, text=self.texts[self.lang]["password_ops"])
        self.password_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self.proxy_tab, width=35, show="*")
        self.password_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.proxy_tab.grid_columnconfigure(1, weight=1)

        # Hızlandırma Ayarları İçeriği
        self.headless_var = tk.BooleanVar(value=True)
        self.headless_checkbox = ttk.Checkbutton(self.performance_tab, text=self.texts[self.lang]["headless_mode"], variable=self.headless_var)
        self.headless_checkbox.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        self.no_images_var = tk.BooleanVar(value=True)
        self.no_images_checkbox = ttk.Checkbutton(self.performance_tab, text=self.texts[self.lang]["no_images"], variable=self.no_images_var)
        self.no_images_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        self.no_js_var = tk.BooleanVar(value=False)
        self.no_js_checkbox = ttk.Checkbutton(self.performance_tab, text=self.texts[self.lang]["disable_js"], variable=self.no_js_var)
        self.no_js_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        self.ignore_cert_errors_var = tk.BooleanVar(value=True)
        self.ignore_cert_errors_checkbox = ttk.Checkbutton(self.performance_tab, text=self.texts[self.lang]["ignore_cert_errors"], variable=self.ignore_cert_errors_var)
        self.ignore_cert_errors_checkbox.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Kontrol Butonları
        self.button_frame = ttk.Frame(self.root, padding="10")
        self.button_frame.pack(pady=5)

        self.start_button = ttk.Button(self.button_frame, text=self.texts[self.lang]["start_browser"], command=self.start_browser_thread)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(self.button_frame, text=self.texts[self.lang]["stop_browser"], command=self.stop_browser_thread, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Durum Çubuğu
        self.status_label = ttk.Label(self.root, text=self.texts[self.lang]["status_waiting"], relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(side="bottom", fill="x", ipady=2)

    def start_browser_thread(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=self.texts[self.lang]["status_starting"])
        
        proxy_address = self.proxy_address_entry.get().strip()
        proxy_type = self.proxy_type_var.get().strip().lower()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not proxy_address:
            messagebox.showerror(self.texts[self.lang]["error_title"], self.texts[self.lang]["error_proxy_address"])
            self.reset_buttons()
            return
        
        proxy_scheme = ""
        if proxy_type == "http":
            proxy_scheme = "http://"
        elif proxy_type == "https":
            proxy_scheme = "https://"
        elif proxy_type == "socks4":
            proxy_scheme = "socks4://"
        elif proxy_type == "socks5":
            proxy_scheme = "socks5://"
        else:
            messagebox.showerror(self.texts[self.lang]["error_title"], self.texts[self.lang]["error_invalid_proxy_type"])
            self.reset_buttons()
            return

        if username and password:
            proxy_full_address = f"{username}:{password}@{proxy_address}"
        else:
            proxy_full_address = proxy_address

        full_proxy_string = f"{proxy_scheme}{proxy_full_address}"

        thread = threading.Thread(target=self._run_browser, args=(full_proxy_string,))
        thread.daemon = True
        thread.start()

    def _run_browser(self, full_proxy_string):
        chrome_options = Options()
        
        chrome_options.add_argument(f"--proxy-server={full_proxy_string}")
        
        if self.ignore_cert_errors_var.get():
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--allow-insecure-localhost")
        
        if self.headless_var.get():
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")

        if self.no_images_var.get():
            chrome_options.add_experimental_option(
                "prefs", {"profile.managed_default_content_settings.images": 2}
            )
        
        if self.no_js_var.get():
            chrome_options.add_experimental_option(
                "prefs", {"profile.managed_default_content_settings.javascript": 2}
            )

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-default-apps")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.get("https://duckduckgo.com/")

            self.status_label.config(text=f"{self.texts[self.lang]['status_started']} {full_proxy_string}")
            messagebox.showinfo(self.texts[self.lang]["success_title"], 
                                self.texts[self.lang]["success_browser_started"].format(proxy_info=full_proxy_string))
            
            while self.driver and self.driver.session_id:
                time.sleep(0.5) 

        except Exception as e:
            error_message = f"{self.texts[self.lang]['error_browser_start']}\n{e}"
            self.status_label.config(text=self.texts[self.lang]["status_error"])
            messagebox.showerror(self.texts[self.lang]["error_title"], error_message + self.texts[self.lang]["error_driver_path"])
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.reset_buttons()

    def stop_browser_thread(self):
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text=self.texts[self.lang]["status_stopping"])
        
        thread = threading.Thread(target=self._stop_browser)
        thread.daemon = True
        thread.start()

    def _stop_browser(self):
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.status_label.config(text=self.texts[self.lang]["status_stopped"])
                messagebox.showinfo(self.texts[self.lang]["info_browser_stopped"])
            except Exception as e:
                self.status_label.config(text=self.texts[self.lang]["status_error"])
                messagebox.showerror(self.texts[self.lang]["error_title"], f"{self.texts[self.lang]['error_browser_stop']}\n{e}")
            finally:
                self.reset_buttons()
        else:
            self.status_label.config(text=self.texts[self.lang]["status_already_stopped"])
            self.reset_buttons()

    def reset_buttons(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProxyBrowserApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_browser_thread)
    root.mainloop()
