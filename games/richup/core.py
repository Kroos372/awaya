from static import Awaish, namePure
from .board import Board
from .player import Player
from .const import Status, Settings
from .trade import TradeSystem
import random

class GameSystem:
    def __init__(self):
        self.context: Awaish = None
        self.status = Status.CLOSED

        self.board: Board = Board()
        self.settings: Settings = Settings()
        self.trade_system: TradeSystem = TradeSystem(self)
        
        self.players: list[Player] = []
        self.dice_point: int = 0
        self.player_index: int
        
        self.doubled: int = 0
        self.vacation_cash: int = 0

    @property
    def current_player(self):
        return self.players[self.player_index]
    
    def get_player(self, nick: str="", trip: str="") -> Player | None:
        for player in self.players:
            if ((trip and player.trip == trip) or
                (not player.trip and player.name == nick)):
                return player
    def simple_get_player(self, nick: str="", trip: str="") -> Player | None:
        for player in self.players:
            if player.name == nick or (player.trip and player.trip == trip):
                return player

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
            self.players.append(Player(nick, trip, flair))
        else:
            # self.players.append(AutoBot(nick, trip, flair))
            pass
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
    
    def set_context(self, context: Awaish):
        if not self.context:
            self.context = context

    def appText(self, text: str, type_: str="", **kwargs):
        self.context.appText(text.replace("$", "\\$"), type_, **kwargs)
    
    def pay_tax(self, player: Player, num: int):
        if self.settings.vacation_cash:
            self.vacation_cash = round(self.vacation_cash + num)
        player.del_cash(num)
        self.appText(f"{player}缴了${num}的税")


    def _next_player(self):
        if self.status:
            self.player_index = (self.player_index + 1) % len(self.players)
            current_player = self.current_player
            self.appText(f"轮到 @{current_player}")
            
            if current_player.on_vacation:
                self.appText(f"{current_player} 度假很愉快，这轮先不要打扰他/她")
                current_player.on_vacation = False
                self._next_player()
            else:
                self.status = Status.BEFORE_ROLL
                self.doubled = 0

    def _format_order(self) -> str:
        text = []
        for i, player in enumerate(self.players):
            if i == self.player_index:
                text.append(f"=={player}==")
            else:
                text.append(player.name)
        return " -> ".join(text)
    def _format_all(self) -> str:
        text = []
        for player in self.players:
            text.append(f"**{player}({player.flair})**：坐标{player.position} 现金${player.cash}")
        return "\n".join(text)
    
    def bankrupt(self, player: Player):
        self.appText(f"{player} 宣告了破产😭😭😭")
        for land in player.lands:
            land.owner = None
        self.board[player.position].players.remove(player)
        self.players.remove(player)
        
        if len(self.players) == 1:
            self.appText(f"{self.players[0]}成为了大富翁！🍾🍾🍾")
            self.end_game()
        else:
            self.player_index -= 1
            self._next_player()

    def play(self, player: Player, msg: str):
        msg_list = msg.split(" ")
        if msg_list[0] == "board":
            text = self._format_order() + "\n" + str(self.board)
            if len(msg_list) > 1 and msg_list[1] == "w":
                self.appText(text, "whisper", to=player.name)
            else:
                self.appText(text)
            return
        if msg_list[0] == "check":
            try:
                player_ = self.simple_get_player(namePure(msg_list[1]))
                if player_ is not None:
                    player = player_
            except:
                pass
            self.appText(player.format())
            return
        if msg == "all":
            self.appText(self._format_all())
            return
        if msg_list[0] == "help":
            try:
                position = int(msg_list[1])
                square = self.board[position]
            except:
                self.appText("参数错误")
                return
            self.appText(square.details())
            return
        if msg == "gg":
            self.bankrupt(player)
            return
        if msg == "auto":
            player.auto_end = not player.auto_end
            self.appText(f"更改成功，当前自动结束值为：{player.auto_end}")
            return
    
        elif msg_list[0] == "trade":
            try:
                target_player = self.simple_get_player(namePure(msg_list[1]))
                assert target_player and target_player != player
            except:
                self.appText("参数错误")
                return
            self.trade_system.create(player, target_player, " ".join(msg_list[2:]))
            return
        elif msg_list[0] == "accept":
            try:
                trade_id = msg_list[1]
            except:
                self.appText("参数错误")
                return
            self.trade_system.accept(player, trade_id)
            return
        elif msg_list[0] == "decline":
            try:
                trade_id = msg_list[1]
            except:
                self.appText("参数错误")
                return
            self.trade_system.decline(player, trade_id)
            return
        elif msg_list[0] == "tradeof":
            try:
                trade_id = msg_list[1]
            except:
                self.appText("参数错误")
                return
            self.appText(self.trade_system.format(trade_id))
            return
        elif msg == "mytrades":
            try:
                player = self.simple_get_player(namePure(msg_list[1]))
            except:
                pass
            self.appText(self.trade_system.trade_of(player))

        if player != self.current_player:
            self.appText(f"现在是{self.current_player}的回合")
            return
        
        if msg == "r":
            if self.status > Status.BEFORE_DOUBLE:
                self.appText("你这回合已经摇过骰子了")
                return
            doubled = player.roll(self)
            self.status = Status.AFTER_ROLL
            if not player.in_prison_turn:
                if doubled:
                    if self.doubled == 3:
                        self.appText(f"{player}连续掷出3次双骰，被怀疑开了，特此保送监狱")
                        player.goto_prison(self)
                        return
                    else:
                        self.status = Status.BEFORE_DOUBLE

                player.move(self, self.dice_point)
                square = player.get_square(self)
                if self.status == Status.ENDING:
                    self._next_player()
                elif self.status != Status.BEFORE_DOUBLE:
                    if player.auto_end:
                        self.play(player, ".")
                    else:
                        self.appText(f"@{player} 请继续操作")
            # 在狱中
            else:
                if doubled:
                    player.in_prison_turn = 0
                    self.appText(f"{player}奇迹般地掷出双骰，保送出狱")
                    player.move(self, self.dice_point)
                elif player.in_prison_turn >= 3:
                    player.in_prison_turn = 0
                    self.appText(f"{player}坐满3回合牢，终于出狱了")
                else:
                    player.in_prison_turn += 1
                    self.appText(f"{player}没能出狱")
                self._next_player()
        elif msg == ".":
            if self.status < Status.AFTER_ROLL:
                self.appText("请先掷骰子")
                return
            if player.cash < 0:
                self.appText("请先让资产为正")
                return
            self.appText(f"{player} 结束了回合")
            self._next_player()
        elif msg == "out":
            if not player.in_prison_turn:
                self.appText("你现在的首要任务是先找办法把自己弄进去")
                return
            if player.parden_card:
                player.parden_card -= 1
                player.in_prison_turn = 0
                self.appText(f"{player}用一张赦免卡出狱了")
                self._next_player()
            elif player.cash >= 50:
                player.del_cash(50)
                player.in_prison_turn = 0
                self.appText(f"{player} V我$50出狱了")
                self._next_player()
            else:
                self.appText("对不起，做不到")
        
        elif msg == "buy":
            if self.status == Status.BEFORE_ROLL:
                self.appText("请先掷骰子")
                return
            player.buy_land(self)
        elif msg_list[0] == "sell":
            try:
                position = int(msg_list[1])
            except:
                self.appText("参数错误")
                return
            player.sell_land(self, position)
        elif msg_list[0] == "build":
            try:
                position = int(msg_list[1])
                if len(msg_list) > 2:
                    num = int(msg_list[2])
                else:
                    num = 1
            except:
                self.appText("参数错误")
                return
            player.build_house(self, position, num)
        elif msg_list[0] == "destroy":
            try:
                position = int(msg_list[1])
                if len(msg_list) > 2:
                    num = int(msg_list[2])
                else:
                    num = 1
            except:
                self.appText("参数错误")
                return
            player.destroy_house(self, position, num)

    def start(self):
        if len(self.players) < 2:
            self.context.appText("至少两人才能开始")
            return

        self.status = Status.BEFORE_ROLL
        self.board.fresh(self)
        random.shuffle(self.players)
        self.player_index = 0

        for player in self.players:
            self.board[0].players.append(player)
            player.cash = self.settings.start_cash
        for square in self.board:
            square.game = self

        self.context.appText(self._format_order())
        self.context.appText(f"由@{self.current_player} 开始")

    def end_game(self):
        self.players = []
        self.status = Status.CLOSED
        self.settings = Settings()
        self.trade_system.clear()
        self.vacation_cash = 0
        self.doubled = 0