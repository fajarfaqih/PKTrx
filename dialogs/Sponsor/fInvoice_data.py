import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormOnSetDataEx(uideflist,parameters):
  config = uideflist.config

  if parameters.DatasetCount == 0 : return 1
  
  param = parameters.FirstRecord
  
  helper = phelper.PObjectHelper(config)
  TransactionItemId = param.TransactionItemId
  
  oSTProgram = helper.GetObject('SponsorTransactionProgram',TransactionItemId)
  
  recInvoice = uideflist.uipInvoice.Dataset.AddRecord()
  
  recInvoice.InvoiceDate = int(config.Now())
  
  oDonor = helper.CreateObject('ExtDonor')
  oDonor.GetData(oSTProgram.SponsorId)
  recInvoice.SponsorName = oDonor.full_name
  recInvoice.SponsorAddress = oDonor.address
  recInvoice.TransactionItemId = TransactionItemId
  recInvoice.ProgramName = oSTProgram.LTransaction.LFinancialAccount.AccountName
  recInvoice.Amount = oSTProgram.LTransaction.Amount
  
def PrintInvoice(config,parameters,returns):
  status = returns.CreateValues(
      ['Is_Err',0],
      ['Err_Message',''],
      ['StreamName',''],
  )

  config.BeginTransaction()
  try:
    helper = phelper.PObjectHelper(config)

    param = parameters.FirstRecord

    oSTProgram = helper.GetObject('SponsorTransactionProgram',param.TransactionItemId)

    filename = GenerateInvoice(config,param)

    sw = returns.AddStreamWrapper()
    sw.Name = 'Invoice'
    sw.LoadFromFile(filename)
    sw.MIMEType = 'application/msword' #config.AppObject.GetMIMETypeFromExtension(filename)

    status.StreamName = sw.Name

    oSTProgram.InvoiceStatus = 'T'
    oSTProgram.InvoiceNo = param.InvoiceNo
    oSTProgram.InvoiceDate = param.InvoiceDate

    oInvoice = helper.CreatePObject('Invoice')
    oInvoice.InvoiceNo = param.InvoiceNo
    oInvoice.InvoiceDate = param.InvoiceDate
    oInvoice.InvoiceTermDate = param.TermDate
    oInvoice.InvoiceAmount = param.Amount or 0.0
    oInvoice.InvoiceAddress = param.SponsorAddress
    oInvoice.InvoiceBankName = param.BankName
    oInvoice.InvoiceBankAccounNumber = param.BankAccount
    oInvoice.InvoiceBankAccounName = param.BankAccountName
    oInvoice.InvoiceOfficername = param.SignName
    oInvoice.InvoiceOfficerPosition = param.JobPosition
    
    BranchCode = config.SecurityContext.GetUserInfo()[4]
    BatchNo = 'SYS-BALANCE-%s' % BranchCode

    oBatch = helper.GetObjectByNames(
       'TransactionBatch',
         {'BatchNo' : BatchNo,
          'BranchCode' : BranchCode,
         })
  if oBatch.isnull:
    oBatch = helper.CreatePObject('TransactionBatch')
    oBatch.BatchNo = BatchNo
    oBatch.BranchCode = BranchCode
    oBatch.BatchDate = config.ModLibUtils.EncodeDate(2010,12,31)
    oBatch.Inputer = config.SecurityContext.InitUser
    oBatch.Description = 'Saldo Awal'
    oBatch.IsPosted = 'T'
    oBatch.BatchTag = 'SYS'
  # end if

  return oBatch
    oInvoice.CreateTransaction()
    
    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

def GenerateInvoice(config,param):
  helper = phelper.PObjectHelper(config)

  # Get Tools
  ToolsConvert = helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Total = param.Amount or 0.0

  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = '000',
            NamaMataUang = 'Rupiah')

  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')

  # Get Template
  PrintHelper = helper.CreateObject('PrintHelper')
  #templateInvoice = PrintHelper.LoadHtmTemplate('tplinvoice')
  templateInvoice = PrintHelper.LoadRtfTemplate('tplInvoice')

  NamaLembaga = helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataInvoice = {}
  dataInvoice['INVOICENO'] = param.InvoiceNo
  dataInvoice['CUSTOMERNAME'] = param.SponsorName
  dataInvoice['CUSTOMERADDRESS'] = param.SponsorAddress
  dataInvoice['INVOICEDATE'] = config.FormatDateTime('mmm,dd yyyy',param.InvoiceDate)
  dataInvoice['TERMDATE'] = config.FormatDateTime('mmm,dd yyyy',param.TermDate)
  dataInvoice['SAYS'] = Terbilang[0] + ' ' + Terbilang[1]
  dataInvoice['AMOUNT'] = 'Rp ' + config.FormatFloat('#,##0.00',Total)
  dataInvoice['QTY'] = '1'
  dataInvoice['DESCRIPTION'] = param.ProgramName
  dataInvoice['BANKNAME'] = param.BankName
  dataInvoice['BANKACCOUNTNO'] = param.BankAccount
  dataInvoice['BANKACCOUNTNAME'] = param.BankAccountName
  dataInvoice['SIGNNAME'] = param.SignName
  dataInvoice['JOBPOSITION'] = param.JobPosition


  Invoice = ''

  corporate = helper.CreateObject('Corporate')

  Invoice  += templateInvoice % dataInvoice

  sBaseFileName = "printinvoice.rtf"
  sFileName = corporate.GetUserHomeDir() + sBaseFileName
  oFile = open(sFileName,'w')
  try:
    oFile.write(Invoice)
  finally:
    oFile.close()

  return sFileName
