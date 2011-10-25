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

  oCATrans = helper.GetObjectByInstance('CATransactItem', sender.ActiveInstance)

  rec.TransactionNo = oCATrans.LTransaction.TransactionNo
  rec.TransactionDate = oCATrans.LTransaction.GetAsTDateTime('TransactionDate')
  rec.Description = oCATrans.LTransaction.Description
  
  oCAReturnInfo = helper.GetObjectByNames('CashAdvanceReturnInfo',
       {'SourceTransactionId' : oCATrans.LTransaction.TransactionId}
    )
    
  if oCAReturnInfo.isnull :
    rec.ReturnStatus = 'F'
  else :
    rec.ReturnStatus = 'T'
  

  
  
  
  
