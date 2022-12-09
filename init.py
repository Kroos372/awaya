import json, os

def dec(cont: str) -> str:
    if cont.startswith(u"\ufeff"):
        return cont.encode("utf8")[3:].decode("utf8")
    else:
        return cont
if __name__ == '__main__':
    with open("info.json", encoding="utf8") as f:
        info = json.loads(dec(f.read()))
        nick, owner = info["nick"], info["ownerTrip"]
    with open("userData.json", encoding="utf8") as f:
        userData = json.loads(dec(f.read()))
        blackName = userData["blackName"]
        whiteList = userData["whiteList"]
    if not nick in blackName:
        blackName.append(nick)
    if not owner in whiteList:
        whiteList.append(owner)
    if not os.path.exists("log"):
        os.mkdir("log")
    if not os.path.exists("traceback"):
        os.mkdir("traceback")
    with open("userData.json", "w", encoding="utf8") as f:
        json.dump(userData, fp=f, ensure_ascii=False, indent=2)

    input("已完成，按Enter退出。\nSuccess, press Enter to exit.")