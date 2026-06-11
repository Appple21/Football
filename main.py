import tkinter as tk
import math
import random

############################
width = 500
height = 735
margin = 50

GOAL_HALF_WIDTH = 60
PENALTY_HALF_WIDTH = 180
SMALL_BOX_HALF_WIDTH = 90

root = tk.Tk()
root.title("Вертикальное футбольное поле")
canvas = tk.Canvas(root, width=width, height=height, bg="#1a1a1a")
canvas.pack()

player_radius = 14
player_speed = 3
turn_senor = 4
kick_power = 10
kick_accuracy = 0
player_x = width / 2
player_y = height / 2 + 100
player_angle = 0.0
keys_pressed = set()

my_keeper_x = width / 2
my_keeper_y = height - margin - 10
my_keeper_radius = 10
my_keeper_speed = 2.5
my_keeper_ball_attached = False
my_keeper_kick_cooldown = 0
MY_KEEPER_ANGLE = 0.0

bot_char = None
bot_radius = 14
bot_speed = 2.5
bot_turn = 3
bot_kick_power = 8
bot_kick_accuracy = 15
bot_x = width / 2
bot_y = height / 2 - 100
bot_angle = 180.0
bot_ball_attached = False
bot_kick_cooldown = 0
bot_delay = 45
bot_wander_timer = 0
bot_steal_delay = 0

bot_keeper_x = width / 2
bot_keeper_y = margin + 10
bot_keeper_radius = 10
bot_keeper_speed = 2.0
bot_keeper_direction = 1
bot_keeper_jump_cooldown = 0
bot_keeper_ball_attached = False
bot_keeper_kick_cooldown = 0

ball_radius = 8
ball_x = width / 2
ball_y = height / 2
ball_vx = 0
ball_vy = 0
ball_attached = False
goal_checked = False
last_touch = None

score_player = 0
score_bot = 0

pillars = []

player_objs  = {}
my_keeper_objs = {}
bot_objs     = {}
bot_keeper_objs = {}
ball_objs    = {}

pillar_objects = []

in_character_select = True
game_started = False
showing_random_char = False
random_char = None

puddles = []

menu_anim_phase = 0
menu_anim_id = None

score_text_bot    = None
score_text_player = None

characters = [
    {"name": "Гаяр",     "color": "black",  "outline": "darkred",    "radius": 14, "speed": 4.25, "turn": 4.25, "kick": 7,  "accuracy": 10},
    {"name": "Лёша",     "color": "red",    "outline": "darkred",    "radius": 14, "speed": 3.75, "turn": 4,    "kick": 6,  "accuracy": 17.5},
    {"name": "Климентий","color": "blue",   "outline": "darkblue",   "radius": 14, "speed": 3,    "turn": 4,    "kick": 20, "accuracy": 25},
    {"name": "Петя",     "color": "orange", "outline": "darkorange", "radius": 12, "speed": 4,    "turn": 6,    "kick": 9,  "accuracy": 12.5},
    {"name": "Максим",   "color": "purple", "outline": "darkviolet", "radius": 14, "speed": 3.25, "turn": 4,    "kick": 8,  "accuracy": 12.5},
    {"name": "Ростислав","color": "green",  "outline": "darkviolet", "radius": 14, "speed": 2,    "turn": 3,    "kick": 4,  "accuracy": random.randint(7, 35)},
]

selected_char = characters[0]
random_button_coords = (0, 0, 0, 0)
random_play_button_coords = (0, 0, 0, 0)

SHIMMER_RANDOM  = ("#7a3a00", "#ffaa33")
SHIMMER_CHAR    = ("#1a2a3a", "#2e6090")
SHIMMER_PLAY    = ("#006622", "#00dd55")
SHIMMER_OUTLINE = ("#555555", "#ffffff")

_menu_button_ids = {}


def lerp_color(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"


def rounded_rect(cv, x1, y1, x2, y2, r=12, **kwargs):
    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
           x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1, x1+r,y1]
    return cv.create_polygon(pts, smooth=True, **kwargs)


def get_shimmer_color(base_dark, base_light, phase_offset=0):
    t = (math.sin(menu_anim_phase + phase_offset) + 1) / 2
    return lerp_color(base_dark, base_light, t)


def select_random_bot():
    available = [c for c in characters if c != selected_char]
    return random.choice(available)


# ─── СВЕТЛАЯ ТРАВА (с травинками) ──────────────────────────────────────────
def draw_grass(cv):
    """Рисует траву по краям поля с заметными травинками."""
    grass_base = "#7bc96f"
    blade_colors = ["#2e7d32", "#388e3c", "#43a047", "#66bb6a"]

    cv.create_rectangle(0, 0, width, margin, fill=grass_base, outline="")
    cv.create_rectangle(0, height-margin, width, height, fill=grass_base, outline="")
    cv.create_rectangle(0, 0, margin, height, fill=grass_base, outline="")
    cv.create_rectangle(width-margin, 0, width, height, fill=grass_base, outline="")

    rng = random.Random(42)

    def draw_blade(x, y, direction):
        h = rng.randint(5, 10)
        bend = rng.randint(-2, 2)
        color = rng.choice(blade_colors)

        if direction == "up":
            cv.create_line(x, y, x + bend, y - h, fill=color, width=1)
            cv.create_line(x, y, x - bend, y - h + 2, fill=color, width=1)
        elif direction == "right":
            cv.create_line(x, y, x + h, y + bend, fill=color, width=1)
            cv.create_line(x, y, x + h - 2, y - bend, fill=color, width=1)
        elif direction == "left":
            cv.create_line(x, y, x - h, y + bend, fill=color, width=1)
            cv.create_line(x, y, x - h + 2, y - bend, fill=color, width=1)

    for x in range(0, width, 3):
        draw_blade(x, margin - 1, "up")
        draw_blade(x, height - margin, "up")

    for y in range(0, height, 3):
        draw_blade(margin - 1, y, "left")
        draw_blade(width - margin, y, "right")


# ─── ИГРОКИ ─────────────────────────────────────────────────────────────────

def _player_color_light(color):
    m = {
        "black":  "#444444",
        "red":    "#ff6666",
        "blue":   "#4488ff",
        "orange": "#ffcc55",
        "purple": "#cc66ff",
        "green":  "#44cc44",
        "yellow": "#ffff88",
        "cyan":   "#88ffff",
    }
    return m.get(color, "#888888")


def create_player_objs(cv, x, y, r, body_color, outline_color, shirt_color=None, direction_color="white"):
    sc = shirt_color or _player_color_light(body_color)
    objs = {}
    objs["shadow"] = cv.create_oval(
        x-r+2, y-r//2+r, x+r+2, y+r//2+r,
        fill="#1a0a00", outline="", stipple="gray50")
    objs["body"] = cv.create_oval(
        x-r, y-r, x+r, y+r,
        fill=body_color, outline=outline_color, width=2)
    objs["shirt"] = cv.create_arc(
        x-r+2, y-r+2, x+r-2, y+r-2,
        start=200, extent=140,
        fill=sc, outline="", style=tk.CHORD)
    hr = max(4, r // 3)
    objs["head"] = cv.create_oval(
        x-hr, y-hr, x+hr, y+hr,
        fill="#f5cba7", outline="#c8956c", width=1)
    objs["dot"] = cv.create_oval(
        x-2, y-r+1, x+2, y-r+5,
        fill=direction_color, outline="")
    return objs


def move_player_objs(cv, objs, x, y, r, angle_deg):
    rad = math.radians(angle_deg)
    dx_tip = math.sin(rad) * r
    dy_tip = -math.cos(rad) * r
    cv.coords(objs["shadow"], x-r+2, y+r//2, x+r+2, y+r)
    cv.coords(objs["body"],   x-r, y-r, x+r, y+r)
    cv.coords(objs["shirt"],  x-r+2, y-r+2, x+r-2, y+r-2)
    hr = max(4, r // 3)
    hx = x + math.sin(rad) * (r * 0.25)
    hy = y - math.cos(rad) * (r * 0.25)
    cv.coords(objs["head"],   hx-hr, hy-hr, hx+hr, hy+hr)
    tip_x = x + dx_tip * 0.75
    tip_y = y + dy_tip * 0.75
    cv.coords(objs["dot"], tip_x-3, tip_y-3, tip_x+3, tip_y+3)


# ─── МЯЧ ────────────────────────────────────────────────────────────────────

def create_ball_objs(cv, x, y, r):
    objs = {}
    objs["shadow"] = cv.create_oval(
        x - r + 4, y + r - 3, x + r + 4, y + r + 5,
        fill="#0a0a0a", outline="", stipple="gray50")
    objs["base"] = cv.create_oval(
        x - r, y - r, x + r, y + r,
        fill="white", outline="#111111", width=2)
    objs["shade"] = cv.create_arc(
        x - r + 1, y - r + 1, x + r - 1, y + r - 1,
        start=270, extent=180,
        fill="white", outline="", style=tk.CHORD)
    ps0 = r * 0.52
    objs["p0"] = cv.create_polygon(
        _hex_pts(x, y, ps0, 5, offset_angle=-90),
        fill="#111111", outline="#444444", width=1, smooth=False)
    for i in range(5):
        ang = math.radians(i * 72 - 90)
        px = x + math.cos(ang) * r * 0.65
        py = y + math.sin(ang) * r * 0.65
        ps = r * 0.30
        objs[f"p{i+1}"] = cv.create_polygon(
            _hex_pts(px, py, ps, 5, offset_angle=i * 72),
            fill="#111111", outline="#444444", width=1, smooth=False)
    sr = r * 0.32
    sx, sy = x - r * 0.28, y - r * 0.28
    objs["shine"] = cv.create_oval(
        sx - sr, sy - sr * 0.65, sx + sr, sy + sr * 0.65,
        fill="white", outline="", stipple="gray75")
    sr2 = r * 0.13
    objs["shine2"] = cv.create_oval(
        sx - sr2, sy - sr2, sx + sr2, sy + sr2,
        fill="white", outline="")
    return objs


def _hex_pts(cx, cy, r, n, offset_angle=0):
    pts = []
    for i in range(n):
        a = math.radians(offset_angle + i * 360 / n)
        pts.append(cx + math.cos(a) * r)
        pts.append(cy + math.sin(a) * r)
    return pts


def move_ball_objs(cv, objs, x, y, r):
    cv.coords(objs["shadow"], x - r + 4, y + r - 3, x + r + 4, y + r + 5)
    cv.coords(objs["base"],   x - r, y - r, x + r, y + r)
    cv.coords(objs["shade"],  x - r + 1, y - r + 1, x + r - 1, y + r - 1)
    ps0 = r * 0.52
    cv.coords(objs["p0"], _hex_pts(x, y, ps0, 5, offset_angle=-90))
    for i in range(5):
        ang = math.radians(i * 72 - 90)
        px = x + math.cos(ang) * r * 0.65
        py = y + math.sin(ang) * r * 0.65
        ps = r * 0.30
        cv.coords(objs[f"p{i+1}"], _hex_pts(px, py, ps, 5, offset_angle=i * 72))
    sr = r * 0.32
    sx, sy = x - r * 0.28, y - r * 0.28
    cv.coords(objs["shine"],  sx - sr, sy - sr * 0.65, sx + sr, sy + sr * 0.65)
    sr2 = r * 0.13
    cv.coords(objs["shine2"], sx - sr2, sy - sr2, sx + sr2, sy + sr2)


# ─── ПОЛЕ ───────────────────────────────────────────────────────────────────

def generate_pillars():
    global pillars
    pillars = []
    quarter_width  = (width - 2 * margin) / 2
    quarter_height = (height - 2 * margin) / 2
    centers = [
        (margin + quarter_width / 2,         margin + quarter_height / 2),
        (width - margin - quarter_width / 2, margin + quarter_height / 2),
        (margin + quarter_width / 2,         height - margin - quarter_height / 2),
        (width - margin - quarter_width / 2, height - margin - quarter_height / 2),
    ]
    for cx, cy in centers:
        pr = random.randint(15, 25)
        bp = random.uniform(1.5, 2.5)
        pillars.append({"x": cx, "y": cy, "radius": pr, "bounce_power": bp})


def draw_pillars():
    global pillar_objects
    pillar_objects = []
    for p in pillars:
        x1,y1,x2,y2 = p["x"]-p["radius"],p["y"]-p["radius"],p["x"]+p["radius"],p["y"]+p["radius"]
        obj = canvas.create_oval(x1,y1,x2,y2, fill="brown", outline="saddlebrown", width=3)
        pillar_objects.append(obj)
        hr = p["radius"] * 0.4
        canvas.create_oval(p["x"]-hr,p["y"]-hr,p["x"]+hr,p["y"]+hr, fill="peru", outline="")


def check_pillar_collision(x, y, radius):
    for p in pillars:
        dx,dy = x-p["x"], y-p["y"]
        dist = math.hypot(dx, dy)
        if dist < radius + p["radius"]:
            nx,ny = (dx/dist,dy/dist) if dist>0 else (1,0)
            overlap = radius + p["radius"] - dist
            x += nx*overlap; y += ny*overlap
            return x, y, nx, ny, p["bounce_power"]
    return x, y, 0, 0, 0


def generate_puddles():
    global puddles
    puddles = []

    for _ in range(random.randint(3, 6)):
        attempts = 0

        while attempts < 100:
            mr = random.randint(20, 50)

            x = random.randint(margin + mr + 20, width - margin - mr - 20)
            y = random.randint(margin + mr + 20, height - margin - mr - 20)

            if not any(math.hypot(x - p["x"], y - p["y"]) < p["radius"] + mr + 20 for p in pillars):
                break

            attempts += 1

        puddle = {"x": x, "y": y, "radius": mr, "ovals": []}

        for _ in range(random.randint(2, 4)):
            rx = mr + random.randint(-10, 20)
            ry = int(mr * (0.5 + random.random() * 0.5))

            ox = x + random.randint(-10, 10)
            oy = y + random.randint(-10, 10)

            ox = max(margin + rx, min(width - margin - rx, ox))
            oy = max(margin + ry, min(height - margin - ry, oy))

            puddle["ovals"].append({
                "x": ox,
                "y": oy,
                "radius_x": rx,
                "radius_y": ry,
                "alpha": random.randint(20, 40),
            })

        puddles.append(puddle)


def draw_puddles():
    for puddle in puddles:
        for oval in puddle["ovals"]:
            x1,y1 = oval["x"]-oval["radius_x"], oval["y"]-oval["radius_y"]
            x2,y2 = oval["x"]+oval["radius_x"], oval["y"]+oval["radius_y"]
            # Насыщенные светло-синие лужи
            canvas.create_oval(x1, y1, x2, y2, fill="#3eb8f0", outline="")


def is_in_puddle(x, y, radius_check=ball_radius):
    for puddle in puddles:
        for oval in puddle["ovals"]:
            dx,dy = x-oval["x"], y-oval["y"]
            if math.hypot(dx/oval["radius_x"], dy/oval["radius_y"]) < 1.0:
                return True
    return False


def draw_rubber_field(cv):
    """Рисует тёмное резиновое покрытие как в футбольной коробке."""
    base_color = "#2a1a14"
    cv.create_rectangle(margin, margin, width-margin, height-margin,
                        fill=base_color, outline="")
    stripe_colors = ["#2e1d16", "#261610", "#2a1a14"]
    stripe_h = 6
    y = margin
    i = 0
    while y < height - margin:
        cv.create_rectangle(margin, y, width-margin, min(y+stripe_h, height-margin),
                            fill=stripe_colors[i % len(stripe_colors)], outline="")
        y += stripe_h
        i += 1
    rng = random.Random(42)
    for _ in range(400):
        rx = rng.randint(margin+2, width-margin-2)
        ry = rng.randint(margin+2, height-margin-2)
        shade = rng.choice(["#3a2218", "#1e1008", "#2f1a12", "#362010"])
        cv.create_oval(rx, ry, rx+2, ry+2, fill=shade, outline="")


def draw_field():
    canvas.delete("all")

    # Трава по периметру (с травинками)
    draw_grass(canvas)

    # Резиновое покрытие поля
    draw_rubber_field(canvas)

    # Разметка белыми линиями
    canvas.create_rectangle(margin, margin, width-margin, height-margin,
                            outline="white", width=3)
    canvas.create_line(margin, height//2, width-margin, height//2,
                       fill="white", width=3)
    canvas.create_oval(width//2-60, height//2-60, width//2+60, height//2+60,
                       outline="white", width=3)
    canvas.create_oval(width//2-4, height//2-4, width//2+4, height//2+4,
                       fill="white", outline="white")
    canvas.create_rectangle(width//2-PENALTY_HALF_WIDTH, margin,
                            width//2+PENALTY_HALF_WIDTH, margin+120,
                            outline="white", width=3)
    canvas.create_rectangle(width//2-PENALTY_HALF_WIDTH, height-margin-120,
                            width//2+PENALTY_HALF_WIDTH, height-margin,
                            outline="white", width=3)
    canvas.create_rectangle(width//2-SMALL_BOX_HALF_WIDTH, margin,
                            width//2+SMALL_BOX_HALF_WIDTH, margin+50,
                            outline="white", width=3)
    canvas.create_rectangle(width//2-SMALL_BOX_HALF_WIDTH, height-margin-50,
                            width//2+SMALL_BOX_HALF_WIDTH, height-margin,
                            outline="white", width=3)

    # Ворота
    canvas.create_rectangle(width//2-GOAL_HALF_WIDTH, margin-15,
                            width//2+GOAL_HALF_WIDTH, margin,
                            outline="blue", width=3, fill="darkblue")
    canvas.create_rectangle(width//2-GOAL_HALF_WIDTH, height-margin,
                            width//2+GOAL_HALF_WIDTH, height-margin+15,
                            outline="red", width=3, fill="darkred")

    # Имя бота
    canvas.create_text(width//2, margin-30,
                       text=f"{bot_char['name']} (БОТ)",
                       font=("Arial", 12, "bold"), fill="lightblue")

    draw_puddles()
    draw_pillars()
    draw_score()


def draw_score():
    global score_text_bot, score_text_player
    bx = width // 2
    by = margin // 2

    pw, ph = 130, 30
    canvas.create_rectangle(bx - pw//2 - 2, by - ph//2 - 2,
                             bx + pw//2 + 2, by + ph//2 + 2,
                             fill="#111111", outline="#888888", width=1)
    canvas.create_rectangle(bx - pw//2, by - ph//2,
                             bx + pw//2, by + ph//2,
                             fill="#1a1a2e", outline="#4444aa", width=2)
    canvas.create_rectangle(bx - pw//2 + 2, by - ph//2 + 2,
                             bx + pw//2 - 2, by - ph//2 + 5,
                             fill="#3333bb", outline="")

    canvas.create_text(bx - 38, by - 7, text="БОТ",
                       font=("Arial", 6, "bold"), fill="#7799ff")
    canvas.create_text(bx + 38, by - 7, text="ВЫ",
                       font=("Arial", 6, "bold"), fill="#ff8899")
    canvas.create_text(bx, by + 4, text=":",
                       font=("Arial", 18, "bold"), fill="#ffffff")

    score_text_bot = canvas.create_text(bx - 22, by + 4,
        text=str(score_bot), font=("Arial", 18, "bold"), fill="#88aaff")
    score_text_player = canvas.create_text(bx + 22, by + 4,
        text=str(score_player), font=("Arial", 18, "bold"), fill="#ff88aa")


def update_score_display():
    if score_text_bot and score_text_player:
        canvas.itemconfig(score_text_bot,    text=str(score_bot))
        canvas.itemconfig(score_text_player, text=str(score_player))


# ─── ОБЪЕКТЫ ИГРЫ ───────────────────────────────────────────────────────────

def create_game_objects():
    global player_objs, my_keeper_objs, bot_objs, bot_keeper_objs, ball_objs

    player_objs = create_player_objs(
        canvas, player_x, player_y, player_radius,
        selected_char["color"], selected_char["outline"])

    my_keeper_objs = create_player_objs(
        canvas, my_keeper_x, my_keeper_y, my_keeper_radius,
        "yellow", "darkorange", shirt_color="#ffdd44")

    bot_objs = create_player_objs(
        canvas, bot_x, bot_y, bot_radius,
        bot_char["color"], bot_char["outline"])

    bot_keeper_objs = create_player_objs(
        canvas, bot_keeper_x, bot_keeper_y, bot_keeper_radius,
        "cyan", "darkblue", shirt_color="#66eeff")

    ball_objs = create_ball_objs(canvas, ball_x, ball_y, ball_radius)


loop_after_id = None


def reset_positions():
    global player_x, player_y, player_angle
    global my_keeper_x, my_keeper_y, my_keeper_ball_attached, my_keeper_kick_cooldown
    global bot_x, bot_y, bot_angle, bot_ball_attached, bot_kick_cooldown, bot_delay, bot_wander_timer, bot_steal_delay
    global bot_keeper_x, bot_keeper_y, bot_keeper_direction, bot_keeper_jump_cooldown
    global bot_keeper_ball_attached, bot_keeper_kick_cooldown
    global ball_x, ball_y, ball_vx, ball_vy, ball_attached, goal_checked, game_started, loop_after_id, last_touch

    if loop_after_id is not None:
        root.after_cancel(loop_after_id)
        loop_after_id = None

    player_x, player_y, player_angle = width/2, height/2+100, 0.0
    my_keeper_x, my_keeper_y = width/2, height-margin-10
    my_keeper_ball_attached = False; my_keeper_kick_cooldown = 0

    bot_x, bot_y, bot_angle = width/2, height/2-100, 180.0
    bot_ball_attached = False; bot_kick_cooldown = 0
    bot_delay = 45; bot_wander_timer = 0; bot_steal_delay = 0

    bot_keeper_x, bot_keeper_y = width/2, margin+10
    bot_keeper_direction = 1; bot_keeper_jump_cooldown = 0
    bot_keeper_ball_attached = False; bot_keeper_kick_cooldown = 0

    ball_x, ball_y = width/2, height/2
    ball_vx, ball_vy = 0, 0
    ball_attached = False; goal_checked = False; last_touch = None; game_started = False


def stop_menu_animation():
    global menu_anim_id
    if menu_anim_id is not None:
        root.after_cancel(menu_anim_id)
        menu_anim_id = None


def start():
    global in_character_select, game_started, showing_random_char, bot_char
    global bot_radius, bot_speed, bot_turn, bot_kick_power, bot_kick_accuracy
    stop_menu_animation()
    in_character_select = False; showing_random_char = False; game_started = False
    bot_char = select_random_bot()
    bot_radius = bot_char["radius"]
    bot_speed  = bot_char["speed"] * 0.75
    bot_turn   = bot_char["turn"]  * 0.75
    bot_kick_power    = bot_char["kick"]     * 1.2
    bot_kick_accuracy = bot_char["accuracy"] * 1.2
    generate_pillars(); generate_puddles()
    reset_positions()
    draw_field()
    create_game_objects()
    game_loop()


def select_character(char):
    global selected_char, player_radius, player_speed, turn_senor, kick_power, kick_accuracy
    selected_char = char
    player_radius = char["radius"]; player_speed = char["speed"]
    turn_senor = char["turn"];      kick_power   = char["kick"]
    kick_accuracy = char["accuracy"]
    start()


# ─── МЕНЮ ───────────────────────────────────────────────────────────────────

def draw_shimmer_button(cv, x1, y1, x2, y2, label, font, text_color,
                        dark_col, light_col, phase_offset=0.0, tag=None):
    fill    = get_shimmer_color(dark_col, light_col, phase_offset)
    outline = get_shimmer_color(SHIMMER_OUTLINE[0], SHIMMER_OUTLINE[1], phase_offset+1.0)
    rect_id = rounded_rect(cv, x1, y1, x2, y2, r=12,
                           fill=fill, outline=outline, width=2)
    cx, cy  = (x1+x2)//2, (y1+y2)//2
    text_id = cv.create_text(cx, cy, text=label, font=font, fill=text_color)
    if tag:
        _menu_button_ids[tag] = (rect_id, text_id, x1, y1, x2, y2,
                                 label, font, text_color, dark_col, light_col, phase_offset)
    return rect_id, text_id


def animate_menu():
    global menu_anim_phase, menu_anim_id
    menu_anim_phase += 0.06
    for tag, data in _menu_button_ids.items():
        rect_id,_,x1,y1,x2,y2,_,_,_,dark_col,light_col,phase_offset = data
        fill    = get_shimmer_color(dark_col,        light_col,        menu_anim_phase+phase_offset)
        outline = get_shimmer_color(SHIMMER_OUTLINE[0],SHIMMER_OUTLINE[1],menu_anim_phase+phase_offset+1.0)
        canvas.itemconfig(rect_id, fill=fill, outline=outline)
    menu_anim_id = root.after(40, animate_menu)


def show_random_character(char):
    global showing_random_char, random_char, random_play_button_coords
    stop_menu_animation(); _menu_button_ids.clear()
    showing_random_char = True; random_char = char
    canvas.delete("all")
    canvas.create_rectangle(0,0,width,height, fill="#0d2a0d")
    rounded_rect(canvas,20,20,width-20,height-20,r=18,outline="#2a7a2a",width=2,fill="")
    canvas.create_text(width//2,height//2-90,text="🎲 СЛУЧАЙНЫЙ ВЫБОР",font=("Arial",22,"bold"),fill="#ffcc44")
    canvas.create_text(width//2,height//2-45,text="Вы играете за:",font=("Arial",15),fill="#aaffaa")
    nc = char["color"] if char["color"] not in ("black","green") else ("#eeeeee" if char["color"]=="black" else "#88ff88")
    rounded_rect(canvas,width//2-110,height//2-20,width//2+110,height//2+20,r=10,fill="#1a3a1a",outline=nc,width=2)
    canvas.create_text(width//2,height//2,text=char["name"],font=("Arial",30,"bold"),fill=nc)
    canvas.create_text(width//2,height//2+45,
        text=f"Скорость: {char['speed']}  |  Удар: {char['kick']}  |  Поворот: {char['turn']}  |  Точность: {char['accuracy']}°",
        font=("Arial",11),fill="#cccccc")
    bx1,by1,bx2,by2 = width//2-90,height//2+80,width//2+90,height//2+122
    draw_shimmer_button(canvas,bx1,by1,bx2,by2,"▶  ИГРАТЬ",("Arial",17,"bold"),"white",
                        SHIMMER_PLAY[0],SHIMMER_PLAY[1],phase_offset=0.0,tag="play_btn")
    random_play_button_coords = (bx1,by1,bx2,by2)
    animate_menu()


def select_random_character():
    show_random_character(random.choice(characters))


def show_character_select():
    global in_character_select
    stop_menu_animation(); _menu_button_ids.clear()
    in_character_select = True
    canvas.delete("all")
    for i in range(height):
        t = i/height
        r_c=int(0x0d+(0x05-0x0d)*t); g_c=int(0x2a+(0x18-0x2a)*t); b_c=int(0x0d+(0x28-0x0d)*t)
        canvas.create_line(0,i,width,i,fill=f"#{r_c:02x}{g_c:02x}{b_c:02x}")
    rounded_rect(canvas,12,12,width-12,height-12,r=18,outline="#2a6a3a",width=2,fill="")
    canvas.create_text(width//2+2,42,text="⚽  ВЫБОР ПЕРСОНАЖА",font=("Arial",21,"bold"),fill="#003300")
    canvas.create_text(width//2,40,text="⚽  ВЫБОР ПЕРСОНАЖА",font=("Arial",21,"bold"),fill="#eeffee")
    rand_x1,rand_y1,rand_x2,rand_y2 = width//2-115,62,width//2+115,100
    draw_shimmer_button(canvas,rand_x1,rand_y1,rand_x2,rand_y2,
        "🎲  СЛУЧАЙНЫЙ ВЫБОР",("Arial",13,"bold"),"white",
        SHIMMER_RANDOM[0],SHIMMER_RANDOM[1],phase_offset=0.0,tag="rand_btn")
    global random_button_coords
    random_button_coords = (rand_x1,rand_y1,rand_x2,rand_y2)
    btn_w,btn_h,start_y,gap = 220,76,112,10
    for i,char in enumerate(characters):
        x1 = width//2-btn_w//2
        y1 = start_y+i*(btn_h+gap)
        x2,y2 = x1+btn_w, y1+btn_h
        draw_shimmer_button(canvas,x1,y1+2,x2,y2+2,"",None,None,
                            SHIMMER_CHAR[0],SHIMMER_CHAR[1],phase_offset=i*0.55,tag=f"char_{i}")
        cc = char["color"]
        if cc in ("black","green"): cc = "#ffffff" if char["color"]=="black" else "#88ff88"
        canvas.create_text(width//2,y1+24,text=char["name"],font=("Arial",15,"bold"),fill=cc)
        canvas.create_text(width//2,y1+50,
            text=f"Скорость: {char['speed']}  |  Удар: {char['kick']}",font=("Arial",9),fill="#cccccc")
        canvas.create_text(width//2,y1+63,
            text=f"Поворот: {char['turn']}  |  Точность: {char['accuracy']}°",font=("Arial",9),fill="#aaaaaa")
        char["button_coords"] = (x1,y1,x2,y2)
    animate_menu()


def on_click(event):
    global in_character_select, showing_random_char
    if showing_random_char:
        x1,y1,x2,y2 = random_play_button_coords
        if x1<=event.x<=x2 and y1<=event.y<=y2: select_character(random_char)
        return
    if not in_character_select: return
    x1,y1,x2,y2 = random_button_coords
    if x1<=event.x<=x2 and y1<=event.y<=y2: select_random_character(); return
    for char in characters:
        if "button_coords" in char:
            x1,y1,x2,y2 = char["button_coords"]
            if x1<=event.x<=x2 and y1<=event.y<=y2: select_character(char); return


# ─── UPDATE VISUALS ──────────────────────────────────────────────────────────

def update_visuals():
    move_player_objs(canvas, player_objs,      player_x,    player_y,    player_radius,    player_angle)
    move_player_objs(canvas, my_keeper_objs,   my_keeper_x, my_keeper_y, my_keeper_radius, 0.0)
    move_player_objs(canvas, bot_objs,         bot_x,       bot_y,       bot_radius,       bot_angle)
    move_player_objs(canvas, bot_keeper_objs,  bot_keeper_x,bot_keeper_y,bot_keeper_radius,180.0)
    move_ball_objs(canvas, ball_objs, ball_x, ball_y, ball_radius)


# ─── ЛОГИКА ИГРЫ ────────────────────────────────────────────────────────────

def end_game(scorer):
    global score_player, score_bot
    if scorer == "player":
        score_player += 1
        text, color = "ГОЛ!", "gold"
    else:
        score_bot += 1
        text, color = "ПРОПУЩЕН ГОЛ!", "red"
    canvas.create_text(width//2+2, height//2+2, text=text, font=("Arial",48,"bold"), fill="black")
    canvas.create_text(width//2,   height//2,   text=text, font=("Arial",48,"bold"), fill=color)
    root.after(3000, start)


def check_goal():
    if width//2-GOAL_HALF_WIDTH < ball_x < width//2+GOAL_HALF_WIDTH and margin-15 < ball_y < margin:
        return "player"
    if width//2-GOAL_HALF_WIDTH < ball_x < width//2+GOAL_HALF_WIDTH and height-margin < ball_y < height-margin+15:
        return "bot"
    return None


def try_pick_ball():
    global ball_attached, last_touch, bot_ball_attached, bot_keeper_ball_attached, my_keeper_ball_attached
    dx,dy = ball_x-player_x, ball_y-player_y
    if math.hypot(dx,dy) < 30:
        if bot_keeper_ball_attached:
            if math.hypot(player_x-bot_keeper_x,player_y-bot_keeper_y) < bot_keeper_radius+player_radius+20:
                bot_keeper_ball_attached = False
            else: return
        if my_keeper_ball_attached:
            if math.hypot(player_x-my_keeper_x,player_y-my_keeper_y) < my_keeper_radius+player_radius+20:
                my_keeper_ball_attached = False
            else: return
        if bot_ball_attached: bot_ball_attached = False
        ball_attached = True; last_touch = "player"


def kick_ball():
    global ball_attached, ball_vx, ball_vy
    if not ball_attached: return
    ball_attached = False
    rad = math.radians(player_angle) + math.radians(random.uniform(-kick_accuracy, kick_accuracy))
    ball_vx = math.sin(rad) * kick_power
    ball_vy = -math.cos(rad) * kick_power


def update_my_keeper():
    global my_keeper_x, my_keeper_ball_attached, my_keeper_kick_cooldown
    global ball_attached, ball_vx, ball_vy, last_touch, ball_x, ball_y
    global bot_ball_attached, bot_keeper_ball_attached
    if my_keeper_kick_cooldown > 0: my_keeper_kick_cooldown -= 1
    kl = width//2-GOAL_HALF_WIDTH+my_keeper_radius
    kr = width//2+GOAL_HALF_WIDTH-my_keeper_radius
    if "left"  in keys_pressed: my_keeper_x = max(kl, my_keeper_x-my_keeper_speed)
    if "right" in keys_pressed: my_keeper_x = min(kr, my_keeper_x+my_keeper_speed)
    dist = math.hypot(ball_x-my_keeper_x, ball_y-my_keeper_y)
    if not my_keeper_ball_attached and dist < my_keeper_radius+ball_radius+10:
        ball_attached=False; bot_ball_attached=False; bot_keeper_ball_attached=False
        my_keeper_ball_attached=True; ball_attached=True; last_touch="my_keeper"
    if my_keeper_ball_attached and my_keeper_kick_cooldown==0:
        if "space" in keys_pressed or "e" in keys_pressed:
            rad = math.radians(random.uniform(-15,15))
            ball_vx=math.sin(rad)*10; ball_vy=-math.cos(rad)*10
            my_keeper_ball_attached=False; ball_attached=False
            last_touch="my_keeper"; my_keeper_kick_cooldown=30


def update_bot():
    global bot_x,bot_y,bot_angle,bot_ball_attached,bot_kick_cooldown,bot_delay,bot_wander_timer,bot_steal_delay
    global ball_attached,ball_vx,ball_vy,last_touch,ball_x,ball_y

    if bot_delay>0: bot_delay-=1; return
    if bot_kick_cooldown>0: bot_kick_cooldown-=1
    if bot_steal_delay>0:   bot_steal_delay-=1

    bot_wander_timer -= 1
    if bot_wander_timer <= 0:
        bot_wander_timer = random.randint(20, 50)
        if random.random() < 0.15:
            bot_angle += random.uniform(-25, 25)

    target_x = ball_x
    target_y = ball_y
    if bot_ball_attached:
        target_x = width/2 + random.uniform(-15, 15)
        target_y = height - margin + 15

    dx, dy = target_x - bot_x, target_y - bot_y
    target_angle = math.degrees(math.atan2(dx, -dy))
    angle_diff = target_angle - bot_angle
    while angle_diff > 180:  angle_diff -= 360
    while angle_diff < -180: angle_diff += 360

    if abs(angle_diff) > bot_turn:
        bot_angle += bot_turn if angle_diff > 0 else -bot_turn
    else:
        bot_angle = target_angle

    rad = math.radians(bot_angle)
    distance_to_target = math.hypot(dx, dy)

    kick_distance = random.randint(80, 280)
    if bot_ball_attached and distance_to_target < kick_distance and bot_kick_cooldown == 0:
        target_goal_x = width//2 + random.uniform(-20, 20)
        target_goal_y = height - margin + random.uniform(-5, 10)
        goal_dx = target_goal_x - bot_x
        goal_dy = target_goal_y - bot_y
        goal_angle = math.atan2(goal_dx, -goal_dy)
        deviation = random.uniform(-bot_kick_accuracy, bot_kick_accuracy)
        kick_rad = goal_angle + math.radians(deviation)
        ball_vx = math.sin(kick_rad) * bot_kick_power
        ball_vy = -math.cos(kick_rad) * bot_kick_power
        bot_ball_attached = False
        ball_attached = False
        last_touch = "bot"
        bot_kick_cooldown = 45
        return

    if not bot_ball_attached and ball_attached and last_touch == "player":
        dist_to_player = math.hypot(player_x - bot_x, player_y - bot_y)
        if dist_to_player < 35:
            if bot_steal_delay == 0:
                bot_steal_delay = 20
            elif bot_steal_delay == 1 and random.random() < 0.4:
                bot_ball_attached = True
                ball_attached = True
                last_touch = "bot"
                bot_steal_delay = 0

    if not bot_ball_attached and not ball_attached:
        dist_to_ball = math.hypot(ball_x - bot_x, ball_y - bot_y)
        if dist_to_ball < 30 and random.random() < 0.85:
            bot_ball_attached = True
            ball_attached = True
            last_touch = "bot"

    should_move = False
    if bot_ball_attached and distance_to_target > 10:
        should_move = random.random() < 0.95
    elif not bot_ball_attached and distance_to_target > 30:
        should_move = random.random() < 0.85

    if should_move:
        current_speed = bot_speed * (0.5 if is_in_puddle(bot_x, bot_y, bot_radius) else 1.0)
        new_x = max(margin+bot_radius, min(width-margin-bot_radius, bot_x + math.sin(rad)*current_speed))
        new_y = max(margin+bot_radius, min(height-margin-bot_radius, bot_y - math.cos(rad)*current_speed))
        new_x, new_y, _, _, _ = check_pillar_collision(new_x, new_y, bot_radius)
        bot_x, bot_y = new_x, new_y


def update_bot_keeper():
    global bot_keeper_x,bot_keeper_direction,bot_keeper_jump_cooldown
    global bot_keeper_ball_attached,bot_keeper_kick_cooldown
    global ball_attached,ball_vx,ball_vy,last_touch,ball_x,ball_y

    if bot_keeper_kick_cooldown>0: bot_keeper_kick_cooldown-=1
    if bot_keeper_jump_cooldown>0: bot_keeper_jump_cooldown-=1

    kl=width//2-GOAL_HALF_WIDTH+bot_keeper_radius
    kr=width//2+GOAL_HALF_WIDTH-bot_keeper_radius

    bot_keeper_x+=bot_keeper_speed*bot_keeper_direction
    if bot_keeper_x>=kr: bot_keeper_x=kr; bot_keeper_direction=-1
    elif bot_keeper_x<=kl: bot_keeper_x=kl; bot_keeper_direction=1

    if bot_keeper_jump_cooldown==0:
        jmp=18
        bot_keeper_x = max(kl, bot_keeper_x-jmp) if ball_x < bot_keeper_x else min(kr, bot_keeper_x+jmp)
        bot_keeper_jump_cooldown = random.randint(30, 50)

    dist=math.hypot(ball_x-bot_keeper_x,ball_y-bot_keeper_y)
    if not bot_keeper_ball_attached and dist<bot_keeper_radius+ball_radius+10:
        ball_attached=False; bot_ball_attached=False
        bot_keeper_ball_attached=True; ball_attached=True; last_touch="bot_keeper"

    if bot_keeper_ball_attached and bot_keeper_kick_cooldown==0:
        dx=bot_x-bot_keeper_x+random.uniform(-80,80)
        dy=abs(bot_y-bot_keeper_y)+random.uniform(50,150)
        ang=math.atan2(dx,dy); pwr=8
        ball_vx=math.sin(ang)*pwr; ball_vy=math.cos(ang)*pwr
        bot_keeper_ball_attached=False; ball_attached=False
        last_touch="bot_keeper"; bot_keeper_kick_cooldown=45


def on_press(event):
    global ball_attached, my_keeper_ball_attached, bot_ball_attached, bot_keeper_ball_attached
    key = event.keysym.lower()
    keys_pressed.add(key)
    if key=="e": try_pick_ball()
    if key=="space":
        if ball_attached and last_touch=="player": kick_ball()
        elif my_keeper_ball_attached: pass
        else: try_pick_ball()
    if key=="q":
        ball_attached=False; bot_ball_attached=False
        bot_keeper_ball_attached=False; my_keeper_ball_attached=False


def on_release(event):
    keys_pressed.discard(event.keysym.lower())


def game_loop():
    global player_x,player_y,player_angle
    global my_keeper_x,my_keeper_ball_attached,my_keeper_kick_cooldown
    global bot_x,bot_y,bot_angle,bot_ball_attached,bot_kick_cooldown,bot_delay,bot_wander_timer,bot_steal_delay
    global bot_keeper_x,bot_keeper_y,bot_keeper_direction,bot_keeper_jump_cooldown
    global bot_keeper_ball_attached,bot_keeper_kick_cooldown
    global ball_x,ball_y,ball_vx,ball_vy,ball_attached,goal_checked,game_started,loop_after_id,last_touch
    if game_started: return
    game_started = True

    def loop():
        global player_x,player_y,player_angle
        global my_keeper_x,my_keeper_ball_attached,my_keeper_kick_cooldown
        global bot_x,bot_y,bot_angle,bot_ball_attached,bot_kick_cooldown,bot_delay,bot_wander_timer,bot_steal_delay
        global bot_keeper_x,bot_keeper_y,bot_keeper_direction,bot_keeper_jump_cooldown
        global bot_keeper_ball_attached,bot_keeper_kick_cooldown
        global ball_x,ball_y,ball_vx,ball_vy,ball_attached,goal_checked,loop_after_id,last_touch

        if "a" in keys_pressed: player_angle -= turn_senor
        if "d" in keys_pressed: player_angle += turn_senor
        for key,sign in [("w",1),("s",-1)]:
            if key in keys_pressed:
                rad=math.radians(player_angle)
                sp=player_speed*(0.5 if is_in_puddle(player_x,player_y,player_radius) else 1.0)
                nx=max(margin+player_radius,min(width-margin-player_radius, player_x+math.sin(rad)*sp*sign))
                ny=max(margin+player_radius,min(height-margin-player_radius,player_y-math.cos(rad)*sp*sign))
                nx,ny,_,_,_ = check_pillar_collision(nx,ny,player_radius)
                player_x,player_y = nx,ny

        update_my_keeper(); update_bot(); update_bot_keeper()
        rad=math.radians(player_angle)

        if ball_attached:
            if last_touch=="player":
                off=player_radius+ball_radius+4
                ball_x=player_x+math.sin(rad)*off; ball_y=player_y-math.cos(rad)*off
            elif last_touch=="bot":
                br=math.radians(bot_angle); off=bot_radius+ball_radius+4
                ball_x=bot_x+math.sin(br)*off; ball_y=bot_y-math.cos(br)*off
            elif last_touch=="bot_keeper":
                off=bot_keeper_radius+ball_radius+4
                ball_x=bot_keeper_x; ball_y=bot_keeper_y+off
            elif last_touch=="my_keeper":
                off=my_keeper_radius+ball_radius+4
                ball_x=my_keeper_x; ball_y=my_keeper_y-off
        else:
            ball_x+=ball_vx; ball_y+=ball_vy
            nbx,nby,nx,ny,bp=check_pillar_collision(ball_x,ball_y,ball_radius)
            if bp>0:
                ball_x,ball_y=nbx,nby
                dp=ball_vx*nx+ball_vy*ny
                ball_vx=(ball_vx-2*dp*nx)*bp; ball_vy=(ball_vy-2*dp*ny)*bp
            fric=0.95 if is_in_puddle(ball_x,ball_y) else 0.99
            ball_vx*=fric; ball_vy*=fric
            in_goal_x = width//2-GOAL_HALF_WIDTH < ball_x < width//2+GOAL_HALF_WIDTH
            top    = (margin-15+ball_radius) if in_goal_x else (margin+ball_radius)
            bottom = (height-margin+15-ball_radius) if in_goal_x else (height-margin-ball_radius)
            left=margin+ball_radius; right=width-margin-ball_radius
            if ball_x<left:   ball_x=left;   ball_vx*=-0.8
            if ball_x>right:  ball_x=right;  ball_vx*=-0.8
            if ball_y<top:    ball_y=top;     ball_vy*=-0.8
            if ball_y>bottom: ball_y=bottom;  ball_vy*=-0.8

        scorer=check_goal()
        if not goal_checked and scorer:
            goal_checked=True; end_game(scorer)

        update_visuals()
        update_score_display()
        loop_after_id=root.after(16,loop)

    loop()


root.bind("<KeyPress>",   on_press)
root.bind("<KeyRelease>", on_release)
root.bind("<Button-1>",   on_click)

show_character_select()
root.mainloop()
