import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist,parameters):

  config = uideflist.Config
  
  rec = uideflist.uipFilter.Dataset.AddRecord()
  Now = config.Now()
  rec.BeginDate = int(Now) - 30
  rec.EndDate = int(Now)
  rec.BranchCode = config.SecurityContext.GetUserInfo()[4]
  rec.UserId = config.SecurityContext.UserId
  
  
def OnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  oDonorTrans = helper.GetObjectByInstance('CATransactItem', sender.ActiveInstance)

  rec.TransactionNo = oDonorTrans.LTransaction.TransactionNo
  rec.TransactionDate = oDonorTrans.LTransaction.GetAsTDateTime('TransactionDate')
  rec.Description = oDonorTrans.LTransaction.Description
  
  

  
  
  
  
