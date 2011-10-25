
def FormSetDataEx(uideflist,paremetes):
  config = uideflist.config

  rec = uideflist.uipFilter.Dataset.AddRecord()

  # Set Default Branch Info
  UserInfo = config.SecurityContext.GetUserInfo()
  rec.BranchCode = str(UserInfo[4])
  rec.BranchName = str(UserInfo[5])
  rec.BranchId = int(UserInfo[2])
  rec.HeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')

  # Set Default Period Date
  Now = config.Now()
  rec.BeginDate = int(Now) - 1
  rec.EndDate = int(Now)


