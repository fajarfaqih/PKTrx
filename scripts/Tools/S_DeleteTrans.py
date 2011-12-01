import sys
import com.ihsan.foundation.pobjecthelper as phelper

def DAFScriptMain(config,parameters,returnpacket):
  app = config.AppObject
  helper = phelper.PObjectHelper(config)
  status = returnpacket.CreateValues(
      ['Is_Error',0],
      ['Error_Message','']
  )
  config.BeginTransaction()
  try:
    oTran = helper.GetObjectByNames('Transaction',{'TransactionNo' : 'BB-CB-001'})
    oTran.Delete()
    config.Commit()    
  except :
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
