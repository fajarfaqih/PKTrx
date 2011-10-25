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
  else:
    rec = parameter.FirstRecord
    batchId = rec.BatchId
    beginNo = rec.BeginNo

    res = config.CreateSQL("\
      select * from transaction \
      where transactioncode='SD001'
      and donor\
      order by transactionid\
    " % batchId).rawresult

    uipTransaction = uideflist.uipTransaction.Dataset
    rownum = 0
    showcount = 0

    while not res.Eof and showcount < LIMIT_TRANSAKSI:
      rownum += 1
      if rownum >= beginNo:
        showcount += 1

        oTran = uipTransaction.AddRecord()
        transactionId = res.TransactionId
        oTran.SetFieldAt(0, 'PObj:Transaction#TransactionId=%d' % transactionId)
        oTran.Nomor = rownum
        oTran.TransactionId = transactionId
        oTran.TransactionTime = timeutils.AsTDateTime(config, res.TransactionTime)
        oTran.Inputer = res.Inputer
        oTran.Description = res.Description
        oTran.ReferenceNo = res.ReferenceNo
        oTran.TransactionCode = res.TransactionCode
        oTran.Proses = 'N'

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

          resDetil.Next()
          detilnum += 1
        #-- while
      #-- if

      res.Next()
    #-- while
  #-- if.else

