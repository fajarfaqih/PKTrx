import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
  rec = uideflist.uipData.Dataset.AddRecord()
  BranchCode = str(uideflist.config.SecurityContext.GetUserInfo()[4])
  BranchName = str(uideflist.config.SecurityContext.GetUserInfo()[5])
  rec.BranchCode = BranchCode
  rec.BeginDate = int(uideflist.config.Now())-1
  rec.EndDate = int(uideflist.config.Now())
  rec.SetFieldByName('LBranch.BranchCode',BranchCode)
  rec.SetFieldByName('LBranch.BranchName',BranchName)

