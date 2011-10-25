import sys
def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  
  config.BeginTransaction()
  try:
    
    strSQL = '\
      select * \
      from enterprise.backuppass'
    resSQL = config.CreateSQL(strSQL).RawResult
    
    while not resSQL.Eof:      
      strSQL = "update enterprise.backuppass set decode='%s' where id_user = '%s'" % (config.ModLibUtils.DecodeStr(resSQL.password),resSQL.id_user)
      config.ExecSQL(strSQL)
      resSQL.Next()

    config.Commit()
  except:
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])

  return 1