import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv
from PIL import Image, ImageTk

class VTempTab(ttk.Frame):
    def __init__(self, parent, vt_tab):
        super().__init__(parent, style='WhiteFrame.TFrame')
        self.vt_tab = vt_tab

        self.dv_entries = []
        self.t1_entries  = []
        self.t2_entries  = []
        self.dt_entries  = []

        self._build_widgets()

    def _build_widgets(self):
        img = Image.open("C:\\Users\\ramaa\\Desktop\\Thermo\\QEERI_logo.png")
        img = img.resize((200, 50), Image.Resampling.LANCZOS)
        self.logo_img = ImageTk.PhotoImage(img)            

        logo_lbl = tk.Label(self, image=self.logo_img, bg="#fafcff")
        logo_lbl.pack(side=tk.TOP, pady=(20, 10))

        title = tk.Label(self, text="Seebeck Calculation", font=("Space Grotesk", 28), bg="#fafcff")
        title.pack(pady=(20, 20))

        load_frame = tk.Frame(self, bg="#fafcff")
        load_frame.pack(fill='x', padx=40, pady=(20,10))
        load_btn = ttk.Button(load_frame, text="Load ΔV Data", style='Purple.TButton', command=self.populate_table)
        load_btn.pack(anchor='center', pady=5)

        self.table_frame = tk.Frame(self, bg="#fafcff", bd=1, relief="solid")
        self.table_frame.pack(anchor='center', padx=40, pady=(0,10))

        dtbtn_frame = tk.Frame(self, bg="#fafcff")
        dtbtn_frame.pack(fill='x', padx=40, pady=(10,0))
        ttk.Button(dtbtn_frame, text="Calc ΔT & Plot", style='Purple.TButton', command=self.calc_and_plot).pack(anchor='center')

        graph_frame = tk.Frame(self, bg='white', bd=1, relief='solid')
        graph_frame.pack(fill='both', expand=True, padx=40, pady=10)
        self.fig = Figure(figsize=(5,3), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("ΔV vs ΔT")
        self.ax.set_xlabel("ΔT (C)")
        self.ax.set_ylabel("ΔV (µV)")
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        btn_frame = tk.Frame(self, bg="#fafcff")
        btn_frame.pack(fill='x', padx=40, pady=(0,20))
        ttk.Button(btn_frame, text="Calc Seebeck", style='Purple.TButton', command=self.calc_seebeck).pack(anchor='center')
        self.result_label = ttk.Label(self, text="Material Seebeck = -- µV/K", style='WhiteLabel.TLabel',
                                      font=(None,16,'bold'), foreground='#2563eb')
        self.result_label.pack(pady=(0,20))

    def populate_table(self):
        for w in self.table_frame.winfo_children(): w.destroy()
        self.dv_entries.clear(); self.t1_entries.clear(); self.t2_entries.clear(); self.dt_entries.clear()

        headers = ["ΔV (µV)", "T1 (C)", "T2 (C)", "ΔT (C)"]
        for col, text in enumerate(headers):
            ttk.Label(self.table_frame, text=text, style='WhiteLabel.TLabel').grid(row=0, column=col, padx=10, pady=5)

        for i, v in enumerate(self.vt_tab.step_voltages):
            e_dv = tk.Entry(self.table_frame, width=10, bg="#fafcff", relief="flat",
                             highlightthickness=1, highlightbackground="#d0d6e0")
            e_dv.insert(0, f"{v*1e6:.2f}")
            e_dv.config(state='readonly')
            e_dv.grid(row=i+1, column=0, padx=10, pady=2)
            self.dv_entries.append(e_dv)

            e_t1 = tk.Entry(self.table_frame, width=10, bg="#fafcff", relief="flat",
                             highlightthickness=1, highlightbackground="#d0d6e0")
            e_t1.grid(row=i+1, column=1, padx=10, pady=2)
            self.t1_entries.append(e_t1)

            e_t2 = tk.Entry(self.table_frame, width=10, bg="#fafcff", relief="flat",
                             highlightthickness=1, highlightbackground="#d0d6e0")
            e_t2.grid(row=i+1, column=2, padx=10, pady=2)
            self.t2_entries.append(e_t2)

            e_dt = tk.Entry(self.table_frame, width=10, bg="#fafcff", relief="flat",
                             highlightthickness=1, highlightbackground="#d0d6e0")
            e_dt.config(state='readonly')
            e_dt.grid(row=i+1, column=3, padx=10, pady=2)
            self.dt_entries.append(e_dt)

    def calc_and_plot(self):
        pts = []
        for ev, e1, e2, ed in zip(self.dv_entries, self.t1_entries, self.t2_entries, self.dt_entries):
            try:
                dv = float(ev.get()); t1 = float(e1.get()); t2 = float(e2.get())
            except ValueError:
                continue
            dt = t1 - t2
            ed.config(state='normal')
            ed.delete(0, 'end')
            ed.insert(0, f"{dt:.3f}")
            ed.config(state='readonly')
            pts.append((dt, dv))
        if not pts:
            return
        pts.sort(key=lambda x: x[0]); xs, ys = zip(*pts)
        self.ax.clear()
        self.ax.plot(xs, ys, marker='o', linestyle='-')
        self.ax.set_title("ΔV vs ΔT")
        self.ax.set_xlabel("ΔT (C)")
        self.ax.set_ylabel("ΔV (µV)")
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw()

    def save_vt_and_seebeck(self, seebeck_coeff: float):
            path = self.vt_tab.file_entry.get().strip()
            if not path:
                messagebox.showerror("Save Error", "Enter a valid file path in the V–t tab.")
                return

            try:
                with open(path, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([])
                    writer.writerow(["Material Seebeck (µV/K)", f"{seebeck_coeff:.6f}"])
            
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not write results to CSV:\n{e}")
            else:
                messagebox.showinfo("Save Complete", "Seebeck value appended to your V–t CSV.")

    def calc_seebeck(self):
        data = []
        for ev, ed in zip(self.dv_entries, self.dt_entries):
            try:
                dv = float(ev.get()); dt = float(ed.get())
            except ValueError:
                continue
            data.append((dt, dv))
        if len(data) < 2:
            messagebox.showerror("Data Error","Need ≥ 2 points")
            return
        xs, ys = zip(*sorted(data))
        slope, _ = np.polyfit(xs, ys, 1)
        mat_s = slope  - 1.93
        self.result_label.config(text=f"Material Seebeck = {mat_s:.2f} µV/K")
        self.save_vt_and_seebeck(mat_s)