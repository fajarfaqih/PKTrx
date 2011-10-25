

def FormSetDataEx(uideflist,params):
  config = uideflist.config

  recParam = uideflist.uipParam.Dataset.AddRecord()
  recParam.BranchCode = config.SecurityContext.GetUserInfo()[4]
