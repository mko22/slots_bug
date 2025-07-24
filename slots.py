from copy import deepcopy
import random

# Define constants for symbols
SYMBOL_EMPTY = 0
SYMBOL_REGULAR = 1
SYMBOL_BONUS = 2

# Initial random source generation
def generate_initial_src(size=100000):
    random.seed()
    return [random.randint(0, 100) for _ in range(size)]

class BaseModel:
    @classmethod
    def blank(cls):
        return {}

    @classmethod
    def spins(cls):
        return {'round_win': 0}

    @classmethod
    def bonus(cls):
        return {'round_win': 0, 'raunds_left': 3}

class BaseGame:
    def __init__(self):
        self.ctx = {}
        self.cur = {}
        self.src_index = 0
        self.src = generate_initial_src()
        self.setup_states()
        self.current_state = 'init'

    def setup_states(self):
        self.states = {
            'init': self.handler_init,
            'spin': self.handler_spin,
            'bonus_init': self.handler_bonus_init,
            'bonus': self.handler_bonus,
        }

    def run(self, num_spins=1000):
        total_spins = 0
        total_bonus_games = 0
        total_win = 0
        self.handler_init()
        print(f"Game initialized with starting balance: {self.cur['balance']}")
        while total_spins < num_spins:
            self.current_state = 'spin'
            self.handler_spin()
            total_spins += 1
            total_win += self.cur.get('spin_win', 0)
            if self.cur.get('bonus_triggered'):
                total_bonus_games += 1
                self.handler_bonus_init()
                while self.cur['raunds_left'] != 0:
                    self.handler_bonus()
                    total_win += self.cur.get('bonus_total_win', 0)
        print(f"Simulation completed after {total_spins} spins.")
        print(f"Total bonus games triggered: {total_bonus_games}")
        print(f"Final balance: {self.cur['balance']}")
        print(f"Total win accumulated: {total_win}")
        rtp = (total_win / (self.cur['bet'] * total_spins))
        print(f"RTP (Return to Player): {rtp:.2f}%")
        with open("results.txt", "a") as f:
            f.write(f"{rtp}\n")

    def get_next_random(self):
        value = self.src[self.src_index % len(self.src)]
        self.src_index += 1
        return value

class GameModel(BaseModel):
    pass

class Game(BaseGame):
    def __init__(self):
        super().__init__()
        self.model_cls = GameModel

    def handler_init(self):
        self.ctx = self.model_cls.blank()
        self.ctx['spins'] = self.model_cls.spins()
        self.ctx['bonus'] = self.model_cls.bonus()
        self.cur['bet'] = 1
        self.cur['balance'] = 100  # Starting balance
        self.cur['bonus_triggered'] = False
        self.cur['spin_win'] = 0
        self.cur['bonus_total_win'] = 0

    def handler_spin(self):
        self.cur['spin_win'] = 0
        self.cur['board'] = [SYMBOL_REGULAR for _ in range(5)]
        bonus_chance = self.get_next_random()
        if bonus_chance < 20:  # 20% chance to trigger bonus
            self.cur['board'][2] = SYMBOL_BONUS
            self.cur['bonus_triggered'] = True
        else:
            win = self.get_next_random() % 5
            self.cur['balance'] += win
            self.cur['spin_win'] = win
            self.cur['bonus_triggered'] = False

    def handler_bonus_init(self):
        self.ctx['bonus'] = self.model_cls.bonus()
        self.cur['raunds_left'] = self.ctx['bonus']['raunds_left']
        self.cur['bonus_simbols'] = []
        self.cur['bonus_total_win'] = 0


    def handler_bonus(self):
        new_symbol_chance = self.get_next_random()
        if new_symbol_chance < 50:  # 50% chance to get a new bonus symbol
            new_value = self.get_next_random() % 10 + 70
            self.cur['bonus_simbols'].append(new_value)
            self.cur['raunds_left'] = self.ctx['bonus']['raunds_left']
        else:
            self.cur['raunds_left'] -= 1

        if self.cur['raunds_left'] == 0:
            total_bonus_win = sum(self.cur['bonus_simbols'])
            self.cur['balance'] += total_bonus_win
            self.cur['bonus_total_win'] = total_bonus_win

# Run the game simulation
if __name__ == "__main__":
    game = Game()

    game.run(num_spins=1)
