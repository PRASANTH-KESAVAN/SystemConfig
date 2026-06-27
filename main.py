import os
import math
import time
import json
import subprocess
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.uix.widget import Widget
from kivy.uix.camera import Camera
from kivy.graphics import Color, Line
from kivy.utils import get_color_from_hex

# Try loading Android APIs (fails gracefully on desktop)
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    PackageManager = autoclass('android.content.pm.PackageManager')
    Intent = autoclass('android.content.Intent')
    HAS_ANDROID = True
except Exception:
    HAS_ANDROID = False

# Colors
BG_COLOR = get_color_from_hex("#121212")
CARD_COLOR = get_color_from_hex("#1E1E1E")
ACCENT_BLUE = get_color_from_hex("#00E5FF")
ACCENT_PURPLE = get_color_from_hex("#6200EA")
TEXT_COLOR = get_color_from_hex("#FFFFFF")

KV_UI = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<CardButton@ButtonBehavior+BoxLayout>:
    text: ""
    icon: ""
    canvas.before:
        Color:
            rgba: get_color_from_hex("#1E1E1E")
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
    Label:
        text: root.text
        bold: True
        color: get_color_from_hex("#FFFFFF")

<DisguiseScreen>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    # Fake Error UI
    FloatLayout:
        Label:
            id: fake_text
            text: "SYSTEM_PROCESS_NOT_RESPONDING\\n\\nERR_CODE: 0x000000FF\\nMemory dump failed.\\n\\nWaiting for debugger..."
            color: get_color_from_hex("#00FF00") if root.theme == "glitch" else get_color_from_hex("#666666")
            font_size: '14sp'
            halign: 'left'
            valign: 'top'
            text_size: self.width - 40, self.height - 40
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

<SetupScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex("#121212")
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label:
            id: setup_title
            text: "Setup Vault"
            font_size: '24sp'
            bold: True
            size_hint_y: 0.2
        Label:
            id: setup_instruction
            text: "Draw your unlock gesture anywhere"
            halign: 'center'
            size_hint_y: 0.2
        Widget:
            size_hint_y: 0.4
        Button:
            id: action_btn
            text: "Next"
            size_hint_y: 0.2
            background_normal: ''
            background_color: get_color_from_hex("#6200EA")
            on_release: root.next_step()

<PinScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex("#121212")
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        Label:
            id: pin_display
            text: "Enter PIN"
            font_size: '24sp'
            bold: True
            size_hint_y: 0.3
        GridLayout:
            cols: 3
            spacing: 15
            size_hint_y: 0.7
            Button:
                text: "1"; on_release: root.add_pin("1"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "2"; on_release: root.add_pin("2"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "3"; on_release: root.add_pin("3"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "4"; on_release: root.add_pin("4"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "5"; on_release: root.add_pin("5"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "6"; on_release: root.add_pin("6"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "7"; on_release: root.add_pin("7"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "8"; on_release: root.add_pin("8"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "9"; on_release: root.add_pin("9"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "C"; on_release: root.clear_pin(); background_color: get_color_from_hex("#6200EA")
            Button:
                text: "0"; on_release: root.add_pin("0"); background_color: get_color_from_hex("#1E1E1E")
            Button:
                text: "OK"; on_release: root.check_pin(); background_color: get_color_from_hex("#00E5FF")

<DashboardScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex("#121212")
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: 0.1
            padding: 10
            Label:
                text: "My Vault"
                font_size: '22sp'
                bold: True
                halign: 'left'
                text_size: self.size
        ScrollView:
            size_hint_y: 0.8
            GridLayout:
                id: apps_grid
                cols: 3
                spacing: 15
                padding: 15
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: 0.1
            spacing: 5
            padding: 5
            canvas.before:
                Color:
                    rgba: get_color_from_hex("#1E1E1E")
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "Vault"
                background_color: 0,0,0,0
                color: get_color_from_hex("#00E5FF")
            Button:
                text: "Add Apps"
                background_color: 0,0,0,0
                on_release: app.sm.current = 'add_apps'
            Button:
                text: "Settings"
                background_color: 0,0,0,0
                on_release: app.sm.current = 'settings'

<AddAppsScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex("#121212")
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: 0.1
            padding: 10
            Button:
                text: "< Back"
                size_hint_x: 0.3
                background_color: get_color_from_hex("#6200EA")
                on_release: app.sm.current = 'dashboard'
            Label:
                text: "Hide Installed Apps"
                font_size: '18sp'
                bold: True
        ScrollView:
            size_hint_y: 0.9
            GridLayout:
                id: installed_apps_grid
                cols: 1
                spacing: 10
                padding: 10
                size_hint_y: None
                height: self.minimum_height

<SettingsScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex("#121212")
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: 0.1
            padding: 10
            Button:
                text: "< Back"
                size_hint_x: 0.3
                background_color: get_color_from_hex("#6200EA")
                on_release: app.sm.current = 'dashboard'
            Label:
                text: "Settings"
                font_size: '18sp'
                bold: True
        ScrollView:
            size_hint_y: 0.9
            GridLayout:
                cols: 1
                spacing: 15
                padding: 15
                size_hint_y: None
                height: self.minimum_height
                CardButton:
                    text: "Change PIN"
                    size_hint_y: None
                    height: 60
                    on_release: app.reset_setup("pin")
                CardButton:
                    text: "Change Unlock Gesture"
                    size_hint_y: None
                    height: 60
                    on_release: app.reset_setup("gesture")
                CardButton:
                    text: "Change Theme (Glitch/System)"
                    size_hint_y: None
                    height: 60
                    on_release: app.toggle_theme()
                CardButton:
                    text: "Auto-Lock Timer"
                    size_hint_y: None
                    height: 60
                Label:
                    text: "Note: Deep hiding apps requires Root.\\nWithout root, apps launch securely from vault."
                    halign: 'center'
                    size_hint_y: None
                    height: 80
                    color: 0.6, 0.6, 0.6, 1
'''

# --- Gesture Recognition Logic ---
def get_angle(dx, dy):
    angle = math.atan2(dy, dx) * 180 / math.pi
    return angle + 360 if angle < 0 else angle

def angle_to_direction(angle):
    # 8-way directional mapping (0=E, 1=NE, 2=N, 3=NW, 4=W, 5=SW, 6=S, 7=SE)
    return round(angle / 45.0) % 8

def normalize_gesture(points):
    if len(points) < 5: return []
    sequence = []
    threshold = 20 # minimum pixel movement to register direction
    
    last_p = points[0]
    for p in points[1:]:
        dx = p[0] - last_p[0]
        dy = p[1] - last_p[1]
        dist = math.hypot(dx, dy)
        if dist > threshold:
            direction = angle_to_direction(get_angle(dx, dy))
            if not sequence or sequence[-1] != direction:
                sequence.append(direction)
            last_p = p
    return sequence

def fuzzy_match(seq1, seq2):
    # Perfect match or single-error tolerance
    if seq1 == seq2: return True
    if abs(len(seq1) - len(seq2)) > 1: return False
    
    # Calculate simple Levenshtein-like distance for 8-way directions
    diffs = 0
    min_len = min(len(seq1), len(seq2))
    for i in range(min_len):
        d1, d2 = seq1[i], seq2[i]
        # Allow slight diagonal deviations (e.g., N(2) vs NE(1))
        dist = min((d1-d2)%8, (d2-d1)%8)
        if dist > 1: 
            diffs += 2
        elif dist == 1:
            diffs += 1
    return diffs <= 2

# --- Screens ---
class GestureOverlay(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = []
        self.line = None
        self.is_recording = False
        self.callback = None
        
    def on_touch_down(self, touch):
        self.points = [(touch.x, touch.y)]
        self.is_recording = True
        return True
        
    def on_touch_move(self, touch):
        if self.is_recording:
            self.points.append((touch.x, touch.y))
        return True
        
    def on_touch_up(self, touch):
        if self.is_recording:
            self.is_recording = False
            seq = normalize_gesture(self.points)
            if self.callback and len(seq) > 0:
                self.callback(seq)
            self.points = []
        return True

class DisguiseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme = "system"
        self.overlay = GestureOverlay(size_hint=(1, 1))
        self.overlay.callback = self.handle_gesture
        self.add_widget(self.overlay)
        
    def on_enter(self):
        store = App.get_running_app().store
        self.theme = store.get('theme')['name'] if store.exists('theme') else 'system'
        if self.theme == "system":
            self.ids.fake_text.text = "Android Recovery\\n\\nApp corrupted.\\nFormat required.\\n\\nWaiting for ADB..."
        else:
            self.ids.fake_text.text = "0x000F FATAL EXCEPTION\\nSEG_FAULT_12049\\n\\nMEMORY DUMP IN PROGRESS [|]"
            
    def handle_gesture(self, sequence):
        app = App.get_running_app()
        store = app.store
        
        if not store.exists('setup'): return
        
        unlock_seq = store.get('setup')['unlock_gesture']
        panic_seq = store.get('setup')['panic_gesture']
        
        if fuzzy_match(sequence, unlock_seq):
            app.sm.transition = FadeTransition()
            app.sm.current = 'pin'
        elif fuzzy_match(sequence, panic_seq):
            # Panic -> instantly close app or reset UI
            self.ids.fake_text.text = "SYSTEM HALTED."

class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.temp_unlock = []
        self.temp_panic = []
        self.pin = ""
        self.overlay = GestureOverlay(size_hint=(1, 0.4), pos_hint={'center_y': 0.5})
        self.overlay.callback = self.handle_gesture
        self.add_widget(self.overlay)

    def on_enter(self):
        self.update_ui()
        
    def update_ui(self):
        if self.step == 1:
            self.ids.setup_instruction.text = "Draw UNLOCK gesture\\n(1/2)"
        elif self.step == 2:
            self.ids.setup_instruction.text = "Confirm UNLOCK gesture\\n(2/2)"
        elif self.step == 3:
            self.ids.setup_instruction.text = "Draw PANIC gesture\\n(Closes vault instantly)"
        elif self.step == 4:
            self.ids.setup_instruction.text = "Confirm PANIC gesture"
        elif self.step == 5:
            self.ids.setup_instruction.text = "Enter a 4-digit PIN\\n(In console/text area for now)"
            self.overlay.opacity = 0
        elif self.step == 6:
            self.ids.setup_instruction.text = "Setup Complete!\\nEntering Vault..."
            Clock.schedule_once(lambda dt: self.finish_setup(), 1.5)

    def handle_gesture(self, sequence):
        if self.step == 1:
            self.temp_unlock = sequence
            self.step = 2
        elif self.step == 2:
            if fuzzy_match(self.temp_unlock, sequence):
                self.step = 3
            else:
                self.ids.setup_instruction.text = "Mismatch! Try again.\\nDraw UNLOCK gesture (1/2)"
                self.step = 1
        elif self.step == 3:
            self.temp_panic = sequence
            self.step = 4
        elif self.step == 4:
            if fuzzy_match(self.temp_panic, sequence):
                self.step = 5
                # Directly ask for PIN via standard screen transition in a real app, 
                # here we fake it with button clicks for simplicity of single file
                App.get_running_app().sm.current = 'setup_pin'
            else:
                self.step = 3
        self.update_ui()

    def finish_setup(self):
        pass

class SetupPinScreen(Screen):
    # Auxiliary screen for setup PIN entry
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_pin = ""
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        self.label = Label(text="Set 4-Digit PIN", font_size='24sp', size_hint_y=0.2)
        layout.add_widget(self.label)
        
        grid = GridLayout(cols=3, spacing=15, size_hint_y=0.8)
        for i in range(1, 10):
            btn = Button(text=str(i), background_color=CARD_COLOR)
            btn.bind(on_release=lambda btn: self.add_num(btn.text))
            grid.add_widget(btn)
        
        btn_clr = Button(text="C", background_color=ACCENT_PURPLE)
        btn_clr.bind(on_release=lambda x: self.clear())
        grid.add_widget(btn_clr)
        
        btn_0 = Button(text="0", background_color=CARD_COLOR)
        btn_0.bind(on_release=lambda btn: self.add_num(btn.text))
        grid.add_widget(btn_0)
        
        btn_ok = Button(text="OK", background_color=ACCENT_BLUE)
        btn_ok.bind(on_release=lambda x: self.submit())
        grid.add_widget(btn_ok)
        
        layout.add_widget(grid)
        self.add_widget(layout)
        
    def add_num(self, num):
        if len(self.temp_pin) < 8:
            self.temp_pin += num
            self.label.text = "*" * len(self.temp_pin)
            
    def clear(self):
        self.temp_pin = ""
        self.label.text = "Set 4-Digit PIN"
        
    def submit(self):
        if len(self.temp_pin) >= 4:
            app = App.get_running_app()
            setup_scr = app.sm.get_screen('setup')
            app.store.put('setup', 
                          unlock_gesture=setup_scr.temp_unlock, 
                          panic_gesture=setup_scr.temp_panic, 
                          pin=self.temp_pin)
            app.store.put('theme', name='system')
            app.sm.current = 'dashboard'

class PinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entered = ""
        self.attempts = 0
        # Hidden camera for intruder selfie
        self.camera = Camera(resolution=(640, 480), play=True, opacity=0)
        self.add_widget(self.camera)
        
    def on_enter(self):
        self.entered = ""
        self.ids.pin_display.text = "Enter PIN"
        self.camera.play = True
        
    def add_pin(self, val):
        self.entered += val
        self.ids.pin_display.text = "*" * len(self.entered)
        
    def clear_pin(self):
        self.entered = ""
        self.ids.pin_display.text = "Enter PIN"
        
    def check_pin(self):
        store = App.get_running_app().store
        correct_pin = store.get('setup')['pin']
        
        if self.entered == correct_pin:
            self.attempts = 0
            self.camera.play = False
            App.get_running_app().sm.transition = SlideTransition(direction="up")
            App.get_running_app().sm.current = 'dashboard'
        else:
            self.attempts += 1
            self.clear_pin()
            self.ids.pin_display.text = "Wrong PIN"
            if self.attempts >= 3:
                # Capture silent photo
                if HAS_ANDROID:
                    self.camera.export_to_png(f"/sdcard/DCIM/intruder_{time.time()}.png")
                # Back to disguise
                self.attempts = 0
                App.get_running_app().sm.current = 'disguise'

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.load_hidden_apps()
        
    def load_hidden_apps(self):
        grid = self.ids.apps_grid
        grid.clear_widgets()
        store = App.get_running_app().store
        
        if not store.exists('hidden_apps'):
            store.put('hidden_apps', apps=[])
            
        hidden = store.get('hidden_apps')['apps']
        if not hidden:
            grid.add_widget(Label(text="No hidden apps yet.\nTap 'Add Apps' below.", size_hint_y=None, height=200, color=(0.5,0.5,0.5,1)))
            return
            
        for pkg in hidden:
            btn = Button(text=pkg.split('.')[-1], size_hint_y=None, height=100, background_color=CARD_COLOR)
            btn.bind(on_release=lambda instance, p=pkg: self.launch_app(p))
            grid.add_widget(btn)

    def launch_app(self, pkg_name):
        if HAS_ANDROID:
            try:
                context = PythonActivity.mActivity
                pm = context.getPackageManager()
                intent = pm.getLaunchIntentForPackage(pkg_name)
                if intent:
                    context.startActivity(intent)
            except Exception as e:
                print("Launch failed:", e)

class AddAppsScreen(Screen):
    def on_pre_enter(self):
        self.populate_apps()
        
    def populate_apps(self):
        grid = self.ids.installed_apps_grid
        grid.clear_widgets()
        
        app_list = []
        if HAS_ANDROID:
            try:
                context = PythonActivity.mActivity
                pm = context.getPackageManager()
                packages = pm.getInstalledPackages(0)
                for i in range(packages.size()):
                    pkg = packages.get(i)
                    if pm.getLaunchIntentForPackage(pkg.packageName):
                        name = pkg.applicationInfo.loadLabel(pm).toString()
                        app_list.append((name, pkg.packageName))
            except Exception:
                pass
        
        if not app_list:
            app_list = [("Mock Facebook", "com.facebook.katana"), ("Mock Instagram", "com.instagram.android"), ("Mock WhatsApp", "com.whatsapp")]
            
        store = App.get_running_app().store
        hidden = store.get('hidden_apps')['apps'] if store.exists('hidden_apps') else []
        
        for name, pkg in sorted(app_list):
            box = BoxLayout(size_hint_y=None, height=60, spacing=10)
            lbl = Label(text=name, size_hint_x=0.7, halign='left')
            lbl.bind(size=lbl.setter('text_size'))
            
            is_hidden = pkg in hidden
            btn = Button(text="Unhide" if is_hidden else "Hide", 
                         size_hint_x=0.3,
                         background_color=ACCENT_BLUE if not is_hidden else ACCENT_PURPLE)
            btn.bind(on_release=lambda instance, p=pkg, b=btn: self.toggle_hide(p, b))
            
            box.add_widget(lbl)
            box.add_widget(btn)
            grid.add_widget(box)

    def toggle_hide(self, pkg_name, btn):
        store = App.get_running_app().store
        hidden = store.get('hidden_apps')['apps'] if store.exists('hidden_apps') else []
        
        if pkg_name in hidden:
            hidden.remove(pkg_name)
            btn.text = "Hide"
            btn.background_color = ACCENT_BLUE
            # Attempt to unhide via root shell
            if HAS_ANDROID:
                subprocess.call(['su', '-c', f'pm enable {pkg_name}'])
        else:
            hidden.append(pkg_name)
            btn.text = "Unhide"
            btn.background_color = ACCENT_PURPLE
            # Attempt to hide via root shell (will silently fail if not rooted)
            if HAS_ANDROID:
                subprocess.call(['su', '-c', f'pm disable-user {pkg_name}'])
                subprocess.call(['su', '-c', f'pm hide {pkg_name}'])
                
        store.put('hidden_apps', apps=hidden)

class SettingsScreen(Screen):
    pass

# --- Main App ---
class VaultApp(App):
    def build(self):
        Builder.load_string(KV_UI)
        self.store = JsonStore('vault_config.json')
        
        # Request Android Permissions on startup
        if HAS_ANDROID:
            request_permissions([
                Permission.CAMERA,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        self.sm = ScreenManager()
        self.sm.add_widget(DisguiseScreen(name='disguise'))
        self.sm.add_widget(SetupScreen(name='setup'))
        self.sm.add_widget(SetupPinScreen(name='setup_pin'))
        self.sm.add_widget(PinScreen(name='pin'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(AddAppsScreen(name='add_apps'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        
        if self.store.exists('setup'):
            self.sm.current = 'disguise'
        else:
            self.sm.current = 'setup'
            
        return self.sm

    def toggle_theme(self):
        current = self.store.get('theme')['name'] if self.store.exists('theme') else 'system'
        new_theme = 'glitch' if current == 'system' else 'system'
        self.store.put('theme', name=new_theme)
        # Update disguise screen
        ds = self.sm.get_screen('disguise')
        ds.theme = new_theme
        ds.on_enter() # refresh text

    def reset_setup(self, reset_type="pin"):
        # Helper to allow changing pin or gesture
        self.store.delete('setup')
        self.sm.current = 'setup'

if __name__ == '__main__':
    VaultApp().run()
