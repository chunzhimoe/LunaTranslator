
import time 
import functools   
import threading 
import os
import winsharedutils
from traceback import print_exc
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout,QApplication
from PyQt5.QtCore import Qt, pyqtSignal  ,QThread
import qtawesome 
from PyQt5.QtCore import pyqtSignal,Qt,QRect,QSize  
from PyQt5.QtGui import  QFont  ,QIcon,QPixmap  ,QMouseEvent
from PyQt5.QtWidgets import  QLabel ,QPushButton ,QSystemTrayIcon ,QAction,QMenu 
import win32utils
import pyperclip,queue
from utils.config import globalconfig,saveallconfig,_TR
from utils.subproc import endsubprocs
import  win32con
import gui.rangeselect
from utils.utils import update
from utils.subproc import subproc_w
from utils.hwnd import mouseselectwindow 
from gui.dialog_savedgame import dialog_savedgame
from gui.dialog_memory import dialog_memory
from gui.textbrowser import Textbrowser
from utils.fullscreen import fullscreen
from gui.rangeselect  import moveresizegame 
from gui.usefulwidget import resizableframeless
class QUnFrameWindow(resizableframeless):   
    displayres =  pyqtSignal(str,str,str ) 
    displayraw1 =  pyqtSignal(list, str,str )  
    displaystatus=pyqtSignal(str,str,bool) 
    showhideuisignal=pyqtSignal()
    hookfollowsignal=pyqtSignal(int,tuple)
    toolbarhidedelaysignal=pyqtSignal() 
    showsavegame_signal=pyqtSignal() 
    clickRange_signal=pyqtSignal(bool)
    rangequick=pyqtSignal()
    showhide_signal=pyqtSignal()
    grabwindowsignal=pyqtSignal()
    bindcropwindow_signal=pyqtSignal()
    fullsgame_signal=pyqtSignal()
    quitf_signal=pyqtSignal() 
    refreshtooliconsignal=pyqtSignal()
    hidesignal=pyqtSignal()
    muteprocessignal=pyqtSignal()   
    def hookfollowsignalsolve(self,code,other): 
        if self._move_drag:
            return 
        if code==3:
            if self.hideshownotauto:
                self.show_()
                try:
                    win32utils.SetForegroundWindow(other[0])
                except:
                    pass
        elif code==4: 
            if self.hideshownotauto:
                self.hide_()
        elif code==5:
            #print(self.pos())
            #self.move(self.pos() + self._endPos)z
            _r=self.object.range_ui
            _r.move(_r.pos().x()+ other[0],_r.pos().y()+ other[1])
            self.move(self.pos().x()+ other[0],self.pos().y()+ other[1])
            #self.move(self.pos().x()+self.rate *other[0],self.pos().y()+self.rate *other[1])
        
    def showres(self,name,color,res):  
        try:
            
            if globalconfig['showfanyisource']:
                #print(_type)
                #self.showline((None,globalconfig['fanyi'][_type]['name']+'  '+res),globalconfig['fanyi'][_type]['color']  )
                self.showline(False,[None,name+'  '+res],color ,1 )
            else:
                #self.showline((None,res),globalconfig['fanyi'][_type]['color']  )
                self.showline(False,[None,res],color  ,1)
            #print(globalconfig['fanyi'][_type]['name']+'  '+res+'\n')
            
            self.object.transhis.getnewtranssignal.emit(name,res)
        except:
            print_exc() 
    def showraw(self,hira,res,color ): 
        if globalconfig['isshowhira'] and globalconfig['isshowrawtext']:
            self.showline(True,[hira,res],color , 2 )
        elif globalconfig['isshowrawtext']:
            self.showline(True,[hira,res],color,1)
        else:
            self.showline(True,None,None,1)
       
        self.object.transhis.getnewsentencesignal.emit(res) 
        self.object.edittextui.getnewsentencesignal.emit(res)  
    def showstatus(self,res,color,clear): 
        self.showline(clear,[None,res],color,1)
    def showline (self,clear,res,color ,type_=1):   
        if clear:
            self.translate_text.clear_and_setfont()
        if res is None:
            return 
        if globalconfig['showatcenter']:
            self.translate_text.setAlignment(Qt.AlignCenter)
        else:
            self.translate_text.setAlignment(Qt.AlignLeft)

        
        if globalconfig['zitiyangshi'] ==2: 
            self.translate_text.mergeCurrentCharFormat_out(globalconfig['miaobiancolor'],color, globalconfig['miaobianwidth2']) 
        elif globalconfig['zitiyangshi'] ==1:  
            self.translate_text.mergeCurrentCharFormat( color, globalconfig['miaobianwidth']) 
        elif globalconfig['zitiyangshi'] ==0: 
            self.translate_text.simplecharformat(color)
        elif globalconfig['zitiyangshi'] ==3: 
            self.translate_text.simplecharformat(color)  
        if type_==1: 
            self.translate_text.append (res[1],[]) 
        else:   
            self.translate_text.append (res[1],res[0])    
        if globalconfig['zitiyangshi'] ==3:
            self.translate_text.showyinyingtext(color  ) 
        if (globalconfig['usesearchword'] or globalconfig['show_fenci']  ) and res[0]:
            self.translate_text.addsearchwordmask(res[0],res[1],self.object.searchwordW.getnewsentencesignal.emit   ) 
        
        
        if globalconfig['autodisappear']:
            if self.hideshownotauto:
                flag=(self.showintab and self.isMinimized()) or (not self.showintab and self.isHidden())
        
                if flag:
                    self.show_()
            self.lastrefreshtime=time.time()
            self.autohidestart=True  
    def autohidedelaythread(self):
        while True:
            if globalconfig['autodisappear'] and self.autohidestart:
                tnow=time.time()
                if tnow-self.lastrefreshtime>=globalconfig['disappear_delay']:
                    self.hidesignal.emit() 
                    self.autohidestart=False
                    self.lastrefreshtime=tnow
                    
            time.sleep(0.5) 
     
    def showhideui(self): 
        if self._move_drag:
            return 
         
        flag=(self.showintab and self.isMinimized()) or (not self.showintab and self.isHidden())
        
        if flag:
            self.show_and_enableautohide() 
        else:
            self.hide_and_disableautohide()
    def leftclicktray(self,reason):
            #鼠标左键点击
            if reason == QSystemTrayIcon.Trigger:
                self.showhideui()
                 
    def hide_and_disableautohide(self):
        self.hideshownotauto=False
        self.hide_()
    def show_and_enableautohide(self): 
        self.hideshownotauto=True 
        self.show_()
     
    def refreshtoolicon(self):

        iconstate = {'fullscreen': self.isletgamefullscreened, "muteprocess": self.processismuteed, "locktoolsbutton":
                     globalconfig['locktools'], "showraw": globalconfig['isshowrawtext'], "automodebutton": globalconfig['autorun']}
        colorstate = {"automodebutton": globalconfig['autorun'], "showraw": globalconfig['isshowrawtext'], "mousetransbutton": self.mousetransparent,
                      "locktoolsbutton": globalconfig['locktools'], "hideocrrange": self.showhidestate, "bindwindow": self.isbindedwindow, "keepontop": globalconfig['keepontop']}
        onstatecolor="#FF69B4"
         
        self._TitleLabel.setFixedHeight(globalconfig['buttonsize']*1.5*self.rate)  
        for i in range(len(self.buttons)):
            name=self.buttons[i].name
            if name in colorstate:
                color=onstatecolor if colorstate[name] else globalconfig['buttoncolor']
            else:
                color=globalconfig['buttoncolor']
            if name in iconstate:
                icon=globalconfig['toolbutton']['buttons'][name]['icon'] if iconstate[name] else globalconfig['toolbutton']['buttons'][name]['icon2']
            else:
                icon=globalconfig['toolbutton']['buttons'][name]['icon']
            self.buttons[i].setIcon(qtawesome.icon(icon,color=color))#(icon[i])
            self.buttons[i].resize(globalconfig['buttonsize']*2 *self.rate,globalconfig['buttonsize']*1.5*self.rate)
        
            if self.buttons[i].adjast:
                self.buttons[i].adjast()
            self.buttons[i].setIconSize(QSize(int(globalconfig['buttonsize']*self.rate),
                                 int(globalconfig['buttonsize']*self.rate)))
        self.showhidetoolbuttons()
        self.translate_text.movep(0,globalconfig['buttonsize']*1.5*self.rate)
        self.textAreaChanged()
        self.setMinimumHeight(globalconfig['buttonsize']*1.5*self.rate)
        self.setMinimumWidth(globalconfig['buttonsize']*2*self.rate)
    def addbuttons(self):
        functions={
            "move":None,
            "retrans":self.startTranslater,
            "automodebutton":self.changeTranslateMode,
            "setting":lambda:self.object.settin_ui.showsignal.emit(),
            "copy":lambda:pyperclip.copy( self.object.currenttext),
            "edit":lambda: self.object.edittextui.showsignal.emit(),
            "showraw":self.changeshowhideraw,
            "history":lambda: self.object.transhis.showsignal.emit() ,
            "noundict":lambda: self.object.settin_ui.button_noundict.click(),
            "fix":lambda: self.object.settin_ui.button_fix.click(),
            "langdu":self.langdu,
            "mousetransbutton":self.changemousetransparentstate,
            "locktoolsbutton":self.changetoolslockstate,
            "gamepad":lambda: dialog_savedgame(self.object.settin_ui),
            "selectgame":lambda :self.object.AttachProcessDialog.showsignal.emit(),
            "selecttext":lambda:self.object.hookselectdialog.showsignal.emit(),
            "selectocrrange":lambda :self.clickRange(False),
            "hideocrrange":self.showhide,
            "bindwindow":self.bindcropwindow_signal.emit,
            "resize":lambda :moveresizegame(self,self.object.textsource.hwnd) if self.object.textsource.hwnd else 0,
            "fullscreen":self._fullsgame,
            "muteprocess":self.muteprocessfuntion,
            "memory":lambda: dialog_memory(self.object.settin_ui,self.object.currentmd5),
            "keepontop":lambda:globalconfig.__setitem__("keepontop",not globalconfig['keepontop']) is None and self.refreshtoolicon() is None and self.setontopthread(),
            "minmize":self.hide_and_disableautohide,
            "quit":self.close
        }
        adjast={"minmize":-2,"quit":-1}
        _type={"quit":2}

        for btn in functions:
            belong=globalconfig['toolbutton']['buttons'][btn]['belong'] if 'belong' in globalconfig['toolbutton']['buttons'][btn] else None
            _adjast=adjast[btn] if btn in adjast else 0
            tp=_type[btn] if btn in _type else 1
            self.takusanbuttons(tp,functions[btn],_adjast,globalconfig['toolbutton']['buttons'][btn]['tip'],btn,belong)
               
    def hide_(self):  
        if self.showintab: 
            win32utils.ShowWindow(self.winId(),win32con.SW_SHOWMINIMIZED )
        else:
            self.hide()
    def show_(self):   
        if self.showintab:
            win32utils.ShowWindow(self.winId(),win32con.SW_SHOWNORMAL )
        else:
            self.show()
        win32utils.SetForegroundWindow(self.winId())
    def showEvent(self, a0 ) -> None: 
        if self.isfirstshow:
            self.showline(True,[None,_TR('欢迎使用')],'',1)
            
            
            showAction = QAction(_TR("&显示"), self, triggered = self.show_and_enableautohide)
            settingAction = QAction(_TR("&设置"), self, triggered = lambda: self.object.settin_ui.showsignal.emit())
            quitAction = QAction(_TR("&退出"), self, triggered = self.close)
                    
            
            self.tray.activated.connect(self.leftclicktray)

            # 创建菜单对象
            self.trayMenu = QMenu(self)
            # 将动作对象添加到菜单
            self.trayMenu.addAction(showAction)
            self.trayMenu.addAction(settingAction)
            # 增加分割线
            self.trayMenu.addSeparator()
            self.trayMenu.addAction(quitAction)
            # 将菜单栏加入到右键按钮中
            self.tray.setContextMenu(self.trayMenu) 
            self.tray.show()
            win32utils.SetForegroundWindow(self.winId())
            self.isfirstshow=False 
            self.setontopthread()
        return super().showEvent(a0)
    def setontopthread(self):
        def _():
            win32utils.SetWindowPos(int(self.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE) 
            while globalconfig['keepontop']:
                try:   
                    hwnd=win32utils.GetForegroundWindow()
                    pid=win32utils.GetWindowThreadProcessId(hwnd)[1] 
                    if pid !=os.getpid(): 
                        win32utils.SetWindowPos(int(self.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE)  
                except:
                    print_exc() 
                time.sleep(0.5)            
            win32utils.SetWindowPos(int(self.winId()), win32con.HWND_NOTOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE) 
        
        threading.Thread(target=_).start()
    def __init__(self, object):
        
        super(QUnFrameWindow, self).__init__(
            None, Qt.FramelessWindowHint|Qt.WindowMinimizeButtonHint)  # 设置为顶级窗口，无边框
        icon = QIcon()
        icon.addPixmap(QPixmap('./files/luna.jpg'), QIcon.Normal, QIcon.On)
        self.setWindowIcon(icon)
        self.tray = QSystemTrayIcon()  
        self.tray.setIcon(icon) 
        self.setWindowFlag(Qt.Tool,not globalconfig['showintab'])
        self.isfirstshow=True
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setAttribute(Qt.WA_ShowWithoutActivating,True)
        self.showintab=  globalconfig['showintab'] 
        self.setWindowTitle('LunaTranslator')
        self.hidesignal.connect(self.hide_)
        self.object = object
        self.lastrefreshtime=time.time()
        self.autohidestart=False
        threading.Thread(target=self.autohidedelaythread).start()
        self.rate = self.object.screen_scale_rate  
        self.muteprocessignal.connect(self.muteprocessfuntion) 
        self.toolbarhidedelaysignal.connect(self.toolbarhidedelay)
        
         
        self.hideshownotauto=True
        self.displaystatus.connect(self.showstatus)
        self.showhideuisignal.connect(self.showhideui)
        self.hookfollowsignal.connect(self.hookfollowsignalsolve) 
        self.displayres.connect(self.showres)
        self.displayraw1.connect(self.showraw)   
        self.refreshtooliconsignal.connect(self.refreshtoolicon)
        self.showsavegame_signal.connect(lambda:dialog_savedgame(self.object.settin_ui))  
        self.clickRange_signal.connect(self.clickRange )
        self.rangequick.connect(self.quickrange)
        self.showhide_signal.connect(self.showhide )
        self.bindcropwindow_signal.connect(functools.partial(mouseselectwindow, self.bindcropwindowcallback))
        self.grabwindowsignal.connect(self.grabwindow)
        self.quitf_signal.connect(self.close)
        self.fullsgame_signal.connect(self._fullsgame) 

        self.object = object  
        
        self.isletgamefullscreened=False
        self.fullscreenmanager=fullscreen()
        self._isTracking=False
        self.quickrangestatus=False
        self.isontop=True  
        self._TitleLabel = QLabel(self)   
        self._TitleLabel.move(0, 0)  
        self.showhidestate=False
        self.processismuteed=False
        self.mousetransparent=False
        self.isbindedwindow=False
        self.buttons=[] 
        self.showbuttons=[] 
        self.addbuttons() 
         
        d=QApplication.desktop()

        globalconfig['position'][0]=min(max(globalconfig['position'][0],0),d.width()-globalconfig['width'])
        globalconfig['position'][1]=min(max(globalconfig['position'][1],0),d.height()-globalconfig['height'])
        
        self.setGeometry( globalconfig['position'][0],globalconfig['position'][1],int(globalconfig['width'] ), int(globalconfig['height'])) 

        
        self.translate_text =  Textbrowser(self)  
         
        
        
        # 翻译框根据内容自适应大小
        self.document = self.translate_text.document()
        
        self.document.contentsChanged.connect(self.textAreaChanged)  
        self.set_color_transparency() 
        self.refreshtoolicon()
    def set_color_transparency(self ):
        self.translate_text.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']*(not self.mousetransparent)/100))
        self._TitleLabel.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                           font-weight: bold;\
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
    def grabwindow(self): 
        
        try:
            hwnd=win32utils.FindWindow('Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22',None) 
            tm=time.localtime()
            if hwnd:
                hwnd=QApplication.desktop().winId() 
                self.hide()
                QApplication.primaryScreen().grabWindow(hwnd).save(f'./cache/screenshot/{tm.tm_year}-{tm.tm_mon}-{tm.tm_mday}-{tm.tm_hour}-{tm.tm_min}-{tm.tm_sec}.png')
                self.show() 
                
            else:
                hwnd=win32utils.GetForegroundWindow()   
                if hwnd==int(self.winId()):
                    hwnd=self.object.textsource.hwnd 
                QApplication.primaryScreen().grabWindow(hwnd).save(f'./cache/screenshot/{tm.tm_year}-{tm.tm_mon}-{tm.tm_mday}-{tm.tm_hour}-{tm.tm_min}-{tm.tm_sec}.png')
                
                
        except:
            pass
    def muteprocessfuntion(self): 
        if self.object.textsource and self.object.textsource.pids :
            self.processismuteed=not self.processismuteed
            self.refreshtoolicon()
            for pid in self.object.textsource.pids:
                winsharedutils.SetProcessMute(pid,self.processismuteed)
        
    
    def _fullsgame(self): 
        if self.object.textsource and  self.object.textsource.hwnd:
            self.isletgamefullscreened=not self.isletgamefullscreened
            self.refreshtoolicon()
            self.fullscreenmanager(self.object.textsource.hwnd,self.isletgamefullscreened) 
     
    def changemousetransparentstate(self): 
        self.mousetransparent= not self.mousetransparent
        self.set_color_transparency()
        
        self.refreshtoolicon()
     
    def showhide(self): 
        if self.object.rect:
            self.showhidestate=not self.showhidestate 
            self.refreshtoolicon()
            self.object.range_ui.setVisible(self.showhidestate) 
    def bindcropwindowcallback(self,pid,hwnd): 
            _pid=os.getpid()
            self.object.textsource.hwnd= hwnd if pid!=_pid else None
            if not(globalconfig['sourcestatus']['texthook']['use'] or globalconfig['sourcestatus']['embedded']['use']):
                self.object.textsource.pids= [pid] if pid!=_pid else None
            self.isbindedwindow=(pid!=_pid)
            self.refreshtoolicon()  
    def changeshowhideraw(self):
        self.object.settin_ui.show_original_switch.click()
        
    def changeTranslateMode(self) : 
        globalconfig['autorun']=not globalconfig['autorun'] 
        self.refreshtoolicon()
    def changetoolslockstate(self): 
        globalconfig['locktools']=not globalconfig['locktools'] 
        self.refreshtoolicon()
    def textAreaChanged(self) :
        if globalconfig['fixedheight']:
            return
        if self.translate_text.cleared:
            return
        newHeight = self.document.size().height() 
        width = self.width()
        self.resize(width, newHeight + globalconfig['buttonsize']*1.5*self.rate) 
      
    def quickrange(self): 
        if self.quickrangestatus:
            self.object.screen_shot_ui.immediateendsignal.emit()
            # if globalconfig['autorun']==False:
            #     self.startTranslater()
        else:
            self.clickRange(True)
        
    def clickRange(self,auto): 
        if globalconfig['sourcestatus']['ocr']['use']==False:
                return 
        self.showhidestate=False
        
        self.quickrangestatus=not self.quickrangestatus
        self.object.range_ui.hide()
        self.object.screen_shot_ui =gui.rangeselect.rangeselct(self.object)
        self.object.screen_shot_ui.show()
        self.object.screen_shot_ui.callback=self.afterrange
        win32utils.SetFocus(self.object.screen_shot_ui.winId() )   
         
        self.object.screen_shot_ui.startauto=auto
        self.object.screen_shot_ui.clickrelease=auto
    def afterrange(self): 
        self.showhide()
        if globalconfig['showrangeafterrangeselect']==False:
            self.showhide()
        if globalconfig['ocrafterrangeselect']:
            self.startTranslater()
    def langdu(self): 
        self.object.readcurrent(force=True)
    def startTranslater(self) :
        if self.object.textsource :
            threading.Thread(target=self.object.textsource.runonce).start()
         
    def toolbarhidedelay(self):
        
        for button in self.buttons:
            button.hide()    
        self._TitleLabel.hide()
    def leaveEvent(self, QEvent) : 
        if globalconfig['locktools']:
            return 
        self.ison=False
        def __(s):
            time.sleep(0.5)
            if self.ison==False:
                s.toolbarhidedelaysignal.emit()
        threading.Thread(target=lambda:__(self) ).start()
        
    def enterEvent(self, QEvent) : 
        
        self.ison=True
 
        for button in self.buttons[-2:] +self.showbuttons:
            button.show()  
        self._TitleLabel.show()
    def resizeEvent(self, e):
        super().resizeEvent(e);
        wh=globalconfig['buttonsize'] *1.5
        height = self.height() - wh *self.rate 
         
        self.translate_text.resize(self.width(), height * self.rate)
        for button in self.buttons[-2:]:
              button.adjast( ) 
        # 自定义窗口调整大小事件
        self._TitleLabel.setFixedWidth(self.width())  

    def showhidetoolbuttons(self):
        showed=0
        self.showbuttons=[] 
        
        for i,button in enumerate(self.buttons[:-2]):
            if button.belong:
                hide=True
                for k in button.belong:
                    if globalconfig['sourcestatus'][k]['use']:
                        hide=False
                        break
                if hide:
                    button.hide()
                    continue 
            if  button.name in globalconfig['toolbutton']['buttons'] and globalconfig['toolbutton']['buttons'][button.name]['use']==False: 
                button.hide()
                continue 

            button.move(showed*button.width() , 0) 
            self.showbuttons.append(button)
            #button.show()
            showed+=1
        self.enterEvent(None)
    def callwrap(self,call,_):
            try: 
                call( )
            except:
                print_exc()
    def takusanbuttons(self, _type,clickfunc,adjast=None,tips=None,save=None,belong=None): 
         
        button=QPushButton(self) 
        if tips: 
            button.setToolTip(_TR(tips) )
         

        style='''
        QPushButton{
          background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;
      }
       
        '''
        if _type==1:
            style+='''
            QPushButton:hover{
           background-color: %s;
           border: 0px;
           font: 100 10pt;
            }'''%globalconfig['button_color_normal']
        elif _type==2:
            style+='''
             QPushButton:hover{
           background-color: %s;
           color: white;
           border: 0px;
           font: 100 10pt;
       }'''%(globalconfig['button_color_close'])
        


        button.setStyleSheet(style)
 
        
        if clickfunc:
            button.clicked.connect(functools.partial(self.callwrap,clickfunc)) 
        else:
            button.lower()
        
        button.name=save
        button.belong=belong
        if adjast<0: 
            button.adjast=lambda  :button.move(self.width() + adjast*button.width() , 0) 
        else:
            button.adjast=None
        self.buttons.append(button) 
         

    def closeEvent(self, a0 ) -> None: 
        self.object.isrunning=False
        self.tray.hide()
        self.tray = None  
        self.hide()
        globalconfig['position']=[self.pos().x(),self.pos().y()]
        
        globalconfig['width']=self.width() 
        globalconfig['height']=self.height() 
        saveallconfig() 
         
        if self.object.textsource:
            self.object.textsource=None
        if self.object.settin_ui.needupdate and globalconfig['autoupdate']: 
            update()
        endsubprocs()
        os._exit(0) 