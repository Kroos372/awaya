from static import random, Awaish
from money import bank

OEMENU = "\n".join([
    "简单刺激的猜单双",
    "oe 单/双 <豆数>: 押豆，猜单双",
    "oe . <豆数> ?<次数>: 单人模式、朴实无华、输或翻倍。",
    "oe ? <豆数> ?<次数>: 更加随机的单人模式。",
    "oe check: 查看当前奖池",
    "oe !: 开奖。"
])

class OddEven:
    def __init__(self):
        self.initOE()
    def initOE(self):
        self.odds = {"total": 0, "users": []}
        self.evens = {"total": 0, "users": []}
        self.last = 0
    def bet(self, odds: bool, trip: str, money: int) -> str:
        if money < self.last:
            return f"您押得没有上家钱多({self.last})"
        elif bank.hasMoney(trip, money) != money:
            return "你没有那么多钱……"

        if odds:
            self.odds["users"].append({"nick": bank.getAttr(trip, "name"), "trip": trip, "money": money})
            self.odds["total"] += money
        else:
            self.evens["users"].append({"nick": bank.getAttr(trip, "name"), "trip": trip, "money": money})
            self.evens["total"] += money
        self.last = money
        return f"已成功下注！\n" + self.check()
    def quickBet(self, trip: str, money: int, probability: float=0.5) -> str:
        if money < 0:
            return "好歹押一块钱吧客官~"
        elif bank.hasMoney(trip, money) != money:
            return "你没有那么多钱……"

        while not probability:
            probability = round(random.random(), 2)
        odds = round(1 / probability, 2)
        result = round(random.random(), 3)
        text = f"获胜概率**{probability}**(赔率{odds})\n结果：{result}\n"

        if result > probability:
            bank.delete(trip, money)
            text += "你输了！😭\n" + bank.format(trip, 2)
        else:
            bank.add(trip, money * (odds - 1))
            text += "你赢了！🍾\n" + bank.format(trip, 2)
        return text
    def check(self) -> str:
        odds, evens = ["### 当前局势：", "#### 赌单"], ["#### 赌双"]
        for i in self.odds["users"]:
            odds.append(f"{i['nick']}：{i['money']}豆")
        odds.append(f"共{self.odds['total']}豆。")
        for i in self.evens["users"]:
            evens.append(f"{i['nick']}：{i['money']}豆")
        evens.append(f"共{self.evens['total']}豆。")
        return "\n".join(odds + evens)
    def go(self) -> str:
        if not (self.odds["total"] and self.evens["total"]):
            return "必须两边都有人下注才能开始！"
        
        result = []
        if random.randint(0, 1):
            win, lose = self.odds, self.evens
            result.append("结果是单！")
        else:
            win, lose = self.evens, self.odds
            result.append("结果是双！")

        for user in lose["users"]:
            money = bank.delete(user["trip"], user["money"])
            result.append(f"{user['nick']}失去了{money}豆。")
        for user in win["users"]:
            money = int(user["money"] / win["total"] * lose["total"])
            bank.add(user["trip"], money)
            result.append(f"{user['nick']}获得了{money}豆。")

        self.initOE()
        return "\n".join(result)

oddeven = OddEven()

def main(context: Awaish, msg: str, type_: str):
    trip = context.user["trip"]
    if msg == "help":
        context.appText(OEMENU)
    elif msg == "check":
        context.appText(oddeven.check())
    elif not bank.get(trip):
        context.appText("你还没有银行！")
    elif msg[0] in ".?":
        msg_list = msg.split(" ")
        try:
            money = int(msg_list[1])
            if len(msg_list) > 2:
                times = int(msg_list[2])
            else:
                times = 1
        except:
            context.appText("参数错误！")
        else:
            if times < 0 or times > 10:
                context.appText("次数太多/少啦.")
            else:
                texts = []
                for _ in range(times):
                    if msg[0] == ".":
                        texts.append(oddeven.quickBet(trip, money))
                    else:
                        texts.append(oddeven.quickBet(trip, money, 0.0))
                context.appText("\n---\n".join(texts))
    elif type_ == "whisper":
        pass
    elif msg == "!":
        context.appText(oddeven.go())
    else:
        array = msg.split(" ")
        try:
            money = int(array[1])
        except:
            context.appText("参数错误！")
        else:
            if array[0] == "单":
                context.appText(oddeven.bet(True, trip, money))
            elif array[0] == "双":
                context.appText(oddeven.bet(False, trip, money))
            else:
                context.appText("参数错误！")

