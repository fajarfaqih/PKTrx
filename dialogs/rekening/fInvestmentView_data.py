import com.ihsan.foundation.pobjecthelper as phelper
import sys,os
import com.ihsan.timeutils as timeutils

AUTHSTATUS = {
      'T' : 'Sudah Otorisasi',
      'F' : 'Belum Otorisasi'
      }

def FormSetDataEx(uideflist, parameter):
  config = uideflist.config
  helper = phelper.PObjectHelper(config)
  
  if (parameter.DatasetCount == 0 or
    parameter.GetDataset(0).Structure.StructureName != 'data'):
    return
    
  rec = parameter.FirstRecord

  key = 'PObj:Investment#AccountNo=%s' % rec.AccountNo
  uideflist.SetData('uipInvestment', key)

  uipInvestment = uideflist.uipInvestment.Dataset.GetRecord(0)
  Now = int(config.Now())
  uipInvestment.BeginDate = Now
  uipInvestment.EndDate = Now
  
  Obj = config.AccessPObject(key).CastToLowestDescendant()
  oInvestment = helper.GetObjectByInstance(Obj.classname,Obj)

  #oInvestment.classname
  
  uipInvestment.InvesteeName = oInvestment.GetInvesteeName()
  


def GetHistTransaction(config, params, returns):
  def AsDateTime(tdate):
    utils = config.ModLibUtils
    return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  AccountNo = rec.AccountNo
  BeginDate = int(rec.BeginDate)
  EndDate   = int(rec.EndDate)

  # Preparing returns
  Investment = helper.GetObject('Investment',AccountNo)

  BeginningBalance = Investment.GetBalanceByDate(BeginDate)

  if BeginDate == EndDate :
    PeriodStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
  else:
    PeriodStr = "%s s/d %s" % (
                   config.FormatDateTime('dd-mm-yyyy',BeginDate),
                   config.FormatDateTime('dd-mm-yyyy',EndDate)
                 )
  # end if

  recSaldo = returns.CreateValues(
          ['BeginningBalance', BeginningBalance or 0.0],
          ['PeriodStr',PeriodStr],
          ['TotalBalance',BeginningBalance or 0.0],
          ['TotalDebet', 0.0],
          ['TotalCredit', 0.0],
        )

  #--- GET HISTORI TRANSAKSI
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'TransactionCode: string',
      'MutationType: string',
      'Amount: float',
      'Debet: float',
      'Kredit: float',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'NoTransaksi:string',
      'Total:float',
      'AuthStatus:string'
    ])
  )

  s = ' \
    SELECT FROM AccountTransactionItem \
    [ \
      AccountNo = :AccountNo and \
      LTransaction.TransactionDate >= :BeginDate and \
      LTransaction.TransactionDate < :EndDate \
    ] \
    ( \
      TransactionItemId, \
      LTransaction.TransactionDate, \
      LTransaction.TransactionCode, \
      LTransaction.ActualDate, \
      MutationType, \
      Amount, \
      LTransaction.ReferenceNo, \
      LTransaction.Description, \
      LTransaction.Inputer, \
      LTransaction.TransactionNo,\
      LTransaction.AuthStatus,\
      Self \
    ) \
    THEN ORDER BY ASC TransactionDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('AccountNo', AccountNo)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate + 1)
  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(ds.ActualDate)
    recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.MutationType = ds.MutationType
    recHist.Amount = ds.Amount
    if ds.MutationType == 'D' :
      recHist.Debet = ds.Amount
      recSaldo.TotalBalance += ds.Amount
      recSaldo.TotalDebet += ds.Amount
    else:
      recHist.Kredit = ds.Amount
      recSaldo.TotalBalance -= ds.Amount
      recSaldo.TotalCredit += ds.Amount
    # endif
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description
    recHist.Inputer = ds.Inputer
    recHist.NoTransaksi = ds.TransactionNo
    recHist.AuthStatus = AUTHSTATUS[ds.AuthStatus]

    ds.Next()
  #-- while

