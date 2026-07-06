import pygame
import random
import math
import time
import sys

# =================ตั้งค่าเริ่มต้น=================
COLS, ROWS = 30, 30
CELL_SIZE = 16
UI_HEIGHT = 120
WIDTH = COLS * CELL_SIZE +5
HEIGHT = (ROWS * CELL_SIZE) + UI_HEIGHT +5
FPS = 30
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
    """สร้างเขาวงกตด้วย DFS แบบให้มีทางออกแน่นอน"""
    # [Top, Right, Bottom, Left] True = มีกำแพง
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
    pygame.display.set_caption("Smelly Maze (เขาวงกตกลิ่นชีส)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("tahoma", 16) # ใช้ Tahoma เพื่อรองรับภาษาไทยหรืออ่านง่าย
    large_font = pygame.font.SysFont("tahoma", 24, bold=True)

    maze = generate_maze(COLS, ROWS)
    
    rat_c, rat_r = 0, 0
    cheese_c, cheese_r = COLS - 1, ROWS - 1
    
    visited_cells = set()
    visited_cells.add((rat_c, rat_r))
    
    thinking_count = 0
    last_move_time = time.time()
    
    game_state = "PLAYING" # PLAYING, WON, LOST
    msg = "Find the Cheese! (Need 5 thinks)"

    running = True
    while running:
        current_time = time.time()
        time_left = TIMEOUT - (current_time - last_move_time)
        
        # เงื่อนไขหนูตาย (คิดเกิน 3 นาที)
        if game_state == "PLAYING" and time_left <= 0:
            game_state = "LOST"
            msg = "GAME OVER: Mouse died from thinking too long (> 3 mins)!"
            time_left = 0

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and game_state == "PLAYING":
                moved = False
                bumped = False
                
                # เช็คทิศทางและการชนกำแพง [Top, Right, Bottom, Left]
                if event.key == pygame.K_UP:
                    if not maze[rat_r][rat_c][0]: rat_r -= 1; moved = True
                    else: bumped = True
                elif event.key == pygame.K_RIGHT:
                    if not maze[rat_r][rat_c][1]: rat_c += 1; moved = True
                    else: bumped = True
                elif event.key == pygame.K_DOWN:
                    if not maze[rat_r][rat_c][2]: rat_r += 1; moved = True
                    else: bumped = True
                elif event.key == pygame.K_LEFT:
                    if not maze[rat_r][rat_c][3]: rat_c -= 1; moved = True
                    else: bumped = True

                # อัปเดตตรรกะหลังขยับ/ชน
                if bumped:
                    thinking_count += 1
                    msg = "Bumped wall! Think Count + 1"
                
                if moved:
                    last_move_time = time.time() # รีเซ็ตเวลาเมื่อมีการขยับสำเร็จ
                    if (rat_c, rat_r) in visited_cells:
                        thinking_count += 1 # เดินย้อนกลับช่องเดิม = ได้คิด
                        msg = "Backtracked! Think Count + 1"
                    else:
                        msg = "Moving..."
                    visited_cells.add((rat_c, rat_r))

                # เช็คจุดจบ
                if rat_c == cheese_c and rat_r == cheese_r:
                    if thinking_count >= 5:
                        game_state = "WON"
                        msg = "YOU WIN! The mouse got the cheese!"
                    else:
                        msg = "At exit, but cheese is LOCKED! (Need 5 thinks)"

        # ---------------- การวาดหน้าจอ (Rendering) ----------------
        screen.fill(BLACK)

        # 1. วาดเขาวงกต (มองเห็นทั้งหมด)
        for r in range(ROWS):
            for c in range(COLS):
                x = c * CELL_SIZE
                y = r * CELL_SIZE + UI_HEIGHT
                
                # วาดพื้น
                pygame.draw.rect(screen, (30, 30, 30), (x, y, CELL_SIZE, CELL_SIZE))
                
                # วาดกำแพง
                if maze[r][c][0]: pygame.draw.line(screen, WHITE, (x, y), (x + CELL_SIZE, y), 1) # Top
                if maze[r][c][1]: pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 1) # Right
                if maze[r][c][2]: pygame.draw.line(screen, WHITE, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 1) # Bottom
                if maze[r][c][3]: pygame.draw.line(screen, WHITE, (x, y), (x, y + CELL_SIZE), 1) # Left

        # 2. วาดชีส
        cheese_x = cheese_c * CELL_SIZE + 2
        cheese_y = cheese_r * CELL_SIZE + UI_HEIGHT + 2
        pygame.draw.rect(screen, CHEESE_COLOR, (cheese_x, cheese_y, CELL_SIZE-4, CELL_SIZE-4))

        # 3. วาดหนู
        rat_x = rat_c * CELL_SIZE + 2
        rat_y = rat_r * CELL_SIZE + UI_HEIGHT + 2
        pygame.draw.rect(screen, MOUSE_COLOR, (rat_x, rat_y, CELL_SIZE-4, CELL_SIZE-4))

        # 4. วาด UI (ส่วนบน)
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, UI_HEIGHT))
        
        # คำนวณระยะกระจัด (เส้นตรงไม่สนกำแพง) เป็น cm (1 ช่อง = 16 cm)
        dist = math.hypot((cheese_c - rat_c), (cheese_r - rat_r)) * 16

        # ข้อความ UI
        ui_texts = [
            f"Distance to Cheese: {dist:.2f} cm",
            f"Time Left (This move): {int(time_left)} sec",
            f"Thinking Count: {thinking_count} / 5",
            f"Status: {msg}"
        ]
        
        for i, text in enumerate(ui_texts):
            color = WHITE
            if i == 1 and time_left < 30: color = RED # เวลาใกล้หมดให้เป็นสีแดง
            if i == 2 and thinking_count >= 5: color = GREEN # คิดครบแล้วเป็นสีเขียว
            
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