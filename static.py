#coding=utf-8
# 进源码啥都别说，先一起喊： 阿瓦！
import json, time, math, re, websocket, requests, threading, traceback, sys, os, random, datetime, string
from typing import Optional, Literal
from enum import IntEnum
from collections import deque

# 真常量
WSADD = "wss://hack.chat/chat-ws"
# WSADD = "ws://localhost:8765"

PREFIX, WHTFIX, OWNFIX = ";", "0", "."
TIME_ZONE = +8
LATEXOOM = r"$\begin{pmatrix}qaq\\[20231128em]\end{pmatrix}$"
KICK = "/kick" # 会自动加空格
EHHH = "&zwj;"

MENUMIN = "\n".join([
    "早",
    "普通用户: ",
    f">前缀=={PREFIX}==:",
    "status, hasn, hash, code, colo, left, peep, welc, seen, look, Lori, decp, list, setu, prime, hug, shoot, uwu, kkme",
    "阿瓦豆:",
    "regst, sign, bank, rank, v, packet, aka, borrow, lend, reject, repay, store, loans",
    "无前缀:",
    "r, rollen, rprime, time, today, 游戏",
    "",
    "白名单用户：",
    f">前缀=={WHTFIX}==:",
    "addb, delb, igno, unig, bans, uban, kill, unwe, encap, decap, lock, unlock, gnkey, " + 
    "setrl, addw, delw, list, room, fun, regst",
    "",
    f"发送=={PREFIX}help 命令==可获得该指令详细用法，如=={PREFIX}help help==",
    f"白名单用{WHTFIX}help",
    "开源地址: https://github.com/Kroos372/awaya , 欢迎star～(∠・ω< )⌒★"
])
OWNMENU = "\n".join([
    "好好反思下身为主人为什么还要菜单",
    "addw, delw: 增减白名单trip; igon, unig: 增减peep忽略名称(正则);",
    "chkr: 检查回答; tstr: 测试问题对应的回答; delr: 删除回答;",
    "relo: 清空一些变量; stfu: 休眠开关; atrm: 报错重启开关;",
    "prtt, delp: 增删保护的trip; send: 发送消息; beat: 心跳(检测被踢)频率(默认120秒)",
    "kkal: 踢出最后到倒数x个用户; eval: 执行代码; remake: 重启",
    "看源码去吧你"
])
COMMANDS = {
    "help": "\n".join([
        "# Help Of Commands:",
        "||",
        "|:-:|",
        "|参数: <命令>|",
        "|描述: 查询<命令>的使用方法。|",
        f"|例: {PREFIX}help help|",
        "|注: <>包起来的是参数类型，如<昵称>代表填写昵称，不要带<>，认真看使用示例。|",
        "|前面加==?==表示可选参数，<参数1>/<参数2>表示两参数任选一。|"
    ]),
    "status": "\n".join([
        "# Bot STATUS:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 本bot的一些信息。|",
        f"|例: {PREFIX}status|"
    ]),
    "hasn": "\n".join([
        "# Hash Now Online User:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 查询==当前在线==名为<昵称>用户的Hash的历史昵称|",
        f"|例: {PREFIX}hasn @awa_ya|",
    ]),
    "hash": "\n".join([
        "# History Nickname For Hash Of Nick:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 查询使用过所有<昵称>的用户的Hash的历史昵称|",
        f"|例: {PREFIX}hash @awa_ya|",
        "|注: 谨慎使用，当心后果。|"
    ]),
    "code": "\n".join([
        "# History Nickname For Hash Code:",
        "||",
        "|:-:|",
        "|参数: <Hash码>|",
        "|描述: 查询使用过所有<昵称>的用户的Hash的历史昵称|",
        f"|例: {PREFIX}hash abcdefg|",
        "|注: `/myhash`可快捷查看自己的Hash。谨慎使用，当心后果。|"
    ]),
    "colo": "\n".join([
        "# Color Of Nickname:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 查询当前名为<昵称>的用户的颜色|",
        f"|例: {PREFIX}hash abcdefg|",
    ]),
    "left": "\n".join([
        "# Leave Message For Someone:",
        "||",
        "|:-:|",
        "|参数: <昵称>/*<识别码> <消息>|",
        "|描述: 为<昵称>或<识别码>留言，会在用户上线或发言时私信。|",
        f"|例: {PREFIX}left *coBad2 我喜欢你|",
        f"|例2: {PREFIX}left awa_ya 你喜欢我|",
        "|注: 用户上线时通知格式：<昵称>曾在（<时间>）通过<方式>给您留言：<消息>|",
    ]),
    "peep": "\n".join([
        "# View History Messages:",
        "||",
        "|:-:|",
        "|参数: <整数> ?<整数>|",
        "|描述: 浏览最近的<整数>条消息，参数长度为二时则会选择最近520条消息中第<整数>至第<整数>条。|",
        f"|例: {PREFIX}peep 23|",
        "|注: 最多存储520条消息，查看消息过长时无法显示。|",
        f"|注2: 使用{PREFIX}peep *<参数> 可订阅peep, 在当前识别码每次加入时自动发送peep|",
        "|注3: 返回消息中名字前带有*的表示该消息是更改后的（别老updateMessage了）。|"
    ]),
    "welc": "\n".join([
        "# Set Welcome Message:",
        "||",
        "|:-:|",
        "|参数: ?<欢迎语>|",
        "|描述: 为当前识别码设置欢迎语，参数为空时清除欢迎语。|",
        f"|例: {PREFIX}welc 早|",
        "|注: 别太长。|"
    ]),
    "seen": "\n".join([
        "# Last Saw Someone At:",
        "||",
        "|:-:|",
        "|参数: <昵称>/*<识别码>|",
        f"|描述: 最后一次看到某昵称或识别码的时间，与他最后一句话的内容。|",
        f"|例: {PREFIX}seen *coBad2|",
    ]),
    "look": "\n".join([
        "# I Don't Know:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        f"|描述: 当前在线昵称的加入时间，发言频率，以及与{PREFIX}seen相同。|",
        f"|例: {PREFIX}look Krs_|",
    ]),
    "Lori": "\n".join([
        "# L Or i ?",
        "||",
        "|:-:|",
        "|参数: <字符>|",
        "|描述: 帮你区分I和l，什么的。 |",
        f"|例: {PREFIX}Lori I |",
        "|注: 首个大写命令 |",
    ]),
    "decp": "\n".join([
        "# ???",
        "||",
        "|:-:|",
        "|???: ???|",
        "|???: ???|",
        "|???: ???|",
        "|???: 前面的区域，以后再来探索吧~|",
    ]),
    "list": "\n".join([
        "# LIST Sth.:",
        "||",
        "|:-:|",
        "|参数: wht/blk/ign/ban/afks/word|",
        "|描述: 列出一些名单|",
        f"|例: {PREFIX}list wht|",
        "|注: 你感到神秘的力量在涌动|"
    ]),
    "setu": "\n".join([
        "# Colorful Picture:",
        "||",
        "|:-:|",
        "|参数: ?<参数>|",
        "|描述: 涩图怎么又回来了，你们谁有头绪|",
        f"|例: {PREFIX}setu tag=阿瓦|",
        "|注: 来自[点我](https://api.lolicon.app/#/setu), 参数详情自己看。有rl(我加的)。|"
    ]),
    "uwu": "\n".join([
        "# U-Uwuify:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: uwuwuwuwuwuw|",
        f"|例: {PREFIX}uwu|"
    ]),
    "kkme": "\n".join([
        "# KicK ME:",
        "||",
        "|:-:|",
        "|参数: ?<昵称>|",
        "|描述: 踢出相同识别码的僵尸号，参数留空自动匹配。|",
        f"|例: {PREFIX}kkme Krs_|"
    ]),

    "regst": "\n".join([
        "# REGiSTer Bank:",
        "||",
        "|:-:|",
        "|参数: ?<账户名>|",
        "|描述: 发起一个注册银行的请求，可自定义账户名|",
        f"|例: {PREFIX}regst VioletSand|",
        "|注: 若当前识别码已有账户，则可以改名|"
    ]),
    "sign": "\n".join([
        "# SIGN:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 签到，随机获得阿瓦豆(签到时间越长越多) |",
    ]),
    "bank": "\n".join([
        "# BANK:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 查看自己的银行|",
    ]),
    "rank": "\n".join([
        "# RANKing List:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 查看排行榜|",
    ]),
    "v": "\n".join([
        "# giVe:",
        "||",
        "|:-:|",
        "|参数: <trip> <钱数>|",
        "|描述: V我50|",
    ]),
    "packet": "\n".join([
        "# Red PACKET:",
        "||",
        "|:-:|",
        "|参数: <id> / <钱数> <人数>|",
        "|描述: 发红包（发完会生成id）或抢红包|",
        f"|例: {PREFIX}packet 30 3|",
        f"|例2: {PREFIX}packet abcdef|",
    ]),
    "aka": "\n".join([
        "# Also Known As:",
        "||",
        "|:-:|",
        "|参数: <trip>|",
        "|描述: 为当前账号添加关联识别码|",
        f"|例: {PREFIX}aka //////|",
    ]),
    "borrow": "\n".join([
        "# BORROW from:",
        "||",
        "|:-:|",
        "|参数: <trip> <豆数> <期限(天)>|",
        "|描述: 向其他人发起借款，对方使用lend同意或reject拒绝|",
        f"|例: {PREFIX}borrow coBad2 520|",
        "|注: <trip>填机器人识别码可向银行借款，银行利率2%|"
    ]),
    "lend": "\n".join([
        "# LEND to:",
        "||",
        "|:-:|",
        "|参数: <债务id> <利率(每日)>|",
        "|描述: 同意借款请求|",
        f"|例: {PREFIX}lend abcdef 0.05|",
        "|注：债务逾期后可使用reject强制返还|"
    ]),
    "reject": "\n".join([
        "# REJECT!:",
        "||",
        "|:-:|",
        "|参数: <债务id> ?<豆数>|",
        "|描述: 拒绝借款请求，或在债务逾期后强制扣钱|",
        f"|例: {PREFIX}reject qaqaqa 123|",
    ]),
    "repay": "\n".join([
        "# REPAY:",
        "||",
        "|:-:|",
        "|参数: <债务id> <豆数>|",
        "|描述: 还钱|",
        f"|例: {PREFIX}repay nomore 555|",
    ]),
    "loans": "\n".join([
        "# Get My LOANS:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 查询自己的债务|",
        f"|例: {PREFIX}loans|",
    ]),
    "store": "\n".join([
        "# STORE My Money:",
        "||",
        "|:-:|",
        "|参数: <豆数>|",
        "|描述: 以债务形式储存豆子|",
        f"|例: {PREFIX}store 999|",
    ]),

    "st": "\n".join([
        "# Stock Trading:",
        "||",
        "|:-:|",
        "|参数: 买入/卖出/持有/行情/排行|",
        "|描述: 炒股系统|",
        "|例1: st 买入 100|",
        "|例2: st 卖出 50|",
        "|例3: st 行情|",
        "|注: 股价每秒更新一次，有一定波动性，请谨慎投资|"
    ]),
    "r": "\n".join([
        "# Random Integer:",
        "||",
        "|:-:|",
        "|参数: ?<整数> ?<整数>|",
        "|描述: 1\\~1000、1\\~<整数>、<整数>\\~1、或<整数>\\~<整数>之间的随机整数。|",
        "|例: r 6 666|",
    ]),
    "rollen": "\n".join([
        "# ROLL to ENd(?):",
        "||",
        "|:-:|",
        "|参数: ?<整数>|",
        "|描述: 不断在1与整数间r，直到归1|",
        "|例: rollen 12345|",
        "|注: 自动截断，いたずら断念 殺人鬼|"
    ]),
    "time": "\n".join([
        "# Literature Clock:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 文学作品里的时间。|",
        "|例: time|",
        "|注: [来自点我](https://literature-clock.jenevoldsen.com/)|",
    ]),
    "today": "\n".join([
        "# TODAY in History:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 历史上的今天。|",
        "|例: today|",
        "|注: [来自点我](https://wai.shaiwang.life/)|",
    ]),
    "游戏": "\n".join([
        "# Games:",
        "||",
        "|:-:|",
        "|瓦: 一些小游戏|",
    ])
}
WTCOMMANDS = {
    "addb": "\n".join([
        "# ADD Blacklist:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>加入对应类型的黑名单|",
        f"|例: {WHTFIX}addb nick _|"
    ]),
    "delb": "\n".join([
        "# DELete Blacklist:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>移出对应类型的黑名单|",
        f"|例: {WHTFIX}delb hash akstnhmyrw|"
    ]),
    "igno": "\n".join([
        "# IGNOre:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>加入对应类型的peep屏蔽列表|",
        f"|例: {WHTFIX}igno nick _|"
    ]),
    "delb": "\n".join([
        "# UN IGnore:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>移出对应类型的peep屏蔽列表|",
        f"|例: {WHTFIX}unig hash akstnhmyrw|"
    ]),
    "kill": "\n".join([
        "# KILL:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 踢出昵称。|",
        f"|例: {WHTFIX}kill awa_ya|",
        "|注: 可用空格分隔多个|"
    ]),
    "bans": "\n".join([
        "# BANS:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>加入对应类型的封禁列表，加入时踢出|",
        f"|例: {WHTFIX}ban nick uwu_ya|"
    ]),
    "uban": "\n".join([
        "# UnBAN:",
        "||",
        "|:-:|",
        "|参数: <hash/trip/nick> <值>|",
        "|描述: 将<值>移出对应类型的封禁列表|",
        f"|例: {WHTFIX}uban hash abcdefghijkl|"
    ]),
    "addn": "\n".join([
        "# ADD Blacklist Nick:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 将昵称加入黑名单|",
        f"|例: {WHTFIX}addn _|"
    ]),
    "deln": "\n".join([
        "# DELete Blacklist Nick:",
        "||",
        "|:-:|",
        "|参数: <昵称>|",
        "|描述: 将昵称移出黑名单|",
        f"|例: {WHTFIX}deln _|"
    ]),
    "unwe": "\n".join([
        "# UN WElcome:",
        "||",
        "|:-:|",
        "|参数: <识别码>|",
        "|描述: 清除识别码的欢迎语，防刷屏用。|",
        f"|例: {WHTFIX}unwe coBad2|"
    ]),
    "encap": "\n".join([
        "# ENable CAPtcha:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 开启验证码。|",
        "|例: 懒得写|"
    ]),
    "decap": "\n".join([
        "# D?able CAPtcha:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 关闭验证码。|",
        "|例: 懒得写|"
    ]),
    "lock": "\n".join([
        "# LOCKroom:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 锁房。|",
        "|例: 懒得写|"
    ]),
    "unlock": "\n".join([
        "# UNLOCKroom:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 解锁。|",
        "|例: 懒得写|"
    ]),
    "gnkey": "\n".join([
        "# GeNerate KEY:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 生成key，用于无识别码时关闭验证码。|",
        "|例: 懒得写|"
    ]),
    "setrl": "\n".join([
        "# SET Rate Limiter:",
        "||",
        "|:-:|",
        "|参数: <整数> ?<整数> ?word|",
        "|描述: 设置rl器的半衰期与阈值，如果最后一项为word则设置封禁词的rl器|",
        f"|例: {WHTFIX}setrl 30 3 word|",
        "|注: 具体计算方式见源码|"
    ]),
    "addw": "\n".join([
        "# ADD Ban Word:",
        "||",
        "|:-:|",
        "|参数: <词>|",
        "|描述: 添加封禁词，当rl值到则踢出。支持正则。|",
        f"|例: {WHTFIX}addw .|",
        "|注: 笑点解析: 添加白名单也是addw|"
    ]),
    "delw": "\n".join([
        "# DELete Ban Word:",
        "||",
        "|:-:|",
        "|参数: <词>|",
        "|描述: 删除封禁词|",
        f"|例: {WHTFIX}delw 几把|",
    ]),
    "list": "\n".join([
        "# LIST Channel Users:",
        "||",
        "|:-:|",
        "|参数: <频道>|",
        "|描述: 列出某频道的用户。|",
        f"|例: {WHTFIX}list your-channel|",
        "|注: 别用太多，容易rl|"
    ]),
    "room": "\n".join([
        "# ROOM State:",
        "||",
        "|:-:|",
        "|参数: ?<频道>|",
        "|描述: 检查频道状态（锁房/验证码）|",
        f"|例: {WHTFIX}room your-channel|",
        "|注: 别用太多，容易rl|"
    ]),
    "rcolor": "\n".join([
        "# Random COLOR:",
        "||",
        "|:-:|",
        "|参数: 无|",
        "|描述: 随机颜色|",
        "|例: rcolor|",
        "|注: 最好别用|"
    ]),
    "fun": "\n".join([
        "# FUN:",
        "||",
        "|:-:|",
        "|参数: <数字>|",
        "|描述: 设置随机发言概率((1000 - 数字)/1000)|",
        f"|例: {WHTFIX}fun 990|",
    ]),
    "regst": "\n".join([
        "# FUN:",
        "||",
        "|:-:|",
        "|参数: ?- ?<trip>|",
        "|描述: 同意银行注册请求，若第一个参数为`-`则为拒绝。|",
        "|注: 不加参数为查看请求，all为参数则同意所有请求，-all则拒绝所有。|",
        f"|例: {WHTFIX}regst - coBad2 YaAwA7|",
    ]),

    "decp": "\n".join([
        "# D?able CaPtcha:",
        "||",
        "|:-:|",
        "|参数: <key>|",
        "|描述: 在没有识别码的情况下关闭验证码。|",
        f"|例: {PREFIX}decp awawaw|",
        "|注: 详见gnkey|"
    ])
}

HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"}
WEEKS = [None, "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
CLOCKS = [
    "0点了，生日的人生日快乐，没过生日的也要快乐哦~",
    "都已经1点，还不睡觉吗？",
    "2点了，惬意而祥和的时光啊。",
    "3点了，月光依然安静地笼罩着大地。",
    "4点，似乎有什么事情要做？",
    "清晨5点，早起的鸟儿有虫吃~",
    "6点，新的一天又开始了呢！",
    "7点啦，什么时候吃早饭呢？",
    "8点了，今天有什么计划呢？",
    "9点了，感觉怎么样呢？",
    "10点了，喝杯水放松一下吧。",
    "11点，上午过去得好快啊。",
    "12点了，准备吃午饭吧。",
    "13点了，漫长的下午要开始咯~",
    "14点到了，要做些什么事吗？",
    "15点了，是不是该喝杯下午茶？",
    "16点了，摸一摸信赖的人吧~",
    "17点了，忙碌的间隙也不要忘记休息啦。",
    "18点了，有谁准备快乐地下班了吗？",
    "19点了，今天有收获到什么吗？",
    "20点了，晚上应该怎么度过呢？",
    "21点了，夜宵还是散步，都不错呢~",
    "22点了，早睡早起身体好哦~",
    "23点啦，原来都还在聊天吗。"
]
# bo_od
KAWAII = [
    "sender棒棒",
    "sender是小天使",
    "sender最可爱了"
]
# Afk_bot
BODY_PARTS = [
    "heart",    # 心脏
    "head",     # 头部
    "chest",    # 胸部
    "lung",     # 肺
    "stomach",  # 腹部/胃
    "arm",      # 手臂
    "leg",      # 腿
    "hand",     # 手
    "foot",     # 脚
    "neck",     # 脖子
    "shoulder", # 肩膀
    "knee",     # 膝盖
    "eye",      # 眼睛
    "ear",      # 耳朵
    "mouth",    # 嘴巴
    "throat",   # 喉咙
    "brain",    # 大脑
    "liver",    # 肝脏
    "rib",      # 肋骨
    "spine",    # 脊柱
    "j"         # J!
]
# RIP original ModBot. . .
ERRORMSG = [
    "Die.",
    "Nope.",
    "No. But nice try.",
    "Im going to start being rude. . .",
    "I will report you to the internet police, sir.",
    "Your mother was a hamster.",
    "Your father smelt of elderberries.",
    "This is not how this works, or how any of this works.",
    "Dunno that command, try typing with your other cheeck.",
    "I've never seen this man in my life. . .",
]
MOTD = [
    "**Welcome to lounge, have a rest uwu**",
    "Most folks here are Chinese (active 8:00-0:00 UTC+8), but we're totally English-friendly!",
    "---"
]
MONTHS = [
    "",
    "Jan.",
    "Feb.",
    "Mar.",
    "Apr.",
    "May",
    "June",
    "July",
    "Aug.",
    "Sept.",
    "Oct.",
    "Nov.",
    "Dec"
]

# 独立于类的函数
## 处理BOM字符
def _debom(cont: str) -> str:
    if cont.startswith(u"\ufeff"):
        return cont.encode("utf8")[3:].decode("utf8")
    else:
        return cont
## 读文件
def readJson(filename: str):
    with open(f"files/{filename}.json", encoding="utf8") as f:
        data = json.loads(_debom(f.read()))
    return data
## 存入记忆中！
def writeJson(filename, datas):
    with open(f"files/{filename}.json", "w", encoding="utf8") as f:
        json.dump(datas, fp=f, ensure_ascii=False, indent=2)
## 整数秒
def now()->int:
    return int(time.time())
## 不知道
def gmNow(sec=0):
    if not sec:
        sec = now()
    return time.gmtime(sec + TIME_ZONE * Time.HOUR)
## 那个啥，反正就是那个
def getTime() -> str:
    tcg = gmNow()
    try:
        response = requests.get(f"https://literature-clock.jenevoldsen.com/times/{tcg.tm_hour:0>2}_{tcg.tm_min:0>2}.json", timeout=10).json()
    except:
        return "出错啦，请稍后再试(◐_◑)"
    panzerlied = random.choice(response)
    text = ">" + panzerlied["quote_first"] + f"**{panzerlied['quote_time_case']}**" + panzerlied["quote_last"] + "\n\n"
    from_ = "\\- " + panzerlied["title"] + f", *{panzerlied['author']}*"
    return text.replace("<br/>", "\n>") + from_
## 阿瓦
def historyToday() -> str:
    OwO = gmNow()
    today = readJson("history")[str(OwO.tm_mon)][str(OwO.tm_mday)]
    rr = random.sample(today, 5)
    rr.sort()
    return "\n".join(rr)
## r来r去
def rollTo1(maxNum: int=1000) -> str:
    road =  []
    while True:
        ran = random.randint(1, maxNum)
        road.append(str(ran))
        if ran != 1:
            maxNum = ran
        else:
            break
    return f"{', '.join(road)}: {len(road)}"
## 离谱青云客
def chatApi(msg) -> str:
    try:
        cont = requests.get(f"http://api.qingyunke.com/api.php?key=free&msg={msg}", timeout=10).json()
    except:
        return "寄了"
    else:
        cache = cont["content"].replace("菲菲", NAME).replace("{br}", "\n")
        return cache.replace("help", f"==@{NAME} help==，==菜单==或==@{NAME} 帮助==")
## 自定义回复
def reply(sender: str, msg: str, api: bool=True) -> str:
    for ques, ans in answer.items():
        try:
            searched = re.search(ques, msg)
        except:
            del answer[ques]
            writeJson("answer", answer)
            return f"*已清除{ques}的回答"
        else:
            if not (searched and ans):
                continue
            else:
                ans = random.choice(ans).replace("sender", sender)
                if searched.groups():
                    for i, v in enumerate(searched.groups()):
                        ans = re.sub(rf"\\{i+1}", v, ans)
                return EHHH + ans
    if api:
        return chatApi(msg)
    else:
        return None # 乖巧
## 长消息上传
def toWeb(text):
    try:
        requests.post(URL, data={"token": TOKEN, "text": text}, timeout=10)
        return "消息过长，点击链接查看:\n" + URL
    except:
        return text[:512] + "\n...太长了。"
    # return text[:512] + "\n...太长了。"
## 随机字符串
def getStr(length=16) -> str:
    dinnerbone = ""
    strs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    for i in range(length):
        dinnerbone += random.choice(strs)
    return dinnerbone
## 名字提纯
def namePure(name: str) -> str:
    return name.strip("@").strip()
## 自定义回复的空格转换
def textPure(text: str) -> str:
    return text.replace("\\~", "~").replace("~", " ")
## 防止md代码块导致的排版错乱
def mdPure(text: str) -> str:
    return re.sub("(~~~|```)", r"\\\1", text)
## 防止md下划线导致的排版错乱
def nameMd(name: str) -> str:
    return name.replace("_", "\\_")
## 时间差
def timeDiff(seconds: int) -> str:
    if seconds >= Time.DAY:
        diff = f"{seconds // Time.DAY}日"
        return diff + timeDiff(seconds % Time.DAY)
    elif seconds >= Time.HOUR:
        diff = f"{seconds // Time.HOUR}时"
        return diff + timeDiff(seconds % Time.HOUR)
    elif seconds >= Time.MINUTE:
        diff = f"{seconds // Time.MINUTE}分"
        return diff + timeDiff(seconds % Time.MINUTE)
    elif seconds:
        return f"{seconds}秒"
    else:
        return ""
## 格式化时间
def ftime(seconds, format_="%Y-%m-%d %H:%M:%S") -> str:
    struct = gmNow(seconds)
    magnolia = time.strftime(format_, struct)
    return magnolia
## 检验字符串规范
def verify(type_, text):
    if type_ == "nick":
        return re.match(r"^@?[\w]{1,24}$", text)
    elif type_ == "trip":
        return re.match(r"^[A-Za-z0-9+/]{6}$", text)
    elif type_ == "hash":
        return re.match(r"^[A-Za-z0-9+/]{15}$", text)
    elif type_ == "color":
        return re.match(r"^#?([0-9a-fA-F]{3}){1,2}$", text)
    else:
        return None # 乖巧
## 又加回来了
def colorPic(args: str=""):
    if not args:
        loli = "https://api.lolicon.app/setu/v2"
    else:
        loli = "https://api.lolicon.app/setu/v2?" + args
    try:
        jankie = requests.get(loli, timeout=10).json()
        if jankie["error"]:
            return "API出问题啦"
        elif not jankie["data"]:
            return "没有找到符合要求的涩图啦"
        else:
            jankie = jankie["data"][0]
    except:
        return "出问题啦"
    else:
        # 过滤离谱关键词
        tags = [i for i in jankie["tags"] if not re.search("[乳魅内尻屁胸]", i)]
        url = jankie["urls"]["original"]
        pixiv = "https://www.pixiv.net/artworks/" + str(jankie["pid"])
        title = jankie["title"]
        author = jankie["author"]
        return f"![qaq]({url})\n原url：{pixiv}\n标题：{title}\n标签：{', '.join(tags)}\n作者：{author}"
## 返回日期
def nowDay() -> str:
    now_time = time.gmtime(now() + TIME_ZONE * Time.HOUR)
    return f"{now_time.tm_year}{now_time.tm_mon:0>2}{now_time.tm_mday:0>2}"
## 分解质因数！这是我的数学极限了，呜呜……
def getPrime(i, factors) -> list:
    if i < 2:
        return ["没法分解啊啊啊啊(+﹏+)"]
    for x in range(2, int(i**0.5 + 1)):
        if i % x == 0:
            factors.append(str(x))
            getPrime(int(i / x), factors)
            return factors
    factors.append(str(i))
    return factors
## Message Of The Day
# def getMotd() -> str:
#     now_time = time.gmtime(now() + TIME_ZONE * Time.HOUR)
#     year, month, day = now_time.tm_year, now_time.tm_mon, now_time.tm_mday
#     dayday = f"{year}-{month}-{day}"
#     try:
#         resInfo = requests.get("https://timor.tech/api/holiday/info/" + dayday, headers=HEADERS, timeout=10).json()
#         resNext = requests.get(f"https://timor.tech/api/holiday/next/{dayday}?week=Y", headers=HEADERS, timeout=10).json()
#         if resInfo["code"] != 0 or resNext["code"] != 0:
#             raise BaseException
#     except:
#         return "出错啦，请稍后再试(◐_◑)"
#     week = WEEKS[resInfo["type"]["week"]]
#     text = f"今天是**{year}**年 **{month}**月**{day}**日 **{week}**"
#     holiday = resInfo["holiday"]
#     if holiday:
#         text += f"\n休息日，放松一下吧~"
#     else:
#         holiday = resNext["holiday"]
#         text += f"\n距离下个休息日 **{holiday['name']}** 还有 **{holiday['rest']}** 天"

#     return userData["motd"] + "\n&ensp;\n---\n" + text
## 可爱计数
def loliNum(num: int) -> str:
    return f"![{num}](https://count.getloli.com/@:name?num={abs(num)}&padding=1)\n{num}"
## 随机字符
def randomStr(length: int=6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))

# 玩类玩的
## 时间秒数
class Time(IntEnum):
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24
    WEEK = DAY * 7
    MONTH = DAY * 30
    YEAR = DAY * 365
## 仿rate-limiter
class RateLimiter:
    def __init__(self, halflife, threshold):
        self.halflife = halflife
        self.threshold = threshold
        self.records = {}
    # 获取信息
    def search(self, name: str)->dict:
        record = self.records.get(name)
        if not record:
            record = self.records[name] = {"time": now(), "score": 0}
        return record
    def fscore(self, score, time, delta=1):
        # 使分数随时间衰减，半衰期为halflife秒
        score *= 2**((time-now())/self.halflife)
        return score + delta
    # 监测与加分
    def frisk(self, name: str, delta):
        record = self.search(name)
        # 加分
        record["score"] = self.fscore(record["score"], record["time"], delta)
        record["time"] = now()
        # 分数达到阈值(threshold)时被rl
        if record["score"] >= self.threshold:
            return 1
        return 0
    # 返回需要等多少秒才能使threshold降到to
    def waits(self, name: str, to) -> int:
        return int(math.log2(self.records[name]["score"] / to) * self.halflife)
## 用户容器
class Users:
    def __init__(self):
        self.data = {}
    def addUser(self, nick, **kwargs):
        self.data[nick] = dict(kwargs, nick=nick)
    def getUser(self, nick) -> dict:
        try:
            return self.data[nick]
        except KeyError:
            return None # 乖巧
    def delUser(self, nick):
        del self.data[nick]
    def getAttr(self, nick, attr):
        try:
            return self.data[nick][attr]
        except KeyError:
            return None # 乖巧
    def attrGet(self, attr, value):
        for nick, eric in self.data.items():
            if eric[attr] == value:
                return nick
        return None # 乖巧
    def attrsGet(self, attr, value) -> list:
        zhuyue = []
        for nick, maggie in self.data.items():
            if maggie[attr] == value:
                zhuyue.append(nick)
        return zhuyue
    def changeAttr(self, nick, attr, value):
        self.data[nick][attr] = value
    def __iter__(self):
        return iter(self.data.items())
## 消息记录器
class Peeper:
    def __init__(self):
        self.allMsg = []
        self.longlong = []
    def push(self, nick, text, customId="", userid=""):
        if len(text) > 256:
            self.longlong.append(f"{nick}:\n{text}")
            nick = "*"
            text = f"`{nick}: {text[:30]}...`全文见 {PREFIX}long {len(self.longlong)-1}".replace("\n", "")
        self.allMsg.append({
            "nick": nick,
            "text": text,
            "customId": customId,
            "userid": userid
        })
        if len(self.allMsg) > 520:
            del self.allMsg[0]
    def findCustom(self, customId, userid, mode, text):
        if not customId:
            return None
        for i in self.allMsg:
            if i["customId"] == customId and i["userid"] == userid:
                self.push("*"+i["nick"], self.addCustom(i["text"], mode, text))
                return {"nick": i["nick"], "text": self.addCustom(i["text"], mode, text)}
        return None
    def getMsg(self, i1, i2=0):
        flower = []
        if not i2:
            if i1 > 0:
                array = self.allMsg[:i1]
            else:
                array = self.allMsg[i1:]
        else:
            array = self.allMsg[i1:i2]
        for i in array:
            nick = nameMd(i["nick"])
            text = mdPure(i["text"])
            flower.append(f"{nick}: {text}")
        return "\n\n".join(flower)
    def getLong(self, index):
        return self.longlong[index]
    def getPeep(self, msg, pard=1):
        try:
            while_ = msg.split()
            want_peep = int(while_[0])
            if want_peep == 0:
                raise ValueError
            if len(while_) == 1: 
                if want_peep < 0:
                    res = self.getMsg(-want_peep)
                elif pard:
                    res = self.getMsg(-want_peep-pard, -pard)
                else:
                    res = self.getMsg(-want_peep)
            elif len(while_) > 1:
                res = self.getMsg(int(while_[0]), int(while_[1]))
            else:
                raise ValueError
            return f"：\n{res}"
        except (ValueError, IndexError):
            return "然而peep后面需要一个非零整数"
    @staticmethod
    def addCustom(origin, mode, text) -> str:
        if mode == "overwrite":
            return text
        elif mode == "append":
            return origin + text
        else:
            return text + origin
## 挂机器
class Afker:
    def __init__(self):
        self.afk = {}
    def check(self, nick) -> str:
        try:
            doing = self.afk.pop(nick)
            return f"{nick} {doing[0]} 了 {timeDiff(now() - doing[1])}, 欢迎回来(\\*￣ω￣)"
        except KeyError:
            return ""
    def add(self, nick, doing) -> str:
        self.afk[nick] = [doing, now()]
        return f"{nick} 正在{doing}, 加油ヾ(◍°∇°◍)ﾉﾞ"
    def alert(self, msg) -> str:
        huwu = []
        for nick, dpg in self.afk.items():
            if re.search(rf"@{nick}\b", msg):
                huwu.append(f"{nick} {timeDiff(now() - dpg[1])}前开始 正在{dpg[0]}, 请不要打扰ta――")
        return "\n".join(huwu)
    def list(self) -> str:
        xuan2wei1 = []
        for nick, dpg in self.afk.items():
            xuan2wei1.append(f"{nick} 正在 {dpg[0]} (从{timeDiff(now() - dpg[1])}前开始)")
        xuan2wei1 = "\n".join(xuan2wei1)
        return "### 正在挂机的……\n" + xuan2wei1 if xuan2wei1 else "大家都在哦~"
    def clear(self):
        self.afk.clear()
## 留言器
class Lefter:
    def __init__(self, msg: dict[str, dict[str, list[list]]]):
        self.msg = msg
    def add(self, type_, to, sender, senderTrip, text):
        if not verify(type_, to):
            return "昵称或识别码不合法！"
        elif not text:
            return "信息不能为空哦uwu"
        else:
            if type_ not in self.msg:
                self.msg[type_] = {}
            if to not in self.msg[type_]:
                self.msg[type_][to] = []
            self.msg[type_][to].append([sender, senderTrip, now(), text])
            self._writeJson()
            return "留言成功~"
    def check(self, **kwargs) -> str:
        k24 = []
        for type_, to in kwargs.items():
            try:
                tusk = self.msg[type_].pop(to)
            except KeyError:
                continue
            for yaya in tusk:
                if yaya[1]:
                    k24.append(f"{nameMd(yaya[0])}#{yaya[1]} 曾在（{ftime(yaya[2])}）通过{type_}给您留言：\n{mdPure(yaya[3])}")
                else:
                    k24.append(f"{nameMd(yaya[0])} 曾在（{ftime(yaya[2])}）通过{type_}给您留言：\n{mdPure(yaya[3])}")
            self._writeJson()
        return "\n\n".join(k24)
    def check_expire(self):
        save_need = False
        for _, to in self.msg.items():
            for key, value in to.copy().items():
                for i, wtf in enumerate(value.copy()):
                    if wtf[2] + Time.MONTH < now():
                        value.pop(i)
                        save_need = True
                if not value:
                    del to[key]
                    save_need = True
        if save_need:
            self._writeJson()
    def _writeJson(self):
        userData["leftMsg"] = self.msg
        writeJson("userData", userData)
## saw器
class Sawer:
    def __init__(self, last: dict):
        self.last = last or {"nick": {}, "trip": {}}
    def addUser(self, nick, trip, onSet=False):
        time = now()
        # 不是我说，就这个and和or，我自己都觉得天才
        if trip:
            self.last["nick"][nick] = trip
            self.last["trip"][trip] = onSet and self.last["trip"].get(trip) or {"time": time, "msg": None}
        else:
            self.last["nick"][nick] = onSet and self.last["nick"].get(nick) or {"time": time, "msg": None}
        self._writeJson()
    def add(self, nick, trip, msg):
        time = now()
        if trip:
            self.last["trip"][trip] = {"time": time, "msg": msg}
        else:
            self.last["nick"][nick] = {"time": time, "msg": msg}
        self._writeJson()
    def get(self, text: str, type_: str) -> str:
        user = self.last[type_].get(text)
        if not user:
            return "此人还没有光顾此处的样子(◐_◑)"
        if isinstance(user, str):
            type_ = "trip"
            text = user
            user = self.last["trip"][user]
        ltime = user["time"]
        observer = f"最后一次见到{type_}为{text}的用户是在{ftime(ltime)}（距现在{timeDiff(now() - ltime)}）\n"
        if user["msg"] is not None:
            observer += f"他说了：{user['msg'][:50]}"
        else:
            observer += "他加入了。"
        return observer
    def _writeJson(self):
        userData["lastSaw"] = self.last
        writeJson("userData", userData)
## look器
class Looker:
    def __init__(self):
        self.now = {}
    def addUser(self, nick):
        self.now[nick] = {"joined": now(), "words": 0}
    def delUser(self, nick):
        if nick in self.now:
            del self.now[nick]
    def add(self, nick):
        if nick in self.now:
            self.now[nick]["words"] += 1
    def get(self, nick) -> str:
        if nick not in self.now:
            return "查无此人ლ(´ڡ`ლ)"
        else:
            saw = self.now[nick]
            joined = now() - saw["joined"]
            if saw["words"]:
                times = joined / 60 / saw["words"]
                freq = f"每{times:.1f}分钟一次"
            else:
                freq = "无发言记录"
            return f"\n他于{timeDiff(joined)}前加入。\n发言频率：{freq}"
## 在线用户列表器
class ListChat:
    def __init__(self, channel: str, customId: str, passwd: str=""):
        self.nick = f"_list{random.randint(1, 9999)}"
        self.customId = customId
        self.channel = channel
        self.passwd = passwd

        self.oled = False
    def _sendPacket(self, packet):
        encoded = json.dumps(packet)
        try:
            self.ws.send(encoded)
        except websocket.WebSocketException:
            pass
    def rock(self) -> str:
        self.ws = websocket.create_connection(WSADD)
        self._sendPacket({"cmd": "join", "channel": self.channel, "nick": f"{self.nick}#{self.passwd}"})
        while True:
            result = json.loads(self.ws.recv())
            cmd = result["cmd"]

            if cmd == "captcha":
                self.remake(AUTH)
            elif cmd == "warn":
                text = result["text"]
                if text == "Nickname taken": # 这概率
                    self.remake()
                elif re.match(r"^You are (?:be|join)ing", text):
                    break # 开摆
            elif cmd == "info" and text.startswith("You have been denied"):
                self.remake(AUTH)
            elif result.get("channel") and result.get("channel") != self.channel:
                self.remake()
            elif cmd == "onlineSet":
                starry = ""
                for user in result["users"]:
                    if user["isme"]:
                        continue
                    if user["trip"]:
                        trip = user["trip"]
                        if user["uType"] == "mod":
                            trip += "⭐"
                    else:
                        trip = ""
                    starry += f"=={user['nick']}==, **{trip}**, {user['hash']}\n"
                self.ws.close()
                return starry or "空空如也~"
    # 重启
    def remake(self, pswd=""):
        self.ws.close()
        passwd = pswd or self.passwd
        try:
            ryo = ListChat(self.channel, self.customId, passwd)
        except:
            pass
        else:
            ryo.rock()
## 黑名单
class Black:
    def __init__(self, name: str):
        self.name = name
        self.data = userData[name]
    def add(self, type_, to) -> str:
        if not verify(type_, to):
            return "参数不合法！"
        if type_ not in self.data:
            self.data[type_] = []
        if to in self.data[type_]:
            return "已经在了"
        else:
            self.data[type_].append(to)
            self._writeJson()
            return "好好好，又进去了一个"
    def delete(self, type_, to) -> str:
        if not (verify(type_, to) and type_ in self.data):
            return "参数不合法！"
        else:
            try:
                self.data[type_].remove(to)
            except:
                return "没有"
            else:
                self._writeJson()
        return "好好好，又出去了一个"
    def check(self, **kwargs) -> bool:
        for type_, to in kwargs.items():
            if type_ not in self.data:
                continue
            elif to in self.data[type_]:
                return True
        return False
    def clear(self):
        self.data = {}
        self._writeJson()
    def list(self) -> str:
        awaya = []
        for k, v in self.data.items():
            uwuya = ", ".join(v)
            if uwuya:
                awaya.append(f"{k}: {uwuya}")
        return "\n".join(awaya)
    def _writeJson(self):
        userData[self.name] = self.data
        writeJson("userData", userData)
## 房间状态
class RoomChat:
    def __init__(self, channel: str, customId: str, nick: str=""):
        self.nick = nick
        self.customId = customId
        self.channel = channel

        self.oled = False
    def _sendPacket(self, packet):
        encoded = json.dumps(packet)
        try:
            self.ws.send(encoded)
        except websocket.WebSocketException:
            pass
    def rock(self) -> str:
        self.ws = websocket.create_connection(WSADD)
        self._sendPacket({"cmd": "join", "channel": self.channel, "nick": self.nick})
        while True:
            result = json.loads(self.ws.recv())
            cmd = result["cmd"]

            if cmd == "captcha":
                return "Captcha"
            elif cmd == "warn":
                text = result["text"]
                if text == "Nickname taken":
                    return "正常"
                elif re.match(r"^You are (?:be|join)ing", text):
                    break # 开摆
            elif cmd == "info" and text.startswith("You have been denied"):
                return "锁房"
            elif result.get("channel") and result.get("channel") != self.channel:
                self.remake()
            else:
                break
    # 重启
    def remake(self):
        self.ws.close()
        try:
            ryo = RoomChat(self.channel, self.customId, self.nick)
        except:
            pass
        else:
            ryo.rock()
## 更新motd
# class MotdChat:
#     def __init__(self, channel: str, trip: str, motd: str):
#         self.nick = f"motd_{random.randint(1, 9999)}"
#         self.trip = trip
#         self.channel = channel
#         self.motd = motd

#         self.oled = False
#     def _sendPacket(self, packet):
#         encoded = json.dumps(packet)
#         try:
#             self.ws.send(encoded)
#         except websocket.WebSocketException:
#             pass
#     def rock(self) -> str:
#         self.ws = websocket.create_connection(WSADD)
#         self._sendPacket({"cmd": "join", "channel": self.channel, "nick": self.nick + "#" + self.trip})
#         self._sendPacket({"cmd": "setmotd", "motd": self.motd})
#         self.ws.close()
#     # 重启
#     def remake(self):
#         self.ws.close()
#         try:
#             ryo = RoomChat(self.channel, self.customId, self.nick)
#         except:
#             pass
#         else:
#             ryo.rock()
## 消息数记录
class HourCount:
    def __init__(self, data: dict):
        self.data = data
        self.initDay()
        self.initHour()
    def initDay(self):
        self.today = self.data[sysList[3]]
        self.todayUsers = set(self.today["users"])
    def initHour(self):
        self.hour = self.data["hour"]
        self.hourUsers = set(self.hour["users"])
    def add(self, sender: str):
        self.todayUsers.add(sender)
        self.today["users"] = list(self.todayUsers)
        self.hourUsers.add(sender)
        self.hour["users"] = list(self.hourUsers)

        self.hour["count"] += 1
        self.today["count"] += 1
        self.save()
    def get(self) -> tuple:
        return (self.today["count"], len(self.todayUsers)), (self.hour["count"], len(self.hourUsers))
    def save(self):
        writeJson("msgCount", msgCount)
## hash器
class Hasher:
    def __init__(self, data):
        self.data = data
    def addHash(self, nick, hash_):
        if hash_ not in self.data:
            self.data[hash_] = []
        if nick not in self.data[hash_]:
            self.data[hash_].append(nick)
            writeJson("hash", self.data)
    def hashByCode(self, code: str) -> str:
        try:
            return ", ".join(self.data[code]).replace("_", "\\_")
        except:
            return "不存在这个hash码(◐_◑)"
    def hashByName(self, nick: str) -> str:
        l = []
        for i in self.data.values():
            if nick in i:
                text = "，".join(i)
                l.append(text.replace("_", "\\_"))
        l = list(set(l))
        for i, v in enumerate(l):
            l[i] = f"{i+1}\\. "+l[i]
        result = "\n".join(l) or "没有这个名字！"
        return result if len(result) < 666 else toWeb(result)
## 注解用的
class Awaish:
    def appText(self, text: str, type_: str="", **kwargs):
        """chat: 公屏, whisper: 私信, part: 强制独立(命令、custom等)"""
        ...
    def pop(self, num: int=1): ...
    def runContext(self): ...

# 读取文件们
info = readJson("info")
data = readJson("hash")
userData = readJson("userData")
replys = readJson("reply")
answer = readJson("answer")
msgCount = readJson("msgCount")

# 半常量
AUTH, MOD = info["auth"], info["mod"]
URL, TOKEN = info["url"], info["token"]
NAME, OWNER = info["name"], info["owner"]

# 全局变量
## [0涩图开关, 1报时开关, 2休眠开关, 3当前日期, 4sender nick, 5报错是否直接报错, 6心跳频率(秒), 7stfu时间, 8玩的, 9复读库, 10突然说话值]
sysList = [False, True, False, nowDay(), "", info["debug"], 120, 0, False, [], 960]
## [0上次重启]
status_list = [ftime(now())]

if sysList[3] not in msgCount:
    msgCount[sysList[3]] = {"count": 0, "users": []}
if "hour" not in msgCount:
    msgCount["hour"] = {"count": 0, "users": []}

banWords = userData["banWords"]
whiteList = userData["whiteList"]
subscribe = userData["subscribe"]
protect =  userData["protect"]
keys = userData["keys"]
welcome = userData["welText"]

msgRl = RateLimiter(20, 13)
joinRl = RateLimiter(5, 7)
wordRl = RateLimiter(30, 3)
setuRl = RateLimiter(40, 5)
left = Lefter(userData["leftMsg"])
sawer = Sawer(userData["lastSaw"])
black = Black("black")
ignore = Black("ignore")
banned = Black("banned")
hasher = Hasher(data)
hourCount = HourCount(msgCount)

lineReply = {
    # 纪念零姬……
    "0.0": ["0.0.0", ".0.", ";0;"],
    "游戏": ["\n".join([
        "象棋(cc), 真心话(t), uno(u), 数字炸弹(b), 三国杀(s), 干瞪眼(g)",
        "扑克(p), 猜单双(oe), 炸金花(z), 21点(bj)",
        "发送`<前缀> help`获取对应帮助"
    ])],

    "time": getTime,
    "today": historyToday,
}
cmdList = {
    "wht": lambda: f"当前白名单识别码：{', '.join(whiteList)}\n当前粉名单识别码：" + ", ".join(OWNER),
    "word": lambda: f"当前封禁词：{', '.join(banWords)}",
    "blk": lambda: f"当前黑名单：\n{black.list()}",
    "ign": lambda: f"当前被忽略：\n{ignore.list()}",
    "ban": lambda: f"当前被封禁：\n{banned.list()}"
}

if not os.path.exists("logs"):
    os.mkdir("logs")
if not os.path.exists("traceback"):
    os.mkdir("traceback")

for owner in OWNER:
    if not owner in whiteList:
        whiteList.append(owner)
        writeJson("userData", userData)