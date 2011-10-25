import com.ihsan.foundation.pobjecthelper as phelper
import sys
import com.ihsan.timeutils as timeutils

def FormSetDataEx(uideflist,params):
  config = uideflist.Config

  if params.DatasetCount == 0 :
    recData = uideflist.uipData.Dataset.AddRecord()
    recData.BranchCode = config.SecurityContext.GetUserInfo()[4]

    Now = config.Now()
    NowTup = config.ModDateTime.DecodeDate(Now)
    recData.BeginDate = config.ModDateTime.EncodeDate(NowTup[0], 1, 1)
    recData.EndDate = Now

  else:
    helper = phelper.PObjectHelper(config)
    recParam = params.FirstRecord

    ds = GetDataInvestment(config,recParam)

    while not ds.Eof:
      oInv = uideflist.uipInvestment.Dataset.AddRecord()
      oInv.SetFieldAt(0, 'PObj:uipInvestment#AccountNo=%s' % ds.AccountNo)
      oInv.AccountNo = ds.AccountNo
      oInv.AccountName = ds.AccountName
      oInv.InvestmentCatName = ds.InvestmentCatName
      oInv.InvestmentAmount = ds.InvestmentAmount
      oInv.InvestmentNisbah = ds.InvestmentNisbah
      oInv.OpeningDate = timeutils.AsTDateTime(config, ds.OpeningDate)
      oInv.TransactionNo = GetBuyTransactionNo(helper,ds.AccountNo)
      
      # Get InvesteeName
      oInvestment = helper.GetObject('Investment',ds.AccountNo).CastToLowestDescendant()
      oInv.InvesteeName = oInvestment.GetInvesteeName()

      ds.Next()
    # end while

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

def GetDataInvestment(config,recParam):
  IsAllInvestment = recParam.IsAllInvestment
  BranchCode = recParam.BranchCode
  InvestmentCatId = recParam.InvestmentCatId
  BeginDate = recParam.BeginDate
  EndDate = recParam.EndDate

  AddParam = ""
  if IsAllInvestment == 'F' :

    if InvestmentCatId not in [0,None,'']:
      AddParam += " and InvestmentCatId= %d " % InvestmentCatId

    BeginDate = config.FormatDateTime('mm/dd/yyyy', BeginDate)
    EndDate = config.FormatDateTime('mm/dd/yyyy', EndDate)

    AddParam += " and OpeningDate >= '%s' and OpeningDate <= '%s' " % (BeginDate,EndDate)
  # end if

  OQLText = " select from Investment \
    [ BranchCode = '%s' \
      %s] \
    ( AccountNo , \
      AccountName , \
      LInvestmentCategory.InvestmentCatName , \
      InvestmentAmount , \
      InvestmentNisbah , \
      InvestmentShare , \
      OpeningDate, \
      self \
    ) then order by AccountNo ;" % (BranchCode,AddParam)


  oql = config.OQLEngine.CreateOQL(OQLText)
  oql.ApplyParamValues()
  oql.active = 1
  return oql.rawresult

def GetInvestmentList(config,params,returns):
  status = returns.CreateValues(
     ['Is_Err',0],
     ['Err_Message',''],
     ['BranchName',''],
     ['PeriodStr',''],
  )

  rdsInvestList = returns.AddNewDatasetEx(
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
    recParam = params.FirstRecord
    data = GetDataInvestment(config,recParam)

    BeginDate = recParam.BeginDate
    EndDate = recParam.EndDate
    if BeginDate == EndDate :
      PeriodStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
    else:
      PeriodStr = "%s s/d %s" % (
                     config.FormatDateTime('dd-mm-yyyy',BeginDate),
                     config.FormatDateTime('dd-mm-yyyy',EndDate)
                   )
    # end if


    status.BranchName = str(config.SecurityContext.GetUserInfo()[5])
    status.PeriodStr = PeriodStr

    LsProduct = {}
    while not data.Eof :

      rec = rdsInvestList.AddRecord()
      rec.AccountNo = data.AccountNo
      rec.AccountName = data.AccountName
      rec.InvestmentAmount = data.InvestmentAmount
      rec.InvestmentNisbah = data.InvestmentNisbah
      rec.OpeningDate = config.FormatDateTime('dd/mm/yyyy', timeutils.AsTDateTime(config, data.OpeningDate))
      rec.InvestmentCatName = data.InvestmentCatName
      rec.TransactionNo = GetBuyTransactionNo(helper,data.AccountNo)

      # Get InvesteeName
      oInvestment = helper.GetObject('Investment',data.AccountNo).CastToLowestDescendant()
      rec.InvesteeName = oInvestment.GetInvesteeName()

      data.Next()
    # end while

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
