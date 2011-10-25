
def FormSetDataEx(uideflist,parameters):

  config = uideflist.Config
  
  rec = uideflist.uipFilter.Dataset.AddRecord()
  Now = config.Now()
  rec.BeginDate = int(Now) - 30
  rec.EndDate = int(Now)
  rec.BranchCode = config.SecurityContext.GetUserInfo()[4]
  rec.UserId = config.SecurityContext.UserId
  
  
  
  
