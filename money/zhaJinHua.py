import random
from static import Awaish, namePure
from money import bank

class Card:
    SORT = ["2", "3", "4", "5", "6", "7", "8", "9", "H", "J", "Q", "K", "A"]
    SUITS = ["♦", "♣", "♥", "♠"]
    def __init__(self, suit: str, num: str):
        self.suit = suit
        self.num = num
    
        self.point = self.SORT.index(num)
        self.suit_point = self.SUITS.index(suit)
    def __str__(self):
        return self.suit + self.num
    def __lt__(self, other: "Card"):
        if self.point != other.point:
            return self.point < other.point
        else:
            return self.suit_point < other.suit_point

class Deck(list):
    def init_deck(self):
        self.clear()
        for suit in Card.SUITS:
            for num in Card.SORT:
                self.append(Card(suit, num))
        random.shuffle(self)

class Hand(list[Card]):
    GAOPAI = 1
    DUIZI = 2
    SHUNZI = 3
    JINHUA = 4
    SHUNJIN = 5
    BAOZI = 6

    def sort_type(self):
        self.sort(key=lambda card: Card.SORT.index(card.num))
        self.type = self._get_type()

    @property
    def is_235(self) -> bool:
        _235 = "235"
        suits = set()
        for i, card in enumerate(self):
            suits.add(card.suit)
            if card.num != _235[i]:
                return False
        if len(suits) != 3:
            return False
        return True
    @property
    def is_straight(self) -> bool:
        base_point = self[0].point
        return base_point == self[1].point - 1 and base_point == self[2].point - 2
    # 对子剩下的单张点数
    @property
    def single_point(self) -> int:
        if self[0].point == self[1].point:
            return self[2].point
        else:
            return self[0].point

    def _get_type(self) -> int:
        nums = set()
        suits = set()
        for card in self:
            suits.add(card.suit)
            nums.add(card.num)
        
        if len(nums) == 1:
            return self.BAOZI
        elif len(suits) == 1:
            if self.is_straight:
                return self.SHUNJIN
            else:
                return self.JINHUA
        elif self.is_straight:
            return self.SHUNZI
        elif len(nums) == 2:
            return self.DUIZI
        else:
            return self.GAOPAI
    
    def __lt__(self, other: "Hand"):
        if other.type == self.BAOZI and self.is_235:
            return False
        elif self.type == self.BAOZI and other.is_235:
            return True
        elif self.type != other.type:
            return self.type < other.type
        # 相同牌型
        elif self.type == self.GAOPAI or self.type == self.JINHUA:
            for i in range(2, -1, -1):
                if self[i].point != other[i].point:
                    return self[i].point < other[i].point
            return self[2].suit_point < other[2].suit_point
        elif self.type == self.DUIZI:
            if self[1].point != other[1].point:
                return self[1].point < other[1].point
            elif self.single_point != other.single_point:
                return self.single_point < other.single_point
            else:
                return self[1].suit_point < other[1].suit_point
        else:
            return self[2] < other[2]

class Player:
    def __init__(self, trip: str, name: str):
        self.trip = trip
        self.name = name

        self.hand = Hand()
        self.checked = False
    
    def draw(self, card: Card):
        self.hand.append(card)
        
    def sort(self):
        self.hand.sort_type()
        
    def format(self) -> str:
        text = "你的牌："
        if self.checked:
            text += " ".join(str(card) for card in self.hand)
        else:
            text += "?? ?? ??"
        return text
        
    def __str__(self):
        return self.name
    def __eq__(self, value):
        return self.trip == value
    def __lt__(self, other: "Player"):
        return self.hand < other.hand

class Game:
    LEAST_BET = 10
    MAX_BET = 500
    def __init__(self):
        self.context: Awaish
        
        self.status = 0
        self.deck = Deck()
        self.players: list[Player] = []
        self.player_index = 0
        
        self.least_bet = self.LEAST_BET
        self.max_bet = self.MAX_BET

        self.last_bet = 0
        self.all_bets = 0
    @property
    def current_player(self):
        return self.players[self.player_index]
    
    def _format_order(self) -> str:
        text = []
        for player in self.players:
            if player == self.current_player:
                text.append(f"=={player}==")
            else:
                text.append(player.name)
        return "顺序：" + " -> ".join(text)
    
    def set_least(self, num: int):
        if num < 0:
            self.context.appText("数额过小！")
        else:
            for player in self.players:
                if bank.hasMoney(player.trip, num) != num:
                    self.context.appText("数额过大！")
                    return
            self.least_bet = num
            self.context.appText(f"设置底注成功：{self.least_bet}")

    def set_max(self, num: int):
        if num < self.least_bet:
            self.context.appText("数额过小！")
        else:
            self.least_bet = num
            self.context.appText(f"设置封顶成功：{self.max_bet}")
    
    def start_game(self):
        self.status = 1
        self.player_index = 0
        random.shuffle(self.players)

        self.deck.init_deck()

        for player in self.players:
            for _ in range(3):
                player.draw(self.deck.pop())
            player.sort()
            self.context.appText(player.format(), "whisper", to=player.name)
            bank.delete(player.trip, self.least_bet)
            self.all_bets += self.least_bet
        
        self.last_bet = self.least_bet
        self.context.appText(
            f"已自动扣除每位玩家底注{self.least_bet}豆。\n" +
            f"最高下注{self.max_bet}豆，\n" +
            self._format_order() + "\n" +
            f"由@{self.current_player} 开始\n"
        )

    def end_game(self):
        self.status = 0
        self.players = []
        self.deck.clear()
        
        self.least_bet = self.LEAST_BET
        self.max_bet = self.MAX_BET
        self.last_bet = 0
        self.all_bets = 0
    
    def _get_player(self, nick: str) -> Player | None:
        for player in self.players:
            if player.name == nick:
                return player

    def _next_player(self):
        if not self._check_end():
            self.player_index = (self.player_index + 1) % len(self.players)
            self.context.appText(self._format_order())
            self.context.appText(f"轮到 @{self.current_player}")
    
    def bet(self, num: int):
        player = self.current_player
        money = bank.hasMoney(player.trip, num)
        if not player.checked:
            money *= 2
        if money < self.last_bet:
            self.context.appText(f"下注必须比{self.last_bet}大")
        elif money > self.max_bet:
            self.context.appText(f"下注必须比{self.max_bet}小")
        else:
            self.last_bet = money
            if not player.checked:
                money /= 2
                self.context.appText(f"{player}下注了{money}豆（暗注）！")
            else:
                self.context.appText(f"{player}下注了{money}豆！")
            bank.delete(player.trip, money)
            self.all_bets += money
            self.context.appText(f"奖池累计至{self.all_bets}豆！")
            self._next_player()
    
    def fold(self):
        player = self.current_player
        self.players.remove(player)
        self.context.appText(f"{player}失去手牌并离开了游戏")
        self._next_player()
    
    def check(self):
        player = self.current_player
        if not player.checked:
            player.checked = True
            self.context.appText(f"{player}查看了自己的手牌")
        self.context.appText(player.format(), "whisper", to=player.name)

    def compare(self, target: str):
        player = self.current_player
        target_player = self._get_player(target)
        if not target_player:
            self.context.appText("不存在这个玩家！")
            return
        elif target_player == player:
            self.context.appText("不能和自己比！")
            return

        money = bank.hasMoney(player.trip, self.last_bet*2)
        bank.delete(player.trip, money)
        self.all_bets += money
        self.context.appText(f"{player}支付了{money}阿瓦豆与{target_player}比牌！")
        
        if player < target_player:
            loser = player
        else:
            loser = target_player
        self.context.appText(f"{loser}输了！")
        self.players.remove(loser)
        self._next_player()
    
    def _check_end(self) -> bool:
        if len(self.players) == 1:
            winner = self.players[0]
            bank.add(winner.trip, self.all_bets)
            self.context.appText(f"@{winner} 获胜，赢得{self.all_bets}豆！！！🍾🍾🍾")
            self.end_game()
            return True
        return False

ZJHMENU = "\n".join([
    "炸金花，[规则点击此处](https://zhuanlan.zhihu.com/p/717171407)",
    "z 加入",
    "z 退出",
    "加入后：",
    "z 开始",
    f"z set <底注> <最高注>：设置底注与单注封顶，自行协商(默认{Game.LEAST_BET} {Game.MAX_BET})",
    "游戏中：",
    "z <豆数>：下注",
    "z check：看牌",
    "z .：弃牌",
    "z = <昵称>：比牌"
])

def main(context: Awaish, sender: str, msg: str):
    trip = context.user["trip"]
    if msg == "help":
        context.appText(ZJHMENU)
        return
    elif not bank.get(trip):
        context.appText("你还没有银行！")
        return
    elif bank.hasMoney(trip, game.least_bet) != game.least_bet:
        context.appText("你的钱不够底注！")
        return
    
    if msg == "加入" and trip not in game.players:
        game.players.append(Player(trip, sender))
        context.appText(f"加入成功，当前{len(game.players)}位玩家")
        game.context = context
    elif msg == "退出" and trip in game.players:
        game.players.remove(trip)
        context.appText("退出成功")
    
    elif trip in game.players:
        if not game.status:
            if msg.startswith("set"):
                msg_list = msg.split(" ")
                try:
                    game.set_least(msg_list[1])
                    game.set_max(msg_list[2])
                except:
                    context.appText("参数错误！")
            elif msg == "开始":
                game.start_game()
        elif trip == game.current_player:
            if msg == ".":
                game.fold()
            elif msg.startswith("="):
                game.compare(namePure(msg[2:]))
            elif msg == "check":
                game.check()
            else:
                try:
                    game.bet(int(msg))
                except:
                    context.appText("参数错误！")

game = Game()