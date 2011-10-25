import sys, os

def DAFScriptMain(config, parameter, returnpacket):
  sessionpath = config.SecurityContext.SessionDirectory

  IsErr = 0
  ErrMessage = ''
  try:
    userid = config.SecurityContext.userid
    if userid == 'root':
      IsSuperUser = 1
    else:
      IsSuperUser = 0
    useractive = config.CreatePObjImplProxy('UserApp')
    useractive.Key = userid

    if IsSuperUser == 0:
      if useractive.NoLimitLocation <> 'T':
        raise NameError, 'Cannot remove all user session. Permission denied'

    x = os.listdir(sessionpath)
    current_session = config.SecurityContext.userid
    current_session = current_session +'_'+ config.SecurityContext.sessionid
    
    for i in range(len(x)):
      if x[i] <> current_session:
        process_file = sessionpath + x[i]
        if os.access(process_file, os.F_OK) == 1:
          os.remove(process_file)
  except:
    IsErr = 1
    ErrMessage = str(sys.exc_info()[1])

  result_def = 'IsErr: integer; ErrMessage: string'
  record = returnpacket.CreateDataPacketStructure(result_def)
  record.IsErr = IsErr
  record.ErrMessage = 'Server side error : ' + ErrMessage
  
  return 1
