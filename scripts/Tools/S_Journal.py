import sys
import com.ihsan.foundation.pobjecthelper as phelper

def SyncBatchTransActualDate(config, parameters, returnpacket):
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()
  app.ConCreate('DMessage')
  helper = phelper.PObjectHelper(config)
  corporate = helper.CreateObject('Corporate')
      
  filename = corporate.GetUserHomeDir() + "/RepairActualDateLog.txt"
  try:
    fh = open(filename,'w')
    
    # Sinkronisai Tanggal Transaksi dan Tanggal Batch
    logmessage = "Proses Sinkronisasi Tanggal Transaksi dan Tanggal Batch"
    app.ConWriteln(logmessage ,'DMessage')
    fh.write(logmessage + '\n')
    
    sSQL = "\
      select b.TransactionId \
      from transaction.transactionbatch a, \
          transaction.transaction b \
      where a.batchid=b.batchid \
         and (a.inputer <> b.inputer or a.batchdate <> b.actualdate) \
         and transactioncode <> 'TB' "
         
    oRes = config.CreateSQL(sSQL).RawResult
    
    oBatchHelper = helper.CreateObject('BatchHelper')
    oRes.First()
    while not oRes.Eof:
      oTran = helper.GetObject('Transaction', oRes.TransactionId)
       
      logmessage = "Proses Transaksi %s ( Id %d ) : " % (oTran.TransactionNo, oTran.TransactionId)
      app.ConWriteln(logmessage ,'DMessage')
      fh.write(logmessage+ '\n')
      
      oBatch = oBatchHelper.GetBatchUser( oTran.LBatch.GetAsTDateTime('BatchDate'), oTran.Inputer, oTran.BranchCode)

      config.BeginTransaction()
      try:
        oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
        oTran.BatchId = oBatch.BatchId
        logmessage = 'Berhasil'
        config.Commit()  
      except :
        config.Rollback()
        status.Is_Error = 1
        status.Error_Message = str(sys.exc_info()[1])
        logmessage = 'Gagal ' + str(sys.exc_info()[1])
      # end try except
      
      app.ConWriteln(logmessage ,'DMessage')
      fh.write(logmessage + '\n')
      
      oRes.Next()
    # end while 

  finally:
    fh.close()
  
  sw = returnpacket.AddStreamWrapper()
  sw.LoadFromFile(filename)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)

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
      
      AddParam = ''
      #AddParam = " and branchcode='%s' " % config.SecurityContext.GetUserInfo()[4]
      AddParam += " and actualdate between '2011-01-01' and '2011-01-31' "
      AddParam += " and transactioncode <> 'TB' "
      #AddParam += " and transactionid in (140505, 140528)"
      #AddParam += " and isposted = 'F' "
      #AddParam += " and exists ( select 1 from transaction.transactionitem a , transaction.accounttransactionitem b \
      #                where a.transactionitemid=b.transactionitemid and b.accountno='11901.001.000' and a.transactionid=t.transactionid )"
      #AddParam = " and transactionno = 'KK-2011-221-KMD01-0000174' "
      # AddParam = " and transactionid in (select distinct c.transactionid \
      #        from accounting.journalitem a ,transaction.transaction c where \
      #        c.journalblockid = a.id_journalblock and \
      #          not exists( \
      #             select accountinstance_id from accounting.accountinstance b where a.accountinstance_id=b.accountinstance_id) ) "
      
      # AddParam += " and exists( \
      #               select 1 from \
      #                 transaction.transactionitem i , \
      #                 transaction.accounttransactionitem a, \
      #                 transaction.productaccount b, \
      #                 transaction.product c \
      #               where a.transactionitemid=i.transactionitemid \
      #                 and a.accountno = b.accountno \
      #                 and b.productid = c.productid \
      #                 and (b.productid = 125 or productcode like '122%' ) \
      #                 and t.transactionid=i.transactionid)"

      # AddParam += " and not exists( \
      #         select 1 \
      #         from accounting.journalitem a ,transaction.transaction c,transaction.transactionitem b where \
      #           c.transactionid = b.transactionid  \
      #           and c.journalblockid = a.id_journalblock  \
      #           and c.actualdate between '2011-01-01' and '2011-01-31' \
      #           and a.fl_account in ('4210101','4210102','4210103','4220101') \
      #           and b.branchcode='001' and c.transactionid=t.transactionid )"                
      
      AddParam += " and exists ( select 1 from transaction.transactionitem i where i.transactionid=t.transactionid )"
      #AddParam += " and TransactionId > 35788 "

      # Total Data
      sSQLCount = "select count(TransactionId) \
              from transaction t \
              where Transactionid is not null \
                  %s " % ( AddParam )
      
      oResCount = config.CreateSQL(sSQLCount).RawResult

      TotalData = oResCount.GetFieldValueAt(0) or 0
      
      # Get Data
      sSQL = "select TransactionId \
              from transaction t \
              where Transactionid is not null \
                  %s \
                  order by TransactionId " % (
                   AddParam )

      oRes = config.CreateSQL(sSQL).RawResult
      logProcess = ''

      idx = 1
      oRes.First()
      while not oRes.Eof:
        oTran = helper.GetObject('Transaction', oRes.TransactionId)
        logmessage = "Proses Data ke %d dari %s data " % ( idx, TotalData)

        app.ConWriteln(logmessage ,'DJournal')
        fh.write(logmessage +  '\n')

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

        idx += 1
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
      AddParam += " and actualdate between '2011-01-01' and '2011-01-10' "
      AddParam += " and isposted='F' "

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

def DeleteTransaction(config, parameters, returnpacket):
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()
  app.ConCreate('DJournal')
  helper = phelper.PObjectHelper(config)
  corporate = helper.CreateObject('Corporate')
      
  filename = corporate.GetUserHomeDir() + "DeleteTransactionLog.txt"
  
  try:
    fh = open(filename,'w')
    try:
                  
      AddParam = " TransactionId is not null "
      AddParam += " and transactioncode = 'INVC'"

      sSQL = "select TransactionId \
              from transaction \
              where %s order by TransactionId " % ( AddParam )
      
      oRes = config.CreateSQL(sSQL).RawResult
      
      oRes.First()
      while not oRes.Eof:
        oTran = helper.GetObject('Transaction', oRes.TransactionId)
        
        logmessage = "\nProses Delete TransactionId %d No Trans %s : " % ( oRes.TransactionId, oTran.TransactionNo)
        app.ConWrite(logmessage ,'DJournal')
        fh.write(logmessage)
        
        if oTran.isnull : raise '','Data Transaksi Tidak Ditemukan'
        oTran.DeleteJournal()

        config.BeginTransaction()
        try :
          oTran.Delete()
          config.Commit()
          logmessage = "Proses Hapus Transaksi Berhasil"           
        except :
          config.Rollback()
          logmessage = 'Proses Hapus Transaksi Gagal'

        app.ConWrite(logmessage ,'DJournal')
        fh.write(logmessage)

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