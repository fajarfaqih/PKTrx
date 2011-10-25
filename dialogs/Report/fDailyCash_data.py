import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
  rec = uideflist.uipData.Dataset.AddRecord()
  BranchCode = str(uideflist.config.SecurityContext.GetUserInfo()[4])
  BranchName = str(uideflist.config.SecurityContext.GetUserInfo()[5])
  rec.BranchCode = BranchCode
  rec.BeginDate = int(uideflist.config.Now())
  rec.EndDate = rec.BeginDate
  rec.IsAllCash = 'F'
  rec.SetFieldByName('LBranch.BranchCode',BranchCode)
  rec.SetFieldByName('LBranch.BranchName',BranchName)
