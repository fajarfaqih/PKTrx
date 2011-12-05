import com.ihsan.foundation.pobjecthelper as phelper
import simplejson

def FormSetDataEx(uideflist, parameters) :
  config = uideflist.config

  BranchCode = config.SecurityContext.GetUserInfo()[4]
  BranchName = config.SecurityContext.GetUserInfo()[5]
  
  rec = uideflist.uipFilter.Dataset.AddRecord()

  rec.BeginDate = int(config.Now())
  rec.EndDate = rec.BeginDate

  rec.BranchCode = BranchCode
  rec.BranchName = BranchName
  rec.HeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')


def GetHistTransaction(config, params, returns):
  def AsDateTime(tdate):
    utils = config.ModLibUtils
    return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

  helper = phelper.PObjectHelper(config)

  rec = params.FirstRecord
  OwnerId = rec.OwnerId
  IsAllOwner = rec.IsAllOwner
  BeginDate = rec.BeginDate
  EndDate   = rec.EndDate
  BranchCode = rec.BranchCode

  if BeginDate == EndDate:
     Tanggal = '%s' % config.FormatDateTime('dd-mm-yyyy', BeginDate)
  else:
     Tanggal = '%s s/d %s' % (
                 config.FormatDateTime('dd-mm-yyyy', BeginDate),
                 config.FormatDateTime('dd-mm-yyyy', EndDate)
               )
               
  # Preparing returns
  status = returns.CreateValues(
     ['Tanggal',Tanggal],
     ['TotalAmount', 0.0],
  )
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionDateStr: string',
      'TransactionCode: string',
      'TransactionType: string',
      'MutationType: string',
      'Amount: float',
      'AmountEkuivalen: float',
      'Rate: float',
      'CurrencyCode: string',
      'CurrencyName: string',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'NoTransaksi:string',
      'OwnerName:string',
      'OwnerCode:string',
      'BudgetCode:string',
      'GroupName:string',
      'ItemName:string',
      'BudgetTransTypeDesc:string'
    ])
  )


  AddParam = ""
  if IsAllOwner == 'F' :
    AddParam += " and LBudget.OwnerId = %d " % OwnerId
    
  s = ' \
    SELECT FROM BudgetTransaction \
    [ \
      LTransaction.LTransaction.ActualDate >= :BeginDate \
      and LTransaction.LTransaction.ActualDate < :EndDate \
      and LTransaction.BranchCode = :BranchCode \
      %s \
    ] \
    ( \
      LTransaction.TransactionItemId, \
      LTransaction.LTransaction.ActualDate, \
      LTransaction.LTransaction.TransactionCode, \
      LTransaction.LTransaction.LTransactionType.Description as TransactionType, \
      LTransaction.MutationType, \
      LTransaction.Amount, \
      LTransaction.Ekuivalenamount, \
      LTransaction.Rate, \
      LTransaction.CurrencyCode, \
      LTransaction.LCurrency.Short_Name, \
      LTransaction.LTransaction.Rate as TransRate, \
      LTransaction.LTransaction.CurrencyCode as TransCurrencyCode, \
      LTransaction.LTransaction.LCurrency.Short_Name as TransCurrencyName, \
      LTransaction.LTransaction.ReferenceNo, \
      LTransaction.LTransaction.Description, \
      LTransaction.LTransaction.Inputer, \
      LTransaction.LTransaction.TransactionNo,\
      LBudget.BudgetCode, \
      LBudget.LBudgetItem.LParent.BudgetItemDescription as ItemGroup, \
      LBudget.LBudgetItem.BudgetItemDescription as ItemDetail, \
      LBudget.LOwner.OwnerName, \
      LBudget.LOwner.OwnerCode, \
      self.BudgetTransType, \
      self.BudgetTransType $ as BudgetTransTypeDesc,  \
      Self \
    ) \
    THEN ORDER BY ASC OwnerCode,BudgetCode, ActualDate, ASC TransactionItemId;' % AddParam

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('BeginDate', int(BeginDate))
  oql.SetParameterValueByName('EndDate', int(EndDate) + 1)
  oql.SetParameterValueByName('BranchCode', BranchCode)

  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  TotalAmount = 0.0
  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(ds.ActualDate)
    recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.TransactionType = ds.Description
    recHist.MutationType = ds.MutationType
    recHist.OwnerName = ds.OwnerName
#    recHist.

    TranCurrencyCode = ds.CurrencyCode_1
    TranCurrencyName = ds.Short_Name_1
    TransRate        = ds.Rate_1
    
    if ds.CurrencyCode != TranCurrencyCode and ds.CurrencyCode == '000':
      CurrencyCode = TranCurrencyCode
      CurrencyName = TranCurrencyName
      Rate = TransRate
      Amount      = ds.Amount / Rate
    else :
      CurrencyCode = ds.CurrencyCode
      CurrencyName = ds.Short_Name
      Rate = ds.Rate
      Amount = ds.Amount
    # end if
      
    recHist.Amount = Amount
    recHist.AmountEkuivalen = ds.Ekuivalenamount

    if ds.BudgetTransType == 'R' :
      recHist.Amount = -1 * Amount
      recHist.AmountEkuivalen = -1 * ds.Ekuivalenamount

    recHist.CurrencyCode = CurrencyCode
    recHist.CurrencyName = CurrencyName

    recHist.Rate = ds.Rate
    TotalAmount += ds.Ekuivalenamount
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description_1
    recHist.Inputer = ds.Inputer
    recHist.NoTransaksi = ds.TransactionNo
    recHist.GroupName = ds.BudgetItemDescription
    recHist.ItemName = ds.BudgetItemDescription_1
    recHist.BudgetCode = ds.BudgetCode
    recHist.BudgetTransTypeDesc = ds.Enum_Description

    ds.Next()
  #-- while
  status.TotalAmount = TotalAmount
