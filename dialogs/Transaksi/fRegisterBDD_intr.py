KodeTransaksi = ['KK','KM']

class fRegisterBDD :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication

  def Show(self , mode = 1):
    uipTran = self.uipTransaction
    
    uipTran.Edit()
    uipTran.ShowMode = mode
    uipTran.HasContract = 'F'
    
    return self.FormContainer.Show()

  def CheckRequired(self):
    app = self.app
    uipTran = self.uipTransaction

    if uipTran.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'

    if uipTran.GetFieldValue('LCashAccount.AccountNo') in ['',None] :
      raise 'PERINGATAN','Kas / Bank belum dipilih'

    if (uipTran.Amount or 0.0) <= 0.0:
      raise 'PERINGATAN','Nilai Transaksi tidak boleh <= 0.0'
      
    if uipTran.GetFieldValue('LCPIACategory.CPIACatCode') in ['',None] :
      raise 'PERINGATAN','Kategori Biaya dimuka belum dipilih'

    if uipTran.GetFieldValue('LCostAccount.Account_Code') in ['',None] :
      raise 'PERINGATAN','Akun Biaya belum dipilih'

  def bSimpanClick(self, sender):
    app = self.app
    
    self.CheckRequired()
    if app.ConfirmDialog('Yakin simpan transaksi ?'):
      self.FormObject.CommitBuffer()
      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr == 1:
        app.ShowMessage(res.ErrMessage)
        sender.ExitAction = 0
      else:
        Message = 'Transaksi Berhasil.\nNomor Transaksi : ' + res.TransactionNo
        if res.IsErr == 2:
          Message += '\n Proses Jurnal Gagal.' + res.ErrMessage

        app.ShowMessage(Message)
        if app.ConfirmDialog('Apakah akan cetak kwitansi ?'):
          oPrint = app.GetClientClass('PrintLib','PrintLib')()
          oPrint.doProcessByStreamName(app,ph.packet,res.StreamName)

        sender.ExitAction = 1
    #-- if
