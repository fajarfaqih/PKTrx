REVERSE_MNEMONIC = {'D':'C','C':'D'}

def GetKwitansiDonor(oTran):
#   LsTemplate = {
#     'EN' : {
#        ['D','1'] : 'KwitansiDonorEN',
#        ['D','2'] : 'KwitansiDonorENBackground',
#        ['D','1'] : 'KwitansiDonorENA5',
#        ['D','2'] : 'KwitansiDonorENBackgroundA5'
#       },
#     'INA' : {
#        ['D','1'] : 'KwitansiDonor',
#        ['D','2'] : 'KwitansiDonorBackground',
#        ['I','1'] : 'KwitansiDonorA5',
#        ['I','2'] : 'KwitansiDonorBackgroundA5',
#       },
#   }
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency  
  Total = oTran.Amount or 0.0

  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)          
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang

  # Get Marketer Name  
  MarketerName = ''  
  if oTran.MarketerId not in ['',None,0]:
    MarketerName = oTran.LMarketer.Full_Name
  
  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPenerimaan')
  
  TemplateName = 'KwitansiDonorFix'
  if oTran.CurrencyCode != '000':
    TemplateName = 'KwitansiDonorFixEN'

  templateKwitansi = PrintHelper.LoadRtfTemplate(TemplateName)
  
  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
  UserInfo = oTran.Config.SecurityContext.GetUserInfo()
  #
  oDonor = oTran.GetDonor()
  DonorNo = oDonor.donor_no
  Name = oDonor.full_name
  Address = oDonor.address
  
  aAddress = ['','']
  if len(Address) > 0 :  
    aAddress = ToolsConvert.Divider(Address,50)      
    if len(aAddress) == 1 : aAddress.append('')
  
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['IDDONOR'] = DonorNo
  dataKwitansi['RECEIVEDFROM'] = Name
  dataKwitansi['ALAMAT1'] = aAddress[0]
  dataKwitansi['ALAMAT2'] = aAddress[1]
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['KODEAKUN'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['MARKETER'] = MarketerName
  dataKwitansi['TELP'] = ''
  
  # Set Data Info Cabang
  oBranch = oTran.Helper.GetObject('Branch',UserInfo[4])
  if oBranch.isnull : raise 'PERINGATAN','Data Cabang tidak ditemukan'
  dataKwitansi['CABANGNAMA'] = oBranch.BranchName or ''
  dataKwitansi['CABANGALAMAT'] = oBranch.Branch_Address or ''
  dataKwitansi['CABANGTELEPON'] = oBranch.Branch_Phone or ''
  dataKwitansi['CABANGFAX'] = oBranch.Branch_Fax or ''
  dataKwitansi['CABANGREK1'] = "- %s" % oBranch.Branch_BankAccount1 or ''
  Account2 = ''
  if oBranch.Branch_BankAccount2 not in ['',None] :
    Account2 = "- %s" % oBranch.Branch_BankAccount2 
  dataKwitansi['CABANGREK2'] = Account2
  dataKwitansi['KOTA'] = oBranch.Location or ''

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  rowdetail = 0
  #while not oItems.EndOfList:
  #  itemElmt = oItems.CurrentElement
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        
  
  aRate = oTran.Rate
  if aRate == 0 : aRate = 1 
  oRes = oTran.Config.CreateSQL(aSQLText).RawResult

  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
          
    if oItem.MutationType == 'C':
      rowdetail += 1
      DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
           'LINE' : '-' , #str(rowdetail),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description[:40],
           'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount/aRate),
           'CURRSYMBOL' : Currency.Symbol,
        }      
    else:
      dataKwitansi['NAMAKAS'] = oItem.RefAccountName 
      dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
#       oItems.Next()
    oRes.Next()
  #-- while
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)
  maxrowdetail = 5
  
  for row in range(maxrowdetail - rowdetail):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE
  
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiAssetDonor(oTran):
#   LsTemplate = {
#     'EN' : {
#        ['D','1'] : 'KwitansiDonorEN',
#        ['D','2'] : 'KwitansiDonorENBackground',
#        ['D','1'] : 'KwitansiDonorENA5',
#        ['D','2'] : 'KwitansiDonorENBackgroundA5'
#       },
#     'INA' : {
#        ['D','1'] : 'KwitansiDonor',
#        ['D','2'] : 'KwitansiDonorBackground',
#        ['I','1'] : 'KwitansiDonorA5',
#        ['I','2'] : 'KwitansiDonorBackgroundA5',
#       },
#   }
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency  
  Total = oTran.Amount or 0.0

  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)          
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang

  # Get Marketer Name  
  MarketerName = ''  
  if oTran.MarketerId not in ['',None,0]:
    MarketerName = oTran.LMarketer.Full_Name
  
  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPenerimaan')
  
  TemplateName = 'KwitansiDonorFix'
  if oTran.CurrencyCode != '000':
    TemplateName = 'KwitansiDonorFixEN'

  templateKwitansi = PrintHelper.LoadRtfTemplate(TemplateName)
  
  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
  UserInfo = oTran.Config.SecurityContext.GetUserInfo()
  #
  oDonor = oTran.GetDonor()
  DonorNo = oDonor.donor_no
  Name = oDonor.full_name
  Address = oDonor.address
  
  aAddress = ['','']
  if len(Address) > 0 :  
    aAddress = ToolsConvert.Divider(Address,50)      
    if len(aAddress) == 1 : aAddress.append('')
  
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['IDDONOR'] = DonorNo
  dataKwitansi['RECEIVEDFROM'] = Name
  dataKwitansi['ALAMAT1'] = aAddress[0]
  dataKwitansi['ALAMAT2'] = aAddress[1]
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['KODEAKUN'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['MARKETER'] = oTran.PaidTo #MarketerName
  dataKwitansi['TELP'] = ''
  
  # Set Data Info Cabang
  oBranch = oTran.Helper.GetObject('Branch',UserInfo[4])
  if oBranch.isnull : raise 'PERINGATAN','Data Cabang tidak ditemukan'
  dataKwitansi['CABANGNAMA'] = oBranch.BranchName or ''
  dataKwitansi['CABANGALAMAT'] = oBranch.Branch_Address or ''
  dataKwitansi['CABANGTELEPON'] = oBranch.Branch_Phone or ''
  dataKwitansi['CABANGFAX'] = oBranch.Branch_Fax or ''
  dataKwitansi['CABANGREK1'] = "- %s" % oBranch.Branch_BankAccount1 or ''
  Account2 = ''
  if oBranch.Branch_BankAccount2 not in ['',None] :
    Account2 = "- %s" % oBranch.Branch_BankAccount2 
  dataKwitansi['CABANGREK2'] = Account2
  dataKwitansi['KOTA'] = oBranch.Location or ''

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  rowdetail = 0
  #while not oItems.EndOfList:
  #  itemElmt = oItems.CurrentElement
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        
  
  aRate = oTran.Rate
  if aRate == 0 : aRate = 1 
  oRes = oTran.Config.CreateSQL(aSQLText).RawResult

  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
          
    if oItem.MutationType == 'D':
      rowdetail += 1
      DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
           'LINE' : '-' , #str(rowdetail),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description[:40],
           'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount/aRate),
           'CURRSYMBOL' : Currency.Symbol,
        }
    #endif
#       oItems.Next()
    oRes.Next()
  #-- while
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)
  maxrowdetail = 5
  
  for row in range(maxrowdetail - rowdetail):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE
  
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiInvoice(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPenerimaan')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPenerimaan')

  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
  #
  Name,Address = oTran.GetDataDonor()
  aAddress = ['','']
  if len(Address) > 0 :  
    aAddress = ToolsConvert.Divider(Address,50)      
    if len(aAddress) == 1 : aAddress.append('')
  
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['RECEIVEDFROM'] = Name
  dataKwitansi['ALAMAT1'] = aAddress[0]
  dataKwitansi['ALAMAT2'] = aAddress[1]
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['KODEAKUN'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  dataKwitansi['KETERANGAN'] = oTran.Description

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  i = 1
  #while not oItems.EndOfList:
  #  itemElmt = oItems.CurrentElement
  #aSQLText = " select transactionitemid from transactionitem \
  #                 where transactionid=%d " % oTran.TransactionId        

  aRate = oTran.Rate
  #oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  
  
  oInvoice = oTran.Helper.GetObjectByNames('InvoiceProduct', 
          {'TransactionId' : oTran.TransactionId}
      ).CastToLowestDescendant()
      
  dataKwitansi['NAMAKAS'] = "%s %s " % (oInvoice.InvoiceBankName,oInvoice.InvoiceBankAccountNumber) 
  dataKwitansi['KODEAKUN'] = ''    
  
  oItem = oTran.Helper.GetObjectByNames('TransactionItem', 
          {'TransactionId' : oTran.TransactionId}
      ).CastToLowestDescendant()
  
  DETAIL += '%(LINE)2s      %(NOACCOUNT)-10s   %(DESCRIPTION)-50s   %(CURRSYMBOL)-2s %(AMOUNT)25s \n\\par ' % {
           'LINE' : str(i),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description,
           'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount/aRate),
           'CURRSYMBOL' : Currency.Symbol,
        }

  dataKwitansi['DETAIL'] = DETAIL

  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiInvoiceNew(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency  
  Total = oTran.Amount or 0.0

  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)          
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPenerimaan')
  
  TemplateName = 'KwitansiDonorFix'
  if oTran.CurrencyCode != '000':
    TemplateName = 'KwitansiDonorFixEN'

  templateKwitansi = PrintHelper.LoadRtfTemplate(TemplateName)
  
  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
  UserInfo = oTran.Config.SecurityContext.GetUserInfo()
  
  # Get Invoice
  oInvoice = oTran.Helper.GetObjectByNames('InvoiceProduct', 
          {'TransactionId' : oTran.TransactionId}
      ).CastToLowestDescendant()

  # Get Data donor
  oSponsor = oInvoice.LSponsor
  DonorNo = oSponsor.Donor_No
  Name = oSponsor.full_name
  Address = oSponsor.address
  
  aAddress = ['','']
  if len(Address) > 0 :  
    aAddress = ToolsConvert.Divider(Address,50)      
    if len(aAddress) == 1 : aAddress.append('')
  
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['IDDONOR'] = DonorNo
  dataKwitansi['RECEIVEDFROM'] = Name
  dataKwitansi['ALAMAT1'] = aAddress[0]
  dataKwitansi['ALAMAT2'] = aAddress[1]
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['KODEAKUN'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['MARKETER'] = oInvoice.InvoiceContactPerson
  dataKwitansi['TELP'] = ''
  
  # Set Data Info Cabang
  oBranch = oTran.Helper.GetObject('Branch',UserInfo[4])
  if oBranch.isnull : raise 'PERINGATAN','Data Cabang tidak ditemukan'
  dataKwitansi['CABANGNAMA'] = oBranch.BranchName or ''
  dataKwitansi['CABANGALAMAT'] = oBranch.Branch_Address or ''
  dataKwitansi['CABANGTELEPON'] = oBranch.Branch_Phone or ''
  dataKwitansi['CABANGFAX'] = oBranch.Branch_Fax or ''
  dataKwitansi['CABANGREK1'] = "- %s" % oBranch.Branch_BankAccount1 or ''
  Account2 = ''
  if oBranch.Branch_BankAccount2 not in ['',None] :
    Account2 = "- %s" % oBranch.Branch_BankAccount2 
  dataKwitansi['CABANGREK2'] = Account2
  dataKwitansi['KOTA'] = oBranch.Location or ''

  DETAIL = ''
  
  dataKwitansi['NAMAKAS'] = "%s %s " % (oInvoice.InvoiceBankName,oInvoice.InvoiceBankAccountNumber)
  dataKwitansi['KODEAKUN'] = ''
  
  oItem = oTran.Helper.GetObjectByNames('TransactionItem', 
          {'TransactionId' : oTran.TransactionId}
      ).CastToLowestDescendant()
  
  aRate = oTran.Rate
  if oItem.CurrencyCode != oTran.CurrencyCode :
    Amount = oItem.Amount/aRate
  else:
    Amount = oItem.Amount  
  # end if

  DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
           'LINE' : '-' , #str(rowdetail),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oInvoice.LProductAccount.AccountName, #oItem.Description[:40],
           'AMOUNT' :  config.FormatFloat('#,##0.00',Amount),
           'CURRSYMBOL' : Currency.Symbol,
        } 
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)
  for row in range(4):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE
  
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiInvoiceNew_OLD(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPenerimaan')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPenerimaanNew')

  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
  #
  Name,Address = oTran.GetDataDonor()
  aAddress = ['','']
  if len(Address) > 0 :  
    aAddress = ToolsConvert.Divider(Address,50)      
    if len(aAddress) == 1 : aAddress.append('')
  
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['RECEIVEDFROM'] = Name
  dataKwitansi['ALAMAT1'] = aAddress[0]
  dataKwitansi['ALAMAT2'] = aAddress[1]
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['KODEAKUN'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  dataKwitansi['KOTA'] = oTran.Config.SecurityContext.GetUserInfo()[5]
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['TELP'] = ''

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  i = 1
  #while not oItems.EndOfList:
  #  itemElmt = oItems.CurrentElement
  #aSQLText = " select transactionitemid from transactionitem \
  #                 where transactionid=%d " % oTran.TransactionId        

  aRate = oTran.Rate
  #oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  
  
  oInvoice = oTran.Helper.GetObjectByNames('InvoiceProduct', 
          {'TransactionId' : oTran.TransactionId}
      ).CastToLowestDescendant()
      
  dataKwitansi['NAMAKAS'] = "%s %s " % (oInvoice.InvoiceBankName,oInvoice.InvoiceBankAccountNumber)
  dataKwitansi['KODEAKUN'] = ''
  
  oItem = oTran.Helper.GetObjectByNames('TransactionItem', 
          {'TransactionId' : oTran.TransactionId}
      ).CastToLowestDescendant()
  
  DETAIL += '%(LINE)2s      %(NOACCOUNT)-10s   %(DESCRIPTION)-50s   %(CURRSYMBOL)-2s %(AMOUNT)25s \n\\par ' % {
           'LINE' : str(i),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description,
           'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount/aRate),
           'CURRSYMBOL' : Currency.Symbol,
        }

  dataKwitansi['DETAIL'] = DETAIL

  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)
  
def GetKwitansiPenerimaan(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Total = oTran.Amount or 0.0
  Currency = oTran.LCurrency
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')

  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPenerimaan')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPenerimaan')

  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
  #
  Name,Address = oTran.GetDataDonor()
  aAddress = ['','']
  if len(Address) > 0 :  
    aAddress = ToolsConvert.Divider(Address,50)      
    if len(aAddress) == 1 : aAddress.append('')
  
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['RECEIVEDFROM'] = Name
  dataKwitansi['ALAMAT1'] = aAddress[0]
  dataKwitansi['ALAMAT2'] = aAddress[1]
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['KODEAKUN'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  dataKwitansi['KETERANGAN'] = oTran.Description

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  i = 1
  #while not oItems.EndOfList:
  #  itemElmt = oItems.CurrentElement
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  aRate = oTran.Rate
  oRes = oTran.Config.CreateSQL(aSQLText).RawResult

  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
           
    if oItem.CurrencyCode != oTran.CurrencyCode :
      Amount = oItem.Amount/aRate
    else:
      Amount = oItem.Amount  
    # end if
           
    if oItem.MutationType == 'C':
      DETAIL += '%(LINE)2s      %(NOACCOUNT)-10s   %(DESCRIPTION)-50s   %(CURRSYMBOL)-2s %(AMOUNT)25s \n\\par ' % {
           'LINE' : str(i),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description,
           'AMOUNT' :  config.FormatFloat('#,##0.00',Amount),
           'CURRSYMBOL' : Currency.Symbol,
        }
      i+=1
    else:
      dataKwitansi['NAMAKAS'] = oItem.RefAccountName 
      dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
#       oItems.Next()
    oRes.Next()
  #-- while

  dataKwitansi['DETAIL'] = DETAIL

  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiPenerimaanNew(oTran):
  config = oTran.Config
  config.FlushUpdates()
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')
  
  # Set Terbilang
  Total = oTran.Amount or 0.0
  Currency = oTran.LCurrency
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')

  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang
  oBranch = oTran.Helper.GetObject('Branch',oTran.Config.SecurityContext.GetUserInfo()[4])
  if oBranch.isnull : raise 'PERINGATAN','Data Cabang tidak ditemukan'

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPenerimaan')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPenerimaanNew')

  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
  #
  Name,Address = oTran.GetDataDonor()
  aAddress = ['','']
  if len(Address) > 0 :  
    aAddress = ToolsConvert.Divider(Address,50)      
    if len(aAddress) == 1 : aAddress.append('')
  
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['RECEIVEDFROM'] = Name
  dataKwitansi['ALAMAT1'] = aAddress[0]
  dataKwitansi['ALAMAT2'] = aAddress[1]
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['KODEAKUN'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  dataKwitansi['KOTA'] = oBranch.Location or ''
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['TELP'] = ''

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  rowdetail = 0
  #while not oItems.EndOfList:
  #  itemElmt = oItems.CurrentElement
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  
  aRate = oTran.Rate
  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
           
    if oItem.MutationType == 'C':
      rowdetail += 1
      
      if oItem.CurrencyCode != oTran.CurrencyCode :
        Amount = oItem.Amount/aRate
      else:
        Amount = oItem.Amount
      # end if

      DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
           'LINE' : '-' , #str(rowdetail),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description[:40],
           'AMOUNT' :  config.FormatFloat('#,##0.00', Amount),
           'CURRSYMBOL' : Currency.Symbol,
        }
    else:
      dataKwitansi['NAMAKAS'] = oItem.RefAccountName 
      dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
#       oItems.Next()
    oRes.Next()
  #-- while
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)
  maxrowdetail = 5
    
  for row in range(maxrowdetail - rowdetail):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE

  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)
  
def GetKwitansiPengembalianUangMuka(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = '000',
            NamaMataUang = Currency.Symbol_Says)
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')

  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
#     templateKwitansi = PrintHelper.LoadTemplate('KwitansiPenerimaan')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPenerimaan')

  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['RECEIVEDFROM'] = oTran.ReceivedFrom
  dataKwitansi['ALAMAT1'] = ''
  dataKwitansi['ALAMAT2'] = ''
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['KODEAKUN'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  i = 1
  #while not oItems.EndOfList:
  #  itemElmt = oItems.CurrentElement
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  
  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
           
    if oItem.MutationType == 'D':
      if oItem.CurrencyCode != oTran.CurrencyCode :
        Amount = oItem.Amount / oTran.Rate
      else:
        Amount = oItem.Amount
         
      DETAIL += '%(LINE)2s      %(NOACCOUNT)-10s   %(DESCRIPTION)-50s   %(CURRSYMBOL)-2s %(AMOUNT)25s \n\\par ' % {
           'LINE' : str(i),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description,
           'AMOUNT' :  config.FormatFloat('#,##0.00', Amount),
           'CURRSYMBOL' : Currency.Symbol,
        }
      if oItem.IsA('AccountTransactionItem'):
        if oItem.LFinancialAccount.CastToLowestDescendant().IsA('CashAccount') :
          dataKwitansi['NAMAKAS'] = oItem.RefAccountName
          dataKwitansi['KODEAKUN'] = oItem.AccountCode
      i += 1
      
    #else:
    #  dataKwitansi['NAMAKAS'] = oItem.RefAccountName 
    #  dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
    oRes.Next()
  #-- while
  
  # Jika Nama Kas Tidak ada dalam detil defaultnya adalah kas cabang
  if dataKwitansi['NAMAKAS'] == '':
    oBranchCash = oTran.Helper.GetObjectByNames('BranchCash',
        { 'BranchCode' : oTran.Config.SecurityContext.GetUserInfo()[4],
          'CurrencyCode' : '000',
        }
    )
    if oBranchCash.isnull :
      raise '','Data Kas Cabang tidak ditemukan'
    dataKwitansi['NAMAKAS'] = oBranchCash.AccountName
    dataKwitansi['KODEAKUN'] = oBranchCash.GetAccountInterface()
  dataKwitansi['DETAIL'] = DETAIL

  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)
      
def GetKwitansiPengeluaran(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = '000',
            NamaMataUang = Currency.Symbol_Says)
  
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')

  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPengeluaran')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPengeluaran')

  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['PAIDTO'] = oTran.PaidTo[:30]
  dataKwitansi['ALAMAT1'] = ''
  dataKwitansi['ALAMAT2'] = ''
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.ReceivedFrom #config.SecurityContext.InitUser[:15]
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  i = 1
  #while not oItems.EndOfList:
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  aRate = oTran.Rate
  oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
    
    if oItem.CurrencyCode == oTran.CurrencyCode :
      aAmount = oItem.Amount
    else :
      if oItem.CurrencyCode == '000' :
        aAmount = oItem.Amount / aRate
      else:
        aAmount = oItem.Amount * oItem.Rate
      # end if 
    # end if
              
    if oItem.MutationType == 'D':
      DETAIL += '%(LINE)2s      %(NOACCOUNT)-10s   %(DESCRIPTION)-50s   %(CURRSYMBOL)-2s %(AMOUNT)25s \n\\par ' % {
           'LINE' : str(i),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description,
           'AMOUNT' :  config.FormatFloat('#,##0.00',aAmount),
           'CURRSYMBOL' : Currency.Symbol,             
        }
      i+=1
    else:        
      dataKwitansi['NAMAKAS'] = oItem.RefAccountName[:25]
      dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
    oRes.Next()
  #-- while
  
  dataKwitansi['DETAIL'] = DETAIL
  
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiPengeluaranNew(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = '000',
            NamaMataUang = Currency.Symbol_Says)
  
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang
  oBranch = oTran.Helper.GetObject('Branch',oTran.Config.SecurityContext.GetUserInfo()[4])

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPengeluaran')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPengeluaranNew')
  
  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['PAIDTO'] = oTran.PaidTo[:60]
  dataKwitansi['ALAMAT1'] = ''
  dataKwitansi['ALAMAT2'] = ''
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.ReceivedFrom #config.SecurityContext.InitUser[:15]
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KOTA'] = oBranch.Location
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  
  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  rowdetail = 0
  #while not oItems.EndOfList:
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  aRate = oTran.Rate
  oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
    
    if oItem.CurrencyCode == oTran.CurrencyCode :
      aAmount = oItem.Amount
    else :
      if oItem.CurrencyCode == '000' :
        aAmount = oItem.Amount / aRate
      else:
        aAmount = oItem.Amount * oItem.Rate
      # end if 
    # end if

    if oItem.MutationType == 'D':
      rowdetail += 1    
      DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
           'LINE' : '-' , #str(rowdetail),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description[:40],
           'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount/aRate),
           'CURRSYMBOL' : Currency.Symbol,
        }
    else:        
      dataKwitansi['NAMAKAS'] = oItem.RefAccountName[:25]
      dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
    oRes.Next()
  #-- while
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)
  maxrowdetail = 5
  
  for row in range(maxrowdetail - rowdetail):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE
    
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiPembelianAsetNew(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = '000',
            NamaMataUang = Currency.Symbol_Says)
  
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang
  oBranch = oTran.Helper.GetObject('Branch',oTran.Config.SecurityContext.GetUserInfo()[4])

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPengeluaran')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPengeluaranNew')
  
  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['PAIDTO'] = oTran.PaidTo[:60]
  dataKwitansi['ALAMAT1'] = ''
  dataKwitansi['ALAMAT2'] = ''
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.ReceivedFrom #config.SecurityContext.InitUser[:15]
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KOTA'] = oBranch.Location
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  
  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  rowdetail = 0
  #while not oItems.EndOfList:
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  aRate = oTran.Rate
  oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
    
    if oItem.CurrencyCode == oTran.CurrencyCode :
      aAmount = oItem.Amount
    else :
      if oItem.CurrencyCode == '000' :
        aAmount = oItem.Amount / aRate
      else:
        aAmount = oItem.Amount * oItem.Rate
      # end if 
    # end if

    if oItem.MutationType == 'D' and oItem.TransactionItemType == 'G':
      rowdetail += 1    
      DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
           'LINE' : '-' , #str(rowdetail),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description[:40],
           'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount/aRate),
           'CURRSYMBOL' : Currency.Symbol,
        }
    else:
      dataKwitansi['NAMAKAS'] = oItem.RefAccountName[:25]
      dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
    oRes.Next()
  #-- while
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)
  maxrowdetail = 5
  for row in range(maxrowdetail - rowdetail):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE

  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiPengembalianUangMukaNew(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)
  
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang
  oBranch = oTran.Helper.GetObject('Branch',oTran.Config.SecurityContext.GetUserInfo()[4])
  if oBranch.isnull : raise 'PERINGATAN','Data Cabang tidak ditemukan'

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPengeluaran')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPengeluaranNew')
  
  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['PAIDTO'] = oTran.PaidTo[:30]
  dataKwitansi['RECEIVEDFROM'] = oTran.ReceivedFrom[:30]
  dataKwitansi['ALAMAT1'] = ''
  dataKwitansi['ALAMAT2'] = ''
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo#config.SecurityContext.InitUser[:15]
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KOTA'] = oBranch.Location
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  
  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  rowdetail = 0
  #while not oItems.EndOfList:
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  aRate = oTran.Rate
  oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
    
    if oItem.CurrencyCode == oTran.CurrencyCode :
      aAmount = oItem.Amount
    else :
      if oItem.CurrencyCode == '000' :
        aAmount = oItem.Amount / aRate
      else:
        aAmount = oItem.Amount * oItem.Rate
      # end if 
    # end if

    if oItem.MutationType == 'D':
      rowdetail += 1    
      DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
           'LINE' : '-' , #str(rowdetail),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description[:40],
           'AMOUNT' :  config.FormatFloat('#,##0.00', aAmount),
           'CURRSYMBOL' : Currency.Symbol,
        }
    #else:        
    #  dataKwitansi['NAMAKAS'] = oItem.RefAccountName[:25]
    #  dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
    oRes.Next()
  #-- while
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)
  maxrowdetail = 5
  
  for row in range(maxrowdetail - rowdetail):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE
    
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiInvestasiKembaliNew(oTran):
  config = oTran.Config
  config.FlushUpdates()
  helper = oTran.Helper
  
  # Get Tools
  ToolsConvert = helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = oTran.CurrencyCode,
            NamaMataUang = Currency.Symbol_Says)
  
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  #corporate = helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang
  oBranch = helper.GetObject('Branch', oTran.BranchCode)
  if oBranch.isnull : raise 'PERINGATAN','Data Cabang tidak ditemukan'

  # Get Template
  PrintHelper = helper.CreateObject('PrintHelper')
  #templateKwitansi = PrintHelper.LoadTemplate('KwitansiPengeluaran')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiInvestasiKembaliNew')
  
  NamaLembaga = helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['PAIDTO'] = oTran.PaidTo[:30]
  dataKwitansi['RECEIVEDFROM'] = oTran.ReceivedFrom[:30]
  dataKwitansi['ALAMAT1'] = ''
  dataKwitansi['ALAMAT2'] = ''
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.PaidTo#config.SecurityContext.InitUser[:15]
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KOTA'] = oBranch.Location or ''
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  dataKwitansi['INVESTEENAME'] = oTran.ReceivedFrom
  
  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  rowdetail = 0
  #while not oItems.EndOfList:
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  aRate = oTran.Rate
  oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  while not oRes.Eof:
    oItem = helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
    
    if oItem.CurrencyCode == oTran.CurrencyCode :
      aAmount = oItem.Amount
    else :
      if oItem.CurrencyCode == '000' :
        aAmount = oItem.Amount / aRate
      else:
        aAmount = oItem.Amount * oItem.Rate
      # end if 
    # end if

    if oItem.MutationType == 'D':
      rowdetail += 1    
      DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
           'LINE' : '-' , #str(rowdetail),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description[:40],
           'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount/aRate),
           'CURRSYMBOL' : Currency.Symbol,
        }
    #else:        
    #  dataKwitansi['NAMAKAS'] = oItem.RefAccountName[:25]
    #  dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
    oRes.Next()
  #-- while
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)
  maxrowdetail = 5
  
  for row in range(maxrowdetail - rowdetail):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE
    
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)
  
def GetKwitansiPiutang(oTran,EmpMutationType):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = '000',
            NamaMataUang = Currency.Symbol_Says)
  
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  UserInfo = oTran.Config.SecurityContext.GetUserInfo()
  
  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  if EmpMutationType == 'D' :
    templateFileName = 'KwitansiPiutangNew'
  else:
    templateFileName = 'KwitansiBayarPiutangNew'
    
  templateKwitansi = PrintHelper.LoadRtfTemplate(templateFileName)
  
  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  if EmpMutationType == 'D' :
    dataKwitansi['KASIR'] = oTran.ReceivedFrom[:30]
  else :
    dataKwitansi['KASIR'] = oTran.PaidTo[:30]
  # end if

  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  
  # Set Data Info Cabang
  oBranch = oTran.Helper.GetObject('Branch',UserInfo[4])
  if oBranch.isnull : raise 'PERINGATAN','Data Cabang tidak ditemukan'
  dataKwitansi['CABANGNAMA'] = oBranch.BranchName or ''
  dataKwitansi['CABANGALAMAT'] = oBranch.Branch_Address or ''
  dataKwitansi['CABANGTELEPON'] = oBranch.Branch_Phone or ''
  dataKwitansi['CABANGFAX'] = oBranch.Branch_Fax or ''
  dataKwitansi['CABANGREK1'] = "- %s" % oBranch.Branch_BankAccount1 or ''
  Account2 = ''
  if oBranch.Branch_BankAccount2 not in ['',None] :
    Account2 = "- %s" % oBranch.Branch_BankAccount2 
  dataKwitansi['CABANGREK2'] = Account2
  dataKwitansi['KOTA'] = oBranch.Location or ''
  
  DETAIL = ''
  oItem = oTran.Helper.GetObjectByNames(
        'TransactionItem', 
        {'MutationType' : EmpMutationType, 
         'TransactionId' : oTran.TransactionId}
    ).CastToLowestDescendant()
    
  DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
       'LINE' : '-' , #str(rowdetail),
       'NOACCOUNT' : oItem.AccountCode,
       'DESCRIPTION' : oItem.Description[:40],
       'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount),
       'CURRSYMBOL' : Currency.Symbol,
    }
  dataKwitansi['NAMADEBITUR'] = oItem.RefAccountName[:100]  
  
  oItem = oTran.Helper.GetObjectByNames(
        'TransactionItem', 
        {'MutationType' : REVERSE_MNEMONIC[EmpMutationType], 
         'TransactionId' : oTran.TransactionId}
    ).CastToLowestDescendant()

  dataKwitansi['NAMAKAS'] = oItem.RefAccountName[:25]
  dataKwitansi['KODEAKUN'] = oItem.AccountCode
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)  
  for row in range(4):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE
    
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)

def GetKwitansiTransferInternal(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = '000',
            NamaMataUang = Currency.Symbol_Says)
  
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')
  
  # Get Branch Info
  UserInfo = oTran.Config.SecurityContext.GetUserInfo()
  
  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiTransferInternalNew')
  
  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['KASIR'] = '      '
  dataKwitansi['USER_CETAK'] = UserInfo[4]
  dataKwitansi['INPUTER'] = oTran.Inputer
  # end if    
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol
  
  # Set Data Info Cabang
  oBranch = oTran.Helper.GetObject('Branch',UserInfo[4])
  if oBranch.isnull : raise 'PERINGATAN','Data Cabang tidak ditemukan'
  dataKwitansi['CABANGNAMA'] = oBranch.BranchName or ''
  dataKwitansi['CABANGALAMAT'] = oBranch.Branch_Address or ''
  dataKwitansi['CABANGTELEPON'] = oBranch.Branch_Phone or ''
  dataKwitansi['CABANGFAX'] = oBranch.Branch_Fax or ''
  dataKwitansi['CABANGREK1'] = "- %s" % oBranch.Branch_BankAccount1 or ''
  Account2 = ''
  if oBranch.Branch_BankAccount2 not in ['',None] :
    Account2 = "- %s" % oBranch.Branch_BankAccount2 
  dataKwitansi['CABANGREK2'] = Account2
  dataKwitansi['KOTA'] = oBranch.Location or ''
  
  DETAIL = ''
  oItem = oTran.Helper.GetObjectByNames(
        'TransactionItem', 
        {'MutationType' : 'C', 
         'TransactionId' : oTran.TransactionId}
    ).CastToLowestDescendant()
    
  DETAIL += 0 * ' '  + '%(LINE)2s %(NOACCOUNT)-6s  %(DESCRIPTION)-40s  %(CURRSYMBOL)-2s %(AMOUNT)20s \n\\par ' % {
       'LINE' : '-' , #str(rowdetail),
       'NOACCOUNT' : oItem.AccountCode,
       'DESCRIPTION' : oItem.Description[:40],
       'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount),
       'CURRSYMBOL' : Currency.Symbol,
    }
  dataKwitansi['KASSUMBER'] = oItem.RefAccountName[:100]
  
  oItem = oTran.Helper.GetObjectByNames(
        'TransactionItem', 
        {'MutationType' : 'D', 
         'TransactionId' : oTran.TransactionId}
    ).CastToLowestDescendant()

  dataKwitansi['KASTUJUAN'] = oItem.RefAccountName[:25]
  dataKwitansi['KODEAKUN'] = oItem.AccountCode
  
  # Tambah isi detail dengan sisa baris max detail (max 5 baris)  
  for row in range(4):
    DETAIL += '\n\\par '
  # end for
  
  # Tambah isi detail dengan garis pemisah dengan total  
  UNDERLINE =  54 * ' '  + '-----------------------'
  dataKwitansi['DETAIL'] = DETAIL + UNDERLINE
    
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)
  
def GetKwitansiPengeluaranUangMuka(oTran):
  config = oTran.Config
  config.FlushUpdates()
  
  # Get Tools
  ToolsConvert = oTran.Helper.LoadScript('Tools.S_Convert')

  # Set Terbilang
  Currency = oTran.LCurrency
  Total = oTran.Amount or 0.0
  
  Terbilang = ToolsConvert.Terbilang(config,Total,
            KodeMataUang = '000',
            NamaMataUang = Currency.Symbol_Says)
  
  Terbilang = ToolsConvert.Divider(Terbilang,45)
  if len(Terbilang) == 1 : Terbilang.append('')

  # Get Branch Info
  #corporate = oTran.Helper.CreateObject('Corporate')
  #CabangInfo = corporate.GetCabangInfo(oTran.BranchCode)
  #Nama_Cabang = CabangInfo.Nama_Cabang

  # Get Template
  PrintHelper = oTran.Helper.CreateObject('PrintHelper')
#     templateKwitansi = PrintHelper.LoadTemplate('KwitansiPengeluaran')
  templateKwitansi = PrintHelper.LoadRtfTemplate('KwitansiPengeluaran')    

  NamaLembaga = oTran.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  dataKwitansi = {}
  dataKwitansi['NOTRANSAKSI'] = oTran.TransactionNo
  dataKwitansi['PAIDTO'] = oTran.PaidTo[:30]
  dataKwitansi['ALAMAT1'] = ''
  dataKwitansi['ALAMAT2'] = ''
  dataKwitansi['NAMAKAS'] = ''
  dataKwitansi['TERBILANG1'] = Terbilang[0]
  dataKwitansi['TERBILANG2'] = Terbilang[1]
  dataKwitansi['NAMA_LEMBAGA'] = NamaLembaga
  dataKwitansi['USER_CETAK'] = oTran.ReceivedFrom #config.SecurityContext.InitUser[:15]
  dataKwitansi['WAKTU_CETAK'] = config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now())
  dataKwitansi['TGL_BAYAR'] = config.FormatDateTime('dd mmmm yyyy',oTran.GetAsTDateTime('ActualDate'))
  dataKwitansi['TOTAL'] = config.FormatFloat('#,##0.00',Total)
  dataKwitansi['KETERANGAN'] = oTran.Description
  dataKwitansi['CURRSYMBOL'] = Currency.Symbol

  DETAIL = ''
  #oItems = oTran.Ls_TransactionItem
  i = 1
  #while not oItems.EndOfList:
  aSQLText = " select transactionitemid from transactionitem \
                   where transactionid=%d " % oTran.TransactionId        

  oRes = oTran.Config.CreateSQL(aSQLText).RawResult
  
  while not oRes.Eof:
    oItem = oTran.Helper.GetObject(
          'TransactionItem', oRes.TransactionItemId
      ).CastToLowestDescendant()
      
    if oItem.MutationType == 'D':
      Description = oItem.Description           
      DETAIL += '%(LINE)2s      %(NOACCOUNT)-10s   %(DESCRIPTION)-50s   %(CURRSYMBOL)-2s %(AMOUNT)25s \n\\par ' % {
           'LINE' : str(i),
           'NOACCOUNT' : oItem.AccountCode,
           'DESCRIPTION' : oItem.Description,
           'AMOUNT' :  config.FormatFloat('#,##0.00',oItem.Amount),
           'CURRSYMBOL' : Currency.Symbol,             
        }
      i+=1
    else:        
      dataKwitansi['NAMAKAS'] = oItem.RefAccountName[:25]
      dataKwitansi['KODEAKUN'] = oItem.AccountCode
    #endif
    oRes.Next()
  #-- while
  
  dataKwitansi['DETAIL'] = DETAIL
  
  return oTran.CreateRTFForPrint(templateKwitansi,dataKwitansi)
