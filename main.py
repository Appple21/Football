import tkinter as tk
import math

root = tk.Tk()
root.title("Вертикалчвьное футбольное поле")

############################
width = 500
height = 735
margin = 50

canvas = tk.Canvas(root, width=width, height=height, bg="green")
canvas.pack()

###################################
canvas.create_rectangle(margin, margin, width - margin, height - margin, outline="white", width=3)
canvas.create_line(margin, height // 2, width - margin, height // 2, fill="white", width=3)
# центр
canvas.create_oval(width // 2 - 60, height // 2 - 60, width // 2 + 60, height // 2 + 60, outline="white", width=3)
canvas.create_oval(width // 2 - 4, height // 2 - 4, width // 2 + 4, height // 2 + 4, fill="white", outline="white")
# штрафные
canvas.create_rectangle(width // 2 - 90, margin, width // 2 + 90, margin + 120, outline="white", width=3)
canvas.create_rectangle(width // 2 - 90, height - margin - 120, width // 2 + 90, height - margin, outline="white", width=3)
# вратарские
canvas.create_rectangle(width // 2 - 45, margin, width // 2 + 45, margin + 50, outline="white", width=3)
canvas.create_rectangle(width // 2 - 45, height - margin - 50, width // 2 + 45, height - margin, outline="white", width=3)
# ворота
canvas.create_rectangle(width // 2 - 30, margin - 15, width // 2 + 30, margin, outline="white", width=3)
canvas.create_rectangle(width // 2 - 30, height - margin, width // 2 + 30, height - margin + 15, outline="white", width=3)

#######################
# параметры игрока
player_radius = 14
player_speed = 3
turn_senor = 4

player_x = width / 2
player_y = height / 2
player_angle = 0.0

keys_pressed = set()
#яйко zzzz
ball_radius = 8

ball_x = width / 2 + 100
ball_y = height / 2

ball_vx = 0
ball_vy = 0

ball_attached = False

ball = canvas.create_oval(
    ball_x - ball_radius,
    ball_y - ball_radius,
    ball_x + ball_radius,
    ball_y + ball_radius,
    fill="white",
    outline="black"
    )


##############################################
player_circle = canvas.create_oval(player_x - player_radius, player_y - player_radius, player_x + player_radius, player_y + player_radius, fill="red", outline="darkred", width=2)
player_line = canvas.create_line(player_x, player_y, player_x, player_y - player_radius, fill="white", width=2)

######################
def update_visuals():
    canvas.coords(
        player_circle,
        player_x - player_radius,
        player_y - player_radius,
        player_x + player_radius,
        player_y + player_radius
    )

    rad = math.radians(player_angle)

    canvas.coords(
        player_line,
        player_x,
        player_y,
        player_x + math.sin(rad) * player_radius,
        player_y - math.cos(rad) * player_radius
    )

    canvas.coords(
        ball,
        ball_x - ball_radius,
        ball_y - ball_radius,
        ball_x + ball_radius,
        ball_y + ball_radius
    )

def game_loop():
    global player_x, player_y, player_angle
    global ball_x, ball_y, ball_vx, ball_vy, ball_attached
    # поворот
    if "left" in keys_pressed or "a" in keys_pressed: player_angle -= turn_senor
    if "right" in keys_pressed or "d" in keys_pressed: player_angle += turn_senor
    # движение
    if "up" in keys_pressed or "w" in keys_pressed:
        rad = math.radians(player_angle)
        new_x = max(margin + player_radius, min(width - margin - player_radius, player_x + math.sin(rad) * player_speed))
        new_y = max(margin + player_radius, min(height - margin - player_radius, player_y - math.cos(rad) * player_speed))
        player_x, player_y = new_x, new_y
    rad = math.radians(player_angle)

    if ball_attached:
        offset = player_radius + ball_radius + 4

        ball_x = player_x + math.sin(rad) * offset
        ball_y = player_y - math.cos(rad) * offset

    else:
        ball_x += ball_vx
        ball_y += ball_vy

        # трение
        ball_vx *= 0.99
        ball_vy *= 0.99

        # столкновение со стенками поля
        left = margin + ball_radius
        right = width - margin - ball_radius
        top = margin + ball_radius
        bottom = height - margin - ball_radius


        if ball_x < left:
            ball_x = left
            ball_vx *= -0.8

        if ball_x > right:
            ball_x = right
            ball_vx *= -0.8

        if ball_y < top:
            ball_y = top
            ball_vy *= -0.8

        if ball_y > bottom:
            ball_y = bottom
            ball_vy *= -0.8
    update_visuals()
    root.after(16, game_loop)
#хватаем и пинаем мяч
def try_pick_ball():
    global ball_attached

    dx = ball_x - player_x
    dy = ball_y - player_y

    distance = math.hypot(dx, dy)

    if distance < 30:
        ball_attached = True
def kick_ball():
    global ball_attached, ball_vx, ball_vy

    if not ball_attached:
        return

    ball_attached = False

    rad = math.radians(player_angle)

    kick_speed = 10

    ball_vx = math.sin(rad) * kick_speed
    ball_vy = -math.cos(rad) * kick_speed

###############################
def on_press(event): keys_pressed.add(event.keysym.lower())
def on_release(event): keys_pressed.discard(event.keysym.lower())
def on_press(event):
    global ball_attached
    key = event.keysym.lower()
    keys_pressed.add(key)
    if key == "e":
        try_pick_ball()
    if key == "space":
        kick_ball()
    if key == "space" and ball_attached == False:
        try_pick_ball()
        kick_ball()
    if key == "q":
        ball_attached = False
root.bind("<KeyPress>", on_press)
root.bind("<KeyRelease>", on_release)

game_loop()
root.mainloop()
