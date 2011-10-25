class fBudgetRevision :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.form = formObj
    self.RevisionAmount = 0

  def bSimpanClick(self, sender):
    app = self.app
    form = self.form
    if app.ConfirmDialog('Yakin simpan data ?'):
      form.CommitBuffer()
      
      ph = self.FormObject.CallServerMethod("SaveRevision", form.GetDataPacket())
      
      res = ph.FirstRecord
      if res.IsErr:
        raise 'PERINGATAN',res.ErrMessage
      self.RevisionAmount = self.uipBudget.Amount
      app.ShowMessage('Revisi Berhasil disimpan')

      sender.ExitAction = 1
    #-- if

    
