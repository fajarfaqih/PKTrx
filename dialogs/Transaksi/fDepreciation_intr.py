class fDepreciation:
  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    
  def Show(self):
    self.FormContainer.Show()
    
  def ProcessClick(self,sender):
    self.form.CommitBuffer()
    rph = self.app.ExecuteScript("BatchProcess/L_Depreciation",self.form.GetDataPacket())
    
    status = rph.FirstRecord
    if status.Is_Err :
      raise 'PERINGATAN',status.Err_Message
  
