from typing import TYPE_CHECKING
from .board import Prison
from .const import Status, DICES
import random

if TYPE_CHECKING:
    from .board import Square, Land
    from .core import GameSystem

class Player:
    is_bot: bool
    def __init__(self, name: str, trip: str, flair: str):
        self.trip = trip
        self.name = name
        self.flair = flair

        self.position: int = 0
        self.cash: int = 0
        self.parden_card: int = 0
        self.lands: list["Land"] = []

        self.on_vacation: bool = False
        self.in_prison_turn: int = 0
        
        self.auto_end: bool = False
    
    def __str__(self):
        return self.name
    def __eq__(self, value):
        if self.trip:
            return self.trip == value
        else:
            return self.name == value
    
    def get_square(self, game: "GameSystem") -> "Square":
        return game.board[self.position]
    def get_land_num(self, type_: str) -> int:
        num = 0
        for land in self.lands:
            if land.type == type_:
                num += 1
        return num
    def owns_country(self, game: "GameSystem", country: str) -> bool:
        lands: list["Land"] = game.board.get_country(country)
        for land in lands:
            if land.owner != self:
                return False
        return True

    def format(self) -> str:
        self.lands.sort()
        text = [
            f"### {self}({self.flair})",
            f"坐标：{self.position}",
            f"现金：**${self.cash}**",
            "**地产**:",
            "、".join(land.f_name for land in self.lands)
        ]
        if self.parden_card:
            text.insert(3, f"赦免卡：{self.parden_card}")
        if self.on_vacation:
            text.insert(3, "**度假中**")
        elif self.in_prison_turn:
            text.insert(3, f"**狱中**：{self.in_prison_turn}回合")
        return "\n".join(text)

    def del_cash(self, num: int):
        self.cash = round(self.cash - num)
    def add_cash(self, num: int):
        self.cash = round(self.cash + num)
    def give_cash(self, player: "Player", num: int):
        self.del_cash(num)
        player.add_cash(num)
    def del_card(self, num: int=1):
        self.parden_card -= num
    def add_card(self, num: int=1):
        self.parden_card += num
    
    def roll(self, game: "GameSystem", num: int=2) -> bool:
        """返回值: 是否双骰"""
        rolls = [random.randint(1, 6) for _ in range(num)]
        result = []
        for point in rolls:
            result.append(DICES[point])
        result = ",".join(result)
        
        sum_ = sum(rolls)
        game.dice_point = sum_
        game.appText(f"{self} 掷出了 {result}({sum_})")
        game.appText("————")
        if rolls[0] == rolls[1]:
            game.appText(f"{self} 掷出了双骰，请再掷一次")
            game.doubled += 1
            return True
        return False

    def move(self, game: "GameSystem", step: int, teleport: bool=False):
        self.get_square(game).remove_player(self)
        if teleport:
            self.position = (self.position + step) % 40
        else:
            if step >= 0:
                direction = 1
            else:
                direction = -1
            for i in range(abs(step)):
                self.position = (self.position + direction) % 40
                if game.board[self.position].type == "start" and i != step - 1:
                    self.add_cash(200)
                    game.appText(f"{self}经过起点，获得$200")
        square: "Land" = self.get_square(game)
        game.appText(f"{self} 移动到了【{square.f_name}】")
        square.players.append(self)
        game.appText("————")
        square.land_on(self)

    def move_to(self, game: "GameSystem", position: int, teleport: bool=False):
        self.get_square(game).remove_player(self)
        if not teleport and position != 0 and position < self.position:
            self.add_cash(200)
            game.appText(f"{self}经过起点，获得$200")
        self.position = position
        self.move(game, 0, True)

    def advance_to(self, game: "GameSystem", type_: str):
        self.get_square(game).remove_player(self)
        for _ in range(40):
            self.position = (self.position + 1) % 40
            if game.board[self.position].type == type_:
                break
        self.move(game, 0, True)
    
    def goto_prison(self, game: "GameSystem"):
        self.in_prison_turn = 1
        self.move_to(game, Prison.position, True)
        game.appText(f"{self}被关进了监狱")
        game.status = Status.ENDING
    
    
    def build_house(self, game: "GameSystem", position: int, num: int=1):
        try:
            assert position >= 0 and position < 40 and game.board[position].type == "land"
            assert num > 0
        except:
            game.appText("参数错误")
            return
        land: "Land" = game.board[position]
        if not (land.owner == self and self.owns_country(game, land.country)):
            game.appText(f"你没有完整的【{land.country}】")
            return
        if land.houses + num > 5:
            game.appText("数量错误")
            return
        price = land.house_price * num
        if price > self.cash:
            game.appText("金钱不够")
            return
        
        land.houses += num
        self.del_cash(price)
        game.appText(f"在**{land.f_name}**购买了{num}间房屋，花费${price}")
        game.appText(f"当前有{land.f_houses}，剩余${self.cash}")
    
    def destroy_house(self, game: "GameSystem", position: int, num: int=1):
        try:
            assert position >= 0 and position < 40 and game.board[position].type == "land"
            assert num > 0
        except:
            game.appText("参数错误")
            return
        land: "Land" = game.board[position]
        if not (land.owner == self and self.owns_country(game, land.country)):
            game.appText(f"你没有完整的【{land.country}】")
            return
        if land.houses - num < 0:
            game.appText("数量错误")
            return

        price = land.house_price * num / 2
        land.houses -= num
        self.add_cash(price)
        game.appText(f"卖出**{land.f_name}**的{num}间房屋，获得${price}")
        game.appText(f"当前有{land.f_houses}，剩余${self.cash}")
    
    def buy_land(self, game: "GameSystem"):
        land: "Land" = self.get_square(game)
        if not land.price:
            game.appText("这边是非卖品呢亲")
            return
        if land.owner:
            game.appText("这位已经有主人了")
            return
        if self.cash < land.price:
            game.appText("等有钱再说吧")
            return
        
        land.change_owner(self)
        self.del_cash(land.price)
        game.appText(f"成功购买**{land.f_name}**，花费${land.price}")
        game.appText(f"剩余${self.cash}")
    
    def redesign_house(self, game: "GameSystem", house: int, hotel: int):
        tax = 0
        for land in self.lands:
            if not land.houses:
                continue
            if self.houses == 5:
                tax += hotel
            else:
                tax += land.houses * house
        self.del_cash(tax)
        game.appText(f"{self} 共支付 ${tax}")
    
    def sell_land(self, game: "GameSystem", position: int):
        try:
            assert position >= 0 and position < 40 and game.board[position].price
        except:
            game.appText("参数错误")
            return
        land: "Land" = game.board[position] # 或者机场、工厂
        if land.owner != self:
            game.appText("总而言之，先打下它再说吧")
            return
        if land.houses:
            game.appText("这里还有房子没拆")
            return

        land.owner = None
        self.lands.remove(land)
        price = land.price / 2
        self.add_cash(price)
        game.appText(f"成功卖出**{land.f_name}**，获得${price}")
        game.appText(f"剩余${self.cash}")

    def mortgage(self):
        pass