# encoding=utf-8
import Tkinter
import tkFileDialog
import shelve
from Tkinter import *
import time
import os

from platform import AI_Proc,GameLogic
import threading
import Queue

game_rule_text = u'''
我是SSDUT第七届科技文化节（2012年）, 第三届AI编程大赛比赛平台(GUI版) v4.0
发现bug请告诉作者：dawn110110@gmail.com

游戏规则:
- 这是一个赌博游戏，规则与2012年"SAP code slam"比赛规则相同，本程序通过标准输入输出与玩家的AI进程进行通信。

- 初始玩家1在0号位置、玩家2在10号位置 石头在5号位置
  每次双方同时出一个价格、石头往胜者方向移动、输者不扣钱
  若双方出钱相等、第一次往Player1方向移动（也就是坐标-1）之后每次平局交替移动
  当一方没钱、或者石头到达一方位置时游戏结束

使用方法:
1.已经提供c++/java/python接口，参赛选手需要完成的是选择一种语言编写AI代码。（见AI目录）
2.(GUI版中)点击 “选择玩家1的AI“ 和 “选择玩家2的AI“ 分别选择AI文件
    - 若c/c++，选择编译好的可执行程序
    - 若使用java，选择编译好的.class文件
    - 若使用python，选择.py文件即可
3.然后点击 “开始游戏” 即可看到日志输出。

4.0 更新内容(2012-12-18)：
1. 增加线程，使主界面不卡死
2. 修正游戏规则bug若干。
HAPPY CODING~
'''
bug_hints = u'''
====== ERROR ======
啊哦～平台出bug了，或者你写的AI有问题= =
常见错误：
1.是不是AI抛异常了？比如除以0抛出的异常
2.由于本AI平台对输入输出格式有要求，所以不要随意输出信息，如果需要调试，可以打开一个文件并写入
3.你的AI程序的路径中，不要有中文，请把AI放在纯英文目录中
4.如果你使用Java编写AI，请使用JDK1.7版本
'''

class GuiGameLogic(GameLogic):
    def __init__(self,ai1,ai2):
        GameLogic.__init__(self,ai1,ai2)
    def make_log_str(self):
        ''' make a log words '''
        return '\n'.join([
            '=============================================',
            '\t出钱\t余钱\t',
            'p1\t%d\t%d'%(self.p1_moves[-1],self.p1_money),
            'p2\t%d\t%d'%(self.p2_moves[-1],self.p2_money),
            'scotch_pos=%d,'%self.scotch_pos + '-'*self.scotch_pos+"X"+'-'*(10-self.scotch_pos),
            ])
    def game_begin_prepare(self):
        ''' before begin '''
        pass
    def run_one_pass(self):
        ''' run one pass '''
        # run ai again
        self.p1.run_again()
        self.p2.run_again()

        self.p1.vars = ["1",
                str(self.scotch_pos),
                ' '.join([str(x) for x in self.p1_moves]),
                ' '.join([str(x) for x in self.p2_moves])
                ]
        self.p2.vars = ["2",
                str(self.scotch_pos),
                ' '.join([str(x) for x in self.p1_moves]),
                ' '.join([str(x) for x in self.p2_moves])
                ]

        # feed vars to ai and get result
        self.p1.feed_vars()
        self.p2.feed_vars()

        # get result and remove '\n' at the end
        r1 = self.p1.get_result()
        r2 = self.p2.get_result()

        # !!!!
        if len(r1)<=1:
            self.win(2)
            return
        if len(r2)<=1:
            self.win(1)
            return

        while True:
            if r1[-1] in ['\n',',','\r','\t']:
                r1=r1[:-1]
            else:
                break
        
        while True:
            if r2[-1] in ['\n',',','\r','\t']:
                r2=r2[:-1]
            else:
                break
        r1 = int(r1)
        r2 = int(r2)
        self.r1 = r1
        self.r2 = r2

        # # commented by ZXZ
        # could not more than left money
        # if r1>self.p1_money:
        #     r1=self.p1_money
        # if r2>self.p2_money:
        #     r2=self.p2_money

        # record
        self.p1_moves.append(r1)
        self.p2_moves.append(r2)

    def tell_winner(self):
        ''' call after run_one_pass 
        if game over, reutrn True
        else return False
        '''
        r1 = self.r1
        r2 = self.r2

        if r1 <=0:
            self.win(2)
            return True
        elif r2<=0:
            self.win(1)
            return True
        if r1>r2:
            self.scotch_pos-=1
            self.p1_money-=r1
        elif r1<r2:
            self.scotch_pos+=1
            self.p2_money-=r2
        else:
            if self.equal_mark:
                self.equal_mark=False
                self.scotch_pos-=1
                self.p1_money-=r1
            else:
                self.equal_mark=True
                self.scotch_pos+=1
                self.p2_money-=r2

        # tell winner
        if self.scotch_pos<=0:
            self.win(1)
            return True
        elif self.scotch_pos>=10:
            self.win(2)
            return True

        # money left
        if self.p1_money<=0:
            self.win(2)
            return True
        elif self.p2_money<=0:
            self.win(1)
            return True
        return False # at last return False
def get_file_type(filename):
    ''' give a file name, tell a filetype'''
    divided =filename.split('.')
    tail = divided[1].lower()
    if tail in ['python','py','pyw','pyc']:
        return 'python'
    elif tail in ['class']:
        return 'java'
    elif tail in ['exe','out']:
        return 'c++'
    else:
        return ''

class MSG(object):
    def __init__(self,m):
        self.msg = m
    def __repr__(self):
        return "(GAME_MSG,%r)"%self.msg
    def __str__(self):
        return self.__repr__()
    def __unicode__(self):
        return self.__repr__()

class ThreadedGameLogic(threading.Thread,GuiGameLogic):
    def __init__(self,ai1,ai2,mq):
        GuiGameLogic.__init__(self,ai1,ai2)
        threading.Thread.__init__(self)
        self.mq = mq
    def make_log_str(self):
        ret = GuiGameLogic.make_log_str(self)
        self.mq.put(ret)
    def run(self):
        while True:
            self.run_one_pass()
            if self.tell_winner():
                break
            self.make_log_str()
        self.make_log_str()
        self.mq.put(self.win_msg)
        self.mq.put(MSG("game_end"))

class PollingMixin(object):
    ''' periodic call '''
    interval = 200 # 1 second
    running = False
    def _loop(self):
        self.polling_callback()
        if self.running:
            self.after(self.interval,self._loop)
    def polling_callback(self,*args,**kargs):
        ''' to be rewrite '''
        print self,id(self)
    def start_polling(self):
        self.running = True
        self._loop()
    def stop_polling():
        self.running = False

class Application(Frame,PollingMixin):
    WIDTH=70
    HTIGHT=400
    LOG_HEIGHT=40
    counter = 0
    mq = None # msg queue
    game_running = False
    def log(self,msg):
        '''make a log into log area'''
        self.log_area.insert('end',msg+'\n')
        self.log_area.yview_moveto(1.0) # move to bottom
    def polling_callback(self):
        ''' just get the msg and print '''
        try:
            msg = self.mq.get(0)
            if isinstance(msg,str):
                self.log(msg)
            else:
                ''' MSG type defined by myself '''
                if msg.msg == 'game_end':
                    self.game_running = False
        except Queue.Empty,e:
            pass
    def start_game(self):
        try:
            test = self.p1_file and self.p2_file
        except Exception,e:
            self.log("你还没选择AI文件哦亲！")#please choose your AI file first, then click 'start game'")
            return
        try:
            if self.game_running:
                self.log("== INFO == game running , please wait")
                return
            self.ai1 = AI_Proc(lang=get_file_type(self.p1_file),filename=self.p1_file)
            self.ai2 = AI_Proc(lang=get_file_type(self.p2_file),filename=self.p2_file)

            self.game_logic = ThreadedGameLogic(self.ai1,self.ai2,self.mq) # make the game thread
            self.log("==== GAME START ===")
            self.log("AI 1 : ...%r"%self.p1_file[-30:])
            self.log("AI 2 : ...%r"%self.p2_file[-30:])
            self.game_logic.start() # 
            self.game_running = True
        except Exception,e:
            self.game_running = False
            self.log(bug_hints)
            self.log("%r"%e)
    def clear_log(self):
        self.log_area.delete(1.0,'end')
        self.log(time.strftime('%Y年-%m月-%d日, %H:%M:%S\n',time.localtime()))#'(%r,%r)'%self.log_scroll.get())
        self.log(game_rule_text)
    def getPlayerOneFile(self):
        res = self.open_dlg.show()
        if res:
            self.p1_label.config(text='AI_1: ...'+res[-30:])# set label
            self.p1_file = res
    def getPlayerTwoFile(self):
        res = self.open_dlg.show()
        if res:
            self.p2_label.config(text='AI_2: ...'+res[-30:])# set label
            self.p2_file = res

    def createWidgets(self):
        self.btnSetPlayerFile = Button(self,
            text=u"选择玩家1的AI",
            command=self.getPlayerOneFile)
        self.btnSetPlayerFile.pack()
        self.p1_label=Label(self,text='',width=self.WIDTH)
        self.p1_label.pack()

        self.btnSetPlayerFile = Button(self,
            text=u"选择玩家2的AI",
            command=self.getPlayerTwoFile)
        self.btnSetPlayerFile.pack()
        self.p2_label=Label(self,text='',width=self.WIDTH)
        self.p2_label.pack()


        self.btnClear = Button(self,text=u'清空日志',command=self.clear_log)
        self.btnClear.pack()

        self.btnStart = Button(self,text=u'开始游戏',command=self.start_game)
        self.btnStart.pack()

        #text log
        self.log_scroll = Tkinter.Scrollbar(self)
        self.log_scroll.pack(side=RIGHT,fill=Y)

        self.log_area = Text(self,width=self.WIDTH+20,height=self.LOG_HEIGHT)
        self.log_area.focus_set()
        self.log_area.pack(side=LEFT,fill=Y)

        # self.log_scroll.command=self.log_area.yview
        # self.log_area.yscrollcommand=self.log_scroll.set
        self.log_scroll.config(command=self.log_area.yview)
        self.log_area.config(yscrollcommand=self.log_scroll.set)
    def __init__(self, master=None):
        Frame.__init__(self, master,width=self.WIDTH)
        self.open_dlg = tkFileDialog.Open(self)# dlg for open file
        self.pack()
        self.createWidgets()
        self.clear_log() # clear logs
        self.mq = Queue.Queue()
        self.interval = 200
        self.start_polling()
        self.game_running = False


if __name__=="__main__":
    root = Tk()
    app = Application(master=root)
    root.title('第七届科技文化节 "Bid Game" AI测试平台 4.0 版')
    app.mainloop()