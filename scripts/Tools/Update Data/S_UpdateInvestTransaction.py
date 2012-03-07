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
  corporate = helper.CreateObject('Corporate')

  filename = corporate.GetUserHomeDir() + "/RepairActualDateLog.txt"
  try :
    fh = open(filename,'w')

    logmessage = "Proses update data transaksi investasi"
    config.SendDebugMsg(logmessage)
    app.ConWriteln(logmessage ,'DMessage')
    fh.write(logmessage + '\n')

    
    s = " \
      SELECT FROM InvestmentTransactItem \
      [ LTransaction.TransactionCode = 'INVS'] \
      ( \
        TransactionItemId, \
        Self \
      );"

    oql = config.OQLEngine.CreateOQL(s)
    oql.active = 1
    ds  = oql.rawresult
    
    row = 1
    while not ds.Eof:      
      config.BeginTransaction()
      try:

        oInvTransactItem = helper.GetObject('InvestmentTransactItem', ds.TransactionItemId)
        oTran = oInvTransactItem.LTransaction

        logmessage = "Proses Transaksi %s ( Id %d ) : " % (oTran.TransactionNo, oTran.TransactionId)
        app.ConWriteln(logmessage ,'DMessage')
        config.SendDebugMsg(logmessage)
        fh.write(logmessage + '\n')

        oInvestment = oInvTransactItem.LInvestment.CastToLowestDescendant()
        if oInvestment.IsA('InvestmentEmployee') :
          if oInvestment.EmployeeId in [0,None] :
            raise '','Id Employee tidak ditemukan'
          oTran.PaidTo = oInvestment.LEmployee.EmployeeName[:100]
        else : # oInvestment.IsA('InvestmentNonEmployee') :
          oTran.PaidTo = oInvestment.LInvestee.InvesteeName[:100]
        # end if
        logmessage = "Berhasil"

        config.Commit()
      except:
        config.Rollback()
        status.Is_Error = 1
        status.Error_Message = str(sys.exc_info()[1])
        logmessage = "Gagal Id User : %s , %s" % (  oTran.Inputer, str(sys.exc_info()[1]))

      # end try except
      app.ConWriteln(logmessage ,'DMessage')
      fh.write(logmessage + '\n')  

      row += 1
      ds.Next()
    # end while  
  
  finally:
    fh.close()
  
  sw = returnpacket.AddStreamWrapper()
  sw.LoadFromFile(filename)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)

  return 1