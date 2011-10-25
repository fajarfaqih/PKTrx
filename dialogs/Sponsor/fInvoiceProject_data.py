import com.ihsan.foundation.pobjecthelper as phelper
import sys


def AsDateTime(config,tdate):
  utils = config.ModLibUtils
  return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

def FormOnSetDataEx(uideflist,parameters):
  config = uideflist.config

  if parameters.DatasetCount == 0 : return 1
  
  param = parameters.FirstRecord
  
  helper = phelper.PObjectHelper(config)
  DisbId = param.DisbId
  
  oProjectDisb = helper.GetObject('ProjectSponsorDisbursement',DisbId)
  
  recInvoice = uideflist.uipInvoice.Dataset.AddRecord()

  recInvoice.InvoiceDate = AsDateTime(config,oProjectDisb.DisbDatePlan)
  SponsorId = oProjectDisb.LProjectSponsor.SponsorId
  
  oDonor = helper.CreateObject('ExtDonor')
  oDonor.GetData(SponsorId)
  recInvoice.SponsorName = oDonor.full_name
  recInvoice.SponsorAddress = oDonor.address
  #recInvoice.TransactionItemId = TransactionItemId
  recInvoice.ProgramName = oProjectDisb.LProjectSponsor.LProjectAccount.AccountName
  recInvoice.Amount = oProjectDisb.DisbAmountPlan
  
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


    
    filename = GenerateInvoice(config,param)
    
    sw = returns.AddStreamWrapper()
    sw.Name = 'Invoice'
    sw.LoadFromFile(filename)
    sw.MIMEType = 'application/msword' #config.AppObject.GetMIMETypeFromExtension(filename)

    status.StreamName = sw.Name

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
  dataInvoice['QTY'] = 1
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

  
