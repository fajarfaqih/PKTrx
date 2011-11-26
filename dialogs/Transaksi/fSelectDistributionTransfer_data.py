import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.timeutils as timeutils

def FormSetDataEx(uideflist,params):

  config = uideflist.Config
  
  if params.DatasetCount == 0 or params.GetDataset(0).Structure.StructureName != 'data':
    rec = uideflist.uipFilter.Dataset.AddRecord()
    Now = config.Now()
    rec.BeginDate = int(Now) - 30
    rec.EndDate = int(Now)
    rec.BranchCode = config.SecurityContext.GetUserInfo()[4]
    rec.UserId = config.SecurityContext.UserId
  else:
    recParams = params.FirstRecord
    aBeginDate = recParams.BeginDate
    aEndDate = recParams.EndDate
    if recParams.DistType == 'IN' :
      aSourceBranchCode = recParams.SourceBranchCode
      aDestBranchCode = config.SecurityContext.GetUserInfo()[4]
    else:
      aSourceBranchCode = config.SecurityContext.GetUserInfo()[4]
      aDestBranchCode = recParams.DestBranchCode
      
    aDistType = recParams.DistType
    
    if aDistType == 'IN' :
      res = GetDataDistributionIN(config,aSourceBranchCode,aDestBranchCode,aBeginDate,aEndDate)
    else : # aDistType == 'OUT'
      res = GetDataDistributionOUT(config,aSourceBranchCode,aDestBranchCode,aBeginDate,aEndDate)

    uipDistList = uideflist.uipDistributionList.Dataset
    while not res.Eof :
      recDisb = uipDistList.AddRecord()
      recDisb.TransactionDate = timeutils.AsTDateTime(config, res.ActualDate)
      recDisb.BranchCodeSource = res.BranchSource
      recDisb.BranchNameSource = res.BranchName
      recDisb.BranchCodeDest = res.BranchDestination
      recDisb.BranchNameDest = res.BranchName_1
      recDisb.Amount = res.Amount
      recDisb.TransactionNo = res.TransactionNo
      recDisb.Description = res.Description
      recDisb.ReportStatus = res.ReportStatus
      recDisb.TransactionId = res.TransactionId
      recDisb.DistributionId = res.DistributionId
      recDisb.SourceCashAccountNo = res.CashAccountNoSource
      recDisb.SourceCashAccountName = res.AccountName
      recDisb.DestCashAccountNo = res.CashAccountNoDest
      recDisb.DestCashAccountName = res.AccountName_1
      res.Next()
    # end while
  # end if
  
def GetDataDistributionOUT(config,SourceBranchCode,DestBranchCode,BeginDate,EndDate):
  AddParam = ''
  if DestBranchCode != '' :
    AddParam = " and BranchDestination = '%s' " % DestBranchCode

  sOQL = " \
    select from DistributionTransferInfo \
    [ BranchSource = :SourceBranchCode and \
     LTransaction.ActualDate >= :BeginDate and \
     LTransaction.ActualDate <= :EndDate and \
     ReportStatus = 'F' \
     %s ]\
    (LTransaction.ActualDate, \
     BranchSource, \
     LBranchSource.BranchName , \
     BranchDestination, \
     LBranchDestination.BranchName as BranchNameDest, \
     LTransaction.Amount , \
     LTransaction.TransactionNo, \
     LTransaction.Description, \
     ReportStatus, \
     TransactionId , \
     DistributionId, \
     CashAccountNoSource , \
     LCashAccountSource.AccountName as AccountNameSource, \
     CashAccountNoDest, \
     LCashAccountDest.AccountName as AccountNameDest, \
     self) then order by ActualDate,TransactionId ; \
  " % AddParam

  oql = config.OQLEngine.CreateOQL(sOQL)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate)
  oql.SetParameterValueByName('SourceBranchCode', SourceBranchCode)

  oql.ApplyParamValues()

  oql.active = 1

  return oql.rawresult
  
def GetDataDistributionIN(config,SourceBranchCode,DestBranchCode,BeginDate,EndDate):
  AddParam = ''
  if SourceBranchCode != '' :
    AddParam = " and BranchSource = '%s' " % SourceBranchCode
    
  sOQL = " \
    select from DistributionTransferInfo \
    [ BranchDestination = :DestBranchCode and \
     LTransaction.ActualDate >= :BeginDate and \
     LTransaction.ActualDate <= :EndDate \
     %s ]\
    (LTransaction.ActualDate, \
     BranchSource, \
     LBranchSource.BranchName , \
     BranchDestination, \
     LBranchDestination.BranchName as BranchNameDest, \
     LTransaction.Amount , \
     LTransaction.TransactionNo, \
     LTransaction.Description, \
     ReportStatus, \
     TransactionId , \
     DistributionId, \
     CashAccountNoSource , \
     LCashAccountSource.AccountName as AccountNameSource, \
     CashAccountNoDest, \
     LCashAccountDest.AccountName as AccountNameDest, \
     self) then order by ActualDate,TransactionId ; \
  " % AddParam

  oql = config.OQLEngine.CreateOQL(sOQL)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate)
  oql.SetParameterValueByName('DestBranchCode', DestBranchCode)

  oql.ApplyParamValues()

  oql.active = 1

  return oql.rawresult

