import os

def DAFScriptMain(config, parameter, returnpacket):
  sessionpath = config.SecurityContext.SessionDirectory
  result_def = 'session_id: string; user_id: string; UserName: string; branch_code: string; BranchName: string'
  Record = returnpacket.CreateDataPacketStructure(result_def)
  dataset = Record.DataSet
  userobj = config.CreatePObjImplProxy('UserApp')

  sessionlist = os.listdir(sessionpath)
  i = 0
  for session in sessionlist:
    i = i + 1
    session_part = session.split('_')
    user_id = session_part[0]
    if user_id == 'root':
      if i > 1:      
        Record = dataset.AddRecord()
      Record.session_id = session
      Record.user_id = user_id
      Record.UserName = user_id
      Record.branch_code = user_id
      Record.BranchName = user_id
    else:
      try:
        userobj.Key = user_id
        cabang = userobj.LBranchLocation
        if i > 1:      
          Record = dataset.AddRecord()
        Record.session_id = session
        Record.user_id = user_id
        Record.UserName = userobj.UserName
        Record.branch_code = cabang.branch_code
        Record.BranchName = cabang.BranchName
      except:
        continue
  
  return 1
