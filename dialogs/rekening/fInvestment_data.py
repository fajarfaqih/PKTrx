import com.ihsan.foundation.pobjecthelper as phelper
import simplejson
import sys
import com.ihsan.timeutils as timeutils

def FormSetDataEx(uideflist, params) :
  config = uideflist.config

  rec = uideflist.uipInvestee.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.BranchId = int(config.SecurityContext.GetUserInfo()[2])

  Now = config.Now()
  
def GetBuyTransactionNo(helper,AccountNo):
  TransactionNo = ''

  # Get Buy Transaction TransactionNo
  oTran = helper.GetObjectByNames('AccountTransactionItem',
      {'AccountNo' : AccountNo,
       'LTransaction.TransactionCode' : 'INVS',
      }
    )

  if not oTran.isnull :
    TransactionNo = oTran.LTransaction.TransactionNo

  return TransactionNo
  
def GetDataInvestmentNonEmployee(config, params, returns):
  status = returns.CreateValues(
    ['IsErr' , 0],
    ['ErrMessage', ''],
  )
  
  dsInvestmentList = returns.AddNewDatasetEx(
      'InvestmentList',
    ';'.join([
      'AccountNo: string',
      'AccountName: string',
      'InvestmentAmount: float',
      'InvestmentNisbah: float',
      'OpeningDate: string',
      'TransactionNo: string',
      'InvestmentCatName: string',
      'InvesteeName: string',
    ])
  )

  try:
    helper = phelper.PObjectHelper(config)
    InvesteeId = params.FirstRecord.InvesteeId

    OQLText = " select from InvestmentNonEmployee \
      [ InvesteeId = :InvesteeId] \
      ( AccountNo , \
        AccountName , \
        LInvestmentCategory.InvestmentCatName , \
        InvestmentAmount , \
        InvestmentNisbah , \
        InvestmentShare , \
        OpeningDate, \
        self \
      ) then order by AccountNo ;"


    oql = config.OQLEngine.CreateOQL(OQLText)
    oql.SetParameterValueByName('InvesteeId', InvesteeId)
    oql.ApplyParamValues()
    oql.active = 1

    data  = oql.rawresult

    while not data.Eof:
      recList = dsInvestmentList.AddRecord()
      recList.AccountNo = data.AccountNo
      recList.AccountName = data.AccountName
      recList.InvestmentAmount = data.InvestmentAmount
      recList.InvestmentNisbah = data.InvestmentNisbah
      recList.OpeningDate = config.FormatDateTime('dd/mm/yyyy', timeutils.AsTDateTime(config, data.OpeningDate))
      recList.InvestmentCatName = data.InvestmentCatName
      recList.TransactionNo = GetBuyTransactionNo(helper,data.AccountNo)
      data.Next()
    # end while


  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])

def GetDataInvestmentEmployee(config, params, returns):
  status = returns.CreateValues(
    ['IsErr' , 0],
    ['ErrMessage', ''],
  )
  
  dsInvestmentList = returns.AddNewDatasetEx(
      'InvestmentList',
    ';'.join([
      'AccountNo: string',
      'AccountName: string',
      'InvestmentAmount: float',
      'InvestmentNisbah: float',
      'OpeningDate: string',
      'TransactionNo: string',
      'InvestmentCatName: string',
      'InvesteeName: string',
    ])
  )

  try:
    helper = phelper.PObjectHelper(config)
    EmployeeId = params.FirstRecord.EmployeeId

    OQLText = " select from InvestmentEmployee \
      [ EmployeeId = :EmployeeId] \
      ( AccountNo , \
        AccountName , \
        LInvestmentCategory.InvestmentCatName , \
        InvestmentAmount , \
        InvestmentNisbah , \
        InvestmentShare , \
        OpeningDate, \
        self \
      ) then order by AccountNo ;"


    oql = config.OQLEngine.CreateOQL(OQLText)
    oql.SetParameterValueByName('EmployeeId', EmployeeId)
    oql.ApplyParamValues()
    oql.active = 1

    data  = oql.rawresult
    
    while not data.Eof:
      recList = dsInvestmentList.AddRecord()
      recList.AccountNo = data.AccountNo
      recList.AccountName = data.AccountName
      recList.InvestmentAmount = data.InvestmentAmount
      recList.InvestmentNisbah = data.InvestmentNisbah
      recList.OpeningDate = config.FormatDateTime('dd/mm/yyyy', timeutils.AsTDateTime(config, data.OpeningDate))
      recList.InvestmentCatName = data.InvestmentCatName
      recList.TransactionNo = GetBuyTransactionNo(helper,data.AccountNo)
      data.Next()
    # end while


  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])

