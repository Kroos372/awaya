from typing import TYPE_CHECKING
import random
from .const import Status

if TYPE_CHECKING:
    from .player import Player
    from .core import GameSystem

class Square:
    name: str
    type: str
    game: "GameSystem"
    position: int
    def __init__(self):
        self.players: list[Player] = []
    def __getattr__(self, name):
        return None
    @property
    def f_players(self) -> str:
        if self.players:
            flairs = ",".join(player.flair for player in self.players)
            return f"{{=={flairs}==}}"
        else:
            return ""
    @property
    def f_name(self) -> str:
        return str(self)

    def details(self) -> str:
        return "\n".join([
            f"#### {self.name}",
            "**位于该地块的玩家**：" + "，".join(player.name for player in self.players)
        ])

    def land_on(self, player: "Player"):
        pass

    def remove_player(self, player: "Player"):
        if player in self.players:
            self.players.remove(player)

    def __str__(self):
        return self.name + self.f_players + f"#{self.position}"
    

class Start(Square):
    position = 0
    name = "起点"
    type = "start"
    def land_on(self, player):
        player.add_cash(300)
        self.game.appText(f"{player}停靠在起点，获得$300")
   
    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "起点，一切斗争开始的地方。握好你们的钞票，准备占领整个地图吧！",
            "**功能**:",
            "路过起点会获得$200，停在起点会获得$300。"
        ])

class Treasure(Square):
    name = "宝藏"
    type = "treasure"
    events = [
        "进监狱",
        "获得1张赦免卡",
    
        "你的手机坏了。维修费$50",
        "你打赌输了。给每位玩家$50",
        "你的识别码泄露了。支付$60",
        "房产需要装修了。每间房屋支付$30，酒店支付$120",

        "彩票中了三等奖，获得$15",
        "生意赚了一笔。获得$25",
        "生日快乐！每位玩家给你$10",
        "你办了一个派对。向每位玩家收取$50装饰费",
        "挖出Mod。获得$100",
        "亲戚寄给你$100",
        "通过礼品卡获得$100",
        "你捡到了装着现金的钱包。获得$200"
    ]
    moneys = [
        0, 0, -50, 0, -60, 0, 15, 25, 0, 0, 100, 100, 100, 200
    ]
    def land_on(self, player):
        point = random.randint(0, len(self.events) - 1)
        text = f"{player}遇到了宝藏："
        self.game.appText(text + f"**{self.events[point]}**")
        if self.moneys[point]:
            player.add_cash(self.moneys[point])
        elif point == 0:
            player.goto_prison(self.game)
        elif point == 1:
            player.add_card()
        elif point == 3:
            for player_ in self.game.players:
                player.give_cash(player_, 50)
        elif point == 5:
            player.redesign_house(self.game, 30, 120)
        elif point == 8:
            for player_ in self.game.players:
                player_.give_cash(player, 10)
        elif point == 9:
            for player_ in self.game.players:
                player_.give_cash(player, 50)

    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "宝藏？还是说？",
            "**功能**:",
            "失去或获得金钱。"
        ])

class Surprise(Square):
    name = "惊喜"
    type = "surprise"
    events = [
        "前往下一个机场",
        "前往某个机场[5 15 25 35]",
        "前往下一个公司",
        "前往起点",
        "前往某个“首都”[3 9 14 19 24 29 34 39]",
        "后退三格",

        "你的亲戚需要一些经济援助。支付$50",
        "重新设计你的房产。每间房屋支付$25，酒店支付$100",

        "获得1张赦免卡",
        "缴税$20",
        "股票经纪公司向你支付$60的股息",
        "获得$100奖学金",
        "你有一笔新的投资。获得$150",
    ]
    moneys = [
        0, 0, 0, 0, 0, 0, -50, 0, 0, -20, 60, 100, 150
    ]
    texts = [1, 4]
    def land_on(self, player):
        point = random.randint(0, len(self.events) - 1)
        text = f"{player}遇到了惊喜："
        if point not in self.texts:
            self.game.appText(text + f"**{self.events[point]}**")
        if self.moneys[point]:
            player.add_cash(self.moneys[point])
        elif point == 0:
            player.advance_to(self.game, "airport")
        elif point == 1:
            airport = random.choice([5, 15, 25, 35])
            self.game.appText(text + f"**前往{self.game.board[airport].name}**")
            player.move_to(self.game, airport)
        elif point == 2:
            player.advance_to(self.game, "company")
        elif point == 3:
            player.move_to(self.game, 0)
        elif point == 4:
            caption = random.choice([3, 9, 14, 19, 24, 29, 34, 39])
            self.game.appText(text + f"**去{self.game.board[caption].name}旅行**")
            player.move_to(self.game, caption)
        elif point == 5:
            player.move(self.game, -3)
        elif point == 7:
            player.redesign_house(self.game, 25, 100)
        elif point == 8:
            player.add_card()

    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "猝不及防的突发状况也是人生不可或缺的一环。",
            "**功能**:",
            "遭遇各种事件。"
        ])

class Prison(Square):
    position = 10
    name = "监狱（经过）"
    type = "prison"
    def __str__(self):
        text = self.name
        plys = []
        for player in self.players:
            turn = player.in_prison_turn
            if not turn:
                plys.append(f"{player}(经过)")
            else:
                plys.append(f"{player}({turn})")
        if plys:
            plys = ",".join(plys)
            text += "{" + plys + "}"
        return text

    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "阴森的钢铁牢笼。",
            "**功能**:",
            "路过什么也不会发生。",
            "连续掷出3次双骰入狱",
            "进监狱后可 花费$50保释/使用赦免卡/投出两个相同点数 以出狱",
            "入狱3回合后将强制出狱"
        ])

class Vacation(Square):
    position = 20
    name = "度假"
    type = "vacation"
    def __str__(self):
        text = super().__str__()
        if self.game.settings.vacation_cash:
            text += f"(持有${self.game.vacation_cash})"
        return text
    def land_on(self, player):
        player.on_vacation = True
        self.game.appText(f"{player}去度假了，将跳过下一轮")
        self.game.status = Status.ENDING

    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "去海边。",
            "**功能**:",
            "去度假后将会跳过下一回合。"
        ])

class To_Prison(Square):
    position = 30
    name = "进监狱"
    type = "to_prison"
    def land_on(self, player):
        player.goto_prison(self.game)

    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "究竟是犯了什么错呢？",
            "**功能**:",
            "进监狱。"
        ])

class Tax(Square):
    type = "tax"
    def __init__(self, name: str, pay: float | int):
        super().__init__()
        self.name = name
        self.pay = pay
    
    def land_on(self, player):
        if self.pay < 1:
            self.game.pay_tax(player, round(player.cash * self.pay))
        else:
            self.game.pay_tax(player, self.pay)
    
    def __str__(self):
        if self.pay < 1:
            return self.name + f"({self.pay * 100}%)" + f"#{self.position}"
        else:
            return self.name + f"(${self.pay})" + f"#{self.position}"

    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "做守法公民。",
            "**功能**:",
            "缴税。"
        ])

class Earth(Square):
    price: int
    position: int
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.owner: Player = None
        self.mortgaged: bool = False # 抵押获得50%，赎回支付55%

    def __str__(self):
        text = super().__str__()
        if self.mortgaged:
            text += "(抵)"
        if self.owner:
            text += "@" + self.owner.flair
        return text
    
    def __lt__(self, other: "Land | Airport | Company"):
        if self.type != other.type:
            return self.type < other.type
        elif self.type == "land" and self.country != other.country:
            return self.country < other.country
        else:
            return self.name < other.name

    @property
    def f_name(self) -> str:
        return self.name + f"#{self.position}"

    def mortgage(self, game: "GameSystem"):
        if not game.settings.mortgage:
            game.appText("未启用抵押")
            return

        self.mortgaged = not self.mortgaged
        if self.mortgaged:
            price = self.price * 0.5
            self.owner.add_cash(price)
            game.appText(f"抵押成功，获得${price}")
        else:
            price = self.price * 0.55
            self.owner.del_cash(price)
            game.appText(f"赎回成功，支付${price}")
    
    def land_on(self, player):
        if not self.owner:
            self.game.appText(f"可购买此地(${self.price})")
            return False
        elif self.owner == player:
            return False
        return True

    def change_owner(self, player: "Player"):
        if self.owner:
            self.owner.lands.remove(self)
        player.lands.append(self)
        self.owner = player

    def details(self) -> str:
        return "\n".join([
            super().details(),
            f"**所有者**：{self.owner or ''}",
            f"**地价**：${self.price}",
        ])

class Land(Earth):
    type = "land"
    def __init__(self, country: str, name: str, price: int, house_price: int, tolls: list):
        super().__init__(name)
        self.country = country
        self.name = name
        self.price = price
        self.house_price = house_price
        self.tolls = tolls

        self.houses: int = 0
    @property
    def toll(self) -> int:
        return self.tolls[self.houses]
    @property
    def f_name(self) -> str:
        return f"【{self.country}】{self.name}#{self.position}"
    @property
    def f_houses(self) -> str:
        if not self.houses:
            return ""
        if self.houses == 5:
            return "酒店"
        else:
            return f"{self.houses}房"
    def __str__(self):
        text = f"{self.country[0]}." + super().__str__()
        return text + f" {self.f_houses}"

    def mortgage(self):
        if self.houses:
            self.game.appText("当前地产有房子，不能抵押")
            return
        super().mortgage(self.game)

    def land_on(self, player: "Player"):
        if not super().land_on(player):
            return
        player.give_cash(self.owner, self.toll)
        self.game.appText(f"{player} 向 {self.owner} 支付了 ${self.toll} 过路费")

    def details(self) -> str:
        return "\n".join([
            super().details(),
            f"**房价**：${self.house_price}",
            f"**房产**：${self.f_houses}",
            "**描述**:",
            "出于某些神秘原因变得很便宜的土地。",
            "**过路费**:",
            f"拥有地皮：${self.tolls[0]}",
            f"拥有1座房屋：${self.tolls[1]}",
            f"拥有2座房屋：${self.tolls[2]}",
            f"拥有3座房屋：${self.tolls[3]}",
            f"拥有4座房屋：${self.tolls[4]}",
            f"拥有酒店(5座房屋)：${self.tolls[5]}",
        ])

class Airport(Earth):
    type = "airport"
    price = 200
    def land_on(self, player: "Player"):
        if not super().land_on(player):
            return
        airs = self.owner.get_land_num(self.type)
        price = 25 * 2 ** (airs - 1)
        player.give_cash(self.owner, price)
        self.game.appText(f"{player} 向 {self.owner} 支付了 ${price} 过路费（{airs}座机场）")

    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "芜湖起飞。",
            "**过路费**:",
            "拥有1座时：$25",
            "拥有2座时：$50",
            "拥有3座时：$100",
            "拥有4座时：$200",
        ])

class Company(Earth):
    type = "company"
    price = 150
    def __init__(self, name: str):
        super().__init__(name)
        self.owner: Player = None
        self.mortgaged: bool = False
    def land_on(self, player: "Player"):
        if not super().land_on(player):
            return
        companies = self.owner.get_land_num(self.type)
        if companies == 1:
            price = self.game.dice_point * 4
        else:
            price = self.game.dice_point * 10
        player.give_cash(self.owner, price)
        self.game.appText(f"{player} 向 {self.owner} 支付了 ${price} 过路费（{companies}家工厂）")

    def details(self) -> str:
        return "\n".join([
            super().details(),
            "**描述**:",
            "工厂。",
            "**过路费**:",
            "拥有1座时：投出的点数 * $4",
            "拥有2座时：投出的点数 * $10",
        ])

# 净40格
class Board(list[Square]):
    def __init__(self):
        super().__init__()
        self.full_map: list[list[str | Square]]

    def new_map(self):
        self.clear()
        self.extend([
            Start(),
            Land("阿瓦兰", "YC", 60, 50, [2, 10, 30, 90, 160, 250]),
            Treasure(),
            Land("阿瓦兰", "兰枝", 60, 50, [4, 20, 60, 180, 320, 450]),
            Tax("所得税", 0.1),
            Airport("AWL机场"),
            Land("以色列", "特拉维夫", 100, 50, [6, 30, 90, 270, 400, 550]),
            Surprise(),
            Land("以色列", "海法", 100, 50, [6, 30, 90, 270, 400, 550]),
            Land("以色列", "耶路撒冷", 120, 50, [8, 40, 100, 300, 450, 600]),

            Prison(),
            Land("意大利", "威尼斯", 140, 100, [10, 50, 150, 450, 625, 750]),
            Company("电力公司"),
            Land("意大利", "米兰", 140, 100, [10, 50, 150, 450, 625, 750]),
            Land("意大利", "罗马", 160, 100, [12, 60, 180, 500, 700, 900]),
            Airport("MUC机场"),
            Land("德国", "法兰克福", 180, 100, [14, 70, 200, 550, 750, 950]),
            Treasure(),
            Land("德国", "慕尼黑", 180, 100, [14, 70, 200, 550, 750, 950]),
            Land("德国", "柏林", 200, 100, [16, 80, 220, 600, 800, 1000]),

            Vacation(),
            Land("中国", "深圳", 220, 150, [18, 90, 250, 700, 875, 1050]),
            Surprise(),
            Land("中国", "北京", 220, 150, [18, 90, 250, 700, 875, 1050]),
            Land("中国", "上海", 240, 150, [20, 100, 300, 750, 925, 1100]),
            Airport("CDG机场"),
            Land("法国", "里昂", 260, 150, [22, 110, 330, 800, 975, 1150]),
            Land("法国", "图卢兹", 260, 150, [22, 110, 330, 800, 975, 1150]),
            Company("自来水公司"),
            Land("法国", "巴黎", 280, 150, [24, 120, 360, 850, 1025, 1200]),
            
            To_Prison(),
            Land("英国", "利物浦", 300, 200, [26, 130, 390, 900, 1100, 1275]),
            Land("英国", "曼彻斯特", 300, 200, [26, 130, 390, 900, 1100, 1275]),
            Treasure(),
            Land("英国", "伦敦", 320, 200, [28, 150, 450, 1000, 1200, 1400]),
            Airport("JFK机场"),
            Surprise(),
            Land("美国", "旧金山", 350, 200, [35, 175, 500, 1100, 1300, 1500]),
            Tax("奢侈品税", 75),
            Land("美国", "纽约", 400, 200, [50, 200, 600, 1400, 1700, 2000]),
        ])

    def fresh(self, game: "GameSystem"):
        self.new_map()
        for i, square in enumerate(self):
            square.game = game
            square.position = i
        self.full_map = [[""] * 11 for _ in range(11)]
        self.load_full_map()
    
    def load_full_map(self):
        # 从左到右
        for i in range(10):
            self.full_map[0][i] = self[i]
            self.full_map[1][i] = "→"
        # 从上到下
        for i in range(10):
            self.full_map[i][10] = self[10 + i]
            self.full_map[10 - i][9] = "↓"
        # 从右到左
        for i in range(10):
            self.full_map[10][10 - i] = self[20 + i]
            self.full_map[9][i] = "←"
        # 从下到上
        for i in range(10):
            self.full_map[10 - i][0] = self[30 + i]
        for i in range(2, 10):
            self.full_map[i][1] = "↑"

    def __str__(self) -> str:
        text = ["|" * 12, "|" + ":-:|" * 11]
        for line in self.full_map:
            msg = [""]
            for sq in line:
                msg.append(str(sq))
            msg.append("")
            text.append("|".join(msg))
        return "\n".join(text)
    
    def get_country(self, country: str) -> list[Square]:
        lands = []
        for land in self:
            if land.type == "land" and land.country == country:
                lands.append(land)
        return lands