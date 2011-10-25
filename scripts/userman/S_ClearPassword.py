import sys

def DAFScriptMain(config, parameter, returnpacket):
  result_def = 'IsErr: integer; ErrMessage: string'
  return_record = returnpacket.CreateDataPacketStructure(result_def)
  
  IsErr = 0
  ErrMessage = ''
  try:
    dataset = parameter.GetDataset(0)
    record = dataset.GetRecord(0)
    userconst = record.data
    newpass = config.SysVarIntf.GetStringSysVar('AUTHORITY', 'DEFPASSWD')

    user = config.AccessPObject(userconst)
    user.SendChangePasswordRequest(user.user_id, newpass, newpass)

  except:
    IsErr = 1
    ErrMessage = str(sys.exc_info()[1])
    
  return_record.IsErr = IsErr
  return_record.ErrMessage = 'Server side error : ' + ErrMessage
  
  return 1
