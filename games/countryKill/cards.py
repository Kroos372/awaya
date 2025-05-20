import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core import Player, Game, Turn
from main import bocchi as game

def createCards(name, hearts=0, diamonds=0, spades=0, clubs=0, **kwargs) -> list:
    cards = []
    for _ in range(hearts):
        cards.append(Card(name, "红桃", **kwargs))
    for _ in range(diamonds):
        cards.append(Card(name, "方块", **kwargs))
    for _ in range(spades):
        cards.append(Card(name, "黑桃", **kwargs))
    for _ in range(clubs):
        cards.append(Card(name, "梅花", **kwargs))
    return cards

# 牌类
class Card:
    POINTS = ["A"] + list(str(i) for i in range(2, 11)) + list("JQK")
    COLORS = {
        "黑桃": "black",
        "梅花": "black",
        "红桃": "red",
        "方块": "red"
    }
    card_type: str
    name: str
    def __init__(self, suit: str):
        self.suit = suit
        self.color = self.COLORS[suit]
        self.point = random.choice(self.POINTS)
    def __str__(self):
        return f"【{self.name}】"
    def __int__(self):
        return self.POINTS.index(self.point) + 1
    def __eq__(self, value):
        return self.name == value
    def __getattr__(self, attr):
        return None
    def __lt__(self, other: "Card"):
        if self.name != other.name:
            return self.name < other.name
        elif self.suit != other.suit:
            return self.suit < other.suit
        else:
            return self.point < other.point
    # 主动使用
    def execute(self, turn: Turn, player: Player, **kwargs):
        game.appText(f"不能主动使用{self}")
    # 被动生效（或不被响应后生效）
    def effect(self, turn: Turn, player: Player, **kwargs):
        pass
    # 被响应
    def on_respond(self, turn: Turn, player: Player, **kwargs) -> bool:
        return False

class BasicCard(Card):
    card_type = "basic"

class TrickCard(Card):
    card_type = "trick"

class Equipment(Card):
    effect_time: str
    def equip(self, player: Player):
        game.appText(f"{player}装备了{self}")
    def unequip(self, player: Player):
        game.appText(f"{player}失去了{self}")

class Mount(Equipment):
    card_type = "mount"
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name

class Weapon(Equipment):
    card_type = "weapon"
    effect_time = "atk"
    effect_phase: str
    atk_range: int
    def __str__(self):
        return super().__str__() + f"(范围{self.atk_range})"

class Armor(Equipment):
    card_type = "armor"
    effect_time = "dfs"

class MinusMount(Mount):
    effect_time = "atk"
    def __str__(self):
        return super().__str__() + "(-1)"
    def effect(self, turn, player, **kwargs):
        turn.distance_required -= 1

class PlusMount(Mount):
    effect_time = "dfs"
    def __str__(self):
        return super().__str__() + "(+1)"
    def effect(self, turn, player, **kwargs):
        turn.distance_required += 1


# 牌堆类
class Deck(list[Card]):
    def __init__(self):
        self.trash = []
    # 初始化牌堆
    # 51杀, 14雷杀(黑), 8火杀(红), 38闪(红), 8酒, 20桃(红), 5决斗, 2桃园(红桃), 5乐不思蜀, 9铁锁(黑), 5南蛮(黑), 5火攻(红)
    # 10无懈可击, 4兵粮寸断(黑), 3五谷丰登(红桃), 9过河拆桥, 8顺手牵羊, 2万箭齐发(红桃), 3闪电, 3借刀杀人(梅花), 6无中生有(红桃)
    # 数的我自己的三国杀，去掉了以逸待劳、知己知彼、远交近攻，别问为什么
    # 花色比例乱写的
    def initCards(self) -> list:
        # 基本牌与锦囊牌
        self.extend(createCards("杀", 6, 10, 16, 19))
        self.extend(createCards("火杀", 3, 5))
        self.extend(createCards("雷杀", spades=6, clubs=8))
        self.extend(createCards("闪", 12, 26))
        self.extend(createCards("酒", 1, 2, 2, 3))
        self.extend(createCards("桃", 14, 6))
        self.extend(createCards("决斗", 1, 1, 1, 2, type="tip"))
        self.extend(createCards("桃园结义", 2, type="tip"))
        self.extend(createCards("乐不思蜀", 1, 1, 1, 2, type="tip"))
        self.extend(createCards("南蛮入侵", spades=3, clubs=2, type="tip"))
        self.extend(createCards("火攻", 3, 2, type="tip"))
        self.extend(createCards("无中生有", 6, type="tip"))
        # 这俩有点麻烦
        # self.extend(createCards("铁索连环", spades=4, clubs=5, type="tip"))
        # self.extend(createCards("无懈可击", 2, 2, 3, 3, type="tip"))
        self.extend(createCards("兵粮寸断", spades=2, clubs=2, type="tip"))
        self.extend(createCards("五谷丰登", 3, type="tip"))
        self.extend(createCards("过河拆桥", 1, 2, 3, 3, type="tip"))
        self.extend(createCards("顺手牵羊", 2, 3, 1, 2, type="tip"))
        self.extend(createCards("万箭齐发", 2, type="tip"))
        self.extend(createCards("闪电", 0, 1, 1, 1, type="tip"))
        self.extend(createCards("借刀杀人", clubs=3, type="tip"))
        # 装备牌
        self.extend(createCards("骅骝", diamonds=1, type="+1", horse=True))
        self.extend(createCards("爪黄飞电", hearts=2, type="+1", horse=True))
        self.extend(createCards("的卢", clubs=2, type="+1", horse=True))
        self.extend(createCards("绝影", spades=2, type="+1", horse=True))
        self.extend(createCards("大宛", spades=2, type="-1", horse=True))
        self.extend(createCards("赤兔", hearts=2, type="-1", horse=True))
        self.extend(createCards("紫骍", diamonds=2, type="-1", horse=True))
        self.extend(createCards("骅骝", diamonds=1, type="+1", horse=True))
        self.extend(createCards("骅骝", diamonds=1, type="+1", horse=True))

        self.extend(createCards("寒冰剑", spades=2, type="weapon", distance=2))
        self.extend(createCards("贯石斧", diamonds=2, type="weapon", distance=3))
        self.extend(createCards("朱雀羽扇", diamonds=2, type="weapon", distance=4))
        self.extend(createCards("雌雄双股剑", spades=2, type="weapon", distance=2))
        self.extend(createCards("吴六剑", diamonds=1, type="weapon", distance=2))
        self.extend(createCards("青缸剑", spades=2, type="weapon", distance=2))
        self.extend(createCards("青龙偃月刀", spades=1, type="weapon", distance=3))
        self.extend(createCards("古锭刀", spades=1, type="weapon", distance=2))
        self.extend(createCards("方天画戟", diamonds=1, type="weapon", distance=4))
        self.extend(createCards("丈八蛇矛", spades=2, type="weapon", distance=3))
        self.extend(createCards("诸葛连弩", diamonds=2, clubs=1, type="weapon", distance=1))
        self.extend(createCards("麒麟弓", hearts=2, type="weapon", distance=5))

        self.extend(createCards("白银狮子", clubs=2, type="armor"))
        self.extend(createCards("藤甲", clubs=3, type="armor"))
        self.extend(createCards("八卦阵", spades=3, type="armor"))
        self.extend(createCards("仁王盾", clubs=2, type="armor"))
        random.shuffle(self)
    # 弹出牌
    def pop_card(self, disacrd: bool=False) -> "Card":
        if not self:
            while self.trash:
                self.append(self.trash.pop())
            random.shuffle(self)
        card = self.pop()
        if disacrd:
            self.discard(card)
        return card
    # 加入弃置牌
    def discard(self, card) -> "Card":
        if not card.fake:
            self.trash.append(card)
        return card

# 玩家手牌类
class PlayerCards(list[Card]):
    def pop_card(self, index=-1):
        value = self[index]
        self[index] = None
        return value
    def remove_card(self, value):
        if value in self:
            index = self.index(value)
            self[index] = None
    def sweep(self):
        while None in self:
            self.remove(None)
    def __iter__(self):
        for item in super().__iter__():
            if item is not None: 
                yield item
    @property
    def length(self):
        return len([0 for i in self if i is not None])
