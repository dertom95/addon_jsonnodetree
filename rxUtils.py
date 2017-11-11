class rxData:
    disposeables=[]

def addDisposable(disp):
    rxData.disposeables.append(disp)

def disposeAll():
    for disposable in rxData.disposeables:
        print("##########dispose:"+str(disposable))
        disposable.dispose()
    rxData.disposeables=[]
