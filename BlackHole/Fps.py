import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os

class VideoMakerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Generator from Frames")
        self.geometry("700x700")
        self.create_widgets()

    def create_widgets(self):
        # Frames Folder
        tk.Label(self, text="Frames Folder:").pack(anchor='w', padx=10, pady=(10,0))
        frame = tk.Frame(self)
        frame.pack(fill='x', padx=10)
        self.folder_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.folder_var).pack(side='left', fill='x', expand=True)
        tk.Button(frame, text="Select", command=self.select_folder).pack(side='right')

        # Name Pattern
        tk.Label(self, text="Name Pattern Type:").pack(anchor='w', padx=10, pady=(10,0))
        pattern_frame = tk.Frame(self)
        pattern_frame.pack(fill='x', padx=10)
        self.pattern_type = tk.StringVar(value="sequence")
        ttk.Combobox(pattern_frame, textvariable=self.pattern_type,
                     values=["glob", "sequence"], state='readonly', width=10).pack(side='left')
        self.seq_pattern_var = tk.StringVar(value="%04d.png")
        tk.Entry(pattern_frame, textvariable=self.seq_pattern_var).pack(side='left', fill='x', expand=True, padx=5)
        info_txt = (
            "glob: Uses wildcard *.png (requires support in the build).\n"
            "sequence: Sequential name, e.g., frame0001.png to frame9999.png."
        )
        tk.Button(pattern_frame, text="?", width=2,
                  command=lambda: messagebox.showinfo("Pattern Info", info_txt)).pack(side='left')

        # Resolution
        tk.Label(self, text="Resolution:").pack(anchor='w', padx=10, pady=(10,0))
        resolutions = [
            "1280x720 (720p)",
            "1920x1080 (1080p)",
            "2560x1440 (2K)",
            "3840x2160 (4K)",
            "7680x4320 (8K)"
        ]
        self.res_var = tk.StringVar(value=resolutions[1])
        ttk.Combobox(self, textvariable=self.res_var, values=resolutions, state='readonly').pack(fill='x', padx=10)

        # Output Format
        tk.Label(self, text="Output Format:").pack(anchor='w', padx=10, pady=(10,0))
        formats = ["MP4", "MKV", "MOV", "AVI"]
        self.format_var = tk.StringVar(value=formats[0])
        ttk.Combobox(self, textvariable=self.format_var, values=formats, state='readonly').pack(fill='x', padx=10)

        # Format Explanation
        info = (
            "MP4: High compatibility and streaming.\n"
            "MKV: Supports multiple audio/subtitle tracks.\n"
            "MOV: Ideal for Apple ecosystem.\n"
            "AVI: Old format, large file size."
        )
        tk.Label(self, text=info, justify='left', fg='gray').pack(fill='x', padx=10, pady=(5,10))

        # Additional Parameters
        params_frame = tk.LabelFrame(self, text="Video Parameters")
        params_frame.pack(fill='x', padx=10, pady=10)

        def add_info(parent, row, text):
            tk.Button(parent, text="?", width=2,
                      command=lambda: messagebox.showinfo("Info", text)).grid(row=row, column=2, padx=5)

        # Frame Rate
        tk.Label(params_frame, text="Frame Rate (fps):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.fps_var = tk.IntVar(value=24)
        tk.Spinbox(params_frame, from_=1, to=120, textvariable=self.fps_var, width=5).grid(row=0, column=1, padx=5)
        add_info(params_frame, 0, "Number of frames per second.")

        # Preset
        tk.Label(params_frame, text="Preset:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        presets = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower"]
        self.preset_var = tk.StringVar(value="slow")
        ttk.Combobox(params_frame, textvariable=self.preset_var, values=presets, state='readonly', width=10).grid(row=1, column=1, padx=5)
        add_info(params_frame, 1, "Speed vs compression.")

        # CRF
        tk.Label(params_frame, text="CRF (0-51):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.crf_var = tk.IntVar(value=18)
        tk.Spinbox(params_frame, from_=0, to=51, textvariable=self.crf_var, width=5).grid(row=2, column=1, padx=5)
        add_info(params_frame, 2, "Constant quality, 0=lossless, 23=default.")

        # Bitrate
        tk.Label(params_frame, text="Bitrate (kbps):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.bitrate_var = tk.IntVar(value=4000)
        tk.Spinbox(params_frame, from_=100, to=100000, increment=100, textvariable=self.bitrate_var, width=7).grid(row=3, column=1, padx=5)
        add_info(params_frame, 3, "Maximum bitrate.")

        # H.264 Profile
        tk.Label(params_frame, text="H.264 Profile:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        profiles = ["baseline", "main", "high", "high10", "high422", "high444"]
        self.profile_var = tk.StringVar(value="high")
        ttk.Combobox(params_frame, textvariable=self.profile_var, values=profiles, state='readonly', width=10).grid(row=4, column=1, padx=5)
        add_info(params_frame, 4, "Selects color profile and compatibility.")

        # Pixel Format
        tk.Label(params_frame, text="Pixel Format:").grid(row=5, column=0, sticky='w', padx=5, pady=5)
        pixfmts = ["yuv420p", "yuv422p", "yuv444p", "yuva420p"]
        self.pixfmt_var = tk.StringVar(value="yuv420p")
        ttk.Combobox(params_frame, textvariable=self.pixfmt_var, values=pixfmts, state='readonly', width=10).grid(row=5, column=1, padx=5)
        add_info(params_frame, 5, "Pixel format: yuv420p compatible with most players.")

        # Tune
        tk.Label(params_frame, text="Tune:").grid(row=6, column=0, sticky='w', padx=5, pady=5)
        tunes = ["film", "animation", "grain", "stillimage", "fastdecode", "zerolatency"]
        self.tune_var = tk.StringVar(value="film")
        ttk.Combobox(params_frame, textvariable=self.tune_var, values=tunes, state='readonly', width=10).grid(row=6, column=1, padx=5)
        add_info(params_frame, 6, "Settings for content type.")

        # GOP Size
        tk.Label(params_frame, text="GOP Size (keyint):").grid(row=7, column=0, sticky='w', padx=5, pady=5)
        self.gop_var = tk.IntVar(value=250)
        tk.Spinbox(params_frame, from_=1, to=10000, textvariable=self.gop_var, width=7).grid(row=7, column=1, padx=5)
        add_info(params_frame, 7, "Frames between keyframes.")

        # Save Video
        tk.Label(self, text="Save video to:").pack(anchor='w', padx=10)
        out_frame = tk.Frame(self)
        out_frame.pack(fill='x', padx=10)
        self.output_var = tk.StringVar()
        tk.Entry(out_frame, textvariable=self.output_var).pack(side='left', fill='x', expand=True)
        tk.Button(out_frame, text="Select", command=self.select_output).pack(side='right')

        # Generate Button
        tk.Button(self, text="Generate Video", command=self.generate_video, bg='#4CAF50', fg='white', padx=10, pady=5).pack(pady=20)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def select_output(self):
        fmt = self.format_var.get().lower()
        filetypes = [(f"Video (*.{fmt})", f"*.{fmt}"), ("All files", "*")]
        path = filedialog.asksaveasfilename(defaultextension=f".{fmt}", filetypes=filetypes)
        if path:
            self.output_var.set(path)

    def generate_video(self):
        inp = self.folder_var.get()
        out = self.output_var.get()
        if not inp or not out:
            messagebox.showerror("Error", "Frames folder and output file must be selected.")
            return

        width, height = self.res_var.get().split()[0].split('x')
        opts = ["-framerate", str(self.fps_var.get())]
        if self.pattern_type.get() == "glob":
            opts += ["-pattern_type", "glob", "-i", os.path.join(inp, "*.png")]
        else:
            opts += ["-i", os.path.join(inp, self.seq_pattern_var.get())]
        opts += ["-s", f"{width}x{height}",
                 "-c:v", "libx264",
                 "-preset", self.preset_var.get(),
                 "-crf", str(self.crf_var.get()),
                 "-b:v", f"{self.bitrate_var.get()}k",
                 "-profile:v", self.profile_var.get(),
                 "-pix_fmt", self.pixfmt_var.get(),
                 "-tune", self.tune_var.get(),
                 "-g", str(self.gop_var.get()),
                 out]
        try:
            subprocess.run(["ffmpeg"] + opts, check=True)
            messagebox.showinfo("Success", f"Video generated at {out}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("FFmpeg Error", str(e))

if __name__ == "__main__":
    app = VideoMakerApp()
    app.mainloop()