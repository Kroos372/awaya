# 写的什么玩意啊我草
import random

## 名字提纯
def namePure(name: str) -> str:
    return name.strip("@").strip()

# [0游戏开关, 1[玩家列表], 2{玩家: Player对象}, 3当前轮次对象]
countryKill = [False, [], {}, {}]

KILLMENU = "\n".join([
    "油杀...",
    "s 加入: 加入一场三国杀。",
    "s 退出: 在开始之前退出对局。",
    "s 开始: 开始一场三国杀。",
    "s <牌>: 出牌，具体规则请查看出牌规则。",
    "s 结束: 在对局中结束游戏。",
    "s 规则: 获取三国杀的出牌规则。",
])
KILLRULE = "\n".join([
    "行牌规则：",
    "s <牌的序号> <参数>, 如==s 1 @Krs_==, ==s 4 Krs_ awa_ya==。以下是注意事项：",
    "进入濒死状态会自动出手上的桃/酒(没有求桃)",
    "不出牌或无法出牌发送=s .==, 进行选择发送==s <序号>==",
    "弃牌阶段发送==s . <序号1> <序号2>==等",
    "使用==s help <牌名>==查看卡牌描述与部分特殊效果的出法",
    "==s check==查看自己当前的牌与序号, ==s all==查看所有人的装备牌与序号",
    "温馨提示: 出牌前请注意距离、防具等属性。"
])

POINTS = ["A"] + list(range(2, 11)) + list("JQK")
BLACK, RED = ["黑桃", "梅花"], ["红桃", "方块"]

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
    "酒": "酒杀使用==s <杀的序号> <酒的序号> <参数>==",
    
    "桃园结义": "出牌阶段，对所有角色使用。每名目标角色回复1点体力。",
    "铁索连环": "\n".join([
        "出牌阶段，指定一至两名角色，分别使其处于“连环状态”。",
        "重铸：出牌阶段，你可以将此牌置入弃牌堆，然后摸一张牌。",
        "注：此牌规则比较复杂，有问题可以百度。"
    ]),

    "决斗": "出牌阶段，对一名其他角色使用。由该角色开始，你与其轮流打出一张【杀】，首先不出【杀】的一方受到另一方造成的1点伤害。",
    "火攻": "出牌阶段，对一名有手牌的角色使用。该角色展示一张手牌，然后若你弃置一张与所展示牌相同花色的手牌，则【火攻】对其造成1点火焰伤害。",
    "闪电": "出牌阶段，对你使用。将【闪电】放置于你的判定区里。若判定结果为♠2~9，则目标角色受到3点雷电伤害。若判定不为此结果，将之移动到下家的判定区里。",
    "过河拆桥": "出牌阶段，对一名区域内有牌的其他角色使用。你将其区域内的一张牌弃置。",
    "顺手牵羊": "出牌阶段，对距离为1且区域内有牌的一名其他角色使用。你获得其区域内的一张牌。\n(s <序号> <昵称> 手/<装备序号>)",
    "南蛮入侵": "出牌阶段，对所有其他角色使用。每名目标角色需打出一张【杀】，否则受到1点伤害。\n(s <序号> <昵称> 手/<装备序号>)",
    "万箭齐发": "出牌阶段，对所有其他角色使用。每名目标角色需打出一张【闪】，否则受到1点伤害。",
    "乐不思蜀": "出牌阶段，对一名其他角色使用。将【乐不思蜀】放置于该角色的判定区里，若判定结果不为♥，则跳过其出牌阶段。",
    "兵粮寸断": "出牌阶段，对距离为1的一名其他角色使用。将【兵粮寸断】放置于该角色的判定区里，若判定结果不为♣，则跳过其摸牌阶段。",
    "无中生有": "出牌阶段，对你使用。摸两张牌。",
    "五谷丰登": "出牌阶段，对所有角色使用。你从牌堆亮出等同于现存角色数量的牌，每名目标角色选择并获得其中的一张。",
    "借刀杀人": "出牌阶段，对装备区里有武器牌的一名其他角色使用。该角色需对其攻击范围内，由你指定的一名角色使用一张【杀】，否则将装备区里的武器牌交给你。",
    "无懈可击": "抵消目标锦囊牌对一名角色产生的效果，或抵消另一张【无懈可击】产生的效果。",

    "丈八蛇矛": "攻击范围：3。你可以将两张手牌当【杀】使用或打出。(s 丈 <序号> <序号> ?<昵称>)",
    "诸葛连弩": "攻击范围：1。出牌阶段，你可以使用任意数量的【杀】。",
    "吴六剑": "攻击范围：2。锁定技，与你势力相同的其他角色攻击范围+1。\n注：目前还没写武将牌，所以此技能没用。",
    "朱雀羽扇": "攻击范围：4。你可以将一张普通【杀】当具火焰伤害的【杀】使用。",
    "青缸剑": "攻击范围：2。锁定技，当你使用【杀】指定一名角色为目标后，无视其防具。",
    "方天画戟": "攻击范围：4。当你使用【杀】时，且此【杀】是你最后手牌，你可以额外指定至多两个目标。\n(s 杀 <昵称> <昵称> <昵称>)",
    "雌雄双股剑": "攻击范围：2。当你使用【杀】指定一名异性角色为目标后，你可以令其选择一项：弃置一张手牌；或令你摸一张牌。",
    "青龙偃月刀": "攻击范围：3。当你使用的【杀】被【闪】抵消时，你可以对相同的目标再使用一张【杀】。",
    "贯石斧": "攻击范围：3。当你使用的【杀】被【闪】抵消时，你可以弃置两张牌，则此【杀】依然造成伤害。",
    "麒麟弓": "攻击范围：5。当你使用【杀】对目标角色造成伤害时，你可以弃置其装备区里的一张坐骑牌。",
    "寒冰剑": "攻击范围：2。当你使用的【杀】对目标角色造成伤害时，若该角色有牌，你可以防止此伤害，改为依次弃置其两张牌。",
    "古锭刀": "攻击范围：2。锁定技，当你使用【杀】对目标角色造成伤害时，若其没有手牌，此伤害+1。",
    "三尖两刃刀": "攻击范围：3。你使用【杀】对目标角色造成伤害后，可弃置一张手牌并对该角色距离1的另一名角色造成1点伤害。",

    "白银狮子": "锁定技，当你受到伤害时，若该伤害多于1点，则防止多余的伤害；当你失去装备区里的【白银狮子】时，你回复1点体力。",
    "藤甲": "锁定技，【南蛮入侵】、【万箭齐发】和普通【杀】对你无效。当你受到火焰伤害时，此伤害+1。",
    "仁王盾": "锁定技，黑色的【杀】对你无效。",
    "八卦阵": "每当你需要使用或打出一张【闪】时，你可以进行一次判定：若判定结果为红色，则视为你使用或打出了一张【闪】。"
}
# 玩家类
class Player:
    def __init__(self, name, gender, maxLife, cards):
        # 昵称
        self.name = name # 昵称
        self.gender = gender # 性别（怪）
        self.maxLife = self.life = maxLife # 生命值与最大生命值
        self.cards = PlayerCards(cards) # 手牌
        self.equipments = [] # 装备牌
        self.delays = [] # 延时锦囊牌
    # 回血
    def heal(self, point: int, recall:bool=False):
        self.life = min(self.maxLife, self.life + point)
        text = f"{self.name}回复了{point}点体力，现在还有{self.life}点体力。\n"
        if self.life < 1 and not recall:
            return text + self.dying()
        else:
            return text
    # 扣血
    def hurt(self, damage: int, type_: str=""):
        text = ""
        if damage > 1 and self.isEquipped("白银狮子"):
            damage = 1
            text += f"{self.name}使用白银狮子免去了多余的伤害\n"
        elif type_ == "火" and self.isEquipped("藤甲"):
            text += "【藤甲】使火焰伤害增加了1点\n"
            damage += 1

        self.life -= damage
        text += f"{self.name}受到了{damage}点伤害，还剩{self.life}点体力\n"
        if self.life < 1:
            return text + self.dying()
        else:
            return text
    # 濒死
    def dying(self):
        text = f"{self.name}剩余**{self.life}**点体力，进入濒死状态。\n"
        for card in self.cards:
            if card.name in ["桃", "酒"]:
                self.cards.remove(card)
                text += f"自动使用了【{card.name}】\n" + self.heal(1, True)
                if self.life > 0:
                    break
        # 这下真死了
        if self.life < 1:
            countryKill[1].remove(self.name)
            del countryKill[2][self.name]
            text += f"{self.name}似了！😭😭😭\n"
            if len(countryKill[1]) == 1:
                winner = gameOver()
                text += f"@{winner} 获胜！🍾🍾🍾\n"
        return text

    # 是否拥有装备
    def isEquipped(self, equipment, type_: str="name") -> bool:
        return any(i[type_] == equipment for i in self.equipments)
    def equip(self, equipment: "Card") -> str:
        text = f"{self.name}装备了【{equipment.readName}】\n"
        for old in self.equipments:
            if old.type == equipment.type:
                text += self.unequip(old, True)
                break
        if equipment.name == "诸葛连弩":
            countryKill[3]["kill"]["killed"] = False
        self.equipments.append(equipment)
        return text
    def unequip(self, equipment: "Card", trash=False) -> str:
        text = f"{self.name}失去了【{equipment.name}】\n"
        self.equipments.remove(equipment)
        if equipment.name == "白银狮子":
            text += f"{self.name}失去了【白银狮子】，回复一点体力\n" + self.heal(1)
        if trash:
            cardList.appTrash(equipment)
        return text

    # 测量距离
    def distanceTo(self, target: str) -> int:
        index1 = countryKill[1].index(self.name)
        index2 = countryKill[1].index(target)
        distance1 =  abs(index2 - index1)
        distance2 = len(countryKill[1]) - distance1

        distance = min(distance1, distance2)
        if countryKill[2][target].isEquipped("+1", "type"):
            distance += 1
        if self.isEquipped("-1", "type"):
            distance -= 1
        return distance
    # 是否能打到
    def canHit(self, target: str) -> bool:
        distance = self.distanceTo(target)
        for i in self.equipments:
            if i.type == "weapon":
                distance -= i.distance - 1
                break
        return distance <= 1

    # 指定目标
    def toKill(self, target: str, card: "Card"):
        targetObj = countryKill[2][target]
        dodgeList = countryKill[3]["targets"]
        if not self.canHit(target):
            dodgeList.remove(targetObj.name)
            return illegal("距离不够！\n")
        text = ""
        if self.isEquipped("青缸剑"):
            text += f"【青缸剑】：{self.name}无视了防具\n"
        else:
            if card.name == "杀" and self.isEquipped("朱雀羽扇"):
                text += f"【朱雀羽扇】：【杀】被当做【火杀】使用\n"
                card = Card("火杀", card.suit, fake=True)
            if self.isEquipped("雌雄双股剑") and self.gender != targetObj.gender and not countryKill[3]["kill"]["weaponed"]:
                weaponEff("雌雄双股剑", target)
                text += f"【雌雄双股剑】：{target}与你性别不同，{target}可以在以下选项中选择一项:\n"
                text += f"1\\. 弃置一张牌 2. 令{self.name}摸一张牌\n(s 1 <序号>/s 2)"
            if targetObj.isEquipped("仁王盾") and card.suit in BLACK:
                dodgeList.remove(targetObj.name)
                return f"被{target}的【仁王盾】抵消了。\n"
            elif targetObj.isEquipped("藤甲"):
                if card.name == "杀":
                    dodgeList.remove(targetObj.name)
                    return f"被{target}的【藤甲】抵消了。\n"
            elif targetObj.isEquipped("八卦阵"):
                text += f"{target}的【八卦阵】发动了。\n"
                judge = cardList.judge().suit
                if judge in RED:
                    dodgeList.remove(targetObj.name)
                    return text + f"判定结果为{judge}, 闪避成功\n"
                else:
                    text += f"判定结果为{judge}, 闪避失败\n"
        return text
    # 造成伤害
    def kill(self, target: str, card: "Card"):
        targetObj: "Player" = countryKill[2][target]
        killObj = countryKill[3]["kill"]
        text = ""
        if card.liquor:
            damage = 2
            card.liquor = False
        else:
            damage = 1

        if self.isEquipped("古锭刀") and not targetObj.cards:
            text += "【古锭刀】使伤害增加了1点\n"
            damage += 1
        if self.isEquipped("寒冰剑") and not killObj["weaponed"]:
            weaponEff("寒冰剑")
            text += f"【寒冰剑】：{self.name}可防止此次伤害，改为弃置{target}2张牌。(s 手/<序号> 手/<序号>或s .)"
        else:
            text += targetObj.hurt(damage, card.name[0])
            countryKill[3]["targets"].remove(target)
            card.damage = 1
        if not killObj["weaponed"]:
            if self.isEquipped("三尖两刃刀"):
                weaponEff("三尖两刃刀")
                text += f"【三尖两刃刀】：{self.name}可弃置一张手牌，对与{target}距离为1的角色造成1点伤害。(s <序号> <昵称>或s .)"
            elif self.isEquipped("麒麟弓") and targetObj.isEquipped(True, "horse"):
                weaponEff("麒麟弓")
                text += f"【麒麟弓】：{self.name}可弃置{target}装备区一张坐骑牌。(s <序号>或s .)"
        return text

    # 摸牌
    def draw(self, num: int) -> str:
        for _ in range(num):
            card = cardList.pop()
            self.cards.append(card)
        return self.formatHand()
    # 判定
    def judge(self) -> str:
        text = ""
        while self.delays:
            card = self.delays.pop()
            judgeCard = cardList.judge()
            cardName, suit = card.name, judgeCard.suit
            text += f"被判定牌为【{cardName}】，判定结果为=={suit}{judgeCard.point}==\n"
            if cardName == "乐不思蜀":
                if suit == "红桃":
                    text += f"判定成功，无事发生。\n"
                else:
                    text += f"判定失败...{self.name}==跳过出牌阶段==，请直接弃牌\n"
                    countryKill[3]["temp"].append(cardName)
                cardList.appTrash(card)
            elif cardName == "兵粮寸断":
                if suit == "梅花":
                    text += f"判定成功，无事发生。\n"
                else:
                    text += f"判定失败...{self.name}==跳过摸牌阶段==，请直接出牌\n"
                    countryKill[3]["temp"].append(cardName)
                cardList.appTrash(card)
            elif cardName == "闪电":
                if suit == "黑桃" and (2 <= judgeCard.point <= 9):
                    countryKill[3]["temp"].append(cardName)
                    text += f"判定成功...{self.name}==受到3点雷电伤害==。\n"
                    text += self.hurt(3, "雷")
                    cardList.appTrash(card)
                else:
                    nextPlayer = getNext()
                    countryKill[2][nextPlayer].delays.append(card)
                    text += f"判定失败，无事发生。\n闪电转到{nextPlayer}\n"
        return text
    # 获取牌
    def getCard(self, index: str) -> "Card":
        try:
            card = self.cards[int(index)-1]
            if card is None:
                raise ValueError
            else:
                return card
        except (ValueError, IndexError):
            return None
    # 随机抽牌
    def randomCard(self) -> "Card":
        card = None
        while card is None:
            index = random.randint(0, self.cards.length-1)
            card = self.cards[index]
        return card

    # 格式化输出判定/装备牌
    def formatCards(self) -> str:
        text = "#### 判定区: " + ", ".join([i.name for i in self.delays]) + "\n#### 装备区:\n"
        result = []
        for i, v in enumerate(self.equipments):
            iType = v.type
            if iType == "weapon":
                temp = f"武器: {v.readName}"
            elif iType == "armor":
                temp = f"防具: {v.name}"
            else:
                temp = f"坐骑: {v.readName}"
            result.append(temp + f" (序号{i+1})")
        return text + "\n".join(result)
    # 格式化为表格输出手牌
    def formatHand(self) -> str:
        self.cards.sweep()
        if self.cards:
            self.cards.sort(key=lambda x: x.name)
            return formatTable(self.cards)
        else:
            return "当前无手牌！"
    # 格式化输出所有人的牌
    def formatAll(self) -> str:
        text = ""
        for k, v in countryKill[2].items():
            text += f"### {k}({v.gender})(与您距离{self.distanceTo(k)})\n{v.formatCards()}\n#### 手牌数量: {len(v.cards)}, 体力值: {v.life}\n"
        return text
# 牌堆类
class Cards:
    def __init__(self):
        self.trash = []
        self.initCards()
    # 初始化牌堆
    # 51杀, 14雷杀(黑), 8火杀(红), 38闪(红), 8酒, 20桃(红), 5决斗, 2桃园(红桃), 5乐不思蜀, 9铁锁(黑), 5南蛮(黑), 5火攻(红)
    # 10无懈可击, 4兵粮寸断(黑), 3五谷丰登(红桃), 9过河拆桥, 8顺手牵羊, 2万箭齐发(红桃), 3闪电, 3借刀杀人(梅花), 6无中生有(红桃)
    # 数的我自己的三国杀，去掉了以逸待劳、知己知彼、远交近攻，别问为什么
    # 花色比例乱写的
    def initCards(self) -> list:
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
        cards += createCards("南蛮入侵", spades=3, clubs=2, type="tip")
        cards += createCards("火攻", 3, 2, type="tip")
        cards += createCards("无中生有", 6, type="tip")
        # 这俩有点麻烦
        # cards += createCards("铁索连环", spades=4, clubs=5, type="tip")
        # cards += createCards("无懈可击", 2, 2, 3, 3, type="tip")
        cards += createCards("兵粮寸断", spades=2, clubs=2, type="tip")
        cards += createCards("五谷丰登", 3, type="tip")
        cards += createCards("过河拆桥", 1, 2, 3, 3, type="tip")
        cards += createCards("顺手牵羊", 2, 3, 1, 2, type="tip")
        cards += createCards("万箭齐发", 2, type="tip")
        cards += createCards("闪电", 0, 1, 1, 1, type="tip")
        cards += createCards("借刀杀人", clubs=3, type="tip")
        # 装备牌
        cards += createCards("骅骝", diamonds=1, type="+1", horse=True)
        cards += createCards("爪黄飞电", hearts=2, type="+1", horse=True)
        cards += createCards("的卢", clubs=2, type="+1", horse=True)
        cards += createCards("绝影", spades=2, type="+1", horse=True)
        cards += createCards("大宛", spades=2, type="-1", horse=True)
        cards += createCards("赤兔", hearts=2, type="-1", horse=True)
        cards += createCards("紫骍", diamonds=2, type="-1", horse=True)
        cards += createCards("骅骝", diamonds=1, type="+1", horse=True)
        cards += createCards("骅骝", diamonds=1, type="+1", horse=True)

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
        self.cards = cards
    # 弹出牌
    def pop(self) -> "Card":
        if not self.cards:
            while self.trash:
                self.cards.append(self.trash.pop())
            random.shuffle(self.cards)
        return self.cards.pop()
    # 加入弃置牌
    def appTrash(self, card) -> "Card":
        if not card.fake:
            self.trash.append(card)
        return card
    # 判定(弹出+弃置)
    def judge(self):
        return self.appTrash(self.pop())
# 牌类
class Card:
    def __init__(self, name, suit, **kargs):
        self.name = name
        self.suit = suit
        self.point = random.choice(POINTS)
        for k, v in kargs.items():
            self.__setattr__(k, v)
    @property
    def readName(self):
        if self.type == "weapon":
            return f"{self.name}(范围{self.distance})"
        elif self.horse:
            return f"{self.name}({self.type})"
        else:
            return self.name
    def __getattr__(self, attr):
        return None
    def __getitem__(self, key):
        if key == "name":
            return self.name
        elif key == "type":
            return self.type
        elif key == "horse":
            return self.horse
        else:
            return super().__getitem__(key)
# 玩家手牌类
class PlayerCards(list):
    def pop(self, index=-1):
        value = self[index]
        self[index] = None
        return value
    def remove(self, value):
        if value in self:
            index = self.index(value)
            self[index] = None
    def sweep(self):
        while None in self:
            super().remove(None)
    def __len__(self):
        return len([0 for i in self if i is not None])
    def __iter__(self):
        for item in super().__iter__():
            if item is not None: 
                yield item
    @property
    def length(self):
        return super().__len__()

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
# 武器发力了
def weaponEff(name, *target):
    countryKill[3]["cmd"] = name
    countryKill[3]["wait"] = True
    countryKill[3]["temp"] = target
    countryKill[3]["kill"]["weaponed"] = True
# 非法（莫名其妙）
def illegal(text: str="") -> str:
    countryKill[3]["legal"] = False
    return text
# 是否有序号的牌
def assertId(sender, ids, eq=False) -> bool:
    if eq:
        length = len(countryKill[2][sender].equipments)
    else:
        length = len(countryKill[2][sender].cards)
    for i in ids:
        try:
            assert int(i) <= length
        except:
            return False
    return True
# 获取下家名称
def getNext() -> str:
    index = countryKill[1].index(countryKill[3]["player"])
    index = (index + 1) % len(countryKill[1])
    return countryKill[1][index]
# 检查是否有需要出闪的
def checkKill(playerObj, cardObj) -> str:
    try:
        dodgeObj = countryKill[3]["targets"]
    except:
        return ""
    target = dodgeObj[0]
    if dodgeObj:
        text = playerObj.toKill(target, cardObj)
        if not countryKill[3]["wait"] and target in dodgeObj:
            countryKill[3]["wait"] = True
            countryKill[3]["cmd"] = "杀"
            text += f"@{target} 请使用闪"
    else:
        countryKill[3]["wait"] = False
        countryKill[3]["cmd"] = None
        countryKill[3]["kill"].update({"lent": None, "weaponed": False})
        text = f"@{countryKill[3]['player']} 请继续出牌"
    return text
# 初始化当前轮次状态
def initTurn(player):
    countryKill[3].update({
        "player": player, # 此回合轮到的玩家
        "kill": {
            "killed": False, # 是否出过杀
            "card": None, # 【杀】卡
            "lent": None, # 借谁的刀
            "weaponed": False # 是否发动过武器
        }, # 杀相关
        "cmd": None, # 操作，如杀、决斗、过河拆桥或装备牌技能
        "temp": [], # 一些延时生效的效果参数
        "targets": [], # 等待的目标
        "wait": False, # 是否等待响应（是否可以继续出牌）
        "legal": True, # 出牌是否合法（是否扣牌）
    })
# 检查参数长度与玩家合法
def verifyArray(array: list, length: int=2, playerNum: int=1) -> bool:
    return len(array) >= length and all(namePure(i) in countryKill[1] for i in array[1:playerNum+1])
# 卡牌列表格式化为表格
def formatTable(cards) -> str:
    hands = ["|序号|", "|:-:|", "|花色|", "|牌名|"]
    for i, v in enumerate(cards):
        hands[0] += f"{i+1}|"
        hands[1] += ":-:|"
        hands[2] += f"{v.suit}{v.point}|"
        hands[3] += f"【{v.readName}】|"
    return "\n".join(hands)
# 杀复用
def killFunc(senderObj, cardObj, array) -> str:
    turn = countryKill[3]
    killObj = turn["kill"]
    text = ""
    if len(array) < 2:
        text += illegal("没有参数！\n")
    elif (not killObj["lent"]) and killObj["killed"]:
        text += illegal("您这回合已经出过【杀】了！\n")
    else:
        if array[1].isdigit():
            try:
                card2Obj = senderObj.cards[int(array[1])-1]
            except:
                pass
            else:
                if card2Obj.name == "酒":
                    senderObj.cards.pop(int(array.pop(1))-1)
                    cardObj.liquor = True
                    text += "【酒】洒在了刀上，伤害+1\n"
        if senderObj.isEquipped("方天画戟") and len(senderObj.cards) == 1:
            array = array[1:4]
        else:
            array = array[1:2]
        array = [namePure(i) for i in array]
        if not all(i in countryKill[1] for i in array):
            text += illegal("参数不正确！\n")
        elif senderObj.name in array:
            text += illegal("不可以伤害自己...\n")
        else:
            turn["targets"] = array
            killObj["card"] = cardObj
            if not (killObj["lent"] or senderObj.isEquipped("诸葛连弩")):
                killObj["killed"] = True
    return text
# 幽默函数名
def sheepBridge(senderObj: "Player", array: list, sheep: bool) -> str:
    text = ""
    if not verifyArray(array, 3):
        text += illegal("参数错误！\n")
    else:
        target = namePure(array[1])
        if (sheep and senderObj.distanceTo(target) > 1):
            text += illegal("【顺手牵羊】只能对距离为1的角色使用！\n")
        else:
            targetObj: "Player" = countryKill[2][target]
            if array[2] == "手":
                if not targetObj.cards:
                    text += illegal(f"{target}没有手牌ヾ(。￣□￣)ﾂ")
                else:
                    card = targetObj.randomCard()
                    targetObj.cards.remove(card)
                    if sheep:
                        senderObj.cards.append(card)
                        text += f"随机顺走了{target}的【{card.name}】给了{senderObj.name}！"
                    else:
                        cardList.appTrash(card)
                        text += f"随机弃置了{target}的【{card.name}】！"
            else:
                try:
                    equipment = targetObj.equipments[int(array[2])-1]
                except (TypeError, IndexError):
                    text += illegal(f"{target}没有那张牌！")
                else:
                    if sheep:
                        senderObj.cards.append(equipment)
                        text += f"{senderObj.name}顺走了{target}的【{equipment.name}】！\n"
                    else:
                        text += f"{senderObj.name}弃置了{target}的【{equipment.name}】！\n"
                    text += targetObj.unequip(equipment, not sheep)
    return text
def arrowBarbarian(sender: str, arrow: bool=False) -> str:
    text = ""
    countryKill[3]["wait"] = True
    _targets = []
    for target, targetObj in countryKill[2].items():
        if target == sender:
            continue
        elif targetObj.isEquipped("藤甲"):
            if arrow:
                text += f"{target}的【藤甲】抵消了【万箭齐发】\n"
            else:
                text += f"{target}的【藤甲】抵消了【南蛮入侵】\n"
            continue
        elif arrow and targetObj.isEquipped("八卦阵"):
            text += f"{target}的【八卦阵】发动了\n"
            judge = cardList.judge().suit
            if judge in RED:
                text + f"判定结果为{judge}, 闪避成功\n"
                continue
            else:
                text += f"判定结果为{judge}, 闪避失败\n"
        _targets.append(target)
    countryKill[3]["targets"] = _targets
    dodo = " @".join(_targets)
    if arrow:
        text += f"【万箭齐发】: 请@{dodo} 出【闪】\n"
    else:
        text += f"【南蛮入侵】: 请@{dodo} 出【杀】\n"
    return text

# 发牌
def deal(context):
    for i in countryKill[1]:
        cards = []
        for j in range(4):
            cards.append(cardList.pop())
        cards.sort(key=lambda x: x.name)
        gender = random.choice(["男", "女"]) # 幽默
        countryKill[2][i] = Player(i, gender, 4, cards)
        context.appText(f"您的性别是{gender}，以下是您的牌\n{countryKill[2][i].formatHand()}", "whisper", to=i)
# 出牌
def play(context, sender, msg):
    array = msg.split(" ")
    command, text = array[0], ""
    senderObj: "Player" = countryKill[2][sender]
    if command == "check":
        turn = countryKill[3]
        text = f"当前是{turn['player']}的轮次\n"
        if turn["wait"]:
            targets = ", ".join(turn["targets"])
            text += f"，现在在等待{targets}对【{turn['cmd']}】的响应\n"
        text += f"#### 性别：{senderObj.gender}, 体力值：{senderObj.life}\n"
        return context.appText(text + f"{senderObj.formatCards()}\n#### 手牌:\n{senderObj.formatHand()}", "whisper")
    elif command == "help":
        card = msg[5:]
        if card in USAGE:
            text = USAGE[card]
        else:
            text = "不存在这张牌！"
    elif command == "all":
        text = senderObj.formatAll()
    elif command == "结束":
        countryKill[0] = False
        countryKill[1] = []
        countryKill[2] = {}
        text = "唔，结束了……"
    else:
        if command == "丈" and senderObj.isEquipped("丈八蛇矛"):
            if len(array) < 3:
                return context.appText("参数不足！")
            elif not assertId(sender, array[1:3]):
                return context.appText("序号错误！")
            else:
                for i in array[1:3]:
                    card = senderObj.cards.pop(int(i)-1)
                    cardList.appTrash(card)
                text += f"【丈八蛇矛】：{sender}将两张牌当做了【杀】使用\n"
                cardObj = Card("杀", "", fake=True)
                cardName = "杀"
                array = ["杀"] + array[3:]

        turn = countryKill[3]
        player = turn["player"]
        playerObj: "Player" = countryKill[2][player]
        # 被动出牌
        if turn["wait"] and (sender in turn["targets"] or sender in turn["temp"]):
            turnCmd = turn["cmd"]
            targets: list = turn["targets"]
            cardObj: "Card" = senderObj.getCard(command)
            if cardObj:
                cardName = cardObj.name
            else:
                cardName = ""
                illegal()

            if turnCmd == "杀":
                killObj = turn["kill"]
                if killObj["lent"]:
                    player = killObj["lent"]
                    playerObj = countryKill[2][player]
                if cardName == "闪":
                    text = f"{sender} 闪避了【{killObj['card'].name}】\n"
                    turn["wait"] = False
                    if not killObj["weaponed"]:
                        if playerObj.isEquipped("贯石斧"):
                            weaponEff("贯石斧", player)
                            text += f"【贯石斧】：{player}可以选择弃置两张牌，使此【杀】依旧造成伤害\n"
                        elif playerObj.isEquipped("青龙偃月刀"):
                            weaponEff("青龙偃月刀", player)
                            text += f"【青龙偃月刀】：【杀】被抵消，{player}可以选择再出一张【杀】\n"
                    if not turn["wait"]:
                        targets.remove(sender)
                elif command == ".":
                    if turnCmd[-1] == "杀":
                        turn["wait"] = False
                        text = f"{sender} 未能闪避\n" + playerObj.kill(sender, killObj["card"])
                else:
                    text += "出牌错误！\n"
            elif turnCmd == "五谷丰登":
                if sender != targets[0]:
                    return context.appText("还没到你！")
                cards = turn["temp"]
                try:
                    card = cards.pop(int(command)-1)
                except (TypeError, IndexError):
                    return context.appText("序号错误。。")
                targets.remove(sender)
                senderObj.cards.append(card)
                if len(targets) > 1:
                    text += f"{sender}取走了【{card.name}】、轮到@{targets[0]} 选择。\n{formatTable(cards)}"
                else:
                    countryKill[2][targets[0]].cards.append(cards[0])
                    text += f"{sender}取走了【{card.name}】、{targets[0]}获得了余下的【{cards[0].name}】\n"
                    turn["wait"] = False
            elif turnCmd == "决斗":
                if sender != targets[0]:
                    return context.appText("还没到你！")
                elif cardName and cardName[-1] == "杀":
                    targets.reverse() # 天才
                    text += f"{sender}出了【杀】、轮到@{targets[0]}\n"
                elif command == ".":
                    turn["wait"] = False
                    text += f"{sender}无【杀】可出\n" + senderObj.hurt(1)
                else:
                    text += illegal("出牌错误！\n")
            elif turnCmd == "火攻":
                # 展示手牌
                if sender != player:
                    if cardObj:
                        turn["temp"] = [cardObj.suit, senderObj]
                        turn["targets"] = [player]
                        text += f"{sender}展示了【{cardObj.name}】=={cardObj.suit}==\n"
                        text += f"@{player} 可弃置一张相同花色的手牌，造成一点火焰伤害\n"
                        illegal() # 只展示不弃置
                    else:
                        text += "参数有误！\n"
                # 弃牌伤害
                else:
                    if cardObj:
                        if cardObj.suit != turn["temp"][0]:
                            text += illegal("花色不符！\n")
                        else:
                            turn["wait"] = False
                            text += f"{sender}弃置了【{cardObj.name}】=={cardObj.suit}==\n" + turn["temp"][1].hurt(1, "火")
                    elif command == ".":
                        turn["wait"] = False
                        text += f"{sender}不弃牌，"
                    else:
                        text += "出牌错误！\n"

            elif turnCmd == "万箭齐发":
                if cardName == "闪":
                    targets.remove(sender)
                    text += f"{sender}使用了【闪】。\n"
                    if targets:
                        text += "还剩@" + " @".join(targets)
                    else:
                        turn["wait"] = False
                elif command == ".":
                    targets.remove(sender)
                    text += f"{sender}受到一点伤害。\n" + senderObj.hurt(1)
                    if targets:
                        text += "还剩@" + " @".join(targets)
                    else:
                        turn["wait"] = False
                else:
                    text += illegal("你需要出【闪】！\n")
            elif turnCmd == "南蛮入侵":
                if cardName and cardName[-1] == "杀":
                    targets.remove(sender)
                    text += f"{sender}使用了【杀】。\n"
                    if targets:
                        text += "还剩@" + " @".join(targets)
                    else:
                        turn["wait"] = False
                elif command == ".":
                    targets.remove(sender)
                    text += f"{sender}受到一点伤害。\n" + senderObj.hurt(1)
                    if targets:
                        text += "还剩@" + " @".join(targets)
                    else:
                        turn["wait"] = False
                else:
                    text += illegal("你需要出【杀】！\n")

            elif sender in turn["temp"]:
                illegal()
                killer = turn["kill"]["lent"] or turn["player"]
                killerObj: "Player" = countryKill[2][killer]
                targetObj: "Player" = countryKill[2][targets[0]]
                if turnCmd == "雌雄双股剑":
                    if command == "1":
                        try:
                            card = senderObj.cards.pop(int(array[1]) - 1)
                        except (TypeError, ValueError):
                            text += "参数错误！"
                        else:
                            cardList.appTrash(card)
                            text += f"{sender}弃置了【{card.name}】\n"
                            turn["wait"] = False
                    else:
                        context.appText("你摸了1张，这是你现在的牌:\n" + killerObj.draw(1), "whisper", to=killerObj.name)
                        turn["wait"] = False
                elif turnCmd == "青龙偃月刀":
                    if cardName and cardName[-1] == "杀":
                        turn["kill"]["killed"] = False
                        text += killFunc(senderObj, cardObj, ["杀", targetObj.name])
                    elif command == ".":
                        turn["targets"] = []
                        turn["wait"] = False
                    else:
                        text += "你只能继续出【杀】！\n"
                elif turnCmd == "贯石斧":
                    if command == ".":
                        targets.pop()
                        turn["wait"] = False
                    elif not assertId(sender, array[:2]):
                        text += "序号错误！\n"
                    else:
                        for i in array[:2]:
                            card = senderObj.cards.pop(int(i)-1)
                            cardList.appTrash(card)
                        text += f"{sender}弃置了两张牌，对{targetObj.name}造成伤害！\n"
                        text += senderObj.kill(targetObj.name, turn["kill"]["card"])
                        turn["wait"] = False
                elif turnCmd == "麒麟弓":
                    try:
                        equipment = targetObj.equipments[int(array[1])-1]
                    except (TypeError, IndexError):
                        text += f"{targetObj.name}没有那张牌！"
                    else:
                        text += targetObj.unequip(equipment, True)
                        turn["wait"] = False
                elif turnCmd == "寒冰剑":
                    if command == ".":
                        targets.pop()
                        text += f"{sender}不选择。【杀】依旧生效\n"
                        turn["wait"] = False
                        text += senderObj.kill(targetObj.name, turn["kill"]["card"])
                    elif not assertId(targetObj.name, [i for i in array if i != "手"], True):
                        text += "参数错误！\n"
                    else:
                        for cmd in array:
                            if cmd == "手":
                                array.remove("手")
                                card = targetObj.randomCard()
                                targetObj.cards.remove(card)
                                cardList.appTrash(card)
                                text += f"随机弃置了{targetObj.name}的【{card.name}】"
                            else:
                                equipment = targetObj.equipments[int(array[1])-1]
                                text += targetObj.unequip(equipment, True)
                        turn["wait"] = False
                elif turnCmd == "三尖两刃刀":
                    if command == ".":
                        turn["wait"] = False
                        text += "无事发生。\n"
                    elif verifyArray(array):
                        _target = namePure(array[1])
                        if targetObj.distanceTo(_target) > 1:
                            text += f"{_target}与{targetObj.name}距离大于1！\n"
                        else:
                            try:
                                _card: "Card" = senderObj.cards.pop(int(array[0])-1)
                            except (TypeError, IndexError):
                                text += "参数有误！\n"
                            else:
                                cardList.appTrash(_card)
                                text += f"{sender}弃置了一张牌，对{_target}造成一点伤害。\n"
                                text += countryKill[2][_target].hurt(1)
                                turn["wait"] = False
                    else:
                        text += "参数有误！\n"

            if (not turn["wait"]) and countryKill[0]:
                turn["temp"] = []
                text += f"@{player} 继续出牌。\n"
        # 主动出牌
        elif not turn["wait"] and sender == player:
            # 跳过&弃牌
            if command == ".":
                illegal()
                if len(array) > 1 and not assertId(sender, array[1:]):
                    text += "序号错误！\n"
                else:
                    cards = []
                    for i in array[1:]:
                        card = cardList.appTrash(senderObj.cards.pop(int(i)-1))
                        cards.append(card.name)
                    text += f"{sender}弃置了{'、'.join(cards) or '空气'}\n"
                    if len(senderObj.cards) > senderObj.life:
                        text += f"您的手牌数大于体力值，请弃牌直到剩**{senderObj.life}**张!\n"
                    else:
                        context.appText(text + f"{sender}结束了自己的回合\n\n---\n")
                        senderObj.cards.sweep()
                        return goTurn(context, True)
            elif turn["cmd"] == "pass":
                illegal()
                text += "您正在【乐不思蜀】中，不能出牌！😪\n"
            else:
                cardObj = senderObj.getCard(command)
                if cardObj:
                    cardName = cardObj.name
                else:
                    return context.appText("指令错误！")
                if cardName[-1] == "杀":
                    text += killFunc(senderObj, cardObj, array)
                elif cardName == "桃":
                    if senderObj.life == senderObj.maxLife:
                        text += illegal("您已经满血了！\n")
                    else:
                        text += senderObj.heal(1)
                elif cardName == "桃园结义":
                    for obj in countryKill[2].values():
                        text += obj.heal(1)
                elif cardName == "无中生有":
                    text += f"{sender}摸了两张牌。"
                    senderObj.cards.pop(int(command)-1)
                    context.appText("你摸了2张，这是你现在的牌:\n" + senderObj.draw(2), "whisper", to=sender)
                elif cardName == "五谷丰登":
                    index = countryKill[1].index(senderObj.name)
                    turn["targets"] = countryKill[1][index:] + countryKill[1][:index]
                    cards = []
                    for _ in countryKill[1]:
                        cards.append(cardList.pop())
                    turn["temp"] = cards
                    turn["wait"] = True
                    text += f"{formatTable(cards)}\n以上是摸到的牌，请@{sender} 开始先选(s <序号>)\n"
                
                elif cardName == "决斗":
                    if not verifyArray(array):
                        text += illegal("参数错误！\n")
                    else:
                        target = namePure(array[1])
                        turn["targets"] = [target, sender]
                        turn["wait"] = True
                        text += f"【决斗】：从@{target} 开始，双方轮流出【杀】！"
                elif cardName == "火攻":
                    if not verifyArray(array):
                        text += illegal("参数错误！\n")
                    else:
                        target = namePure(array[1])
                        turn["targets"] = [target]
                        turn["wait"] = True
                        text += f"【火攻】：@{target} 展示一张手牌"
                elif cardName == "借刀杀人":
                    if not verifyArray(array, 3, 2):
                        text += illegal("参数错误！\n")
                    else:
                        lentObj: "Player" = countryKill[2][namePure(array[1])]
                        if not lentObj.isEquipped("weapon", "type"):
                            text += illegal(f"{lentObj.name}没有武器！\n")
                        else:
                            target = namePure(array[2])
                            killCard = None
                            for card in lentObj.cards:
                                if card.name[-1] == "杀":
                                    killCard = card
                                    break
                            if killCard:
                                text += f"自动出了{lentObj.name}的【杀】\n"
                                text += killFunc(lentObj, killCard, ["杀", target])
                                cardName = killCard.name
                            else:
                                for equipment in lentObj.equipments:
                                    if equipment.type == "weapon":
                                        weapon = equipment
                                        break
                                lentObj.equipments.remove(weapon)
                                senderObj.equipments.append(weapon)
                                text += f"{lentObj.name}没有【杀】，{player}获得武器【{weapon.name}】\n"

                elif cardName == "顺手牵羊":
                    text += sheepBridge(senderObj, array, True)
                elif cardName == "过河拆桥":
                    text += sheepBridge(senderObj, array, False)
                elif cardName == "万箭齐发":
                    text += arrowBarbarian(sender, True)
                elif cardName == "南蛮入侵":
                    text += arrowBarbarian(sender, False)

                elif cardName in ["乐不思蜀", "兵粮寸断", "闪电"]:
                    try:
                        target = namePure(array[1])
                        targetObj = countryKill[2][target]
                    except (IndexError, KeyError):
                        text += illegal("参数错误！\n")
                    else:
                        if cardName == "兵粮寸断" and senderObj.distanceTo(targetObj.name) > 1:
                            text += illegal("【兵粮寸断】只能对距离为1的玩家使用！\n")
                        else:
                            for delay in targetObj.delays:
                                if delay.name == cardName:
                                    text += illegal("不能添加同样的判定牌两次！\n")
                                    break
                            else:
                                turn["targets"] = [target]
                                targetObj.delays.append(cardObj)
                                text += f"{target}判定区增加一张牌，{sender}继续出牌。"

                elif cardObj.type in ["weapon", "armor", "+1", "-1"]:
                    text += senderObj.equip(cardObj)
                
                else:
                    text += illegal(f"不能主动出【{cardName}】！\n")
                
                if turn["legal"]:
                    turn["cmd"] = cardName
        else:
            return

        if turn.get("targets") and turn["cmd"][-1] == "杀":
            killer = turn["kill"]["lent"] or turn["player"]
            text += checkKill(countryKill[2][killer], turn["kill"]["card"])

        if turn["legal"]:
            describe = ""
            describe += f"{sender}出了【{cardName}】\n"
            if cardName in DESCRIPTION:
                describe += DESCRIPTION[cardName]
            text = describe + text
            senderObj.cards.remove(cardObj)
        turn["legal"] = True

    context.appText(text)
# 转换轮次(判定&摸牌)
def goTurn(context, next: bool=False) -> str:
    turn = countryKill[3]
    if next:
        turn["player"] = getNext()
        context.appText(f"轮到@{turn['player']}")

    playerObj: "Player" = countryKill[2][turn["player"]]
    initTurn(playerObj.name)
    if playerObj.delays:
        context.appText(f"开始对{playerObj.name}进行判定。")
        context.appText(playerObj.judge())
    if "兵粮寸断" not in turn["temp"]:
        context.appText(f"{playerObj.name}摸了两张牌。")
        context.appText(f"你摸了2张，这是你现在的牌\n{playerObj.draw(2)}", "whisper", to=playerObj.name)
    if "乐不思蜀" in turn["temp"]:
        turn["cmd"] = "pass"
# game over
def gameOver() -> str:
    countryKill[0] = False
    winner = countryKill[1].pop()
    del countryKill[2][winner]
    return winner
# main
def main(context, sender: str, msg: str):
    if msg == "help":
        context.appText(KILLMENU)
    elif msg == "规则":
        context.appText(KILLRULE)
    elif countryKill[0] and sender in countryKill[1]:
        play(context, sender, msg)
    elif msg == "加入" and not countryKill[0]:
        if sender.isdigit() and len(sender) == 1:
            context.appText("请不要使用个位数字昵称！")
        elif sender in countryKill[1]:
            context.appText("你已经加入过了！")
        else:
            countryKill[1].append(sender)
            context.appText("加入成功!")
    elif msg == "退出" and not countryKill[0]:
        if sender in countryKill[1]:
            countryKill[1].remove(sender)
            context.appText("退出成功！")
    elif msg == "开始":
        if len(countryKill[1]) < 2:
            context.appText("需要至少两个人！")
        else:
            countryKill[0] = True
            deal(context)
            first = countryKill[3]["player"] = random.choice(countryKill[1])
            goTurn(context)
            context.appText(f"牌发好了！随机由=={first}==先开始！")

cardList = Cards()