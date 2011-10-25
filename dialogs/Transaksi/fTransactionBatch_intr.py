class fTransactionBatch :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication

  def bCreateClick(self, sender):
    if self.app.ConfirmDialog('Yakin akan membuat batch transaksi ?'):
      ph = self.app.CreateValues(
          ['BatchDate', self.uipBatch.BatchDate],
          ['Description', self.uipBatch.Description or ''],
          )

      ph = self.FormObject.CallServerMethod("CreateBatch", ph)
      res = ph.FirstRecord

      if res.IsErr == 1:
        self.app.ShowMessage(res.ErrMessage)
#        sender.ExitAction = 0
      else:
        self.uipBatch.Edit()
        self.uipBatch.BatchNo = res.BatchNo
        self.uipBatch.Description = res.Description
        self.pAction_bCreate.Enabled = 0
    #-- if

  def FormOnShow(self,sender):
    self.pBatch_BatchDate.SetFocus()
    
  def Show(self):
    return self.FormContainer.Show()
    
