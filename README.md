# manim_in_kivy
Rendering MANIM animations directly on a Kivy application with OpenGL

https://user-images.githubusercontent.com/23220309/176371321-3aff84c2-f7d7-4f8b-b08d-1e643e8bbfc5.mp4

If you want to render MANIM animations on a mobile app, the first step is being able to render MANIM inside Kivy.

1) First, install [MANIM](https://www.manim.community/) and [Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html)

Hacking MANIM

2) modify the file `manim.renderer.opengl_renderer.OpenGLRenderer`.
Inside `OpenGLRenderer`, modify the function `get_raw_frame_buffer_object_data`: we are going to intercept the frames that would be sent to `ffmpeg` and send them to Kivy

```python
    def get_raw_frame_buffer_object_data(self, dtype="f1"):
        # Copy blocks from the fbo_msaa to the drawn fbo using Blit
        # pw, ph = self.get_pixel_shape()
        # gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.fbo_msaa.glo)
        # gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, self.fbo.glo)
        # gl.glBlitFramebuffer(
        #     0, 0, pw, ph, 0, 0, pw, ph, gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR
        # )
        num_channels = 4
        ret = self.frame_buffer_object.read(
            viewport=self.frame_buffer_object.viewport,
            components=num_channels,
            dtype=dtype,
        )
        from kivy.app import App
        app = App.get_running_app()
        app.update_frame_to_render(ret)
        return ret
```

3) Run `main.py`

4) Enjoy rendering MANIM animations inside a cross-platform Kivy app.

Optional:

I you want to make sure ffmpeg is not used, go to `manim.scene.scene_file_writer.SceneFileWriter` and change the function `write_opengl_frame`:
```python
    def write_opengl_frame(self, renderer):
        if write_to_movie():
            renderer.get_raw_frame_buffer_object_data(),

            # self.writing_process.stdin.write(
            #     renderer.get_raw_frame_buffer_object_data(),
            # )
        elif is_png_format() and not config["dry_run"]:
            target_dir = self.image_file_path.parent / self.image_file_path.stem
            extension = self.image_file_path.suffix
            self.output_image(
                renderer.get_image(),
                target_dir,
                extension,
                config["zero_pad"],
            )
```




