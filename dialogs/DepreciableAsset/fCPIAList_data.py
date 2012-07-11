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

    ds = GetDataCPIA(config,recParam)

    LsProduct = {}
    while not ds.Eof:
      oCPIA = uideflist.uipCPIA.Dataset.AddRecord()
      oCPIA.SetFieldAt(0, 'PObj:CostPaidInAdvance#AccountNo=%s' % ds.AccountNo)
      oCPIA.AccountNo = ds.AccountNo
      oCPIA.AccountName = ds.AccountName
      oCPIA.Description = ds.Description
      oCPIA.NilaiAwal = ds.NilaiAwal
      oCPIA.OpeningDate = timeutils.AsTDateTime(config, ds.OpeningDate)
      oCPIA.CostAccountNo = ds.CostAccountNo
      oCPIA.Account_Name = ds.Account_Name
      oCPIA.TransactionNo = GetBuyTransactionNo(helper,ds.AccountNo)
      oCPIA.CPIACatName = ds.CPIACatName

      ds.Next()
    # end while

def GetBuyTransactionNo(helper,AccountNo):
  TransactionNo = ''

  # Get Buy Transaction TransactionNo
  oTran = helper.GetObjectByNames('AccountTransactionItem',
      {'AccountNo' : AccountNo,
       'LTransaction.TransactionCode' : 'CPIA',
      }
    )

  if not oTran.isnull :
    TransactionNo = oTran.LTransaction.TransactionNo

  return TransactionNo

def GetDataCPIA(config,recParam):

  IsAllCPIA = recParam.IsAllCPIA
  BranchCode = recParam.BranchCode
  Account_Code = recParam.Account_Code
  BeginDate = recParam.BeginDate
  EndDate = recParam.EndDate
  CPIACatId = recParam.CPIACatId

  AddParam = ""
  if IsAllCPIA == 'F' :

    if CPIACatId not in [0,'',None] :
      AddParam += " and CPIACatId= %d " % CPIACatId
    # end if
    
    if Account_Code != '':
      AddParam += " and CostAccountNo= '%s' " % Account_Code

    BeginDate = config.FormatDateTime('mm/dd/yyyy', BeginDate)
    EndDate = config.FormatDateTime('mm/dd/yyyy', EndDate)

    AddParam += " and OpeningDate >= '%s' and OpeningDate <= '%s' " % (BeginDate,EndDate)


  OQLText = " select from CostPaidInAdvance \
    [ BranchCode = '%s' \
      %s] \
    ( AccountNo, \
      AccountName, \
      CostAccountNo, \
      Description, \
      NilaiAwal, \
      LAccount.Account_Name, \
      OpeningDate, \
      LCPIACategory.CPIACatName, \
      self \
    ) then order by AccountNo ;" % (BranchCode,AddParam)


  oql = config.OQLEngine.CreateOQL(OQLText)
  oql.ApplyParamValues()
  oql.active = 1
  return oql.rawresult

def GetCPIAList(config,params,returns):
  status = returns.CreateValues(
     ['Is_Err',0],
     ['Err_Message',''],
     ['BranchName',''],
     ['PeriodStr',''],
  )

  rdsCPIAList = returns.AddNewDatasetEx(
      'CPIAList',
    ';'.join([
      'AccountNo: string',
      'AccountName: string',
      'NilaiAwal: float',
      'Balance: float',
      'Description: string' ,
      'TotalPenyusutan: float',
      'OpeningDate: string',
      'TransactionNo: string',
      'CostAccountNo: string',
      'CostAccountName: string',
      'CPIACatName: string',
    ])
  )

  try:
    helper = phelper.PObjectHelper(config)
    recParam = params.FirstRecord
    data = GetDataCPIA(config,recParam)

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

    while not data.Eof :

      recCPIA = rdsCPIAList.AddRecord()

      recCPIA.AccountNo = data.AccountNo
      recCPIA.AccountName = data.AccountName
      recCPIA.Description = data.Description
      recCPIA.NilaiAwal = data.NilaiAwal
      recCPIA.OpeningDate = config.FormatDateTime('dd/mm/yyyy', timeutils.AsTDateTime(config, data.OpeningDate))
      recCPIA.CostAccountNo = data.CostAccountNo
      recCPIA.CostAccountName = data.Account_Name
      recCPIA.TransactionNo = GetBuyTransactionNo(helper,data.AccountNo)
      recCPIA.CPIACatName = data.CPIACatName
      

      data.Next()
    # end while

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

