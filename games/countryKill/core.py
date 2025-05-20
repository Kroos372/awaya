from .cards import PlayerCards, Card
from ._static import TurnStatus, TurnPhases
from static import Awaish
from typing import Iterable, Generator

class Player:
    def __init__(self, name: str, gender: str, max_life: int, hands: list, power: str, role: str=None):
        # 昵称
        self.name = name # 昵称
        self.gender = gender # 性别（怪）
        self.power = power # 势力
        self.max_life = self.life = max_life # 生命值与最大生命值
        self.role = role # 身份

        self.hands = PlayerCards(hands) # 手牌
        # 装备
        self.equipments = []

        self.delays = [] # 延时锦囊牌
        
        self.chained = False
    def __str__(self):
        return self.name
    def __eq__(self, value):
        return self.name == value
    def __hash__(self):
        return self.name


class ResponseSystem:
    def __init__(self, turn: "Turn"):
        self.turn = turn
        self.pending_responses: list[Generator] = []
        
    def request(self, requester: Player, card: Card, *args) -> Generator[None, str, None]:
        cmd = yield
        while not card.on_respond(self.turn, ):
            cmd = yield
    
    def create_request(self, requester: Player, card: Card, *args):
        new_request = self.request(requester, card, *args)
        next(new_request)
        self.pending_responses.insert(0, new_request)

    def respond(self, responder: Player, *args):
        pass

class Turn:
    def __init__(self, game: "Game", player: Player):
        self.game = game
        self.player = player

        self.status = TurnStatus.PLAYING
        self.phase = TurnPhases.PLAYING
        self.response_system = ResponseSystem(game)
    
    def play(self, player: Player, msg: str):
        pass


class Game:
    def __init__(self):
        self.context: Awaish
        self.turn: Turn
        
        self.status = 0
        self.players: list[Player] = []
        self.player_index = 0
    @property
    def current_player(self):
        return self.players[self.player_index]
    @property
    def next_player(self):
        next_index = (self.player_index + 1) % len(self.players)
        return self.players[next_index]
    
    def distance_between(self, atk_target: Player, dfs_target: Player) -> int:
        index1 = self.players.index(atk_target)
        index2 = self.players.index(dfs_target)
        distance1 =  abs(index2 - index1)
        distance2 = len(self.players) - distance1

        distance = min(distance1, distance2) - atk_target.atk_distance + dfs_target.dfs_distance
        return distance

    def _get_player(self, sender: str) -> Player:
        return self.players[self.players.index(sender)]

    def _next_player(self):
        self.player_index = (self.player_index + 1) % len(self.players)
    
    def _next_turn(self):
        pass
    
    def play(self, sender: str, msg: str):
        player = self._get_player(sender)
        if msg == "check":
            return
        elif msg == "all":
            return
        
        self.turn.play(player, msg)

game = Game()