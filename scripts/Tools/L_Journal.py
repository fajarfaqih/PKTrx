import sys
import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.util.logsvrclient as lclib

# globals
gid = -1
oLogger = lclib.LogSvrClient(None, 'localhost', 2423, 'debug')

def DAFLongScriptMain(config, parameter, pid, monfilename):
    global gid, oLogger
    
    gid = pid
    helper = phelper.PObjectHelper(config)    
    oLogger.writeLog('Script mulai...')
    RegenerateJournalItem(config, helper)
    oLogger.writeLog('Script selesai!')
  
    return 1

def RegenerateJournalItem(config, helper):
  try:
    TranHelper = helper.LoadScript('Transaction.TransactionHelper')
    
    AddParam = ''
    #AddParam = " and branchcode='%s' " % config.SecurityContext.GetUserInfo()[4]
    AddParam += " and actualdate between '2011-01-01' and '2011-12-31' "
    AddParam += " and transactioncode <> 'TB' "
    #AddParam += " and amount <= 50000000 "
    #AddParam += " and authstatus = 'F' "
    AddParam += " and transactioncode = 'TI' "
    #AddParam += " and transactioncode = 'EAR' "
    #AddParam += " and transactionid in (140505, 140528)"
    #AddParam += " and isposted = 'F' "
    #AddParam += " and exists ( select 1 from transaction.transactionitem a , transaction.accounttransactionitem b \
    #                where a.transactionitemid=b.transactionitemid and b.accounttitype ='D' and b.fundentity=2 and \
    #                      b.accountno like '12101%' and a.transactionid=t.transactionid )"
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
    
    #AddParam += " and exists ( select 1 from transaction.transactionitem i where i.transactionid=t.transactionid and parameterjournalid like 'PI%')"
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
    
    stopscript = int(config.GetGlobalSetting('STOPSCRIPT'))
    while not oRes.Eof and stopscript == 0:
      oTran = helper.GetObject('Transaction', oRes.TransactionId)
      logmessage = "Proses Data ke %d dari %s data " % ( idx, TotalData)
      oLogger.writeLog(logmessage)

      logmessage = "Proses TransactionId %d No Trans %s : " % ( oRes.TransactionId, oTran.TransactionNo)
      oLogger.writeLog( logmessage)
      
      if oTran.AuthStatus == 'F' :
        config.BeginTransaction()
        try :
          logmessage = "Proses Otorisasi" 
          oLogger.writeLog( logmessage)

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
      
      oLogger.writeLog(logmessage)

      idx += 1
      oRes.Next()
      stopscript = int(config.GetGlobalSetting('STOPSCRIPT'))
    # end while

    oLogger.writeLog('PROCESS SUCCESSFULL')
  except:
    oLogger.writeLog('PROCESS ERROR')
    oLogger.writeLog('PROCESS ERROR MESSAGE : ' + str(sys.exc_info()[1]))

