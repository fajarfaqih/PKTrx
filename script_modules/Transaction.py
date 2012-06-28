# Transaction.py

import com.ihsan.foundation.mobject as mobject
import com.ihsan.foundation.pobject as pobject
import simplejson
import sys
import com.ihsan.fileutils as utils
import com.ihsan.net.socketclient as socketclient
import types
import com.ihsan.util.customidgenAPI as customidgenAPI
import Voucher

# GLOBALS
MNEMONICS = {
    ('D', 'P'): 'D',
    ('D', 'N'): 'C',
    ('C', 'P'): 'C',
    ('C', 'N'): 'D'
}
REVERSE_MNEMONIC = {'D':'C','C':'D'}

class BatchHelper(mobject.MObject):

  def GetBatchExternal(self,aDate,aUserId,aBranchCode):
    helper = self.Helper
    config = self.Config
    
    config.BeginTransaction()
    try:
         
      aDescription = 'EXT_%s_%s' % (aUserId,config.FormatDateTime('dd/mm/yyyy',aDate)) 
            
      oBatch = helper.GetObjectByNames(
        'TransactionBatch',
        {  'Inputer' : aUserId,
           'BatchDate' : aDate,
           'BatchTag' : 'OPR',
           'IsPosted' : 'T',
           'IsClosed' : 'F' 
        }
      )
      
      if oBatch.isnull :
        oBatch = helper.CreatePObject('TransactionBatch')
        oBatch.BatchDate  = aDate
        oBatch.BranchCode   = aBranchCode
        oBatch.Inputer      = aUserId
        oBatch.Description  = aDescription 
        oBatch.BatchTag = 'OPR'
      # end if
        
      config.Commit()   
    except:
      config.Rollback()    
      raise 
         
    config.BeginTransaction()
    try :
      oBatch.PostToAccounting()    
      config.Commit()
    except:
      config.Rollback()
      raise
      
    return oBatch
    
  def GetBatchUser(self, aDate, aUserId=None, aBranchCode=None):
    helper = self.Helper
    config = self.Config
    
    # WARNING : Jangan gunakan/panggil fungsi ini  
    # di dalam lingkup config.BeginTransaction() - config.Commit() 
    # Karena dalam fungsi ini sudah terdapat baris kode pemanggilan 
    # database transaction (config.BeginTransaction())
    SecContext = config.SecurityContext
    
    if aUserId == None :
      aUserId = SecContext.UserID
    # end if 
    
    if aBranchCode == None :
      aBranchCode = SecContext.GetUserInfo()[4]     
    # end if
      
    aDescription = '%s_%s' % (aUserId,config.FormatDateTime('dd/mm/yyyy',aDate)) 
    
    oBatch = helper.GetObjectByNames(
        'TransactionBatch',
        {  'Inputer' : aUserId,
           'BatchDate' : aDate,
           'BatchTag' : 'OPR',
           'IsPosted' : 'T',
           'IsClosed' : 'F' ,
           'BranchCode' : aBranchCode
        }
      )
      
    if oBatch.isnull :
      config.BeginTransaction()
      try:    
        oBatch = helper.CreatePObject('TransactionBatch')
        oBatch.BatchDate  = aDate
        oBatch.BranchCode   = aBranchCode
        oBatch.Inputer      = aUserId
        oBatch.Description  = aDescription 
        oBatch.BatchTag = 'OPR'
        config.Commit()   
      except:
        config.Rollback()    
        raise 
      
     
      config.BeginTransaction()
      try :
        oBatch.PostToAccounting()    
        config.Commit()
      except:
        config.Rollback()
        raise
    # end if oBatch.isnull

    return oBatch

class TransactionBatch(pobject.PObject):
  # static variable
  pobject_classname = 'TransactionBatch'
  pobject_keys = ['BatchId']

  def OnCreate(self):
    self.BatchDate = int(self.Config.Now())
    #mlu = self.Config.ModLibUtils
    #self.BatchDate = int(mlu.EncodeDate(2010, 1, 4))
    self.IsClosed = 'F'
    self.IsPosted = 'F'
    
  def PostToAccounting(self):
    helper = self.Helper; config = self.Config

    request = {}
    request['trx_code']     = 'CreateJournal'
    request['journal_date'] = self.BatchDate
    request['journal_type'] = 'IST'
    request['branch_code']  = self.BranchCode
    request['description'] = self.Description
    request['user_id']      = self.Inputer
    request['source_app']   = 'com.pkpu.transaction'
    request['source_app_class'] = 'TransactionBatch'
    request['source_app_ref']   = str(self.BatchId)

    #-- send to accounting interface
    sMessage = simplejson.dumps(request)
    app = config.AppObject
    #acc_host = helper.GetObject('ParameterGlobal', 'GLSVCHST').Get()
    #acc_port = helper.GetObject('ParameterGlobal', 'GLSVCPRT').GetInt()
    acc_host = config.GetGlobalSetting('GLSVCHOST')
    acc_port = int(config.GetGlobalSetting('GLSVCPORT'))
    conn = app.UseCachedTCPConn(acc_host, acc_port)

    try:
      conn.SendSTXETXMessage(sMessage)
      response = simplejson.loads(conn.ReadSTXETXMessage())
    finally:
      app.ReleaseCachedTCPConn(conn, 1)
    #--

    status = response[u'status']
    if status == 0:
      raise 'PostToAccounting', response[u'errMsg']
    elif status == 1:
      self.BatchNo = response['journal_no']
      self.IsPosted = 'T'
    else:
      raise

  def NewTransaction(self, aTranCode, aUserId = ''):
    # Validasi Batch
    if self.IsPosted == 'T' and self.IsClosed == 'T' :
      raise '','Anda tidak dapat melakukan transaksi karena tanggal telah ditutup.'

    param = {'Owner': self, 'TranCode': aTranCode, 'UserId' : aUserId}
    oTran = self.Helper.CreatePObject('Transaction', param)
    oTran.ActualDate = self.GetAsTDateTime('BatchDate') 

    return oTran
  
  def NewExtTransaction(self, aTranCode, aExtAppCode, aUserId = ''):
    # Validasi Batch
    
    oTran = self.NewTransaction(aTranCode,aUserId)
    oTran.SubSystemCode = aExtAppCode
    
    return oTran
    
class TransHistoryOfChanges(pobject.PObject):
  # static variable
  pobject_classname = 'TransHistoryOfChanges'
  pobject_keys = ['HistoryId']

  def OnCreate(self):
    self.UserId = self.Config.SecurityContext.InitUser
    self.ProcessTime = int(self.Config.Now())

class Transaction(pobject.PObject):
  # static variable
  pobject_classname = 'Transaction'
  pobject_keys = ['TransactionId']

  def CheckGlobalPermition(self):
    permit = self.Helper.GetObject('ParameterGlobal', 'TRALLOW').Get()
    if permit.upper() != 'T':
      raise 'Permition', 'Global permition reject to create transaction!'

  def OnCreate(self, param):
    self.CheckGlobalPermition()
    self.BatchId = param['Owner'].BatchId
    self.TransactionCode = param['TranCode']
    
    if param['UserId'] == '' :
      aUserId = self.Config.SecurityContext.InitUser
    else :  
      aUserId = param['UserId'] 
    # end if
    self.Inputer = aUserId
    
    self.TransactionDate = int(self.Config.Now())
    self.ActualDate = int(self.Config.Now())
    self.TransactionTime = self.Config.Now()
    self.AuthStatus = 'F'
    self.IsPosted = 'F'    
    self.CurrencyCode = '000'
    self.Rate = 1

  def GenerateTransactionNumber(self,CashCode,IsChangeTransNo = 0):
    
    VoucherCode = self.LTransactionType.VoucherCode
    #y = config.ModLibUtils.DecodeDate(config.Now())[0]
    TransactionYear = self.ActualDate[0]
    branchCode = self.BranchCode

    # Cek apakah perlu generate nomor baru atau ada perubahan cashcode
    if (self.TransactionNo or '') != '' and not IsChangeTransNo: 
      splitNumber = self.TransactionNo.split('-')
      if splitNumber[3] == CashCode and \
         splitNumber[1] == str(TransactionYear) and \
         splitNumber[0] == VoucherCode and \
         splitNumber[2] == branchCode : # Cek jika cashcode masih sama
        return

    # Proses generate number
    config = self.Config
    
    TransactionCode = self.TransactionCode or ''
    if  TransactionCode == '' :
      raise 'GenerateTransactionNumber','TransactionCode tidak ditemukan'

    #CashCode = oCashAccount.CashCode
    if CashCode == '' :
      raise 'GenerateTransactionNumber','CashCode tidak ditemukan.'

    #y = config.ModLibUtils.DecodeDate(config.Now())[0]
    #branchCode = config.SecurityContext.GetUserInfo()[4]
    
    
    #raise '',"TES %s " %self.LTransactionType.VoucherCode

    prefixNumber = "%s-%s-%s-%s" % (
              self.LTransactionType.VoucherCode ,
              str(TransactionYear),
              branchCode,
              CashCode)


    # Get Sequence
    #rsSeq = config.CreateSQL("select nextval('seq_transactionnumber')").RawResult
    #strId = str(rsSeq.GetFieldValueAt(0)).zfill(7)
    customid = customidgenAPI.custom_idgen(config)
    customid.PrepareGetID('TRANSACTION', prefixNumber)
    try:
      id = customid.GetLastID()
      strID = str(id).zfill(7)
      customid.Commit()
    except:
      customid.Cancel()
      raise '', str(sys.exc_info()[1])

    self.TransactionNo = prefixNumber + '-' + strID

  def CreateAccountTransactionItem(self, oAccount,IsUpdateBalance='T'):
    param = {'Owner': self, 'Account': oAccount}
    oItem = self.Helper.CreatePObject('AccountTransactionItem', param)
    oItem.IsUpdateBalance = IsUpdateBalance
        
    if self.ChannelAccountNo in ['',None,0] and oAccount.IsA('CashAccount'):
      self.ChannelAccountNo = oAccount.AccountNo

    return oItem

  def CreateDonorTransactionItem(self, oProductAccount, aDonorId):
    param = {'Owner': self, 'Account': oProductAccount, 'DonorId': aDonorId}
    oItem = self.Helper.CreatePObject('DonorTransactionItem', param)

    return oItem

  def CreateZakahDistTransactItem(self, oProductAccount, aAshnaf):
    param = {'Owner': self, 'Account': oProductAccount, 'Ashnaf': aAshnaf}
    oItem = self.Helper.CreatePObject('ZakahDistTransactItem', param)

    return oItem

  def CreateCATransactItem(self, CashAdvanceAccount):
    param = {'Owner': self, 'Account': CashAdvanceAccount}
    oItem = self.Helper.CreatePObject('CATransactItem', param)

    return oItem

  def CreateCAReturnTransactItem(self, CashAdvanceAccount):
    param = {'Owner': self, 'Account': CashAdvanceAccount}
    oItem = self.Helper.CreatePObject('CAReturnTransactItem', param)

    return oItem

  def CreateInvestmentTransactItem(self,InvestmentAccount):
    param = {'Owner': self, 'Account': InvestmentAccount}
    oItem = self.Helper.CreatePObject('InvestmentTransactItem', param)

    return oItem

  def CreateAssetTransactionItem(self, oAccount,IsUpdateBalance='T'):
    param = {'Owner': self, 'Account': oAccount}
    oItem = self.Helper.CreatePObject('FixedAssetTransactItem', param)
    oItem.IsUpdateBalance = IsUpdateBalance
        
    if self.ChannelAccountNo in ['',None,0] and oAccount.IsA('CashAccount'):
      self.ChannelAccountNo = oAccount.AccountNo

    return oItem

  def CreateGLTransactionItem(self, GLAccount, aCurrency):
    param = {'Owner': self, 'GLAccount': GLAccount, 'CurrencyCode': aCurrency}
    oItem = self.Helper.CreatePObject('GLTransactionItem', param)

    return oItem

  def SetAuth(self, authAction):
    if self.AuthStatus == 'T' :
      raise 'Authorization', 'Transaksi sudah diotorisasi'

    self.AuthStatus = 'T'
    self.AuthAction = authAction
    self.AuthDate   = self.Config.Now()
    self.AuthUser   = self.Config.SecurityContext.InitUser

  def Approval(self):
    self.SetAuth('A')

    oItems = self.Ls_TransactionItem
    aSQLText = " select transactionitemid from transactionitem \
                     where transactionid=%d " % self.TransactionId        

    oRes = self.Config.CreateSQL(aSQLText).RawResult
    
    #self.Config.FlushUpdates()
    #while not oItems.EndOfList:
    
    while not oRes.Eof:
      #itemElmt = oItems.CurrentElement
      #oItem = self.Helper.GetObjectByInstance(
      #    'TransactionItem', itemElmt
      #).CastToLowestDescendant()
      oItem = self.Helper.GetObject(
           'TransactionItem',oRes.transactionitemid
      ).CastToLowestDescendant()

      oItem.SetApproval()
      
      #oItems.Next()
      oRes.Next()
    #-- while
    
    
  def Reject(self):
    self.SetAuth('R')

    oItems = self.Ls_TransactionItem
    while not oItems.EndOfList:
      itemElmt = oItems.CurrentElement
      oItem = self.Helper.GetObjectByInstance(
          'TransactionItem', itemElmt
      ).CastToLowestDescendant()

      oItem.SetReject()

      oItems.Next()
    #-- while

    oItems.DeleteAllPObjs()

  def OnDelete(self):
    helper = self.Helper
    # Sementara Dinonaktifkan karena belum bisa menangkap message raise dari database
    
    # Cek Transaksi RAK Antar Cabang
    oDistributionInfo = helper.GetObjectByNames('DistributionTransferInfo',
      {'TransactionId' : self.TransactionId}
    )
    if not oDistributionInfo.isnull :
      oDistributionInfo.Delete()

    # Delete Inbox Transaction
    if self.SubSystemCode in ['',None] :
      oInbox = helper.GetObjectByNames('InboxTransaction',{'TransactionId':self.TransactionId})    
      if not oInbox.isnull :      
        oInbox.Delete()
    
    # Delete Detail Transaction
    self.DeleteTransactionItem()
    
    # Cek Transaksi Invoice
    oInvoice = helper.GetObjectByNames('InvoiceProduct',{ 'PaymentTransactionId' : self.TransactionId } )
    
    if not oInvoice.isnull :
      oInvoice.PaymentTransactionId = None
      oInvoice.InvoicePaymentStatus = 'F'
    
    self.Config.FlushUpdates()
    
  def CancelTransaction(self):
    #self.AuthStatus = 'F'
    self.IsPosted = 'F'
    self.ChannelAccountNo = ''
    
    # Delete Detail Transaction
    self.DeleteTransactionItem()
    
  def DeleteTransactionItem(self):    
    # Delete Detail Transaction
    oItems = self.Ls_TransactionItem
    
    while not oItems.EndOfList:
      itemElmt = oItems.CurrentElement
      oItem = self.Helper.GetObjectByInstance(
          'TransactionItem', itemElmt
      ).CastToLowestDescendant()      
      self.Config.SendDebugMsg(oItem.classname)
      oItem.CancelTransaction()

      oItems.Next()
    #-- while
    oItems.DeleteAllPObjs()

  def AutoApproval(self):
    self.Approval()
    self.AuthUser = 'AUTO APPROVAL'

  def AutoApprovalUpdate(self):
    if self.AuthStatus == 'T' : 
      self.AuthStatus = 'F'
      self.Approval()
    
  def DeleteJournal(self):
    config = self.Config
    helper = self.Helper

    status = 0
    err_msg = ''
    
    if self.IsPosted != 'T' : return 0, 'Transaksi belum di posting'
    
    try:
      dMsg = {
        'subsystemcode' :'PKPU',
        'class_name' : 'Transaction',
        'key_id' : self.TransactionId,
        'trx_code': 'DeleteJournalItem', 
        'journal_no': self.LBatch.BatchNo, 
        'id_journalblock': self.JournalBlockId,
        'id_transaksi' : self.TransactionId,
      }
      
      sMessage = simplejson.dumps(dMsg)
      
      app = config.AppObject
      #acc_host = helper.GetObject('ParameterGlobal', 'GLSVCHST').Get()
      #acc_port = helper.GetObject('ParameterGlobal', 'GLSVCPRT').GetInt()
      acc_host = config.GetGlobalSetting('GLSVCHOST')
      acc_port = int(config.GetGlobalSetting('GLSVCPORT'))

      conn = app.UseCachedTCPConn(acc_host, acc_port)
      #conn = socketclient.TCPClient_STX_ETX((acc_host, acc_port))
      try:
        conn.SendSTXETXMessage(sMessage)
        #print sMessage
        #conn.Send(sMessage)
        #raise '',conn.ReadSTXETXMessage()
        resp = simplejson.loads(conn.ReadSTXETXMessage())
        
        #resp = simplejson.loads(conn.Receive())
      finally:
        app.ReleaseCachedTCPConn(conn, 1)
        #pass
      #--
    except:
      #return 2, str(sys.exc_info()[1])
      #status = 2
      #err_msg = str(sys.exc_info()[1])
      raise

    config.BeginTransaction()
    try:
      rstatus = resp[u'status']
      
      if rstatus == 0:
        status = 2
        err_msg = str(resp['errMsg'])
      elif rstatus == 1:
        self.IsPosted = 'F'
        self.JournalBlockId = None
      else:
        status = 2
        err_msg = 'undetermine status'
      config.Commit()
    except:
      config.Rollback()
      raise
      status = 2
      err_msg = str(sys.exc_info()[1])

    return status, err_msg
    
  def CreateJournal(self):
    config = self.Config
    helper = self.Helper

    status = 0
    err_msg = ''

    #return status, err_msg
    
    if self.AuthStatus != 'T': return 0, 'Transaksi belum otorisasi!'

    try:
      
      oJData = self.CreateJournalData()

      #-- send to accounting interface
      # Cek perubahan transaksi
      edit_mode = (self.JournalBlockId not in [None,0])
      sMessage = oJData.GetJSON(self.LBatch.BatchNo, edit_mode)
      
      app = config.AppObject
      #acc_host = helper.GetObject('ParameterGlobal', 'GLSVCHST').Get()
      #acc_port = helper.GetObject('ParameterGlobal', 'GLSVCPRT').GetInt()
      acc_host = config.GetGlobalSetting('GLSVCHOST')
      acc_port = int(config.GetGlobalSetting('GLSVCPORT'))

      conn = app.UseCachedTCPConn(acc_host, acc_port)
      #conn = socketclient.TCPClient_STX_ETX((acc_host, acc_port))

      try:
        conn.SendSTXETXMessage(sMessage)
        #print sMessage
        #conn.Send(sMessage)
        resp = simplejson.loads(conn.ReadSTXETXMessage())

        #resp = simplejson.loads(conn.Receive())
      finally:
        app.ReleaseCachedTCPConn(conn, 1)
        #pass
      #--
    except:
      return 2, str(sys.exc_info()[1])

    config.BeginTransaction()
    try:
      rstatus = resp[u'status']
      if rstatus == 0:
        status = 2
        err_msg = str(resp['errMsg'])
      elif rstatus == 1:
        self.IsPosted = 'T'
        self.JournalBlockId = resp['list_block'][str(self.TransactionId)]
      else:
        status = 2
        err_msg = 'undetermine status'

      config.Commit()
    except:
      config.Rollback()
      status = 2
      err_msg = str(sys.exc_info()[1])

    return status, err_msg
  #--

  def CreateJournalData(self):
    global MNEMONICS

    config = self.Config
    helper = self.Helper

    oJData  = JournalData(helper, self.LBatch)
    block   = oJData.InsertJournalBlock('Transaction',
      self.TransactionId,
      self.TransactionCode,
      self.Inputer,
      self.Description)

    listItem = self.Ls_TransactionItem

    listItem.First()
    while not listItem.EndOfList:
      objDetil = listItem.CurrentElement
      oItem = helper.GetObjectByInstance('TransactionItem', objDetil).CastToLowestDescendant()

      aJournalCode = oItem.ParameterJournalId

      oPJournal = helper.GetObjectByNames('ParameterJournal', {'JournalCode': aJournalCode})

      # get transaction details
      aSQLScript = oJData.GetSQL_LoadData(oPJournal)

      sParam = {'TransactionItemId': oItem.TransactionItemId}
      aSQLText = aSQLScript % sParam

      # process all journal codes
      oTCodes = oPJournal.GetTCodes()

      oRes = config.CreateSQL(aSQLText).RawResult

      # possibly wrong query definition, can be detected here
      if oRes.Eof:
        raise "Data error", "No data available for transaction journal"

      for oTCode in oTCodes:
        # *** main journal ***
        aItem = helper.CreateRecord()
        aItem.Class_Name = oItem.classname
        aItem.Key_Id = oItem.TransactionItemId
        aItem.Referensi = oItem.TransactionItemId
        aItem.Nomor_Rekening = oItem.RefAccountNo
        aItem.Nama_Rekening  = oItem.RefAccountName

        # Kode Account
        if oTCode.AccountBase == 'T':
          accountCode = (oTCode.AccountCode or '').strip()
          if accountCode == '':
            aItem.Kode_Account = oItem.AccountCode
          else:
            aItem.Kode_Account = oItem.GetFieldByName(accountCode) or ''

        elif oTCode.AccountBase == 'P':
          aItem.Kode_Account = oTCode.AccountCode

        elif oTCode.AccountBase == 'R' :
          aProductId  = oRes.ProductId
          aKode       = oTCode.AccountCode
          oProduk     = helper.GetObject('Product', aProductId)
          aSSL        = oProduk.GetAccountInterface(aKode).AccountCode
          aItem.Kode_Account = aSSL

        elif oTCode.AccountBase == 'I' :
          aContId     = oRes.GLIContainerId
          aKode       = oTCode.AccountCode
                    
          oContainer  = helper.GetObject('GLInterfaceContainer', aContId)
          aSSL        = oContainer.GetAccountInterface(aKode).AccountCode
          aItem.Kode_Account = aSSL

        elif oTCode.AccountBase == 'G' :
          aKode       = oTCode.AccountCode

          oTranGLInterface =  oItem.GetGLInterface(aKode)
          if oTranGLInterface.isnull :
            raise '', 'GL Interface Transaksi dengan kode %s tidak ditemukan ' % aKode
          aSSL        = oTranGLInterface.AccountCode
          aItem.Kode_Account = aSSL

        # end if elif
          
        #-- if
        if aItem.Kode_Account == '':
          raise '',"Kode Account pada detil transaksi tidak ditemukan (%d %s %s)" % (self.TransactionId, oTCode.AccountBase, aJournalCode)
  
        # cabang
        aSC = oTCode.BranchBase
        if aSC == 'T':
          aItem.Kode_Cabang = self.BranchCode
        elif aSC == 'M':
          aItem.Kode_Cabang = '001'
        else: # aSC == 'A':
          aItem.Kode_Cabang = oItem.BranchCode
        #-- if

        # Kode Valuta
        aSV = oTCode.CurrencyBase
        if aSV == 'I':
          aItem.Kode_Valuta = '000'
        elif aSV == 'T':
          aItem.Kode_Valuta = oItem.CurrencyCode
        else: # aSV == 'A'
          aItem.Kode_Valuta = oItem.CurrencyCode
        #-- if

        aItem.Jenis_Mutasi = MNEMONICS[(oRes.MutationType, oTCode.BaseSign)]
        aItem.Nilai_Mutasi = oRes.GetFieldValue(oTCode.AmountBase) or 0.0

        aItem.Kode_RC = ''

        if aItem.Kode_Valuta == '000':
          aItem.Kode_Kurs  = ''
          aItem.Nilai_Kurs = 1.0
        else:
          #aItem.Kode_Kurs    = oRes.Kode_Kurs or ''
          aItem.Kode_Kurs    = 'TT' or ''
          aItem.Nilai_Kurs   = oRes.GetFieldValue(oTCode.RateBase)

        aItem.Keterangan   = self.Description
        if oTCode.IsSendJournalDescription == 'T' :
          aItem.Keterangan_Jurnal = oTCode.Description
        else:
          aItem.Keterangan_Jurnal = ''

        oJData.InsertJournalItem(block, aItem)
        #-- if
      #-- for
      listItem.Next()
    #-- while

    return oJData

  def CreateRTFForPrint(self,templatePrint,dataPrint):
    SlipTransaksi = templatePrint % dataPrint
    corporate = self.Helper.CreateObject('Corporate')
    sBaseFileName = "kwintasi.rtf"
    sFileName = corporate.GetUserHomeDir() + '/' + sBaseFileName
    oFile = open(sFileName,'w')
    try:
      oFile.write(SlipTransaksi)
    finally:
      oFile.close()
  
    return sFileName
  
  def CreateTextForPrint(self,templatePrint,dataPrint):
    SlipTransaksi = templatePrint % dataPrint
    corporate = self.Helper.CreateObject('Corporate')
    sBaseFileName = "kwintasi.txt"
    sFileName = corporate.GetUserHomeDir() + '/' + sBaseFileName
    oFile = open(sFileName,'w')
    try:
      oFile.write(SlipTransaksi)
    finally:
      oFile.close()
  
    return sFileName
      
  def CreateTemplateSlipTrans(self):
    # Create Template Slip Transaksi
    templateSlip = "%(ReferenceNo)s"

    return templateSlip

  def GetDataSlipTrans(self):
    # Get data Slip Transaksi
    # Notes : Sesuaikan dengan template di fungsi CreateTemplateSlipTrans
    dataSlip = {'ReferenceNo' : self.ReferenceNo}

    return dataSlip

  def GetLeftMarginValidasi(self): return 0
  
  def GetDonor(self):
    DonorId = self.GetDonorId()
    oDonor = self.Helper.CreateObject('ExtDonor')

    if not oDonor.GetData(DonorId): raise 'PERINGATAN','Data Donor tidak ditemukan'
    
    return oDonor
    
  def GetDataDonor(self):
    if self.TransactionCode in ['SD001'] :
      # Get Info Donor
      DonorId = self.GetDonorId()
      oDonor = self.Helper.CreateObject('ExtDonor')
  
      if not oDonor.GetData(DonorId): raise 'PERINGATAN','Data Donor tidak ditemukan'
      return oDonor.full_name,oDonor.address
    else:
      return (self.ReceivedFrom or ''),'' 

  def GetDonorId(self):
    if self.TransactionCode not in ['SD001'] : return self.DonorId
    oItems = self.Ls_DonorTransactionItem
    oItems.First()
    itemElmt = oItems.CurrentElement
    return itemElmt.DonorId

  def GetAmountPerGroup(self):
    # 1 Zakat
    # 2 Infaq
    # 3 Wakaf
    # 4 Lainnya

    EntityValue = {
       1 : 0.0,
       2 : 0.0,
       3 : 0.0,
       4 : 0.0,
    }
    
    if self.TransactionCode in ['SD001'] :
      oItems = self.Ls_DonorTransactionItem
      while not oItems.EndOfList:
        oItem = oItems.CurrentElement
        if oItem.FundEntity not in [None,0]:
           if oItem.FundEntity in [4,5]:
             EntityValue[4] += oItem.Amount #(oItem.Amount * oItem.Rate)
           else:
             EntityValue[oItem.FundEntity] += oItem.Amount #(oItem.Amount * oItem.Rate)
           #-- end if else
        #-- end if
        oItems.Next()
      # end while
    return EntityValue[1],EntityValue[2],EntityValue[3],EntityValue[4]

  def GetZakahAmount(self):
    Zakat,Infaq,Wakaf,Lainnya = self.GetAmountPerGroup()
    return Zakat

  def GetBSZ(self, Detail):
    config = self.Config

    # Get Tools
    ToolsConvert = self.Helper.LoadScript('Tools.S_Convert')

    # Get Template
    PrintHelper = self.Helper.CreateObject('PrintHelper')
    templateBSZ = PrintHelper.LoadTemplate('bsz')

    # Get Info Donor
    DonorId = self.GetDonorId()
    oDonor = self.Helper.CreateObject('ExtDonor')

    if not oDonor.GetData(DonorId): raise 'PERINGATAN','Data Donor tidak ditemukan'

    Address = ToolsConvert.Divider(oDonor.address,50)
    if len(Address) == 1 : Address.append('')

    # Get Total
    Total = self.GetZakahAmount()

    # Set Terbilang
    Terbilang = ToolsConvert.Terbilang(config,Total,KodeMataUang='000')
    Terbilang = ToolsConvert.Divider(Terbilang,45)
    if len(Terbilang) == 1 : Terbilang.append('')

    # Get Nama Lembaga
    NamaLembaga = self.Helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
    
    dataBSZ = {
       'DONOR_NAMA' : oDonor.full_name,
       'NPWP' : oDonor.npwp_no or '',
       'NPWZ' : oDonor.npwz_no or '',
       'DONOR_ALAMAT1' : Address[0],
       'DONOR_ALAMAT2' : Address[1],
       'NAMA_LEMBAGA' : NamaLembaga,
       'USER_CETAK' : config.SecurityContext.InitUser,
       'WAKTU_CETAK' : config.FormatDateTime('dd-mm-yyyy hh:nn',config.Now()),
       'TGL_BAYAR' : config.FormatDateTime('dd-mm-yyyy',self.GetAsTDateTime('ActualDate')),
       'TOTAL' : config.FormatFloat('#,##0.00',Total),
       'TERBILANG1' : Terbilang[0],
       'TERBILANG2' : Terbilang[1],
       'CABANG' : NamaLembaga,
        }
    
    #PREFIX = ['EMAS','DAGANG','TANI','TAMBANG','TERNAK','JASA','RIKAZ']
    PREFIX = ['A','B','C','D','E','F','G']

    for i in range(Detail.RecordCount):
      rec = Detail.GetRecord(i)
      dataBSZ[PREFIX[i]+'_THN'] = str(rec.TahunPerolehan)
      dataBSZ[PREFIX[i]+'_KADAR'] = str(rec.Kadar)
      dataBSZ[PREFIX[i]+'_DASAR'] = config.FormatFloat('#,##0.00',rec.DasarPengenaan)
      dataBSZ[PREFIX[i]+'_ZAKAT'] = config.FormatFloat('#,##0.00',rec.Jumlah)
    # end for
        
    return self.CreateDataForPrint(templateBSZ,dataBSZ)

  def GetKwitansi(self):
    BranchCode = self.Config.SecurityContext.GetUserInfo()[4]
    """if BranchCode == '001' :
      if self.TransactionCode in ['SD001'] :
        return Voucher.GetKwitansiDonor(self)
      elif self.TransactionCode in ['CI','PEAR','PXAR','INVP'] :
        return Voucher.GetKwitansiPenerimaan(self)
      elif self.TransactionCode in ['DD001','CO','EAR','XAR','TI','PAD','FA','FAI','FAIP','CPIA','GT','CA','DT','INVS'] :
        return Voucher.GetKwitansiPengeluaranNew(self)      
      #elif self.TransactionCode in ['CA','DT','INVS'] :
      #  return Voucher.GetKwitansiPengeluaranUangMuka(self)  
      elif self.TransactionCode in ['CAR','DTR','CARR','INVSR'] :
        return Voucher.GetKwitansiPengembalianUangMuka(self)
      elif self.TransactionCode in ['INVC'] :
        return Voucher.GetKwitansiInvoice(self)
      else:
        raise '','Transaksi Tidak Memiliki Fungsi Cetak Kwitansi'
    else:"""
    
    if self.TransactionCode in ['SD001'] :
      return Voucher.GetKwitansiDonor(self)
    elif self.TransactionCode in ['FAD'] :
      return Voucher.GetKwitansiAssetDonor(self)
    elif self.TransactionCode in ['CI','INVP'] :
      return Voucher.GetKwitansiPenerimaanNew(self)
    elif self.TransactionCode in ['DD001','CO','PAD','FAI','FAIP','CPIA','GT','CA','DT','INVS'] :
      return Voucher.GetKwitansiPengeluaranNew(self)
    elif self.TransactionCode in ['FA']:
      return Voucher.GetKwitansiPembelianAsetNew(self)
    elif self.TransactionCode in ['CAR','DTR','CARR','CARB'] :
      return Voucher.GetKwitansiPengembalianUangMukaNew(self)
    elif self.TransactionCode in ['INVSR'] :  
      return Voucher.GetKwitansiInvestasiKembaliNew(self)
    elif self.TransactionCode in ['INVC'] :
      return Voucher.GetKwitansiInvoiceNew(self)  
    elif self.TransactionCode in ['EAR','PEAR','XAR','PXAR'] :
      EMPMUTATIONTYPE = {'EAR' : 'D','PEAR' : 'C','XAR' : 'D','PXAR' : 'C'}
      EmpMutationType = EMPMUTATIONTYPE[self.TransactionCode]        
      return Voucher.GetKwitansiPiutang(self,EmpMutationType)
    elif self.TransactionCode in ['TI','TIR'] :
      return Voucher.GetKwitansiTransferInternal(self)  
    else:
      raise '','Transaksi Tidak Memiliki Fungsi Cetak Kwitansi'          

      
  def CreateDataForPrint(self,templatePrint,dataPrint):
    SlipTransaksi = chr(15) + chr(27) + chr(69) + chr(27) + chr(67) + chr(32) # chr(0) + chr(6) #chr(31)

    leftmargin = self.GetLeftMarginValidasi() * ""
    if (templatePrint in [None,""] or
         len(templatePrint) <= 0 or
         len(dataPrint) == 0 ) :
      raise '','Template cetak kosong atau data yang dicetak tidak ada'
    # end if

    corporate = self.Helper.CreateObject('Corporate')
    if type(templatePrint) is types.StringType:
      #Template using string data type
      SlipTransaksi  += "\n\n\n" + leftmargin  + templatePrint % dataPrint
    elif type(templatePrint) is types.ListType:
      #Template using list data type
      tmp_slip = []
      for template in templatePrint:
        tmp_slip.append(leftmargin + template % dataPrint)
      #-endfor
      SlipTransaksi += '\n'.join(tmp_slip)
    #-endifelse

    sBaseFileName = "printtransaksi.txt"
    sFileName = corporate.GetUserHomeDir() + sBaseFileName
    oFile = open(sFileName,'w')
    try:
      oFile.write(SlipTransaksi)
    finally:
      oFile.close()

    return sFileName

  def SaveInbox(self,data):
    helper = self.Helper
    Inbox = helper.GetObjectByNames(
                'InboxTransaction',
                {'TransactionId':self.TransactionId}
            )

    if Inbox.isnull:
      Inbox = helper.CreatePObject(
            'InboxTransaction',
            self.TransactionCode
        )
      Inbox.TransactionId = self.TransactionId
      Inbox.SaveDataPacket(data)
    else:
      Inbox.UpdateDataPacket(data)
    # end if

    Inbox.Description = self.Description

class TransactionItem(pobject.PObject):
  # static variable
  pobject_classname = 'TransactionItem'
  pobject_keys = ['TransactionItemId']

  def OnCreate(self, param):
    self.TransactionId = param['Owner'].TransactionId

  def SetMutation(self, MutationType, Amount, Rate):
    aAmount = Amount
    aRate = Rate 
    
    if self.LTransaction.CurrencyCode != self.CurrencyCode: 
      if self.LTransaction.CurrencyCode != '000' and self.CurrencyCode == '000':
        aAmount = aAmount * aRate
        aRate = 1
      elif self.LTransaction.CurrencyCode == '000' and self.CurrencyCode != '000':
        aRate = self.LCurrency.Kurs_Tengah_BI
        aAmount = aAmount / aRate
      else:
        raise '','Transaksi Antar Valas Tidak Diperbolehkan'
      # end if else   
    #endi if
    self.MutationType = MutationType
    self.Amount = aAmount
    self.Rate = aRate
    self.EkuivalenAmount = aAmount * aRate

  def SetJournalParameter(self, ParameterJournalId):
    self.ParameterJournalId = ParameterJournalId

  def SetApproval(self):
    pass

  def SetReject(self):
    pass
  
  def OnDelete(self):
    self.LsGLInterface.DeleteAllPObjs()

  def CancelTransaction(self):
    helper = self.Helper
    
    self.MutationType = REVERSE_MNEMONIC[self.MutationType]

    # Cek Transaksi Sponsor
    oSTransaction = helper.GetObject('SponsorTransaction',self.TransactionItemId)
    if not oSTransaction.isnull:
      oSTransaction.Delete()
    # end if  

    # Cek Transaksi Mitra
    oVTransaction = helper.GetObject('VolunteerTransaction',self.TransactionItemId)
    if not oVTransaction.isnull:
      oVTransaction.Delete()
    # end if
    
    # Cek Transaksi Budget     
    oBTransaction = helper.GetObject('BudgetTransaction',self.TransactionItemId)    
    if not oBTransaction.isnull:      
      oBTransaction.Delete()
    # end if  
  
    # Cek Transaksi Pengembalian Uang Muka
    oReturnInfo = helper.GetObjectByNames('CashAdvanceReturnInfo',
       {'ReturnTransactionId' : self.TransactionId}
    )
    if not oReturnInfo.isnull : 
      oCATransact = helper.GetObjectByNames('CATransactItem',
         {'TransactionId' : oReturnInfo.SourceTransactionId})
      oCATransact.ReturnTransactionItemId = 0    
      
      oReturnInfo.Delete()
    # end if
    
    # Cek Transaksi RAK Antar Cabang
    # oDistributionInfo = helper.GetObjectByNames('DistributionTransferInfo',
    #   {'TransactionId' : self.TransactionId}
    # )
    # if not oDistributionInfo.isnull :
    #   oDistributionInfo.Delete()

    # Cek Transaksi Invoice
    oInvoice = helper.GetObjectByNames('InvoiceProduct',
       { 'PaymentTransactionItemId' : self.TransactionItemId } 
    )
    
    if not oInvoice.isnull :
      oInvoice.PaymentTransactionId = None
      oInvoice.PaymentTransactionItemId = None
      oInvoice.InvoicePaymentStatus = 'F'
    
    self.Config.FlushUpdates()

  def AddAmount(self, Amount):
    self.Amount += Amount
    self.EkuivalenAmount += (Amount * self.Rate)

  def CreateBudgetTransaction(self,BudgetId):
    oBudgetTrans = self.Helper.CreatePObject('BudgetTransaction')
    oBudgetTrans.BudgetId = BudgetId
    oBudgetTrans.TransactionItemId = self.TransactionItemId
    oBudgetTrans.LBudget.UpdateRealization(self.Amount * self.Rate)
    oBudgetTrans.BudgetTransType = 'A'
    
  def CreateBudgetTransactionReturn(self,BudgetId):
    oBudgetTrans = self.Helper.CreatePObject('BudgetTransaction')
    oBudgetTrans.BudgetId = BudgetId
    oBudgetTrans.TransactionItemId = self.TransactionItemId
    oBudgetTrans.LBudget.UpdateRealization(-(self.Amount * self.Rate))
    oBudgetTrans.BudgetTransType = 'R'
      
  def CreateBSZTransaction(self,BSZId):
    oBSZTran = self.Helper.CreatePObject('BSZTransaction')
    oBSZTran.BSZId = BSZId
    oBSZTran.TransactionItemId = self.TransactionItemId

  def SetAccountInterface(self,AccountInterface):
    self.AccountCode = AccountInterface
  
  def AddGLInterface(self, aCode, aAccountCode, aDescription):
    oGLInterface = self.Helper.CreatePObject('TransItemGLInterface')
    oGLInterface.TransactionItemId = self.TransactionItemId
    oGLInterface.GLInterfaceCode = aCode
    oGLInterface.AccountCode = aAccountCode
    oGLInterface.Description = aDescription

  def GetGLInterface(self, aCode) :
    oTranItemGLInterface  = self.Helper.GetObjectByNames('TransItemGLInterface', 
             { 'TransactionItemId' : self.TransactionItemId ,
               'GLInterfaceCode' : aCode
             }
          )
    return oTranItemGLInterface

class TransItemGLInterface(pobject.PObject):
  # static variable
  pobject_classname = 'TransItemGLInterface'
  pobject_keys = ['GLInterfaceId']


class AccountTransactionItem(TransactionItem):
  # static variable
  pobject_classname = 'AccountTransactionItem'

  def OnCreate(self, param):
    TransactionItem.OnCreate(self, param)
    oAccount = param['Account']
    self.AccountNo = oAccount.AccountNo
    self.BranchCode = oAccount.BranchCode
    self.CurrencyCode = oAccount.CurrencyCode

    self.RefAccountNo = oAccount.AccountNo
    self.RefAccountName = oAccount.AccountName
    self.IsUpdateBalance = 'T'

    self.AccountCode = oAccount.GetAccountInterface()

  def SetMutation(self, MutationType, Amount, Rate):
    TransactionItem.SetMutation(self, MutationType, Amount, Rate)
    # place here if you want to update balance on transaction

  def SetApproval(self):
    oAccount = self.LFinancialAccount.CastToLowestDescendant()
    if self.IsUpdateBalance != 'F' : 
      oAccount.UpdateBalance(self.MutationType, self.Amount)

  def CancelTransaction(self):
    TransactionItem.CancelTransaction(self)
    oAccount = self.LFinancialAccount.CastToLowestDescendant()        
    if self.LTransaction.AuthStatus == 'T' and self.IsUpdateBalance != 'F' :
      isBalanceIgnored = 0
      if self.LTransaction.TransactionCode == 'TB' :
        isBalanceIgnored = 1
      #if self.LTransaction.TransactionType = 'TB' :  
      oAccount.UpdateBalance(self.MutationType, self.Amount,isBalanceIgnored)
     
  def SetFundEntity(self,FundEntity):        
    self.FundEntity = FundEntity
    
  def SetCollectionEntity(self, aFundEntity):
    self.FundEntity = aFundEntity
    oAccount = self.LFinancialAccount.CastToLowestDescendant()
    self.AccountCode = oAccount.GetCollectionInterface(aFundEntity)

  def SetDistributionEntity(self, aFundEntity):
    self.FundEntity = aFundEntity
    oAccount = self.LFinancialAccount.CastToLowestDescendant()
    self.AccountCode = oAccount.GetDistributionInterface(aFundEntity)
  
  def GetAccountName(self):
    return self.LFinancialAccount.AccountName

class DonorTransactionItem(AccountTransactionItem):
  # static variable
  pobject_classname = 'DonorTransactionItem'

  def OnCreate(self, param):
    AccountTransactionItem.OnCreate(self, param)
    self.DonorId = param['DonorId']

    oAccount = param['Account']
    #self.AccountCode = oAccount.GetCollectionInterface()

  def SetMutation(self, Amount, Rate):
    #self.CurrencyCode = '000'
    #Amount = Amount * Rate
    #Rate = 1
    
    AccountTransactionItem.SetMutation(self, 'C', Amount, Rate)

  def SetReverseMutation(self, Amount, Rate):
    AccountTransactionItem.SetMutation(self, 'D', Amount, Rate)

class ZakahDistTransactItem(AccountTransactionItem):
  # static variable
  pobject_classname = 'ZakahDistTransactItem'

  def OnCreate(self, param):
    AccountTransactionItem.OnCreate(self, param)
    self.Ashnaf = param['Ashnaf']

    #oAccount = param['Account']
    #self.AccountCode = oAccount.GetDistributionInterface(self.FundEntity)

  #def SetMutation(self, Amount, Rate):
  #  AccountTransactionItem.SetMutation(self, 'D', Amount, Rate)


class CashAdvanceTransactItem(AccountTransactionItem):
  # static variable
  pobject_classname = 'CashAdvanceTransactItem'

class AccReceivableTransactItem(AccountTransactionItem):
  # static variable
  pobject_classname = 'AccReceivableTransactItem'

class DeprAssetTransactItem(AccountTransactionItem):
  # static variable
  pobject_classname = 'DeprAssetTransactItem'

class FixedAssetTransactItem(DeprAssetTransactItem):
  # static variable
  pobject_classname = 'FixedAssetTransactItem'

  def SetFundEntity(self, aFundEntity) :
    self.FundEntity = aFundEntity
    oAsset = self.LFixedAsset
    #if oAsset.LAssetCategory.AssetType == 'T' :

    #if aFundEntity == 4 :
      # Account Code Amil diambil dari GL Interface Kategori Asset
    #  AccountCode = oAsset.GetAmilCostForAssetAccount() #self.Helper.GetObject('ParameterGlobal', 'GLIASSETFROMAMIL').Get()

    #else:
      # Account Code Selain diambil dari Produk
    AccountCode = oAsset.GetAssetKelolaanPlusAccount(aFundEntity)

    self.AddGLInterface('ASET_KELOLA', AccountCode,'Penambahaan Aset Kelolaan')

class InvestmentTransactItem(AccReceivableTransactItem):
  # static variable
  pobject_classname = 'InvestmentTransactItem'

  def SetMutation(self, MutationType, PrincipalAmount, ShareAmount, Rate):
    AccReceivableTransactItem.SetMutation(self, MutationType, PrincipalAmount, Rate)
    
    Amount = PrincipalAmount + ShareAmount
    self.Amount = Amount
    self.Rate = Rate
    self.EkuivalenAmount = Amount * Rate

    self.PrincipalAmount = PrincipalAmount
    self.ShareAmount = ShareAmount
    self.InvestmentTIType = 'P'
  
  def SetApproval(self):
    oAccount = self.LInvestment
    if self.IsUpdateBalance != 'F' :
      oAccount.UpdateBalance(self.MutationType, self.PrincipalAmount)

  def CancelTransaction(self):
    AccountTransactionItem.CancelTransaction(self)
    oAccount = self.LInvestment
    if self.LTransaction.AuthStatus == 'T' and self.IsUpdateBalance != 'F' :
      isBalanceIgnored = 0
      if self.LTransaction.TransactionCode == 'TB' :
        isBalanceIgnored = 1
      oAccount.UpdateBalance(self.MutationType, self.PrincipalAmount,isBalanceIgnored)

class CATransactItem(CashAdvanceTransactItem):
  # static variable
  pobject_classname = 'CATransactItem'

  def OnDelete(self) :
    CashAdvanceTransactItem.OnDelete()
    if self.DistributionTransferId not in [0,None]:
      oTransferInfo = helper.GetObject( 'DistributionTransferInfo', self.DistributionTransferId)
      oTransferInfo.UpdateBalance( '+', request[u'Amount'])

class CAReturnTransactItem(CashAdvanceTransactItem):
  # static variable
  pobject_classname = 'CAReturnTransactItem'
  
  def SetReturnInfo(self,oCATransact):
    # Create Cash Advance Return Info 
    oReturnInfo = self.Helper.CreatePObject('CashAdvanceReturnInfo')
    oReturnInfo.SourceTransactionId = oCATransact.LTransaction.TransactionId
    oReturnInfo.ReturnTransactionId = self.LTransaction.TransactionId
    oReturnInfo.BranchCode = self.Config.SecurityContext.GetUserInfo()[4]
    
    oCATransact.ReturnTransactionItemId = self.TransactionItemId
    
class CashAdvanceReturnInfo(pobject.PObject):
  # static variable
  pobject_classname = 'CashAdvanceReturnInfo'
  pobject_keys = ['SourceTransactionId']
  
class BSZ(pobject.PObject):
  # static variable
  pobject_classname = 'BSZ'
  pobject_keys = ['BSZId']

  def OnDelete(self):
    self.Ls_BSZDetail.DeleteAllPObjs()
    self.Ls_BSZTransaction.DeleteAllPObjs()
      
  def GetTotal(self):
    sSQL = 'select sum(zakahvalue) from bszdetail where bszid=%d' % self.BSZId
    res = self.Config.CreateSQL(sSQL).rawresult
    
    return res.GetFieldValueAt(0) or 0.0
  
  def GetTransactionDate(self) :
    config = self.Config
    sOQL = "select from BSZTransaction \
              [BSZId = :BSZID] \
              (LTransaction.LTransaction.ActualDate, self); \
    "

    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('BSZID', self.BSZId)
    oql.ApplyParamValues()
    oql.active = 1
    resBSZTran = oql.rawresult

    if not resBSZTran.Eof :
      y, m, d = resBSZTran.ActualDate[:3]
      return config.ModLibUtils.EncodeDate(y, m, d)
    else :
      return self.GetAsTDateTime('BSZDate')

  def GenerateBSZData(self):
    helper = self.Helper
    config = self.Config
    
    oDonor = self.LDonor

    ToolsConvert = helper.LoadScript('Tools.S_Convert')
  
    Address = ToolsConvert.Divider(oDonor.Address,50)
    if len(Address) == 1 : Address.append('')
  
    # Get Total
    #Total = self.GetZakahAmount()
    Total = self.GetTotal()
  
    # Set Terbilang
    Terbilang = ToolsConvert.Terbilang(config,Total,
              KodeMataUang = '000',
              NamaMataUang = 'Rupiah')
    #Terbilang = ToolsConvert.Divider(Terbilang,45)
    #if len(Terbilang) == 1 : Terbilang.append('')
  
    # Get Nama Lembaga
    NamaLembaga = helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
  
    # Prepare Data
    Now = config.Now()
    dataBSZ = {
       'BSZNO' : self.BSZNumber , #oDonor.full_name,
       'DONOR_NAMA' : oDonor.Full_Name , #oDonor.full_name,
       'NPWP' : oDonor.NPWP_No , #oDonor.npwp_no or '',
       'NPWZ' : oDonor.NPWZ_No , #oDonor.npwz_no or '',
       'DONOR_ALAMAT' : oDonor.Address,
       'NAMA_LEMBAGA' : NamaLembaga,
       'USER_CETAK' : config.SecurityContext.InitUser,
       'WAKTU_CETAK' : config.FormatDateTime('dd-mm-yyyy hh:nn',Now),
       'TGL_BAYAR' : config.FormatDateTime('dd-mm-yyyy',self.GetTransactionDate()),
       'TOTAL' : config.FormatFloat('#,##0.00',Total),
       'TERBILANG' : Terbilang,
       'CABANG' : NamaLembaga,
       'P1':'','P2':'','P3':'','P4':'','P5':'',
       'P6':'','P7':'','P8':'','P9':'','P10':'',
       'P11':'','P12':'','P13':'','P14':'','P15':'',
       'Z1':'','Z2':'','Z3':'','Z4':'','Z5':'',
       'Z6':'','Z7':'','Z8':'','Z9':'','Z10':'',
       'Z11':'','Z12':'','Z13':'','Z14':'','Z15':'',
        }

    ## PROCESS NPWP_NO
    # get digit no
    npwp = oDonor.NPWP_No or ''
    npwpD = '' #.join(i for i in npwp if i.isdigit())
    for c in npwp:
      if c.isdigit():
        npwpD += c
  
    # insert to dataBSZ
    idx = 1
    for c in npwpD:
      dataBSZ['P%d'%idx] = c
      idx += 1
  
    ## PROCESS NPWZ_NO
    # get digit no
    npwz = oDonor.NPWZ_No or ''
    npwzZ = '' #''.join(i for i in npwz if i.isdigit())
    for c in npwz:
      if c.isdigit():
        npwzZ += c
  
    # insert to dataBSZ
    idx = 1
    for c in npwzZ:
      dataBSZ['Z%d'%idx] = c
      idx += 1
  
    #raise '',dataBSZ
    #PREFIX = ['EMAS','DAGANG','TANI','TAMBANG','TERNAK','JASA','RIKAZ']
    PREFIX = ['A','B','C','D','E','F','G']
  
    #Detail = parameters.uipDetail
    
    sSQL = 'select * from bszdetail where bszid=%d order by item' % self.BSZId
  
    res = config.CreateSQL(sSQL).rawresult
  
    #for i in range(Detail.RecordCount):
    i = 0
    while not res.Eof:
      TahunPerolehan = ''
      Kadar = ''
      if res.Year != 0 and res.Percentage != 0 :
        TahunPerolehan = str(res.Year)
        Kadar = str(res.Percentage)
  
      dataBSZ[PREFIX[i]+'_THN'] = TahunPerolehan
      dataBSZ[PREFIX[i]+'_KADAR'] = Kadar
      dataBSZ[PREFIX[i]+'_DASAR'] = config.FormatFloat('#,##0.00',res.BasicValue)
      dataBSZ[PREFIX[i]+'_ZAKAT'] = config.FormatFloat('#,##0.00',res.ZakahValue)
  
      res.Next()
      i+=1

    # end while  
  
    return dataBSZ
        
class BSZDetail(pobject.PObject):
  # static variable
  pobject_classname = 'BSZDetail'
  pobject_keys = ['BSZDetailId']

class BSZTransaction(pobject.PObject):
  # static variable
  pobject_classname = 'BSZTransaction'
  pobject_keys = ['TransactionItemId']

class GLTransactionItem(TransactionItem):
  # static variable
  pobject_classname = 'GLTransactionItem'

  def OnCreate(self, param):
    TransactionItem.OnCreate(self, param)

    self.BranchCode = self.Config.SecurityContext.GetUserInfo()[4]
    self.CurrencyCode = param['CurrencyCode']
    self.RefAccountNo = param['GLAccount']
    self.AccountCode = param['GLAccount']
    self.GLNumber = param['GLAccount']

  def GetAccountName(self):
    return self.GLName

class JournalData:
  def __init__(self, helper, oBatch):
    self.helper = helper
    self.config = helper.Config
    self.batch = oBatch
    self.listBlock = []

  def InsertJournalBlock(self, class_name, key_id, transaction_tag, user_input, keterangan=''):
    keterangan = keterangan.replace("`", "")
    dData = {
      'subsystemcode'   : 'PKPU',
      'class_name'      : class_name,
      'key_id'          : key_id,
      'transaction_tag' : transaction_tag,
      'user_input'      : user_input,
      'keterangan'      : keterangan,
      'details'         : []
    }
    self.listBlock.append(dData)
    return dData

  def InsertJournalItem(self, aBlock, aData):
    if aData.Jenis_Mutasi == 'D':
      aData.Debit  = aData.Nilai_Mutasi
      aData.Credit = 0.0
    else:
      aData.Debit  = 0.0
      aData.Credit = aData.Nilai_Mutasi
    #-- if.else

    keterangan = aData.Keterangan
    keterangan = keterangan.replace("`", "")
    dData = {
      'kode_account'  : aData.Kode_Account,
      'kode_cabang'   : aData.Kode_Cabang,
      'kode_valuta'   : aData.Kode_Valuta,
      'rc_code'       : aData.Kode_RC,
      'debit'         : aData.Debit,
      'credit'        : aData.Credit,
      'kode_kurs'     : aData.Kode_Kurs,
      'nilai_kurs'    : aData.Nilai_Kurs,
      'keterangan'    : keterangan,
      'nomor_rekening' : aData.Nomor_Rekening,
      'nama_rekening'  : aData.Nama_Rekening,
      'referensi'     : aData.Referensi,
      'source_class_id' : aData.Class_Name,
      'source_key_id' : aData.Key_Id,
      'keterangan_jurnal' : aData.Keterangan_Jurnal
    }

    aBlock['details'].append(dData)
    return dData

  def GetSQL_LoadData(self, oParam):
    oGlobalParam = self.config.CreatePObjImplProxy("ParameterGlobal")
    oGlobalParam.Key = 'SQLJIPATH'

    aBaseDir = self.config.HomeDir + oGlobalParam.NILAI_PARAMETER_STRING + '/'
    return utils.GetStringFromFile(aBaseDir + oParam.DataSource)

  def GetHISQL_LoadData(self, oParam):
    oGlobalParam = self.config.CreatePObjImplProxy("ParameterGlobal")
    oGlobalParam.Key = 'SQLHJIPATH'

    aBaseDir = self.config.HomeDir + oGlobalParam.NILAI_PARAMETER_STRING + '/'
    return utils.GetStringFromFile(aBaseDir + oParam.DataSource)

  def GetMsgString(self, journal_no):
    dMsg = {'trx_code': 'CreateJournalItem', 'journal_no': journal_no, 'list_block': self.listBlock}
    sMsg = str(dMsg)
    return sMsg

  def GetJSON(self, journal_no, edit_mode):
    dMsg = {'trx_code': 'CreateJournalItem', 'journal_no': journal_no, 'edit_mode' : edit_mode ,'list_block': self.listBlock}
    sMsg = simplejson.dumps(dMsg)
    return sMsg

class Inbox(pobject.PObject):
    #Static variable
    pobject_classname = 'Inbox'
    pobject_keys = ['InboxId']

    def pobject_init(self):
        corporate = self.Helper.CreateObject('Corporate')
        inboxhomedir = self.Config.GetGlobalSetting('INBOXHOMEDIR')
        #s_pod = self.Helper.GetObject('ParameterGlobal', 'POD').GetFormatted()
        s_pod = self.Config.FormatDateTime('yyyymmdd', self.Config.Now())

        cabang = corporate.LoginContext.Kode_Cabang
        #self.inbox_location = '%sinbox\\%s\\' % (self.Config.GetHomeDir(), cabang)
        self.inbox_location = '%s\\%s\\%s\\' % (inboxhomedir, s_pod, cabang)
        self.login_context = corporate.LoginContext

    #public method
    def OnCreate(self, aKodeInbox = None):
        Now = self.Config.Now()
        self.BranchCode       = self.login_context.Kode_Cabang
        #self.Level_User   = self.login_context.Level_User
        #self.Grup_User    = ''
        #self.Limit        = 0
        #self.Is_Terproses = 'F'
        #self.Status       = 'V'
        self.UserId      = self.Config.SecurityContext.UserID

        self.InputDate = int(Now)
        self.InputTime = Now
        self.FileName    = 'jam.%s-%d.packet' % (
            self.Config.FormatDateTime('hh.nn.ss', self.Config.Now()),
            self.getID()
        )

        #if aKodeInbox != None:
        self.KodeInbox = aKodeInbox

    def OnDelete(self):
        aFileInbox = self.inbox_location + self.FileName
        #utils.SafeDeleteFile(aFileInbox)
        #self.PObject.Ls_Override.DeleteAllPObjs()
        self.Ls_History.DeleteAllPObjs()

    def getID(self):
        return self.InboxId

    def SaveDataPacket(self, oPacket):
        aFileInbox = self.inbox_location + self.FileName

        #aDefinition, aData = oPacket.GetSerializationString()
        #aHeader = hex(len(aDefinition)).ljust(8)
        #aText = aHeader + aDefinition + aData

        if not utils.DirectoryExist(self.inbox_location):
            utils.CreateDeepDirectory(self.inbox_location)

        #utils.SaveStringToFile(aText, aFileInbox)
        oPacket.SaveToFile(aFileInbox)

    def UpdateDataPacket(self,oPacket):
        self.GenerateHistory()
        
        self.FileName    = 'jam.%s-%d.packet' % (
            self.Config.FormatDateTime('hh.nn.ss', self.Config.Now()),
            self.getID()
        )
        
        aFileInbox = self.inbox_location + self.FileName
        if not utils.DirectoryExist(self.inbox_location):
            utils.CreateDeepDirectory(self.inbox_location)
        
        Now = self.Config.Now()    
        self.UserId      = self.Config.SecurityContext.UserID
        self.InputDate = int(Now)
        self.InputTime = Now
        self.BranchCode = self.Config.SecurityContext.GetUserInfo()[4]
        oPacket.SaveToFile(aFileInbox)
        
    def LoadDataPacket(self, BranchCode = None):
        self.inbox_location = self.LoadInboxLocation( BranchCode)
        aFileInbox = self.inbox_location + self.FileName
        #aText = utils.GetStringFromFile(aFileInbox)
        #n = int(aText[:8].strip(), 16)

        #aDefinition = aText[8:8+n]
        #aData = aText[8+n:]

        ph = self.Config.AppObject.CreatePacket()
        #ph.Packet.SetSerializationString(aDefinition, aData)
        ph.Packet.LoadFromFile(aFileInbox)

        return ph

    def LoadInboxLocation(self, BranchCode = None):
        inboxhomedir = self.Config.GetGlobalSetting('INBOXHOMEDIR')
        s_pod = self.Config.FormatDateTime('yyyymmdd', self.GetAsTDateTime('InputDate'))
        
        if BranchCode not in ['', None] :
          cabang = BranchCode
        else:
          cabang = self.BranchCode
        # end if  
        
        return '%s\\%s\\%s\\' % (inboxhomedir, s_pod, cabang)
         
    def Override(self):
        self.Status = 'T'

    def Otorisasi(self):
        self.Status = 'O'

    def getFormName(self):
      return self.LParameterInbox.Nama_Form

    def GenerateHistory(self):
        oHistory = self.Helper.CreatePObject('InboxHistory')
        oHistory.FileName = self.FileName
        oHistory.InputDate = self.GetAsTDateTime('InputDate')
        oHistory.InputTime = self.GetAsTDateTime('InputTime')
        oHistory.InboxId = self.InboxId
        oHistory.UserId = self.UserId
        oHistory.BranchCode = self.Config.SecurityContext.GetUserInfo()[4]
        oHistory.NextInboxHistory = self.LastInboxHistoryId or 0

        self.LastInboxHistoryId = oHistory.InboxHistoryId

class InboxTransaction(Inbox):
    #Static variable
    pobject_classname = 'InboxTransaction'

    def OnCreate(self, Kode_Inbox):
        Inbox.OnCreate(self, Kode_Inbox)
        #Inbox.OnCreate(self, Kode_Inbox[0])
        #self.Kode_Transaksi = Kode_Inbox[1]

class InboxHistory(pobject.PObject):
    pobject_classname = 'InboxHistory'
    pobject_keys = ['InboxHistoryId']
    
class DistributionTransferInfo(pobject.PObject):
    pobject_classname = 'DistributionTransferInfo'
    pobject_keys = ['DistributionId']
    
    def OnCreate(self):
      self.ReportStatus = 'F'
      self.ReportTransactionId = 0
      
    def UpdateBalance( self, aType, aAmount):
      if aType == '+' :
        self.Balance += aAmount
      else : # aType == '-'
        self.Balance -= aAmount
    
    def OnDelete(self):
      #sqlCheck = 'select count(transactionitemid) from accounttransaction where '
      oqlCheck = "select from CATransactItem \
         [DistributionTransferId = :Id ] \
         (self)  \
         "
    
    def SetBalance(self,aAmount) :
      self.Balance = aAmount

      # Hitung RAK yang sudah dipakai oleh cabang
      # ( untuk mengcover proses ubah transaksi )
      SQLSum = "select sum(amount)  as TotalUsed \
          from transaction.TransactionItem a, \
              transaction.AccountTransactionItem b \
          where a.TransactionItemId = b.TransactionItemId \
            and AccountTIType='C' \
            and DistributionTransferId = %d " % self.DistributionId

      oRes = self.Config.CreateSQL(SQLSum).RawResult
      TotalUsed = oRes.TotalUsed or 0.0

      if TotalUsed > 0.0:
        self.Balance -= TotalUsed

class FixedAssetTransactInfo(pobject.PObject):
    # static variable
    pobject_classname = 'FixedAssetTransactInfo'
    pobject_keys = ['TransactionItemId']
    
    def OnCreate(self,param):
      self.TransactionItemId = param['TransactionItem'].TransactionItemId
      self.AccountNo = param['FixedAsset'].AccountNo
      
    def SetSellAmount(self,Amount):
      self.SellAmount = Amount
      
    def SetCashAdvance(self,Amount):
      self.CashAdvance = Amount  
