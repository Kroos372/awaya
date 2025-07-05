from static import Awaish
import random

UNOMENU = "\n".join([
    "UNO, Rewriten from [Blaze](https://github.com/geGDVS/UNO/)",
    "u join",
    "u bot",
    "u quit",
    "u start",
    "u <card>",
    "u end",
    "u rules: rules in Chinese",
])
UNORULE = "\n".join([
    "牌先出完者获胜。游戏规则:",
    "一般地，uno牌分为<颜色><名称(多是数字)>两部分(如==G2==, ==R.==)，打出的牌需 与上家<颜色>或/和<名称>相同。",
    "对于<名称>部分，存在以下几种具有特殊效果的情况:",
    "1. ==-==(转向): 出牌顺序逆转(顺时针变逆时针，反之亦然)",
    "2. ==.==(禁止): 使下家跳过一回合",
    "3. ==+2==: 使下家增加2张牌，并跳过一回合。",
    "另外有==wild==(变色), ==+4==两种需要参数的特殊牌:",
    "1. wild <颜色>: 指定下家需要出的颜色(无<名称>)",
    "2. +4 <颜色>: 在==wild==的基础上，使下家增加4张牌，并跳过一回合。",
    "#### +4的质疑规则: ",
    "一般地，+4只能在无与当前牌<颜色>相同的牌时出(如当前牌是==B1==，手中拥有B色牌则不能出+4)。",
    "玩家A出+4时，下家B可以选择质疑A。质疑后该玩家须展示手牌。此时有两种情况:",
    "1. A出牌合规(无与当前牌<颜色>相同的牌): 变色生效，B摸6张，并跳过一回合",
    "2. A出牌不合规(有与当前牌<颜色>相同的牌): 变色生效，A摸4张，B跳过一回合",
    "---",
    "出牌规则:",
    "==u 牌 <参数>==出牌，例如==u G2==, ==u wild B==",
    "==u .==跳过回合, ==u ?!==质疑",
    "==u check==查看自己目前的牌, ==u all==查看所有人牌数",
])

class Card:
    COLORS = {
        "R": "red",
        "G": "green",
        "B": "blue",
        "Y": "#d9da1f"
    }
    SORT = [str(num) for num in range(10)] + ["+2", ".", "-"]
    def __init__(self, color: str="", number: str="", wild: str=""):
        self.color = color
        self.number = number
        self.wild = wild
    def __str__(self):
        if self.color:
            color_name = self.COLORS[self.color]
            text = rf"$\color{{{color_name}}}{{{self.color}{self.number}}}$"
            if self.number == ".":
                text += "(🚫)"
            elif self.number == "-":
                text += "(🔄)"
            return text
        elif self.wild == "WILD":
            return r"$\color{red}{w}\color{green}{i}\color{blue}{l}\color{#d9da1f}{d}$"
        else:
            return "+4"
    def __lt__(self, other: "Card"):
        if other.wild:
            if self.color or other.wild == "+4":
                return True
            else:
                return False
        elif self.wild:
            return False
        elif self.color != other.color:
            return self.color < other.color
        else:
            return self.SORT.index(self.number) < self.SORT.index(other.number)
    def __eq__(self, value: str):
        if self.wild:
            return self.wild == value
        else:
            return self.color + self.number == value
    @property
    def display_name(self) -> str:
        if self.color:
            return str(self)
        elif self.wild == "WILD":
            return r"$\large{\color{red}{W}\color{green}{I}\color{blue}{L}\color{#d9da1f}{D}}$"
        else:
            return r"$\Large{+4}$"

class Cards(list[Card]):
    def __init__(self):
        self._trash = []
    
    def pop_card(self, discard: bool=False) -> Card:
        if not self:
            self.extend(self._trash)
            self._trash = []
            random.shuffle(self)

        card = self.pop()
        if discard:
            self.discard(card)
        return card
    def discard(self, card):
        self._trash.append(card)
    def _create_card(self, **kwargs):
        self.append(Card(**kwargs))
    def new_cards(self):
        super().__init__()
        for color in "RGBY":
            for _ in range(2):
                for number in range(1, 10):
                    self._create_card(color=color, number=str(number))
                for number in ["+2", ".", "-"]:
                    self._create_card(color=color, number=number)
            self._create_card(color=color, number="0")
        for _ in range(4):
            self._create_card(wild="+4")
            self._create_card(wild="WILD")
        random.shuffle(self)

class Player:
    def __init__(self, name: str):
        self.is_bot = False
        self.name = name
        self.cards: list[Card] = []
    def __str__(self):
        return self.name
    def __eq__(self, value):
        return self.name == value

    def get_card(self, command: str):
        return self.cards[self.cards.index(command)]

    def valid_play(self, card: Card | None) -> bool:
        if not card:
            return False
        valid = True
        self.cards.remove(card)
        if len(self.cards) == 1 and self.cards[0].wild:
            valid = False
        self.cards.append(card)
        return valid
    def check_win(self) -> bool:
        if len(self.cards) == 1:
            uno.context.appText(f"{uno.current_player} ==UNO==!!!")
        elif not self.cards:
            uno.context.appText(
                "Game over.\n" +
                f"{uno.current_player} won."
            )
            uno.end_game()
            return True
        return False
    def has_color(self, color: str) -> bool:
        for card in self.cards:
            if card.color == color:
                return True
        return False
    def draw_cards(self, num: int):
        for _ in range(num):
            self.cards.append(uno.cards.pop_card())
        # LOL
        if num > 1:
            s = "s"
        else:
            s = ""

        uno.context.appText(f"Drawed {num} card{s}, " + self.format_cards(), "whisper", to=self.name)
    def format_cards(self) -> str:
        self.cards.sort()
        return "Your cards: \n" + " ".join([str(card) for card in self.cards])

class AutoBot(Player):
    def __init__(self, name: str):
        super().__init__(name)
        self.is_bot = True

    def draw_cards(self, num: int):
        for _ in range(num):
            self.cards.append(uno.cards.pop_card())

    def getCardType(self) -> dict[str, list[Card]]:
        types = {
            "R": [],
            "Y": [],
            "B": [],
            "G": [],

            "+2": [],
            ".": [],
            "-": [],

            "WILD": []
        }
        types.update({str(x): [] for x in range(10)})
        for card in self.cards:
            if card.wild:
                types["WILD"].append(card)
            else:
                types[card.color].append(card)
                types[card.number].append(card)
        
        return types

    def getMaxColor(self, types: dict=None) -> str:
        types = types or self.getCardType()
        color = "R"
        maxinum = len(types["R"])
        for i in "YBG":
            if len(types[i]) > maxinum:
                maxinum = len(types[i])
                color = i
        return color

    def play(self) -> str:
        if uno.status == 2:
            return "."
        else:
            types = self.getCardType()
            color, number = uno.last_card.color, uno.last_card.number
            card: Card = None

            if types[color]:
                card = random.choice(types[color])
                text = card.color + card.number
            elif types.get(number):
                card = random.choice(types[number])
                text = card.color + card.number
            elif types["WILD"]:
                card = random.choice(types["WILD"])
                text = f"{card.wild} {self.getMaxColor(types)}"

            if not self.valid_play(card):
                text = ""

        return text or "."

class Uno:
    def __init__(self):
        self.context: Awaish
        self.plus4_player: Player
        self.status = 0 # 0: 结束, 1: 出牌, 2: 质疑
        self.cards = Cards()
        self.players: list[Player | AutoBot] = []
    @property
    def current_player(self):
        return self.players[self.player_index]
    
    def _format_order(self) -> str:
        text = []
        for i, player in enumerate(self.players):
            if i == self.player_index:
                text.append(f"=={player}==")
            else:
                text.append(player.name)
        return "Order: " + " -> ".join(text)
    def _format_all(self) -> str:
        text = []
        for player in self.players:
            text.append(f"{player}: {len(player.cards)}")
        return "\n".join(text)
    
    def start_game(self):
        self.status = 1
        self.player_index = 0
        
        random.shuffle(self.players)
        self.cards.new_cards()
        self.last_card = self.cards.pop_card(True)
        while self.last_card.wild:
            self.last_card = self.cards.pop_card(True)
        
        for player in self.players:
            player.draw_cards(7)

        self.context.appText(
            self._format_order() + "\n" +
            f"Start with card {self.last_card}\n" +
            f"@{self.current_player} plays first.\n" +
            "P.S. Enable latex to get best experience"
        )
        self._check_bot()

    def end_game(self):
        self.status = 0
        self.players = []
        self.cards.clear()
    
    def _get_player(self, sender: str) -> Player:
        return self.players[self.players.index(sender)]
    
    def _next_player(self):
        self.player_index = (self.player_index + 1) % len(self.players)
        self.context.appText(f"Turn to @{self.current_player}")
    
    def _is_valid(self, card: Card) -> bool:
        return card.color == self.last_card.color or card.number == self.last_card.number
    
    def _reverse(self):
        self.players.reverse()
        self.player_index = len(self.players) - 1 - self.player_index
        self.context.appText("Order reversed")
    
    def _change_color(self, color: str):
        new_card = Card(color)
        self.last_card = new_card
        self.context.appText(f"Color changed to {new_card.display_name}")
    
    def _challenge_plus4(self):
        player = self.current_player
        
        if self.plus4_player.has_color(self.plus4_card.color):
            self.context.appText(
                "Challenge successfully!\n" +
                f"{self.plus4_player} drawed 4 cards."
            )
            self.plus4_player.draw_cards(4)
        else:
            self.context.appText(
                "Challenge failed...\n" +
                f"{player} drawed 6 cards."
            )
            player.draw_cards(6)

        self.status = 1
        self._next_player()
    
    def _play_wild_card(self, card: Card, color: str):
        if color not in "RGBY":
            self.context.appText("Wrong color.")
            return

        player = self.current_player
        last_card = self.last_card
        self.context.appText(f"{player} played {card.display_name}!")
        self.cards.discard(card)
        player.cards.remove(card)

        if player.check_win():
            return

        self._change_color(color)
        self._next_player()

        if card.wild == "+4":
            self.plus4_player = player
            self.plus4_card = last_card
            self.status = 2
            self.context.appText(f"@{self.current_player} send ==u ?!== to challenge or ==u .== to skip.")
    
    def _play_normal_card(self, card: Card):
        player = self.current_player
        if not self._is_valid(card):
            self.context.appText("Invalid play.")
            return

        self.cards.discard(card)
        player.cards.remove(card)
        self._normal_card_effect(card)
    
    def _normal_card_effect(self, card: Card):
        player = self.current_player
        self.context.appText(f"{player} played {card.display_name}")
        
        if player.check_win():
            return
        
        if card.number == "-":
            self._reverse()
        elif card.number == ".":
            self._next_player()
            self.context.appText(f"Skipped {self.current_player}")
        elif card.number == "+2":
            self._next_player()
            self.current_player.draw_cards(2)
            self.context.appText(f"{self.current_player} drawed 2 cards then skipped")

        self.last_card = card
        self._next_player()
    
    def _check_bot(self):
        if self.status and self.current_player.is_bot:
            bot: AutoBot = self.current_player
            self.play(bot.name, bot.play())
    
    def play(self, sender: str, msg: str):
        if msg == "check":
            player = self._get_player(sender)
            self.context.appText(
                f"Last card: {self.last_card}, "
                + self._format_order() + "\n"
                + player.format_cards(),
                "whisper", to=sender
            )
        elif msg == "all":
            self.context.appText(
                self._format_order() + "\n" +
                "Player hands: \n" + self._format_all()
            )
        elif self.current_player == sender:
            player = self.current_player
            if msg == "?!" and self.status == 2:
                self._challenge_plus4()
            elif msg == ".":
                if self.status == 1:
                    drawed_card = self.cards.pop_card()
                    self.context.appText(f"{sender} drawed 1 card")
                    if not drawed_card.wild and self._is_valid(drawed_card):
                        self._normal_card_effect(drawed_card)
                        self.cards.discard(drawed_card)
                    else:
                        player.cards.append(drawed_card)
                        self.context.appText(player.format_cards(), "whisper", to=sender)
                        self._next_player()
                else:
                    self.context.appText(
                        f"{sender} didn't challenge.\n"
                        f"{sender} drawed 4 cards then skipped."
                    )
                    self.status = 1
                    player.draw_cards(4)
                    self._next_player()
            elif self.status == 1:
                try:
                    command, *args = msg.upper().split(" ")
                    card = player.get_card(command)

                    if not player.valid_play(card):
                        self.context.appText("The last card cannot be a wild card")
                        return
                    if card.wild:
                        self._play_wild_card(card, args[0])
                    else:
                        self._play_normal_card(card)
                except Exception:
                    self.context.appText("Wrong play.")
            else:
                self.context.appText("Wrong play.")
        else:
            self.context.appText("Not your turn.")
        
        self._check_bot()

def main(context: Awaish, sender: str, msg: str, bot: bool=False):
    if msg == "join":
        if uno.status:
            context.appText("The game is in progress, please wait for the next round")
        elif sender in uno.players:
            context.appText("You've already joined")
        else:
            if not bot:
                uno.players.append(Player(sender))
            else:
                uno.players.append(AutoBot(sender))
            context.appText(f"Joined successfully, {len(uno.players)} player(s) now.")
    elif msg == "quit" and sender in uno.players and not uno.status:
        uno.players.remove(sender)
        context.appText("You left the game...")
    elif msg == "start" and not uno.status:
        if len(uno.players) >= 2:
            uno.context = context
            uno.start_game()
        else:
            context.appText("Not enough people.")
    elif msg == "end" and uno.status:
        uno.end_game()
        context.appText("Game over...")
    elif msg == "help":
        context.appText(UNOMENU)
    elif msg == "rules":
        context.appText(UNORULE)
    elif msg[:3] == "bot":
        addNick = msg[4:] or context.nick
        if uno.status:
            context.appText("The game is in progress, please wait for the next round")
        elif addNick in uno.players:
            context.appText("BOT!!!!!!!😭")
            main(context, addNick, "quit", True)
        else:
            context.appText("BOT!!!!!!!ヾ|≧_≦|〃")
            main(context, addNick, "join", True)
    elif sender in uno.players and uno.status:
        uno.play(sender, msg)

uno = Uno()