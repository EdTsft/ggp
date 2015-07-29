import logging
import random

from pygdl.sexpr import to_s_expression_string

logger = logging.getLogger(__name__)


class PrologGamePlayer(object):
    MIN_SCORE = 0
    MAX_SCORE = 100
    def __init__(self, game_state, role, _start_clock, play_clock):
        self.logger = logging.getLogger(__name__ + self.__class__.__name__)
        self.logger.info('Created {!s} with role "{!s}"'.format(
            self.__class__.__name__, role))
        self.game_state = game_state
        self.role = role
        self.play_clock = play_clock


    def update_moves(self, new_moves):
        roles = list(self.game_state.get_roles())
        roles = list(self.game_state.get_roles())
        assert(len(roles) == len(new_moves))

        self.logger.debug("GAME DESCRIPTION FOR TURN %s",
                          self.game_state.get_turn())
        for base in self.game_state.get_state_terms():
            self.logger.debug("\t%s", str(base))

        for role, move in zip(roles, new_moves):
            self.game_state.set_move(role, to_s_expression_string(move))
        self.game_state.next_turn()

    def stop(self):
        self.logger.info('Stopping game. Terminal: {!s}. Score: {!s}'.format(
            self.game_state.is_terminal(),
            self.game_state.get_utility(self.role)))

    def abort(self):
        self.logger.info('Aborting game.')


class Legal(PrologGamePlayer):
    player_name = 'Legal'

    def get_move(self):
        moves = self.game_state.get_legal_moves(self.role)
        first_move = next(moves)
        moves.close()
        return str(first_move)


class Random(PrologGamePlayer):
    player_name = 'Random'

    def get_move(self):
        random_move = None
        for i, move in enumerate(self.game_state.get_legal_moves(self.role)):
            if random.randint(0, i) == 0:
                random_move = move

        return str(random_move)

class CompulsiveDeliberation(PrologGamePlayer):
    player_name = 'CompulsiveDeliberation'

    def __init__(self, game_state, role, _start_clock, play_clock):
        super().__init__(game_state, role, _start_clock, play_clock)
        assert self.game_state.get_num_roles() == 1, \
            "CompulsiveDeliberation player only works for single-player games."

    def get_best_score_and_move(self):
        if self.game_state.is_terminal():
            return self.game_state.get_utility(self.role), None

        moves = list(self.game_state.get_legal_moves(self.role))

        best_score = self.MIN_SCORE - 1
        best_move = None
        for move in moves:
            self.game_state.set_move(self.role, move)
            self.game_state.next_turn()
            score, _ = self.get_best_score_and_move()
            self.game_state.previous_turn()

            assert score >= self.MIN_SCORE
            assert score <= self.MAX_SCORE

            if score > best_score:
                best_score = score
                best_move = move

            if best_score == self.MAX_SCORE:
                break

        return best_score, best_move

    def get_move(self):
        _, move = self.get_best_score_and_move()
        return str(move)

