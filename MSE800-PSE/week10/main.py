import random
import itertools

def get_o_or_x():
    while True:
        choice = input("Do you want to be x or o? ").lower()
        if choice in ["x", "o"]:
            return choice
        else:
            print("Invalid choice. Please choose x or o.")

def print_board(board):
    print("\n")
    num = 1
    for i in range(3):
        row = []
        for j in range(3):
            if board[i][j] == " ":
                row.append(str(num))
                num += 1
            else:
                row.append(board[i][j])
        print(" | ".join(row))
        if i < 2:
            print("---------")
    print("\n")



def play_game(board, human_player):
    current_player = human_player
    while not game_over(board):
        print_board(board)
        if play_one_turn(board, current_player, human_player):
            break  
        current_player = other_player(current_player)

def play_one_turn(board, current_player, human_player):
    if current_player == human_player:
        make_human_move(board, current_player)
    else:
        make_computer_move(board, current_player)

    if winner := check_win(board):
        print_board(board)
        print(f"Player {winner} wins!")
        return True  # Game over (win)

    if check_draw(board):
        print_board(board)
        print("It's a draw!")
        return True  # Game over (draw)

    return False

# Function for human player's move
def make_human_move(board, current_player):
    while True:
        try:
            move = int(input(f"Player {current_player}, enter your move (1-9): ")) - 1
            row, col = divmod(move, 3)
            
            if 0 <= move <= 8 and board[row][col] == " ":
                board[row][col] = current_player
                break  
            else:
                print("This spot is already taken or invalid. Try again.")
        except (ValueError, IndexError):
            print("Invalid move. Please choose a number between 1 and 9.")


def empty_squares(board):
     return [
        (i, j)
        for i, j in itertools.product(range(3), range(3))
        if board[i][j] == " "
    ]

def make_computer_move(board, current_player):
    if candidates := empty_squares(board):
    
        choice = random.choice(candidates)
        row, col = choice
        board[row][col] = current_player  
    else:
        print("No available moves left!")

def game_over(board):
    return check_win(board) is not None or check_draw(board)

# Function to check for a win
def check_win(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0] 
        # Check columns
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]  
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0] 
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]  

    return None

def check_draw(board):
    for row in board:
        for cell in row:
            if cell == " ":
                return False
    return True

def other_player(current_player):
    return "o" if current_player == "x" else "x"

def main():
    board = [[" " for _ in range(3)] for _ in range(3)]
    human_player = get_o_or_x()  
    print(f"Player 1, you are {human_player}!")
    play_game(board, human_player)

if __name__ == "__main__":
    main()
