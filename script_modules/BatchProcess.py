# corporate.py

import com.ihsan.foundation.mobject as mobject
import com.ihsan.foundation.pobject as pobject
import com.ihsan.net.socketclient as socket
import os, sys
import ConfigParser
#import rpdb2

# CONSTANTS
CUSTOM_SECTION = 'CUSTOM'
CORPORATE_USER = 'system@corporate'
DEFAULT_CORPORATE_PORT = 2190

class record:
    pass

class BPHelper(mobject.MObject):
  
  def DoExecute(self,ScenarioCode,Params):
    config = self.Config
    helper = self.Helper
     
    app = config.AppObject
    app.ConCreate('BP')
    app.ConWriteln('Mulai Proses Skenario %s ' % ScenarioCode ,'BP')
      
    oBPScenario = helper.GetObjectByNames("BPScenario", {"BPScenarioCode" : ScenarioCode})  
    oBPScenario.Execute(app , Params)
  
class BPScenario(pobject.PObject):
  # static variable
  pobject_classname = 'BPScenario'
  pobject_keys = ['BPScenarioId']

  # Execute Params:
  # ProcessDate --> Execute invoke date in float  
  def Execute(self, App , Params):
    config = self.Config
    helper = self.Helper
    
    sql = "select * from BPScenarioStep where BPScenarioid=%d and IsEnabled='T' order by BPStepSequence " % self.BPScenarioId
    
    resSQL = self.Config.CreateSQL(sql).rawresult
        
    fLog = ""    
    while not resSQL.Eof :
      oBPStep = helper.GetObject('BPScenarioStep',resSQL.BPScriptId)
      if oBPStep.isnull : raise '','Step Tidak Ditemukan'
      LogMessage = 'STEP %d : %s ' % (oBPStep.BPStepSequence ,oBPStep.LBPScript.BPScriptDescription )
      App.ConWriteln(LogMessage,'BP')
                          
      oBPStep.LBPScript.DoProcess(App, Params)
      resSQL.Next()
    
class BPScenarioStep(pobject.PObject):
  # static variable
  pobject_classname = 'BPScenarioStep'
  pobject_keys = ['BPStepId']
  
class BPScript(pobject.PObject):
  # static variable
  pobject_classname = 'BPScript'
  pobject_keys = ['BPScripId']

  def GetScriptByScriptName(self):
    if self.BPScriptName in ['',None] :
      raise '','\nBatch Script Id : %d\nError : Script Name is empty' % self.BPScriptId

    ScriptName = self.BPScriptName
    return 

  def GetScriptByScriptPath(self):
    if self.BPScriptPath in ['',None] :
      raise '','\nBatch Script Id : %d\nError : Script Path is empty' % self.BPScriptId

    ScriptPath = self.BPScriptPath
    ScriptName = ScriptPath.replace('/','.').replace('\\','.')
    return ScriptName

  def DoProcess(self,App, Params):
    config = self.Config
    helper = self.Helper
    
    App.ConWriteln("== Process Script %s " % self.BPScriptDescription,"BP")

    #-- Load Script
    #oScript = helper.LoadScript(self.GetScriptByScriptName())
    oScript = helper.LoadScript(self.GetScriptByScriptPath())

    oScript.DoProcess(self.Config, App, Params)

#class BPScenario
