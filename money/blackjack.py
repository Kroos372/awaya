import random
from static import Awaish
from money import bank

class Card:
    SORT = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    SUITS = ["♦", "♣", "♥", "♠"]
    POINTS = {
        str(i): i for i in range(2, 11)
    }
    POINTS.update({
        i: 10 for i in "JQK"
    })
    POINTS.update({
        "A": 11
    })
    def __init__(self, suit: str, num: str):
        self.suit = suit
        self.num = num

        self.point = self.POINTS[num]
    def __str__(self):
        return self.suit + self.num
    def __lt__(self, other: "Card"):
        return self.point < other.point
    def __eq__(self, value):
        return self.point == value

class Deck(list[Card]):
    def init_deck(self):
        self.clear()
        for suit in Card.SUITS:
            for num in Card.SORT:
                self.append(Card(suit, num))
        random.shuffle(self)

class Hand(list[Card]):
    @property
    def is_blackjack(self):
        return len(self) == 2 and self.total_point == 21
    @property
    def bursted(self):
        return self.total_point > 21
    @property
    def total_point(self):
        sum_point = 0
        As = 0
        for card in self:
            if card == 11:
                As += 1
            sum_point += card.point
        for _ in range(As):
            if sum_point > 21:
                sum_point -= 10
        return sum_point
    def format(self):
        text = " ".join(str(card) for card in self)
        text += f" (总点数{self.total_point})"
        if self.bursted:
            " (💥)"
        elif self.is_blackjack:
            text += " (黑杰克)"
        return text

class PlayerHand(Hand):
    def __init__(self, bet: int):
        super().__init__()
        self.bet = bet
    def format(self) -> str:
        text = super().format()
        text += f" (赌注{self.bet}豆)"
        return text
    
class BankerHand(Hand):
    playing = False
    def format(self) -> str:
        if not self.playing:
            return f"{self[0]} ??"
        else:
            return super().format()

class Player:
    def __init__(self, trip: str, name: str, bet: int):
        self.trip = trip
        self.name = name
        self.bet = bet

        self.hands: list[PlayerHand] = []
        self.hand_index = 0
        
        self.on_insurance = False
    @property
    def is_first_turn(self) -> bool:
        return len(self.hands) == 1 and len(self.hands[0]) == 2
    @property
    def current_hand(self):
        return self.hands[self.hand_index]

    def format(self) -> str:
        text = []
        current_hand = self.current_hand
        for hand in self.hands:
            if hand == current_hand:
                text.append(hand.format() + " <-")
            else:
                text.append(hand.format())
        return "\n".join(text)

    def __str__(self):
        return self.name
    def __eq__(self, value):
        return self.trip == value


class Game:
    context: Awaish
    def __init__(self):
        self.deck = Deck()
        self._reset()
    
    def format_all(self) -> str:
        text = ["### 阿瓦娅手牌"]
        text.append(self.banker_hand.format())
        text.append("### 玩家手牌")
        current_player = self.current_player
        for player in self.players:
            if player == current_player:
                text.append(f"#### =={player}==")
            else:
                text.append(f"#### {player}")
            text.append(player.format())
        return "\n".join(text)
    
    def _reset(self):
        self.status = 0
        self.players: list[Player] = []
        self.player_index = 0
        
        self.banker_hand = BankerHand()

    @property
    def current_player(self):
        return self.players[self.player_index]
    
    def _next_player(self):
        self.player_index += 1
        if self.player_index == len(self.players):
            self._banker_play()
        else:
            self._start_turn()

    def _start_turn(self):
        player = self.current_player
        self.context.appText(f"轮到@{player}")
        self._start_hand()
        if not self.status:
            return
        if self.banker_hand[0] == 11:
            self.context.appText("阿瓦娅的明牌是A，可选择bj =购买保险")

        self.context.appText("请选择操作")
    
    def _next_hand(self):
        player = self.current_player
        player.hand_index += 1
        if player.hand_index == len(player.hands):
            self._next_player()
        else:
            self._start_hand()
    
    def _start_hand(self):
        player = self.current_player
        hand = player.current_hand
        self.context.appText(f"\n\n---\n当前手牌：\n" + hand.format())
        if hand[0] == hand[1]:
            self.context.appText("两张牌分数相同，可选择bj -分牌（将额外下注）")
        elif hand.is_blackjack:
            self.context.appText("黑杰克！🃏")
            self._next_hand()
    
    def _draw(self, end: bool=False):
        player = self.current_player
        hand = player.current_hand
        card = self.deck.pop()
        hand.append(card)
        
        point = hand.total_point
        self.context.appText(f"{player}摸到了{card}，当前手牌：\n" + hand.format())
        if point == 21:
            self.context.appText("已到达21点，自动停牌")
            self._next_hand()
        elif point > 21:
            self.context.appText(f"{player}爆炸了🤯🤯🤯")
            self._next_hand()
        elif end:
            self._next_hand()

    def start(self):
        self.status = 1
        self.deck.init_deck()
        
        for _ in range(2):
            self.banker_hand.append(self.deck.pop())
        
        for player in self.players:
            first_hand = PlayerHand(player.bet)
            for _ in range(2):
                first_hand.append(self.deck.pop())
            player.hands.append(first_hand)
            bank.delete(player.trip, player.bet, "21点")

        self.context.appText(
            "已扣除每位玩家下注并开始游戏\n\n---\n" +
            self.format_all() +
            "---"
        )
        
        # if self.banker_hand.is_blackjack and self.banker_hand[0] == 10:
        #     self._banker_play()
        # else:
        #     self._start_turn()
        self._start_turn()
    
    def play(self, msg: str):
        player = self.current_player
        hand = player.current_hand
        
        if msg == "=":
            if player.is_first_turn and self.banker_hand[0] == 11:
                if bank.getAttr(player.trip, "money") < player.bet / 2:
                    self.context.appText("你的钱不够！")
                    return
                player.on_insurance = True
                bank.delete(player.trip, player.bet / 2, "21点")
                self.context.appText(f"已花费{player.bet / 2}豆购买保险")
            else:
                self.context.appText("只能在你的回合刚开始且阿瓦娅明牌为A时买保险！")
        elif msg == "-":
            if len(hand) == 2 and hand[0] == hand[1]:
                if bank.getAttr(player.trip, "money") < player.bet:
                    self.context.appText("你的钱不够！")
                    return
                bank.delete(player.trip, player.bet, "21点")

                second_card = hand.pop()
                second_hand = PlayerHand(player.bet)
                second_hand.append(second_card)

                hand.append(self.deck.pop())
                second_hand.append(self.deck.pop())
                player.hands.insert(player.hand_index + 1, second_hand)
                self.context.appText(
                    "分牌成功。当前手牌：\n" +
                    player.format() +
                    "\n请继续。"
                )
            else:
                self.context.appText("只能在手牌刚开始且两张牌相同时分牌！")
            
        elif msg == "1":
            self._draw()
        elif msg == "2":
            if bank.getAttr(player.trip, "money") <hand.bet:
                self.context.appText("你的钱不够！")
            elif len(hand) != 2:
                self.context.appText("只能在手牌刚开始时双倍下注！")
            else:
                self.context.appText(f"{player}双倍下注了，只能再摸一张牌。")
                bank.delete(player.trip, player.bet, "21点")
                hand.bet *= 2
                self._draw(True)
        elif msg == ".":
            self.context.appText("已停止发牌。")
            self._next_hand()
    
    def _banker_play(self):
        hand = self.banker_hand
        hand.playing = True
        self.context.appText("\n\n---\n轮到阿瓦娅，阿瓦娅手牌是：\n" + hand.format())
        
        if hand.is_blackjack:
            self.context.appText("黑杰克！🃏")
            for player in self.players:
                if player.on_insurance:
                    self.context.appText(f"{player}保险生效，退回{player.bet * 1.5}豆。")
                    bank.add(player.trip, player.bet * 1.5, "21点")
                for hand in player.hands:
                    if hand.is_blackjack:
                        self.context.appText(f"{player}与阿瓦娅平局，退回{hand.bet}豆。")
                        bank.add(player.trip, hand.bet, "21点")
                    else:
                        self.context.appText(f"{player}输了😭")
                        bank.offer(hand.bet, f"{player.trip}21点")
            self._reset()
            return

        point = hand.total_point
        if point >= 17:
            self.context.appText(f"已到达17点，阿瓦娅停止摸牌。\n最终点数=={point}==")
            self._final_settle()
        while self.status:
            card = self.deck.pop()
            hand.append(card)

            self.context.appText(f"阿瓦娅摸到了{card}，当前手牌：\n" + hand.format())
            point = hand.total_point
            if point > 21:
                self.context.appText(f"阿瓦娅爆炸了🤯🤯🤯")
                self._final_settle()
            elif point < 17:
                self.context.appText("阿瓦娅继续摸牌")
            else:
                self.context.appText(f"已到达17点，阿瓦娅停止摸牌。\n最终点数=={point}==")
                self._final_settle()
    
    def _final_settle(self):
        self.context.appText("\n\n---\n")
        b_point = self.banker_hand.total_point
        if b_point > 21:
            b_point = -1
        
        for player in self.players:
            for hand in player.hands:
                point = hand.total_point

                if point > 21 or point < b_point:
                    self.context.appText(f"{player}输了😭({point}点)")
                    bank.offer(hand.bet, f"{player.trip}21点")
                    continue

                bank.add(player.trip, hand.bet, "21点")
                if hand.is_blackjack:
                    hand.bet *= 1.5
                    self.context.appText(f"{player}赢了，获得{hand.bet}豆(黑杰克)！！！🍾🍾🍾")
                elif point == b_point:
                    self.context.appText(f"🤔平局。退给{player} {hand.bet}豆。")
                    continue
                else:
                    self.context.appText(f"{player}赢了，获得{hand.bet}豆！！🍾")
                bank.add(player.trip, hand.bet, "21点")

        self._reset()

BJMENU = "\n".join([
    "21点",
    "bj <豆数>：下注并加入",
    "bj 退出：退出，不扣豆",
    "bj 开始",
    "游戏中：",
    "bj =：买保险（如果能）",
    "bj 1：要牌",
    "bj 2：双倍下注",
    "bj .：停牌",
    "bj -：分牌（如果能）",
    "bj check：查看局面"
])

def main(context: Awaish, sender: str, msg: str):
    trip = context.user["trip"]
    if msg == "help":
        context.appText(BJMENU)
        return
    elif not bank.get(trip):
        context.appText("你还没有银行！")
        return

    elif msg == "退出" and trip in game.players:
        if game.status:
            context.appText("这局已经开始了，等下局吧~")
            return
        game.players.remove(trip)
        context.appText("退出成功")
    
    elif trip in game.players:
        if game.status:
            if msg == "check":
                context.appText(game.format_all())
            elif trip == game.current_player:
                game.play(msg)
        elif msg == "开始":
            game.context = context
            game.start()

    elif trip not in game.players:
        if game.status:
            context.appText("这局已经开始了，等下局吧~")
            return
        try:
            bet = int(msg)
            assert bet > 0
        except:
            context.appText("参数错误！")
            return
        if bank.getAttr(trip, "money") <bet:
            context.appText("你的钱不够！")
        else:
            game.players.append(Player(trip, sender, bet))
            context.appText("加入成功")

game = Game()