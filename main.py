import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import os
import io
import time
import imageio
from PIL import Image, ImageTk, ImageSequence
from tkinter import filedialog

from mybot import AutoBot
from pytesseract import pytesseract as pyt

worker_bot = AutoBot(pyt)

# pytesseract.pytesseract.tesseract_cmd = os.path.join(os.getcwd(), 'Tesseract-OCR', 'tesseract.exe')


def start_program():
    top = tk.Toplevel()
    top.title("Gestor Trabajo Remoto")
    message = 'Proceso Iniciado'
    if not worker_bot.start_knight_online():
        message = 'Error. Falta Iniciar Coordenadas, Resolucion o el Proceso ya esta activo'
    start_label = tk.Label(top, text=message, font=("Arial", 20))
    start_label.pack(padx=20, pady=10)


def stop_program():
    worker_bot.is_active = False


def start_origin_pos():

    status = worker_bot.config_origin()
    if not status:
        top = tk.Toplevel()
        top.title('Error leyendo coordenadas')
        message = f'Coordenada leida: {worker_bot.initial_coords}'
        tk_label = tk.Label(top, text=message, font=("Arial", 20))
        tk_label.pack(padx=20, pady=20)



def configure_descent_key():
    def save_num():
        num = num_entry.get()
        try:
            num = int(num)
            if not (0 <= num <= 9):
                raise ValueError()
            descent_key = num
            worker_bot.config_descent_key(descent_key)
            top.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a number from 0 to 9.")

    top = tk.Toplevel()
    top.title("Ingresa la tecla de Descent")
    msg = tk.Label(top, text="El valor debe ser de 0 a 9:", font=("Arial", 16))
    msg.pack()
    num_entry = tk.Entry(top, font=("Arial", 14))
    num_entry.pack(pady=10)

    save_btn = tk.Button(top, text="Guardar", command=save_num, font=("Arial", 14), height=2)

    save_btn.pack()


def exit_program():
    time.sleep(3)
    root.destroy()


def show_options():
    def set_option(option):
        worker_bot.set_resolution(option)
        option_window.destroy()

    option_window = tk.Toplevel(root)
    option_window.title("Seleccionar Resolucion")

    option_label = ttk.Label(option_window, text="Pantalla: ")
    option_label.pack(padx=10, pady=10)

    option_1_button = ttk.Button(option_window, text="1920x1080", command=lambda: set_option('A'))
    option_1_button.pack(padx=10, pady=5)

    option_2_button = ttk.Button(option_window, text="1600x900", command=lambda: set_option('B'))
    option_2_button.pack(padx=10, pady=5)

    option_3_button = ttk.Button(option_window, text="1366x768", command=lambda: set_option('C'))
    option_3_button.pack(padx=10, pady=5)

    option_window.grab_set()
    option_window.wait_window()


def get_image_path():
    # replace this with your own logic to get the image path
    return os.path.join(os.getcwd(), "background_animation.gif")


# create the root window
root = tk.Tk()
root.title("Mi trabajo Remoto")
root.geometry("290x480")

# set custom window icon
icon_path = os.path.join(os.getcwd(), "icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(default=icon_path)

# calculate the button width and height based on the anchor of the window
width = root.winfo_width() // 2
height = root.winfo_height() // 6 * 2

# add a dynamic background image
image_path = get_image_path()
if os.path.exists(image_path):
    # use imageio to load the image
    gif = imageio.mimread(image_path)
    # create a list of the individual frames
    frames = [ImageTk.PhotoImage(Image.fromarray(image).rotate(-90)) for image in gif]
    # set the initial frame as the first image
    frame = 0
    # create a label to hold the background image
    background_label = tk.Label(root, image=frames[0])
    background_label.image = frames[0]  # keep a reference to the image to prevent garbage collection
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    # animate the GIF
    animate_flag = True


    def animate():
        global frame, animate_flag
        if animate_flag:
            # update the image on the label
            background_label.configure(image=frames[frame])
            frame = (frame + 1) % len(frames)
        root.after(50, animate)


    animate()

# create the button to show the date
style = ttk.Style()

style.configure(
    'TButton', borderwidth=0, relief='raised', background='#f0f0f0', height=height,
    width=width, font=('Arial', 16), foreground='#000000', bd=3, fg='white', bg='black'
)

style.map(
    'TButton',
    background=[('active', '#d9d9d9')],
    foreground=[('active', '#000000')]
)

file_types = (
        ('Image files', '*.png;*.jpg;*.gif'),
        ('PNG files', '*.png'),
        ('JPG files', '*.jpg'),
        ('GIF files', '*.gif'),
        ('All files', '*.*')
    )


# create button to stop and start the animation
def toggle_animation():
    global animate_flag
    animate_flag = not animate_flag


# create button to change the background image
def change_background():
    # create a new window to select the image and rotation options
    window = tk.Toplevel(root)
    window.title("Change Background")

    # function to update the preview image
    def update_preview_image():
        # load the selected image and rotate it if necessary
        image = Image.open(selected_image.get())
        if rotate_left.get():
            image = image.transpose(Image.ROTATE_90)
        elif rotate_right.get():
            image = image.transpose(Image.ROTATE_270)

        # create a preview image with the selected rotation
        preview_image = ImageTk.PhotoImage(image.rotate(-90))
        preview_label.configure(image=preview_image)
        preview_label.image = preview_image

    # create a frame to hold the image selection and rotation options
    frame = ttk.Frame(window)
    frame.pack(padx=20, pady=10)

    # create a label for the image selection
    image_label = ttk.Label(frame, text="Select an animated GIF:")
    image_label.grid(row=0, column=0, padx=5, pady=5)

    # create a variable to hold the selected image
    selected_image = tk.StringVar()

    # function to select the image
    def select_image():
        filename = filedialog.askopenfilename(
            filetypes=file_types,
            title='Selecciona tu waifu rikolina'
        )
        if filename:
            selected_image.set(filename)
            update_preview_image()

    # create a button to select the image
    select_button = ttk.Button(frame, text="Select", command=select_image)
    select_button.grid(row=0, column=1, padx=5, pady=5)

    # create a label for the rotation options
    rotation_label = ttk.Label(frame, text="Rotation:")
    rotation_label.grid(row=1, column=0, padx=5, pady=5)

    # create variables for the rotation options
    rotate_left = tk.BooleanVar()
    rotate_right = tk.BooleanVar()

    # function to update the preview image when the rotation options are changed
    def update_rotation():
        update_preview_image()

    # create checkbuttons for the rotation options
    left_button = ttk.Checkbutton(frame, text="Left", variable=rotate_left, onvalue=True, offvalue=False,
                                  command=update_rotation)
    left_button.grid(row=1, column=1, padx=5, pady=5)
    right_button = ttk.Checkbutton(frame, text="Right", variable=rotate_right, onvalue=True, offvalue=False,
                                   command=update_rotation)
    right_button.grid(row=1, column=2, padx=5, pady=5)

    # create a label for the preview image
    preview_label = ttk.Label(frame)
    preview_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

    # create a frame to hold the buttons
    button_frame = ttk.Frame(window)
    button_frame.pack(padx=20, pady=10)

    def confirm_change():
        global frames, frame, image_path
        if selected_image.get():
            # load the selected image and rotate it if necessary
            with open(selected_image.get(), 'rb') as f:
                image_data = f.read()
                image_pil = Image.open(io.BytesIO(image_data))
                if rotate_left.get():
                    image_pil = image_pil.transpose(Image.ROTATE_90)
                elif rotate_right.get():
                    image_pil = image_pil.transpose(Image.ROTATE_270)
                # create a list of the individual frames
                frames = [ImageTk.PhotoImage(image.rotate(-90))
                          for image in ImageSequence.Iterator(image_pil)]
                frame = 0
                # update the background label
                background_label.configure(image=frames[0])
                # change the background image path
                image_path = selected_image.get()
        if rotate_left.get() or rotate_right.get():
            # rotate the current frames to the left or right
            angle = 90 if rotate_left.get() else 270
            frames = [ImageTk.PhotoImage(image_pil.rotate(angle).resize((400, 500), Image.LANCZOS))
                      for image_pil in ImageSequence.Iterator(Image.open(image_path))]
            # update the background label
            background_label.configure(image=frames[0])
        window.destroy()

    # create buttons to confirm or cancel the change
    confirm_button = ttk.Button(button_frame, text="Confirm", command=confirm_change)
    confirm_button.grid(row=0, column=0, padx=5, pady=5)
    cancel_button = ttk.Button(button_frame, text="Cancel", command=window.destroy)
    cancel_button.grid(row=0, column=1, padx=5, pady=5)

    # set the initial state of the rotation options to False
    rotate_left.set(False)
    rotate_right.set(False)

    # update the preview image with the initial state
    # update_preview_image()




button_names = [
    "2. Elegir Num Descent",  #
    "3. Definir Origen",  #
    "4. Iniciar Programa",  #
    "Detener Programa",  #
]

button_commands = [
    configure_descent_key,
    start_origin_pos,
    start_program,
    stop_program
]

# create buttons

date_button = ttk.Button(root, text="1. Configurar Resolucion", command=show_options, style='TButton')
date_button.pack(side="top", padx=20, pady=10)

for i in range(4):
    button = ttk.Button(root, text=button_names[i], command=button_commands[i], style='TButton')
    button.pack(padx=20, pady=10)

change_button = ttk.Button(root, text="Change Background", command=change_background, style='TButton')
change_button.pack(side="top", padx=20, pady=10)


toggle_button = ttk.Button(root, text="Stop Animation", command=toggle_animation, style='TButton')
toggle_button.pack(side="top", padx=20, pady=10)

exit_button = ttk.Button(root, text="Salir", command=exit_program, style='TButton')
exit_button.pack(padx=20, pady=10)

# start the main event loop
root.mainloop()
