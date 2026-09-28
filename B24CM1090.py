
import time
from config import *


class B24CM1090:

    def __init__(self, engine):
        self.engine = engine
        self.nodes_expanded = 0
        self.depth = 3

        self.total_time_budget = 55.0
        self.time_spent = 0.0
        self.moves_played = 0
        self.max_search_depth = 8
        self.previous_best_move = None

    def get_best_move(self):
        call_start = time.perf_counter()
        best_move = None
        
        try:
            self.nodes_expanded = 0
            legal_moves = self.engine.get_legal_moves()

            if not legal_moves:
                return None

            self.moves_played += 1

            remaining_total = max(
                0.0, self.total_time_budget - self.time_spent
            )

            moves_left_estimate = max(
                1, min(75 - self.moves_played + 1, 30)
            )

            per_move_budget = remaining_total / moves_left_estimate
            per_move_budget *= self._game_phase_factor()
            per_move_budget = min(per_move_budget, 3.0)

            deadline = time.perf_counter() + per_move_budget

            maximizing = self.engine.white_to_move
            best_move = legal_moves[0]

            depth = 1

            while depth <= self.max_search_depth:
                ordered_moves = self._order_moves(legal_moves)

                if self.previous_best_move in ordered_moves:
                    ordered_moves.remove(self.previous_best_move)
                    ordered_moves.insert(0, self.previous_best_move)

                current_best_move = None
                current_best_score = (
                    float("-inf") if maximizing else float("inf")
                )

                root_alpha = float("-inf")
                root_beta = float("inf")

                for move in ordered_moves:
                    if time.perf_counter() >= deadline:
                        raise TimeoutError

                    self.engine.make_move(move)
                    try:
                        score = self._alphabeta(
                            depth - 1,
                            root_alpha,
                            root_beta,
                            not maximizing,
                            deadline
                        )
                    finally:
                        self.engine.undo_move()

                    if maximizing and score > current_best_score:
                        current_best_score = score
                        current_best_move = move
                        root_alpha = max(root_alpha, current_best_score)

                    elif not maximizing and score < current_best_score:
                        current_best_score = score
                        current_best_move = move
                        root_beta = min(root_beta, current_best_score)

                if current_best_move is not None:
                    best_move = current_best_move
                    self.previous_best_move = current_best_move

                depth += 1

            return best_move

        except TimeoutError:
            return best_move

        finally:
            self.time_spent += time.perf_counter() - call_start

    def evaluate_board(self, game_state="ongoing"):

        if game_state == "checkmate":
            return -100000 if self.engine.white_to_move else 100000

        if game_state == "stalemate":
            return 0

        score = 0
        board = self.engine.board

        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                piece = board[r][c]

                if piece == EMPTY_SQUARE:
                    continue

                score += PIECE_VALUES.get(piece, 0)

                pst = self._get_pst(piece)
                if pst is not None:
                    bonus = pst[r][c]
                    score += bonus if piece.startswith("w") else -bonus

        if self.engine.is_in_check():
            score += -5 if self.engine.white_to_move else 5

        mobility = len(self.engine._get_all_possible_moves())
        score += (
            mobility * 1.0
            if self.engine.white_to_move
            else -mobility * 1.0
        )

        return score

    def _alphabeta(self, depth, alpha, beta, maximizing, deadline):
        self.nodes_expanded += 1

        if time.perf_counter() >= deadline:
            raise TimeoutError

        legal_moves = self.engine.get_legal_moves()

        if not legal_moves:
            if self.engine.is_in_check():

                return -100000 - depth if maximizing else 100000 + depth

            return 0

        if depth == 0:
            return self.evaluate_board("ongoing")

        legal_moves = self._order_moves(legal_moves)

        if maximizing:
            value = float("-inf")

            for move in legal_moves:
                self.engine.make_move(move)
                try:
                    value = max(
                        value,
                        self._alphabeta(
                            depth - 1, alpha, beta, False, deadline
                        )
                    )
                finally:
                    self.engine.undo_move()

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return value

        else:
            value = float("inf")

            for move in legal_moves:
                self.engine.make_move(move)
                try:
                    value = min(
                        value,
                        self._alphabeta(
                            depth - 1, alpha, beta, True, deadline
                        )
                    )
                finally:
                    self.engine.undo_move()

                beta = min(beta, value)

                if alpha >= beta:
                    break

            return value

    def _order_moves(self, moves):

        def mvv_lva_score(move):
            if move.piece_captured == EMPTY_SQUARE:
                return 0

            victim_value = abs(
                PIECE_VALUES.get(move.piece_captured, 0)
            )
            attacker_value = abs(
                PIECE_VALUES.get(move.piece_moved, 0)
            ) or 1

            return victim_value * 100 - attacker_value

        return sorted(
            moves,
            key=mvv_lva_score,
            reverse=True
        )

    def _game_phase_factor(self):
        board = self.engine.board
        total_material = 0

        for row in board:
            for piece in row:
                if piece != EMPTY_SQUARE and piece[1] != "K":
                    total_material += abs(
                        PIECE_VALUES.get(piece, 0)
                    )

        starting_material = 980
        ratio = (
            total_material / starting_material
            if starting_material
            else 1.0
        )

        return max(0.5, min(1.2, 0.5 + ratio * 0.7))

    def _get_pst(self, piece):
        ptype = piece[1]

        if ptype == "P":
            return PAWN_PST
        if ptype == "N":
            return KNIGHT_PST
        if ptype == "B":
            return BISHOP_PST
        if ptype == "R":
            return ROOK_PST
        if ptype == "K":
            return KING_PST_LATE_GAME

        return None