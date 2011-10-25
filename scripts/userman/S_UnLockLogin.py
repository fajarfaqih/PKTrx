import sys

def DAFScriptMain(config, parameter, returnpacket): 
  result_def = 'IsErr: integer; ErrMessage: string'
  return_record = returnpacket.CreateDataPacketStructure(result_def)
  
  IsErr = 0
  ErrMessage = ''
  config.BeginTransaction()
  try:
    dataset = parameter.GetDataset(0)
    record = dataset.GetRecord(0)
    userconst = record.data

    user = config.AccessPObject(userconst)
    user.UnLockLogin()
    config.Commit()
  except:
    config.Rollback()
    IsErr = 1
    ErrMessage = str(sys.exc_info()[1])
    
  return_record.IsErr = IsErr
  return_record.ErrMessage = 'Server side error : ' + ErrMessage
  
  return 1
