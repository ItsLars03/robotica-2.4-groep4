import tkinter as tk
import serial
import time
import ax12
import math

speed = 0

try:
    motor = ax12.Ax12()
except serial.SerialException:
    print("Error: Could not open serial port.")
    exit()

servos = motor.learnServos(1, 17)
print(f"Found servos: {servos}")

widgets = {}
current_index, step = 0, 0

def move_motor(sid, val):
    try:
        motor.moveSpeed(sid, int(float(val)), widgets[sid]["speed_slider"].get())
    except Exception as e:
        print(f"Move error {sid}: {e}")

def set_target(sid, entry):
    try:
        val = int(entry.get())
        if 0 <= val <= 1023:
            motor.move(sid, val)
            widgets[sid]["slider"].set(val)
    except:
        pass


def draw_position(sid, pos):
    c = widgets[sid]["canvas"]
    c.delete("indicator")
    angle = math.radians((-((pos / 1023) * 300) + 120) % 360)
    x = 125 + 100 * math.cos(angle)
    y = 125 + 100 * math.sin(angle)
    c.create_oval(x-5, y-5, x+5, y+5, fill="red", tags="indicator")

def safe_read(func, *args, retries=2, default=None):
    for _ in range(retries):
        try:
            return func(*args)
        except:
            time.sleep(0.002)
    return default

def toggle_wheel_mode(sid):
    state = widgets[sid]["wheel_var"].get()
    if state:
        motor.setAngleLimit(sid, 0, 0)
        widgets[sid]["slider"].pack_forget()
        widgets[sid]["onoff_btn"].pack(pady=3)
    else:
        motor.setAngleLimit(sid, 0, 1023)
        widgets[sid]["onoff_btn"].pack_forget()
        widgets[sid]["slider"].pack()

def toggle_motor_run(sid):
    if widgets[sid]["running"]:
        motor.moveSpeed(sid, 0, 0)
        widgets[sid]["onoff_btn"].config(text="Run")
        widgets[sid]["running"] = False
    else:
        spd = widgets[sid]["speed_slider"].get()
        motor.moveSpeed(sid, 0, spd)
        widgets[sid]["onoff_btn"].config(text="Stop")
        widgets[sid]["running"] = True

def update_servos():
    global current_index, step
    if not servos: return
    sid = servos[current_index]
    try:
        if step == 0:
            pos = safe_read(motor.readPosition, sid, default="-")
            widgets[sid]["pos_var"].set(pos)
            if isinstance(pos, int): draw_position(sid, pos)

        elif step == 1:
            widgets[sid]["voltage"] = safe_read(motor.readVoltage, sid, default=0) / 10

        elif step == 2:
            widgets[sid]["temp"] = safe_read(motor.readTemperature, sid, default=0)

        elif step == 3:
            moving = safe_read(motor.readMovingStatus, sid, default=0)
            widgets[sid]["moving"] = "Yes" if moving else "No"

        elif step == 4:
            spd = safe_read(motor.readSpeed, sid, default=0)
            speed = ((spd & 0x3FF) * 0.111) * (1 if spd < 1024 else -1)
            widgets[sid]["speed"] = speed

        elif step == 5:
            ld = safe_read(motor.readLoad, sid, default=0)
            load = ((ld & 0x3FF) / 1023 * 1.3875) * (1 if ld < 1024 else -1)
            widgets[sid]["load"] = load

            w = widgets[sid]
            w["status"].config(text=
                f"Voltage: {w['voltage']:.1f} V\n"
                f"Temp: {w['temp']} C\n"
                f"Moving: {w['moving']}\n"
                f"Speed: {w['speed']:.1f} RPM\n"
                f"Torque: {w['load']:.3f} Nm"
            )

    except Exception as e:
        print(f"Read error {sid}: {e}")

    step = (step + 1) % 6
    if step == 0:
        current_index = (current_index + 1) % len(servos)
    root.after(35, update_servos)

# --- GUI ---
root = tk.Tk()
root.title("AX-12A Servo Controller")
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

for sid in servos:
    f = tk.LabelFrame(frame, text=f"Servo {sid}")
    f.pack(side="left", padx=10, pady=10)

    sld = tk.Scale(f, from_=0, to=1023, orient='horizontal',
                   command=lambda v, s=sid: move_motor(s, v),
                   length=250)
    sld.pack()

    spd_sld = tk.Scale(f, from_=0, to=1023, orient='horizontal',
                       length=250, label="Speed")
    spd_sld.pack()

    e = tk.Entry(f, width=5)
    e.pack()
    tk.Button(f, text="Set Target", command=lambda s=sid, e=e: set_target(s, e)).pack()

    wheel_var = tk.IntVar()
    wheel_cb = tk.Checkbutton(f, text="Wheel Mode", variable=wheel_var,
                              command=lambda s=sid: toggle_wheel_mode(s))
    wheel_cb.pack()

    onoff_btn = tk.Button(f, text="Run", command=lambda s=sid: toggle_motor_run(s))
    onoff_btn.pack(pady=3)
    onoff_btn.pack_forget()  # hide initially

    pos_var = tk.StringVar()
    pos_var.set("-")
    tk.Label(f, textvariable=pos_var, font=("Arial", 12)).pack()

    c = tk.Canvas(f, width=250, height=250, bg="white")
    c.pack()
    c.create_oval(25, 25, 225, 225, outline="black")
    for ang in [0, 90, 180, 270]:
        rad = math.radians(ang)
        x = 125 + 100 * math.cos(rad)
        y = 125 + 100 * math.sin(rad)
        c.create_oval(x-3, y-3, x+3, y+3, fill="black")

    status = tk.Label(f, text="Motor Status", justify="left", font=("Arial", 9))
    status.pack()

    widgets[sid] = {
        "slider": sld, "speed_slider": spd_sld, "canvas": c,
        "pos_var": pos_var, "status": status,
        "wheel_var": wheel_var, "onoff_btn": onoff_btn,
        "running": False
    }

if servos:
    root.after(500, update_servos)
else:
    print("No servos found.")

root.mainloop()