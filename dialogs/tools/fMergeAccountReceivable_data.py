import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.config
  
  recData1 = uideflist.uipData1.Dataset.AddRecord()
  recData1.BranchCode = config.SecurityContext.GetUserInfo()[4]
  recData2 = uideflist.uipData2.Dataset.AddRecord()
  recData2.BranchCode = config.SecurityContext.GetUserInfo()[4]
  
def MergeAccountReceivable(config,params,returns):
  status = returns.CreateValues(
    ['IsErr',0],
    ['ErrMessage','']
  )

  config.BeginTransaction()
  try :
    param = params.FirstRecord
    
    helper = phelper.PObjectHelper(config)
    
    oSourceAR = helper.GetObject("EmployeeCashAdvance")

    config.Commit()
  except:
    config.Rollback()
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])


