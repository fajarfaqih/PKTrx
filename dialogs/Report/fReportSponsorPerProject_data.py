
import com.ihsan.foundation.pobjecthelper as phelper
import simplejson

def FormSetDataEx(uideflist, params) :
  config = uideflist.config

  rec = uideflist.uipSponsor.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.BeginDate = (config.Now())
  rec.EndDate = rec.BeginDate


def GetHistTransaction(config, params, returns):
  def AsDateTime(tdate):
    utils = config.ModLibUtils
    return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  SponsorId = rec.SponsorId
  BeginDate = rec.BeginDate
  EndDate   = rec.EndDate
  ProjectSponsorId = rec.ProjectSponsorId
  IsAllProject = rec.IsAllProject
  AccountNo = rec.AccountNo


  # Preparing returns
  oProjectAccount = helper.GetObject('ProjectAccount',AccountNo)
  
  recSaldo = returns.CreateValues(
     ['BeginningBalance', 0.0],
     ['TotalDebet', 0.0],
     ['TotalCredit', 0.0],
     ['EndBalance', 0.0],
     ['PeriodStr',''],
  )

  if BeginDate == EndDate:
    Tanggal = '%s' % config.FormatDateTime('dd mmm yyyy', BeginDate)
  else:
    Tanggal = '%s s/d %s' % (
                config.FormatDateTime('dd mmm yyyy', BeginDate),
                config.FormatDateTime('dd mmm yyyy', EndDate)
               )
  recSaldo.PeriodStr = Tanggal
  recSaldo.BeginningBalance = oProjectAccount.GetBalanceByDate(BeginDate)

  # Transaction History
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'TransactionCode: string',
      'TransactionType: string',
      'Debet: float',
      'Kredit: float',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'NoTransaksi:string',
      'PercentageOfAmil: float',
      'AmilAmount: float',
    ])
  )

  #AddParam = ''
  #if IsAllProject != 'T' :
  #  AddParam = ' and LTransaction.AccountNo=:AccountNo '
    
  s = ' \
    SELECT FROM SponsorTransaction \
    [ \
      SponsorId = :SponsorId and \
      LTransaction.LTransaction.ActualDate >= :BeginDate \
      and LTransaction.LTransaction.ActualDate < :EndDate \
      and LTransaction.AccountNo = :AccountNo \
    ] \
    ( \
      LTransaction.TransactionItemId, \
      LTransaction.LTransaction.ActualDate as ActualDate, \
      LTransaction.LTransaction.TransactionCode, \
      LTransaction.LTransaction.LTransactionType.Description as TransactionType, \
      LTransaction.MutationType, \
      LTransaction.Amount, \
      LTransaction.LTransaction.ReferenceNo, \
      LTransaction.LTransaction.Description, \
      LTransaction.LTransaction.Inputer, \
      LTransaction.LTransaction.TransactionNo,\
      Self \
    ) \
    THEN ORDER BY ASC ActualDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('SponsorId', SponsorId)
  oql.SetParameterValueByName('BeginDate', int(BeginDate))
  oql.SetParameterValueByName('EndDate', int(EndDate) + 1)
  oql.SetParameterValueByName('AccountNo', AccountNo)
#  oql.SetParameterValueByName('ProjectSponsorId', ProjectSponsorId)

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
    recHist.TransactionType = ds.Description
    #recHist.MutationType = ds.MutationType
    if ds.MutationType == 'D' :
      recHist.Debet = ds.Amount
      recHist.Kredit = 0.0
      TotalDebet += ds.Amount
    else:
      recHist.Debet = 0.0
      recHist.Kredit = ds.Amount
      TotalCredit += ds.Amount
      
    #recHist.Amount = ds.Amount
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description_1
    recHist.Inputer = ds.Inputer
    recHist.NoTransaksi = ds.TransactionNo
    recHist.PercentageOfAmil = 0.0
    

    oTranDonor = helper.GetObject('DonorTransactionItem',ds.TransactionItemId)
    if not oTranDonor.isnull:
      recHist.PercentageOfAmil = oTranDonor.PercentageOfAmil
      
    recHist.AmilAmount = (recHist.PercentageOfAmil/100) * ds.Amount
    
    ds.Next()
  #-- while
  recSaldo.EndBalance = recSaldo.BeginningBalance - TotalDebet + TotalCredit
  recSaldo.TotalDebet = TotalDebet
  recSaldo.TotalCredit = TotalCredit
