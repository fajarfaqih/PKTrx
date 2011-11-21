import com.ihsan.foundation.pobjecthelper as phelper
import sys,os
import com.ihsan.timeutils as timeutils
import pyFlexcel


def FormSetDataEx(uideflist,params):
  config = uideflist.config
  helper = phelper.PObjectHelper(config)

  if params.DatasetCount == 0 or params.GetDataset(0).Structure.StructureName != 'data':
    rec = uideflist.uipFilter.Dataset.AddRecord()

    Today = int(config.Now())
    rec.BranchCode = config.SecurityContext.GetUserInfo()[4]
    rec.BeginDate = Today
    rec.EndDate = Today
  else:
    rec = params.FirstRecord
    aBeginDate = rec.BeginDate
    aEndDate = rec.EndDate
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
    aIsShowPaidInvoice = rec.IsShowPaidInvoice
    
    res  = GetDataInvoice(config,aBeginDate,aEndDate,aBranchCode,aIsShowPaidInvoice)
    
    uipInvoice = uideflist.uipInvoice.Dataset

    while not res.Eof:
      recInvoice = uipInvoice.AddRecord()
      InvoiceId = res.InvoiceId
      #recInvoice.SetFieldAt(0, 'PObj:Invoice#InvoiceId=%d' % InvoiceId)
      config.SendDebugMsg('InvoiceId %d ' % res.InvoiceId)
      recInvoice.InvoiceId = res.InvoiceId
      recInvoice.InvoiceNo = res.InvoiceNo
      recInvoice.InvoiceDate = timeutils.AsTDateTime(config, res.InvoiceDate)
      recInvoice.InvoicePaymentStatus = res.InvoicePaymentStatus
      recInvoice.InvoiceCurrencyName = res.Short_Name
      recInvoice.InvoiceAmount = res.InvoiceAmount
      recInvoice.SponsorId = res.SponsorId
      recInvoice.SetFieldByName('LSponsor.Id',res.SponsorId)
      recInvoice.SetFieldByName('LSponsor.Full_Name',res.Full_Name)
      recInvoice.SetFieldByName('LProductAccount.AccountNo',res.ProductAccountNo)
      recInvoice.SetFieldByName('LProductAccount.AccountName',res.AccountName)
      recInvoice.Description = res.Description
      recInvoice.TransactionId = res.TransactionId
      
      res.Next()
    # end if

def GetDataInvoice(config,aBeginDate,aEndDate,aBranchCode,aIsShowPaidInvoice='F'):
  AddFilter = ''
  if aIsShowPaidInvoice == 'F' :
    AddFilter += " and InvoicePaymentStatus = 'F' "
    
  s = ' \
    SELECT FROM InvoiceProduct \
    [ \
      InvoiceDate >= :BeginDate \
      and InvoiceDate <= :EndDate \
      and BranchCode = :BranchCode \
      %s \
    ] \
    ( \
      InvoiceId, \
      InvoiceNo, \
      InvoiceAmount, \
      InvoicePaymentStatus, \
      InvoiceDate, \
      SponsorId, \
      LSponsor.Full_Name,\
      ProductAccountNo ,\
      LProductAccount.AccountName, \
      Description, \
      TransactionId, \
      LCurrency.Short_Name, \
      Self \
    ) \
    THEN ORDER BY ASC InvoiceId;' % AddFilter


  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('BeginDate', int(aBeginDate))
  oql.SetParameterValueByName('EndDate', int(aEndDate))
  oql.SetParameterValueByName('BranchCode', aBranchCode)

  oql.ApplyParamValues()

  oql.active = 1
  
  return oql.rawresult


def GetExcelInvoice(config,parameters,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['FileName',''],)
    
  
  try:
    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate')
    pathtemplates = config.HomeDir + 'templates\\'
    pathresult = corporate.GetUserHomeDir() + '\\'

    resFilename  = pathresult + 'InvoiceList.xls'
    rec = parameters.FirstRecord
    aBeginDate = rec.BeginDate
    aEndDate = rec.EndDate
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
    aIsShowPaidInvoice = rec.IsShowPaidInvoice

    res  = GetDataInvoice(config,aBeginDate,aEndDate,aBranchCode,aIsShowPaidInvoice)


    workbook = pyFlexcel.Open(pathtemplates + 'tplInvoiceList.xls')
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


      workbook.SetCellValue(2,2,config.SecurityContext.GetUserInfo()[5])
      workbook.SetCellValue(3,2,StrTanggal)
      
      row = 6
      while not res.Eof:
        workbook.SetCellValue(row,1,res.InvoiceNo)
        tglInvoice = config.FormatDateTime('dd-mm-yyyy',timeutils.AsTDateTime(config, res.InvoiceDate))
        workbook.SetCellValue(row,2,tglInvoice)
        workbook.SetCellValue(row,3,res.InvoiceAmount)
        workbook.SetCellValue(row,4,res.InvoicePaymentStatus)
        workbook.SetCellValue(row,5,res.Full_Name)
        workbook.SetCellValue(row,6,res.AccountName)
        workbook.SetCellValue(row,7,res.Description)

        row += 1
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
    
def DeleteInvoice(config,parameters,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['StreamName',''],)

  config.BeginTransaction()
  try:
    InvoiceId = parameters.FirstRecord.InvoiceId
    helper = phelper.PObjectHelper(config)

    # Get Invoice Data
    oInvoice = helper.GetObject('InvoiceProduct',InvoiceId)
    oInvoice.Delete()
    
    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message =str(sys.exc_info()[1])
  
def PrintInvoice(config,parameters,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['StreamName',''],)


  try:
    InvoiceId = parameters.FirstRecord.InvoiceId

    helper = phelper.PObjectHelper(config)


    # Get Invoice Data
    oInvoice = helper.GetObject('InvoiceProduct',InvoiceId)
    InvoiceData = oInvoice.GenerateInvoicePrintData()

    corporate = helper.CreateObject('Corporate')
    sBaseFileName = "printinvoice.rtf"
    sFileName = corporate.GetUserHomeDir() + "\\" + sBaseFileName
    oFile = open(sFileName,'w')
    try:
      oFile.write(InvoiceData)
    finally:
      oFile.close()

    sw = returns.AddStreamWrapper()
    sw.LoadFromFile(sFileName)
    sw.MIMEType = 'application/msword'
    sw.Name = 'Invoice'

    status.StreamName = sw.Name

  except:
    status.Is_Err = 1
    status.Err_Message =str(sys.exc_info()[1])
