#modul untuk mencatat history

def AddHistory(config, ObjName, LsField, ObjDest, IdChange, mode) :
  pass

def CreateHistory(config, ObjName, ObjSource, LsFieldInput, mode) :

  return 1
  
  IdChange = (config.SecurityContext.UserID, int(config.Now()),config.SecurityContext.InitIP)

  DefaultDestField = ('ChangeType','DataSourceClass','DataSourceRef',
    'DataSourceRefInteger','DataSourceType','ProcessTime','UserId','TerminalId')
  DefaultDestClass = 'HistoryOfChanges'
  paramCreateHist = {
    'Sponsor':('AddHistory(config,ObjName,LsField,ObjNameField,IdChange,mode)',1,''),
    'SENTINEL':('Function','UseDefaultClassAndField','ExtParam')
  }
  if paramCreateHist.has_key(ObjName) :
    if not paramCreateHist[ObjName][1] :
       pass
    eval(paramCreateHist[ObjName][0])
  return 1

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)


  return 1
