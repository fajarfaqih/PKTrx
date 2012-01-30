import pyFlexcel

class fPrintSaldoAwal:
  def __init__(self,formObj,parentObj):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  # -- FORM EVENT --
  def bRekapClick(self,sender):
    app = self.app
    form = self.form
    
    BranchCode = self.uipData.GetFieldValue('LBranch.BranchCode') or ''
    
    resp = form.CallServerMethod('GetSummaryBeginBalance',
      app.CreateValues(['BranchCode', BranchCode]))
    
    status = resp.FirstRecord
    if status.Is_Err : raise 'Peringatan',status.Err_Message
    
    sw = resp.Packet.GetStreamWrapper(0)
    fileName = self.app.SaveFileDialog("Save to file..", "Format File(*.xls)|*.xls")

    if fileName.find(".xls") == -1 : fileName += ".xls"
    sw.SaveToFile(fileName)

    self.app.ShellExecuteFile(fileName)
    
    
  # -- USER DEFINE METHOD --

  def Show(self):
    self.FormContainer.Show()
