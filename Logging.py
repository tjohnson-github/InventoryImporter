
textLog: List[str]

def logStr(entry: Any, print=True):
    global textLog
    print(str(entry))
    textLog.append(str(entry))



def saveLog():
    global textLog

    for line in textLog:
        pass
