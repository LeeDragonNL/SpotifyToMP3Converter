from tkinter import ttk
from turtle import bgcolor
from ttkthemes import ThemedTk

# Create themed window
root = ThemedTk(theme="breeze")
root.title("Login Form")
root.geometry("600x350")



# Apply styles
style = ttk.Style()
style.configure("TButton", font=("Monospace", 12), padding=5)

# Create widgets
label1 = ttk.Label(root, text="Insert a spotfiy link or playlist:", font=("Monospace", 12))
label1.pack(pady=5)
entry1 = ttk.Entry(root, width=30)
entry1.pack(pady=5)



button = ttk.Button(root, text="Downloaden", command=lambda: print("Login Clicked"))
button.pack(pady=10)

root.mainloop()