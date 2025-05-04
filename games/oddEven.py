from static import bank, random, Context

OEMENU = "\n".join([
    "简单刺激的猜单双",
    "oe 单/双 <豆数>: 押豆，猜单双",
    "oe . <豆数>: 单人模式、朴实无华、输或翻倍。",
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
    def quickBet(self, trip: str, money: int) -> str:
        if money < 0:
            return "好歹押一块钱吧客官~"
        elif bank.hasMoney(trip, money) != money:
            return "你没有那么多钱……"
        if random.random() > 0.5:
            bank.delete(trip, money)
            return "你输了！\n" + bank.format(trip, 2)
        else:
            bank.add(trip, money)
            return "你赢了！\n" + bank.format(trip, 2)
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

def main(context: Context, msg: str):
    trip = context.user["trip"]
    if msg == "help":
        context.appText(OEMENU)
    elif msg == "check":
        context.appText(oddeven.check())
    elif not bank.get(trip):
        context.appText("你还没有银行！")
    elif msg == "!":
        context.appText(oddeven.go())
    elif msg[0] == ".":
        try:
            money = int(msg[2:])
        except:
            context.appText("参数错误！")
        else:
            context.appText(oddeven.quickBet(trip, money))
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

