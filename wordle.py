import pygame
import random

# Game settings
WIDTH = 350
HEIGHT = 600
WORD_LENGTH = 5
GRID_SIZE = 50
NUM_GUESSES = 6
INPUT_BOX_HEIGHT = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
YELLOW = (200, 200, 0)
GREEN = (0, 128, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Wordle")
font = pygame.font.Font(None, 36)

# Load word list
def load_word():
    with open("words.txt", "r") as f:
        words = f.readlines()
        return random.choice(words).strip().upper()

# Check a guess with no double yellow logic
def check_guess(guess, answer):
    letter_counts = {char: answer.count(char) for char in set(answer)}  
    result = [""] * WORD_LENGTH  

    # First Pass: Identify Green Letters 
    for i in range(WORD_LENGTH):
        if guess[i] == answer[i] and letter_counts[guess[i]] > 0: 
            result[i] = "GREEN"
            letter_counts[guess[i]] -= 1

    # Second Pass: Identify Yellow Letters
    for i in range(WORD_LENGTH):
        if guess[i] in answer and result[i] != "GREEN" and letter_counts[guess[i]] > 0:  
            result[i] = "YELLOW"
            letter_counts[guess[i]] -= 1 

    # Third Pass: Mark the rest as grey
    for i in range(WORD_LENGTH):
        if not result[i]: 
            result[i] = "GREY" 

    return result

# Draw the Wordle grid
def draw_grid(screen):
    block_size = GRID_SIZE + 5
    for row in range(NUM_GUESSES):
        for col in range(WORD_LENGTH):
            pygame.draw.rect(screen, WHITE,
                             [col * block_size + (WIDTH - block_size * WORD_LENGTH) // 2,
                              row * block_size + 10, GRID_SIZE, GRID_SIZE], 2)

# Draw text on the screen
def draw_text(screen, text, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


# Main game loop
def main():
    answer = load_word()
    guess = ""
    guesses = []
    game_over = False
    num_guesses_remaining = NUM_GUESSES
    current_letter_index = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_BACKSPACE:
                    guess = guess[:-1]
                    current_letter_index = max(0, current_letter_index - 1) 
                elif event.unicode.isalpha():
                    if current_letter_index < WORD_LENGTH: 
                        guess += event.unicode.lower()
                        current_letter_index += 1

        if guess and current_letter_index == WORD_LENGTH: 
            result = check_guess(guess.upper(), answer)
            guesses.append((guess, result))
            guess = ""
            current_letter_index = 0 
            num_guesses_remaining -= 1
            if result == ["GREEN"] * WORD_LENGTH:
                game_over = True
            elif num_guesses_remaining == 0:
                game_over = True

        screen.fill(WHITE)
        draw_grid(screen)

        # Draw previous guesses
        for i, (word, colors) in enumerate(guesses):
            for j, (letter, color) in enumerate(zip(word, colors)):
                block_size = GRID_SIZE + 5
                center_x = j * block_size + block_size // 2 + (WIDTH - block_size * WORD_LENGTH) // 2
                center_y = i * block_size + block_size // 2 + 10
                pygame.draw.rect(screen, color,
                                 [center_x - GRID_SIZE // 2, center_y - GRID_SIZE // 2, GRID_SIZE, GRID_SIZE])
                draw_text(screen, letter.upper(), BLACK, center_x, center_y)

        # Input box and current guess display
        input_rect = pygame.Rect((WIDTH - INPUT_BOX_HEIGHT * WORD_LENGTH) // 2,
                                 HEIGHT - INPUT_BOX_HEIGHT - 10,
                                 INPUT_BOX_HEIGHT * WORD_LENGTH, INPUT_BOX_HEIGHT)
        pygame.draw.rect(screen, BLACK, input_rect, 2)

        for i in range(WORD_LENGTH):  
            if i < current_letter_index:  
                draw_text(screen, guess[i].upper(), BLACK, 
                          input_rect.left + i * INPUT_BOX_HEIGHT + INPUT_BOX_HEIGHT // 2, 
                          input_rect.centery)
            else:  
                draw_text(screen, "_", BLACK,  
                          input_rect.left + i * INPUT_BOX_HEIGHT + INPUT_BOX_HEIGHT // 2, 
                          input_rect.centery) 

        # Game Over message 
        if game_over:
            # Darken Background
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)  # Adjust for desired darkness
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

             # Message box
            font = pygame.font.Font(None, 48)  # Adjust font size if needed
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

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
