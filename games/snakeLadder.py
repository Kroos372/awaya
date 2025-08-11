import random
from static import Awaish
from money import bank

SNAKE_MENU = "\n".join([
    "蛇棋",
    "sl join <flair>: 加入游戏，flair为玩家标识在棋盘上的字符",
    "sl flair <flair>: 更改标识",
    "sl quit: 退出游戏",
    "sl bot: 添加机器人",
    "sl start: 开始游戏",
    "sl rules: 规则"
])
SNAKE_RULE = "\n".join([
    "https://baike.baidu.com/item/%E8%9B%87%E6%A3%8B/3674048",
    "sl r: 摇骰子",
    "sl check: 查看棋盘"
])

class Player:
    is_bot: bool
    def __init__(self, name: str, trip: str, flair: str):
        self.trip = trip
        self.name = name
        self.flair = flair
        self.position: int = 0
    
    def __str__(self):
        return self.name
    def __eq__(self, value):
        if self.trip:
            return self.trip == value
        else:
            return self.name == value

class Human(Player):
    is_bot = False

class AutoBot(Player):
    is_bot = True



class Square:
    def __init__(self, number: int):
        self.number = number
        self.step: int = 0 # 0表示什么都没有, 数字表示+或-对应的格数
        self.players: list[Player] = []
    def __str__(self):
        return str(self.number + 1)

class Board(list[Square]):
    def __init__(self):
        self.new_board()
        super().__init__()
    
    def new_board(self, ladders: int=6, snakes: int=7):
        self.clear()
        for i in range(100):
            self.append(Square(i))
        
        # ↑
        for _ in range(ladders):
            start = 99
            step = 99
            while (start + step > 98) or self[start].step or self[start+step].step:
                start = random.randint(0, 87)
                step = random.randint(11, 66)
            self[start].step = step
        # ↓
        for _ in range(snakes-1):
            start = 0
            step = 99
            while (start - step < 0) or self[start].step or self[start-step].step:
                start = random.randint(11, 98)
                step = random.randint(11, 66)
            self[start].step = -step
        # 终点前滑下去，蛇棋不得不品的一环
        self[random.randint(93, 98)].step = -step
    
    def move_player(self, player: Player, step: int):
        to = player.position + step
        
        if to == 99:
            game.context.appText(f"{player}到达终点，获胜！")
            game.end_game()
        elif to > 99:
            real_step = 99 - player.position # 实际向前移动步数
            backward = step - real_step # 向后退回步数

            game.context.appText(f"{player}到达终点后又回退了{backward}格")
            self.move_player(player, real_step - backward)
        else:
            self[player.position].players.remove(player)
            player.position = to
            self[to].players.append(player)
            game.context.appText(f"{player}移动到了{self[to]}")
    
    def format(self) -> str:
        head = ["|" * 11, "|" + ":-:|" * 10]
        index = 0
        direction = 1 # 1向右, -1向左

        for _ in range(10):
            text = "|"
            for _ in range(10):
                square = self[index]
                if not square.step:
                    text_ = str(index + 1)
                elif square.step > 0:
                    text_ = f"{index+1}(↑{index+square.step+1})"
                else:
                    text_ = f"{index+1}(↓{index+square.step+1})"
                
                if square.players:
                    flairs = ",".join(player.flair for player in square.players)
                    text_ += f"[{flairs}]"

                if direction > 0:
                    text = text + f"{text_}|"
                else:
                    text = f"|{text_}" + text
                index += 1

            direction *= -1
            head.insert(2, text)
        
        return "\n".join(head)

class Game:
    DICES = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    def __init__(self):
        self.context: Awaish
        self.status = 0

        self.board: Board = Board()
        
        self.players: list[Player] = []
        self.player_index: int

    @property
    def current_player(self):
        return self.players[self.player_index]
    
    def get_player(self, nick: str="", trip: str="") -> Player | None:
        for player in self.players:
            if ((trip and player.trip == trip) or
                (not player.trip and player.name == nick)):
                return player
    
    def get_square(self, player: Player) -> Square:
        return self.board[player.position]

    def add_player(self, nick: str, trip: str, flair: str="👒", bot: bool=False):
        if self.status:
            self.context.appText("这局已经开始了")
            return
        if self.get_player(nick, trip):
            self.context.appText("你已经加入过了")
            return
        if not flair:
            self.context.appText("请设置一个标识")
            return
        
        if not bot:
            self.players.append(Human(nick, trip, flair))
        else:
            self.players.append(AutoBot(nick, trip, flair))
        self.context.appText("加入成功，再找些人吧")
    
    def remove_player(self, player: Player):
        if self.status:
            self.context.appText("这局已经开始了")
            return
        if not player:
            self.context.appText("你已经退出过了")
            return
        
        self.players.remove(player)
        self.context.appText("退出成功")
    
    def _format_order(self) -> str:
        text = []
        for i, player in enumerate(self.players):
            if i == self.player_index:
                text.append(f"=={player}==")
            else:
                text.append(player.name)
        return " -> ".join(text)

    def play(self, player: Player, msg: str):
        msg_list = msg.split(" ")
        if msg == "check":
            self.context.appText(self._format_order())
            self.context.appText(self.board.format())
            self.context.appText(f"你位于{self.get_square(player)}")
            return
        if player != self.current_player:
            self.context.appText(f"现在是{self.current_player}的回合")
            return
        
        if msg == "r":
            dices = self.roll()
            step = sum(dices)
            self.context.appText(f"{player}摇出了{self.format_dices(dices)}(**{step}**)")
            self.board.move_player(player, step)
            self._handle_snake(player)
            self._next_player()
        
        if self.status and self.current_player.is_bot:
            self.play(self.current_player, "r")
    
    def _handle_snake(self, player: Player):
        step = self.get_square(player).step
        if not step:
            return
        
        if step > 0:
            self.context.appText("\n".join([
                f"{player}遇到了梯子。",
                f"{player}爬上了梯子..."
            ]))
        else:
            self.context.appText("\n".join([
                f"{player}遇到了蛇！",
                f"{player}从蛇身滑了下去..."
            ]))

        self.board.move_player(player, step)
    
    def roll(self, nums: int=1) -> list[int]:
        return [random.randint(1, 6) for _ in range(nums)]
    
    def format_dices(self, rolls: list[int]) -> str:
        result = []
        for point in rolls:
            result.append(self.DICES[point])
        return ", ".join(result)
    
    def _next_player(self):
        if self.status:
            self.player_index = (self.player_index + 1) % len(self.players)
            self.context.appText(f"轮到 @{self.current_player}")
    
    def start(self):
        if len(self.players) < 2:
            self.context.appText("至少两人才能开始")
            return

        self.status = 1
        self.player_index = 0
        self.board.new_board()
        random.shuffle(self.players)
        for player in self.players:
            self.board[0].players.append(player)

        self.context.appText(self._format_order())
        self.context.appText(self.board.format())
        self.context.appText(f"由@{self.current_player} 开始")

    def end_game(self):
        self.players = []
        self.status = 0


game = Game()


def main(context: Awaish, sender: str, msg: str):
    game.context = context
    trip = context.user["trip"]
    player = game.get_player(sender, trip)
    msg_list = msg.split(" ")

    if msg == "rules":
        context.appText(SNAKE_RULE)
    elif msg == "help":
        context.appText(SNAKE_MENU)

    elif msg == "end" and player:
        game.end_game()
        context.appText("唔，结束了;;;;")
    elif msg_list[0] == "bot":
        if bank.offering_box in game.players:
            context.appText("BOT!!!!!!!😭")
            game.remove_player(game.get_player(sender, trip))
        else:
            context.appText("BOT!!!!!!!ヾ|≧_≦|〃")
            game.add_player(context.nick, bank.offering_box, bot=True)
    elif msg_list[0] == "join":
        game.add_player(sender, trip, msg[5:6])
    elif msg == "start":
        if game.status:
            context.appText("已经开始了")
        else:
            game.start()
    elif msg == "quit":
        game.remove_player(player)
    elif msg_list[0] == "flair" and player:
        try:
            flair = msg_list[1][:1]
        except:
            context.appText("...")
        else:
            player.flair = flair
            context.appText(f"成功更改标识为{flair}")

    elif game.status and player:
        if sender != player.name:
            player.name = sender
        game.play(player, msg)