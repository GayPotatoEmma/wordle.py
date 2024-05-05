import pygame
import random
import time
import requests

# Game settings
WIDTH = 450
HEIGHT = 650
WORD_LENGTH = 5
GRID_SIZE = 50
NUM_GUESSES = 6
INPUT_BOX_HEIGHT = 40
REVEAL_SPEED = 0.2

# Colors
PRIMARY_COLOR = (102, 187, 106)
PRIMARY_DARK = (210, 210, 210)
BACKGROUND = (245, 245, 245)
GREY = (224, 224, 224)
GREEN = (156, 204, 101)
YELLOW = (255, 241, 118)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Keyboard settings
KEYBOARD_LAYOUT = [
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM"
]
KEY_WIDTH = 40
KEY_HEIGHT = 50
KEY_SPACING = 7

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Wordle")

# Load fonts
try:
    font_path = "Roboto-Regular.ttf"
    font = pygame.font.Font(font_path, 36)
except FileNotFoundError:
    font = pygame.font.SysFont("Segoe UI", 36)

# Pre-render colored backgrounds
bg_images = {
    "GREY": pygame.Surface((GRID_SIZE, GRID_SIZE)).convert(),
    "YELLOW": pygame.Surface((GRID_SIZE, GRID_SIZE)).convert(),
    "GREEN": pygame.Surface((GRID_SIZE, GRID_SIZE)).convert()
}
bg_images["GREY"].fill(GREY)
bg_images["YELLOW"].fill(YELLOW)
bg_images["GREEN"].fill(GREEN)

# Functions

# Load word list from URL
def load_word():
    word_url = "https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/45c977427419a1e0edee8fd395af1e0a4966273b/wordle-answers-alphabetical.txt"
    try:
        response = requests.get(word_url)
        response.raise_for_status()
        words = response.text.splitlines()
        return random.choice(words).strip().upper()
    except requests.exceptions.RequestException as e:
        print("Error fetching word list:", e)
        return None  # Handle the error (e.g., use a default word list)


# Check a guess
def check_guess(guess, answer):
    letter_counts = {char: answer.count(char) for char in set(answer)}
    result = [""] * WORD_LENGTH

    # Green Letters
    for i in range(WORD_LENGTH):
        if guess[i] == answer[i] and letter_counts[guess[i]] > 0:
            result[i] = "GREEN"
            letter_counts[guess[i]] -= 1

    # Yellow Letters
    for i in range(WORD_LENGTH):
        if guess[i] in answer and result[i] != "GREEN" and letter_counts[guess[i]] > 0:
            result[i] = "YELLOW"
            letter_counts[guess[i]] -= 1

    # Grey Letters
    for i in range(WORD_LENGTH):
        if not result[i]:
            result[i] = "GREY"

    return result


# Draw the Wordle grid
def draw_grid(screen):
    block_size = GRID_SIZE + 5
    for row in range(NUM_GUESSES):
        for col in range(WORD_LENGTH):
            pygame.draw.rect(screen, GREY,
                             [col * block_size + (WIDTH - block_size * WORD_LENGTH) // 2,
                              row * block_size + 10, GRID_SIZE, GRID_SIZE], 2, border_radius=0)


# Draw text on the screen
def draw_text(screen, text, color, x, y, font_size=36):
    font_obj = pygame.font.Font(font_path, font_size)
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


# Draw a key with rounded corners and a subtle shadow
def draw_key(screen, x, y, letter, color):
    pygame.draw.rect(screen, PRIMARY_DARK, (x + 2, y + 2, KEY_WIDTH, KEY_HEIGHT), border_radius=8)
    pygame.draw.rect(screen, color, (x, y, KEY_WIDTH, KEY_HEIGHT), border_radius=8)
    draw_text(screen, letter, WHITE, x + KEY_WIDTH // 2, y + KEY_HEIGHT // 2, font_size=20)


# Draw the on-screen keyboard
def draw_keyboard(screen, guesses):
    y = HEIGHT - 3 * (KEY_HEIGHT + KEY_SPACING)
    for row in KEYBOARD_LAYOUT:
        x = (WIDTH - len(row) * (KEY_WIDTH + KEY_SPACING)) // 2
        for letter in row:
            color = GREY
            for guess, result in guesses:
                for i, (l, r) in enumerate(zip(guess, result)):
                    if letter == l:
                        color = r
                        break
            draw_key(screen, x, y, letter, color)
            x += KEY_WIDTH + KEY_SPACING
        y += KEY_HEIGHT + KEY_SPACING


# Helper function to get the clicked key
def get_clicked_key(pos):
    y = HEIGHT - 3 * (KEY_HEIGHT + KEY_SPACING)
    for row in KEYBOARD_LAYOUT:
        x = (WIDTH - len(row) * (KEY_WIDTH + KEY_SPACING)) // 2
        for letter in row:
            rect = pygame.Rect(x, y, KEY_WIDTH, KEY_HEIGHT)
            if rect.collidepoint(pos):
                return letter
            x += KEY_WIDTH + KEY_SPACING
        y += KEY_HEIGHT + KEY_SPACING
    return None


# Reveal a guess with input blocking
def reveal_guess(screen, guess, result, row):
    block_size = GRID_SIZE + 5
    x_start = (WIDTH - block_size * WORD_LENGTH) // 2
    y_start = row * block_size + 10

    input_blocked = True
    for i, (letter, color) in enumerate(zip(guess, result)):
        x = x_start + i * block_size
        y = y_start

        screen.blit(bg_images[color], (x, y))
        draw_text(screen, letter.upper(), WHITE, x + GRID_SIZE // 2, y + GRID_SIZE // 2)

        for event in pygame.event.get():  
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()
        time.sleep(REVEAL_SPEED)
    input_blocked = False


# Main game loop
def main():
    answer = load_word()
    guess = ""
    guesses = []
    game_over = False
    num_guesses_remaining = NUM_GUESSES
    current_letter_index = 0
    input_blocked = False 

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not input_blocked:
                pos = pygame.mouse.get_pos()
                clicked_key = get_clicked_key(pos)
                if clicked_key:
                    if clicked_key == "BACKSPACE":
                        guess = guess[:-1]
                        current_letter_index = max(0, current_letter_index - 1)
                    elif len(guess) < WORD_LENGTH and clicked_key.isalpha():
                        guess += clicked_key.lower()
                        current_letter_index += 1
            if event.type == pygame.KEYDOWN and not game_over and not input_blocked:
                if event.key == pygame.K_BACKSPACE:
                    guess = guess[:-1]
                    current_letter_index = max(0, current_letter_index - 1)
                elif event.unicode.isalpha():
                    if current_letter_index < WORD_LENGTH:
                        guess += event.unicode.lower()
                        current_letter_index += 1

        if guess and current_letter_index == WORD_LENGTH and not input_blocked:
            result = check_guess(guess.upper(), answer)
            guesses.append((guess, result))
            reveal_guess(screen, guess, result, len(guesses) - 1)
            guess = ""
            current_letter_index = 0
            num_guesses_remaining -= 1
            if result == ["GREEN"] * WORD_LENGTH:
                game_over = True
            elif num_guesses_remaining == 0:
                game_over = True

        screen.fill(BACKGROUND)

        # Draw previous guesses (backgrounds and letters)
        for i, (word, colors) in enumerate(guesses):
            block_size = GRID_SIZE + 5
            x_start = (WIDTH - block_size * WORD_LENGTH) // 2
            y_start = i * block_size + 10
            for j, (letter, color) in enumerate(zip(word, colors)):
                x = x_start + j * block_size
                y = y_start
                screen.blit(bg_images[color], (x, y))
                draw_text(screen, letter.upper(), WHITE, x + GRID_SIZE // 2, y + GRID_SIZE // 2)

        # Draw grid on top of colored backgrounds
        draw_grid(screen)

        # Input box
        y = HEIGHT - 3 * (KEY_HEIGHT + KEY_SPACING)
        input_rect = pygame.Rect((WIDTH - INPUT_BOX_HEIGHT * WORD_LENGTH) // 2,
                                 y - INPUT_BOX_HEIGHT - 20,
                                 INPUT_BOX_HEIGHT * WORD_LENGTH, INPUT_BOX_HEIGHT)
        pygame.draw.rect(screen, PRIMARY_DARK, (input_rect.x + 2, input_rect.y + 2, input_rect.width, input_rect.height), border_radius=8)
        pygame.draw.rect(screen, GREY, (input_rect.x, input_rect.y, input_rect.width, input_rect.height), border_radius=8)

        for i in range(WORD_LENGTH):
            if i < current_letter_index:  # Use < instead of <= here
                draw_text(screen, guess[i].upper(), BLACK,
                          input_rect.left + i * INPUT_BOX_HEIGHT + INPUT_BOX_HEIGHT // 2,
                          input_rect.centery)
            else:
                draw_text(screen, "_", PRIMARY_DARK,
                          input_rect.left + i * INPUT_BOX_HEIGHT + INPUT_BOX_HEIGHT // 2,
                          input_rect.centery)

        # Game Over message
        if game_over:
            # Darken Background
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            # Message box
            font = pygame.font.Font(font_path, 48)
            text = "Game Over!" if num_guesses_remaining == 0 else "You Win!"
            text_surface = font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            pygame.draw.rect(screen, BLACK, text_rect, 2)
            screen.blit(text_surface, text_rect)

            # Word reveal
            reveal_text = f"The word was: {answer}"
            reveal_surface = font.render(reveal_text, True, WHITE)
            reveal_rect = reveal_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(reveal_surface, reveal_rect)

        draw_keyboard(screen, guesses)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()