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
    
    #Translators: Insert Symbol dialog. You can set the name of the window that appears when pressing F5, natively EDICO doesn't speak nothing. 
    CONST_INSERT_SYMBOL_WINDOW = _("Insert symbol")
    #Translators: this is the name of the Graphic viewer window obbject on the main window, you can get the correct name for your language using the navigator object.
    CONST_GRAPHIC_VIEWER_WINDOW = _("Graphic viewer")
    #Translators: this is the name of the Braille viewer window obbject on the main window, you can get the correct name for your language using the navigator object.
    CONST_BRAILLE_VIEWER_WINDOW = _("Braille viewer")
    #Translators: the Run Demo button
    runDemoButtonText = _("Run demo")
    #Translators: the Machine identifier readonly edit
    pcCodeEditText = _("Machine identifier:")
    
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
        edicoObj.edicoApi._oEdico = None
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
            if obj.role == controlTypes.ROLE_BUTTON and obj.name and "Ejecutar demo" in obj.name :
                obj.name = obj.name.replace("Ejecutar demo",self.runDemoButtonText)
            if obj.role == controlTypes.ROLE_EDITABLETEXT and controlTypes.STATE_READONLY in obj.states and obj.name and "Identificador de equipo:" in obj.name :
                obj.name = obj.name.replace("Identificador de equipo:",self.pcCodeEditText).replace("..",".")
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