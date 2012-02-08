import sys
import com.ihsan.foundation.pobjecthelper as phelper

def RegenerateJournal(config, parameters, returnpacket):
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()
  app.ConCreate('DJournal')
  helper = phelper.PObjectHelper(config)
  corporate = helper.CreateObject('Corporate')
      
  filename = corporate.GetUserHomeDir() + "/GenerateJournalLog.txt"
  try:
    fh = open(filename,'w')
    
    # Posting Journal
    config.BeginTransaction()
    try :
      logmessage = "Proses Batch Transaksi (Journal) "
      app.ConWriteln(logmessage ,'DJournal')
      fh.write(logmessage + '\n')
      
      sSQL = "\
         select BatchId \
         from transactionbatch \
         where IsPosted='T' \
           and BatchDate >= '2011-01-01' \
           and BatchDate <= '2011-01-31'"
           
      oRes = config.CreateSQL(sSQL).RawResult
      
      oRes.First()
      while not oRes.Eof:
        oBatch = helper.GetObject('TransactionBatch', oRes.BatchId)
         
        logmessage = "Proses Batch %s ( Id %d ) : " % (oBatch.BatchNo, oRes.BatchId)
        app.ConWriteln(logmessage ,'DJournal')
        fh.write(logmessage+ '\n')

        try:
          oBatch.PostToAccounting()
          if oBatch.IsPosted == 'T' :
            logmessage = 'Berhasil'    
        except :
          logmessage = 'Gagal ' + str(sys.exc_info()[1])
        # end try except
        
        app.ConWriteln(logmessage ,'DJournal')
        fh.write(logmessage + '\n')
        
        oRes.Next()
      # end while 
      
      config.Commit()
    except:
      config.Rollback()
      status.Is_Error = 1
      status.Error_Message = str(sys.exc_info()[1])
    # end try except
  finally:
    fh.close()
  
  sw = returnpacket.AddStreamWrapper()
  sw.LoadFromFile(filename)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)

def RegenerateJournalItem(config, parameters, returnpacket):
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()
  app.ConCreate('DJournal')
  helper = phelper.PObjectHelper(config)
  corporate = helper.CreateObject('Corporate')
      
  filename = corporate.GetUserHomeDir() + "GenerateJournalItemLog.txt"
  
  try:
    fh = open(filename,'w')
    try:
      TranHelper = helper.LoadScript('Transaction.TransactionHelper')
      
      AddParam = " and branchcode='%s' "
      AddParam = " and actualdate between '2011-01-01' and '2011-01-31' "      

      sSQL = "select TransactionId \
              from transaction \
              where Transactionid is not null \
                  %s \
                  order by TransactionId " % ( 
                   config.SecurityContext.GetUserInfo()[4],
                   AddParam )

      oRes = config.CreateSQL(sSQL).RawResult
      logProcess = ''
      oRes.First()
      while not oRes.Eof:
        oTran = helper.GetObject('Transaction', oRes.TransactionId)
        logmessage = "Proses TransactionId %d No Trans %s : " % ( oRes.TransactionId, oTran.TransactionNo)

        app.ConWrite(logmessage ,'DJournal')
        fh.write(logmessage)
        
        if oTran.AuthStatus == 'F' :
          config.BeginTransaction()
          try :
            logmessage = "Proses Otorisasi" 
            app.ConWrite(logmessage ,'DJournal')
            fh.write(logmessage)

            oTran.AutoApproval()
            config.Commit()
          except :
            config.Rollback()
            logmessage = 'Gagal Otorisasi'

        if oTran.AuthStatus == 'T' :
          st, errmsg = oTran.CreateJournal()
          if st == 2 :
            logmessage = 'Gagal ' + errmsg 
          else:
            logmessage = 'Berhasil'
          # end if else
        # end if  
        
        app.ConWriteln(logmessage ,'DJournal')
        fh.write(logmessage + '\n')
        logProcess += logmessage + '\n'

        oRes.Next()
      # end while

    except:
      status.Is_Error = 1
      status.Error_Message = str(sys.exc_info()[1])
  
  finally:
    fh.close()
  
  sw = returnpacket.AddStreamWrapper()
  sw.LoadFromFile(filename)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)

def GenerateJournalItem(config, parameters, returnpacket):
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()
  app.ConCreate('DJournal')
  helper = phelper.PObjectHelper(config)
  corporate = helper.CreateObject('Corporate')
      
  filename = corporate.GetUserHomeDir() + "GenerateJournalItemLog.txt"
  
  try:
    fh = open(filename,'w')
    try:
      TranHelper = helper.LoadScript('Transaction.TransactionHelper')
      
      AddParam = " TransactionId is not null "
      #AddParam += " and branchcode='%s' " % config.SecurityContext.GetUserInfo()[4]
      AddParam += " and actualdate between '2011-01-01' and '2011-01-31' "

      sSQL = "select TransactionId \
              from transaction \
              where %s order by TransactionId " % ( AddParam )

      oRes = config.CreateSQL(sSQL).RawResult
      logProcess = ''
      oRes.First()
      while not oRes.Eof:
        oTran = helper.GetObject('Transaction', oRes.TransactionId)
        logmessage = "Proses TransactionId %d No Trans %s : " % ( oRes.TransactionId, oTran.TransactionNo)

        app.ConWrite(logmessage ,'DJournal')
        fh.write(logmessage)
        
        if oTran.AuthStatus == 'F' :
          config.BeginTransaction()
          try :
            logmessage = "Proses Otorisasi" 
            app.ConWrite(logmessage ,'DJournal')
            fh.write(logmessage)

            oTran.AutoApproval()
            config.Commit()
          except :
            config.Rollback()
            logmessage = 'Gagal Otorisasi'

        if oTran.AuthStatus == 'T' :
          st, errmsg = oTran.CreateJournal()
          if st == 2 :
            logmessage = 'Gagal ' + errmsg 
          else:
            logmessage = 'Berhasil'
          # end if else
        # end if  
        
        app.ConWriteln(logmessage ,'DJournal')
        fh.write(logmessage + '\n')
        logProcess += logmessage + '\n'

        oRes.Next()
      # end while

    except:
      status.Is_Error = 1
      status.Error_Message = str(sys.exc_info()[1])
  
  finally:
    fh.close()
  
  sw = returnpacket.AddStreamWrapper()
  sw.LoadFromFile(filename)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)
    
def GenerateAll(config, parameters, returnpacket):
  status = returnpacket.CreateValues(["Is_Err", 0], ["Err_Message", ""])
  app = config.GetAppObject()
  app.ConCreate('DJournal')
  helper = phelper.PObjectHelper(config)
  corporate = helper.CreateObject('Corporate')
      
  filename = corporate.GetUserHomeDir() + "GenerateJournalLog.txt"
  
  try:
    fh = open(filename,'w')
    try:
                  
      sSQL = "select TransactionId \
              from transaction \
              where branchcode='%s' \
                  and AuthStatus='T' \
                  and IsPosted='F' " % config.SecurityContext.GetUserInfo()[4]
      
      oRes = config.CreateSQL(sSQL).RawResult
      
      oRes.First()
      while not oRes.Eof:
        logmessage = "Proses TransactionId %d : " % oRes.TransactionId
        app.ConWrite(logmessage ,'DJournal')
        fh.write(logmessage)
        
        oTran = helper.GetObject('Transaction', oRes.TransactionId)
        st, errmsg = oTran.CreateJournal()
        if st == 2 :
          logmessage = 'Gagal ' + errmsg 
        else:
          logmessage = 'Berhasil'
        # end if
        
        app.ConWriteln(logmessage ,'DJournal')
        fh.write(logmessage + '\n')

        oRes.Next()
      # end while
                
    except:
      status.Is_Err = 1
      status.Err_Message = str(sys.exc_info()[1])
  
  finally:
    fh.close()  
  
  sw = returnpacket.AddStreamWrapper()
  sw.LoadFromFile(filename)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)        
