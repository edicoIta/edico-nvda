#Addon for EDICO Math Editor
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2021 Alberto Zanella - IRIFOR

import eventHandler
from . import sharedMessages as shMsg
import appModuleHandler
import api
import speech
import textInfos
import NVDAObjects
import config
import braille
import comHelper
from logHandler import log
import controlTypes
import watchdog
import NVDAObjects.window.edit as edit

class EdicoCOMApiProvider :
    _EdicoObjName = 'Edico.EdicoComObj'
    _oEdico = None
    def getApiObject(self) :
        if not self._oEdico : 
            oEdico = comHelper.getActiveObject(self._EdicoObjName,dynamic=True)
            if (oEdico) :
                self._oEdico = oEdico
        return self._oEdico
    
    def isEmpty(self,cnt) : return len(cnt) > 0

edicoApi = EdicoCOMApiProvider()
class EdicoEditor(edit.RichEdit20) :
    hasBackspaced = False
    
    def detectPossibleSelectionChange(self) :
        newInfo=self.makeTextInfo(textInfos.POSITION_SELECTION)
        if(len(newInfo.text) == 0) : return
        speech.speakTextSelected(edicoApi.getApiObject().GetHightLightedText())

    def _get_role(self) :
        return controlTypes.ROLE_EDITABLETEXT
    
    def event_gainFocus(self):
        txt = edicoApi.getApiObject().GetHightLightedText()
        speech.speakText(edicoApi.getApiObject().GetObjectTypeAndText(self.windowHandle)+ " "+ edicoApi.getApiObject().GetLine())
        braille.handler.handleGainFocus(self)
    
    def event_typedCharacter(self, ch):
        if self.hasBackspaced : 
            self.hasBackspaced = False
        else :    
            txt = edicoApi.getApiObject().GetBackSpace()
            if config.conf['keyboard']['speakTypedCharacters']:
                speech.speakText(txt)
        braille.handler.handleCaretMove(self)
    
    def script_caret_deleteCharacter(self,gesture):
        gesture.send()
        txt = edicoApi.getApiObject().GetChar()
        if config.conf['keyboard']['speakTypedCharacters']:
            speech.speakText(txt)
        braille.handler.handleCaretMove(self)
    
    def script_caret_backspaceCharacter(self,gesture):
        self.hasBackspaced = True
        txt = edicoApi.getApiObject().GetBackSpace()
        speech.speakText(txt)
        gesture.send()
    
    def script_reportAddedSymbol(self,gesture):
        gesture.send()
        txt = edicoApi.getApiObject().GetBackSpace()
        speech.speakText(txt)
        braille.handler.handleCaretMove(self)
    
    def script_caret_moveByCharacter(self, gesture):
        gesture.send()
        speech.speakText(edicoApi.getApiObject().GetChar())
        braille.handler.handleCaretMove(self)
    
    def script_caret_moveByLine(self, gesture):
        gesture.send()
        speech.speakText(edicoApi.getApiObject().GetLine())
        braille.handler.handleCaretMove(self)
    
    def script_caret_moveByWord(self,gesture):
        gesture.send()
        speech.speakText(edicoApi.getApiObject().SayWord())
        braille.handler.handleCaretMove(self)
    
    def script_typeCaret(self,gesture) :
        hwnd = self.windowHandle
        watchdog.cancellableSendMessage(hwnd,0x00C2,1,"^")
        self.event_typedCharacter(None)
        
    def script_f2(self,gesture):
        gesture.send()
        appm = self.appModule
        appm.reportWindowStatus(appm.CONST_BRAILLE_VIEWER_WINDOW)
    
    def script_f4(self,gesture):
        gesture.send()
        appm = self.appModule
        appm.reportWindowStatus(appm.CONST_GRAPHIC_VIEWER_WINDOW)
    
    __gestures = {
    'kb:shift+ì': 'typeCaret',
    'kb:f2': 'f2',
    'kb:control+k': 'reportAddedSymbol',
    'kb:control+i': 'reportAddedSymbol',
    'kb:control+d': 'caret_moveByLine',
    'kb:f4': 'f4',
    "kb:delete": "caret_deleteCharacter",
    }