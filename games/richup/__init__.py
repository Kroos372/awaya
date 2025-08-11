from static import Awaish
from .core import GameSystem

RICH_MENU = "\n".join([
    "大富翁，前缀“ru ”",
    "join <flair>: 加入游戏，flair为玩家标识在棋盘上的字符",
    "flair <flair>: 更改标识",
    "quit: 退出游戏",
    "start: 开始游戏",
    "end: 结束游戏",
    "rules: 规则"
])
RICH_RULE = "\n".join([
    "board: 查看棋盘",
    "- board w: 以私信返回",
    "check ?<昵称>: 查看资产",
    "all: 查看所有玩家概览",
    "help <格子序号>: 查看地块详情",
    "————",
    "r: 摇骰子",
    ".: 结束回合",
    "auto: 开启/关闭 自动结束回合",
    "out: 支付\\$50或赦免卡出狱(在狱中时)",
    "gg: 破产",
    "————",
    "buy: 购买地产",
    "sell <序号>: 卖出地产",
    "build <序号> ?<数量>: 盖房子",
    "destroy <序号> ?<数量>: 卖房子",
    "————",
    "trade <昵称> <钱数> ?<序号> ... - <钱数> ?<序号> ...: 发起交易（第一行是自己给出的，第二行是需要对方给的）",
    "- 例：trade Krs_ 0 1 3-400 card （两块地换$400与一张赦免卡）",
    "accept <交易ID>: 同意交易",
    "decline <交易ID>: 拒绝或取消交易",
    "mytrades: 查看自己的交易",
    "tradeof <交易ID>: 查看某个交易",
    "————",
    "支持[richup.io](https://richup.io/)谢谢喵"
])

game = GameSystem()

def main(context: Awaish, sender: str, msg: str):
    game.set_context(context)
    trip = context.user["trip"]
    player = game.get_player(sender, trip)
    msg_list = msg.split(" ")
    if msg == "rules":
        context.appText(RICH_RULE)
    elif msg == "help":
        context.appText(RICH_MENU)

    elif msg == "end" and player:
        game.end_game()
        context.appText("唔，结束了;;;;")
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