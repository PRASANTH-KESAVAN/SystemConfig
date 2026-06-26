from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock

# The Kivy UI layout defined as a string for simplicity
KV = '''
ScreenManager:
    CrashScreen:
    PinScreen:
    VaultScreen:

<CrashScreen>:
    name: 'crash_screen'
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    Label:
        text: "System Error 0x000F\\nApp Corrupted."
        color: 1, 0, 0, 1
        font_size: '20sp'
        halign: 'center'

<PinScreen>:
    name: 'pin_screen'
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 20
        
        Label:
            id: pin_label
            text: "Enter PIN"
            font_size: '24sp'
            size_hint_y: 0.2
            
        TextInput:
            id: pin_input
            password: True
            input_type: 'number'
            font_size: '30sp'
            halign: 'center'
            multiline: False
            size_hint_y: 0.2
            
        Button:
            text: "Unlock"
            size_hint_y: 0.2
            background_color: 0.2, 0.6, 1, 1
            on_release: root.check_pin(pin_input.text)
            
        Widget:
            size_hint_y: 0.4

<VaultScreen>:
    name: 'vault_screen'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        
        Label:
            text: "Hidden App Vault"
            font_size: '24sp'
            size_hint_y: 0.1
            
        BoxLayout:
            orientation: 'vertical'
            spacing: 10
            # Placeholder for hidden apps/data
            Button:
                text: "Hidden App 1"
            Button:
                text: "Hidden App 2"
            Button:
                text: "Hidden App 3"
                
        Button:
            text: "Lock and Exit"
            size_hint_y: 0.1
            background_color: 1, 0, 0, 1
            on_release: root.lock_app()
'''

class CrashScreen(Screen):
    def __init__(self, **kwargs):
        super(CrashScreen, self).__init__(**kwargs)
        self.touch_points = []

    def on_touch_down(self, touch):
        # Start recording touch points when user touches screen
        self.touch_points = [touch.pos]
        return True

    def on_touch_move(self, touch):
        # Record points as user drags finger
        self.touch_points.append(touch.pos)
        return True

    def on_touch_up(self, touch):
        # Analyze the drawn shape when user lifts finger
        if len(self.touch_points) < 15:
            return True # Not enough points to be a shape
            
        start_p = self.touch_points[0]
        end_p = self.touch_points[-1]
        
        # Get the lowest point drawn (minimum Y value)
        min_y = min(p[1] for p in self.touch_points)
        
        # LOGIC TO DETECT A "U" SHAPE:
        # 1. Starts high, dips down, ends high.
        # 2. Moves from left to right.
        dip_from_start = start_p[1] - min_y
        dip_from_end = end_p[1] - min_y
        left_to_right = end_p[0] - start_p[0]
        
        # If the shape dips by at least 100 pixels and moves right
        if dip_from_start > 100 and dip_from_end > 100 and left_to_right > 50:
            print("U Shape Detected!")
            self.manager.current = 'pin_screen'
            
        self.touch_points = [] # Reset
        return True

class PinScreen(Screen):
    def check_pin(self, entered_pin):
        # Set your desired PIN here
        CORRECT_PIN = "1234" 
        
        if entered_pin == CORRECT_PIN:
            self.ids.pin_input.text = ""
            self.ids.pin_label.text = "Enter PIN"
            self.manager.current = 'vault_screen'
        else:
            self.ids.pin_label.text = "Incorrect PIN!"
            self.ids.pin_input.text = ""

class VaultScreen(Screen):
    def lock_app(self):
        # Go back to the fake crash screen
        self.manager.current = 'crash_screen'

class HiddenVaultApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    HiddenVaultApp().run()