# code by sora
import random
from enum import Enum
from static import bank 
from typing import List, Dict, Optional

class Card:
    def __init__(self, suit: int, value: int):
        self.suit = suit  # 0-3: ♠♥♣♦
        # 将A的值从1改为14
        self.value = 14 if value == 1 else value  # 2-13, A=14
        
    def __str__(self):
        suits = ['♠', '♥', '♣', '♦']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        display_value = 0 if self.value == 14 else self.value - 1
        return f"{suits[self.suit]}{values[display_value]}"

class HandType(Enum):
    SPECIAL = 0  # 235不同花色
    BAOZI = 6    # 豹子
    SHUNJIN = 5  # 顺金
    JINHUA = 4   # 金花
    SHUNZI = 3   # 顺子
    DUIZI = 2    # 对子
    SINGLE = 1   # 单张

class Hand:
    def __init__(self, cards: List[Card]):
        self.cards = sorted(cards, key=lambda x: x.value)
        self.type = self._evaluate_hand()
        
    def _evaluate_hand(self) -> HandType:
        # 检查特殊牌型(235)
        if len({card.suit for card in self.cards}) == 3 and \
           sorted([14 if x == 1 else x for x in [card.value for card in self.cards]]) == [2,3,5]:
            return HandType.SPECIAL
            
        # 检查豹子
        if len({card.value for card in self.cards}) == 1:
            return HandType.BAOZI
            
        # 检查顺金和金花
        same_suit = len({card.suit for card in self.cards}) == 1
        values = sorted([card.value for card in self.cards])
        is_straight = (values[2] - values[0] == 2 and values[1] - values[0] == 1) or \
                     (values == [12, 13, 14])  # Q,K,A
        
        if same_suit and is_straight:
            return HandType.SHUNJIN
        if same_suit:
            return HandType.JINHUA
        if is_straight:
            return HandType.SHUNZI
            
        # 检查对子
        if len({card.value for card in self.cards}) == 2:
            return HandType.DUIZI
            
        return HandType.SINGLE

class Player:
    def __init__(self, trip: str, name: str):
        self.trip = trip
        self.name = name
        self.hand: Optional[List[Card]] = None
        self.seen_cards = False
        self.total_bet = 0
        self.folded = False

    def update_name(self, new_name: str):
        self.name = new_name

class ZhaJinHua:
    RULES = """
炸金花具体规则：[点我点我点我（欠点了）](https://zhuanlan.zhihu.com/p/717171407)
z 加入 加入游戏
z 规则 查看规则
z 开始 开始游戏
z 看牌 看牌
z <金额> 下注
z 比牌 <对手昵称> 比牌
z 弃牌 弃牌
"""
    def __init__(self, context):
        self.context = context
        self.players: Dict[str, Player] = {}  # trip做key
        self.trip_to_name: Dict[str, str] = {}  # 映射
        self.deck: List[Card] = []
        self.current_player: Optional[str] = None  #存当前玩家trip
        self.game_started = False
        self.pot = 0
        self.base_bet = 0
        self.current_bet = 0
        self.last_bettor: Optional[str] = None  #存上家trip

    def update_player_name(self, trip: str, new_name: str):
        """更新玩家昵称"""
        if trip in self.players:
            self.players[trip].update_name(new_name)
            self.trip_to_name[trip] = new_name

    def _init_deck(self):
        self.deck = [Card(s, v) for s in range(4) for v in range(2, 15)]
        random.shuffle(self.deck)

    def join_game(self, trip: str, name: str) -> bool:
        if self.game_started:
            self.context.appText(f"游戏已经开始，{name}无法加入")
            return False
        if len(self.players) >= 6:
            self.context.appText("游戏人数已满")
            return False
        self.players[trip] = Player(trip, name)
        self.trip_to_name[trip] = name
        self.context.appText(f"{name}加入了游戏")
        return True

    def start_game(self):
        if len(self.players) < 2:
            self.context.appText("玩家数量不足，无法开始游戏")
            return
        
        self.game_started = True
        self._init_deck()
        
        # 发牌
        for player in self.players.values():
            player.hand = [self.deck.pop() for _ in range(3)]
            player.total_bet = self.base_bet
            self.pot += self.base_bet
            
        self.current_bet = self.base_bet
        self.current_player = list(self.players.keys())[0]
        self.context.appText("游戏开始！每位玩家已收到三张牌")
        self._display_player_order()
        
        # 私发牌面
        for player in self.players.values():
            self._send_private_cards(player.trip)

    def _send_private_cards(self, trip: str):
        if trip not in self.players:
            return
        player = self.players[trip]
        if not player.seen_cards:
            cards_str = "???"
        else:
            cards_str = " ".join(str(card) for card in player.hand)
        self.context.appText(f"你的牌是: {cards_str}", "whisper", to=player.name)

    def look_cards(self, trip: str):
        if trip not in self.players or self.players[trip].folded:
            return
        player = self.players[trip]
        player.seen_cards = True
        self._send_private_cards(trip)
        self.context.appText(f"{player.name}看了自己的牌")

    def bet(self, trip: str, amount: int):
        if not self._validate_bet(trip, amount):
            return
        
        player = self.players[trip]
        self.pot += amount
        player.total_bet += amount
        self.current_bet = amount if player.seen_cards else amount * 2
        self.last_bettor = trip
        self.context.appText(f"{player.name}{'(明牌)' if player.seen_cards else '(暗牌)'} 下注{amount}阿瓦豆！")
        bank.delete(trip, amount)
        self.context.appText(f"奖池已累积到{self.pot}阿瓦豆！！！")

        self._next_player()

    def compare_cards(self, trip: str, target_trip: str):
        if not self._validate_compare(trip, target_trip):
            return
            
        compare_cost = self.current_bet * 2
        if bank.getAttr(trip, "money") < compare_cost:
            self.context.appText(f"余额不足，当前余额{bank.getAttr(trip, 'money')}")
            return
        else:
            self.context.appText(f"{self.players[trip].name}花费{compare_cost}向{self.players[target_trip].name}发起比牌！")
            bank.delete(trip, compare_cost)
        self.players[trip].total_bet += compare_cost
        self.pot += compare_cost
        
        player_hand = Hand(self.players[trip].hand)
        target_hand = Hand(self.players[target_trip].hand)
        
        winner_trip = self._compare_hands(player_hand, target_hand, trip, target_trip)
        loser_trip = target_trip if winner_trip == trip else trip
        
        self.players[loser_trip].folded = True
        self.context.appText(f"{self.players[trip].name}与{self.players[target_trip].name}比牌，{self.players[winner_trip].name}胜！败者留下注金离开")
        
        if self._check_game_end():
            self._end_game()
        else:
            self._next_player()

    def _compare_hands(self, hand1: Hand, hand2: Hand, player1: str, player2: str) -> str:
        # 比较牌型大小
        # 235打豹子
        if hand1.type == HandType.SPECIAL and hand2.type == HandType.BAOZI:
            return player1
        elif hand1.type == HandType.BAOZI and hand2.type == HandType.SPECIAL:
            return player2

        if hand1.type.value > hand2.type.value:
            return player1
        elif hand2.type.value > hand1.type.value:
            return player2
        
        # 同种牌型比较
        if hand1.type == HandType.DUIZI:
            # 对子比较
            pair1 = next(v for v in {c.value for c in hand1.cards} if sum(1 for c in hand1.cards if c.value == v) == 2)
            pair2 = next(v for v in {c.value for c in hand2.cards} if sum(1 for c in hand2.cards if c.value == v) == 2)
            if pair1 != pair2:
                return player1 if pair1 > pair2 else player2
            # 对子相同，比较单牌
            single1 = next(c for c in hand1.cards if c.value != pair1)
            single2 = next(c for c in hand2.cards if c.value != pair2)
            if single1.value != single2.value:
                return player1 if single1.value > single2.value else player2
            # 单牌相同，比较对子的花色
            suit1 = min(c.suit for c in hand1.cards if c.value == pair1)
            suit2 = min(c.suit for c in hand2.cards if c.value == pair2)
            if suit1 != suit2:
                return player1 if suit1 < suit2 else player2
            # 对子花色相同，比较单牌花色
            return player1 if single1.suit < single2.suit else player2
        
        # 其他牌型比较最大牌
        cards1 = sorted(hand1.cards, key=lambda c: (c.value, -c.suit), reverse=True)
        cards2 = sorted(hand2.cards, key=lambda c: (c.value, -c.suit), reverse=True)
        
        for card1, card2 in zip(cards1, cards2):
            if card1.value != card2.value:
                return player1 if card1.value > card2.value else player2
            if card1.suit != card2.suit:
                return player1 if card1.suit < card2.suit else player2
                
        # 完全相同，主动比牌者输
        return player2

    def fold(self, trip: str):
        if trip not in self.players or self.players[trip].folded:
            return
            
        player = self.players[trip]
        player.folded = True
        self.context.appText(f"{player.name}弃牌")
        
        if self._check_game_end():
            self._end_game()
        else:
            self._next_player()

    def _validate_bet(self, trip: str, amount: int) -> bool:
        player = self.players[trip]
        if not self.game_started or trip not in self.players:
            return False
        if self.players[trip].folded:
            return False
        if trip != self.current_player:
            self.context.appText(f"还没轮到你，当前玩家是{self.players[self.current_player].name}")
            return False
        if bank.getAttr(trip, "money") < amount:
            self.context.appText(f"余额不足，当前余额{bank.getAttr(trip, 'money')}")
            return False
        if bank.getAttr(trip, "money") == amount:
            self.context.appText(f"{player.name}ALL IN了！")
            self.context.appText(f"![](https://postimg.cc/vgMpWNWt)")
            
        if player.seen_cards == False:
            amount *= 2
        if amount < self.current_bet:
            self.context.appText(f"下注金额不能小于当前注数{self.current_bet}")
            return False
        return True

    def _validate_compare(self, trip: str, target_trip: str) -> bool:
        if not self.game_started or trip not in self.players or target_trip not in self.players:
            return False
        if self.players[trip].folded or self.players[target_trip].folded:
            return False
        if trip != self.current_player:
            self.context.appText(f"还没轮到你，当前玩家是{self.players[self.current_player].name}")
            return False
        return True

    def _next_player(self):
        active_players = [p for p in self.players.keys() if not self.players[p].folded]
        current_idx = active_players.index(self.current_player)
        self.current_player = active_players[(current_idx + 1) % len(active_players)]
        
        if self.current_player == self.last_bettor:
            self._end_game()
        else:
            self._display_player_order()

    def _check_game_end(self) -> bool:
        active_players = [p for p in self.players.keys() if not self.players[p].folded]
        return len(active_players) == 1

    def _end_game(self):
        global game
        winner_trip = next(p for p in self.players.keys() if not self.players[p].folded)
        winner = self.players[winner_trip]
        self.context.appText(f"游戏结束！获胜者是{winner.name}，赢得{self.pot}阿瓦豆！")
        self.context.appText(f"{winner.name}的牌是: {' '.join(str(card) for card in winner.hand)}")
        bank.add(winner_trip, self.pot)
        self.game_started = False
        game = None  # 重置游戏实例

    def _display_player_order(self):
        """显示玩家出牌顺序"""
        active_players = [p for p in self.players.keys() if not self.players[p].folded]
        order = []
        self.context.appText("当前行动顺序：（被高光玩家行动）")
        for trip in active_players:
            name = self.players[trip].name
            if trip == self.current_player:
                name = f"=={name}=="
            order.append(name)
        self.context.appText("->".join(order))

def main(context, name: str, trip: str, command: str):
    global game
    if game != None:
        game.context = context
    if command == "加入" or command == "join":
        if trip == "":
            context.appText("亲请带着你的银行卡进行游玩！")
            return
        if game is None:
            game = ZhaJinHua(context)
        if trip in game.players:
            context.appText("你已经加入游戏了！")
            return
        game.join_game(trip, name)
    elif command == "规则" or command == "help":
        context.appText(ZhaJinHua.RULES)
    else:
        # 更新玩家当前昵称
        game.update_player_name(trip, name)
        
        if command == "开始" or command == "start":
            if not game.game_started:
                game.start_game()
            else:
                context.appText("游戏已经开始了！")
        elif command == "看牌" or command == "look":
            game.look_cards(trip)
        elif command.isdigit():
            game.bet(trip, int(command))
        elif (command.startswith("比牌 ") or command.startswith("compare ")):
            target_name = command[3:].strip() if command.startswith("比牌") else command[7:].strip()
            target_trip = next((t for t, n in game.trip_to_name.items() if n == target_name), None)
            if target_trip:
                game.compare_cards(trip, target_trip)
            else:
                context.appText(f"找不到玩家：{target_name}")
        elif command == "弃牌" or command == "fold":
            game.fold(trip)

game: ZhaJinHua = None