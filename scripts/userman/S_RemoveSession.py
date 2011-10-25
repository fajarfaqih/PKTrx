import sys, os

def DAFScriptMain(config, parameter, returnpacket):
  dataset = parameter.GetDataset(0)
  record = dataset.GetRecord(0)
  session = record.data
  sessionpath = config.SecurityContext.SessionDirectory + session

  IsErr = 0
  ErrMessage = ''
  try:
    userid = config.SecurityContext.userid
    if userid == 'root':
      IsSuperUser = 1
    else:
      IsSuperUser = 0
    current_session = userid +'_'+ config.SecurityContext.sessionid

    if session == current_session:
      raise NameError, 'Cannot remove current session'

    useractive = config.CreatePObjImplProxy('UserApp')
    useractive.Key = userid

    usersession = config.CreatePObjImplProxy('UserApp')
    userid = session.split('_')
    userid = userid[0]
    usersession.Key = userid

    if IsSuperUser == 0:
      if (useractive.NoLimitLocation <> 'T') and (useractive.branch_code <> usersession.branch_code):
        raise NameError, 'Cannot remove user session from different branch'

    if os.access(sessionpath, os.F_OK) == 1:
      os.remove(sessionpath)
  except:
    IsErr = 1
    ErrMessage = str(sys.exc_info()[1])

  result_def = 'IsErr: integer; ErrMessage: string'
  record = returnpacket.CreateDataPacketStructure(result_def)
  record.IsErr = IsErr
  record.ErrMessage = 'Server side error : ' + ErrMessage
  
  return 1
