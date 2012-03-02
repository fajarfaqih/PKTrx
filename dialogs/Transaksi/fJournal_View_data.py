import com.ihsan.foundation.pobjecthelper as phelper
import simplejson

def FormSetDataEx(uideflist, parameter):
  config = uideflist.config

  helper = phelper.PObjectHelper(config)
  
  param = parameter.FirstRecord

  TransactionId = param.TransactionId
  oTransaction = helper.GetObject('Transaction',TransactionId)
  
  if oTransaction.IsPosted == 'F' :
    raise 'PERINGATAN','Transaksi Belum Memiliki Jurnal Accounting. Silahkan otorisasi atau posting ulang jurnal'
  
  BatchNo = oTransaction.LBatch.BatchNo
  JournalBlockId = oTransaction.JournalBlockId
  
  # Set Info Journal

  recJournal = uideflist.uipJournal.Dataset.AddRecord()

  recJournal.journal_no = BatchNo
  recJournal.journal_date = oTransaction.LBatch.GetAsTDateTime('BatchDate')
  recJournal.transaction_date = oTransaction.GetAsTDateTime('TransactionDate')
  recJournal.user_create = oTransaction.Inputer
  
  
  # Set Info Journal Item
  uipJournalItem = uideflist.uipJournalItem
  
  request = {}
  request['trx_code'] = 'GetInfoJournal'
  request['journal_no'] = BatchNo
  request['Id_Transaksi'] = TransactionId
  request['Id_Journal_Block']  = JournalBlockId

  sMsg = simplejson.dumps(request)

  app = config.AppObject

  #acc_host = helper.GetObject('ParameterGlobal', 'GLSVCHST').Get()
  #acc_port = helper.GetObject('ParameterGlobal', 'GLSVCPRT').GetInt()
  acc_host = config.GetGlobalSetting('GLSVCHOST')
  acc_port = int(config.GetGlobalSetting('GLSVCPORT'))
  conn = app.UseCachedTCPConn(acc_host, acc_port)

  try:
    conn.SendSTXETXMessage(sMsg)
    response =  simplejson.loads(conn.ReadSTXETXMessage())

  finally:
    app.ReleaseCachedTCPConn(conn, 1)
  #--


  config.BeginTransaction()
  try:
    status = response[u'status']

    if status == 0:
      raise 'accounting', response[u'errMsg']
    elif status == 1:
      for list_journalitem in response[u'list_journal'] :
        config.SendDebugMsg('1')
        rec = uipJournalItem.Dataset.AddRecord()
        rec.Account_Code  = str(list_journalitem[u'Account_Code'])
        config.SendDebugMsg('2')
        rec.Account_Name  = str(list_journalitem[u'Account_Name'].encode('ascii','ignore'))
        config.SendDebugMsg('3')
        rec.Branch_Code   = str(list_journalitem[u'Branch_Code'])
        config.SendDebugMsg('4')
        rec.Branch_Name   = str(list_journalitem[u'Branch_Name'])
        config.SendDebugMsg('5')
        rec.Currency_Code = str(list_journalitem[u'Currency_Code'])
        config.SendDebugMsg('6')
        rec.Kode_Kurs     = str(list_journalitem[u'Kode_Kurs'] or '')
        config.SendDebugMsg('7')
        rec.Nilai_Kurs    = list_journalitem[u'Nilai_Kurs']
        config.SendDebugMsg('8')
        rec.Nama_RC       = str(list_journalitem[u'Nama_RC'] or '')
        config.SendDebugMsg('9')
        rec.Nomor_Rekening= str(list_journalitem[u'Nomor_Rekening'])
        config.SendDebugMsg('10')
        rec.Nama_Rekening = str(list_journalitem[u'Nama_Rekening'] or '')
        config.SendDebugMsg('11')
        rec.Amount_Debet  = list_journalitem[u'Amount_Debet']
        config.SendDebugMsg('12')
        rec.Amount_Credit = list_journalitem[u'Amount_Credit']

    else:
      raise 'accounting', 'undetermine status'

    config.Commit()
  except:
    config.Rollback()
    raise '',list_journalitem

  return 0
