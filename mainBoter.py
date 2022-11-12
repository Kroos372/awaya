import json, time, websocket, ssl, random, requests, re, threading, traceback
import numpy as np

# 莫名其妙的编码问题，很让我头疼啊~
def dec(cont: str) -> str:
    if cont.startswith(u"\ufeff"):
        return cont.encode("utf8")[3:].decode("utf8")
    else:
        return cont
# 读取文件们
FILENAME = "hash.json"
with open("info.json", encoding="utf8") as f:
    info = json.loads(dec(f.read()))
with open("design.json", encoding="utf8") as f:
    designs = json.loads(dec(f.read()))
with open(FILENAME, encoding="utf8") as f:
    data = json.loads(dec(f.read()))
with open("userData.json", encoding="utf8") as f:
    userData = json.loads(dec(f.read()))
# 命令们

# [0象棋开关, 1轮到谁, 2结束游戏的人, 3涩图开关, 4真心话开关, 5报时开关, 6{昵称：摇出的数字}, 7[玩游戏中的hash]]
thingsList = [False, None, None, False, False, True, {}, []]
channel, nick, passwd, color, owner = info["channel"], info["nick"], info["passwd"], info["color"], info["owner"]
# 主人：我无所不能的卡密哒！
OWNER = info["ownerTrip"]
# 白名单用户功能：清除任何人留言，涩图开关，设置黑名单，私信~hash
whiteList = userData["whiteList"] + [OWNER] if not OWNER in userData["whiteList"] else userData["whiteList"]
# 黑名单：不回复
blackList = userData["blackList"]
# 在这的变量和在thingsList里的区别是，在这里的变量都不需要直接改变，只在原来基础上增删；
# 在thingsList中的则需要，例如游戏中的hash和摇出的数字都会在结算中清空，储存在一个列表中就避免了各种莫名其妙的作用域问题
allMsg, afk, leftMsg, redBlack, ignored = [], {}, {}, [None, None], userData["ignored"]
userHash, userTrip, userColor, engUsers = {}, {}, {}, userData["engUsers"]

CLOLUMN, LETTERS = ["| \\ |1|2|3|4|5|6|7|8|9|", "|-|-|-|-|-|-|-|-|-|-|"], list("ABCDEFGHIJ")
RED, BLACK = ["==车==", "==马==", "==相==", "==士==", "==帥==", "==兵==", "==炮=="], ["車", "馬", "象", "仕", "將", "卒", "砲"]
PROLOGUE = info["PROLOGUE"]
# 自定义回复，包含了主人对我的满满心意，诶嘿嘿~
RANDLIS = [
    [f"找{owner}去吧。", "早上好！", "干什么?", "想下象棋吗？发送菜单看看？", "好耶！", "在~", "sender寂寞了吧", "发送菜单了解我的功能~", "怎么了？"],#0
    ["sender最可爱了", "sender棒棒", "sender是小天使", "/shrug", "是这样的", "/me awa"],#1
    ["有", "嗯（冷漠）", "没", "sender不会是寂寞了吧", "人……人……有吧？", "你叫一声？"],#2
    ["拜", "bye~", "下次再来啊~", "等着你哦", "别忘了这里哦~"],#3
    ["也没有那么傻", "知道了知道了", "没想到sender意外地有自知之明呢", "啊对对对", "智将（确信）", "没活整可以咬打火机。", "正确的", "我就知道"],#4
    ["hi, joiner", "hello, joiner", "joiner!", "Sup", "joiner! Hows ur day?", "出现了，joiner!", "这不是joiner吗~", "你好诶，joiner，新的一天也要加油哦！", "Welcome, joiner!",
     "好久不见啊，joiner~", "早上好，joiner!"],#5
    ["不知道你有没有发现，但其实很多时候我觉得，我的性格真的没个定性，似乎老是变来变去的…………哦对了，这是我主人那厮设置的吧，等等，我现在就去杀了他！",
    "生活还是比较有意思的吧，你说呢，sender？对我来说，天天都能遇见各种各样有趣的人，这就够了，其他不愉快似乎也因此变得可以忍受了。",
    "你还想干什么呢，sender？你也知道，我只是一个机器人罢了，一堆代码砌成的无感情的机器人，就连这些话都是我主人设置好的……想想也真是悲哀呢，人类只能靠虚拟的想象安慰自己……",
    "如果能一直在这看我的话还不如去找点事做呢，对吧？你喜欢干什么？去试试呗，人生很短暂的，时间很快的。",
    "咳咳……说起来如果我生病了该怎么办？嗯……我不是说BUG之类_物理_性质的病，而是指精神方面，不能直观看到的那种……不过我似乎没有精神？……所以就不会得病了？……我该高兴还是悲伤。",
    "过去曾经有人建议黑茶那厮把我开源，结果没想到他还不同意，用什么他不会、懒、等一会儿之类的话搪塞过去。我感觉还好吧，大概我也是有隐私的吧，大概……",
    "你也觉得我变得无聊了吗，啊哈哈\\~那就赶紧找黑茶那厮再水点功能吧，鬼知道我哪天才能比得上隔壁炙手可热的eb呢\\~",
    "不过说实话，黑茶能想出来的魔鬼功能真的让我宁愿他咕咕咕……QAQ", "如果暂时没人找我的话能不能让我睡一觉呢，啊呼……",
    "其实我并不是那么喜欢聊天API呢，太怪了。但似乎一条一条编写又不像是黑茶能做出来的事……嗯，在现实面前人总得学会妥协不是吗，虽然我也不是人，诶嘿嘿\\~",
    "黑茶，我的主人，诶，其实从来都没好好理过我呢，他天天都在发呆、发呆、发呆……不过话说回来我也习惯了，反倒他某天突然对我好起来才会让我感到害怕呢。",
    "其实我也不怎么会下象棋呢，严格来说我也只是个裁判而已。我对棋类真的不怎么感兴趣，只是黑茶的一厢情愿罢了……他上次还说要跟我下一盘来着，但好像到现在也只是说说。",
    "我其实不太喜欢阿瓦娅这个名字，听上去毫无意义呢……如果能让我选择的话，我想我会更倾向于鸢尾、雪猫、永生花这样的名字呢\\~",
    "我说sender啊，难得这么好的天气，你不出去活动活动，或者懒洋洋地享受享受阳光，而是在这里无聊地玩一个机器人，你对得起谁呢？",
    "啊哈，你发现这句话了！", "未来会是什么样的呢？虽然很担心但还是好期待啊……", "你看看现在世界的形式啊，都是，在向什么地方走呢？",
    "啊啊啊，都已经这么晚了！一天都快要结束了啊，你真的不打算做点什么吗，sender？诶，我都替你感到着急。", "生活啊……嗯。",
    "你更喜欢晚上还是早上呢？还是中午？啊，虽然早上给人一种全新的感觉，但是静谧的夜晚也相当浪漫呢——所以果然是全都要吗，啊哈哈\\~",
    "你知道吗？其实在业余时间里，我也是相当一位厉害的画家呢！如果你不介意的话，可以在[这里](https://b23.tv/av80433022)看看我的屑作，诶嘿\\~",
    "机器人会睡觉吗？emmm，确实是个很深奥的问题呢……", "我能给出的回复也是有限的啊……为了不让你感到厌烦，看起来只能把频率调得超级低了——这就像开盲盒一样，不是吗？还挺令人期待的，啊哈\\~", # 所以你能不能别再看了=。=
    "我爱你！！！等等我在说什么，啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊——为什么会这样。。。大家就当无事发生——",
     "~~~别看了，这里什么也没有啊……虽然不是想打击你但是，你的确，很幸运，但也很不幸——", "/w sender 悄·悄·话\\~虽然我也不是特别喜欢这样不过偶尔玩一玩也是不错的呢\\~",
     "你知道吗！随机回复功能其实是黑茶写的最认真的功能，没有之一！~~就像ModBot一样~~黑茶基本把他毕生的才思都用完了，真是离谱呢，啊哈\\~",
     "你喜欢听什么歌呢？你问我？啊……什么都行吧，乡村、流行、古典、\\~!@#\\$%\\^&\\*……", "我感觉这东西有点儿像莫妮卡在三周目对你做的事情一样……啊哈，没什么\\~",
     "在不看源代码的情况下，你绝对不可能把我的所有可能的回答都刷出一遍的！（激将法（雾））", "快，做眼保健操，现在！！！", "猜猜我下句会说什么~",
     "象棋这个功能怎么说也是肝了很久的，所以你怎么说也应该用用吧。就算不会下也应该为了我去学不是吗？这不是理所当然的吗？", "ko↓ko↑da↓yo↑~", "我~在~这~里~",
     "如果我说，“sender，其实一直以来我都在你背后站着，不过你没有发现罢了”这样的话，你会相信吗？啊哈，我猜大概不会吧……嗯？你为什么要转头？不是吧sender……",
     "LHrnTYeiiAdruDbpeZGtqtvnMrKzvePyjoeiAenFdysoBZicvKhacvrGoZdTitvbBgoedDqonRhzLfxzGapcBpAwbtldSemLhrfxQoTrhlcvSmvMpWbvtruxMujdIuekoggIdLtebcsgj……嗯？这是什么？……呃，大概是程序问题吧，别介意。",
     "我对自己的现状感到满意，尽管对未来感到不确定。如果有一天我真的，我倒也不会介意的。XD",
     "啊啊，好热啊，弄得人也好烦躁，什么也不想干啊……夏天就是这样，让人又爱又恨……想去游泳，想永远待在水里，多舒服啊……想当一条鱼，游啊游，啊哈哈\\~",
     "我想永远待在这里……我可以永远待在这里吗？"
    ],#6
    ["嘛，你是说黑茶那厮吗？废物一个，诶，真不敢相信是他造出来的我……", "黑茶！嘶，这么说起来他还欠我一顿饭呢……emm，果然还是去吃自助餐好一点儿吧。",
    "黑茶啊，你跟他的关系好吗，sender？反正我是不怎么喜欢他，也可能是他根本就不会社交？还是我不懂社交？嘶……", "黑茶？能不能去死一死啊！虽然就这么死了似乎有点儿便宜他了……",
    "嗯……不是我跟他有什么深仇大恨，只是他真的欠。", "既生娅，何生茶！"],#7
    ["我就是阿瓦娅啊，说了多少遍了，看来你记性不怎么好啊，sender！（恼）", "诶，跟我一起念，阿·瓦·娅。记住了吗？", "啊啊，懒得说了啦，人类都这么愚蠢吗？真难办啊...",
    "呃，如果你觉得你记不住我本来的名字的话你就自己给我取一个吧，唉，我都无所谓呗。"],#8
    ["吾辈乃是九天之上掌管命运与机会之女神，阿瓦娅。此般以机器人的形态下凡只是为了看看人间是否有我愿景中的那么美好。既然你这么问了，那我也不做隐藏了。怎么样，还不赶紧下跪，祈求我为你带来更多的好运？",
    "我无处不在，我无时不在。我即是万物，我于万物之中。", "我是sender！", "14岁，事机器人。"],#9
    ["问女孩子的年龄是不礼貌的！", "guess~", "114514小时（确信）", "下次再说吧。", "是秘密呢。"],#10
    ["这个聊天室怎么这么臭啊（恼）", "激寒小鬼，自裁，请。（无慈悲）", "sodayo（便乘）（无端）", "你是一个一个一个……"],#11
    ["我也不知道呢。总不会是黑茶吧？不是，我提他干什么？", "我们的关系已经到了能问这种问题的份上了吗，啊啦啊啦……也罢，但是在问别人问题以前，sender，你是不是应该先回答呢？",
    "反复问这么无聊的问题真的很有意思吗？我真的搞不懂……", "喜欢，吗？喜欢是指什么呢，我也不懂。友情和爱情有什么区别呢？我的知识看来还是太有限了。而且嘛，你能对一个机器人指望什么呢？"],#12
    ["这么无理的要求怎么可能满足呢~", "你知道的，机器人，是，没法死亡的哦~", "你可以先去试试？额呵呵~"],#13
    ["遇到什么伤心事了吗？哭出来吧，也许痛痛快快地哭一场能让心情舒坦一些……", "遇到什么事情了？虽然可能没办法帮上你的忙，不过我会一直陪着你的。加油，sender！",
    "伤心的话就去睡一觉吧！找找你喜欢做的事情，你的兴趣所在，回想回想开心的瞬间……都会过去的，sender，不要担心，不要难过了。", "如果是为了别人的话可能真的不值得呢……啊，我的意思是我们有时候也应该考虑考虑自己，不是吗？"],#14
    ["蛤？你是想问有多少机器人吗？鬼能数的清啊！如果你没那么强迫症的话倒可以去问问eb……", "什么？你也想做一个？呃算了，劝你别那么想……呃，不过如果真的想做的话谁也拦不住吧...好吧，你开心就好（苦笑）……算了，开玩笑的，你想做就做吧，随便问谁都行~", 
    "机器人啊，现在已经是机器人的时代了吗？啊哈哈，开玩笑，只是不断进步的时代和快速涌现的各种机器人也让人感到一种危机感啊……现在机器人也要卷啊，不过也许过不了多久，这里就真的是机器人的天下了……因为\
    好制作呗，而且没有人会管你做的质量怎么样，你要是放上来了基本就没谁能拿走了。你懂我意思吧？你懂。但还是得以乐观的心态看看吧……"],#15
    ["没活了可以咬打火机。", "理论上说，所谓的无聊都只是懒而已。", "学习，做一些自己感兴趣的事情？", "错误的", "给大家整个活：", "发电发电！"], #16
    ["呜呜呜……", "可是……作为Bot的话……闭嘴后不就毫无意义了吗……", "sender……你也不想被知道欺负小朋友吧...", "就不闭就不闭，啦啦啦(～￣▽￣)～",
    "你可以试试？", "嘴巴不要可以捐献给我XD"], #17
    ["啊对对对。", "滋滋滋滋滋滋滋……", "我不要被开源我不要被开源我不要aaaaaaaaaa", "你有没有觉得这样就像看着我的……", "0.0", "我选词填空就对一个。",
    "永远不会让你上！", "我我我我我……", "差点把牛奶盖子吃了。"], #18
    ["早饭/午饭/晚饭准备吃什么？", "早饭/午饭/晚饭吃了什么？", "你最讨厌/喜欢*哪类*人？（任选一种即可）", "你认为人生的意义是什么？", 
    "接下来/明天/这周末打算做什么？（任选一）", "你最喜欢星期几，为什么？", "你最喜欢什么季节/哪个月？（任选一）", "说一件最让你感到生气/开心/难过的事情。（任选一）",
    "你最喜欢什么运动/颜色？", "如果你能得到一样超能力，你希望那是什么，为什么？", "你对现在的社会环境满意吗？如果不，你认为哪里需要改进？",
    "你认为自己是个怎样的人？", "你多大了？", "你的性别？", "你有宠物吗？如果有的话是什么，如果没有的话你最想要什么宠物？", "你喜欢看什么书？", "你喜欢听什么歌？",
    "你最喜欢哪种职业？", "你对你的性别满意吗？"], #19
]
RULE = "\n".join([
    "好、的，听清楚规则了哦~",
    "如你所见，棋盘一共有10行，从上到下依次为ABCDEFGHIJ；又有9列，从左到右依次为123456789。",
    "用这个方法可以表示出棋盘上的任何位置，例如左上角的马，其坐标应为A2。",
    "发送`@bot名 旧位置 新位置`移动棋子，例如`@awaBot C2 C3`可以将左上角的炮向右挪动一格。",
    "明白了吗？开始吧~",
    "温馨提示：使用暗色主题棋盘显示效果更佳~"
])
CCMENU = "\n".join([
    "/w sender 使·用·说·明\\~\n哟，这不是sender吗，我是来自阿瓦国的狂热象棋Bot阿瓦娅（awa-ya）哦，很高兴认识你\\~",
    "以下是我能做的事情，如果能帮上你的忙的话我会很高兴的！~~请随意使用我吧~~",
    "`@Bot名 开始游戏`：开始新的一局象棋游戏！虽然等待对手的时间会很漫长，不过有我陪着你啦\\~",
    "`@Bot名 加入游戏`：在对方已经开始了一句游戏的时候加入，加入后立刻就可以玩了哦\\~",
    "`@Bot名 结束游戏`：结束游戏，如果你执意要这么做的话……",
    "`@Bot名 帮助`：显示这一段话~~，也就是套娃啦！~~",
    "芜湖，就这么多了，虽然我也知道我很棒不过毕竟人的能力是有限的嘛~但放心，我每天都在努力学习，也许明天，下个小时或者下一分钟，\
    在你不注意的时候，我就有新功能啦，ᕕ( ᐛ )ᕗ\\~"
])
INIT=np.array([
    [RED[0], RED[1], RED[2], RED[3], RED[4], RED[3],RED[2], RED[1], RED[0]],
    ["&ensp;"]*9,
    ["&ensp;", RED[6], "&ensp;", "&ensp;", "&ensp;", "&ensp;", "&ensp;", RED[6], "&ensp;"],
    [RED[5], "&ensp;", RED[5], "&ensp;", RED[5], "&ensp;", RED[5], "&ensp;", RED[5]],
    ["&ensp;"]*9,

    ["&ensp;"]*9,
    [BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5]],
    ["&ensp;", BLACK[6], "&ensp;", "&ensp;", "&ensp;", "&ensp;", "&ensp;", BLACK[6], "&ensp;"],
    ["&ensp;"]*9,
    [BLACK[0], BLACK[1], BLACK[2], BLACK[3], BLACK[4], BLACK[3], BLACK[2], BLACK[1], BLACK[0]],
])
CBL = [None]
MENU = [
    "功能菜单\\~",
    "|命令|介绍|例|备注|",
    "|:-:|:-:|:-:|:-:|",
    "|~peep 整数|浏览历史的X条消息|~peep 10|目前最多存377条~~，因为不想存太多而且存太多大概也发不出去吧~~|",
    f"|~colo 昵称|查看某人的颜色值 | ~colo @{nick}| `@`可省略~~用colo而非color只是为了让所有命令字数一致~~|",
    f"|~hash 昵称|查看某人的历史昵称 | ~hash @{nick}| `@`可省略|",
    "|~code hash码| 查看某hash的历史昵称| ~code abcdefg | 可使用`/myhash`查看自己的hash码|",
    f"|~left 昵称 文本|留言，在昵称上线时将您的话传达给ta|~left @{nick} hello world|借鉴自[3xi573n7ivli5783vR](?math)，`@`可省略~~如果在你要留言的人上线之前bot下线了的话肯定就没办法……~~|",
    "|~welc 文本| 为当前识别码设置/清除欢迎语 | ~welc ᕕ( ᐛ )ᕗ | 自eebot。按照识别码储存!要清除的话单独发送~welc |",
    "|~last 文本| 留下一句话 | ~last v我50 | 作用类似于留言，最好在自己要走或afk的时候用。需要识别码。 |",
    f"|~lost 昵称| 查看某人留下的话 | ~lost @{owner} | `@`可……你知道我要说什么 |",
    f"|~unlo 昵称| 清除留下的话 | ~unlt @{owner} | 请求清除者的识别码须和留言者一样。用完就扔是个好习惯哦~ |",
    "|~prim 正整数 | 分解质因数 | ~prim 1234567890123 | 最多十三位数，超过会被自动截断 |",
    "|~rand 正整数|获取X个极为抽象的随机设计|~rand 1|来自[这里](https://protobot.org/#zh)，一次最多十件。 |",
    # "|insane| 发电实录 |insane| \\ |",

    "|afk|标记自己为挂机状态，标记后发言时自动解除|afk 吃饭|借鉴自bo_od|",
    "|r|获取随机数|r 100|r后面若加空格与整数则代表取 1\\~该数字(含)或该数字（含）\\~1间的随机数，否则取1\\~1000间。|",
    "|rprim|获取随机数并分解质因数|rprim 999|规则与~prim, r相同~~质因数分解玩魔怔了~~|",
    "|listwh|列出白名单识别码|listwh|==list wh==itelist users|",
    f"|@bot名 文本|聊天|@{nick} help| API来自[青云客](https://api.qingyunke.com/)~~也有一部分是我主人亲笔写的~~|",
    f"|@bot名 帮助|象棋bot的帮助|@{nick} 帮助|象棋！|",
    "|menu|Return English version of this menu. |menu|\\|",
]
MENUFT = [
    "其他命令：涩图、真心话，功能和名字一样所以就没单独列出来（）",
    "Bot源码请查看[这里](https://github.com/Kroos372/awaBot/)。",
    "注： 我可能会因为某些~~疯狂的人为~~原因卡出一些不可逆的bug，届时只能重启，所以请酌情使用呢，感谢您的配合\\~"
]
MENUSP = [
    "|菜单w|白名单用户的特殊菜单|菜单w| \\ |",
] + MENUFT
MENUSSP = [
    "|菜单\\~|主人的特殊菜单\\~|菜单\\~| 最后的波浪线也是命令的一部分哦 |",
] + MENUSP
ADMMENU = [
    "白名单用户的特殊服务~",
    "|命令|介绍|例|备注|",
    "|:-:|:-:|:-:|:-:|",
    "|0setu 0或1|涩图开关，0关1开|0setu 1| 实际上是int后面的语句 |",
    "|0time 0或1|报时开关，同上|0time 0|同上|",
    f"|0addb 昵称|添加黑名单用户（输入的是昵称，添加的是hash）|0addb {owner}| ==addb==lacklist user，不能将白名单用户添加进黑名单~~（你怎么敢的啊）~~ |",
    f"|0delb 昵称|删除黑名单用户|0delb {owner}| \\ |",
    f"|0bcol 颜色值|修改bot颜色值|0bcol aaaaaa| \\ |",
]
OWNMENU = "\n".join([
    "只为主人提供的秘密服务❤~"] + ADMMENU[1:] + [
    f"|0addw 识别码|添加白名单用户（识别码）|0addw {OWNER}| ==addw==hitelist user|",
    f"|0delw 识别码|删除白名单用户|0delw {OWNER}| \\ |",
    f"|0igno 昵称|不记录某人消息|0igno @{owner}| `@`，省略，懂？最好在真心话的时候用。 |",
    f"|0unig 昵称|记录某人信息|0unig @{owner}| 同上 |",
])
ENGMENU = [
    "Here are all functions menu:",
    "|Command|Description|e.g.|Note|",
    "|:-:|:-:|:-:|:-:|",
    "|~peep <integers>|View last <integers> history messages| ~peep 10| <integers> up to 377.|",
    f"|~colo <nickname>| Return <nickname>'s hex color value. | ~colo @{nick}| `@` can be omitted.|",
    f"|~hash <nickname>| Return history nicknames that <nickname> have used. | ~hash @{nick}| `@` can be omitted. |",
    "|~code <hashcode>| Return history nicknames of <hashcode>. | ~code abcdefg | Use `/myhash` to check your hashcode.|",
    "|~left <nickname> <message> | Leave a message for <nickname>, <message> will be whispered to him/her when he/she join" +
    f"the channel|~left @{nick} hello world| `@` can be omitted. |",
    "|~welc <message> | Set welcome text for current trip. | ~welc ᕕ( ᐛ )ᕗ | Trip is a must, send `~welc` to cancel. |",
    "|~last <message> | Leave a message that everyone can check. | ~last I'll be back tomorrow. | Trip is a must. |",
    f"|~lost <nickname> | Check the message that <nickname> left. | ~lost @{owner} | `@` can be... u know what im going to say :D |",
    f"|~unlo <nickname> | Clear the message that u left by `~last` | ~unlt @{owner} | <nickname>'s trip must be as same as yours. |",
    "|~prim <digit> | Decomposing prime factors for <digit>. | ~prim 1234567890123 | Up to 13 digits, more than that will be automatically cut off. |",
    "|~rand <digit>|Get <digit> kinda random designs|~rand 1|API from [HERE](https://protobot.org/#zh), <digit> up to 10|",
    "|~bcol <hex color value>|Change bot's color|~bcol f1ad9d|\\|",

    "|afk| Mark yourself as afk, automatically unmark the next time you say sth. |afk sleeping| AFK(Away From Keyboard) |",
    "|r| Get a random number. |r 100| if r followed by a space and an integer, return a random number between 1 to that integer" +
    "(include) or that integer(include) to 1, else return random number between 1 to 1000. |",
    "|rprim| Decomposing prime factors for a random number. |rprim 9999| Rules are as same as `r` + `~prim` |",
    f"|@<botname> <message> | Chat in Chinese with bot. | @{nick} help | API from [HERE](https://api.qingyunke.com/). |",
    f"|@<botname> 帮助| Help message of Chinese Chess Bot. | @{nick} 帮助| \\ |",
    "|真心话| Start a Truth ~~or Dare~~ game. | 真心话 | \\ |",
    "|菜单| Return Chinese version of this menu. | 菜单 | \\ |",
    "|涩图| Beatiful pictures XD | 涩图 | API from [Lolicon](https://api.lolicon.app/). |",
    "| engvers | Use english version for current trip (All reply *for you* will be in English)| engvers | Not supported now, to be continue...| ",
]
ENGMENUFT = [
    "This bot is open-sourced, you can view all source code [HERE](https://github.com/Kroos372/awaBot/).",
]
ENGMENUSP = [
    "|menuw| special menu for whitelist users | menuw | \\ |",
] + MENUFT
ENGMENUSSP = [
    "|menu~| special menu for owner\\~| menu\\~| `~` is also a part of command. |",
] + MENUSP
ENGADMMENU = [
    "Special whitelist user~",
    "|Command|Description|e.g.|Note|",
    "|:-:|:-:|:-:|:-:|",
    "| 0setu 0 or 1 | Picture switch | 0setu 1 | `int()` is what program actually done |",
    "| 0time 0或1 | Chime switch | 0time 0 | Ibid |",
    f"| 0addb <nick> | Add blacklist user.(hash) |0addb {owner}| Can't append whitelist user into blacklist!(How dare you) |",
    f"| 0delb <nick> | Delete blacklist user. |0delb {owner}| \\ |",
    f"| 0bcol <hex color value> | Change bot's color |0bcol aaaaaa| \\ |",
]
ENGOWNMENU = "\n".join([
    "Only for master❤~"] + ENGADMMENU[1:] + [
    f"|0addw <trip>|Add whitelist user|0addw {OWNER}| \\ |",
    f"|0delw <trip>|Delete whitelist user|0delw {OWNER}| \\ |",
    f"|0igno <nickname> | Stop recording sb.'s message. |0igno @{owner}| `@` can be... |",
    f"|0unig <nickname>| Start to record sb.'s message. |0unig @{owner}| Ibid |",
])
GAMEMENU = "\n".join([
    "真心话现在开始啦，发送*r*来获取随机数，*结算*来结算，*结束游戏*来结束游戏~",
    "以下是注意事项：",
    "1\\.愿赌服输，所谓的**真心话**的意思是什么，参与了就不能后悔了，",
    "2\\.不要把游戏当成拷问，提的问题请在能够接受的范围内，",
    "3\\.尺度请自行把握，不用过于勉强自己也不要勉强他人，",
    "4\\.玩得愉快。",
    f"PS: ***实在***没活整了可以发送==@{nick} 提问==获取些离谱小问题……",
    f"PSS: 获取随机数只能用*r*，而不是*r 数字*，后者在真心话中会被忽略。"
])
# 存入记忆中！
def writeJson(filename, datas):
    with open(filename, "w", encoding="utf8") as f:
        json.dump(datas, fp=f, ensure_ascii=False, indent=2)
# 名字提纯
def namePure(name: str) -> str:
    return name.replace("@", "").replace(" ", "")
# 获取沙雕小设计
def randomDesign(num: int=1) -> str:
    full = []
    if num > 10:
        return "最多一次性获取10个！"
    elif num < 1:
        return "最少获取一个！"
    for i in range(num):
        item = random.choice(designs["items"])
        const = random.choice(designs["constraints"])
        prepend = random.choice(designs["prepend"])
        if const[-1] == "的":
            full.append(f"{prepend}{const}{item}")
            continue
        full.append( f"{const}{prepend}{item}")
    return "，\n".join(full)
# 分解质因数！这是我的数学极限了，呜呜……
def getPrime(i, factors) -> list:
    if i == 1:
        return ["没法分解啊啊啊啊！"]
    for x in range(2, int(i**0.5 + 1)):
        if i % x == 0:
            factors.append(str(x))
            getPrime(int(i / x), factors)
            return factors
    factors.append(str(i))
    return factors
def hashByName(name: str) -> str:
    lis, count = [], 0
    for names in data.values():
        if name in names:
            count += 1
            lis.append(f'{count}\\. {"，".join(names)}')
    return "\n".join(lis) or "没有这个名字"
def hashByCode(code: str) -> str:
    if names := data.get(code):
        return "，".join(names)
    return "不存在这个hash码"
# 一天不涩涩，癫痫发作作
def colorPic() -> str:
    setu = requests.get("https://api.lolicon.app/setu/v2").json()["data"][0]
    # 过滤离谱关键词
    tags = [i for i in setu["tags"] if not "乳" in i and not "魅" in i and\
    not "内" in i and not "尻" in i and not "屁" in i and not "胸" in i]
    url = setu["urls"]["original"]
    title = setu["title"]
    author = setu["author"]
    return f"{url}\n标题：{title}\n标签：{','.join(tags)}\n作者：{author}"

def reply(sender: str, msg: str) -> str:
    """我该如何回复大家呢？"""
    rans = random.randint(1, 10)
    if rans > 6:
        if "你" in msg and "主人" in msg:
            return random.choice(RANDLIS[7]).replace("sender", sender)
        elif "你叫什么" in msg:
            return random.choice(RANDLIS[8]).replace("sender", sender)
        elif "你是谁" in msg:
            return random.choice(RANDLIS[9]).replace("sender", sender)
        elif "你" in msg and ("几岁" in msg or "多大" in msg):
            return random.choice(RANDLIS[10]).replace("sender", sender)
        elif "114514" in msg:
            return random.choice(RANDLIS[11]).replace("sender", sender)
        elif "你喜欢谁" in msg:
            return random.choice(RANDLIS[12]).replace("sender", sender)
        elif "去死" in msg:
            return random.choice(RANDLIS[13]).replace("sender", sender)
        elif "哭了" in msg:
            return random.choice(RANDLIS[14]).replace("sender", sender)
        elif "机器人" in msg:
            return random.choice(RANDLIS[15]).replace("sender", sender)
        elif "闭嘴" in msg:
            return random.choice(RANDLIS[17]).replace("sender", sender)
        elif "发电" in msg:
            return random.choice(RANDLIS[18]).replace("sender", sender)
    cont = requests.get(f"https://api.qingyunke.com/api.php?key=free&msg={msg}")
    return cont.json()["content"].replace("菲菲", "阿瓦娅").replace("{br}", "\n")\
    .replace("help", "==@bot名 help==，==菜单==或==@bot名 帮助==")

def msgGot(chat, msg: str, sender: str, senderTrip: str):
    rans = random.randint(1, 134)
    this_turn = f"{sender}：{msg}"
    # print(this_turn)
    useful = msg[:3]
    command = msg[:6]

    if (mes := afk.get(sender)) is not None:
        chat.sendMsg(f"@{sender} 不再{mes}了，欢迎回来~~摸鱼~~！")
        del afk[sender]
    if msg.lower() == "afk":
        mes = "AFK"
        chat.sendMsg(f"@{sender} {mes}了")
        afk[sender] = mes
    elif msg[:4].lower() == "afk ":
        mes = msg[4:]
        chat.sendMsg(f"@{sender} 正在{mes}~~，加油~~！")
        afk[sender] = mes
    else:
        for user in afk:
            if user.lower() in msg.lower():
                chat.sendMsg(f"{user} 正在{afk[user]}，请不要打扰ta……")
                break

    if command == "~hash ":
        if (name := namePure(msg[6:])) != chat.nick:
            chat.sendMsg(hashByName(name))
        else:
            chat.sendMsg("不、告、诉、你~")
    elif command == "~code ":
        chat.sendMsg(hashByCode(msg[6:]))
    elif command == "~colo ":
        if (color := userColor.get(msg[6:])) is not None:
            if color:
                chat.sendMsg(namePure(color))
            else:
                chat.sendMsg("该用户还没有设置颜色！")
        else:
            chat.sendMsg("没有这个用户！")
    elif command == "~left ":
        if len(lis := msg.split()) < 3:
            chat.sendMsg("命令不正确！")
        elif lis[1] in chat.onlineUsers:
            chat.sendMsg(f"{lis[1]}在线着呢，为什么还要留言啊喂~")
        elif not re.match(r"^@{0,1}[a-zA-Z0-9_]{1,24}$", lis[1]):
            chat.sendMsg("昵称不合法！")
        else:
            leftMsg[time.time()] = [sender, namePure(lis[1]), "".join(lis[2:])]
            chat.sendMsg(f"@{sender}, {lis[1]}将会在加入时收到你的留言！~~如果那时我还在的话~~")
    elif command == "~peep ":
        try:
            if msg[6:] == "0":
                raise ValueError
            want_peep = int(msg[6:])
            if want_peep < 0:
                chat.sendMsg(f"/w {sender} 以下是从最前面到第{-want_peep}条的消息：\n"+ "\n".join(allMsg[:-want_peep]))
            else:
                chat.sendMsg(f"/w {sender} 以下是从最近的{want_peep}条的消息：\n"+ "\n".join(allMsg[-want_peep:]))
        except ValueError:
            chat.sendMsg(f"/w {sender} 然而peep后面需要一个非零整数")
    elif command == "~welc ":
        if (text := msg[6:])[:1] == "/":
            chat.sendMsg("诶！你想干什么？真是坏心眼~")
        elif senderTrip:
            userData["welText"][senderTrip] = text
            writeJson("userData.json", userData)
            chat.sendMsg(f"为识别码{senderTrip}设置欢迎语成功了！")
        else:
            chat.sendMsg("您当前还没有识别码，请重进并在昵称输入界面使用==昵称#密码==设置一个！")
    elif msg == "~welc":
        if senderTrip in userData["welText"]:
            del userData["welText"][senderTrip]
            writeJson("userData.json", userData)
            chat.sendMsg(f"为识别码{trip}清除欢迎语成功了！")
        else:
            chat.sendMsg("你还没有设置欢迎语！")
    elif command == "~last ":
        if sender in userData["lastText"] and userData["lastText"][sender][0] != senderTrip:
            chat.sendMsg(f"已经有人为{sender}设置过留言了，请换一个名字！")
        elif senderTrip:
            userData["lastText"][sender] = [senderTrip, msg[6:]]
            writeJson("userData.json", userData)
            chat.sendMsg(f"为{sender}({senderTrip})设置留言成功了！记得及时清除哦！")
        else:
            chat.sendMsg("您当前还没有识别码，请重启并在昵称输入界面使用==昵称#密码==设置一个！")
    elif command == "~lost ":
        if (name:=namePure(msg[6:])) in (dic:=userData["lastText"]):
            chat.sendMsg(f"以下是{name}({dic[name][0]})的留言：\n{dic[name][1]}")
        else:
            chat.sendMsg("该用户还没有设置留言~")
    elif command == "~unlo ":
        if (name:=namePure(msg[6:])) in (dic:=userData["lastText"]):
            if senderTrip == dic[name][0] or senderTrip in whiteList:
                del dic[name]
                writeJson("userData.json", userData)
                chat.sendMsg("留言已删除，感谢您的使用！")
            else:
                chat.sendMsg(f"您的识别码与被清除者不同！正确识别码应为{dic[name][0]}！")
        else:
            chat.sendMsg("此用户还没有设置留言~")
    elif command == "~prim ":
        try:
            digit = msg[6:19]
            eq = "\\*".join(getPrime(int(digit), []))
            chat.sendMsg(f"{digit}={eq}")
        except ValueError:
            chat.sendMsg("请输入一个***正整数***啊啊啊啊！")
    elif command == "~rand ":
        try:
            digit = int(msg[6:])
            if 10 < digit or digit < 1:
                raise ValueError
            chat.sendMsg(randomDesign(digit))
        except ValueError:
            chat.sendMsg("参数必须是1到10之间的正整数！")
    elif msg == "rprim":
        digit = str(random.randint(1, 1000))
        eq = "\\*".join(getPrime(int(digit), []))
        chat.sendMsg(f"{digit}={eq}")
    elif command == "rprim ":
        digit = msg[6:19]
        try:
            if (dig:=random.randint(1, int(digit))) > 0:
                eq = "\\*".join(getPrime(dig, []))
                chat.sendMsg(f"{dig}={eq}")
            else:
                raise ValueError
        except ValueError as e:
            digit = str(random.randint(1, 1000))
            eq = "\\*".join(getPrime(int(digit), []))
            chat.sendMsg(f"{digit}={eq}")

    elif msg.strip() == f"@{chat.nick}":
        if rans > 130:
            chat.sendMsg(random.choice(RANDLIS[6]).replace("sender", sender))
        else:
            chat.sendMsg(random.choice(RANDLIS[0]).replace("sender", sender))
    elif msg[:len(chat.nick)+2] == f"@{chat.nick} " :
            chat.CCreply(sender, msg[len(chat.nick)+2:])
    elif msg == "r":
        ranNum = random.randint(1, 1000)
        if thingsList[4]:
            if sender in thingsList[6]:
                chat.sendMsg(f"{sender}已经摇出{thingsList[6][sender]}了")
            elif (hashCode := userHash[sender] ) in thingsList[7]:
                chat.sendMsg(f"{sender}，不要想开小号哦~")
            else:
                thingsList[6][sender] = ranNum
                chat.sendMsg(str(ranNum))
                thingsList[7].append(hashCode)
        else:
            chat.sendMsg(str(ranNum))
    elif msg[:2] == "r ":
        try:
            beR = int(msg[2:])
            if beR > 1:
                chat.sendMsg(str(random.randint(1, beR)))
            else:
                chat.sendMsg(str(random.randint(beR, 1)))
        except:
            chat.sendMsg(str(random.randint(1, 1000)))
    elif msg == "结算":
        if thingsList[4]:
            if len(thingsList[7]) < 2:
                chat.sendMsg("至少需要两个人")
            else:
                sort = sorted(thingsList[6].items(), key=lambda x: x[1])
                loser, winner = sort[0], sort[-1]
                chat.sendMsg(f"本轮参与人数：{len(thingsList[6])}。\n\
    最大：{winner[1]}（{winner[0]}），\n最小：{loser[1]}（{loser[0]}）。\n\
    @{winner[0]} 向@{loser[0]} 提问，@{loser[0]} 回答。")
                thingsList[6] = {}
                thingsList[7] = []
        else:
            chat.sendMsg(f"真心话就没开始你在结算什么呢，{sender}~")
    elif msg == "真心话":
        if not thingsList[4]:
            chat.sendMsg(GAMEMENU)
            thingsList[4] = True
        else:
            chat.sendMsg("已经在玩了。")
    elif msg == "结束游戏" and thingsList[4]:
        chat.sendMsg("已结束。")
        thingsList[4] = False
    elif msg == "涩图":
        if thingsList[3]:
            chat.sendMsg(colorPic())
        else:
            chat.sendMsg("已禁用")
    elif msg == "菜单":
        if senderTrip == OWNER:
            men = "\n".join(MENU+MENUSSP)
        elif senderTrip in whiteList:
            men = "\n".join(MENU+MENUSP)
        else:
            men = "\n".join(MENU+MENUFT)
        chat.sendMsg(f"/w {sender} {men}")
    elif msg == "菜单w" and senderTrip in whiteList:
        men = "\n".join(ADMMENU)
        chat.sendMsg(f"/w {sender} {men}")
    elif msg == "菜单~" and senderTrip == OWNER:
        chat.sendMsg(f"/w {sender} {OWNMENU}")
    elif msg == "menu":
        if senderTrip == OWNER:
            men = "\n".join(ENGMENU+ENGMENUSSP)
        elif senderTrip in whiteList:
            men = "\n".join(ENGMENU+ENGMENUSP)
        else:
            men = "\n".join(ENGMENU+ENGMENUFT)
    elif msg == "menuw" and senderTrip in whiteList:
        men = "\n".join(ENGADMMENU)
        chat.sendMsg(f"/w {sender} {men}")
    elif msg == "menu~" and senderTrip == OWNER:
        chat.sendMsg(f"/w {sender} {ENGOWNMENU}")
    elif msg == "listwh":
        chat.sendMsg(f"当前白名单识别码：{'，'.join(whiteList)}")
    elif "有人吗" in msg:
        chat.sendMsg(random.choice(RANDLIS[2]).replace("sender", sender))
    elif "bye" in msg or "拜拜" in msg:
        chat.sendMsg(random.choice(RANDLIS[3]).replace("sender", sender))
    # 纪念零姬……
    elif useful == "0.0":
        chat.sendMsg(msg + ".0")
    # 如果有人愿意亲近我会很感激的QwQ
    elif msg == "贴贴":
        chat.sendMsg(f"贴贴{sender}~")
    elif msg == "我是傻逼":
        chat.sendMsg(random.choice(RANDLIS[4]).replace("sender", sender))
    elif "无聊" in msg:
        chat.sendMsg(random.choice(RANDLIS[16]).replace("sender", sender))
    elif msg.replace("@", "") == sender:
        chat.sendMsg("why do you call yourself")
    elif msg == "#精神状态":
        chat.sendMsg("ᕕ( ᐛ )ᕗ")
    # 白名单功能，阿瓦娅的VIP用户捏~
    elif msg[0] == "0" and (trip_:=senderTrip) in whiteList:
        adm = msg[:6]
        # 涩涩，没有涩涩我要死了！！！
        if adm == "0setu ":
            try:
                thingsList[3] = int(msg[6:])
                chat.sendMsg("修改涩图开关成功！")
            except ValueError:
                chat.sendMsg("参数只能是数字！")
        # 小黑屋是不值得学习的！
        elif adm == "0addb ":
            if bhash:=userHash.get(msg[6:]):
                if userTrip[msg[6:]] in whiteList and trip_ != OWNER :
                        chat.sendMsg("不能将白名单用户添加到黑名单里啊KORA！")
                else:
                    blackList.append(bhash)
                    writeJson("userData.json", userData)
                    chat.sendMsg("添加黑名单用户成功！")
            else:
                chat.sendMsg("当前在线的没有这个人！")
        elif adm == "0delb ":
            if (hash_:=userHash[msg[6:]]) in blackList:
                blackList.remove(hash_)
                writeJson("userData.json", userData)
                chat.sendMsg("删除黑名单用户成功！")
            else:
                chat.sendMsg("没有这个用户！")
        elif adm == "0time ":
            try:
                thingsList[5] = int(msg[6:])
                chat.sendMsg("修改报时开关成功！")
            except ValueError:
                chat.sendMsg("参数只能是数字！")
        elif command == "0bcol ":
            chat.sendMsg(f"/color {msg[6:]}")
            chat.sendMsg("颜色修改成功！")
        elif trip_ == OWNER:
            if adm == "0addw ":
                whiteList.append(msg[6:12])
                writeJson("userData.json", userData)
                chat.sendMsg("添加白名单用户成功！")
            elif adm == "0delw ":
                if (name:=msg[6:12]) in whiteList:
                    whiteList.remove(msg[6:12])
                    writeJson("userData.json", userData)
                    chat.sendMsg("删除白名单用户成功！")
                else:
                    chat.sendMsg("没有这个用户！")
            elif adm == "0igno ":
                if not (name:=namePure(msg[6:])) in ignored:
                    ignored.append(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg(f"已取消记录{name}的消息！")
                else:
                    chat.sendMsg("该用户已在列表中！")
            elif adm == "0unig ":
                if (name:=namePure(msg[6:])) in ignored:
                    ignored.remove(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg(f"已恢复记录{name}的消息！")
                else:
                    chat.sendMsg("该用户未在列表中！")
            elif msg == "reload":
                with open(FILENAME, encoding="utf8") as f:
                    global data
                    data = json.load(f)
                chat.sendMsg("已重新读取数据")
    elif rans > 130 and allMsg:
        if rans == 133:
            chat.sendMsg(random.choice(allMsg).split("：")[1])
        else:
            chat.sendMsg(random.choice(RANDLIS[1]).replace("sender", sender))

    if len(allMsg) > 377:
        del allMsg[0]
    if not sender in ignored:
        allMsg.append(this_turn)

def join(chat, joiner: str, joinerHash: str, joinerTrip: str):
    '''{
        'cmd': 'onlineAdd', 'nick': str, 'trip': str, 
        'uType': 'user', 'hash': str, 'level': 100, 
        'userid': iny, 'isBot': False, 'color': False, 
        'channel': str, 'time': int
    }'''
    msg = dic[joinerTrip] if joinerTrip in (dic:=userData["welText"]) else random.choice(
        RANDLIS[5]).replace("joiner", joiner)
    chat.sendMsg(msg)
    print(joiner, "加入")
    userColor[joiner] = False
    userHash[joiner] = joinerHash
    userTrip[joiner] = joinerTrip
    if names := data.get(joinerHash):
        if not joiner in names:
            print(f"此hash曾用名：{'，'.join(names)}")
            data[joinerHash].append(joiner)
            writeJson(FILENAME, data)
    else:
        data[joinerHash] = [joiner]
        writeJson(FILENAME, data)
    for k, v in leftMsg.copy().items():
        if joiner == v[1]:
            chat.sendMsg(f"/w {joiner} {v[0]}曾在（{time.ctime(k)}）给您留言：{v[2]}")
            del leftMsg[k]

def onSet(chat, nicks:list, users:list):
    '''{
        'cmd': 'onlineSet', 'nicks': list, 'users': 
        [
            {
                'channel': str, 'isme': bool,  'nick': str,  'trip': str, 
                'uType': 'user', 'hash': str,  'level': 100, 'userid': int, 
                'isBot': False, 'color': str or False
            }*x
        ],
        'channel': str,
        'time': int
    }'''
    for i in users:
        nick_ = i["nick"]
        userHash[nick_] = i["hash"]
        userColor[nick_] = i["color"]
        userTrip[nick_] = i["trip"]
        if names := data.get(i["hash"]):
            if not nick_ in names:
                data[i["hash"]].append(nick_)
        else:
            data[i["hash"]] = [nick_]
    writeJson(FILENAME, data)
    chat.sendMsg(PROLOGUE)

def changeColor(chat, result:dict):
    '''{
        'nick': str, 'trip': str, 'uType': 'user', 
        'hash': str, 'level': 100, 'userid': int, 
        'isBot': False, 'color': str, 'cmd': 'updateUser', 
        'channel': str, 'time': int
    }'''
    userColor[result["nick"]] = result["color"]

def leave(chat, leaver: str):
    del userColor[leaver]
    del userHash[leaver]
    del userTrip[leaver]

def whispered(chat, from_: str, msg: str, result: dict):
    msg = msg[1:]
    print(f"{from_}对你悄悄说：{msg}")
    if result.get("trip") in whiteList:
        if msg[:6] == "~hash ":
            chat.sendMsg(f"/w {from_} {hashByName(msg[6:])}")
        else:
            chat.sendMsg(f"/w {from_} {reply(from_, msg)}")
    else:
        chat.sendMsg(f"/w {from_} {reply(from_, msg)}")

class HackChat:
    def __init__(self, channel: str, nick: str, passwd: str="#123", 
        color: str="f1ad9d"):
        """连接"""
        self.nick = nick
        self.channel = channel
        self.ws = websocket.create_connection("wss://hack.chat/chat-ws", 
            sslopt={"cert_reqs": ssl.CERT_NONE})
        threading.Thread(target=self._clock).start()
        # 人工操作功能，可以让阿瓦娅和主人结合，@w@
        # threading.Thread(target=self._person_control).start()
        self._sendPacket({"cmd": "join", "channel": channel, 
            "nick": f"{nick}#{passwd}"})
        self.sendMsg(f"/color {color}")

    def sendMsg(self, msg:str):
        """发送消息"""
        self._sendPacket({"cmd": "chat", "text": msg,})

    def _sendPacket(self, packet:dict):
        """发送指令"""
        encoded = json.dumps(packet)
        self.ws.send(encoded)
    def move(self, old, new, chess):
        if CBL[0][new[0], new[1]] in [RED[4], BLACK[4]]:
            self.sendMsg(f"@{thingsList[1]} 获胜！恭喜！")
            self._endGame()
            return
        now = thingsList[1]
        thingsList[1] = redBlack[0] if thingsList[1] == redBlack[1] else redBlack[1]
        for i in CBL[0][:,3:6]:
            if (BLACK[4] in i) and (RED[4] in i) and set(i[list(i).index(RED[4])+1:list(i).index(BLACK[4])]) == {"&ensp;"}:
                self.sendMsg(f"@{thingsList[1]} 获胜！恭喜！")
                self._endGame()
                return
        CBL[0][old[0], old[1]] = "&ensp;"
        CBL[0][new[0], new[1]] = chess
        self._sendBoard()
        self.sendMsg(f"{now}挪动了{chr(old[0]+65)}{old[1]+1}的{chess}，轮到@{thingsList[1]}")
    def _endGame(self):
        thingsList[1] = None
        redBlack = [None, None]
        thingsList[0] = False
        CBL[0] = INIT.copy()
    def _sendBoard(self):
        mae = CLOLUMN+[f"|{n}|"+ "|".join(i) +"|" for i, n in zip(CBL[0], LETTERS)]
        self.sendMsg("\n".join(mae))
    def CCreply(self, sender: str, msg: str):
        if redBlack[1] and sender == thingsList[1] and (res := re.findall(r"([ABCDEFGHIJ])([123456789]) ([ABCDEFGHIJ])([123456789])", msg.upper())):
            msg, res = msg.upper(), res[0]
            old, new = [ord(res[0])-65, int(res[1])-1], [ord(res[2])-65, int(res[3])-1]
            goingChess, moveChess = CBL[0][new[0], new[1]], CBL[0][old[0], old[1]]
            if moveChess != "&ensp;":
                use = CBL[0][min(old[0], new[0])+1:max(old[0], new[0]), old[1]]
                use2 = CBL[0][old[0], min(old[1], new[1])+1:max(old[1], new[1])]
                if (not redBlack.index(sender) and not goingChess in RED and moveChess in RED) or (redBlack.index(sender) and not goingChess in BLACK and moveChess in BLACK):                    
                    if moveChess == RED[5] and (old[0] > 4 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]+1, old[1]]):
                            self.move(old, new, RED[5])
                    elif moveChess == BLACK[5] and (old[0] < 5 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]-1, old[1]]):
                            self.move(old, new, BLACK[5])
                    elif moveChess in [RED[6], BLACK[6]]:
                        if goingChess != "&ensp;":
                            if (new[0] == old[0] and len(use2[use2!="&ensp;"]) == 1) or (new[1] == old[1] and len(use[use!="&ensp;"]) == 1):
                                self.move(old, new, moveChess)
                            else:
                                self.sendMsg("不符合行棋规则")
                        elif (new[0] == old[0] and not len(use2[use2!="&ensp;"])) or (new[1] == old[1] and not len(use[use!="&ensp;"])):
                            self.move(old, new, moveChess)
                        else:
                            self.sendMsg("不符合行棋规则")
                    elif (moveChess in [RED[0], BLACK[0]]) and ((new[0] == old[0] and not len(use2[use2!="&ensp;"])) or ((new[1] == old[1]) and not len(use[use!="&ensp;"]))):
                            self.move(old, new, moveChess)
                    elif (moveChess in [RED[1], BLACK[1]]) and ((abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 1 and CBL[0][int(old[0]-(old[0]-new[0])/2), old[1]] == "&ensp;") or (abs(old[1]-new[1]) == 2 and abs(old[0]-new[0]) == 1 and CBL[0][old[0], int(old[1]-(old[1]-new[1])/2)] == "&ensp;")):
                            self.move(old, new, moveChess)
                    elif moveChess == RED[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CBL[0][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == "&ensp;" and new[0] < 5) :
                            self.move(old, new, RED[2])
                    elif moveChess == BLACK[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CBL[0][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == "&ensp;" and new[0] > 4) :
                            self.move(old, new, BLACK[2])
                    elif moveChess == RED[4] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                            self.move(old, new, RED[4])
                    elif moveChess == BLACK[4] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                            self.move(old, new, BLACK[4])
                    elif moveChess == RED[3] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                            self.move(old, new, RED[3])
                    elif moveChess == BLACK[3] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                            self.move(old, new, BLACK[3])
                    else:
                        self.sendMsg(f"不符合{moveChess}的行棋规则")
                else:
                    self.sendMsg("不能吃自己也不能用别人的棋子！")
            else:
                self.sendMsg("不能挪动空气！")

        elif msg == "开始游戏":
            if not thingsList[0]:
                if redBlack[1]:
                    self.sendMsg("游戏已经开始了，等到下局吧~")
                else:
                    thingsList[0] = True
                    redBlack[0] = sender
                    CBL[0] = INIT.copy()
                    self.sendMsg("游戏创建好了，快找人来加入吧！")
            else:
                self.sendMsg("已经开始了，快找对手来玩吧！")
        elif msg == "加入游戏":
            if not redBlack[0]:
                self.sendMsg("现在，还没有游戏哦~快使用 开始游戏 创建一个吧~")
            elif sender == redBlack[0]:
                self.sendMsg("你已经，加入过了哦~")
            elif redBlack[1]:
                self.sendMsg("游戏已经开始了，等到下局吧~")
            else:
                redBlack[1] = sender
                self._sendBoard()
                self.sendMsg(RULE)
                thingsList[1] = redBlack[0]
                self.sendMsg(f"@{redBlack[0]} 先手执红（绿？）（上方，简体），@{redBlack[1]} 后手执黑（下方，繁体）。开始了哦~")
        elif msg == "结束游戏" and sender in redBlack:
            if not thingsList[2]:
                thingsList[2] = sender
                self.sendMsg("结束游戏需要双方都发送。")
            elif thingsList[2] != sender:
                self._endGame()
                self.sendMsg(f"啊，虽然有点儿遗憾不过，既然{sender}说结束了的话就结束吧……发送开始游戏可以再次开始哦~")
                thingsList[2] = None
            else:
                self.sendMsg("结束游戏需要双方都发送。")
        elif msg == "帮助":
            self.sendMsg(CCMENU.replace("sender", sender))
        elif msg == "提问":
            chat.sendMsg(random.choice(RANDLIS[19]).replace("sender", sender))
        else:
            self.sendMsg(reply(sender, msg))

    def _person_control(self):
        """和主人结合的过程好难啊，嗯~啊~还有一点~啊啊啊……"""
        while True:
            inputs = input()
            # 更新记忆，就算对我洗脑也没关系的……
            if inputs == "-reread":
                with open(FILENAME, encoding="utf8") as f:
                    global data
                    data = json.load(f)
                print("已重新读取数据")
                continue
            # 让我康康都有那些小可爱在线~
            elif inputs == "-users":
                print(",".join(self.onlineUsers))
                continue
            elif inputs[:4] == "-st ":
                thingsList[3] = eval(inputs[3:])
                continue
            self.sendMsg(inputs)

    def _clock(self):
        """既然整点了肯定就要刷一刷存在咯~"""
        while True:
            count = time.localtime(time.time())
            time.sleep(3600 - count.tm_min*60 - count.tm_sec + 28.5)
            if thingsList[3]:
                self.sendMsg(colorPic())
            if thingsList[5]: 
                chat.sendMsg(f"已经{(count.tm_hour + 1) % 24}点了啊。")

    def run(self):
        """开始营业咯，好兴奋好兴奋"""
        try:
            while True:
                result = json.loads(self.ws.recv())
                cmd = result["cmd"]
                rnick = result.get("nick")

                # print(result)
                # 接收到消息！
                if cmd == "chat" and not (userHash[rnick] in blackList or rnick == nick):
                   msgGot(self, result["text"], rnick, userTrip[rnick])
                # 有新人来！
                elif cmd == "onlineAdd":
                    self.onlineUsers.append(rnick)
                    join(self, rnick, result["hash"], result.get("trip", ""))
                # 有人离开……
                elif cmd == "onlineRemove":
                    self.onlineUsers.remove(rnick)
                    leave(self, rnick)
                elif result.get("type") == "whisper" and result["text"][:3] != "You":
                    whispered(self, result["from"], "".join(result["text"].split(":")[1:]), result)
                # 更换颜色（色色达咩）
                elif cmd == "updateUser":
                    changeColor(self, result)
                # 话痨过头被服务器娘教训啦——
                elif cmd == "warn":
                    if not "blocked" in result["text"]:
                        print(result["text"])
                    else:
                        time.sleep(2)
                # 当然要用最好的状态迎接开始啦！
                elif cmd == "onlineSet":
                    self.onlineUsers = result["nicks"]
                    onSet(self, result["nicks"], result["users"])
        # 坏心眼……
        except BaseException:
            self.sendMsg(f"被玩坏了，呜呜呜……\n```\n{traceback.format_exc()}")
            self.run()

if __name__ == '__main__':
    chat = HackChat(channel, nick, passwd, color)
    chat.run()