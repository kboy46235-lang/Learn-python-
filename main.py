from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
import urllib.request
import json
import threading
import time
import os

# --- Android Secure Flag Integration for Zero Recent Apps Preview ---
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    WindowManager = autoclass('android.view.WindowManager$LayoutParams')
    # FLAG_SECURE prevents screenshots and hides app contents in recent apps preview
    activity.getWindow().setFlags(WindowManager.FLAG_SECURE, WindowManager.FLAG_SECURE)
except Exception as e:
    pass

# --- Permanent Cloud & Local Storage State ---
class AppState:
    CONFIG_FILE = "mac10_vault_config.json"
    
    has_password = False
    saved_password = ""
    wrong_attempts = 0
    
    my_username = ""
    is_registered = False
    target_user = ""
    
    CLOUD_URL = "https://api.jsonbin.io/v3/b/6a5f932fda38895dfe7b9025"
    API_KEY = "$2a$10$DsLzTIRSPZLgP9kLKWN7u.x0bUIxUcr8.752gmkRon.NzP5QBYaEi"
    
    registered_users = ["mac10", "manish", "khushi"]
    cloud_chats = {}

    @classmethod
    def load_local_data(cls):
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    cls.saved_password = data.get("password", "")
                    cls.has_password = data.get("has_password", False)
                    cls.my_username = data.get("username", "")
                    cls.is_registered = data.get("is_registered", False)
            except Exception as e:
                pass

    @classmethod
    def save_local_data(cls):
        try:
            data = {
                "password": cls.saved_password,
                "has_password": cls.has_password,
                "username": cls.my_username,
                "is_registered": cls.is_registered
            }
            with open(cls.CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            pass

# --- 1. Python Cover Login ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.add_widget(Label(text="[b]Learn Python Pro[/b]", markup=True, font_size=28, color=get_color_from_hex('#3498DB')))
        layout.add_widget(Label(text="Login to start learning", font_size=14, color=get_color_from_hex('#95A5A6')))
        self.email_input = TextInput(hint_text='Email or Mobile Number', multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.email_input)
        login_btn = Button(text="LOG IN", bold=True, size_hint_y=None, height=55, background_color=get_color_from_hex('#0095F6'))
        login_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(login_btn)
        self.add_widget(layout)

# --- 2. Python Dashboard ---
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=50)
        top_bar.add_widget(Label(text="[b]Python Masterclass[/b]", markup=True, font_size=18))
        menu_btn = Button(text="⋮", font_size=26, size_hint_x=None, width=50, background_color=(0,0,0,0))
        menu_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        top_bar.add_widget(menu_btn)
        layout.add_widget(top_bar)

        scroll = ScrollView()
        v_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        v_layout.bind(minimum_height=v_layout.setter('height'))
        
        for i in range(1, 16):
            btn = Button(text=f"▶ Lecture {i}: Python Basics & Advanced", size_hint_y=None, height=60, background_color=get_color_from_hex('#1A252F'))
            btn.bind(on_press=lambda x, title=i: self.open_video(f"Lecture {title}"))
            v_layout.add_widget(btn)
            
        scroll.add_widget(v_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def open_video(self, title):
        vs = self.manager.get_screen('video_player')
        vs.title_text = title
        self.manager.current = 'video_player'

# --- 3. Video Player ---
class VideoPlayerScreen(Screen):
    title_text = "Lecture"
    def __init__(self, **kwargs):
        super(VideoPlayerScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.lbl = Label(text="", size_hint_y=None, height=40, bold=True)
        layout.add_widget(self.lbl)
        layout.add_widget(Label(text="[color=2ECC71]▶ HD Streaming Active...[/color]", markup=True, font_size=18))
        layout.add_widget(Slider(min=0, max=100, value=30, size_hint_y=None, height=40))
        
        back = Button(text="Close Player", size_hint_y=None, height=45, background_color=get_color_from_hex('#C0392B'))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(back)
        self.add_widget(layout)

    def on_enter(self):
        self.lbl.text = self.title_text

# --- 4. Settings with Hidden Mac10 Gateway ---
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="[b]Settings & Privacy[/b]", markup=True, font_size=20, size_hint_y=None, height=45, color=get_color_from_hex('#3498DB')))
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=10)
        content.bind(minimum_height=content.setter('height'))
        
        for s in ["Account Privacy", "Two-Factor Auth", "Login Activity", "Blocked Accounts", "Help & Support"]:
            content.add_widget(Button(text=s, size_hint_y=None, height=50, background_color=(0.15, 0.15, 0.15, 1)))

        mac10_btn = Button(text="Mac10", size_hint_y=None, height=60, bold=True, background_color=get_color_from_hex('#8E44AD'))
        mac10_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'vault_auth'))
        content.add_widget(mac10_btn)

        back = Button(text="← Back to Dashboard", size_hint_y=None, height=50, background_color=get_color_from_hex('#2C3E50'))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        content.add_widget(back)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

# --- 5. Smart Vault Auth ---
class VaultAuthScreen(Screen):
    def __init__(self, **kwargs):
        super(VaultAuthScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        self.title_lbl = Label(text="[b]Mac10 Vault[/b]", markup=True, font_size=22, color=get_color_from_hex('#E67E22'))
        layout.add_widget(self.title_lbl)
        
        self.info_lbl = Label(text="", font_size=14, color=(0.8,0.8,0.8,1))
        layout.add_widget(self.info_lbl)
        
        self.pass_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.pass_input)
        
        self.btn = Button(text="Submit", size_hint_y=None, height=55, bold=True, background_color=get_color_from_hex('#2980B9'))
        self.btn.bind(on_press=self.verify)
        layout.add_widget(self.btn)
        
        back = Button(text="Back", size_hint_y=None, height=45, background_color=(0.4,0.4,0.4,1))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        layout.add_widget(back)
        self.add_widget(layout)

    def on_enter(self):
        AppState.load_local_data()
        self.pass_input.text = ""
        AppState.wrong_attempts = 0
        if not AppState.has_password:
            self.title_lbl.text = "[b]Create Password[/b]"
            self.info_lbl.text = "Set a secure password for Mac10:"
            self.btn.text = "CREATE"
        else:
            self.title_lbl.text = "[b]Enter Password[/b]"
            self.info_lbl.text = "Enter your secret password:"
            self.btn.text = "UNLOCK"

    def verify(self, instance):
        entered = self.pass_input.text.strip()
        if not AppState.has_password:
            if len(entered) > 0:
                AppState.saved_password = entered
                AppState.has_password = True
                AppState.save_local_data()
                self.info_lbl.text = "Password Created! Go back & re-enter."
                self.manager.current = 'settings'
        else:
            if entered == AppState.saved_password:
                AppState.wrong_attempts = 0
                if not AppState.is_registered:
                    self.manager.current = 'register'
                else:
                    self.manager.current = 'insta_home'
            else:
                AppState.wrong_attempts += 1
                if AppState.wrong_attempts >= 2:
                    AppState.wrong_attempts = 0
                    self.manager.current = 'dashboard'
                else:
                    self.info_lbl.text = f"Wrong Password! Attempt {AppState.wrong_attempts}/2"

# --- 6. Unique Instagram Profile Registration Screen ---
class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="[b]Create Instagram Account[/b]", markup=True, font_size=24, color=get_color_from_hex('#E1306C')))
        
        self.status = Label(text="Choose a unique username", font_size=13, color=(0.7,0.7,0.7,1))
        layout.add_widget(self.status)
        
        self.user_in = TextInput(hint_text='Username (e.g. manish_10)', multiline=False, size_hint_y=None, height=48)
        layout.add_widget(self.user_in)
        
        reg_btn = Button(text="REGISTER ID", size_hint_y=None, height=50, bold=True, background_color=get_color_from_hex('#3897F0'))
        reg_btn.bind(on_press=self.register_user)
        layout.add_widget(reg_btn)
        self.add_widget(layout)

    def register_user(self, instance):
        uname = self.user_in.text.strip().lower()
        if len(uname) > 2:
            if uname in AppState.registered_users:
                self.status.text = "[-] Username already taken!"
            else:
                AppState.registered_users.append(uname)
                AppState.my_username = uname
                AppState.is_registered = True
                AppState.save_local_data()
                self.manager.current = 'insta_home'
        else:
            self.status.text = "[-] Minimum 3 characters required!"

# --- 7. Strict Validated Search Hub ---
class InstaHomeScreen(Screen):
    def __init__(self, **kwargs):
        super(InstaHomeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="[b]Instagram Direct (Cloud Live)[/b]", markup=True, font_size=22, size_hint_y=None, height=40, color=get_color_from_hex('#E1306C')))
        
        search_box = BoxLayout(size_hint_y=None, height=50, spacing=8)
        self.search_in = TextInput(hint_text='Search username (e.g. mac10)...', multiline=False)
        search_btn = Button(text="Search", size_hint_x=None, width=90, background_color=get_color_from_hex('#3897F0'))
        search_btn.bind(on_press=self.search_user_strict)
        search_box.add_widget(self.search_in)
        search_box.add_widget(search_btn)
        layout.add_widget(search_box)
        
        self.status = Label(text="Type exact username to verify", size_hint_y=None, height=30, color=(0,1,0,1))
        layout.add_widget(self.status)
        
        self.scroll = ScrollView()
        self.box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=5)
        self.box.bind(minimum_height=self.box.setter('height'))
        self.scroll.add_widget(self.box)
        layout.add_widget(self.scroll)
        
        nav = BoxLayout(size_hint_y=None, height=60, spacing=5)
        nav.add_widget(Button(text="👤 Profile", background_color=get_color_from_hex('#2C3E50')))
        nav.add_widget(Button(text="🔍 Explore", background_color=get_color_from_hex('#2C3E50')))
        
        msg_btn = Button(text="💬 Direct", background_color=get_color_from_hex('#2C3E50'))
        msg_btn.bind(on_press=self.open_direct_chat)
        nav.add_widget(msg_btn)
        
        layout.add_widget(nav)
        self.add_widget(layout)

    def on_enter(self):
        AppState.target_user = ""
        self.search_in.text = ""
        self.status.text = "Type exact username to verify"

    def search_user_strict(self, instance):
        q = self.search_in.text.strip().lower()
        if not q:
            self.status.text = "[-] Please enter a username!"
            AppState.target_user = ""
            return
        
        if q in AppState.registered_users:
            AppState.target_user = q
            self.status.text = f"[+] Found @{q}! Tap Direct to open live chat."
        else:
            AppState.target_user = ""
            self.status.text = f"[-] User @{q} does not exist!"

    def open_direct_chat(self, instance):
        if AppState.target_user:
            self.manager.current = 'insta_chat'
        else:
            self.status.text = "[-] First search & find a valid user!"

# --- 8. Private Live Cloud DM Chat Screen ---
class InstaChatScreen(Screen):
    def __init__(self, **kwargs):
        super(InstaChatScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.header = Label(text="[b]Live Cloud DM[/b]", markup=True, size_hint_y=None, height=40)
        layout.add_widget(self.header)
        
        self.scroll = ScrollView()
        self.chat_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=5)
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        self.scroll.add_widget(self.chat_box)
        layout.add_widget(self.scroll)
        
        inp = BoxLayout(size_hint_y=None, height=55, spacing=8)
        self.msg = TextInput(hint_text='Type live message...', multiline=False)
        inp.add_widget(self.msg)
        send = Button(text="SEND", size_hint_x=None, width=90, bold=True, background_color=get_color_from_hex('#3897F0'))
        send.bind(on_press=self.send_message)
        inp.add_widget(send)
        layout.add_widget(inp)
        
        back = Button(text="← Back to Home", size_hint_y=None, height=45, background_color=(0.5,0,0,1))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'insta_home'))
        layout.add_widget(back)
        self.add_widget(layout)

        self.is_syncing = True
        threading.Thread(target=self.background_listener, daemon=True).start()

    def on_enter(self):
        target = AppState.target_user if AppState.target_user else "mac10"
        self.header.text = f"[b]Live Chat with @{target}[/b]"
        self.refresh_chat()

    def refresh_chat(self):
        self.chat_box.clear_widgets()
        target = AppState.target_user
        chats = AppState.cloud_chats.get(target, [])
        for c in chats:
            row = BoxLayout(size_hint_y=None, height=40)
            row.add_widget(Label(text=f"{c['sender']}: {c['text']}", halign='left'))
            self.chat_box.add_widget(row)

    def send_message(self, instance):
        m = self.msg.text.strip()
        target = AppState.target_user
        if m and target:
            if target not in AppState.cloud_chats:
                AppState.cloud_chats[target] = []
            
            sender_name = AppState.my_username if AppState.my_username else "Manish"
            AppState.cloud_chats[target].append({"sender": sender_name, "text": m})
            self.msg.text = ""
            self.refresh_chat()
            threading.Thread(target=self.sync_to_cloud, args=(AppState.cloud_chats,)).start()

    def sync_to_cloud(self, chats_data):
        try:
            data = json.dumps({"chats": chats_data}).encode('utf-8')
            req = urllib.request.Request(AppState.CLOUD_URL, data=data, method='PUT')
            req.add_header('Content-Type', 'application/json')
            req.add_header('X-Master-Key', AppState.API_KEY)
            urllib.request.urlopen(req)
        except Exception as e:
            pass

    def background_listener(self):
        while self.is_syncing:
            time.sleep(3)
            try:
                req = urllib.request.Request(f"{AppState.CLOUD_URL}/latest")
                req.add_header('X-Master-Key', AppState.API_KEY)
                response = urllib.request.urlopen(req)
                result = json.loads(response.read().decode())
                remote_chats = result.get("record", {}).get("chats", {})
                if remote_chats:
                    AppState.cloud_chats = remote_chats
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: self.refresh_chat(), 0)
            except Exception as e:
                pass

# --- App Runner ---
class PythonStealthApp(App):
    def build(self):
        AppState.load_local_data()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(VideoPlayerScreen(name='video_player'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(VaultAuthScreen(name='vault_auth'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(InstaHomeScreen(name='insta_home'))
        sm.add_widget(InstaChatScreen(name='insta_chat'))
        return sm

    def on_pause(self):
        # App ko background me dalne par wapas python dashboard par bhej dega
        self.root.current = 'dashboard'
        return True

    def on_resume(self):
        pass

if __name__ == '__main__':
    PythonStealthApp().run()
