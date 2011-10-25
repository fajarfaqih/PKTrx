import sys

def DAFScriptMain(config, parameter, returnpacket): 
  result_def = 'IsErr: integer; ErrMessage: string'
  return_record = returnpacket.CreateDataPacketStructure(result_def)
  
  IsErr = 0
  ErrMessage = ''
  config.BeginTransaction()
  try:
    lockall_sql = 'UPDATE UserApp SET login_count = 3'
    config.ExecSQL(lockall_sql)

    config.Commit()
  except:
    config.Rollback()
    IsErr = 1
    ErrMessage = str(sys.exc_info()[1])
    
  return_record.IsErr = IsErr
  return_record.ErrMessage = 'Server side error : ' + ErrMessage
  
  return 1
