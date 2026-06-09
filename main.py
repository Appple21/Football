import tkinter as tk
import math
import random

############################
width = 500
height = 735
margin = 50

# Глобальные переменные для canvas и игры
root = tk.Tk()
root.title("Вертикальное футбольное поле")
canvas = tk.Canvas(root, width=width, height=height, bg="green")
canvas.pack()

# параметры игрока (будут установлены при выборе персонажа)
player_radius = 14
player_speed = 3
turn_senor = 4
kick_power = 10
kick_accuracy = 0  # неточность удара в градусах
player_x = width / 2
player_y = height / 2 + 100
player_angle = 0.0
keys_pressed = set()

# мяч
ball_radius = 8
ball_x = width / 2
ball_y = height / 2
ball_vx = 0
ball_vy = 0
ball_attached = False
goal_checked = False

# Графические объекты
player_circle = None
player_line = None
ball = None

# Флаги
in_character_select = True
game_started = False

characters = [
    {
        "name": "Гаяр",
        "color": "black",
        "outline": "darkred",
        "radius": 14,
        "speed": 5,
        "turn": 5,
        "kick": 7,
        "accuracy": 20  # неточность в градусах (чем больше, тем хуже)
    },
    {
        "name": "Лёша",
        "color": "red",
        "outline": "darkred",
        "radius": 14,
        "speed": 3,
        "turn": 5,
        "kick": 6,
        "accuracy": 35
    },
    {
        "name": "Климентий",
        "color": "blue",
        "outline": "darkblue",
        "radius": 14,
        "speed": 3,
        "turn": 4,
        "kick": 20,
        "accuracy": 50
    },
    {
        "name": "Петя",
        "color": "orange",
        "outline": "darkorange",
        "radius": 12,
        "speed": 3,
        "turn": 7,
        "kick": 9,
        "accuracy": 25
    },
    {
        "name": "Максим",
        "color": "purple",
        "outline": "darkviolet",
        "radius": 14,
        "speed": 3,
        "turn": 4,
        "kick": 8,
        "accuracy": 25
    },
    {
        "name": "Ростислав",
        "color": "green",
        "outline": "darkviolet",
        "radius": 14,
        "speed": 2,
        "turn": 3,
        "kick": 4,
        "accuracy": random.randint(15, 75)
    }
]


def draw_field():
    #Отрисовка футбольного поля#
    canvas.delete("all")
    canvas.create_rectangle(margin, margin, width - margin, height - margin, outline="white", width=3)
    canvas.create_line(margin, height // 2, width - margin, height // 2, fill="white", width=3)
    # центр
    canvas.create_oval(width // 2 - 60, height // 2 - 60, width // 2 + 60, height // 2 + 60, outline="white", width=3)
    canvas.create_oval(width // 2 - 4, height // 2 - 4, width // 2 + 4, height // 2 + 4, fill="white", outline="white")
    # штрафные
    canvas.create_rectangle(width // 2 - 90, margin, width // 2 + 90, margin + 120, outline="white", width=3)
    canvas.create_rectangle(width // 2 - 90, height - margin - 120, width // 2 + 90, height - margin, outline="white",
                            width=3)
    # вратарские
    canvas.create_rectangle(width // 2 - 45, margin, width // 2 + 45, margin + 50, outline="white", width=3)
    canvas.create_rectangle(width // 2 - 45, height - margin - 50, width // 2 + 45, height - margin, outline="white",
                            width=3)
    # ворота
    canvas.create_rectangle(width // 2 - 30, margin - 15, width // 2 + 30, margin, outline="white", width=3)
    canvas.create_rectangle(width // 2 - 30, height - margin, width // 2 + 30, height - margin + 15, outline="white",
                            width=3)


def create_game_objects():
    global player_circle, player_line, ball

    player_circle = canvas.create_oval(
        player_x - player_radius, player_y - player_radius,
        player_x + player_radius, player_y + player_radius,
        fill=selected_char["color"], outline=selected_char["outline"], width=2
    )

    player_line = canvas.create_line(
        player_x, player_y,
        player_x, player_y - player_radius,
        fill="white", width=2
    )

    ball = canvas.create_oval(
        ball_x - ball_radius, ball_y - ball_radius,
        ball_x + ball_radius, ball_y + ball_radius,
        fill="white", outline="black"
    )


def reset_positions():
    global player_x, player_y, player_angle
    global ball_x, ball_y, ball_vx, ball_vy, ball_attached, goal_checked, game_started

    player_x = width / 2
    player_y = height / 2 + 100
    player_angle = 0.0

    ball_x = width / 2
    ball_y = height / 2
    ball_vx = 0
    ball_vy = 0
    ball_attached = False
    goal_checked = False
    game_started = False


def start():
    #Перезапуск игры#
    global in_character_select, game_started
    in_character_select = False
    game_started = False
    reset_positions()
    draw_field()
    create_game_objects()
    game_loop()


def select_character(char):
    global selected_char, player_radius, player_speed, turn_senor, kick_power, kick_accuracy

    selected_char = char
    player_radius = char["radius"]
    player_speed = char["speed"]
    turn_senor = char["turn"]
    kick_power = char["kick"]
    kick_accuracy = char["accuracy"]

    start()


def show_character_select():
    #Показать экран выбора персонажа#
    global in_character_select
    in_character_select = True
    canvas.delete("all")
    canvas.create_rectangle(0, 0, width, height, fill="darkgreen")

    canvas.create_text(
        width // 2, 50,
        text="ВЫБОР ПЕРСОНАЖА",
        font=("Arial", 24, "bold"),
        fill="white"
    )

    # Рисуем кнопки для каждого персонажа
    button_width = 200
    button_height = 80
    start_y = 120
    gap = 20

    for i, char in enumerate(characters):
        x1 = width // 2 - button_width // 2
        y1 = start_y + i * (button_height + gap)
        x2 = width // 2 + button_width // 2
        y2 = y1 + button_height

        # Кнопка
        canvas.create_rectangle(x1, y1, x2, y2, fill="gray30", outline="white", width=2)
        # Имя персонажа
        canvas.create_text(
            width // 2, y1 + 20,
            text=char["name"],
            font=("Arial", 16, "bold"),
            fill=char["color"]
        )

        # Характеристики
        stats_text = f"Скорость: {char['speed']} | Удар: {char['kick']} | Поворот: {char['turn']} | Точность: {char['accuracy']}°"
        canvas.create_text(
            width // 2, y1 + 50,
            text=stats_text,
            font=("Arial", 10),
            fill="white"
        )

        # Сохраняем координаты кнопки в персонаже для обработки кликов
        char["button_coords"] = (x1, y1, x2, y2)


def on_click(event):
    #Обработка кликов мыши#
    if not in_character_select:
        return
    # Проверяем клики по кнопкам выбора персонажа
    for char in characters:
        if "button_coords" in char:
            x1, y1, x2, y2 = char["button_coords"]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                select_character(char)
                return


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


def end_game():
    canvas.create_text(width // 2, height // 2, text="ГОЛ!", font=("Arial", 48, "bold"), fill="gold")
    root.after(3000, start)  # Перезапуск через 3 секунды


def check_goal():
    # Верхние ворота
    if (width // 2 - 30 < ball_x < width // 2 + 30 and
            margin - 15 < ball_y < margin):
        return True

    # Нижние ворота
    if (width // 2 - 30 < ball_x < width // 2 + 30 and
            height - margin < ball_y < height - margin + 15):
        return True

    return False


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
    
    # Добавляем случайное отклонение в зависимости от точности
    deviation = random.uniform(-kick_accuracy, kick_accuracy)
    rad += math.radians(deviation)
    
    ball_vx = math.sin(rad) * kick_power
    ball_vy = -math.cos(rad) * kick_power


def on_press(event):
    global ball_attached
    key = event.keysym.lower()
    keys_pressed.add(key)

    if key == "e":
        try_pick_ball()
    if key == "space":
        if ball_attached:
            kick_ball()
        else:
            try_pick_ball()
    if key == "q":
        ball_attached = False


def on_release(event):
    keys_pressed.discard(event.keysym.lower())


def game_loop():
    global player_x, player_y, player_angle
    global ball_x, ball_y, ball_vx, ball_vy, ball_attached, goal_checked, game_started

    if game_started:
        return
    game_started = True

    def loop():
        global player_x, player_y, player_angle
        global ball_x, ball_y, ball_vx, ball_vy, ball_attached, goal_checked

        # поворот
        if "left" in keys_pressed or "a" in keys_pressed:
            player_angle -= turn_senor
        if "right" in keys_pressed or "d" in keys_pressed:
            player_angle += turn_senor

        # движение ВПЕРЁД
        if "up" in keys_pressed or "w" in keys_pressed:
            rad = math.radians(player_angle)
            new_x = max(margin + player_radius,
                        min(width - margin - player_radius, player_x + math.sin(rad) * player_speed))
            new_y = max(margin + player_radius,
                        min(height - margin - player_radius, player_y - math.cos(rad) * player_speed))
            player_x, player_y = new_x, new_y

        # движение НАЗАД
        if "down" in keys_pressed or "s" in keys_pressed:
            rad = math.radians(player_angle)
            new_x = max(margin + player_radius,
                        min(width - margin - player_radius, player_x - math.sin(rad) * player_speed))
            new_y = max(margin + player_radius,
                        min(height - margin - player_radius, player_y + math.cos(rad) * player_speed))
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

            # границы для ворот
            if width // 2 - 30 < ball_x < width // 2 + 30:
                top = margin - 15 + ball_radius
            else:
                top = margin + ball_radius

            if width // 2 - 30 < ball_x < width // 2 + 30:
                bottom = height - margin + 15 - ball_radius
            else:
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

        # гол ли
        if not goal_checked and check_goal():
            goal_checked = True
            end_game()

        update_visuals()
        root.after(16, loop)

    loop()


# Привязка событий
root.bind("<KeyPress>", on_press)
root.bind("<KeyRelease>", on_release)
root.bind("<Button-1>", on_click)

# Показать экран выбора персонажа
show_character_select()
root.mainloop()
