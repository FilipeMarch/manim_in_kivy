
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import numpy as np

from manim import *
config.disable_caching = True
config.pixel_height = 1080
config.pixel_width = 1920
config.background_color = '#161925'

from kivy.core.window import Window
Window.size = (1920, 1130)

# Manim animation that will be rendered
class MyAnimationTest(Scene):
    def construct(self):
        cp = ComplexPlane(x_range=[-60, 60], y_range=[-60, 60])
        cp.scale(1/8)
        cp.prepare_for_nonlinear_transform()

        self.play(Create(cp), run_time=3)
        self.play(cp.animate.apply_complex_function(lambda z: z**3), run_time=3)
        self.wait()


# The image object to display inside Kivy, using the texture from the animation
class ManimCanvas(F.Image):
    arrays = F.ListProperty()
    total_number_of_frames = F.NumericProperty(0)
    total_number_of_frames_string = F.StringProperty()
    frame_index = F.NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texture = self.create_texture()
        self.anim = Clock.schedule_interval(self.update_texture, 1/15)
        Clock.schedule_once(self.save_app_variable)

    def save_app_variable(self, *args):
        """
        Saves the app variable to later update the string `number_of_frames_rendered`
        """
        self.app = App.get_running_app()

    def create_texture(self, size=(1920, 1080)):
        """
        Create a texture to display the animation.
        """
        texture = Texture.create(
            size = size,
            colorfmt = "rgba"
        )
        texture.flip_vertical()
        return texture
        
    def update_texture(self, *args):
        """
        Update the texture with the next frame.
        """
        
        # If already rendered all frames, reset the frame_index so we can loop the animation
        if self.frame_index > self.total_number_of_frames-1:
            self.frame_index = 0
        
        # If there are frames to be rendered
        if self.arrays:
            # Update the strings so we can visualize the total number of frames calculated and rendered
            self.app.number_of_frames_rendered = f'Number of frames rendered: {self.frame_index}'
            self.total_number_of_frames_string = f'Total number of frames: {self.total_number_of_frames}'
            
            # Current frame
            frame = self.arrays[self.frame_index]
            
            # Checking the renderer
            if config.renderer != 'opengl':
                # This would be Cairo renderer
                buf = frame.tobytes()
                self.texture.blit_buffer(buf, colorfmt="rgba", bufferfmt="ubyte")
            else:
                # OpenGL renderer
                self.texture.blit_buffer(frame, colorfmt="rgba", bufferfmt="ubyte")
                
            # Updating the frame_index
            self.frame_index += 1
        

    def start_rendering(self, *args):
        """
        Starts rendering the animation.
        """

        # Create a thread to start rendering, so we can visualize the frames while they are being created by MANIM
        import threading
        thread = threading.Thread(target=self.render_animation)
        thread.start()

    def render_animation(self, *args):
        """
        Renders an animation,
        Unschedule and schedule `update_texture` to a higher FPS (from 15 FPS to 60 FPS)
        """
        print('Starting to render animation')
        s = MyAnimationTest()
        app = App.get_running_app()
        s.render(False, app)
        Clock.unschedule(self.update_texture)
        Clock.schedule_interval(self.update_texture, 1/60)

class MainScreen(F.Screen):
    pass


Builder.load_string('''
<MainScreen>:
    manim_canvas: manim_canvas.__self__
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: self.minimum_height
            Label:
                text: app.number_of_frames_rendered
            Button:
                size_hint: None, None
                size: dp(150), dp(50)
                text: 'Start Rendering'
                pos_hint: {'center_x': .5}
                on_release: manim_canvas.start_rendering()
            Label:
                text: manim_canvas.total_number_of_frames_string
        ManimCanvas:
            id: manim_canvas
''')


class MainApp(App):
    frames = F.ListProperty([])
    number_of_frames_rendered = F.StringProperty('')

    def build(self):
        self.main_screen = MainScreen()
        return self.main_screen

    def update_frame_to_render(self, frame):
        """
        Every time a frame is rendered, i.e., a `np.array` is calculated by manim (if using Cairo as renderer) or `bytes` (if using OpenGL),
        this function is called, adding the `np.array` (or `bytes`) to the list of arrays.
        """
        self.main_screen.manim_canvas.total_number_of_frames += 1
        self.main_screen.manim_canvas.arrays.append(frame)


MainApp().run()
