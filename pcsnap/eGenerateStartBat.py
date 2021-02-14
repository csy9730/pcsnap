import os,sys
import re
import glob
import json

# import pyparsing
programNameList=["cmake","cmake-gui" ,"code","swig","doxygen","7z","7zFM"
,"BC2.exe","Cmder.exe","spacesniffer","curl","everything","githubDesktop"
,"Listary","notepad++","vim"]
# git mingw32-make curl 
# Dependencies
pathList =["D:/greensoftware/*/*"]


def pathExistFile(pth,target):
    """ return full path of target """
    if not os.path.isdir(pth):#如果是文件则跳过
        return "";
    filelist=os.listdir(pth)#该文件夹下所有的文件（包括文件夹）
    filelist = [ f.lower() for f in filelist]
    target= target.lower()
    return os.path.join( pth, target) if target in filelist else ""


def pathListExpand(pthList):
    """ get path list

    :param pthList: a list contain paths like "D:\\greensoftware\\*\\",will replace */? with paths.
    :return list contain path,
    """
    return [g  for pth in pthList for g in  glob.glob(pth) ] 

    
def pathListExistFile(pthList,target):
    lst =[]
    for pth in pthList:
        fd = pathExistFile(pth,target)
        if fd!="":
            lst.append(fd)
    lst2 = []
    for i in lst:
        if i not in lst2:
            lst2.append(i)

    return lst2
def pth_split(pth):
	(fp,tfn) = os.path.split(pth)
	(shn,ext) = os.path.splitext(tfn)
	return (fp,shn,ext)
def genrateBatCaller(exePath,callerPath="."):
    (fp,shn,ext) = pth_split(exePath)
    with open(os.path.join( callerPath,shn+".bat"),'w') as fp:
        fp.write("@\""+exePath+"\" %*" )
    return callerPath,shn+".bat"

def searchFile2batCaller(targetList, pthList,callerPath=None,use_tmp=False,config=None):
    pthList2 = pathListExpand(pthList)

    if config:
        with open(config,"r") as fp:
            config = json.load(fp)
            output = config["output"]
    else:
        output=[{"name": target,"files":pathListExistFile(pthList2,target)}  for target in targetList]

        

    for adct in output:
        if adct["files"] and callerPath:
            binpath=genrateBatCaller(adct["files"][0],callerPath)
            adct.update({"bin": binpath })

    if use_tmp:
        dct={
            "input":{
                "outdir":callerPath,
                "inputdir":pthList,
                "exe": targetList,
                "_env": pthList2,
            },
            "output":output
        }
        with open("tmp_startbat.json","w") as fp:
            json.dump(dct,fp,indent=2,ensure_ascii=False)
    

#----------------------test--------------------------#
def pathExistFileTest():
    pth = r"D:\greensoftware\7-Zip"
    target= "7z.exe"
    fd = pathExistFile(pth,target)
    print(fd)
def pathListExistFileTest():
    pth = [r"D:\greensoftware", r"D:\greensoftware\7-zip" ]
    target= "7z.exe"
    pth = pathListExpand(pth)
    fd = pathListExistFile(pth,target)
    print(fd)

def pathListExpandTest():
    pth = ["D:\\greensoftware\\*\\","D:\\greensoftware\\"]
    pth2 = pathListExpand(pth)
    
    print(pth2)
def genrateBatCallerTest():
    pth = "D:\\greensoftware\\7-zip\\7z.exe"
    genrateBatCaller(pth ,".")
def genrateBatCallerTest2():
    pthList = ["D:\\greensoftware\\*\\","D:\\greensoftware\\"]
    target = "7z.exe"
    exePath =pathListExistFile(pthList,target)
    if len(exePath)==1:
        genrateBatCaller(exePath[0],callerPath=".")
def test():
    pathExistFileTest()
    pathListExpandTest()
    pathListExistFileTest()
    genrateBatCallerTest()

def listdir(pth,filelist):
    for files in filelist:#遍历所有文件
        Olddir=os.path.join(pth,files);#原来的文件路径
        if os.path.isdir(Olddir):#如果是文件夹z则跳过
            continue;
        rc = re.compile("^7z.exe$")
        # fd = rc.findall(files)
        fd = re.fullmatch(rc,files)
        if fd is not None:
            print( type(fd.group()))
            return
        else:
            continue
        if files=="7z.exe":
            print( True)
def testWrap():
    pass
def main():
    import argparse
    parser = argparse.ArgumentParser(description="search exe and add it to a quickon bat file")            # description参数可以用于插入描述脚本用途的信息，可以为空
    parser.add_argument('exeName', nargs='*',help=" input exec names")
    parser.add_argument('--include','-i',default=[],action='append',dest ='inputdirs',help = 'add a path to search path,'
                                                                                        'a path such as "D:\\tmp\*" ')
    parser.add_argument('--use-env','-E',action='store_true',dest ='use_env',help = 'enable to add env.path to search path',  default=False)
    parser.add_argument('--outputdir','-o',action='store',dest ='outputdir',help = 'output bat file in the dir')
    parser.add_argument('--config','-c',action='store',dest ='config',help = 'config json file')
    parser.add_argument('--use-tmp',action='store_true',dest ='use_tmp',help = 'enable to add env.path to search path',  default=False)
    # parser.add_argument('--test','-t',action='store_true',help = 'a test')
    args = parser.parse_args()
    args = parser.parse_args(['7z.exe' , 'bc2.exe' ,'--use-env','-i', "D:\\greensoftware\\7-Zip" ,'-i', "D:\\greensoftware\\*\\","--use-tmp",
                                "-o","." , "-c","tmp_startbat.json"])
    print(args)
    if args.use_env:
        args.inputdirs.extend(os.getenv("path").split(";") ) 
          
    searchFile2batCaller(args.exeName, args.inputdirs,args.outputdir,args.use_tmp,args.config)

if __name__=='__main__':
    main()