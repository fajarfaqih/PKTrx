import com.ihsan.foundation.pobjecthelper as phelper
import sys
#import com.ihsan.util.logsvrclient as lclib
import com.ihsan.timeutils as timeutils
import simplejson

# GLOBALS
LIMIT_TRANSAKSI = 10
LIMIT_DETIL     = 10

#oLogger = lclib.LogSvrClient(None, 'localhost', 2423, 'dafapp')

def FormSetDataEx(uideflist, parameter):
  config = uideflist.config
  uip = uideflist.uipData
  helper = phelper.PObjectHelper(config)

  if parameter.DatasetCount == 0 or parameter.GetDataset(0).Structure.StructureName != 'data':
    rec = uip.Dataset.AddRecord()

    rec.Today = int(config.Now())
    rec.BranchCode = config.SecurityContext.GetUserInfo()[4]
    rec.BeginDate = rec.Today
    rec.EndDate = rec.Today
  else:
    rec = parameter.FirstRecord
    #batchId = rec.BatchId
    #beginNo = rec.BeginNo
    BeginDate = rec.BeginDate
    EndDate = rec.EndDate
    LIMIT_TRANSAKSI = rec.TransactionNumber
    TransactionCode = rec.TransactionCode
    IsAllTransactionType = rec.IsAllTransactionType
    BranchCode = config.SecurityContext.GetUserInfo()[4]
    SearchText = rec.SearchText
    SearchCategory = rec.SearchCategory

#    oBatch = helper.GetObjectByNames('TransactionBatch',
#        { 'Inputer' : Inputer,
#          'BatchDate' : BeginDate,
#        })

#    if oBatch.isnull :
#      raise '','Tidak ada transaksi untuk user %s pada tanggal %s' % (Inputer,config.FormatDateTime('dd-mm-yyyy', BeginDate))

    #uipData = uideflist.uipData.Dataset.GetRecord(0)
    #uipData.BatchNo = oBatch.BatchNo
    #batchId = oBatch.BatchId
    AddParam = ''
    if IsAllTransactionType == 'F' :
      AddParam += " and TransactionCode = '%s' " % TransactionCode
    #end if
    
    if SearchCategory != 0 :
      SearchCategoryList = {
        1 : 'TransactionNo',
        2 : 'Description',
      }
      AddParam += " and upper(%s) LIKE '%%%s%%' " % (SearchCategoryList[SearchCategory],SearchText.upper())
    
    res = config.CreateSQL("\
      select * from transaction a \
      where authstatus = 'F'\
      %s \
      and exists ( \
         select 1 from transactionbatch b \
         where a.batchid=b.batchid \
           and b.branchcode = '%s' \
           and b.batchdate >= '%s' \
           and b.batchdate <= '%s' )\
      order by actualdate,transactionid \
      limit %d \
     " % (
       AddParam,
       BranchCode,
       config.FormatDateTime('yyyy-mm-dd', BeginDate),
       config.FormatDateTime('yyyy-mm-dd', EndDate),
       LIMIT_TRANSAKSI)).rawresult

    if res.Eof:
      raise '','Tidak ada transaksi pada tanggal %s s.d. %s' % (
            config.FormatDateTime('dd-mm-yyyy', BeginDate),
            config.FormatDateTime('dd-mm-yyyy', EndDate)
      )
      
    uipTransaction = uideflist.uipTransaction.Dataset
    rownum = 0
    showcount = 0

    while not res.Eof : #and showcount < LIMIT_TRANSAKSI:
      rownum += 1

      oTran = uipTransaction.AddRecord()
      transactionId = res.TransactionId
      oTran.SetFieldAt(0, 'PObj:Transaction#TransactionId=%d' % transactionId)
      oTran.Nomor = rownum
      oTran.TransactionId = transactionId
      oTran.TransactionNo = res.TransactionNo
      oTran.TransactionTime = timeutils.AsTDateTime(config, res.TransactionTime)
      oTran.TransactionDate = timeutils.AsTDateTime(config, res.ActualDate)
      oTran.Inputer = res.Inputer
      oTran.Description = res.Description
      oTran.ReferenceNo = res.ReferenceNo
      oTran.TransactionCode = res.TransactionCode
      oTran.Proses = 'N'
      oTran.DonorNo = res.DonorNo
      oTran.DonorName = res.DonorName

      # get detil
      resDetil = config.CreateSQL("\
        select * from transactionitem \
        where transactionid = %d \
      " % transactionId).rawresult

      detilnum = 0
      while not resDetil.Eof and detilnum < LIMIT_DETIL:
        oDetil = oTran.uipTransactionItem.AddRecord()
        itemId = resDetil.TransactionItemId
        oDetil.SetFieldAt(0, 'PObj:TransactionItem#TransactionItemId=%d' % itemId)
        oDetil.TransactionItemId = itemId
        oDetil.RefAccountNo = resDetil.RefAccountNo
        oDetil.RefAccountName = resDetil.RefAccountName
        oDetil.CurrencyCode = resDetil.CurrencyCode
        oDetil.MutationType = resDetil.MutationType
        oDetil.Amount = resDetil.Amount
        oDetil.Rate = resDetil.Rate
        oDetil.ParameterJournalId = resDetil.ParameterJournalId

        resDetil.Next()
        detilnum += 1
      #-- while

      res.Next()
    #-- while
  #-- if.else

def ProsesOtorisasi(config, params, returns):
  helper = phelper.PObjectHelper(config)
  data = params.FirstRecord
  tranList = eval(data.TransactionList)
  app = config.AppObject
  app.ConCreate('OTO')
  
  status = returns.CreateValues(
    ["Is_Err",0],
    ["Err_Message",""],
    ["Is_Process",0],
    ["Jurnal_Status",'F'],
    ["FileLogJournal",'']
  )

  # PROSES OTORISASI TRANSAKSI
  config.BeginTransaction()
  try :
    app.ConWriteln('Mulai Proses Otorisasi','OTO')
    #batchNo = data.BatchNo
    lsTransaksi = []
    for tranId in tranList.keys():
      aProses = tranList[tranId]
      oTran = helper.GetObject('Transaction', tranId)
      status.Is_Process = (aProses in ['O','B'])
      if aProses == 'O':
        app.ConWriteln('Proses Otorisasi Transaksi No : %s' % oTran.TransactionNo,'OTO')
        oTran.Approval()
        lsTransaksi.append(oTran)
      elif aProses == 'B':
        app.ConWriteln('Proses Batalkan Transaksi No : %s' % oTran.TransactionNo,'OTO')
        oTran.Reject()
        oTran.Delete()
      #--if.elif
    #-- for
          
    status.Jurnal_Status = 'F'

    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  #-- try.except

  # PROSES JURNAL TRANSAKSI
  if (len(lsTransaksi) > 0 ) and (status.Is_Err == 0):
    app.ConWriteln('Mulai Proses Jurnal ','OTO')
    logJournal = ""
    for oTran in lsTransaksi :
      app.ConWrite('Proses Jurnal Transaksi No : %s' % oTran.TransactionNo,'OTO')
      stJournal,msg = oTran.CreateJournal()
      if stJournal == 2:
        logJournal += "%s (Gagal Jurnal) -- %s \n" % (oTran.TransactionNo,msg)
        app.ConWriteln(' Gagal -- %s' % msg,'OTO')
      else :
        app.ConWriteln(' Sukses','OTO')
      # end if else
    # end for

    if len(logJournal) > 0:
      sBaseFileName = "logJournal.txt"
      corporate = helper.CreateObject('Corporate')
      sPathFileName = corporate.GetUserHomeDir() + "\\" + sBaseFileName
      oFile = open(sPathFileName,'w')
      try:
        oFile.write(logJournal)
      finally:
        oFile.close()
      # end try finally

      sw = returns.AddStreamWrapper()
      sw.Name = 'LogJournal'
      sw.LoadFromFile(sPathFileName)
      sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(sPathFileName)

      status.Is_Err = 2
      status.FileLogJournal = sw.Name

    else:
      status.Jurnal_Status = 'T'
    #end if
  #end if
  
  return
  
  if (len(lsTransaksi) > 0 ) and (status.Is_Err == 0):
    try:
      listBlock = []
      for oTran in lsTransaksi :
        oJD = oTran.CreateJournalData()
        listBlock = listBlock + oJD.listBlock
      #-- for

      dMsg = {'trx_code': 'CreateJournalItem', 'journal_no': batchNo, 'edit_mode' : 0 ,  'list_block': listBlock}
      sMsg = simplejson.dumps(dMsg)
        
      app = config.AppObject
      acc_host = helper.GetObject('ParameterGlobal', 'GLSVCHST').Get()
      acc_port = helper.GetObject('ParameterGlobal', 'GLSVCPRT').GetInt()
      conn = app.UseCachedTCPConn(acc_host, acc_port)
      try:
        conn.SendSTXETXMessage(sMsg)
        resp = simplejson.loads(conn.ReadSTXETXMessage())
      finally:
        app.ReleaseCachedTCPConn(conn, 1)
      #-- try.finally
      
    except:
      status.Is_Err = 2
      status.Err_Message = str(sys.exc_info()[1])
    #-- try.except

    if status.Is_Err == 0:
      config.BeginTransaction()
      try:
        if resp['status'] == 0:
          raise 'journal', resp['errMsg']
        elif resp['status'] == 1:
          for oTran in lsTransaksi :
            oTran.IsPosted = 'T'
            oTran.JournalBlockId = resp['list_block'][str(oTran.TransactionId)]
          #-- for
          
          status.Jurnal_Status = 'T'
        else:
          raise 'journal', 'undetermine status'
        #-- if.elif.else

        config.Commit()
      except:
        config.Rollback()
        status.Is_Err = 2
        status.Err_Message = str(sys.exc_info()[1])
      #-- try.except
    #-- if
  #-- if

