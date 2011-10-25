MAPEntity = {'Z': 1, 'I': 2, 'W': 3}
colors = {0:-2147483624 , 1:16777215}

class fInterFundTransfer :

  # ****  FORM EVENT & METHOD ****
  
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication

  def SourceAfterLookUp(self,ctlLink,Link):
    uip = self.uipTransaction
    uip.Edit()
    uip.SourceCategory = uip.GetFieldValue('LAccountSource.FundCategory')
    uip.CurrencyCode = uip.GetFieldValue('LAccountSource.CurrencyCode')
    uip.FundEntitySource = MAPEntity[uip.GetFieldValue('LAccountSource.FundCategory') or 'I']
    uip.SourceRate = uip.GetFieldValue('LAccountSource.LCurrency.Kurs_Tengah_BI')
    uip.SourceAmount = 0.0
    self.SetSrcCtlRate()
    self.SetEkuivalenAmount()
    
  def DestAfterLookup(self,ctlLink,Link):
    uip = self.uipTransaction
    uip.Edit()
    uip.FundEntityDestination = MAPEntity[uip.GetFieldValue('LAccountDestination.FundCategory') or 'I']
    uip.DestRate = uip.GetFieldValue('LAccountDestination.LCurrency.Kurs_Tengah_BI')
    uip.DestAmount = 0.0
    
    self.SetDestCtlRate()
    self.SetEkuivalenAmount()

  def bSimpanClick(self, sender):
    app = self.app
    if self.app.ConfirmDialog('Yakin simpan transaksi ?'):
      self.CheckInput()

      self.FormObject.CommitBuffer()
      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr == 1:
        self.app.ShowMessage(res.ErrMessage)
        sender.ExitAction = 0
      else: # res.IsErr in [0,2]
        Message = 'Transaksi Berhasil.\nNomor Transaksi : ' + res.TransactionNo
        if res.IsErr == 2:
          Message += '\n Proses Jurnal Gagal.' + res.ErrMessage

        app.ShowMessage(Message)
        if self.app.ConfirmDialog('Apakah akan cetak kwitansi ?'):
          oPrint = app.GetClientClass('PrintLib','PrintLib')()
          #app.ShowMessage("Masukkan kertas ke printer untuk cetak kwitansi")
          oPrint.doProcessByStreamName(app,ph.packet,res.StreamName)

        sender.ExitAction = 1
    #-- if

  # *** PRIVATE METHOD *** #
  
  def Show(self,mode=1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    
    return self.FormContainer.Show()

  # Set property kurs
  def SetSrcCtlRate(self):
    stEnabled = self.uipTransaction.GetFieldValue('LAccountSource.CurrencyCode') != '000'
    self.pTransaction_SourceRate.Enabled = stEnabled
    self.pTransaction_SourceRate.Color= colors[stEnabled]

  def SetDestCtlRate(self):
    stEnabled = self.uipTransaction.GetFieldValue('LAccountDestination.CurrencyCode') != '000'
    self.pTransaction_DestRate.Enabled = stEnabled
    self.pTransaction_DestRate.Color= colors[stEnabled]

  # Fungsi yang di execute saat perubahan kurs atau nominal
  def AmountOnExit(self,sender):
    self.SetEkuivalenAmount()
    
  # Method untuk set nilai-nilai transaksi
  def SetEkuivalenAmount(self):
    app = self.app
    uipTran = self.uipTransaction

    # Cek Apakah account sumber dan tujuan telah dipilih
    SourceAccountNo = uipTran.GetFieldValue('LAccountSource.AccountNo') or ''
    DestAccountNo = uipTran.GetFieldValue('LAccountDestination.AccountNo') or ''
    if SourceAccountNo == '' or DestAccountNo == '' : return

    SCurrencyCode = uipTran.GetFieldValue('LAccountSource.CurrencyCode') or '000'
    DCurrencyCode = uipTran.GetFieldValue('LAccountDestination.CurrencyCode') or '000'

    #if SCurrencyCode != '000' and DCurrencyCode != '000' :
    #  raise 'PERINGATAN','Transaksi antar valas tidak diperbolehkan'

    uipTran.Edit()

    # Jika transaksi antar rupiah
    if (SCurrencyCode == DCurrencyCode) :
      uipTran.Rate = (uipTran.SourceRate or 0.0) #1.0
      uipTran.TranCurrencyCode = SCurrencyCode #'000'
      #uipTran.TranCurrencyName = 'IDR'
      uipTran.DestAmount = (uipTran.SourceAmount or 0.0)
      uipTran.Amount = uipTran.DestAmount

    # Jika sumber kas adalah valas
    elif SCurrencyCode != '000':
      uipTran.Rate = (uipTran.SourceRate or 0.0)
      uipTran.TranCurrencyCode = SCurrencyCode
      #uipTran.TranCurrencyName = uipTran.GetFieldValue('LAccountSource.LCurrency.Short_Name')
      uipTran.DestAmount = (uipTran.SourceAmount or 0.0 )* (uipTran.Rate or 0.0)
      uipTran.Amount = uipTran.SourceAmount

    # Jika kas tujuan adalah valas
    elif DCurrencyCode != '000' :
      uipTran.Rate = (uipTran.DestRate or 0.0)
      uipTran.TranCurrencyCode = DCurrencyCode
      #uipTran.TranCurrencyName = uipTran.GetFieldValue('LAccountDestination.LCurrency.Short_Name')
      uipTran.DestAmount = (uipTran.SourceAmount or 0.0 ) / (uipTran.Rate or 0.0)
      uipTran.Amount = uipTran.DestAmount

  def CheckInput(self):
    uipTran = self.uipTransaction
    if (uipTran.GetFieldValue('LBatch.BatchId') or 0) == 0 :
      raise 'PERINGATAN', 'Batch transaksi belum diinputkan. Silahkan input dahulu batch transaksi'
      
    return
    #if (self.uipTransaction.GetFieldValue('LAccountSource.CurrencyCode') !=
    #  self.uipTransaction.GetFieldValue('LAccountDestination.CurrencyCode')):
    #  raise 'Transaksi', 'Kode valuta tidak sama!'


    SCurrencyCode = uipTran.GetFieldValue('LCashAccountSource.CurrencyCode') or '000'
    DCurrencyCode = uipTran.GetFieldValue('LCashAccountDestination.CurrencyCode') or '000'

    if SCurrencyCode != '000' and DCurrencyCode != '000' :
      raise 'PERINGATAN','Transaksi antar valas tidak diperbolehkan'

    if (uipTran.Amount or 0.0 ) <= 0.0 :
      raise 'PERINGATAN','Nilai Transfer belum diinputkan lengkap. Silahkan input dahulu'


