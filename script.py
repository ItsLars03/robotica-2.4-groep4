import cv2
import tkinter as tk
from PIL import Image, ImageTk

# --- GLOBALE VARIABELE OM DE CAMERA AAN/UIT TE ZETTEN ---
camera_on = True

# Stel hier de resolutie van het window (en dus van de camera) in:
win_width  = 800
win_height = 480

def video_loop():
    """
    Deze functie wordt telkens opnieuw aangeroepen (via root.after).
    Als camera_on == True dan lezen we een frame uit de camera en tonen dat.
    Als camera_on == False dan bouwen we een volledig zwart plaatje en tonen dat.
    """
    global camera_on

    if camera_on:
        ret, frame = cap.read()
        if ret:
            # Converteer naar RGB en maak van de numpy-array een PIL-image
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
        else:
            # Mocht de camera om de één of andere reden geen frame geven,
            # maak dan alsnog een zwart plaatje
            img = Image.new("RGB", (win_width, win_height), (0, 0, 0))
    else:
        # Hier maken we een volledig zwart plaatje
        img = Image.new("RGB", (win_width, win_height), (0, 0, 0))

    # Converteer PIL-image naar PhotoImage en toon in lbl_video
    imgtk = ImageTk.PhotoImage(image=img)
    lbl_video.imgtk = imgtk
    lbl_video.config(image=imgtk)

    # Roep deze functie na ±15 ms opnieuw aan (ongeveer 60 FPS)
    root.after(15, video_loop)

def on_mode_click():
    print("MODE-button ingedrukt!")

def on_gripper_click():
    print("GRIPPER Close/Open ingedrukt!")

def on_stop_click():
    print("STOP-button ingedrukt!")

def on_cam_click():
    """
    Bij een klik togglen we de camera_on flag.
    Als we net aan stonden, gaan we uit (zwart scherm).
    Andersom, we gaan weer aan (camera doet het weer).
    """
    global camera_on
    camera_on = not camera_on
    if camera_on:
        print("CAM aan: live-camera-feed weer zichtbaar.")
    else:
        print("CAM uit: scherm is nu zwart.")

# --- TKINTER WINDOW OPZETTEN ---
root = tk.Tk()
root.title("Camera-mockup met Toggle CAM")

# Stel de window-grootte in; we gebruiken deze afmetingen ook voor de camera.
root.geometry(f"{win_width}x{win_height}")
root.resizable(False, False)

# --- LABEL VOOR DE CAMERA (FULL-SCREEN ACHTERGROND) ---
lbl_video = tk.Label(root)
lbl_video.place(x=0, y=0, relwidth=1, relheight=1)

# --- “CAM”-LABEL (rechtsboven) ---
lbl_cam = tk.Label(
    root,
    text="CAM",
    font=("Helvetica", 12, "bold"),
    fg="#333333",
    bg="#ffffff",
    bd=1, relief="ridge",
    padx=8, pady=4
)
lbl_cam.place(relx=0.98, rely=0.02, anchor="ne")
lbl_cam.bind("<Button-1>", lambda e: on_cam_click())

# --- “MODE”-LABEL (middenboven) ---
lbl_mode = tk.Label(
    root,
    text="MODE",
    font=("Helvetica", 16, "bold"),
    fg="#555555",
    bg="#ffffff",
    bd=0
)
lbl_mode.place(relx=0.5, rely=0.15, anchor="center")

# --- “AUTO / MANUAL”-BUTTON (onder MODE) ---
btn_mode = tk.Button(
    root,
    text="AUTO / MANUAL",
    command=on_mode_click,
    bd=2,
    relief="ridge",
    bg="#ffffff",
    fg="#333333",
    font=("Helvetica", 14, "bold"),
    padx=12, pady=6
)
btn_mode.place(relx=0.5, rely=0.25, anchor="center")

# --- “GRIPPER”-LABEL (linksonder) + “Close / Open”-BUTTON eronder ---
lbl_gripper = tk.Label(
    root,
    text="GRIPPER",
    font=("Helvetica", 14, "bold"),
    fg="#555555",
    bg="#ffffff",
    bd=0
)
lbl_gripper.place(relx=0.02, rely=0.80, anchor="sw")

btn_gripper = tk.Button(
    root,
    text="Close / Open",
    command=on_gripper_click,
    bd=2,
    relief="ridge",
    bg="#ffffff",
    fg="#333333",
    font=("Helvetica", 12),
    padx=10, pady=4
)
btn_gripper.place(relx=0.02, rely=0.88, anchor="sw")

# --- “STOP”-BUTTON (rechtsonder) ---
btn_stop = tk.Button(
    root,
    text="STOP",
    command=on_stop_click,
    bd=2,
    relief="ridge",
    bg="#ffffff",
    fg="#333333",
    font=("Helvetica", 12, "bold"),
    padx=10, pady=4
)
btn_stop.place(relx=0.98, rely=0.90, anchor="se")

# --- START DE CAMERA ---
cap = cv2.VideoCapture(0)
# Forceer dat de camera exact dezelfde resolutie levert als ons window
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  win_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, win_height)

# Start de videoloop
root.after(0, video_loop)
root.mainloop()

# --- OPRUIMEN ---
cap.release()
cv2.destroyAllWindows()
