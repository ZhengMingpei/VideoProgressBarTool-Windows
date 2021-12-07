from PIL import Image,ImageFont,ImageDraw
import string,time,os,sys,json

FOREGROUND = 1
BACKGROUND = 2

def strCountUnits(str):
    '''找出字符串共占多少单位英文字母宽度
    （含中英文、空格、数字、标点符号）
    中文按照两个单位英文字母宽度
    '''
    count_en = count_dg = count_sp = count_zh = count_pu = 0
    for s in str:
        # 英文
        if s in string.ascii_letters:
            count_en += 1
        # 数字
        elif s.isdigit():
            count_dg += 1
        # 空格
        elif s.isspace():
            count_sp += 1
        # 中文
        elif s.isalpha():
            count_zh += 1
        # 特殊字符
        else:
            count_pu += 1
    return count_en+count_dg+count_sp+count_zh*2+count_pu

class Model:
    def __init__(self,config_file_name):
        with open(config_file_name, "r",encoding="utf-8") as f:
            config = json.load(f)
        self.timeline = []
        for i in config['timeLine']:
            self.timeline.append([i['endTime'],i['text']])
        self.videowidth = config['video']['width']
        self.videoheight = config['video']['height']
        self.probarheight = config['processbar']['height']
        self.probarbackcolor = config['processbar']['background']
        self.probarforecolor = config['processbar']['foreground']
        self.textfont = config['text']['font']
        self.textsize = config['text']['size']
        self.textcolor = config['text']['color']
        self.cutcolor = config['text']['cutcolor']
    def __str__(self) -> str:
        a = ""
        for name,value in vars(self).items():  ###dir()和vars()的区别就是dir()只打印属性（属性,属性......）而vars()则打印属性与属性的值（属性：属性值......）
            a = a + name +"=" +str(value)+"\n"
        return a

    def createImgColor(self,imgtype):
        imgTemp = Image.new('RGBA',(self.videowidth,self.videoheight),"#00000000")
        if(imgtype==BACKGROUND):
            colorRegion = Image.new('RGBA',(self.videowidth,self.probarheight),self.probarbackcolor)
        else:
            colorRegion = Image.new('RGBA',(self.videowidth,self.probarheight),self.probarforecolor)
        imgTemp.paste(colorRegion,(0,self.videoheight-self.probarheight))
        return imgTemp

    def createImgText(self):
        imgTemp = Image.new('RGBA',(self.videowidth,self.videoheight),"#00000000")
        # colorRegion = Image.new('RGBA',(self.videowidth,self.probarheight),self.probarbackcolor)
        # imgTemp.paste(colorRegion,(0,self.videoheight-self.probarheight))
        font = ImageFont.truetype(self.textfont, size=self.textsize)
        altime = self.timeline[-1][0]
        lastendtime = 0
        for i in self.timeline:
            draw = ImageDraw.Draw(imgTemp)
            abPosY = self.videoheight- self.probarheight + (self.probarheight - self.textsize)/2 
            if(abPosY<0 or abPosY>=self.videoheight):
                abPosY = 0
            textLeftUpPosxy = ((i[0]+lastendtime)/2/altime*self.videowidth-strCountUnits(i[1])/2*self.textsize/2,abPosY)
            # text position: left, top
            draw.text(xy=textLeftUpPosxy, text=i[1], font=font,fill=self.textcolor,anchor="lt")
            draw.line(xy=[(i[0]/altime*self.videowidth,self.videoheight-self.probarheight),(i[0]/altime*self.videowidth,self.videoheight)],fill=self.cutcolor,width=3)
            # draw.line(xy=[(i[2]*self.videoWidth,self.videoHeight-self.processBarHeight),(i[2]*self.videoWidth,self.videoHeight)],fill=self.processBarTextColor,width=3)        
            lastendtime = int(i[0])
        return imgTemp


if __name__ == "__main__":
    if(len(sys.argv)!=2):
        print("参数不正确，应指定1个json配置文件")
        exit()
    jsonfile = sys.argv[1]
    dirname = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    if(sys.platform=='win32'):
        absdirname = os.getcwd()+"\\"+dirname
    else:
        absdirname = os.getcwd()+"/"+dirname
    if(os.path.exists(absdirname)==False):
        os.mkdir(absdirname)

    # windows
    if(sys.platform=='win32'):
        absdirname = absdirname + "\\"
        os.system('copy '+jsonfile + ' '+ absdirname  + jsonfile)
    # linux
    else:
        absdirname = absdirname + "/"
        os.system('cp '+jsonfile + ' '+ absdirname  + jsonfile)  
    
    a = Model(jsonfile)
    print(a)

    a.createImgText().save(absdirname+"01-text.png",'png')
    print("01-text.png")
    a.createImgColor(FOREGROUND).save(absdirname+"02-foreground.png",'png')
    print("02-foreground.png")
    a.createImgColor(BACKGROUND).save(absdirname+"03-background.png",'png')
    print("03-background.png")
