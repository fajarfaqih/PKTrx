
def FormSetDataEx(uideflist,params):
  config = uideflist.Config
  
  recData = uideflist.uipData.Dataset.AddRecord()
  
  recData.BranchCode = config.SecurityContext.GetUserInfo()[4]
