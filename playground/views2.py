# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

ROWS = 6
COLS = 7
PLAYER = 1
AI = 2
EMPTY = 0

def evaluate_window(window, player): 
    opponent = AI if player == PLAYER else PLAYER
    score = 0

    if window.count(player) == 4:
        score += 0
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        score += 0
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        score += 0

    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 0

    return score

def score_position(board, player):
    score = 0

    # Score center column
    center_array = [board[r][COLS//2] for r in range(ROWS)]
    center_count = center_array.count(player)
    score += center_count * 1.2

    # Score Horizontal
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, player)

    # Score Vertical
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, player)

    # Score positive sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    # Score negative sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    return score

def is_terminal_node(board):
    return check_winner(board, PLAYER) or check_winner(board, AI) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if check_winner(board, AI):
                return (None, 1)
            elif check_winner(board, PLAYER):
                return (None, -1)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI))
    
    if maximizing_player:
        value = float('-inf')
        column = valid_locations[0]
        for col in valid_locations:
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, col, AI)
            new_score = minimax(temp_board, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player
        value = float('inf')
        column = valid_locations[0]
        for col in valid_locations:
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, col, PLAYER)
            new_score = minimax(temp_board, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_locations(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY]
def drop_piece(board, col, piece):
    if col < 0 or col >= COLS or board[0][col] != EMPTY:
        raise ValueError("Column is full or invalid")
    
    for r in range(ROWS - 1, -1, -1):  # Izmenjeno: iteriramo od dna ka vrhu
        if board[r][col] == EMPTY:
            board[r][col] = piece
            return
# def drop_piece(board, col, piece):
#     for r in range(ROWS):  # Izmenjeno: iteriramo od vrha ka dnu
#         if board[r][col] == EMPTY:
#             board[r][col] = piece
#             return

def check_winner(board, player):
    # Horizontal check
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] == player and board[r][c+1] == player and board[r][c+2] == player and board[r][c+3] == player:
                return True

    # Vertical check
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] == player and board[r+1][c] == player and board[r+2][c] == player and board[r+3][c] == player:
                return True

    # Diagonal checks
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] == player and board[r+1][c+1] == player and board[r+2][c+2] == player and board[r+3][c+3] == player:
                return True
            if board[r+3][c] == player and board[r+2][c+1] == player and board[r+1][c+2] == player and board[r][c+3] == player:
                return True

    return False

@require_http_methods(["GET"])
def get_best_move(request):
    board_str = request.GET.get('board', '[]')
    
    try:
        board = json.loads(board_str)
        if not isinstance(board, list) or not all(isinstance(row, list) for row in board):
            raise ValueError("Invalid board format")
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format for board'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    print(f"Current board state: {board}")  # Ova linija će vam pomoći da proverite stanje board-a

    best_col, _ = minimax(board, 1, float('-inf'), float('inf'), True)
    return JsonResponse({'best_move': best_col})