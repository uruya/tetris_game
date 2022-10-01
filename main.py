import tkinter as tk
from queue import Queue
import numpy as np
from random import randint
from time import time

GAME_W, GAME_H = 10, 18
SCN_W, SCN_H = 400, 720
BLOCK_W, BLOCK_H = SCN_W // GAME_W, SCN_H // GAME_H
TIMER_WAIT = 50

get_time = lambda: time() * 1000
out_of_screen = lambda x, y: x < 0 or x >= GAME_W or y < 0 or y >= GAME_H
g_pos = {'x': 0, 'y': 0}
g_events = Queue()

def init_game():
    global g_buf, g_pat, g_time, g_scene
    g_buf = [[0 for _ in range(GAME_W)] for _ in range(GAME_H)]
    g_pat, g_time, g_scene = None, get_time(), 0 # g_scene = 0: Playing, 1: Game Over

def create_pattern():
    pats = [['0100', '0100', '0100', '0100'], ['0000', '0100', '0110', '0100'],
    ['0000', '0110', '0100', '0100'], ['0000', '0110', '0010', '0010'],
    ['0000', '0010', '0110', '0100'], ['0000', '0100', '0110', '0010']]

    return [p := pats[randint(0, 5)], [p := np.rot90(np.array(list(map(lambda x: [int(v) for v in x], p)), int)).tolist() for _ in range(randint(1, 4))][-1]][1]

def is_crashed(pat, x, y):
    for i in range(16):
        if pat[i // 4][i % 4]:
            if out_of_screen(i % 4 + x, i // 4 + y) or pat[i // 4][i % 4] & g_buf[i // 4 + y][i % 4 + x]:
                return True
    return False

def draw_one_block(canvas, x, y):
    if not out_of_screen(x, y):
        x1, y1 = x * BLOCK_W, y * BLOCK_H
        x2, y2 = x1 + BLOCK_W - 1, y1 + BLOCK_H - 1
        canvas.create_rectangle(x1, y1, x2, y2, fill='white', width=0, tag='objects')

def draw_game(canvas):
    canvas.delete('objects')

    for i in range(GAME_W * GAME_H):
        if g_buf[i // GAME_W][i % GAME_W]:
            draw_one_block(canvas, i % GAME_W, i // GAME_W)
    if g_pat:
        for i in range(4 * 4):
            if g_pat[i // 4][i % 4]:
                draw_one_block(canvas, i % 4 + g_pos['x'], i // 4 + g_pos['y'])
    if g_scene == 1:
        canvas.create_rectangle(40, SCN_H // 2 - 50, SCN_W - 40, SCN_H // 2 + 50, fill='gray', tag='objects')
        canvas.create_text(SCN_W // 2, SCN_H // 2, text='GameOver\n\nPlease Space Key', font=('Monospace', 14, 'bold'), justify='center', fill='white', anchor='center', tag='objects')

def main_proc(root, canvas):
    global g_buf, g_pat, g_time, g_scene

    if(e := g_events.get() if not g_events.empty() else None) is not None:
        if g_scene == 0 and g_pat is not None:
            if e == 'Left': g_pos['x'] += -1 if not is_crashed(g_pat, g_pos['x'] - 1, g_pos['y']) else 0
            elif e == 'Right': g_pos['x'] += 1 if not is_crashed(g_pat, g_pos['x'] + 1, g_pos['y']) else 0
            elif e == 'space': g_pat = pat if not is_crashed(pat := np.rot90(np.array(g_pat, int)).tolist(), **g_pos) else g_pat
            elif g_scene == 1 and e == 'space':
                init_game()
    
    if g_scene == 0:
        if g_pat is None:
            g_pat = create_pattern()
            for top in range(4):
                if any(g_pat[top]):
                    g_pos['x'], g_pos['y'] = (GAME_W - 4) // 2, -top
                    break
            g_scene = 1 if is_crashed(g_pat, **g_pos) else 0
        
        if get_time() - g_time > 400 or e == 'Down':
            if is_crashed(g_pat, g_pos['x'], g_pos['y'] + 1):
                for y in range(4):
                    for x in range(4):
                        if not out_of_screen(g_pos['x'] + x, g_pos['y'] + y):
                            g_buf[g_pos['y'] + y][g_pos['x'] + x] |= g_pat[y][x]
                g_pat = None
                new_buf = list(filter(lambda line: not all(line), g_buf))
                g_buf = [[0 for _ in range(GAME_W)] for _ in range(GAME_H - len(new_buf))] + new_buf
            else:
                g_pos['y'] += 1

            g_time = get_time()
    draw_game(canvas)
    root.after(TIMER_WAIT, main_proc, root, canvas)

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry(f'{SCN_W}x{SCN_H}')
    canvas = tk.Canvas(root, width=SCN_W, height=SCN_H, bg='black')
    canvas.place(x=0, y=0)
    root.bind('<Key>', lambda e: g_events.put(e.keysym) if e.keysym in ('Left', 'Right', 'Down', 'space') else None)
    init_game()
    root.after(TIMER_WAIT, main_proc, root, canvas)
    root.mainloop()
