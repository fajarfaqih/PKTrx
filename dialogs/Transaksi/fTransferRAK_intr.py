DefaultItems = [ 'Inputer',
                 'BranchCode',
                 'TransactionDate',
                 'FloatTransactionDate',
                 'ActualDate',
                 'TransactionNo',
                 'ShowMode',
                 ]

colors = {0:-2147483624 , 1:16777215}


class fTransferRAK :

  # *** FORM EVENT *** #
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.DefaultValues = {}

  def SourceAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction

    self.SetSrcCtlRate()
    uipTran.Edit()
    uipTran.SourceRate = uipTran.GetFieldValue('LCashAccountSource.LCurrency.Kurs_Tengah_BI')
    uipTran.SourceAmount = 0.0
    self.SetEkuivalenAmount()

  def DestinationAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction

    self.SetDestCtlRate()

    uipTran.Edit()
    uipTran.DestRate = uipTran.GetFieldValue('LCashAccountDestination.LCurrency.Kurs_Tengah_BI')
    uipTran.DestAmount = 0.0

    self.SetEkuivalenAmount()

  def LSourceBranchAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction

    uipTran.Edit()
    uipTran.SourceBranchCode = uipTran.GetFieldValue('LSourceBranch.BranchCode')

  def LDestBranchAfterLookup(self, sender, linkui):
    uipTran = self.uipTransaction

    uipTran.Edit()
    uipTran.DestBranchCode = uipTran.GetFieldValue('LDestBranch.BranchCode')
    
  def AmountOnExit(self,sender):
    self.SetEkuivalenAmount()

  def bSimpanClick(self, sender):
    if self.Simpan(1):
      self.ClearData()

  def bSimpanCloseClick(self, sender):
    if self.Simpan(2):
      sender.ExitAction = 1

  def SumberDanaChange(self, sender):
    self.SwitchSumberDana()
  
  # *** PRIVATE METHOD *** #

  def SwitchSumberDana(self):
    uipTran = self.uipTransaction
    ctlFundEntity = self.pTransaction_FundEntity

    self.pTransaction_LAccountSource.enabled = ctlFundEntity.ItemIndex != 3
    
    if ctlFundEntity.ItemIndex == 3:
      uipTran.SetFieldValue('LAccountSource.AccountNo', '')
      uipTran.SetFieldValue('LAccountSource.AccountName', '')
    
  def Show(self,mode = 1):
    self.uipTransaction.Edit()
    self.uipTransaction.ShowMode = mode
    if mode == 1:
      # Insert Mode
      self.uipTransaction.FundEntity = 1
      
      self.SaveDefaultValues()
      
    else:
      self.pAction_bSave.Visible = 0

      # Move button position
      self.pAction_bCancel.Left = self.pAction_bSaveClose.Left
      self.pAction_bSaveClose.Left = self.pAction_bSave.Left

      self.SetSrcCtlRate()
      self.SetDestCtlRate()

    self.SwitchSumberDana()

    return self.FormContainer.Show()

  # Set property kurs
  def SetSrcCtlRate(self):
    stEnabled = self.uipTransaction.GetFieldValue('LCashAccountSource.CurrencyCode') != '000'
    self.pTransaction_SourceRate.Enabled = stEnabled
    self.pTransaction_SourceRate.Color= colors[stEnabled]

  def SetDestCtlRate(self):
    stEnabled = self.uipTransaction.GetFieldValue('LCashAccountDestination.CurrencyCode') != '000'
    self.pTransaction_DestRate.Enabled = stEnabled
    self.pTransaction_DestRate.Color= colors[stEnabled]

  # Fungsi untuk menyimpan nilai2 default yang akan digunakan pada saat input ulang
  def SaveDefaultValues(self):
    uipTran = self.uipTransaction
    for item in DefaultItems :
      self.DefaultValues[item] = uipTran.GetFieldValue(item)

  def ClearData(self):
    # Reset data untuk input ulang
    self.uipTransaction.ClearData()

    # Mengembalikan nilai-nilai default yang telah disimpan sebelumnya
    uipTran = self.uipTransaction
    uipTran.Edit()
    for item in DefaultItems :
      uipTran.SetFieldValue(item,self.DefaultValues[item])
      
    self.pTransaction_ActualDate.SetFocus()

  # Method untuk set nilai-nilai transaksi
  def SetEkuivalenAmount(self):
    app = self.app
    uipTran = self.uipTransaction

    # Cek Apakah account sumber dan tujuan telah dipilih
    SourceAccountNo = uipTran.GetFieldValue('LCashAccountSource.AccountNo') or ''
    DestAccountNo = uipTran.GetFieldValue('LCashAccountDestination.AccountNo') or ''
    if SourceAccountNo == '' or DestAccountNo == '' : return

    SCurrencyCode = uipTran.GetFieldValue('LCashAccountSource.CurrencyCode') or '000'
    DCurrencyCode = uipTran.GetFieldValue('LCashAccountDestination.CurrencyCode') or '000'

    if SCurrencyCode != DCurrencyCode and SCurrencyCode != '000' and DCurrencyCode != '000' :
        raise 'PERINGATAN','Transaksi antar valas tidak diperbolehkan'

    uipTran.Edit()
    uipTran.AmountEkuiv = (uipTran.Amount or 0.0) * (uipTran.Rate or 0.0)

    # Jika transaksi untuk valuta yang sama
    if (SCurrencyCode == DCurrencyCode) :
      if SCurrencyCode == '000' :
        # Jika Transfer rupiah
        uipTran.Rate = 1.0
        uipTran.TranCurrencyCode = '000'
        uipTran.TranCurrencyName = 'IDR'
        uipTran.DestAmount = (uipTran.SourceAmount or 0.0)
        uipTran.Amount = uipTran.DestAmount
      else:
        # Jika Transfer valas
        uipTran.Rate = (uipTran.SourceRate or 0.0)
        uipTran.TranCurrencyCode = SCurrencyCode
        uipTran.TranCurrencyName = uipTran.GetFieldValue('LCashAccountSource.LCurrency.Short_Name')
        uipTran.DestAmount = (uipTran.SourceAmount or 0.0)
        uipTran.Amount = uipTran.DestAmount

    # Jika sumber kas adalah valas
    elif SCurrencyCode != '000':
      uipTran.Rate = (uipTran.SourceRate or 0.0)
      uipTran.TranCurrencyCode = SCurrencyCode
      uipTran.TranCurrencyName = uipTran.GetFieldValue('LCashAccountSource.LCurrency.Short_Name')
      uipTran.DestAmount = (uipTran.SourceAmount or 0.0 )* (uipTran.Rate or 0.0)
      uipTran.Amount = uipTran.SourceAmount

    # Jika kas tujuan adalah valas
    elif DCurrencyCode != '000' :
      uipTran.Rate = (uipTran.DestRate or 0.0)
      uipTran.TranCurrencyCode = DCurrencyCode
      uipTran.TranCurrencyName = uipTran.GetFieldValue('LCashAccountDestination.LCurrency.Short_Name')
      uipTran.DestAmount = (uipTran.SourceAmount or 0.0 ) / (uipTran.Rate or 0.0)
      uipTran.Amount = uipTran.DestAmount

  def CheckRequired(self):
    uipTran = self.uipTransaction
    
    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'

    if uipTran.GetFieldValue('LCashAccountSource.AccountNo') == None :
      raise 'PERINGATAN', 'Kas Sumber belum diinputkan!'

    if uipTran.GetFieldValue('LCashAccountDestination.AccountNo') == None :
      raise 'PERINGATAN', 'Kas Tujuan belum diinputkan!'
      
    if (uipTran.GetFieldValue('LCashAccountSource.AccountNo') ==
      uipTran.GetFieldValue('LCashAccountDestination.AccountNo')):
      raise 'PERINGATAN', 'Kas Sumber dan Tujuan tidak boleh sama!'
      
    if uipTran.FundEntity != 4 and uipTran.GetFieldValue('LAccountSource.AccountNo') in ['',None]:
      raise 'PERINGATAN', 'Data Produk Belum dipilih\nUntuk sumber dana selain AMIL, data produk harus dipilih'

    SCurrencyCode = uipTran.GetFieldValue('LCashAccountSource.CurrencyCode') or '000'
    DCurrencyCode = uipTran.GetFieldValue('LCashAccountDestination.CurrencyCode') or '000'

    if SCurrencyCode != DCurrencyCode and SCurrencyCode != '000' and DCurrencyCode != '000' :
      raise 'PERINGATAN','Transaksi antar valas tidak diperbolehkan'

    if (uipTran.Amount or 0.0 ) <= 0.0 :
      raise 'PERINGATAN','Nilai Transfer belum diinputkan lengkap. Silahkan input dahulu'

  def Simpan(self,savemode):
    app = self.app
    uipTran = self.uipTransaction
    
    self.CheckRequired()
    
    if app.ConfirmDialog('Yakin simpan transaksi ?'):
      self.FormObject.CommitBuffer()
      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr == 1 :
        app.ShowMessage(res.ErrMessage)
        return 0
      else:
        Message = 'Transaksi Berhasil.\nNomor Transaksi : ' + res.TransactionNo
        if res.IsErr == 2:
          Message += '\n Proses Jurnal Gagal.' + res.ErrMessage

        app.ShowMessage(Message)
        if savemode == 2 :
          if app.ConfirmDialog('Apakah akan cetak kwitansi ?'):
            oPrint = app.GetClientClass('PrintLib','PrintLib')()
            #app.ShowMessage("Masukkan kertas ke printer untuk cetak kwitansi")
            oPrint.doProcessByStreamName(app,ph.packet,res.StreamName)
          # endif
        # endif
        self.DefaultValues['ActualDate'] = uipTran.ActualDate
      # endif else

      return 1
    #-- if
    return 0


