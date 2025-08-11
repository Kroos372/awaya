from typing import TYPE_CHECKING
from static import randomStr

if TYPE_CHECKING:
    from .board import Land
    from .core import GameSystem
    from .player import Player

class Trade:
    def __init__(self, sender: "Player", sender_items: list["Land | str"],
                 receiver: "Player", receiver_items: list["Land | str"]):
        self.sender = sender
        self.sender_items = sender_items
        self.receiver = receiver
        self.receiver_items = receiver_items

class TradeError(BaseException):
    def __init__(self, message: str=""):
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return self.message

class TradeSystem(dict[str, Trade]):
    def __init__(self, game: "GameSystem"):
        super().__init__()
        self.game = game
        
    def parse_items(self, player: "Player", items: list[str]):
        result = []
        cash = int(items.pop(0))
        if cash > player.cash:
            raise TradeError("钱数不足")
        result.append(cash)
        for item in items:
            if not item:
                continue
            if item == "card":
                result.append("card")
                continue
            land: "Land" = self.game.board[int(item)]
            if land.owner != player:
                raise TradeError(f"{land.f_name} 不是你的")
            if land.houses:
                raise TradeError(f"{land.f_name} 上有房子，无法交易")
            result.append(land)
        return result

    def create(self, sender: "Player", receiver: "Player", msg: str):
        send_receive = msg.split("-")
        try:
            sender_items = self.parse_items(sender, send_receive[0].split(" "))
            receiver_items = self.parse_items(receiver, send_receive[1].split(" "))
        except TradeError as e:
            self.game.appText(e.message)
            return
        except:
            self.game.appText("参数错误")
            return

        trade = Trade(sender, sender_items, receiver, receiver_items)
        trade_id = randomStr()
        while trade_id in self:
            trade_id = randomStr()
        self[trade_id] = trade
        self.game.appText(f"成功发起交易，ID为{trade_id}")
        
    def accept(self, player: "Player", trade_id: str):
        trade = self.get(trade_id)
        if trade is None:
            self.game.appText("ID不存在")
            return
        if trade.receiver != player:
            self.game.appText("你不是该交易的乙方")
            return
        
        self.execute(trade_id)

    def decline(self, player: "Player", trade_id: str):
        trade = self.get(trade_id)
        if trade is None:
            self.game.appText("ID不存在")
            return
        if trade.receiver != player and trade.sender != player:
            self.game.appText("你不是该交易的双方")
            return
        del self[trade]
        self.game.appText("已取消本次交易")

    def check_legal(self, sender: "Player", receiver: "Player", items: list["Land"]):
        items = items.copy()
        cash = items.pop(0)
        if cash > sender.cash:
            raise TradeError(f"{sender} 钱数不足")
        if items.count("card") > sender.parden_card:
            raise TradeError(f"{sender} 赦免卡不足")
        for item in items:
            if item == "card":
                continue
            elif item.owner != sender:
                raise TradeError(f"{item.f_name} 不是 {sender} 的")
        
    def execute_items(self, sender: "Player", receiver: "Player", items: list["Land"]):
        self.check_legal(sender, receiver, items)

        sender.give_cash(receiver, items.pop(0))
        for item in items:
            if item == "card":
                sender.parden_card -= 1
                receiver.parden_card += 1
            else:
                item.change_owner(receiver)

    def execute(self, trade_id: str):
        trade = self[trade_id]
        try:
            self.execute_items(trade.sender, trade.receiver, trade.sender_items)
            self.execute_items(trade.receiver, trade.sender, trade.receiver_items)
        except TradeError as e:
            self.game.appText(e.message)
            return
        del self[trade_id]
        self.game.appText("交易成功")
    
    def format_items(self, items: list["str | int | Land"]):
        cash = items.pop(0)
        result = [f"- 现金：${cash}"]
        for item in items:
            if item == "card":
                result.append("- 赦免卡")
            else:
                result.append(f"- {item.f_name}")
        return "\n".join(result)
    def format(self, trade_id: str) -> str:
        trade = self.get(trade_id)
        if trade is None:
            return ""
        text = [
            f"### {trade_id}",
            f"甲方：{trade.sender}，乙方：{trade.receiver}",
            "甲方物品：",
            self.format_items(trade.sender_items),
            "————",
            "乙方物品：",
            self.format_items(trade.receiver_items),
        ]
        return "\n".join(text)
    def trade_of(self, player: "Player") -> str:
        text = []
        for trade_id, trade in self.items():
            if trade.sender == player or trade.receiver == player:
                text.append(self.format(trade_id))
        
        return "\n\n---\n".join(text)