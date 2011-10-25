
def FormSetDataEx(uideflist,paremetes):
  rec = uideflist.uipFilter.Dataset.AddRecord()
  rec.BranchCode = str(uideflist.config.SecurityContext.GetUserInfo()[4])
  rec.BeginDate = int(uideflist.config.Now()) - 1
  rec.EndDate = int(uideflist.config.Now())

  
  
