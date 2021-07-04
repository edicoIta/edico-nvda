#Addon for EDICO Math Editor
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2021 Alberto Zanella - IRIFOR

import config
import os
import globalVars
import braille
import addonHandler
import gui
from gui import guiHelper
from gui.settingsDialogs import SettingsDialog
import wx
import brailleTables

addonHandler.initTranslation()

PROFILE_NAME = "edico"

#Translators: This string is the file name of the Lambda braille table for the translated language. The file should be present in the "brailleTables" directory in this addon. The default is the italian braille translation table.
TABLE_NAME = _("edico-ita.utb")

# Check whether the edico profile already exists
def profileExists() :
	try :
		(config.conf._getProfile(PROFILE_NAME))
		return True
	except :
		return False

'''
Creates a new profile edico.ini. By default it is of the form:

[braille]
	translationTable = table\path\tableName
	tetherTo = focus
	readByParagraph = False

'''
def createEdicoProfile() :
	config.conf.createProfile(PROFILE_NAME)
	config.conf.save()
	lp = config.conf._getProfile(PROFILE_NAME,True)
	#Creates braille config
	brlcfg = {}
	#TODO: remove translationTable = False when edico tables are ready
	setDefaultBraillevalues(brlcfg,translationTable = True)
	#Write profile
	lp["braille"] = brlcfg
	lp.write()
	#Update profile trigger
	trigs = config.conf.triggersToProfiles["app:"+PROFILE_NAME] = PROFILE_NAME
	#Update profile configs
	config.conf.saveProfileTriggers()


def setDefaultBraillevalues(brlcfg,translationTable = True,tetherTo = True,readByParagraph = True,wordWrap = True):
	if translationTable : brlcfg["translationTable"] = _getBrlTablePath(TABLE_NAME)
	if translationTable : brlcfg["inputTable"] = _getBrlTablePath(TABLE_NAME)
	if translationTable : brlcfg["expandAtCursor"] = False
	if tetherTo : brlcfg["tetherTo"] = "focus"
	if readByParagraph : brlcfg["readByParagraph"] = False
	if wordWrap : brlcfg["wordWrap"]=False

#Contains custom braille tables for edico
_edicoBrailleTables = None
def getEdicoBrailleTables() :
	global _edicoBrailleTables
	if _edicoBrailleTables == None :
		_edicoBrailleTables = tuple((_getBrlTablePath(file),file,False,) for file in os.listdir(_getBrlTablesDir()) if os.path.isfile(os.path.join(_getBrlTablesDir(), file)) and file.startswith("edico-"))
	return _edicoBrailleTables

# Adds the braille table to the list in braille settings dialog
def addBrailleTableToGUI():
	#Retrieves all tables in addon directory with prefix 'edico-' and adds them to the global collection
	for table in getEdicoBrailleTables() :
			brailleTables.addTable(table[0],table[1],False,True,True)	


# Removes the braille table to the list in braille settings dialog
def removeBrailleTableToGUI():
	for table in getEdicoBrailleTables() :
		brailleTables._tables.pop(table[0])

	
# Retrieves the current absolute path for the braille table and updates the profile entry (useful for portable NVDA)
def updateTablePath() :
	lp = config.conf._getProfile(PROFILE_NAME,True)
	#If a system table has been selected, do not force the abspath
	if "edico-" not in lp["braille"]["translationTable"] : return
	basepath = _getBrlTablesDir()
	tablename = os.path.basename(lp["braille"]["translationTable"])
	if basepath not in lp["braille"]["translationTable"]: #Directory has been moved
		lp["braille"]["translationTable"] = _getBrlTablePath(tablename)
		lp["braille"]["inputTable"] = _getBrlTablePath(tablename)
		lp.write()

# Gets the absolute path of the braille table in tableName
def _getBrlTablePath(tableName) :
	return os.path.join(_getBrlTablesDir(),tableName)
	
#Get the absolute path to the brailleTables directory
def _getBrlTablesDir() :
	return os.path.abspath(os.path.join(globalVars.appArgs.configPath, "addons", "edico", "appModules",PROFILE_NAME,"brailleTables"))


def onQuickProfileWizardDialog(evt) :
	gui.mainFrame._popupSettingsDialog(QuickProfileWizardDialog)

class QuickProfileWizardDialog(SettingsDialog):
	# Translators: This is the label for the Quick Profile Wizard dialog.
	# This dialog helps the user to reset relevant profile options without deleting his custom settings.
	title = _("Revert EDICO Profile Wizard")

	def makeSettings(self, settingsSizer):
		sHelper=guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the static text of the Quick Profile Wizard dialog.
		msgIntro=_("Choose which options you want to reset to the default value for the EDICO profile")
		self.introStxt=sHelper.addItem(wx.StaticText(self,label=msgIntro))
		# Translators: This is the label for a checkbox in the
		# Quick Profile Wizard dialog.
		self.defaultTranslationTableCheckBox=sHelper.addItem(wx.CheckBox(self,label=_("Keep the EDICO braille table for the current language (%s)") % TABLE_NAME))
		self.defaultTranslationTableCheckBox.SetValue(True)
		# Translators: This is the label for a checkbox in the
		# Quick Profile Wizard dialog.
		self.brailleTetherToFocusCheckBox=sHelper.addItem(wx.CheckBox(self,label=_("Set the braille cursor to tether the focus")))
		self.brailleTetherToFocusCheckBox.SetValue(True)
		# Translators: This is the label for a checkbox in the
		# Quick Profile Wizard dialog.
		self.disableReadByParagraphCheckBox=sHelper.addItem(wx.CheckBox(self,label=_("Disable the Braille reading by paragraph")))
		self.disableReadByParagraphCheckBox.SetValue(True)
		# Translators: This is the label for a checkbox in the
		# Quick Profile Wizard dialog.
		self.disableBrailleWordWrapCheckBox=sHelper.addItem(wx.CheckBox(self,label=_("Disable word wrappping of the braille line")))
		self.disableBrailleWordWrapCheckBox.SetValue(True)

	def postInit(self):
		self.defaultTranslationTableCheckBox.SetFocus()

	def onOk(self,evt):
		lp = config.conf._getProfile(PROFILE_NAME,True)
		brlcfg = lp["braille"]
		setDefaultBraillevalues(brlcfg,self.defaultTranslationTableCheckBox.IsChecked(),self.brailleTetherToFocusCheckBox.IsChecked(),self.disableReadByParagraphCheckBox.IsChecked(),self.disableBrailleWordWrapCheckBox.IsChecked())
		lp.write()
		super(QuickProfileWizardDialog, self).onOk(evt)
