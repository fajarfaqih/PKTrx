import sys
import com.ihsan.foundation.pobjecthelper as phelper
import simplejson

OldBranch = '101'

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)

  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()
  app.ConCreate('DJournal')
  helper = phelper.PObjectHelper(config)
  corporate = helper.CreateObject('Corporate')
      
  filename = corporate.GetUserHomeDir() + "GenerateJournalItemLog.txt"
  
  try:
    fh = open(filename,'w')
    try:
      TranHelper = helper.LoadScript('Transaction.TransactionHelper')      
      
      AddParam = ''
      AddParam += " and inputer = 'SUDIANA' "
      #AddParam += " and TransactionCode = 'SD001' "
      AddParam += " and TransactionCode not in ('CAR', 'CA') "
      AddParam += " and BranchCode = '101' "
      #AddParam += " and TransactionNo = 'KM-2011-101-000-0000007' "

      # Total Data
      sSQLCount = "select count(TransactionId) \
              from transaction t \
              where Transactionid is not null \
                  %s " % ( AddParam )
      
      oResCount = config.CreateSQL(sSQLCount).RawResult

      TotalData = oResCount.GetFieldValueAt(0) or 0
      
      # Get Data
      sSQL = "select TransactionId \
              from transaction t \
              where Transactionid is not null \
                  %s \
                  order by TransactionId " % (
                   AddParam )

      oRes = config.CreateSQL(sSQL).RawResult
      logProcess = ''

      idx = 1
      oRes.First()
      while not oRes.Eof:
        oTran = helper.GetObject('Transaction', oRes.TransactionId)

        logmessage = "Proses Data ke %d dari %s data " % ( idx, TotalData)
        WriteLog(config, app, fh, 'DJournal', logmessage)

        logmessage = "Proses TransactionId %d No Trans %s : " % ( oRes.TransactionId, oTran.TransactionNo)
        WriteLog(config, app, fh, 'DJournal', logmessage)
        
        try: 
          Inbox = helper.GetObjectByNames(
                  'InboxTransaction',
                  {'TransactionId': oTran.TransactionId}
              )

          ph = Inbox.LoadDataPacket(OldBranch)
          #uideflist.SetCustomReturnDataset(ph)
          params = ph.Packet
          # uipart must have TransactionNo member
          uipTran = params.uipTransaction.GetRecord(0)
          uipTran.TransactionNo = oTran.TransactionNo


          if oTran.TransactionCode =='SD001' : 
            FundCollection(config, params)
          elif oTran.TransactionCode =='DD001' : 
            FundDistribution(config, params)
          elif oTran.TransactionCode =='GT' : 
            GeneralTransaction(config, params)
          elif oTran.TransactionCode =='CO' :
            CashOut(config, params)
          elif oTran.TransactionCode =='TI' :
            TransferInternal(config, params)
          # end if  

          logmessage = "Transfer Transaksi Berhasil"
        except :
          logmessage = "Transfer Transaksi Gagal : "  + str(sys.exc_info()[1])
        
        WriteLog(config, app, fh, 'DJournal', logmessage)

        idx += 1
        oRes.Next()
      # end while

    except:
      status.Is_Error = 1
      status.Error_Message = str(sys.exc_info()[1])
  
  finally:
    fh.close()
  
  sw = returnpacket.AddStreamWrapper()
  sw.LoadFromFile(filename)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)


def WriteLog(config, app, FileBuf, LogName, LogMessage):
  app.ConWriteln(LogMessage, LogName)
  FileBuf.write(LogMessage + '\n')
  config.SendDebugMsg(LogMessage)


def FundCollection(config, params):
  helper = phelper.PObjectHelper(config)
  oTransaction = params.uipTransaction.GetRecord(0)

  request = {}
  
  BranchCode =config.SecurityContext.GetUserInfo()[4]
  request['ReferenceNo'] = oTransaction.ReferenceNo
  request['Description'] = oTransaction.Description
  request['ActualDate'] = oTransaction.ActualDate
  request['Amount'] = oTransaction.TotalAmount
  request['Inputer'] = oTransaction.Inputer
  #request['BatchId'] = oTransaction.GetFieldByName('LBatch.BatchId')
  request['TransactionNo'] = oTransaction.TransactionNo
  request['CashCurrency'] = oTransaction.GetFieldByName('LCurrency.Currency_Code')
  request['PaidTo'] = oTransaction.PaidTo
  #request['PettyCashAccountNo'] = oTransaction.GetFieldByName('LPettyCash.AccountNo')

  oDonor = params.uipDonor.GetRecord(0)
  request['DonorId'] = oDonor.DonorId
  request['DonorNo'] = oDonor.DonorNo
  request['DonorName'] = oDonor.DonorName
  request['DonorType'] = oDonor.DonorType
  request['MarketerId'] = oDonor.GetFieldByName('LMarketer.MarketerId')
  
  # Cek Marketer
  oMarketer = helper.GetObject('Marketer',request['MarketerId'])
  if oMarketer.isnull :
    raise '','Data Marketer tidak ditemukan / tidak valid / tidak terdaftar sebagai marketer'
  
  request['Rate'] = oTransaction.Rate
  request['BankAccountNo'] = oTransaction.GetFieldByName('LBank.AccountNo')
  request['AssetCode'] = oTransaction.GetFieldByName('LAsset.Account_Code')
  request['AssetName'] = oTransaction.GetFieldByName('LAsset.Account_Name')
  request['AssetCurrency'] = oTransaction.GetFieldByName('LValuta.Currency_Code')
  request['BranchCode'] = BranchCode

  request['SponsorId'] = oTransaction.GetFieldByName('LSponsor.SponsorId')
  request['VolunteerId'] = oTransaction.GetFieldByName('LVolunteer.VolunteerId')
  #request['ProductBranchCode'] = oTransaction.GetFieldByName('LProductBranch.Kode_Cabang')
  request['ShowMode'] = oTransaction.ShowMode
  request['PaymentType'] = oTransaction.PaymentType
  
  items = []

  ItemDescList = []
  for i in range(params.uipTransactionItem.RecordCount):
    oItem = params.uipTransactionItem.GetRecord(i)
    item = {}
    
    item['ProductId'] = oItem.GetFieldByName('LProduct.ProductId')
    item['Amount'] = oItem.Amount
    #item['Valuta'] = oItem.GetFieldByName('LCurrency.Currency_Code')
    #item['Rate']   = oItem.Rate
    #item['Ekuivalen'] = oItem.Ekuivalen
    item['Description'] = oItem.Description
    item['FundEntity'] = oItem.FundEntity
    item['PercentageOfAmil'] = oItem.PercentageOfAmil

    # Set ProductAccount
    ProductId = oItem.GetFieldByName('LProduct.ProductId')

    oProductAccount = helper.GetObjectByNames('ProductAccount',
        {
          'ProductId' : ProductId ,
          'BranchCode' : BranchCode,
          'CurrencyCode' : '000'
        }
     )
    item['AccountNo'] = oProductAccount.AccountNo
    
    items.append(item)
    ItemDescList.append(oItem.Description)
  #-- for

  request['Items']= items

  if request['Description'] == '' :
    request['Description'] = ','.join(ItemDescList)[:100]
    oTransaction.Description = request['Description']

  sRequest = simplejson.dumps(request)
  oService = helper.LoadScript('Transaction.Collection')

  response = oService.CollectionUpdate(config, sRequest,params)

  response = simplejson.loads(response)
  TransactionNo = response[u'TransactionNo']
  
  IsErr = response[u'Status']
  ErrMessage = response[u'ErrMessage']

  if IsErr : raise '', ErrMessage

def FundDistribution(config, params):
  helper = phelper.PObjectHelper(config)  
  oTransaction = params.uipTransaction.GetRecord(0)
  
  request = {}
  BranchCode =config.SecurityContext.GetUserInfo()[4]

  request['ReferenceNo'] = oTransaction.ReferenceNo
  request['Description'] = oTransaction.Description
  request['Amount'] = oTransaction.TotalAmount
  request['Inputer'] = oTransaction.Inputer
  #request['BatchId'] = oTransaction.GetFieldByName('LBatch.BatchId')
  request['TransactionNo'] = oTransaction.TransactionNo
  request['PaidTo'] = oTransaction.PaidTo
  request['CashCurrency'] = oTransaction.GetFieldByName('LCurrency.Currency_Code')
  request['DonorId'] = oTransaction.DonorId
  request['ReceivedFrom'] = oTransaction.ReceivedFrom
  request['ActualDate'] = oTransaction.ActualDate
  
  
  request['Rate'] = oTransaction.Rate
  request['BankAccountNo'] = oTransaction.GetFieldByName('LBank.AccountNo')
  request['AssetCode'] = oTransaction.GetFieldByName('LAsset.Account_Code')
  request['AssetName'] = oTransaction.GetFieldByName('LAsset.Account_Name')
  request['AssetCurrency'] = oTransaction.GetFieldByName('LValuta.Currency_Code')
  request['BranchCode'] = BranchCode

  request['SponsorId'] = oTransaction.GetFieldByName('LSponsor.SponsorId')
  request['VolunteerId'] = oTransaction.GetFieldByName('LVolunteer.VolunteerId')
  #request['ProductBranchCode'] = oTransaction.GetFieldByName('LProductBranch.Kode_Cabang')
  request['PeriodId'] = oTransaction.GetFieldByName('PeriodId')
  request['PaymentType'] = oTransaction.PaymentType

  items = []
  
  for i in range(params.uipTransactionItem.RecordCount):
    oItem = params.uipTransactionItem.GetRecord(i)
    item = {}
    item['ProductId'] = oItem.GetFieldByName('LProduct.ProductId')

    item['Ashnaf'] = oItem.Ashnaf
    item['Amount'] = oItem.Amount
    item['Description'] = oItem.Description
    item['FundEntity'] = oItem.FundEntity
    item['DistItemAccount'] = oItem.DistItemCode
    item['BudgetId'] = oItem.BudgetId or 0

    # Set ProductAccount
    ProductId = oItem.GetFieldByName('LProduct.ProductId')

    oProductAccount = helper.GetObjectByNames('ProductAccount',
        {
          'ProductId' : ProductId ,
          'BranchCode' : BranchCode,
          'CurrencyCode' : '000'
        }

     )
    item['AccountNo'] = oProductAccount.AccountNo
    item['BudgetCode'] = oItem.BudgetCode or ''

    items.append(item)
  #-- for
  
  request['Items']= items
  sRequest = simplejson.dumps(request)
  oService = helper.LoadScript('Transaction.Distribution')
  
  response = oService.DistributionUpdate(config, sRequest ,params)

  response = simplejson.loads(response)

  TransactionNo = response[u'TransactionNo']
  IsErr = response[u'Status']
  ErrMessage = response[u'ErrMessage']

  if IsErr : raise '', ErrMessage

def GeneralTransaction(config, params):
  helper = phelper.PObjectHelper(config)

  oTransaction = params.uipTransaction.GetRecord(0)
  BranchCode =config.SecurityContext.GetUserInfo()[4]

  request = {}
  request['ReferenceNo'] = oTransaction.ReferenceNo
  request['Description'] = oTransaction.Description
  request['TotalDebit'] = oTransaction.TotalDebit
  request['TotalCredit'] = oTransaction.TotalCredit
  request['Amount'] = oTransaction.TotalDebit
  request['Rate'] = 1.0
  request['Inputer'] = oTransaction.Inputer
  #request['BatchId'] = oTransaction.GetFieldByName('LBatch.BatchId')
  request['BranchCode'] = BranchCode
  request['ActualDate'] = oTransaction.ActualDate
  request['TransactionNo'] = oTransaction.TransactionNo

  items = []

  for i in range(params.uipTransactionItem.RecordCount):
    oItem = params.uipTransactionItem.GetRecord(i)
    item = {}
    itemType = oItem.ItemType
    item['ItemType'] = itemType

    if itemType == 'C':
      item['DonorId'] = int(oItem.DonorId)
      item['DonorName'] = oItem.DonorName
      item['ProductId'] = oItem.ProductIdColl

      oProductAccount = helper.GetObjectByNames('ProductAccount',
        {
          'ProductId' : oItem.ProductIdColl ,
          'BranchCode' : BranchCode,
          'CurrencyCode' : '000'
        }

       )

      item['AccountNo'] = oProductAccount.AccountNo
      item['VolunteerId'] = oItem.GetFieldByName('LVolunteer.VolunteerId')
      item['FundEntity'] = oItem.FundEntityCollection
      item['PercentageOfAmil'] = oItem.PercentageOfAmil
    elif itemType == 'D':
      item['ProductId'] = oItem.ProductIdDist #oItem.GetFieldByName('ProductDist.ProductId')

      oProductAccount = helper.GetObjectByNames('ProductAccount',
        {
          'ProductId' : oItem.ProductIdDist ,
          'BranchCode' : BranchCode,
          'CurrencyCode' : '000'
        }
       )
      item['AccountNo'] = oProductAccount.AccountNo

      item['SponsorId'] = oItem.SponsorId or 0
      item['SponsorName'] = oItem.SponsorName
      item['FundEntity'] = oItem.FundEntityDist
      item['Ashnaf'] = oItem.Ashnaf
    elif itemType == 'B':
      item['AccountNo'] = oItem.GetFieldByName('LCashAccount.AccountNo')
    elif itemType == 'G':
      item['AccountCode'] = oItem.GetFieldByName('LLedger.Account_Code')
      item['AccountName'] = oItem.AccountName

    item['Valuta'] = oItem.CurrencyCode
    item['MutationType'] = oItem.MutationType
    item['Amount'] = oItem.Amount
    item['Rate']   = oItem.Rate
    item['Ekuivalen'] = oItem.Ekuivalen
    item['Description'] = oItem.Description

    items.append(item)
  #-- for

  request['Items']= items
  sRequest = simplejson.dumps(request)


  oService = helper.LoadScript('Transaction.GeneralTransaction')

  TransactionCode = 'GT'
  response = oService.UpdateTransaction(TransactionCode, config, sRequest, params)


  response = simplejson.loads(response)
  TransactionNo = response[u'TransactionNo']  
  IsErr = response[u'Status']
  ErrMessage = response[u'ErrMessage']

  if IsErr : raise '', ErrMessage

def CashOut(config, params):
  helper = phelper.PObjectHelper(config)

  oTransaction = params.uipTransaction.GetRecord(0)
    
  BranchCode =config.SecurityContext.GetUserInfo()[4]

  request = {}
  request['ReferenceNo'] = oTransaction.ReferenceNo
  request['Description'] = oTransaction.Description
  request['ActualDate'] = oTransaction.ActualDate
  request['Amount'] = oTransaction.TotalAmount
  request['Inputer'] = oTransaction.Inputer
  request['BatchId'] = oTransaction.GetFieldByName('LBatch.BatchId')
  request['TransactionNo'] = oTransaction.TransactionNo
  request['PaidTo'] = oTransaction.PaidTo
  request['ReceivedFrom'] = oTransaction.ReceivedFrom
  
  request['Rate'] = oTransaction.Rate
  request['CurrencyCode'] = '000'
  request['RateCash'] = oTransaction.RateCash
  request['RateBank'] = oTransaction.RateBank

  request['BankAccountNo'] = oTransaction.GetFieldByName('LBank.AccountNo')
  request['AssetCode'] = oTransaction.GetFieldByName('LAsset.Account_Code')
  request['AssetName'] = oTransaction.GetFieldByName('LAsset.Account_Name')
  request['AssetCurrency'] = oTransaction.GetFieldByName('LValuta.Currency_Code')
  request['BranchCode'] = BranchCode
  request['PaymentType'] = oTransaction.PaymentType

  items = []

  for i in range(params.uipTransactionItem.RecordCount):
    oItem = params.uipTransactionItem.GetRecord(i)
    item = {}
    item['AccountCode'] = oItem.AccountCode
    item['AccountName'] = oItem.AccountName
    item['Amount'] = oItem.Amount
    item['Valuta'] = oItem.GetFieldByName('LCurrency.Currency_Code')
    item['Rate']   = oItem.Rate
    item['Ekuivalen'] = oItem.Ekuivalen
    item['Description'] = oItem.Description
    item['BudgetId'] = oItem.BudgetId
    
    items.append(item)
  #-- for

  request['Items']= items
  sRequest = simplejson.dumps(request)

  oService = helper.LoadScript('Transaction.CashOut')

  response = oService.CashOutUpdate(config, sRequest,params)

  response = simplejson.loads(response)
  TransactionNo = response[u'TransactionNo']

  IsErr = response[u'Status']
  ErrMessage = response[u'ErrMessage']
  
  if IsErr : raise '', ErrMessage

def TransferInternal(config, params):
  helper = phelper.PObjectHelper(config)

  oTransaction = params.uipTransaction.GetRecord(0)
    
  BranchCode =config.SecurityContext.GetUserInfo()[4]

  request = {}
  #request['BatchId'] = oTransaction.GetFieldByName('LBatch.BatchId')
  request['ActualDate'] = oTransaction.ActualDate
  request['SourceAccountNo'] = oTransaction.GetFieldByName('LCashAccountSource.AccountNo')
  if request['SourceAccountNo'] == 'BC.101.000' :
    request['SourceAccountNo'] == 'BC.104.000'
  request['DestAccountNo'] = oTransaction.GetFieldByName('LCashAccountDestination.AccountNo')
  if request['DestAccountNo'] == 'BC.101.000' :
    request['DestAccountNo'] == 'BC.104.000'

  request['TransactionNo'] = oTransaction.TransactionNo
  request['ReferenceNo'] = oTransaction.ReferenceNo
  request['Description'] = oTransaction.Description
  request['TranCurrencyCode'] = oTransaction.TranCurrencyCode
  request['Amount'] = oTransaction.Amount
  request['Rate'] = oTransaction.Rate
  request['Inputer'] = config.SecurityContext.InitUser
  request['BranchCode'] = config.SecurityContext.GetUserInfo()[4]


  request['SourceCurrencyCode'] = oTransaction.GetFieldByName('LCashAccountSource.CurrencyCode')
  request['SourceAmount'] = oTransaction.SourceAmount
  request['SourceRate'] = oTransaction.SourceRate

  sRequest = simplejson.dumps(request)

  oService = helper.LoadScript('Transaction.GeneralTransaction')

  TransactionCode = 'TI'
  response = oService.UpdateTransaction(TransactionCode, config, sRequest, params)

  response = simplejson.loads(response)

  TransactionNo = response[u'TransactionNo']
  IsErr = response[u'Status']
  ErrMessage = response[u'ErrMessage']
  
  if IsErr : raise '', ErrMessage