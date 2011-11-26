import sys
import simplejson

import com.ihsan.foundation.pobjecthelper as phelper

# constant
GALAT = 0.001

dictErrorMap = {
  'Successful':'000',
  'InternalError':'999',
  
  'PrepaidNotAvailable':'997',

  'InactiveAccount':'990',
  'ClosedAccount':'991',
  'AccountBalanceLow':'992',
  'AccountNotFound':'899',
  'AccountBlocked':'998',
  
  'Sentinel':'xxx'
}

def DAFScriptMain(config, params, returns):
  rawMessage = params.FirstRecord.data
  
  request = convert(simplejson.loads(rawMessage))
  response = processRequest(config, request)
  #response = request
  rawResponse = simplejson.dumps(response)
  
  returns.CreateSimpleDataPacket().data = rawResponse
#--

class record:
  pass
#--

def processRequest(config, request):
  #import rpdb2; rpdb2.start_embedded_debugger('000')
  
  response = {}
  try:
    try:
      trxType = request['trx_type']      
      TransactionNo = ''
      if trxType in ('TEST'):
        Test(config, request, response)
      elif trxType in ('NEW_TRANFUNDCOLL'):
        CreateFundCollection(config, request, response)
      elif trxType in ('DEL_TRANFUNDCOLL'):
        DeleteFundCollection(config, request, response)
      else:
        raise 'InternalError','Unknown transaction type'
      
      response['is_err'] = 0
      response['error_code'] = ''
      response['err_info'] = ''
      response['status'] = ''
    except:
      response['is_err'] = 1
      response['error_code'] = str(sys.exc_info()[0])
      response['err_info'] = str(sys.exc_info()[1])
      if dictErrorMap.has_key(response['error_code']):
        response['status'] = dictErrorMap[response['error_code']]
      else:
        response['status'] = dictErrorMap['InternalError']
  finally:
    config.ResetCache()

  return response
#--

def Test(config, request, response):
  #if request['biller_id'] == 1 :
  #  status = '000'
  #else :  
  #  status = '111'
  response['err_info'] = "Berhasil"
   
def CreateFundCollection(config, request, response):
  # REQUEST FROM EXTERNAL APP
  # - TransactionDate --> Tanggal Transaksi
  # - UserId --> UserInput
  # - BranchId --> Kode Cabang dari database intranet
  # - CurrencyCode --> Kode Valuta
  # - Description --> Deskripsi Transaksi
  # - DonorId --> Id DOnatur
  # - CashAccountNo --> Kode Kas
  # 
  
  #TransactionDate = request['transaction_date']
  UserId = request['user_id'].upper()
  #BranchId = request['branch_id']  
  ProductId = request['product_id']
  DonorId = request['donor_id']
  CashAccountNo = request['cash_accountno']
  CurrencyCode = request['currency_code']
  MarketerId = request['marketer_id']
  Description = request['description']
  Rate = 1.0
  Amount = request['amount']
  FundEntity = request['fund_entity']
  strTransactionDate = request['transaction_date']
  
  y, m, d = strTransactionDate.split('-')
  TransactionDate = config.ModLibUtils.EncodeDate(int(y),int(m),int(d))
  
  
  # Set Currency Default jika request tidak diinputkan
  if CurrencyCode == '' :
    CurrencyCode = '000'

  helper = phelper.PObjectHelper(config)

  # Cek Amount
  if Amount <= 0.0 :
    raise '','Nilai Transaksi'
  # Cek User
  oUser = helper.GetObject('UserApp',UserId)
  #oUser = config.CreatePObjImplProxy('UserApp')
  #oUser.key = UserId
  if oUser.isnull :
    raise 'PERINGATAN','Id User tidak terdaftar'
  if oUser.Branch_Code == '':
    raise 'PERINGATAN','Data user belum memiliki cabang'
  BranchCode = oUser.Branch_Code  
  
  # Cek Cabang
  #oBranch = helper.GetObjectByNames( 'Branch' , { 'BranchId' : BranchId } )
  #if oBranch.isnull :
  #  raise 'PERINGATAN','Id Cabang tidak terdaftar'
  
  # Cek Currency Code
  oCurrencyCode = helper.GetObject( 'Currency' , CurrencyCode)
  if oCurrencyCode.isnull :
    raise 'PERINGATAN','Kode Valuta tidak dikenali'
    
  # Cek Produk
  oProductAccount = helper.GetObjectByNames( 'ProductAccount',
      { 'ProductId' : ProductId, 
        'CurrencyCode' : CurrencyCode, 
        'BranchCode' : BranchCode }
    )

  if oProductAccount.isnull :
    raise 'PERINGATAN','Kode produk tidak ditemukan'
    
  # Cek Donatur
  oDonatur = helper.GetObject('VDonor',DonorId)
  if oDonatur.isnull :
    raise 'PERINGATAN','Id donatur tidak ditemukan'
      
  if MarketerId in [0,'',None] :
    MarketerId = oDonatur.Marketer_Id 
  
  # Cek CashAccount
  if CashAccountNo != '' :
    oCashAccount = helper.GetObject('CashAccount',CashAccountNo)
    if oCashAccount.isnull :
      raise 'PERINGATAN','Akun Kas Tidak ditemukan'
    oCashAccount = oCashAccount.CastToLowestDescendant()
    
    if oCashAccount.IsA("BankCash") :
      ChannelCode = 'A'
    elif oCashAccount.IsA("BranchCash") :
      ChannelCode = 'R'
    elif oCashAccount.IsA("PettyCash") :
      ChannelCode = 'P'
    # end if.elif  
  else:
    oCashAccount = helper.GetObjectByNames('BranchCash',
        {'BranchCode': BranchCode, 'CurrencyCode': CurrencyCode})
    if oCashAccount.isnull:
      raise 'Collection', 'Rekening kas cabang %s:%s tidak ditemukan' % (BranchCode, CurrencyCode)
    ChannelCode = 'R'

  # Get Batch  
  #PrintHelper = helper.CreateObject('PrintHelper')  
  oBatchHelper = helper.CreateObject("BatchHelper")
  oBatch = oBatchHelper.GetBatchExternal(TransactionDate,UserId,BranchCode)
  
  config.BeginTransaction()
  try :
    oTran = oBatch.NewExtTransaction('SD002','EXTCOLL',UserId)
    
    oTran.Inputer     = UserId
    oTran.BranchCode  = BranchCode
    
    oTran.ReferenceNo = 'EXT01' 
    oTran.Description = Description  
    oTran.DonorNo = oDonatur.Donor_No
    oTran.DonorName = oDonatur.Full_Name
    oTran.CurrencyCode = CurrencyCode
    oTran.Rate = Rate
    oTran.MarketerId = MarketerId
    oTran.ChannelCode = ChannelCode    
    oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
    oTran.Amount = Amount 
    
    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, DonorId)
    oItemPA.SetMutation(Amount, Rate)
    oItemPA.Description = Description

    oItemPA.SetJournalParameter('C10')
    oItemPA.SetCollectionEntity(FundEntity)
    oItemPA.PercentageOfAmil = oProductAccount.LProduct.PercentageOfAmilFunds or 0.0
    if oDonatur.IsSponsor() : oDonatur.AddTransaction(oItemPA)
    
    oItemBC = oTran.CreateAccountTransactionItem(oCashAccount)
    oItemBC.SetMutation('D', Amount, Rate)
    oItemBC.Description = Description
    oItemBC.SetJournalParameter('10')
    
    oTran.GenerateTransactionNumber(oCashAccount.CashCode)
    
    #corporate = helper.CreateObject('Corporate')
    #if corporate.CheckLimitOtorisasi(Amount * Rate):
    #  oTran.AutoApproval()    
    
    config.Commit() 
  except :
    config.Rollback()
    raise
  
  response['transactionno'] = oTran.TransactionNo

def DeleteFundCollection(config, request, response):
  helper = phelper.PObjectHelper(config)
  
  TransactionNo = request['transaction_no']
  
  oTran = helper.GetObjectByNames('Transaction',{'TransactionNo' : TransactionNo})
  if oTran.isnull : 
    raise '','Transaksi Tidak ditemukan'
  
  #TranHelper = helper.LoadScript('Transaction.TransactionHelper')
  #TranHelper.DeleteTransactionJournal(oTran,'D')
  
  config.BeginTransaction()
  try :
    if oTran.SubSystemCode != 'EXTCOLL' :
      raise '','Anda tidak diperbolehkan menghapus transaksi dengan nomor %s melalui fungsi ini.' % oTran.TransactionNo 
      
    if oTran.AuthStatus == 'T' :
      raise '','Transaksi tidak boleh dihapus karena sudah di otorisasi'
      
    oTran.Delete()
    config.Commit() 
  except :
    config.Rollback()
    raise   

################################################################################

def convert(data):
  # convert json load format to native python dictionary
  if isinstance(data, unicode):
    return str(data)
  elif isinstance(data, dict):
    return dict(map(convert, data.iteritems()))
  elif isinstance(data, (list, tuple)):
    return type(data)(map(convert, data))
  else:
    return data
#--

def GetLiabilityAccount(helper, accountCode, ignoreBlocked=0):
  try:
    oRekening = helper.GetObject('RekeningLiabilitas',accountCode).CastToLowestDescendant()
  except:
    raise 'AccountNotFound','Unknown account'
    
  if oRekening.Status_Rekening == 3:
    raise 'ClosedAccount','Closed account'

  if (not ignoreBlocked) and oRekening.Is_Blokir == 'T':
    raise 'AccountBlocked','Account has blocked status'
    
  return oRekening
#--
