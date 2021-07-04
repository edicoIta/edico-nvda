#Addon for EDICO Math Editor
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2021 Alberto Zanella - IRIFOR

import UIAHandler
import ui
from logHandler import log
import api
from keyboardHandler import KeyboardInputGesture
import addonHandler
import textInfos
import appModuleHandler
import controlTypes
from . import edicoObj
from . import edicoProfileSetup
from . import sharedMessages
import NVDAObjects
import winUser
import wx

addonHandler.initTranslation()

class AppModule(appModuleHandler.AppModule):
    
    CONST_INSERT_SYMBOL_WINDOW = _("Inserisci simbolo")
    CONST_GRAPHIC_VIEWER_WINDOW = _("Visualizzazione reale")
    CONST_BRAILLE_VIEWER_WINDOW = _("Visualizzazione Braille")
    
    def __init__(self, *args, **kwargs):
        super(AppModule, self).__init__(*args, **kwargs)
        if  (edicoProfileSetup.profileExists()) :
            #We update the table abs path since the user should have a portable version and the path may be different.
              edicoProfileSetup.updateTablePath()
              # pass #TODO: when braille is ok, previous line shuld be uncommented 
        else: #If a edico profile doesn't exists:
            edicoProfileSetup.createEdicoProfile()
        edicoProfileSetup.addBrailleTableToGUI()

    def terminate(self) :
        super(AppModule, self).terminate()
        #Clean-up custom braille tables
        edicoProfileSetup.removeBrailleTableToGUI()
    
    def chooseNVDAObjectOverlayClasses(self, obj, clsList):
        if self.isEdicoEditor(obj) :
            clsList.insert(0,edicoObj.EdicoEditor)
    
    def event_NVDAObject_init(self, obj):
        try :
            if obj.role == controlTypes.ROLE_PANE and obj.childCount == 2 and obj.firstChild.firstChild.role == controlTypes.ROLE_EDITABLETEXT and obj.lastChild.firstChild.role == controlTypes.ROLE_LIST and obj.name == None:
                obj.name = self.CONST_INSERT_SYMBOL_WINDOW
        except: pass
    
    def _get_statusBarTextInfo(self) :
        obj = NVDAObjects.NVDAObjectTextInfo(api.getForegroundObject(),textInfos.POSITION_ALL)
        obj.text = edicoObj.edicoApi.getApiObject().GetStatusBar()
        return obj
        
    def isEdicoEditor(self,obj) :
        return obj.windowClassName and obj.windowClassName.startswith('WindowsForms10.RichEdit20W.app.') and obj.role == controlTypes.ROLE_STATICTEXT
    
    def script_openQuckProfileWizard(self, gesture):
        wx.CallAfter(edicoProfileSetup.onQuickProfileWizardDialog, None)
    script_openQuckProfileWizard.category = "Edico"
    # Translators: Message presented in input help mode.
    script_openQuckProfileWizard.__doc__ = _("Shows a dialog to revert edico profile options to the default.")
    
    def script_altF(self,gesture) :
        KeyboardInputGesture.fromName("alt").send()
        KeyboardInputGesture.fromName("f").send()
    
    def reportWindowStatus(self,const) :
        #Get main window document
        eUIA = UIAHandler.handler.clientObject.ElementFromHandle(api.getForegroundObject().windowHandle)
        searchCondition = UIAHandler.handler.clientObject.createPropertyCondition(UIAHandler.UIA_NamePropertyId,const)
        res = eUIA.findFirst(UIAHandler.TreeScope_Descendants,searchCondition)
        if res :
            ui.message(const + " " + sharedMessages.GLB_ON)
        else :
            ui.message(const + " " + sharedMessages.GLB_OFF)
    
    __gestures = {
    'kb:nvda+alt+r': 'openQuckProfileWizard',
    'kb:alt+f': 'altF',
    }