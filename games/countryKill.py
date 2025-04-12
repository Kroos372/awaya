import random

## 名字提纯
def namePure(name: str) -> str:
    return name.strip("@").strip()

# [0游戏开关, 1[玩家列表], 2{玩家: Player对象}]
countryKill = [False, [], {}]

POINTS = ["A"] + list(range(2, 11)) + list("JQK")
BLACK, RED = ["黑桃", "梅花"], ["红桃", "方块"]
# [[处于“连环状态”的玩家]]
chained = []
# 当前轮次状态
nowTurn = {
    # player: str, # 此回合轮到的玩家
    # dodged: bool, # 最近的杀是否被闪避
    # killed: bool, # player是否出过杀
    # cmd: str, # 操作，如杀、决斗、过河拆桥或装备牌技能
    # target: List[str], # 操作目标
    # temp: List[str], # 一些延时生效的效果参数，比如造成三尖两刃刀选择的多名目标
    # wait: bool, # 是否等待响应（是否可以继续出牌）
}

# 都是牌上写的，有争议别找我
def createDescription(text, author) -> str:
    return "\n".join([f">“{text}”", f">——{author}", "", ""])
DESCRIPTION = {
    # 锦囊
    "桃园结义": createDescription(
        "既结为兄弟，则同心协力，救困扶危；上报国家，下安黎庶；不求同年同月同日生，只愿同年同月同日死。皇天后土，实鉴此心，背义忘恩，天人共戮。",
        "《三国演义》"
    ),
    "铁索连环": createDescription(
        "或三十为一排，或五十为一排，首尾用铁环连锁，上铺阔板，休言人可渡，马亦可走矣。乘此而行，任他风浪潮水上下，复何惧哉？",
        "《三国演义》"
    ),
    "火攻": createDescription(
        "行火必有因，烟火必素具。",
        "《孙子·火攻》"
    ),
    "无懈可击": createDescription(
        "击其懈怠，出其空虚。",
        "曹操"
    ),
    "无中生有": createDescription(
        "天下万物生于有，有生于无。",
        "《老子》"
    ),
    "过河拆桥": createDescription(
        "你休得顺水推船，偏不许我过河拆桥。",
        "康进之"
    ),
    "南蛮入侵": createDescription(
        "南蛮一人持矛入侵，川兵百人见而奔逃。",
        "无名氏"
    ),
    "五谷丰登": createDescription(
        "是故风雨时节，五谷丰熟，社稷安宁。",
        "《六韬·龙韬·立将》"
    ),
    "万箭齐发": createDescription(
        "安得夫差水犀手，三千强弩射潮低。",
        "苏东坡"
    ),
    "顺手牵羊": createDescription(
        "效马效羊者右牵之。",
        "《礼记·曲礼上》"
    ),
    "借刀杀人": createDescription(
        "敌已明，友未定，引友杀敌，不自出力，以《损》推演。",
        "《三十六计》"
    ),
    # 装备
    "紫骍": createDescription(
        "怀夏后之九代，想陈王之紫骍。",
        "《梁书·张率传》"
    ),
    "绝影": createDescription(
        "公所乘马名绝影。",
        "《三国志·魏书》"
    ),
    "赤兔": createDescription(
        "人中吕布，马中赤兔！",
        "《三国演义》"
    ),
    "的卢": createDescription(
        "备急曰：‘的卢，今日危矣，可努力。’的卢乃一踊三丈，遂得过。",
        "《世语》"
    ),
    "爪黄飞电": createDescription(
        "操骑爪黄飞电马，引十万之众，与天子猎于许田。",
        "《三国演义》"
    ),
    "大宛": createDescription(
        "大宛汗血古共知，青海龙种骨更奇，网丝旧画昔尝见，不意人间今见之。",
        "《天马歌》"
    ),
    # 除了骅骝都是两张
    "骅骝": createDescription(
        "枥下骅骝思鼓角，门前老将识风云。",
        "《上将行》"
    ),

    "贯石斧": createDescription(
        "斧，甫也，甫，始也。凡将制器，始用斧伐木，已乃制之也。",
        "《释名·释用器》"
    ),
    "雌雄双股剑": createDescription(
        "又名鸳鸯剑，鸳剑长三尺七寸，鸯剑长三尺四寸，利可断金。",
        "《三国演义》"
    ),
    "吴六剑": createDescription(
        "吴大皇帝有宝剑六，一曰白虹，二曰紫电，三曰辟邪，四曰流星，五曰青冥，六曰百里。",
        "《古今连》"
    ),
    "青缸剑": createDescription(
        "云乃拔青缸剑乱砍，手起处，衣甲平过，血如涌泉。",
        "《三国演义》"
    ),
    "青龙偃月刀": createDescription(
        "刀势既大，其三十六刀法，兵仗遇之，无不屈者，刀类中以此为第一。",
        "《三才图会·器用》"
    ),
    "麒麟弓": createDescription(
        "虎筋弦响弓开处，雕羽翅飞箭到时。",
        "《三国演义》"
    ),
    "诸葛连弩": createDescription(
        "又损益连弩，谓之元戎，以铁为矢，矢长八寸，一弩十矢俱发。",
        "《魏氏春秋》"
    ),
    "丈八蛇矛": createDescription(
        "马上所持，言其矟矟便杀也；又曰激矛，激，截也，可以激截敌阵之矛也。",
        "《释名·释兵》"
    ),
    "方天画戟": createDescription(
        "豹子尾摇穿画戟，雄兵十万脱征衣。",
        "《三国演义》"
    ),

    "藤甲": createDescription(
        "穿在身上，渡江不沉，经水不湿，刀箭皆不能入...",
        "《三国演义》"
    ),
    "八卦阵": createDescription(
        "乾三连，坤六断，震仰盂，艮覆碗，离中虚，坎中满，兑上缺，巽下断。",
        "《八卦歌诀》"
    )
}
USAGE = {
    "决斗": "出牌阶段，对一名其他角色使用。由该角色开始，你与其轮流打出一张【杀】，首先不出【杀】的一方受到另一方造成的1点伤害。",
    "桃园结义": "出牌阶段，对所有角色使用。每名目标角色回复1点体力。",
    "铁索连环": "\n".join([
        "出牌阶段，指定一至两名角色，分别使其处于“连环状态”。",
        "重铸：出牌阶段，你可以将此牌置入弃牌堆，然后摸一张牌。",
        "注：此牌规则比较复杂，有问题可以百度。"
    ]),
    "火攻": "出牌阶段，对一名有手牌的角色使用。该角色展示一张手牌，然后若你弃置一张与所展示牌相同花色的手牌，则【火攻】对其造成1点火焰伤害。",
    "无懈可击": "抵消目标锦囊牌对一名角色产生的效果，或抵消另一张【无懈可击】产生的效果。",
    "无中生有": "出牌阶段，对你使用。摸两张牌。",
    "闪电": "出牌阶段，对你使用。将【闪电】放置于你的判定区里。若判定结果为♠2~9，则目标角色受到3点雷电伤害。若判定不为此结果，将之移动到下家的判定区里。",
    "过河拆桥": "出牌阶段，对一名区域内有牌的其他角色使用。你将其区域内的一张牌弃置。",
    "南蛮入侵": "出牌阶段，对所有其他角色使用。每名目标角色需打出一张【杀】，否则受到1点伤害。",
    "乐不思蜀": "出牌阶段，对一名其他角色使用。将【乐不思蜀】放置于该角色的判定区里，若判定结果不为♥，则跳过其出牌阶段。",
    "兵粮寸断": "出牌阶段，对距离为1的一名其他角色使用。将【兵粮寸断】放置于该角色的判定区里，若判定结果不为♣，则跳过其摸牌阶段。",
    "五谷丰登": "出牌阶段，对所有角色使用。你从牌堆亮出等同于现存角色数量的牌，每名目标角色选择并获得其中的一张。",
    "万箭齐发": "出牌阶段，对所有其他角色使用。每名目标角色需打出一张【闪】，否则受到1点伤害。",
    "顺手牵羊": "出牌阶段，对距离为1且区域内有牌的一名其他角色使用。你获得其区域内的一张牌。",
    "借刀杀人": "出牌阶段，对装备区里有武器牌的一名其他角色使用。该角色需对其攻击范围内，由你指定的一名角色使用一张【杀】，否则将装备区里的武器牌交给你。",

    "三尖两刃刀": "攻击范围：3。你使用【杀】对目标角色造成伤害后，可弃置一张手牌并对该角色距离1的另一名角色造成1点伤害。",
    "朱雀羽扇": "攻击范围：4。你可以将一张普通【杀】当具火焰伤害的【杀】使用。",
    "雌雄双股剑": "攻击范围：2。当你使用【杀】指定一名异性角色为目标后，你可以令其选择一项：弃置一张手牌；或令你摸一张牌。",
    "贯石斧": "攻击范围：3。当你使用的【杀】被【闪】抵消时，你可以弃置两张牌，则此【杀】依然造成伤害。",
    "寒冰剑": "攻击范围：2。当你使用的【杀】对目标角色造成伤害时，若该角色有牌，你可以防止此伤害，改为依次弃置其两张牌。",
    "吴六剑": "攻击范围：2。锁定技，与你势力相同的其他角色攻击范围+1。\n注：目前还没写武将牌，所以此技能没用。",
    "青缸剑": "攻击范围：2。锁定技，当你使用【杀】指定一名角色为目标后，无视其防具。",
    "古锭刀": "攻击范围：2。锁定技，当你使用【杀】对目标角色造成伤害时，若其没有手牌，此伤害+1。",
    "青龙偃月刀": "攻击范围：3。当你使用的【杀】被【闪】抵消时，你可以对相同的目标再使用一张【杀】。",
    "麒麟弓": "攻击范围：5。当你使用【杀】对目标角色造成伤害时，你可以弃置其装备区里的一张坐骑牌。",
    "诸葛连弩": "攻击范围：1。出牌阶段，你可以使用任意数量的【杀】。",
    "方天画戟": "攻击范围：4。当你使用【杀】时，且此【杀】是你最后手牌，你可以额外指定至多两个目标。",
    "丈八蛇矛": "攻击范围：3。你可以将两张手牌当【杀】使用或打出。",

    "白银狮子": "锁定技，当你受到伤害时，若该伤害多于1点，则防止多余的伤害；当你失去装备区里的【白银狮子】时，你回复1点体力。",
    "藤甲": "锁定技，【南蛮入侵】、【万箭齐发】和普通【杀】对你无效。当你受到火焰伤害时，此伤害+1。",
    "仁王盾": "锁定技，黑色的【杀】对你无效。",
    "八卦阵": "每当你需要使用或打出一张【闪】时，你可以进行一次判定：若判定结果为红色，则视为你使用或打出了一张【闪】。"
}
HELP = "\n".join([
    "三国杀！（建议先了解玩法）",
    "sgs: 加入一场游戏",
    "sgs t: 在开始之前退出游戏。",
    "开始s: 开始一场游戏。"
])
RULE = "\n".join([
    "行牌规则：",
    "s <牌的序号> <参数>, 如==s 1 @Krs_==, ==s 4 Krs_ awa_ya==。以下是注意事项：",
    "出掉一张牌后，后面的牌序号将自动-1",
    "顺手牵羊，过河拆桥等牌的第二个参数可指定装备牌名称或手牌序号",
    "重铸铁锁连环发送==s <序号> 重铸==",
    "不出牌或无法出牌发送=s .==, 进行选择发送==s <序号>==",
    "弃牌阶段发送==s . <序号1> <序号2>==等",
    "使用==s help <牌名>==查看卡牌的描述, ==s check==查看自己当前的牌, ==s all==查看所有人的牌",
    "注: 不能悔牌，出牌前请注意距离、防具等属性。"
])
# 玩家类
class Player:
    def __init__(self, name, gender, maxLife, cards):
        # 昵称
        self.name = name # 昵称
        self.gender = gender # 性别（怪）
        self.maxLife = self.life = maxLife # 生命值与最大生命值
        self.cards = cards # 手牌
        self.equipments = [] # 装备牌
        self.delays = [] # 延时锦囊牌
    # 回血
    def heal(self, point: int):
        self.life = min(self.maxLife, self.life + point)
        text = f"{self.name}回复了{point}点体力，现在还有{self.life}点体力。\n"
        if self.life < 1:
            return text + self.dying()
        else:
            return text
    # 扣血
    def hurt(self, damage: int):
        text = ""
        if damage > 1 and self.isEquipped("白银狮子"):
            damage = 1
            text += f"{self.name}使用白银狮子免去了多余的伤害\n"
        self.life -= damage
        text += f"{self.name}受到了{damage}点伤害\n"
        if self.life < 1:
            return text + self.dying()
        else:
            return text
    # 濒死
    def dying(self):
        nowTurn["wait"] = True
        nowTurn["cmd"] = "求桃"
        nowTurn["temp"] = [self.name]
        index = countryKill[1].index(self.name)
        nowTurn["target"] = countryKill[1][index:] + countryKill[1][:index]
        return f"{self.name}剩余**{self.life}**点体力，进入濒死状态。发送`s 桃`救ta或者`s .`\n"
    # 是否拥有装备
    def isEquipped(self, equipment: str) -> bool:
        for i in self.equipments:
            if i.name == equipment:
                return True
        return False
    def equip(self, equipment: "Card") -> str:
        text = f"{self.name}装备了【{equipment.readName}】\n"
        for i, v in enumerate(self.equipments):
            if v.type == equipment.type:
                cardList.appTrash(self.equipments.pop(i))
                text += f"{self.name}弃置了【{v.name}】\n"
            if v.name == "白银狮子":
                text += f"{self.name}失去了【白银狮子】，回复一点体力\n" + self.heal(1)
        return text

    # 测量距离
    def distanceTo(self, target: str) -> int:
        index1 = countryKill[1].index(self.name)
        index2 = countryKill[1].index(target)
        distance1 =  abs(index2 - index1)
        distance2 = len(countryKill[1]) - distance1
        return min(distance1, distance2)
    # 是否能打到
    def canHit(self, target: str) -> bool:
        distance = self.distanceTo(target)
        for i in self.equipments:
            if i.type == "weapon": distance -= i.distance - 1
        return distance <= 1

    # 指定目标
    def toKill(self, target: str, card: "Card"):
        if not self.canHit(target):
            return "距离不够！\n"
        try:
            targetObj = countryKill[2][target]
        except:
            return "没有这个玩家！\n"
        text = ""
        if self.isEquipped("青缸剑"):
            text += f"【青缸剑】：{self.name}无视了防具,\n"
        else:
            if self.isEquipped("雌雄双股剑") and self.gender != targetObj.gender:
                weaponEff("雌雄双股剑", target)
                return f"【雌雄双股剑】：{target}与你性别不同，{target}可以在以下选项中选择一项:\n1\\. 弃置一张牌 2. 令{self.name}摸一张牌\n"
            if targetObj.isEquipped("仁王盾") and card.suit in BLACK:
                nowTurn["dodged"] = True
                return f"被{target}的【仁王盾】抵消了。\n"
            elif targetObj.isEquipped("藤甲"):
                if card.name == "杀":
                    nowTurn["dodged"] = True
                    return f"被{target}的【藤甲】抵消了。\n"
            elif targetObj.isEquipped("八卦阵"):
                text += f"{target}使用了【八卦阵】\n"
                judge = cardList.pop().suit
                if judge in RED:
                    nowTurn["dodged"] = True
                    return text + f"判定结果为{judge}, 闪避成功\n"
                else:
                    text += f"判定结果为{judge}, 闪避失败\n"
        nowTurn["target"] = [target]
        return text + f"@{target} 请使用【闪】"
    # 造成伤害
    def kill(self, targets: list, card: "Card"):
        targetObj = countryKill[2][targets[0]]
        text, damage = "", 1
        if targetObj.isEquipped("藤甲") and card.name == "火杀":
            text += "【藤甲】使伤害增加了1点\n"
            damage += 1
        if self.isEquipped("古锭刀") and not targetObj.cards:
            text += "【古锭刀】使伤害增加了1点\n"
            damage += 1
        return text + targetObj.hurt(damage)

    # 摸牌
    def draw(self, num: int, judge: bool=False):
        for _ in range(num):
            card = cardList.pop()
            self.cards.append()
        self.cards.sort()
        if judge:
            return card
        else:
            return self.formatHand()

    # 格式化输出判定/装备牌
    def formatCards(self) -> str:
        text = "判定区: " + ", ".join([i.name for i in self.delays]) + "\n装备区: "
        result = []
        for i in self.equipments:
            iType = i.type
            if iType == "weapon":
                result.append(f"武器: {i.readName}")
            elif iType == "armor":
                result.append(f"防具: {i.name}")
            else:
                result.append(f"坐骑: {i.readName}")
        return text + ", ".join(result)
    # 格式化为表格输出手牌
    def formatHand(self) -> str:
        hands = ["|序号|", "|:-:|", "|花色|", "|牌名|"]
        for i, v in enumerate(self.cards):
            hands[0] += f"{i+1}|"
            hands[1] += ":-:|"
            hands[2] += f"{v.suit}{v.point}|"
            hands[3] += v.name + "|"
        return "\n".join(hands)
    # 格式化输出所有人的牌
    def formatAll(self) -> str:
        text = ""
        for k, v in countryKill[1]:
            text += f"#### {k}(与您距离为{self.distanceTo(k)})\n{v.formatCards()}\n手牌数量: {len(v.cards)}\n"
        return text
# 牌堆类
class Cards:
    def __init__(self):
        self.cards = initCards()
        self.trash = []
    # 弹出牌
    def pop(self):
        if not self.cards:
            while self.trash:
                self.cards.append(self.trash.pop())
            random.shuffle(self.cards)
        return self.cards.pop()
    # 加入弃置牌
    def appTrash(self, card):
        self.trash.append(card)
        return card
cardList = Cards()
# 牌类
class Card:
    def __init__(self, name, suit, **kargs):
        self.name = name
        self.suit = suit
        self.point = random.choice(POINTS)
        for k, v in kargs:
            self.__setattr__(k, v)
    @property
    def readName(self):
        if self.type == "weapon":
            return f"{self.name}(范围{self.distance})"
        elif self.type[-1] == "1":
            return f"{self.name}({self.type})"
        else:
            return self.name
    def __getattr__(self, attr):
        return None
    
def createCards(name, hearts=0, diamonds=0, spades=0, clubs=0, **kargs) -> list:
    cards = []
    for i in range(hearts):
        cards.append(Card(name, "红桃", **kargs))
    for i in range(diamonds):
        cards.append(Card(name, "方块", **kargs))
    for i in range(spades):
        cards.append(Card(name, "黑桃", **kargs))
    for i in range(clubs):
        cards.append(Card(name, "梅花", **kargs))
    return cards
# 初始化牌堆
# 51杀, 14雷杀(黑), 8火杀(红), 38闪(红), 8酒, 20桃(红), 5决斗, 2桃园(红桃), 5乐不思蜀, 9铁锁(黑), 5南蛮(黑), 5火攻(红)
# 10无懈可击, 4兵粮寸断(黑), 3五谷丰登(红桃), 9过河拆桥, 8顺手牵羊, 2万箭齐发(红桃), 3闪电, 3借刀杀人(梅花), 6无中生有(红桃)
# 数的我自己的三国杀，去掉了以逸待劳、知己知彼、远交近攻，别问为什么
# 花色比例乱写的
def initCards() -> list:
    cards = []
    # 基本牌与锦囊牌
    cards += createCards("杀", 6, 10, 16, 19)
    cards += createCards("火杀", 3, 5)
    cards += createCards("雷杀", spades=6, clubs=8)
    cards += createCards("闪", 12, 26)
    cards += createCards("酒", 1, 2, 2, 3)
    cards += createCards("桃", 14, 6)
    cards += createCards("决斗", 1, 1, 1, 2, type="tip")
    cards += createCards("桃园结义", 2, type="tip")
    cards += createCards("乐不思蜀", 1, 1, 1, 2, type="tip")
    cards += createCards("铁索连环", spades=4, clubs=5, type="tip")
    cards += createCards("南蛮入侵", spades=3, clubs=2, type="tip")
    cards += createCards("火攻", 3, 2, type="tip")
    cards += createCards("无中生有", 6, type="tip")
    cards += createCards("无懈可击", 2, 2, 3, 3, type="tip")
    cards += createCards("兵粮寸断", spades=2, clubs=2, type="tip")
    cards += createCards("五谷丰登", 3, type="tip")
    cards += createCards("过河拆桥", 1, 2, 3, 3, type="tip")
    cards += createCards("顺手牵羊", 2, 3, 1, 2, type="tip")
    cards += createCards("万箭齐发", 2, type="tip")
    cards += createCards("闪电", 0, 1, 1, 1, type="tip")
    cards += createCards("借刀杀人", clubs=3, type="tip")
    # 装备牌
    cards += createCards("骅骝", diamonds=1, type="+1")
    cards += createCards("爪黄飞电", hearts=2, type="+1")
    cards += createCards("的卢", clubs=2, type="+1")
    cards += createCards("绝影", spades=2, type="+1")
    cards += createCards("大宛", spades=2, type="-1")
    cards += createCards("赤兔", hearts=2, type="-1")
    cards += createCards("紫骍", diamonds=2, type="-1")
    cards += createCards("骅骝", diamonds=1, type="+1")
    cards += createCards("骅骝", diamonds=1, type="+1")

    cards += createCards("寒冰剑", spades=2, type="weapon", distance=2)
    cards += createCards("贯石斧", diamonds=2, type="weapon", distance=3)
    cards += createCards("朱雀羽扇", diamonds=2, type="weapon", distance=4)
    cards += createCards("雌雄双股剑", spades=2, type="weapon", distance=2)
    cards += createCards("吴六剑", diamonds=1, type="weapon", distance=2)
    cards += createCards("青缸剑", spades=2, type="weapon", distance=2)
    cards += createCards("青龙偃月刀", spades=1, type="weapon", distance=3)
    cards += createCards("古锭刀", spades=1, type="weapon", distance=2)
    cards += createCards("方天画戟", diamonds=1, type="weapon", distance=4)
    cards += createCards("丈八蛇矛", spades=2, type="weapon", distance=3)
    cards += createCards("诸葛连弩", diamonds=2, clubs=1, type="weapon", distance=1)
    cards += createCards("麒麟弓", hearts=2, type="weapon", distance=5)

    cards += createCards("白银狮子", clubs=2, type="armor")
    cards += createCards("藤甲", clubs=3, type="armor")
    cards += createCards("八卦阵", spades=3, type="armor")
    cards += createCards("仁王盾", clubs=2, type="armor")
    random.shuffle(cards)
    return cards
# 是否存在这个玩家（真有必要写函数吗）
def verifyPlayer(player) -> bool:
    return namePure(player) in countryKill[1]
# 武器发力了
def weaponEff(name, *target):
    nowTurn["cmd"] = name
    nowTurn["wait"] = True
    nowTurn["target"] = target
# 发牌
def deal(context):
    for i in countryKill[1]:
        cards = []
        for j in range(4):
            cards.append(cardList.pop())
        cards.sort()
        gender = random.choice(["男", "女"]) # 幽默
        countryKill[2][i] = Player(i, gender, 4, cards)
        context.appText(f"您的性别是{gender}，以下是您的牌\n{countryKill[2][i].formatHand()}", "whisper", to=i)
# 初始化当前轮次状态
def initTurn():
    index = countryKill[1].index(nowTurn["player"])
    nowTurn["player"] = countryKill[1][(index + 1) % len(countryKill[1])]
    nowTurn["dodged"] = False
    nowTurn["killed"] = False
    nowTurn["target"] = []
    nowTurn["temp"] = []
    nowTurn["wait"] = False
# 出牌
def play(context, sender, msg):
    array = msg.split(" ")
    if len(array) < 1:
        text = "没有参数！"
    else:
        command, text, legal = array[0], "", True
        senderObj = countryKill[2][sender]
        if command == "check":
            return context.appText(f":\n{senderObj.formatCards()}\n手牌:\n{senderObj.formatHand()}", "whisper")
        elif command == "help":
            card = msg[5:]
            if card in USAGE: text = USAGE[card]
            else: text = "不存在这张牌！"
        elif command == "all":
            text = senderObj.formatAll()
        else:
            try:
                if command != ".":
                    cardObj = senderObj.cards[int(command)-1]
                    cardName = cardObj.name
            except (TypeError, IndexError):
                return context.appText("指令错误！")
            player = nowTurn["player"]
            playerObj = countryKill[2][player]
            # 被动出牌
            if nowTurn["wait"] and sender in nowTurn["target"]:
                turnCmd = nowTurn["cmd"]
                # 跳过
                if command == ".":
                    if turnCmd[-1] == "杀":
                        text = f"{sender} 未能闪避\n" + senderObj.hurt(1)
                        nowTurn["wait"] = False
                elif turnCmd[-1] == "杀" and command == "闪":
                    text = f"{sender} 闪避了【杀】\n"
                    if playerObj.isEquipped("贯石斧"):
                        weaponEff("贯石斧", player)
                        text += f"【贯石斧】：{player}可以选择弃置两张牌，使此【杀】依旧造成伤害\n"
                    elif playerObj.isEquipped("青龙偃月刀"):
                        weaponEff("青龙偃月刀", player)
                        text += f"【青龙偃月刀】：【杀】被抵消，{player}可以选择再出一张【杀】"
                    else:
                        text += f"{player}继续出牌。\n"
            # 主动出牌
            elif not nowTurn["wait"] and sender == player:
                # 跳过&弃牌
                if command == ".":
                    length = len(senderObj.cards)
                    for i in array[1:]:
                        try:
                            assert int(i) > length
                        except:
                            text += "序号错误！\n"
                            break
                    else:
                        cards = []
                        for i in array[1:]:
                            card = cardList.appTrash(senderObj.cards.pop(int(i)))
                            cards.append(card.name)
                        text += f"{sender}弃置了{', '.join(cards)}\n"
                        if len(senderObj.cards) > senderObj.life:
                            text += f"您的手牌数大于体力值，请弃牌直到剩**{senderObj.life}**张!\n"
                        else:
                            context.appText(f"{sender}结束了自己的回合\n---\n")
                            return goTurn(context, True)
                else:
                    text += f"{sender}出了【{cardName}】\n"
                    if cardName in DESCRIPTION:
                        text += DESCRIPTION[cardName]

                    if cardName[-1] == "杀":
                        if len(array) < 2:
                            text = "没有参数！"
                        elif nowTurn["killed"]:
                            text = "您这回合已经出过【杀】了！"
                        else:
                            text = senderObj.toKill(namePure(array[1]), card)
                            nowTurn["temp"] = array[2:]
                            if not nowTurn["dodged"]:
                                nowTurn["cmd"] = cardName
                            else:
                                nowTurn["wait"] = True
                            if not senderObj.isEquipped("诸葛连弩"):
                                nowTurn["killed"] = True
                    elif cardName in ["闪", "无懈可击"]:
                        text = f"不能主动出【{cardName}】！\n"
                    elif cardName == "桃":
                        text = senderObj.heal(1)
                    elif cardObj.type in ["weapon", "armor", "+1", "-1"]:
                        senderObj.equip(cardObj)

    context.appText(text)

# 转换轮次(判定&摸牌)
def goTurn(context, next: bool=False) -> str:
    if next:
        index = countryKill[1].index(nowTurn["player"])
        index = (index + 1) % len(countryKill[1])
        nowTurn["player"] = countryKill[1][index]
        context.appText(f"轮到{nowTurn['player']}")
    playerObj = countryKill[2][nowTurn["player"]]
    context.appText(f"你摸了2张，这是你现在的牌\n{playerObj.draw(2)}", "whisper", to=playerObj.name)

def killReply(context, sender, msg):
    if countryKill[0] and sender in countryKill[1]:
        play(context, sender, msg)
    elif msg == "加入" and not countryKill[0]:
        countryKill[1].append(sender)
        context.appText("加入成功!")
    elif msg == "开始":
        if len(countryKill[1]) < 2:
            context.appText("需要至少两个人！")
        else:
            countryKill[0] = True
            deal(context)
            nowTurn["player"] = random.choice(countryKill[1])
            context.appText(f"牌发好了！随机由{nowTurn['player']}先开始！")
            context.appText(goTurn(context))