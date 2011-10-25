# ClassHelper.py

import com.ihsan.foundation.mobject as mobject 
import com.ihsan.fileutils as fileutils
import pyFlexcel
import codecs

class PrintHelper(mobject.MObject):
  
  def mobject_init(self):
    self.templateBaseDir = self.Config.HomeDir + self.Helper.GetObject('ParameterGlobal', 'TPLPATH').Get()

  def LoadTemplate(self,name):
    name = name + '.txt'
    return fileutils.GetStringFromFile(self.templateBaseDir + '\\' +  name)
    
  def LoadHtmTemplate(self,name):
    name = name + '.htm'
    return fileutils.GetStringFromFile(self.templateBaseDir + '\\' +  name)  
  
  def LoadDocTemplate(self,name):
    name = name + '.doc'
    return self.templateBaseDir + '\\' +  name

  def LoadRtfTemplate(self,name):
    name = name + '.rtf'
    #return fileutils.GetStringFromFile(self.templateBaseDir + '\\' +  name)
    fullname = self.templateBaseDir + '\\' +  name 
    return codecs.open(fullname, 'r', 'utf-8').read()
          
  def LoadExcelTemplate(self,name):
    if name.upper().find('.XLS') < 0 :
      name = name + '.xls'
      
    return pyFlexcel.Open(self.templateBaseDir + '\\' + name)
    
  def GetExcelTemplatePath(self,name):
    return self.templateBaseDir + '\\' + name
