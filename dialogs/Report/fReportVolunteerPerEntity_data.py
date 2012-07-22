import com.ihsan.foundation.pobjecthelper as phelper
import simplejson

def FormSetDataEx(uideflist, params) :
  config = uideflist.config

  rec = uideflist.uipVolunteer.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.GroupBranchCode = str(config.SecurityContext.GetUserInfo()[3])
  rec.BeginDate = (config.Now())
  rec.EndDate = rec.BeginDate


def GetHistTransaction(config, params, returns):
  def AsDateTime(tdate):
    utils = config.ModLibUtils
    return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  VolunteerId = rec.VolunteerId
  BeginDate = rec.BeginDate
  EndDate   = rec.EndDate
  FundEntity = rec.FundEntity
  

  # Preparing returns
  status = returns.CreateValues(
     ['PeriodStr',''],
     ['BeginningBalance', 0.0],
     ['TotalDebet', 0.0],
     ['TotalCredit', 0.0],
     ['EndBalance', 0.0],
     )
     

  oVolunteer = helper.GetObject('Volunteer',VolunteerId)
  if oVolunteer.isnull : raise '',"Data Mitra ID '%s' Tidak Ditemukan" % VolunteerId
  status.BeginningBalance = oVolunteer.GetEntityBalance(FundEntity,BeginDate)

  if BeginDate == EndDate :
    status.PeriodStr = config.FormatDateTime('dd mmm yyyy',BeginDate)
  else:
    status.PeriodStr = "%s s/d %s" % (
                 config.FormatDateTime('dd mmm yyyy',BeginDate),
                 config.FormatDateTime('dd mmm yyyy',EndDate)
               )
  # end if

  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'TransactionCode: string',
      'TransactionType: string',
      'FundEntity:integer',
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

  AddParam = ''
  if FundEntity != 0:
    AddParam = ' and  LTransaction.FundEntity = :FundEntity '
    
  s = ' \
    SELECT FROM VolunteerTransaction \
    [ \
      VolunteerId = :VolunteerId and \
      LTransaction.LTransaction.ActualDate >= :BeginDate \
      and LTransaction.LTransaction.ActualDate < :EndDate \
      %s \
    ] \
    ( \
      LTransaction.TransactionItemId, \
      LTransaction.LTransaction.ActualDate, \
      LTransaction.LTransaction.TransactionCode, \
      LTransaction.LTransaction.LTransactionType.Description as TransactionType, \
      LTransaction.MutationType, \
      LTransaction.Amount, \
      LTransaction.LTransaction.ReferenceNo, \
      LTransaction.LTransaction.Description, \
      LTransaction.LTransaction.Inputer, \
      LTransaction.LTransaction.TransactionNo,\
      LTransaction.FundEntity, \
      Self \
    ) \
    THEN ORDER BY ASC ActualDate, ASC TransactionItemId;' % AddParam

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('VolunteerId', VolunteerId)
  oql.SetParameterValueByName('BeginDate', int(BeginDate))
  oql.SetParameterValueByName('EndDate', int(EndDate) + 1)
  if FundEntity != 0:
    oql.SetParameterValueByName('FundEntity', FundEntity)

  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(ds.ActualDate)
    recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.TransactionType = ds.Description
    #recHist.MutationType = ds.MutationType
    if ds.MutationType == 'C' :
      recHist.Debet = ds.Amount
      recHist.Kredit = 0.0
      status.TotalDebet += ds.Amount
    else:
      recHist.Debet = 0.0
      recHist.Kredit = ds.Amount
      status.TotalCredit += ds.Amount
    # end if

    #recHist.Amount = ds.Amount
    recHist.FundEntity = ds.FundEntity
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description_1
    recHist.Inputer = ds.Inputer
    recHist.NoTransaksi = ds.TransactionNo

    oTranDonor = helper.GetObject('DonorTransactionItem',ds.TransactionItemId)
    if not oTranDonor.isnull:
      recHist.PercentageOfAmil = oTranDonor.PercentageOfAmil

    recHist.AmilAmount = (recHist.PercentageOfAmil/100) * ds.Amount
    
    ds.Next()
  #-- while
  
  status.EndBalance = status.BeginningBalance + status.TotalDebet - status.TotalCredit
  
