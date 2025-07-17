from tkinter import ttk

def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use('clam')

    style.configure('WhiteNotebook.TNotebook',    background='#fafcff')
    style.configure('WhiteNotebook.TNotebook.Tab', background='lightgray')
    style.map(     'WhiteNotebook.TNotebook.Tab',
                  background=[('selected', '#fafcff')])
    style.configure('TNotebook.Client',           background='#fafcff')
    style.configure('WhiteFrame.TFrame',          background='#fafcff')
    style.configure('WhiteLabel.TLabel',          background='#fafcff')

    style.configure('Purple.TButton',
                    background='#8E66F7', foreground='white',
                    font=('Helvetica',12,'bold'),
                    padding=(15,8), borderwidth=0)
    style.map('Purple.TButton',
              background=[('active','#7A5BF7')],
              foreground=[('active','white')])
