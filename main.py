import tkinter as tk
from tkinter import ttk
from instruments.keithley2401 import Keithley2401Controller
from instruments.keithley2000 import Keithley2000Controller
from gui.styles import apply_theme
from gui.tabs.vi_tab import VITab
from gui.tabs.vt_tab import VTTab
from gui.tabs.vtemp_tab import VTempTab

def main():
    root = tk.Tk()
    root.title("Thermoelectric Material Measurement GUI")
    root.geometry("1200x1000")
    root.configure(bg="#fafcff")
    root.option_add("*Foreground", "#0e1e42")

    apply_theme(root)

    notebook = ttk.Notebook(root, style='WhiteNotebook.TNotebook')
    notebook.pack(fill='both', expand=True)

    k2401 = Keithley2401Controller("GPIB0::24::INSTR")
    k2000 = Keithley2000Controller("GPIB0::16::INSTR")

    iv_tab = VITab(notebook, k2401)
    notebook.add(iv_tab, text="V-I")

    vt_tab = VTTab(notebook, k2401, k2000)
    notebook.add(vt_tab, text="V–t")

    Vtemp_tab = VTempTab(notebook, vt_tab)
    notebook.add(Vtemp_tab, text="V-T")

    root.mainloop()

if __name__ == "__main__":
    main()