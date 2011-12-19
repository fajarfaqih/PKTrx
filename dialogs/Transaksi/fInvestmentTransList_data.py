import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.timeutils as timeutils
import pyFlexcel
import sys
import os

def FormSetDataEx(uideflist,params):

  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  
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

    res = GetDataInvestmentTrans(config,aBranchCode,aBeginDate,aEndDate)

    uipTransList = uideflist.uipInvestTransList.Dataset

    LsInvestment = {}
    while not res.Eof :
      recTrans = uipTransList.AddRecord()
      recTrans.TransactionDate = timeutils.AsTDateTime(config, res.ActualDate)
      recTrans.TransactionName = res.Description_1.capitalize()
      recTrans.Amount = res.Amount
      recTrans.TransactionNo = res.TransactionNo
      recTrans.Description = res.Description
      recTrans.TransactionId = res.TransactionId
      recTrans.TransactionItemId = res.TransactionItemId

      recTrans.InvestmentCategory = res.InvestmentCatName #oInvestment.LInvestmentCategory.InvestmentCatName
      recTrans.InvesteeName = res.AccountName
      recTrans.PrincipalAmount = res.PrincipalAmount
      recTrans.ShareAmount = res.ShareAmount
      res.Next()
    # end while
  # end if
  
def GetDataInvestmentTrans(config, BranchCode, BeginDate, EndDate):
  
  sOQL = " \
    select from InvestmentTransactItem \
    [  BranchCode = :BranchCode and \
       LTransaction.ActualDate >= :BeginDate and \
       LTransaction.ActualDate < :EndDate ] \
    ( \
       LTransaction.ActualDate, \
       LTransaction.Amount , \
       LTransaction.TransactionNo, \
       LTransaction.Description, \
       LTransaction.LTransactionType.Description as TransactionName, \
       AccountNo , \
       LInvestment.AccountName, \
       LInvestment.LInvestmentCategory.InvestmentCatName ,\
       TransactionId , \
       TransactionItemId , \
       PrincipalAmount, \
       ShareAmount, \
     self) then order by ActualDate,TransactionId ; \
  "


  oql = config.OQLEngine.CreateOQL(sOQL)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate + 1)
  oql.SetParameterValueByName('BranchCode', BranchCode)

  oql.ApplyParamValues()

  oql.active = 1

  return oql.rawresult

# end def GetDataInvestmentTrans


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

    res = GetDataInvestmentTrans(config,aBranchCode,aBeginDate,aEndDate)
    
    workbook = pyFlexcel.Open(pathtemplates + 'tplInvestmentTransList.xls')
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
        workbook.SetCellValue(row , 3, res.AccountName)
        workbook.SetCellValue(row , 4, res.InvestmentCatName)
        workbook.SetCellValue(row , 5, res.Amount)
        workbook.SetCellValue(row , 6, res.PrincipalAmount)
        workbook.SetCellValue(row , 7, res.ShareAmount)
        workbook.SetCellValue(row , 8, res.TransactionNo)
        workbook.SetCellValue(row , 9, res.Description_1.capitalize())
        workbook.SetCellValue(row , 10, res.Description)
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
