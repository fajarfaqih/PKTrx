import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.timeutils as timeutils
import pyFlexcel
import sys
import os

def FormSetDataEx(uideflist,params):

  config = uideflist.Config
  
  if params.DatasetCount == 0 or params.GetDataset(0).Structure.StructureName != 'data':
    rec = uideflist.uipFilter.Dataset.AddRecord()
    Now = config.Now()
    rec.BeginDate = int(Now) - 30
    rec.EndDate = int(Now)
    rec.BranchCode = config.SecurityContext.GetUserInfo()[4]
    rec.BranchName = config.SecurityContext.GetUserInfo()[5]
    rec.HeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')
    rec.UserId = config.SecurityContext.UserId
  else:
    recParams = params.FirstRecord
    aBeginDate = recParams.BeginDate
    aEndDate = recParams.EndDate
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
    aFilterSourceBranch = recParams.SourceBranchCode
    aFilterDestBranchCode = recParams.DestBranchCode
    aIsReportedShow = recParams.IsReportedShow
    
    res = GetDataDistribution(config,aBranchCode,aBeginDate,aEndDate,aFilterSourceBranch,aFilterDestBranchCode,aIsReportedShow)

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
  
def GetDataDistribution(config,BranchCode,BeginDate,EndDate,FilterSource,FilterDestination,aIsReportedShow):

  AddParams = ''

  if FilterSource != '' :
    AddParams += " and BranchSource = '%s' " % FilterSource

  if FilterDestination != '' :
    AddParams += " and BranchDestination = '%s' " % FilterDestination
  
  if aIsReportedShow == 'F' :
    AddParams += " and ReportStatus = 'F' "
    
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

dictReportStatus = {
  'F' : 'Belum Dilaporkan',
  'T' : 'Telah Dilaporkan',
}

def GetExcelData(config, params, returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['FileName',''],)
    
  try:
    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate')
    pathtemplates = config.HomeDir + 'templates\\'
    pathresult = corporate.GetUserHomeDir() + '\\'

    resFilename  = pathresult + 'BranchDistributionList.xls'

    recParams = params.FirstRecord
    aBeginDate = recParams.BeginDate
    aEndDate = recParams.EndDate
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
    aFilterSourceBranch = recParams.SourceBranchCode
    aFilterDestBranchCode = recParams.DestBranchCode
    aIsReportedShow = recParams.IsReportedShow

    res = GetDataDistribution(config,aBranchCode,aBeginDate,aEndDate,aFilterSourceBranch,aFilterDestBranchCode,aIsReportedShow)

    workbook = pyFlexcel.Open(pathtemplates + 'tplBranchDistributionList.xls')
    workbook.ActivateWorksheet('data')
    try :
      StrTanggal = ''
      if aBeginDate == aEndDate:
         StrTanggal = '%s' % config.FormatDateTime('dd mmm yyyy', aBeginDate)
      else:
         StrTanggal = '%s s.d. %s' % (
                     config.FormatDateTime('dd mmm yyyy', aBeginDate),
                     config.FormatDateTime('dd mmm yyyy', aEndDate)
                   )

      workbook.SetCellValue(2, 3, StrTanggal)

      idx = 0
      while not res.Eof :
        row = idx + 5
        workbook.SetCellValue(row , 1, str(idx+1))
        workbook.SetCellValue(row , 2, config.FormatDateTime('dd-mm-yyyy',timeutils.AsTDateTime(config, res.ActualDate)))
        workbook.SetCellValue(row , 3, res.BranchName)
        workbook.SetCellValue(row , 4, res.BranchName_1)
        workbook.SetCellValue(row , 5, res.Amount)
        workbook.SetCellValue(row , 6, res.TransactionNo)
        workbook.SetCellValue(row , 7, res.Description)
        workbook.SetCellValue(row , 8, dictReportStatus[res.ReportStatus])
        
        idx += 1
        res.Next()
      # end while

      if os.access(resFilename, os.F_OK) == 1:
        os.remove(resFilename)
      workbook.SaveAs(resFilename)

    finally:
      workbook = None

    sw = returns.AddStreamWrapper()
    sw.LoadFromFile(resFilename)
    sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(resFilename)

  except:
    status.Is_Err = 1
    status.Err_Message =str(sys.exc_info()[1])
  # end try except
