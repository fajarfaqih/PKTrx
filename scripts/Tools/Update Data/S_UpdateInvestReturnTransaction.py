import com.ihsan.foundation.pobjecthelper as phelper
import sys

MAPFundEntity = {'Z' : 1 , 'I' : 2, 'W' : 3}
def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  helper = phelper.PObjectHelper(config)

  app = config.GetAppObject()
  app.ConCreate('DMessage')

  logmessage = "Proses update data transaksi investasi"
  app.ConWriteln(logmessage ,'DMessage')

  config.BeginTransaction()
  try:
    s = " \
      SELECT FROM InvestmentTransactItem \
      [ LTransaction.TransactionCode = 'INVSR'] \
      ( \
        TransactionItemId, \
        Self \
      );"

    oql = config.OQLEngine.CreateOQL(s)
    oql.active = 1
    ds  = oql.rawresult
    
    row = 1
    while not ds.Eof:      

      oInvTransactItem = helper.GetObject('InvestmentTransactItem', ds.TransactionItemId)
      oTran = oInvTransactItem.LTransaction

      logmessage = "Proses Transaksi %s ( Id %d ) : " % (oTran.TransactionNo, oTran.TransactionId)
      app.ConWriteln(logmessage ,'DMessage')

      oInvestment = oInvTransactItem.LInvestment.CastToLowestDescendant()
      if oInvestment.IsA('InvestmentEmployee') :
        oTran.ReceivedFrom = oInvestment.LEmployee.EmployeeName[:100]
      else : # oInvestment.IsA('InvestmentNonEmployee') :
        oTran.ReceivedFrom = oInvestment.LInvestee.InvesteeName[:100]
      # end if

      row += 1
      ds.Next()
    # end while  

    config.Commit()
  except:
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
  # end try except  

  return 1