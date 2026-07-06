import pygame
import random
import math
import time
import sys

# =================ตั้งค่าเริ่มต้น=================
COLS, ROWS = 30, 30
CELL_SIZE = 16
UI_HEIGHT = 120
WIDTH = (COLS * CELL_SIZE) + 2  # +2 กันขอบแหว่ง
HEIGHT = (ROWS * CELL_SIZE) + UI_HEIGHT + 2 # +2 กันขอบแหว่ง
FPS = 60
TIMEOUT = 180 # 3 นาที (180 วินาที)

# สี
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
MOUSE_COLOR = (150, 150, 255)
CHEESE_COLOR = (255, 200, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)

def generate_maze(cols, rows):
    """สร้างเขาวงกตด้วย DFS แบบให้มีทางออกแน่นอน (ไม่เปลี่ยนแปลง)"""
    grid = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    stack = []
    
    start_c, start_r = 0, 0
    visited[start_r][start_c] = True
    stack.append((start_c, start_r))
    
    while stack:
        c, r = stack[-1]
        neighbors = []
        if r > 0 and not visited[r-1][c]: neighbors.append(('N', c, r-1))
        if c < cols-1 and not visited[r][c+1]: neighbors.append(('E', c+1, r))
        if r < rows-1 and not visited[r+1][c]: neighbors.append(('S', c, r+1))
        if c > 0 and not visited[r][c-1]: neighbors.append(('W', c-1, r))
        
        if neighbors:
            direction, nc, nr = random.choice(neighbors)
            if direction == 'N':
                grid[r][c][0] = False
                grid[nr][nc][2] = False
            elif direction == 'E':
                grid[r][c][1] = False
                grid[nr][nc][3] = False
            elif direction == 'S':
                grid[r][c][2] = False
                grid[nr][nc][0] = False
            elif direction == 'W':
                grid[r][c][3] = False
                grid[nr][nc][1] = False
            visited[nr][nc] = True
            stack.append((nc, nr))
        else:
            stack.pop()
    return grid

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smelly Maze - AUTO AI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("tahoma", 16)
    large_font = pygame.font.SysFont("tahoma", 24, bold=True)

    maze = generate_maze(COLS, ROWS)
    
    rat_c, rat_r = 0, 0
    cheese_c, cheese_r = COLS - 1, ROWS - 1
    
    thinking_count = 0
    last_move_time = time.time()
    
    game_state = "PLAYING" # PLAYING, WON, LOST
    msg = "AI: Scanning smell..."

    # =================ตัวแปรสำหรับระบบสมอง AI=================
    ai_visited = set()            # จุดที่เคยเดินไปแล้ว
    ai_visited.add((rat_c, rat_r))
    ai_stack = []                 # เก็บเส้นทางไว้สำหรับถอยหลัง (Backtrack)
    ai_bumped_walls = set()       # จำกำแพงที่เคยชนไปแล้วจะได้ไม่ชนซ้ำ
    AUTO_DELAY = 50               # ความเร็วในการขยับของ AI (มิลลิวินาที)
    last_auto_tick = pygame.time.get_ticks()

    running = True
    while running:
        current_ticks = pygame.time.get_ticks()
        current_time = time.time()
        time_left = TIMEOUT - (current_time - last_move_time)
        
        # เงื่อนไขหนูตาย (เวลาหมด)
        if game_state == "PLAYING" and time_left <= 0:
            game_state = "LOST"
            msg = "GAME OVER: Mouse died from thinking too long!"
            time_left = 0

        # Event Handling (เหลือแค่กดปิดเกม)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # =================ระบบ AI ประมวลผลการเดิน=================
        if game_state == "PLAYING" and (current_ticks - last_auto_tick) > AUTO_DELAY:
            last_auto_tick = current_ticks
            
            # เช็คว่าถึงทางออกหรือยัง
            if rat_c == cheese_c and rat_r == cheese_r:
                if thinking_count >= 5:
                    game_state = "WON"
                    msg = "AI WIN! The mouse got the cheese!"
                else:
                    thinking_count += 1
                    msg = "AI: Cheese locked! Thinking at door... (+1)"
                    last_move_time = time.time()
            else:
                # 1. เรียงลำดับทิศทางที่ "ใกล้ชีสที่สุด" (ตามกลิ่น)
                # 0: บน, 1: ขวา, 2: ล่าง, 3: ซ้าย
                dirs = [
                    (0, (rat_c, rat_r - 1)),
                    (1, (rat_c + 1, rat_r)),
                    (2, (rat_c, rat_r + 1)),
                    (3, (rat_c - 1, rat_r))
                ]
                # เรียงลำดับด้วยระยะกระจัด (Euclidean Distance)
                dirs.sort(key=lambda d: math.hypot(cheese_c - d[1][0], cheese_r - d[1][1]))
                
                moved = False
                for wall_idx, target_pos in dirs:
                    # ถ้าทางนี้เคยเดินไปแล้ว AI จะหลีกเลี่ยง (ยกเว้นทางตัน)
                    if target_pos in ai_visited:
                        continue
                        
                    # ทางนี้ไม่เคยไป และอยู่ใกล้ชีส! ลองไปดูซิว่ามีกำแพงไหม?
                    if maze[rat_r][rat_c][wall_idx]:
                        # มีกำแพงกั้น! หนูเดินชน
                        if (rat_c, rat_r, wall_idx) not in ai_bumped_walls:
                            ai_bumped_walls.add((rat_c, rat_r, wall_idx))
                            thinking_count += 1
                            msg = f"AI: Bumped wall! (Think +1)"
                            last_move_time = time.time()
                            moved = True # หยุดคิด 1 จังหวะ
                            break
                    else:
                        # ไม่มีกำแพง! เดินไปได้เลย
                        ai_stack.append((rat_c, rat_r)) # จำทางไว้เผื่อหลง
                        rat_c, rat_r = target_pos
                        ai_visited.add((rat_c, rat_r))
                        msg = "AI: Following cheese smell..."
                        last_move_time = time.time()
                        moved = True
                        break
                        
                # ถ้าประเมินครบทุกทิศแล้วเดินไปไหนไม่ได้เลย (ทางตัน) -> ถอยหลัง!
                if not moved:
                    if len(ai_stack) > 0:
                        rat_c, rat_r = ai_stack.pop()
                        thinking_count += 1
                        msg = "AI: Dead end! Backtracked (Think + 1)"
                        last_move_time = time.time()
                    else:
                        game_state = "LOST"
                        msg = "AI Error: Stuck!"

        # ---------------- การวาดหน้าจอ (Rendering) ----------------
        screen.fill(BLACK)

        # 1. วาดเขาวงกต (มองเห็นทั้งหมดเหมือนเดิม)
        for r in range(ROWS):
            for c in range(COLS):
                x = c * CELL_SIZE
                y = r * CELL_SIZE + UI_HEIGHT
                pygame.draw.rect(screen, (30, 30, 30), (x, y, CELL_SIZE, CELL_SIZE))
                if maze[r][c][0]: pygame.draw.line(screen, WHITE, (x, y), (x + CELL_SIZE, y), 1)
                if maze[r][c][1]: pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 1)
                if maze[r][c][2]: pygame.draw.line(screen, WHITE, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 1)
                if maze[r][c][3]: pygame.draw.line(screen, WHITE, (x, y), (x, y + CELL_SIZE), 1)

        # วาดรอยเท้า AI (แถมให้เพื่อความสวยงาม ให้เห็นว่า AI เคยเดินไปไหนมาแล้วบ้าง)
        for (vc, vr) in ai_visited:
            vx = vc * CELL_SIZE + 6
            vy = vr * CELL_SIZE + UI_HEIGHT + 6
            pygame.draw.rect(screen, (80, 80, 150), (vx, vy, 4, 4))

        # 2. วาดชีส
        cheese_x = cheese_c * CELL_SIZE + 2
        cheese_y = cheese_r * CELL_SIZE + UI_HEIGHT + 2
        pygame.draw.rect(screen, CHEESE_COLOR, (cheese_x, cheese_y, CELL_SIZE-4, CELL_SIZE-4))

        # 3. วาดหนู
        rat_x = rat_c * CELL_SIZE + 2
        rat_y = rat_r * CELL_SIZE + UI_HEIGHT + 2
        pygame.draw.rect(screen, MOUSE_COLOR, (rat_x, rat_y, CELL_SIZE-4, CELL_SIZE-4))

        # 4. วาด UI
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, UI_HEIGHT))
        dist = math.hypot((cheese_c - rat_c), (cheese_r - rat_r)) * 16
        ui_texts = [
            f"Distance to Cheese: {dist:.2f} cm",
            f"Time Left (This move): {int(time_left)} sec",
            f"Thinking Count: {thinking_count} / 5",
            f"Status: {msg}"
        ]
        
        for i, text in enumerate(ui_texts):
            color = WHITE
            if i == 1 and time_left < 30: color = RED
            if i == 2 and thinking_count >= 5: color = GREEN
            text_surf = font.render(text, True, color)
            screen.blit(text_surf, (10, 10 + (i * 25)))

        if game_state == "WON":
            win_surf = large_font.render("YOU WIN!", True, GREEN)
            screen.blit(win_surf, (WIDTH//2 - 60, UI_HEIGHT//2 - 20))
        elif game_state == "LOST":
            lost_surf = large_font.render("GAME OVER", True, RED)
            screen.blit(lost_surf, (WIDTH//2 - 70, UI_HEIGHT//2 - 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()