import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.BranchCode = str(uideflist.config.SecurityContext.GetUserInfo()[4])
  rec.BeginDate = int(uideflist.config.Now()) - 1
  rec.EndDate = int(uideflist.config.Now())
  rec.IsAllProduct = 'T'
