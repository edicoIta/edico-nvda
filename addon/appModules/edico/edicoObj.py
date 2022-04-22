# -*- coding: utf-8 -*-

#Addon for EDICO Math Editor
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2022 Alberto Zanella - I.Ri.Fo.R. - https://www.irifor.eu/

import eventHandler
from . import sharedMessages as shMsg
import appModuleHandler
import re
import api
import speech
import textInfos
import NVDAObjects
import config
import addonHandler
import braille
import comHelper
from logHandler import log
import controlTypes
import watchdog
from NVDAObjects.IAccessible import IAccessible

addonHandler.initTranslation()

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
class EdicoEditor(IAccessible) :
    hasBackspaced = False
    
    #Translators: description of the calculator edit box
    CALCULATOR_EQUATION_EDIT = _("equation")
    def detectPossibleSelectionChange(self) :
        newInfo=self.makeTextInfo(textInfos.POSITION_SELECTION)
        if(len(newInfo.text) == 0) : return
        speech.speakTextSelected(edicoApi.getApiObject().GetHightLightedText())

    def _get_role(self) :
        if(self.IAccessibleObject.accDescription() == "equazione") :
            return super(EdicoEditor,self)._get_role()
        else: return controlTypes.Role.EDITABLETEXT
    
    def event_gainFocus(self):
        txt = edicoApi.getApiObject().GetHightLightedText()
        if(edicoApi.getApiObject().GetObjectTypeAndText(self.windowHandle) != None) :
            txt = edicoApi.getApiObject().GetObjectTypeAndText(self.windowHandle)
        if edicoApi.getApiObject().GetLine() != None :
            txt = txt + " " + edicoApi.getApiObject().GetLine()
        speech.speakText(txt)
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
        txt = edicoApi.getApiObject().GetChar()
        if( (txt != ' ') and (len(txt) == 1) and re.match("[^A-Za-z0-9]",txt)): 
            info = self.makeTextInfo(textInfos.POSITION_SELECTION)
            info.expand(textInfos.UNIT_CHARACTER)
            speech.speakTextInfo(info, unit=textInfos.UNIT_CHARACTER, reason=controlTypes.OutputReason.CARET)
        else: speech.speakText(txt)
        braille.handler.handleCaretMove(self)
    
    def script_caret_moveByLine(self, gesture):
        gesture.send()
        speech.speakText(edicoApi.getApiObject().GetLine())
        braille.handler.handleCaretMove(self)
    
    def script_caret_moveByWord(self,gesture):
        gesture.send()
        speech.speakText(edicoApi.getApiObject().SayWord())
        braille.handler.handleCaretMove(self)
    
    def script_reportCurrentLine(self,gesture):
        speech.speakText(edicoApi.getApiObject().GetLine())
    #Translators: this is a custom implementation of the globalCommands gesture, it doesn't support spelling.
    script_reportCurrentLine.__doc__=_("Reports the current line under the application cursor.")

    
    def script_reportCurrentSelection(self,gesture):
        speech.speakText(edicoApi.getApiObject().GetHightLightedText())
    #Translators: this is a custom implementation of the globalCommands gesture.
    script_reportCurrentSelection.__doc__=_("Announces the current selection in edit controls and documents.")	

    def script_sayAll(self, gesture):
        speech.speakText(edicoApi.getApiObject().GetAll())
    #Translators: Lambda can't read from the current caret position, the implementation of sayAll provided starts reading from the top of the document.
    script_sayAll.__doc__ = _("reads from the beginning of the document up to the end of the text.")	

    
    def script_f2(self,gesture):
        gesture.send()
        appm = self.appModule
        appm.reportWindowStatus(appm.CONST_BRAILLE_VIEWER_WINDOW)
    
    def script_f4(self,gesture):
        gesture.send()
        appm = self.appModule
        appm.reportWindowStatus(appm.CONST_GRAPHIC_VIEWER_WINDOW)
    
    __gestures = {
    'kb:f2': 'f2',
    'kb:control+upArrow': 'caret_moveByLine',
    'kb:control+downArrow': 'caret_moveByLine',
    'kb:control+pageUp': 'caret_moveByLine',
    'kb:control+pageDown': 'caret_moveByLine',
    'kb:control+k': 'reportAddedSymbol',
    'kb:control+i': 'reportAddedSymbol',
    'kb:alt+rightArrow': 'caret_moveByCharacter',
    'kb:alt+leftArrow': 'caret_moveByCharacter',
    'kb:alt+1': 'caret_moveByCharacter',
    'kb:alt+2': 'caret_moveByCharacter',
    'kb:alt+3': 'caret_moveByCharacter',
    'kb:alt+4': 'caret_moveByCharacter',
    'kb:alt+shift+1': 'caret_moveByCharacter',
    'kb:alt+shift+2': 'caret_moveByCharacter',
    'kb:alt+shift+3': 'caret_moveByCharacter',
    'kb:alt+shift+4': 'caret_moveByCharacter',
    'kb:alt+f1': 'caret_moveByCharacter',
    'kb:alt+f1': 'caret_moveByCharacter',
    'kb:alt+f2': 'caret_moveByCharacter',
    'kb:alt+f3': 'caret_moveByCharacter',
    'kb:alt+f5': 'caret_moveByCharacter',
    'kb:delete': 'caret_moveByCharacter',
    'kb:control+d': 'caret_moveByLine',
    'kb:f4': 'f4',
    "kb:delete": "caret_deleteCharacter",
    #Report selection
    'kb(desktop):NVDA+shift+upArrow': 'reportCurrentSelection',
    'kb(laptop):NVDA+shift+s': 'reportCurrentSelection',
    #Say Line
    'kb(desktop):NVDA+upArrow': 'reportCurrentLine',
    'kb(laptop):NVDA+l': 'reportCurrentLine',
    #SayAll override
    "kb(desktop):NVDA+downArrow": "sayAll",
    "kb(laptop):NVDA+a": "sayAll",
    }
