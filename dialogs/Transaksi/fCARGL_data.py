

def FormSetDataEx(uideflist,parameters):
  config = uideflist.Config
  
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
