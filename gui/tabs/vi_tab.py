# V-I sweep, plot, geometry
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data.logger import CsvLogger
from utils.conversions import to_amperes
from numpy import polyfit
from PIL import Image, ImageTk

class VITab(ttk.Frame):
    def __init__(self, parent, keithley2401_controller):
        super().__init__(parent, style='WhiteFrame.TFrame')
        self.keithley = keithley2401_controller
        self.logger = CsvLogger()
        self.c_data = []
        self.v_data = []
        self._build_widgets()

    def _build_widgets(self):    
        img = Image.open("C:\\Users\\ramaa\\Desktop\\Thermo\\QEERI_logo.png")
        img = img.resize((200, 50), Image.Resampling.LANCZOS)
        self.logo_img = ImageTk.PhotoImage(img)            

        logo_lbl = tk.Label(self, image=self.logo_img, bg="#fafcff")
        logo_lbl.pack(side=tk.TOP, pady=(20, 10))

        title = tk.Label(self, text="4-wire V-I measurement", font=("Space Grotesk", 28), bg="#fafcff")
        title.pack(pady=(20, 20))

        input_frame = tk.Frame(self, bg="white", bd=1, relief="solid")
        input_frame.pack(pady=5, padx=40, fill="x", ipady=10)

        file_frame = tk.Frame(input_frame, bg="white")
        file_frame.pack(side=tk.TOP, padx=(0, 20), fill="x", expand=True)
        file_label = tk.Label(file_frame, text="Enter file destination:", font=("Space Grotesk", 16), bg="white")
        file_label.pack(side=tk.LEFT, padx=(20, 5))
        self.file_entry = tk.Entry(file_frame, width=50, bg="#fafcff", relief="flat",
                                   highlightthickness=1, highlightbackground="#d0d6e0")
        self.file_entry.insert(0, "C:\\Users\\username\\Desktop\\VI_sweep.csv")
        self.file_entry.pack(side=tk.LEFT, padx=(5, 0), fill="x", expand=False)

        current_frame = tk.Frame(input_frame, bg="white")
        current_frame.pack(side=tk.BOTTOM, padx=(0, 20), fill="x", expand=True)
        tk.Label(current_frame, text="Current:", font=("Space Grotesk", 16), bg="white").pack(side=tk.LEFT, padx=(20, 100))

        self.entries = {}
        for var in ["MIN", "MAX", "STEP", "COMPLIANCE"]:
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

        button_col = tk.Frame(current_frame, bg="white")
        button_col.pack(side=tk.RIGHT, padx=(10, 0), pady=(23, 0))
        self.start_btn = ttk.Button(button_col, text="Start", style='Purple.TButton', command=self.measure_live)
        self.start_btn.pack(side=tk.LEFT, padx=(10, 5))
        self.clear_btn = ttk.Button(button_col, text="Clear", style='Purple.TButton', command=self.clear_data)
        self.clear_btn.pack(side=tk.RIGHT, padx=(10, 5))

        plot_frame = tk.Frame(self, bg="white", bd=1, relief="solid")
        plot_frame.pack(pady=10, padx=40, fill="x", ipady=20)

        self.fig = Figure(figsize=(8, 4), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.ax.autoscale_view()
        self.ax.set_title("V–I Plot")
        self.ax.set_xlabel("Current (A)")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.grid(True)
        self.line, = self.ax.plot([], [], marker='o', linestyle='-')

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        geo_frame = tk.Frame(self, bg="#fafcff")
        geo_frame.pack(pady=10, padx=40, fill="x", ipady=20)

        geo_row1 = tk.Frame(geo_frame, bg="#fafcff")
        geo_row1.pack(fill="x", pady=(0, 5))
        tk.Label(geo_row1, text="Sample Length (cm):", bg="#fafcff").pack(side=tk.LEFT)
        self.length_entry = tk.Entry(geo_row1, width=10, bg="#fafcff", relief="flat", highlightthickness=1, highlightbackground="#d0d6e0")
        self.length_entry.pack(side=tk.LEFT, padx=(5, 20))

        tk.Label(geo_row1, text="Sample Width (cm):", bg="#fafcff").pack(side=tk.LEFT)
        self.width_entry = tk.Entry(geo_row1, width=10, bg="#fafcff", relief="flat", highlightthickness=1, highlightbackground="#d0d6e0")
        self.width_entry.pack(side=tk.LEFT, padx=(5, 20))

        tk.Label(geo_row1, text="Sample Thickness (μm):", bg="#fafcff").pack(side=tk.LEFT)
        self.thickness_entry = tk.Entry(geo_row1, width=10, bg="#fafcff", relief="flat", highlightthickness=1, highlightbackground="#d0d6e0")
        self.thickness_entry.pack(side=tk.LEFT)

        geo_row2 = tk.Frame(geo_frame, bg="#fafcff")
        geo_row2.pack(fill="x", pady=(5, 0))
        self.calc_btn = ttk.Button(geo_row2, text="Calculate Resistivity", style='Purple.TButton', width=18,
                                   command=self.calculate_geometry)
        self.calc_btn.pack(side=tk.LEFT, padx=(0, 20))

        self.geo_calc = tk.Label(geo_row2, text="Geometry Calculations:", anchor="w", justify=tk.LEFT, bg="#fafcff")
        self.geo_calc.pack(side=tk.LEFT, fill="x", expand=True)

    def measure_live(self):
        if self.c_data or self.v_data:
            messagebox.showerror("Sweep Error", "Please clear previous data before starting a new sweep.")
            return
        try:
            min_v = float(self.entries["MIN"].get())
            max_v = float(self.entries["MAX"].get())
            step_v = float(self.entries["STEP"].get())
            comp = float(self.entries["COMPLIANCE"].get())
        except ValueError:
            messagebox.showerror("Input Error", "Enter valid numeric sweep parameters.")
            return

        unit = self.unit_opt.get()
        conv = to_amperes(1, unit)

        self.keithley.set_compliance(comp)

        currents = []
        i = min_v * conv
        end = max_v * conv + 1e-15
        while i <= end:
            currents.append(i)
            i += step_v * conv

        def do_read(idx):
            I_read, V_read = self.keithley.read()
            self.c_data.append(I_read)
            self.v_data.append(V_read)

            self.line.set_data(self.c_data, self.v_data)
            xmin, xmax = min(self.c_data), max(self.c_data)
            pad_x = (xmax - xmin or abs(xmax) or 1e-3) * 0.05
            ymin, ymax = min(self.v_data), max(self.v_data)
            pad_y = (ymax - ymin or abs(ymax) or 1e-3) * 0.05
            self.ax.set_xlim(xmin - pad_x, xmax + pad_x)
            self.ax.set_ylim(ymin - pad_y, ymax + pad_y)
            self.canvas.draw()
            self.update_idletasks()

            step(idx + 1)

        def step(idx):
            if idx >= len(currents):
                self.keithley.output_off()
                self._save_csv()
                return
            self.keithley.source_current(currents[idx])
            self.after(200, lambda i=idx: do_read(i))

        self.keithley.inst.write(":OUTP ON")
        step(0)

    def _save_csv(self):
        path = self.file_entry.get().strip()
        if not path:
            messagebox.showerror("Save Error", "No file path entered—cannot save CSV.")
            return
        try:
            data = list(zip(self.c_data, self.v_data))
            self.logger.save(path, data)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save CSV:\n{e}")

    def clear_data(self):
        self.c_data.clear()
        self.v_data.clear()
        self.line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.canvas.draw()
        self.geo_calc.config(text="Geometry Calculations:")

    def calculate_geometry(self):
        if len(self.c_data) < 2:
            messagebox.showerror("Not enough data", "Run sweep first.")
            return
        try:
            slope, intercept = polyfit(self.c_data, self.v_data, 1)
            resistance = slope
            L = float(self.length_entry.get()) / 100.0
            W = float(self.width_entry.get()) / 100.0
            t = float(self.thickness_entry.get()) / 1e6
            A = W * t
            resistivity = resistance * (A / L)

            path = self.file_entry.get().strip()
            if path:
                params = {
                    "Resistance (Ohm)": resistance,
                    "Resistivity (Ohm·m)": resistivity,
                    "Sample Length (cm)": self.length_entry.get(),
                    "Sample Width (cm)": self.width_entry.get(),
                    "Sample Thickness (µm)": self.thickness_entry.get(),
                    "Cross-sectional Area (m^2)": A
                }
                self.logger.append_params(path, params)

            result = (f"Resistance: {resistance:.6f} Ω\n"
                      f"Area: {A:.6e} m²\n"
                      f"Resistivity: {resistivity:.6e} Ω·m")
            self.geo_calc.config(text=result)
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))
