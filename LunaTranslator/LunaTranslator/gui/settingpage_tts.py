import functools 

from PyQt5.QtWidgets import   QComboBox 
from gui.inputdialog import getsomepath1
from utils.config import globalconfig    
import os,functools
def setTab5_direct(self) :  
    self.voicecombo=QComboBox( ) 
    self.voicelistsignal.connect(functools.partial(showvoicelist,self ))
    self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self,x))

def setTab5(self) : 
    self.tabadd_lazy(self.tab_widget, ('语音合成'), lambda :setTab5lz(self)) 


def getttsgrid(self) :
        
          
        grids=[ ] 
        i=0
        lendict=len(list(globalconfig['reader'].keys()))
         
        self.ocrswitchs={}
        line=[]
        for name in globalconfig['reader']:
              
            _f=f'./LunaTranslator/tts/{name}.py'
            if os.path.exists(_f)==False:  
                continue 
            
            line+=[((globalconfig['reader'][name]['name']),6),(self.getsimpleswitch(globalconfig['reader'][name],'use',name=name,callback=functools.partial(self.yuitsu_switch,'reader','readerswitchs',name,self.object.startreader),pair='readerswitchs'),1), ] 
            if i%3==2  :
                grids.append(line) 
                line=[]
            else:
                line+=['']
            i+=1
        if len(line):
             grids.append(line) 
        return grids
       
        
def setTab5lz(self) :
         
        grids=getttsgrid(self)
        grids+=[ 
                [''],
                [("选择声音",3),(self.voicecombo,12)],
                [('语速:(-10~10)',3),(self.getspinbox(-10,10,globalconfig['ttscommon'],'rate'  ),2)],
                [('音量:(0~100)',3),(self.getspinbox(0,100,globalconfig['ttscommon'],'volume' ),2)],
                [ ('自动朗读',3),(self.getsimpleswitch(globalconfig,'autoread' ),1)],
                
        ]  
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        return gridlayoutwidget 
 
def changevoice(self,text):
    globalconfig['reader'][self.object.reader_usevoice]['voice']=text
def showvoicelist(self,vl,idx):
    self.voicecombo.blockSignals(True)
    self.voicecombo.clear()
    self.voicecombo.addItems(vl)
    if idx>=0:
        self.voicecombo.setCurrentIndex(idx)
    self.voicecombo.blockSignals(False) 