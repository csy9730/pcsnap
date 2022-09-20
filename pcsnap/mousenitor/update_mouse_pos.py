import win32api
import time 
import random

def rcvPosChar(ofs=1):
    try:
        (x,y) = win32api.GetCursorPos()
        time.sleep(0.05)
        (x2,y2) = win32api.GetCursorPos()
        if x2==x and y2==y:
            win32api.SetCursorPos((x+ofs, y+ofs))
            print("rcvPosChar", time.ctime(),x,y)
        else:
            print("rcvPosChar", time.ctime(),x,y,0)
    except Exception as e:
        print(e)

while 1:
    rcvPosChar()
    time.sleep(30 + random.random())
    rcvPosChar(-1)
    time.sleep(30 + random.random())