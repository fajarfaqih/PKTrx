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
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
    aFilterSourceBranch = recParams.SourceBranchCode
    aFilterDestBranchCode = recParams.DestBranchCode
    
    res = GetDataDistribution(config,aBranchCode,aBeginDate,aEndDate,aFilterSourceBranch,aFilterDestBranchCode)

    uipDistList = uideflist.uipDistributionList.Dataset
    while not res.Eof :
      recDisb = uipDistList.AddRecord()
      recDisb.TransactionDate = timeutils.AsTDateTime(config, res.ActualDate)
      recDisb.BranchNameSource = res.BranchName
      recDisb.BranchNameDest = res.BranchName_1
      recDisb.Amount = res.Amount
      recDisb.TransactionNo = res.TransactionNo
      recDisb.Description = res.Description
      recDisb.ReportStatus = res.ReportStatus
      recDisb.TransactionId = res.TransactionId
      recDisb.DistributionId = res.DistributionId
      res.Next()
    # end while
  # end if
  
def GetDataDistribution(config,BranchCode,BeginDate,EndDate,FilterSource,FilterDestination):

  AddParams = ''

  if FilterSource != '' :
    AddParams += " and BranchSource = '%s' " % FilterSource

  if FilterDestination != '' :
    AddParams += " and BranchDestination = '%s' " % FilterDestination
  
  sOQL = " \
    select from DistributionTransferInfo \
    [ ( BranchSource = :BranchSource or BranchDestination = :BranchDestination) and \
     LTransaction.ActualDate >= :BeginDate and \
     LTransaction.ActualDate <= :EndDate \
     %s ] \
    (DistributionId, \
     LTransaction.ActualDate, \
     LBranchSource.BranchName as BranchNameSource, \
     LBranchDestination.BranchName as BranchNameDest, \
     LTransaction.Amount , \
     LTransaction.TransactionNo, \
     LTransaction.Description, \
     ReportStatus, \
     TransactionId , \
     self) then order by ActualDate,TransactionId ; \
  " % AddParams


  oql = config.OQLEngine.CreateOQL(sOQL)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate)
  oql.SetParameterValueByName('BranchSource', BranchCode)
  oql.SetParameterValueByName('BranchDestination', BranchCode)

  oql.ApplyParamValues()

  oql.active = 1

  return oql.rawresult
  
def OnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  oDonorTrans = helper.GetObjectByInstance('CATransactItem', sender.ActiveInstance)

  rec.TransactionNo = oDonorTrans.LTransaction.TransactionNo
  rec.TransactionDate = oDonorTrans.LTransaction.GetAsTDateTime('TransactionDate')
  rec.Description = oDonorTrans.LTransaction.Description

