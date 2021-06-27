import pygame as pg
import time
import random
import os
from Parasettings import *
from Pokemonsprites import *
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei'] #指定默认字体为黑体
mpl.rcParams['axes.unicode_minus'] = False #解决将负号'-'显示为方块的问题
k=0
winner=0
def k():
    m=0
    #简易AI挑选技能
    maxdamage=0
    for i in range(4):
        if maxdamage < g.opponent.onstage.mvs[i].power:
            m=i
    maxdamage=g.opponent.onstage.mvs[i].power
    return m

class Game:
    def __init__(self):
        pg.init()
        #渲染
        pg.mixer.init()
        #设置大小
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        # 设置绘制时使用的字体
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()
        self.Groundid=random.randint(1,9)
    def load_data(self): # 加载数据
        self.dir = os.path.dirname(__file__)
        img_dir = os.path.join(self.dir,'images')
        # 加载精灵图片
        self.BattleGroundSpritesheet = Spritesheet(os.path.join(img_dir,'BattleGround.png'))
        self.PokemonstateSpritesheet = Spritesheet(os.path.join(img_dir,'Pokemonstate.png'))
        self.PokemonBagSpritesheet = Spritesheet(os.path.join(img_dir,'PokemonBag.png'))
        self.ToolbagSpritesheet = Spritesheet(os.path.join(img_dir,'Toolbag.png'))
        self.TrainerSpritesheet = Spritesheet(os.path.join(os.path.join(img_dir,'Player'),'Trainer2.png'))
        self.Playerimage =Spritesheet(os.path.join(os.path.join(img_dir,'Player'),'lucas3.png'))
        # 加载音乐
        # self.snd_dir = os.path.join(self.dir, 'snd')
        # 跳跃时音效
        # self.jump_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Jump33.wav'))
        # 使用道具时音效
        # self.boost_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Boost16.wav'))

    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        # 游戏的背景音乐
        # pg.mixer.music.load(os.path.join(self.snd_dir, 'Happy Tune.ogg'))
        #初始化
        for sprites in self.all_sprites:
            sprites.kill() 
        #游戏背景和玩家初始化
        self.ground=BackGround(self)
        self.player=Player(self,(60,200),0)
        self.opponent=Player(self,(600,30),1)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.ground)
        self.all_sprites.add(self.opponent)
        self.turn=0
        winner=0
        self.run()
        
    def run(self):
        # loops表示循环次数，-1表示音乐将无限播放下去
        # pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.draw()          #绘制每回合开始选项
            self.events()        #根据鼠标操作改变界面
            self.update()        #回合结束更新状态
        # 退出后停止音乐，fadeout(time)设置音乐淡出的时间，该方法会阻塞到音乐消失
        # pg.mixer.music.fadeout(500)
    def wait_for_operation(self):
        operating=True
        while operating:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    operating = False
                    self.playing = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    operating=False
    def draw_shield_bar(self, surf, x, y, pct):
        if pct < 0:
            pct = 0
        BAR_LENGTH = 194
        BAR_HEIGHT = 17.5
        fill = (pct / 100) * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        pg.draw.rect(surf, GREEN, fill_rect)
        pg.draw.rect(surf, WHITE, outline_rect, 2)
        return 

    def update(self):
        self.all_sprites.update()
        #死亡判定
        if self.opponent.onstage.nowhp<=0:
            self.opponent.onstage.state="death"
        if self.player.onstage.nowhp<=0:
            self.player.onstage.state="death"
        #死亡换宠
        if self.opponent.onstage.state=="death":
            for i in range(1,6):
                if self.opponent.pkm[i].state !="death":
                    self.opponent.onstage=self.opponent.pkm[i]
                    self.opponent.image=self.opponent.onstage.image
                    self.opponent.pkm[0],self.opponent.pkm[i]=self.opponent.pkm[i],self.opponent.pkm[0]
                    break
        #全部濒死 游戏结束 并判定胜者
        if self.opponent.onstage.state=="death":
            self.playing=False
            winner=1
        #玩家宠物濒死,若有活着的强制进入换宠状态，否则结束
        if self.player.onstage.state=="death":
            flag=0
            for i in range(1,6):
                if self.player.pkm[i].state !="death":
                    flag=1
                    self.draw2()
                    break
            if flag==0:
                self.playing==False
        return 
    #事件处理
    #核心代码
    def events(self):
        if self.turn ==0 :
            self.turn +=1
            return 
        oping=True
        while oping:
            for event in pg.event.get():
                # 关闭
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False
                    oping=False
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN :
                    pos=pg.mouse.get_pos()
                    x=int(pos[0])
                    y=int(pos[1])
                    if y<455 :
                        continue
                    if x<WIDTH//2 and y<515:
                        #技能栏
                        self.draw1()
                        oping=False
                    elif x>WIDTH//2 and y<515:
                        #精灵栏
                        self.draw2()
                        oping=False
                    elif x<WIDTH//2 and y>515:
                        #背包栏
                        self.draw3()
                        oping=False
                    elif x>WIDTH//2 and y>515:
                        #重开栏
                        self.draw4()
                        oping=False
        self.turn +=1  
        self.statechange(self.player.onstage)
        self.statechange(self.opponent.onstage)
    def statechange(self,who):
        if who.state=="burned":
            who.nowhp-=who.hp/16
        if who.state=="poisoned":
            who.nowhp-=who.hp/8
    def draw1(self):
        #技能面板
        self.screen.fill(WHITE)
        Pokn=self.player.onstage
        self.all_sprites.draw(self.screen)
        self.drawstate()
        self.option1=subtitle(self,Pokn.mvs[0].name,30,WHITE,(-8+40,438+20))
        self.option1=subtitle(self,str(Pokn.mvs[0].PPnow)+"/"+str(Pokn.mvs[0].PPmax)+Pokn.mvs[0].data[4]+str(Pokn.mvs[0].power)+"(威)"+str(Pokn.mvs[0].accuracy)+"命",30,WHITE,(-8+200,438+20))
        self.option2=subtitle(self,Pokn.mvs[1].name,30,WHITE,(WIDTH//2+40,438+20)) 
        self.option1=subtitle(self,str(Pokn.mvs[1].PPnow)+"/"+str(Pokn.mvs[1].PPmax)+Pokn.mvs[1].data[4]+str(Pokn.mvs[1].power)+"(威)"+str(Pokn.mvs[1].accuracy)+"命",30,WHITE,(WIDTH//2+160,438+20))
        self.option3=subtitle(self,Pokn.mvs[2].name,30,WHITE,(-8+40,438+120))
        self.option1=subtitle(self,str(Pokn.mvs[2].PPnow)+"/"+str(Pokn.mvs[2].PPmax)+Pokn.mvs[2].data[4]+str(Pokn.mvs[2].power)+"(威)"+str(Pokn.mvs[2].accuracy)+"命",30,WHITE,(-8+200,438+120))
        self.option4=subtitle(self,Pokn.mvs[3].name,30,WHITE,(WIDTH//2+40,438+120))
        self.option1=subtitle(self,str(Pokn.mvs[3].PPnow)+"/"+str(Pokn.mvs[3].PPmax)+Pokn.mvs[3].data[4]+str(Pokn.mvs[3].power)+"(威)"+str(Pokn.mvs[3].accuracy)+"命",30,WHITE,(WIDTH//2+160,438+120))
        pg.display.flip()
        draw1ing=True
        while draw1ing:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    draw1ing = False
                    self.playing = False
                if event.type == pg.KEYUP:
                    draw1ing =False
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos=pg.mouse.get_pos()
                    x=int(pos[0])
                    y=int(pos[1])
                    if y<455 :
                        continue
                    if x<WIDTH//2 and y<515:
                        if self.player.onstage.speed<self.opponent.onstage.speed:
                            self.opponent.onstage.useskill(k(),self.player)    
                            self.update()
                            if self.player.onstage.sleepclock>0:
                               self.player.onstage.sleepclock-=1
                               if self.player.onstage.sleepclock==0:
                                   self.player.onstage.state=="normal"
                               draw1ing=False
                            self.player.onstage.useskill(0,self.opponent)
                        else:
                            if self.player.onstage.sleepclock>0:
                               self.player.onstage.sleepclock-=1
                               self.opponent.onstage.useskill(k(),self.player) 
                               if self.player.onstage.sleepclock==0:
                                   self.player.onstage.state=="normal"
                               draw1ing=False
                            self.player.onstage.useskill(0,self.opponent)
                            self.update()
                            self.opponent.onstage.useskill(k(),self.player) 
                    elif x>WIDTH//2 and y>515:
                        if self.player.onstage.speed<self.opponent.onstage.speed:
                            self.opponent.onstage.useskill(k(),self.player)
                            self.update()
                            if self.player.onstage.sleepclock>0:
                               self.player.onstage.sleepclock-=1
                               if self.player.onstage.sleepclock==0:
                                   self.player.onstage.state=="normal"
                               draw1ing=False
                            self.player.onstage.useskill(3,self.opponent)
                        else:
                            if self.player.onstage.sleepclock>0:
                               self.player.onstage.sleepclock-=1
                               self.opponent.onstage.useskill(k(),self.player) 
                               if self.player.onstage.sleepclock==0:
                                   self.player.onstage.state=="normal"
                               draw1ing=False
                            self.player.onstage.useskill(3,self.opponent)
                            self.update()
                            self.opponent.onstage.useskill(k(),self.player)
                    elif x<WIDTH//2 and y>515:
                        if self.player.onstage.speed<self.opponent.onstage.speed:
                            self.opponent.onstage.useskill(k(),self.player)
                            self.update()
                            if self.player.onstage.sleepclock>0:
                               self.player.onstage.sleepclock-=1
                               if self.player.onstage.sleepclock==0:
                                   self.player.onstage.state=="normal"
                               draw1ing=False
                            self.player.onstage.useskill(2,self.opponent)
                        else:
                            if self.player.onstage.sleepclock>0:
                               self.player.onstage.sleepclock-=1
                               self.opponent.onstage.useskill(k(),self.player) 
                               if self.player.onstage.sleepclock==0:
                                   self.player.onstage.state=="normal"
                               draw1ing=False
                            self.player.onstage.useskill(2,self.opponent)
                            self.update()
                            self.opponent.onstage.useskill(k(),self.player) 
                    elif x>WIDTH//2 and y<515:
                        if self.player.onstage.speed<self.opponent.onstage.speed:
                            self.opponent.onstage.useskill(k(),self.player)
                            self.update()
                            if self.player.onstage.sleepclock>0:
                               self.player.onstage.sleepclock-=1
                               if self.player.onstage.sleepclock==0:
                                   self.player.onstage.state=="normal"
                               draw1ing=False
                            self.player.onstage.useskill(1,self.opponent)
                        else:
                            if self.player.onstage.sleepclock>0:
                               self.player.onstage.sleepclock-=1
                               self.opponent.onstage.useskill(k(),self.player) 
                               if self.player.onstage.sleepclock==0:
                                   self.player.onstage.state=="normal"
                               draw1ing=False
                            self.player.onstage.useskill(1,self.opponent)
                            self.update()
                            self.opponent.onstage.useskill(k(),self.player) 
                    draw1ing=False 
    def draw2(self):
        #精灵界面
        self.screen.fill(WHITE)
        Pokn=self.player.onstage 
        self.all_sprites.draw(self.screen)
        self.drawstate()
        self.option1=subtitle(self,self.player.pkm[0].data[3]+"(在场)",30,WHITE,(-8+40,438+20))
        self.option2=subtitle(self,self.player.pkm[1].data[3]+self.player.pkm[1].state,30,WHITE,(WIDTH//3+40,438+20))
        self.option3=subtitle(self,self.player.pkm[2].data[3]+self.player.pkm[2].state,30,WHITE,(-8+40,438+80))
        self.option4=subtitle(self,self.player.pkm[3].data[3]+self.player.pkm[3].state,30,WHITE,(WIDTH//3+40,438+80))
        self.option5=subtitle(self,self.player.pkm[4].data[3]+self.player.pkm[4].state,30,WHITE,(WIDTH*2//3+40,438+20))
        self.option6=subtitle(self,self.player.pkm[5].data[3]+self.player.pkm[5].state,30,WHITE,(WIDTH*2//3+40,438+80))
        pg.display.flip()
        draw2ing=True
        while draw2ing:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    draw2ing = False
                    self.playing = False
                if event.type == pg.KEYUP:
                    draw2ing = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos=pg.mouse.get_pos()
                    x=int(pos[0])
                    y=int(pos[1])
                    if y<455 :
                        continue
                    elif x>WIDTH//3 and  x< WIDTH*2//3 and y<515:
                        if self.player.pkm[1].state=="death":
                            continue
                        self.player.onstage=self.player.pkm[1]
                        self.player.pkm[0],self.player.pkm[1]=self.player.pkm[1],self.player.pkm[0]
                    elif x>WIDTH*2//3 and y<515:
                        if self.player.pkm[2].state=="death":
                            continue
                        self.player.onstage=self.player.pkm[4]
                        self.player.pkm[0],self.player.pkm[4]=self.player.pkm[4],self.player.pkm[0]
                    elif x<WIDTH//3 and y>515:
                        if self.player.pkm[3].state=="death":
                            continue
                        self.player.onstage=self.player.pkm[2]
                        self.player.pkm[0],self.player.pkm[2]=self.player.pkm[2],self.player.pkm[0]
                    elif x>WIDTH//3 and  x< WIDTH*2//3 and y>515:
                        if self.player.pkm[4].state=="death":
                            continue
                        self.player.onstage=self.player.pkm[3]
                        self.player.pkm[0],self.player.pkm[3]=self.player.pkm[3],self.player.pkm[0]
                    elif x>WIDTH*2//3 and y>515:
                        if self.player.pkm[5].state=="death":
                            continue
                        self.player.onstage=self.player.pkm[5]
                        self.player.pkm[0],self.player.pkm[5]=self.player.pkm[5],self.player.pkm[0]
                    self.player.image=self.player.onstage.image
                    self.opponent.onstage.useskill(k(),self.player)
                    draw2ing=False
    def draw3(self):
        #背包界面
        self.screen.fill(WHITE)
        self.Toolbag=Pow(self)
        self.screen.blit(self.Toolbag.image,(0,0))
        self.medcine=subtitle(self,"好伤药",40,BLACK,(400,80))
        pg.display.flip()
        draw3ing=True
        while draw3ing:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    draw3ing = False
                    self.playing = False
                if event.type == pg.KEYUP:
                    draw3ing =False
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos=pg.mouse.get_pos()
                    print(pos)
                    x=int(pos[0])
                    y=int(pos[1])
                    if y>455 :
                        draw3ing=False
                    #使用好伤药回复
                    if x>360 and x<589 and y>60 and y<120:
                        self.player.onstage.nowhp+=200
                        self.player.onstage.nowhp=min(self.player.onstage.nowhp,self.player.onstage.hp)
                        self.opponent.onstage.useskill(k(),self.player)
                        draw3ing=False
    def draw4(self):
        self.playing = False
    def draw(self):
        # 绘制背景和人物
        #注意这里要重新渲染成底色
        self.screen.fill(WHITE)
        self.all_sprites.draw(self.screen)
        #展示可操作选项
        if self.turn==0:
            self.starttitle=subtitle(self,u"野生的训练家出现了", 48, WHITE, (-8+40, 438+20))
            self.player.image=self.player.onstage.image
            self.player.rect=(70,250)
            self.opponent.image=self.opponent.onstage.image
        else:
            self.drawstate()
            self.option1=subtitle(self,"技能",48,WHITE,(-8+40,438+20))
            self.option2=subtitle(self,"精灵",48,WHITE,(WIDTH//2+40,438+20))
            self.option3=subtitle(self,"道具",48,WHITE,(-8+40,438+80))
            self.option4=subtitle(self,"重开",48,WHITE,(WIDTH//2+40,438+80))
        pg.display.flip()
    #更新血量、状态
    def drawstate(self):
        self.state=self.PokemonstateSpritesheet.get_image(633,200,100,30)
        self.state2=self.PokemonstateSpritesheet.get_image(633,200,100,30)
        self.state.set_colorkey(WHITE)
        self.state2.set_colorkey(WHITE)
        self.screen.blit(self.state,(40,40))
        self.screen.blit(self.state2,(500,300))
        self.draw_shield_bar(self.screen, 653, 377, int(self.player.onstage.nowhp*100/self.player.onstage.hp )) 
        self.draw_shield_bar(self.screen, 195, 119, int(self.opponent.onstage.nowhp*100/self.opponent.onstage.hp ))
        self.name1=subtitle(self,self.player.onstage.data[3],30,BLACK,(520,335))
        self.name2=subtitle(self,self.opponent.onstage.data[3],30,BLACK,(80,70))
        self.level1=subtitle(self,str(self.player.onstage.grades),30,BLACK,(750,335))
        self.level2=subtitle(self,str(self.opponent.onstage.grades),30,BLACK,(280,70))
        self.pstate=subtitle(self,str(self.player.onstage.state),30,BLACK,(630,335))
        self.ostate=subtitle(self,str(self.opponent.onstage.state),30,BLACK,(180,70))
        self.hp1=subtitle(self,str(int(self.player.onstage.nowhp))+"/"+str(self.player.onstage.hp),30,BLACK,(670,365))
        self.hp2=subtitle(self,str(int(self.opponent.onstage.nowhp))+"/"+str(self.opponent.onstage.hp),30,BLACK,(220,110))
    # 开始游戏的钩子函数
    def show_start_screen(self): 
        # pg.mixer.music.load(os.path.join(self.snd_dir, 'Yippee.ogg'))
        # pg.mixer.music.play(loops=-1)

        self.screen.fill(BGCOLOR) # 填充颜色
        # 绘制文字
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Let's Enjoy Pokemon Battle!", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to start the game", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("NOTICE: Press any key to go back",22, WHITE, WIDTH / 2, HEIGHT * 4 / 5)
        # 画布翻转
        pg.display.flip()
        self.wait_for_key() # 等待用户敲击键盘中的仍以位置
        # pg.mixer.music.fadeout(500)
    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT: # 点击退出，结束等待循环
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP: # 按下键盘，结束等待循环
                    waiting = False
    def show_go_screen(self):
        # game over/continue
        if not self.running: # 是否在运行
            return
        # pg.mixer.music.load(os.path.join(self.snd_dir, 'Yippee.ogg'))
        # pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR) # 游戏框背景颜色填充
        # 绘制文字
        if winner==1:
            self.draw_text("玩家获胜", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        else:
            self.draw_text("AI获胜", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        # self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        # 等待敲击任意键，
        self.wait_for_key()
        # pg.mixer.music.fadeout(500)
    # 绘制文字
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size) # 设置字体与大小
        text_surface = font.render(text, True, color) # 设置颜色
        text_rect = text_surface.get_rect() # 获得字体对象
        text_rect.midtop = (x, y) # 定义位置 
        self.screen.blit(text_surface, text_rect) # 在屏幕中绘制字体

print("输入你的学号姓名：")
user=input()
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()
pg.quit()
