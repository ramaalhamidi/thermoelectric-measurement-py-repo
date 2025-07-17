# V-t sweep, V-T plot, Seebeck Measurement
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import csv, time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk

class VTTab(ttk.Frame):
    def __init__(self, parent, sourcemeter, multimeter):
        super().__init__(parent, style='WhiteFrame.TFrame')
        self.k2401 = sourcemeter
        self.k2000 = multimeter
        
        self.timestamps = []
        self.voltages = []

        self.step_voltages = []

        self.running = False
        self.idx = 0
        self.update_job = None
        self.current_job = None

        self._build_widgets()

    def _build_widgets(self):
        img = Image.open("C:\\Users\\ramaa\\Desktop\\Thermo\\QEERI_logo.png")
        img = img.resize((200, 50), Image.Resampling.LANCZOS)
        self.logo_img = ImageTk.PhotoImage(img)            

        logo_lbl = tk.Label(self, image=self.logo_img, bg="#fafcff")
        logo_lbl.pack(side=tk.TOP, pady=(20, 10))

        title = tk.Label(self, text="2-wire V-t measurement", font=("Space Grotesk", 28), bg="#fafcff")
        title.pack(pady=(20, 20))
        
        input_frame = tk.Frame(self, bg="white", bd=1, relief="solid")
        input_frame.pack(pady=10, padx=40, fill="x", ipady=10)

        file_frame = tk.Frame(input_frame, bg="white")
        file_frame.pack(side=tk.TOP, padx=(0, 20), fill="x", expand=True)

        file = tk.Label(file_frame, text="Enter file destination:", font=("Space Grotesk", 16), bg="white")
        file.pack(side=tk.LEFT, padx=(20, 5))
        self.file_entry = tk.Entry(file_frame, width=50, bg="#fafcff", relief="flat", highlightthickness=1, highlightbackground="#d0d6e0")
        self.file_entry.insert(0, 'C:\\Users\\username\\Desktop\\Vt.csv')
        self.file_entry.pack(side=tk.LEFT, padx=(5, 0), fill="x", expand=False)

        current_frame = tk.Frame(input_frame, bg="white")
        current_frame.pack(side=tk.BOTTOM, padx=(0, 20), fill="x", expand=True)
        tk.Label(current_frame, text="Current:", font=("Space Grotesk", 16), bg="white").pack(side=tk.LEFT, padx=(20, 100))

        self.entries = {}
        for var in ["MIN", "MAX", "STEP", "STEP DURATION (s)"]:
            col = tk.Frame(current_frame, bg="white")
            col.pack(side=tk.LEFT, padx=5)
            tk.Label(col, text=var, bg="white").pack()
            ent = tk.Entry(col, width=12, bg="#fafcff", relief="flat",
                            highlightthickness=1, highlightbackground="#d0d6e0")
            ent.pack(pady=(2, 0))
            self.entries[var] = ent

        unit_col = tk.Frame(current_frame, bg="white")
        unit_col.pack(side=tk.LEFT, padx=5)

        tk.Label(unit_col, text="UNIT", bg="white").pack(pady=(0, 5))
        self.unit_opt = tk.StringVar(value="mA")
        unit_menu = tk.OptionMenu(unit_col, self.unit_opt, "nA", "μA", "mA", "A")
        unit_menu.config(bg="white", bd=0, highlightthickness=0)
        unit_menu.pack()

        btn_frame = tk.Frame(current_frame, bg='white')
        btn_frame.pack(side='right', padx=(0,20))
        self.start_btn = ttk.Button(btn_frame, text="Start", style='Purple.TButton', command=self.measure_live)
        self.start_btn.pack(side='left', padx=5)
        self.stop_btn = ttk.Button(btn_frame, text="Stop", style='Purple.TButton', command=self.stop)
        self.stop_btn.pack(side='left', padx=5)

        plot_frame = tk.Frame(self, bg='white', bd=1, relief='solid')
        plot_frame.pack(pady=10, padx=40, fill='both', expand=True, ipady=10)
        self.fig = Figure(figsize=(8,4), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Voltage vs Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.grid(True)
        self.line, = self.ax.plot([], [], marker='o', linestyle='-')

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def measure_live(self):
        try:
            min_val = float(self.entries["MIN"].get())
            max_val = float(self.entries["MAX"].get())
            step_val = float(self.entries["STEP"].get())
            step_dur = float(self.entries["STEP DURATION (s)"].get())
        except ValueError:
            messagebox.showerror("Input Error", "Enter valid numeric parameters.")
            return
        unit = self.unit_opt.get()
        conv = {"nA":1e-9, "μA":1e-6, "mA":1e-3, "A":1}[unit]
        self.currents = list(
            np.arange(min_val * conv,
                      max_val * conv + step_val * conv/2,
                      step_val * conv)
        )
        self.step_duration = step_dur
        self.total_duration = self.step_duration * len(self.currents)

        self.start_btn.config(state='disabled')
        self.running = True
        self.idx = 0
        self.timestamps.clear()
        self.voltages.clear()
        self.start_time = time.time()

        self.k2401.output_on()
        self.k2401.set_compliance(21)

        self.step_voltages.clear()
        self.current_steps()
        self.update_plot()

    def _record_step_voltage(self):
        v = self.k2000.measure_voltage()
        self.step_voltages.append(v)

    def current_steps(self):
        if self.idx >= len(self.currents):
            self.stop(save_only=True)
            return

        c = self.currents[self.idx]
        self.k2401.source_current(c)
        
        buffer_ms = 100
        delay_ms = int(self.step_duration * 1000) - buffer_ms
        if delay_ms > 0:
            self.after(delay_ms, self._record_step_voltage)

        self.idx += 1

        self.current_job = self.after(
            int(self.step_duration * 1000),
            self.current_steps
        )

    def update_plot(self):
        if not self.running:
            return
        elapsed = time.time() - self.start_time
        if elapsed >= self.total_duration:
            self.stop(save_only=True)
            return
        v = self.k2000.measure_voltage()
        self.timestamps.append(elapsed)
        self.voltages.append(v)
        self.line.set_data(self.timestamps, self.voltages)
        if self.timestamps:
            xmin, xmax = min(self.timestamps), max(self.timestamps)
            pad_x = (xmax-xmin)*0.05 if xmax>xmin else 1
            ymin, ymax = min(self.voltages), max(self.voltages)
            pad_y = (ymax-ymin)*0.05 if ymax>ymin else 0.1
            self.ax.set_xlim(xmin-pad_x, xmax+pad_x)
            self.ax.set_ylim(ymin-pad_y, ymax+pad_y)
        self.canvas.draw_idle()
        self.update_job = self.after(100, self.update_plot)

    def stop(self, save_only=False):
        if self.running:
            self.running = False
            if self.current_job:
                self.after_cancel(self.current_job)
            if self.update_job:
                self.after_cancel(self.update_job)
            self.k2401.output_off()
        self._save_csv()
        self.start_btn.config(state='normal')
        print(self.step_voltages)

    def _save_csv(self):
        path = self.file_entry.get().strip()
        if not path:
            messagebox.showerror("Save Error", "Enter a valid file name.")
            return
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time_s','Voltage_V','Current_A'])
                for t, v in zip(self.timestamps, self.voltages):
                    curr = self.currents[min(self.idx-1, len(self.currents)-1)]
                    writer.writerow([f"{t:.2f}", f"{v:.6e}", f"{curr:.2e}"])
        except Exception as e:
            messagebox.showerror("Save Error", str(e))