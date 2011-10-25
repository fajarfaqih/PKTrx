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
  

  # Preparing returns
  recSaldo = returns.CreateValues(['BeginningBalance', 0.0])
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
      'NoTransaksi:string'
    ])
  )

  #AddParam = ''
  #if IsAllProject != 'T' :
  #  AddParam = ' and LTransaction.AccountNo=:AccountNo '
    
  s = ' \
    SELECT FROM SponsorTransaction \
    [ \
      SponsorId = :SponsorId and \
      ProjectSponsorId = :ProjectSponsorId and \
      LTransaction.LTransaction.TransactionDate >= :BeginDate \
      and LTransaction.LTransaction.TransactionDate < :EndDate \
    ] \
    ( \
      LTransaction.TransactionItemId, \
      LTransaction.LTransaction.TransactionDate, \
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
    THEN ORDER BY ASC TransactionDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('SponsorId', SponsorId)
  oql.SetParameterValueByName('BeginDate', int(BeginDate))
  oql.SetParameterValueByName('EndDate', int(EndDate) + 1)
  oql.SetParameterValueByName('ProjectSponsorId', ProjectSponsorId)

  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(ds.TransactionDate)
    recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.TransactionType = ds.Description
    #recHist.MutationType = ds.MutationType
    if ds.MutationType == 'D' :
      recHist.Debet = ds.Amount
      recHist.Kredit = 0.0
    else:
      recHist.Debet = 0.0
      recHist.Kredit = ds.Amount
    #recHist.Amount = ds.Amount
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description_1
    recHist.Inputer = ds.Inputer
    recHist.NoTransaksi = ds.TransactionNo

    ds.Next()
  #-- while
  
