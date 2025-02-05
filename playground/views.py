# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

# broj redova i kolona
ROWS = 6
COLS = 7
#igrac
PLAYER = 1
#VI
AI = 2
#oznacava prazno polje
EMPTY = 0

#procenjuje "prozor" na igračkoj tabli (deo niza ili reda), kako bi dala ocenu na osnovu broja igrača i praznih mesta u tom prozoru.
def evaluate_window(window, player):
    opponent = AI if player == PLAYER else PLAYER
    score = 0
#Ako je trenutni igrač PLAYER, protivnik je AI, i obrnuto.
    if window.count(player) == 4:
        score += 10
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        score += 1
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        score += 2
# Ako ima 3 polja protivnika i 1 prazno, oduzima se poen (-1), jer to znači da protivnik ima dobar potez.
    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 1
#fja daje visoku ocenu za prozore koji su blizu potpune linije igrača, a negativnu ocenu za prozore u kojima protivnik ima prednost.
    return score

def score_position(board, player): #ocenjuje trenutnu poziciju na tabli igre za datog igraca
                                   #Svaka vrednost može biti 0 (prazno), 1 (igrač) ili 2 (AI).
    score = 0

    # Score center column -srednja kolona
    center_array = [board[r][COLS//2] for r in range(ROWS)]
    center_count = center_array.count(player)
    score += center_count * 3

    # Ocena horizontalnih linija
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, player)

    # Ocena vertikalnih linija
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, player)

    # Ocena dijagonala sa pozitivnim nagibom sa leva na desno 
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    # Ocena dijagonala sa negativnim nagibom - odozgo na dole 
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, player)
    # vraća ukupnu ocenu pozicije na tabli. Što je veća ocena, to je pozicija bolja za datog igrača
    return score

def is_terminal_node(board): # proverava da li je trenutni položaj na tabli krajnji u igri, tj. da li je igra završena
    # Poziva fja check_winner za oba igrača (PLAYER i AI). Ako je bilo koji igrač pobedio, igra je završena
    return check_winner(board, PLAYER) or check_winner(board, AI) or len(get_valid_locations(board)) == 0

# algoritam pokušava da nađe najbolji mogući potez za AI igrača na osnovu dubine pretrage i ocena pozicija
def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    if depth == 0 or is_terminal: #Ako je depth == 0 ili ako je igra završena, algoritam će prekinuti pretragu
        if is_terminal:
            if check_winner(board, AI):
                return (None, 100000000000000)
            elif check_winner(board, PLAYER):
                return (None, -10000000000000)
            else:  # Igra je zavrsena, nema validnih poteza
                return (None, 0) #Ako nema pobednika, vraca 0
        else:  
            return (None, score_position(board, AI))
    
    #  logika za "maksimizirajućeg igrača", što je AI u ovom slučaju, koji pokušava da izabere najbolji potez
    if maximizing_player: 
        value = float('-inf')
        column = valid_locations[0]
        for col in valid_locations:
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, col, AI)
            # rekurzivno pozivanje minimax fje
            new_score = minimax(temp_board, depth-1, alpha, beta, False)[1]
            if new_score > value: # azuriranje najboljeg poteza
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value # vraca najbolji potez i odg score
    
    else:  # "minimizirajućeg igrača", što je igrač u ovoj implementaciji (ne AI)
        value = float('inf')
        column = valid_locations[0]
        for col in valid_locations: #iteracija kroz sve validne kolone
            temp_board = [row[:] for row in board] #simulacija poteza
            drop_piece(temp_board, col, PLAYER)
            new_score = minimax(temp_board, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value
    
   #vraća listu svih kolona na tabli koje su još uvek dostupne za postavljanje novog poteza
def get_valid_locations(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY] # vraća listu indeksa kolona koje su dostupne za igru

def drop_piece(board, col, piece): #simulira postavljanje pločice na igračkoj tabli u odgovarajuću kolonu
    if col < 0 or col >= COLS or board[0][col] != EMPTY:
        raise ValueError("Column is full or invalid")
    
    for r in range(ROWS - 1, -1, -1):  # Izmenjeno: iteriramo od dna ka vrhu
        if board[r][col] == EMPTY:
            board[r][col] = piece
            return #odmah zavrsava, jer je plocica postavljena
# def drop_piece(board, col, piece):
#     for r in range(ROWS):  # Izmenjeno: iteriramo od vrha ka dnu
#         if board[r][col] == EMPTY:
#             board[r][col] = piece
#             return

def check_winner(board, player): #da li je određeni igrač pobedio na tabli
    # Horizontal check
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] == player and board[r][c+1] == player and board[r][c+2] == player and board[r][c+3] == player:
                return True #Ako se nađe niz od 4 pločice u hor pravcu, fja odmah vraća True, što znači da je igrač pobedio

    # Vertical check
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] == player and board[r+1][c] == player and board[r+2][c] == player and board[r+3][c] == player:
                return True

    # Diagonal checks - proverava da li igrač ima četiri uzastopne pločice u dijagonalnom pravcu
    for r in range(ROWS - 3): 
        for c in range(COLS - 3):
            # pozitivni nagib
            if board[r][c] == player and board[r+1][c+1] == player and board[r+2][c+2] == player and board[r+3][c+3] == player:
                return True 
            # negativni nagib
            if board[r+3][c] == player and board[r+2][c+1] == player and board[r+1][c+2] == player and board[r][c+3] == player:
                return True

    return False #Ako nijedna od dijagonala ne sadrži četiri uzastopne pločice igrača, fja vraća False, što znači da igrač nije pobedio u dijag
  # Django view fja koja obrađuje HTTP GET zahtev kako bi korisniku vratila najbolji potez za AI u igri 
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
  # Izračunavanje najboljeg poteza pomoću Minimax algoritma:
    best_col, _ = minimax(board, 3, float('-inf'), float('inf'), True)
    return JsonResponse({'best_move': best_col}) #Vraća JSON odgovor sa najboljim potezom