# TransactionHelper.py

def GetTransactionNumber(config,transcode='DEFAULT',cashcode='') :
  MapCode = {
    'SD001' : 'KM',
    'DD001' : 'KK',
    'EAR'   : 'KK',
    'PEAR'  : 'KM',
    'TI'    : 'KM',
    'PAD'   : 'KM',
    'CI' : 'KM',
    'CO' : 'KK',    
    'DEFAULT' : 'GT',
  }
  rsSeq = config.CreateSQL("select nextval('seq_transactionnumber')").RawResult
  y,m,d = config.ModLibUtils.DecodeDate(config.Now())
  branchCode = config.SecurityContext.GetUserInfo()[4]
  
  return "%s-%s-%s-%s-%s" % (
          MapCode[transcode],
          str(y),
          branchCode,
          cashcode,
          str(rsSeq.GetFieldValueAt(0)).zfill(7))  


def DeleteTransactionJournal(oTran,OperationType='U'):
  # OperationType ==> D = Delete  , U = Update
  
  # Fungsi ini digunakan sebagai helper yang diakses oleh 
  # fungsi penghapusan transaksi dan update transaksi
  # untuk memudahkan maintenance proses delete journal
  
  # PERINGATAN : JANGAN GUNAKAN FUNGSI INI DI DALAM SCOOP SYNTAX DB TRANSACTIONAL 
  # KARENA DI DALAM FUNGSI DeleteJournal() ADA INTERFACE DENGAN APLIKASI ACCOUNTING
  # By : Wisnu
  
  oTran.DeleteJournal()