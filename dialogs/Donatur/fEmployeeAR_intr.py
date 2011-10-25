KodeTransaksi = ['KK','KM']

class fEmployeeAR :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication

  def Show(self):
    return self.FormContainer.Show()

  def JenisTransaksiOnChange(self,sender):
    uip = self.uipTransaction
    uip.Edit()
    uip.TransactionNo = KodeTransaksi[sender.ItemIndex] + uip.TransactionNo[2:]
    
  def EmployeeAfterLookup (self, sender, linkui):
    self.uipTransaction.EmployeeName = self.uipTransaction.GetFieldValue('LEmployee.Nama_Lengkap')
    
  def bSimpanClick(self, sender):
    if self.app.ConfirmDialog('Yakin simpan transaksi ?'):
      self.FormObject.CommitBuffer()
      ph = self.FormObject.GetDataPacket()

      ph = self.FormObject.CallServerMethod("SimpanData", ph)
      res = ph.FirstRecord
      if res.IsErr:
        self.app.ShowMessage(res.ErrMessage)
        sender.ExitAction = 0
      else:
        self.app.ShowMessage('Transaksi Berhasil')
        sender.ExitAction = 1
    #-- if
