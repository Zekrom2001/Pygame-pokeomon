import pygame as pg
import random
import time
import numpy as np
import pandas as pd
from Parasettings import *
vec = pg.math.Vector2 # 二维变量
Pdata=pd.read_excel("data\database2.xlsx")
Pskill=pd.read_excel("data\skill.xlsx")
Pmoveset=pd.read_excel("data\movesets.xlsx")
Possibility=[1.0,1.5,2.0,2.5,3.0,3.5,4.0,0.25,0.29,0.33,0.40,0.50,0.67]


# 加载与解析精灵图片
class Spritesheet:
    def __init__(self, filename):
        # 主要要使用convert()进行优化， convert()方法会 改变图片的像素格式
        # 这里加载了整张图片
        self.spritesheet = pg.image.load(filename).convert()
        
    # 从比较大的精灵表中，通过相应的xml位置，抓取中出需要的元素
    def get_image(self, x, y, width, height):
        # 创建Surface对象(画板对象)
        image = pg.Surface((width, height))
        # blit — 画一个图像到另一个
        # 将整张图片中，对应位置(x,y)对应大小(width,height)中的图片画到画板中
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        #  pygame.transform.scale 缩放的大小
        # 这里将图片缩放为原来的四倍
        image = pg.transform.scale(image, (width * 4, height * 4))
        return image
     
class subtitle(pg.sprite.Sprite):   
    def __init__(self, game, text, size, color, loc):
        self._layer=1
        self.game=game
        font = pg.font.Font(game.font_name, size) # 设置字体与大小
        self.text_surface = font.render(text, True, color) # 设置颜色
        self.text_rect = self.text_surface.get_rect() # 获得字体对象
        self.text_rect = loc
        self.draw()
    def draw(self):
        self.game.screen.blit(self.text_surface,self.text_rect)
        time.sleep(0.2)

class Player(pg.sprite.Sprite):
    def __init__(self, game, loc , isop):
        self._layer=1
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #随机获取精灵
        self.pkm=[]
        for i in range (6):
            self.pkm.append(Pokemon(random.randint(0,150)))
        #设定玩家和AI的人物图
        # self.pkm[0]=Pokemon(125)
        if isop==0:
            self.image=game.Playerimage.get_image(0,0,47,59)
            self.image.set_colorkey(WHITE)
        else:
            Opx=[15,100]
            Opy=[15,15] 
            Opw=[55,47]
            Oph=[70,66]
            Opid=random.randint(0,1)
            self.image=game.TrainerSpritesheet.get_image(Opx[Opid],Opy[Opid],Opw[Opid],Oph[Opid])
            self.image.set_colorkey(WHITE)
        self.onstage=self.pkm[0]
        self.rect=loc

class Pokemon(pg.sprite.Sprite):
    def getimage(self,index):
        orimage=pg.image.load("images\Pokemon2\{}.png".format(self.data[2])).convert()
        image=pg.Surface((120,120))
        image.blit(orimage,(0,0),(0,0,120,120))
        image=pg.transform.scale(image,(120*2,120*2))
        image.set_colorkey(BLACK)
        return image
    def __init__(self,index):
        self.data=Pdata.loc[index].values
        self.sleepclock=0
        # print(self.data)
        self.image=self.getimage(index)
        self.grades=random.randint(70,100)
        self.nickname=self.data[3]
        maxhard=508
        hardex=[]
        for i in range(5):
            hardex.append(random.randint(0,maxhard))
            maxhard-=hardex[i]
        hardex.append(maxhard)
        #初始化能力与状态
        self.hp=int((self.data[18]+31+pow(hardex[0],0.5)/8)*self.grades/50+10+self.grades)
        self.nowhp=self.hp
        self.attack=int((self.data[16]+31+pow(hardex[1],0.5)/8)*self.grades/50+5)
        self.defense=int((self.data[17]+31+pow(hardex[2],0.5)/8)*self.grades/50+5)
        self.sp_attack=int((self.data[19]+31+pow(hardex[3],0.5)/8)*self.grades/50+5)
        self.sp_defense=int((self.data[20]+31+pow(hardex[4],0.5)/8)*self.grades/50+5)
        self.speed=int((self.data[21]+31+pow(hardex[5],0.5)/8)*self.grades/50+5)
        self.state="normal"
        #获取技能
        self.moves=[]
        self.mvs=[]
        print(Pmoveset['movenumber'][Pmoveset['forme']==self.data[2]].values)
        MoveNumber=int(Pmoveset['movenumber'][Pmoveset['forme']==self.data[2]].values)
        print(MoveNumber)
        i=1
        while i<=4:
            Moveid=random.randint(1,MoveNumber)
            tmp=Pmoveset['move{}'.format(Moveid)][Pmoveset['forme']==self.data[2]].values
            if tmp==[]:
                continue
            print(tmp)
            Move=Pmoveset['move{}'.format(Moveid)][Pmoveset['forme']==self.data[2]].values[0]
            # print(Moveid,Move)
            if Move in self.moves:
                continue
            else:
                self.moves.append(Move)
                i+=1
        # self.moves.append(Pskill["英文名"][Pskill["英文名"]=="poison powder"].values[0])
        # self.moves.append(Pskill["英文名"][Pskill["英文名"]=="stun spore"].values[0])
        # self.moves.append(Pskill["英文名"][Pskill["英文名"]=="sleep powder"].values[0])
        # self.moves.append(Pskill["英文名"][Pskill["英文名"]=="will-o-wisp"].values[0])
        for i in range(4):
            self.mvs.append(Skill(self.moves[i]))
        # print(self.moves)
    def delta(self,S,op):
        #属性加成 = 精灵对属性抗性
        typedelta=Pdata["against_{}".format(S.data[10])][Pdata["name"]==op.data[2]].values[0]
        #暴击加成
        criticalP=self.speed*100/512
        criticalA=random.randint(0,100)
        if criticalA <criticalP:
            criticaldelta=1.5
        else:
            criticaldelta=1.0
        if self.data[8]== S.data[10] or self.data[9] == S.data[10]:
            relationdelta=1.5
        else:
            relationdelta=1.0
        return typedelta * criticaldelta * relationdelta * random.randint(85,100)/100
    def useskill(self,k,who):
        op=who.onstage
        S=self.mvs[k]
        dou=self.delta(S,op)
        # print(S.type,self.grades,self.delta(S,op),self.attack,S.power)
        #伤害计算
        if S.type==1:
            damage=((2*self.grades+10)/250*self.attack/op.defense*S.power+2)*dou
        elif S.type==2:
            damage=((2*self.grades+10)/250*self.sp_attack/op.sp_defense*S.power+2)*dou
        else:
            damage=0
        #效果判断
        if damage>0 and dou >=2:
            who.game.screen.fill(WHITE)
            who.game.all_sprites.draw(who.game.screen)
            who.game.starttitle=subtitle(who.game,"效果拔群", 48, WHITE, (-8+40, 438+20))
            who.game.drawstate()
            pg.display.flip()
            who.game.draw()
        elif damage>0 and dou<=0.5:
            who.game.screen.fill(WHITE)
            who.game.all_sprites.draw(who.game.screen)
            who.game.starttitle=subtitle(who.game,"效果不佳", 48, WHITE, (-8+40, 438+20))
            who.game.drawstate()
            pg.display.flip()
            who.game.draw()
        op.nowhp-=damage
        #特殊效果-改变精灵状态
        if S.name=="鬼火":
            op.state="burned"
            op.attack/=2
        if S.name=="麻痹粉" :
            op.state="para"
            op.speed/=2
        if S.name=="毒粉":
            op.state="posioned"
            op.speed/=2
        if S.name=="睡眠粉":
            op.state="sleep"
            op.sleepclock=random.randint(1,3)
        #技能值减少
        S.PPnow-=1
        
class Skill(pg.sprite.Sprite):
    def __init__(self,SkillName):
        # print(SkillName)
        if Pskill["编号"][Pskill["英文名"]==SkillName].values==[]:
            self.Skillid=1    
        else:
            self.Skillid=Pskill["编号"][Pskill["英文名"]==SkillName].values[0]
        # print(self.Skillid)
        self.data=Pskill.loc[self.Skillid-1].values
        # print(self.data)
        if self.data[5]=="物理":
            self.type=1
        elif self.data[5]=="特殊":
            self.type=2
        else :
            self.type=0
        self.name=self.data[1]
        if self.data[7] != '—' and self.data[7] !="变化":
            self.accuracy=int( self.data[7])
        else:
            self.accuracy='—'
        if self.data[6] != '—' and self.data[6] !="变化" :
            self.power=int(self.data[6])
        else :
            self.power=0
        self.PPmax=int(self.data[8])
        self.PPnow=self.PPmax
    
class BackGround(pg.sprite.Sprite):
    def __init__(self,game):
        self._layer=0
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image1=game.BattleGroundSpritesheet.get_image(0,110*(game.Groundid-1),240,108)
        self.image1.set_colorkey(BLACK)
        self.image2=game.PokemonstateSpritesheet.get_image(470,76,240,48)
        # self.image2.set_colorkey(BLACK)
        self.image=pg.Surface((WIDTH*2,HEIGHT*2))
        self.image.fill(WHITE)
        self.image.blit(self.image1,(0,0))
        self.image.blit(self.image2,(-8,432))
        self.rect=(0,0)
# 道具对象
class Pow(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.image=game.PokemonstateSpritesheet.get_image(370,175,240,160)


