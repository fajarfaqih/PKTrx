class fBranchCashReport:

  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    
  def Show(self):
    self.FormContainer.Show()
    
    
  def bCetakClick(self):
    app = self.app
    form = self.form
    
    form.CommitBuffer()
    resp = form.CallServerMethod('CetakData',form.GetDataPacket())
    
    res = resp.FirstRecord
    
    if res.IsErr : raise 'PERINGATAN',rec.ErrMessage
