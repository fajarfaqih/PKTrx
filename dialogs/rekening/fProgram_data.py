import com.ihsan.foundation.pobjecthelper as phelper
import simplejson
import sys

def FormSetDataEx(uideflist, params) :
  config = uideflist.config

  rec = uideflist.uipProductAccount.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.BeginDate = (config.Now())
  rec.EndDate = rec.BeginDate
  rec.SetFieldByName('LCurrency.Currency_Code','000')
  rec.SetFieldByName('LCurrency.Short_Name','IDR')

def GetProductData(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],['Err_Message',''],
    ['ZakatBalance',0.0],['InfaqBalance',0.0],
    ['WakafBalance',0.0],['AmilBalance',0.0],
    ['NonHalalBalance',0.0],['TotalBalance',0.0],
    ['BranchName',''],['CurrencyName',''],
    ['AccountNo','']
  )
  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  ProductId = rec.ProductId
  CurrencyCode = rec.CurrencyCode
  BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  
  try:
    #Product = helper.GetObject('ProductAccount',rec.AccountNo)
    Product = helper.GetObjectByNames('ProductAccount',
       {'ProductId' : ProductId,
        'CurrencyCode' : CurrencyCode,
        'BranchCode' : BranchCode,
        }
    )
    
    status.ZakatBalance = Product.GetEntityBalance(1)
    status.InfaqBalance = Product.GetEntityBalance(2)
    status.WakafBalance = Product.GetEntityBalance(3)
    status.AmilBalance = Product.GetEntityBalance(4)
    status.NonHalalBalance = Product.GetEntityBalance(5)
    #status.OtherBalance = Product.GetOtherBalance()
    status.TotalBalance = Product.Balance
    status.AccountNo = Product.AccountNo
    
    corporate = helper.CreateObject('Corporate')
    CabangInfo = corporate.GetCabangInfo(Product.BranchCode)
    
    status.BranchName = CabangInfo.Nama_Cabang
    
    app = config.AppObject
    res = app.rexecscript(
                 'accounting',
                 'appinterface/Currency.GetCurrencyInfo',
                 app.CreateValues(['Kode_Valuta',Product.CurrencyCode])
          )
    status.CurrencyName = res.FirstRecord.short_name
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

def GetHistTransaction(config, params, returns):
  def AsDateTime(tdate):
    utils = config.ModLibUtils
    return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  AccountNo = rec.AccountNo
  FundEntity = rec.FundEntity
  BeginDate = int(rec.BeginDate)
  EndDate   = int(rec.EndDate)

  # Preparing returns
  Program = helper.GetObject('ProductAccount',AccountNo)
  EntityBalance = Program.GetEntityBalance(FundEntity,BeginDate)

  if BeginDate == EndDate :
    PeriodStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
  else:
    PeriodStr = "%s s/d %s" % (
                   config.FormatDateTime('dd-mm-yyyy',BeginDate),
                   config.FormatDateTime('dd-mm-yyyy',EndDate)
                 )
  # end if
  
  recSaldo = returns.CreateValues(
          ['BeginningBalance', EntityBalance or 0.0],
          ['PeriodStr',PeriodStr],
          ['TotalDebet',0.0],
          ['TotalCredit',0.0],
        )
  
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'TransactionCode: string',
      'MutationType: string',
      'Amount: float',
      'Debet:float',
      'Kredit:float',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'TransactionNo:string',
      'JenisTransaksi:string'
    ])
  )
  
  AddParam = ''
  if FundEntity != 0:
    AddParam += ' and FundEntity=:FundEntity '
    
  s = ' \
    SELECT FROM AccountTransactionItem \
    [ \
      AccountNo = :AccountNo \
      and LTransaction.ActualDate >= :BeginDate \
      and LTransaction.ActualDate < :EndDate \
      %s \
    ] \
    ( \
      TransactionItemId, \
      LTransaction.TransactionDate, \
      LTransaction.ActualDate, \
      LTransaction.TransactionCode, \
      MutationType, \
      Amount, \
      LTransaction.ReferenceNo, \
      LTransaction.Description, \
      LTransaction.Inputer, \
      LTransaction.TransactionNo,\
      LTransaction.LTransactionType.Description as JenisTransaksi,\
      Self \
    ) \
    THEN ORDER BY ASC ActualDate, ASC TransactionItemId;' % AddParam

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('AccountNo', AccountNo)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate + 1)
  if FundEntity != 0:
    oql.SetParameterValueByName('FundEntity', FundEntity)
    
  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  TotalDebet = 0.0
  TotalCredit = 0.0
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
      TotalDebet += ds.Amount
    else:
      recHist.Kredit = ds.Amount
      TotalCredit += ds.Amount
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description
    recHist.Inputer = ds.Inputer
    recHist.TransactionNo = ds.TransactionNo
    recHist.JenisTransaksi = ds.Description_1

    ds.Next()
  #-- while

  recSaldo.TotalDebet = TotalDebet
  recSaldo.TotalCredit = TotalCredit
