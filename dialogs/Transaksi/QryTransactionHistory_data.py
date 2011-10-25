
def FormSetDataEx(uideflist,parameters):

  config = uideflist.Config

  rec = uideflist.uipFilter.Dataset.AddRecord()
  
  rec.BeginDate = int(config.Now())
  rec.EndDate = int(config.Now())
  rec.BranchCode = config.SecurityContext.GetUserInfo()[4]
  rec.UserId = config.SecurityContext.UserId
  
  
  
  
