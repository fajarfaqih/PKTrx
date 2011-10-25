class fBank:
  def __init__(self, formObj, parentForm, mode):
    self.app = formObj.ClientApplication
    self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
    self.mode = mode
    self.ParamDisplay = {
    'New':'self.DisplayNew()',
    'Edit':'self.DisplayEdit()',
    'View':'self.DisplayView()',
    'SENTINEL':''
    }

  def DisplayNew(self) :
    #self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').Visible = 0
    pass

  def DisplayEdit(self) :
    cCode = self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID')
    cCode.Enabled = 0
    cCode.Color = -2147483624
    
  def DisplayView(self) :
    self.FormObject.SetAllControlsReadOnly()
    self.pAction_bOK.Enabled = 1
    self.pAction_bClose.Visible = 0
    self.pAction_bOK.Caption = '&Close'
    self.pAction_bOK.Cancel = 1

  # --- FORM EVENT
  
  def FormShow(self, mode) :
    eval(self.ParamDisplay[mode])
    self.FormContainer.Show()
    
  def bOKClick(self, sender):
    if self.pAction_bClose.Visible :
      self.FormObject.CommitBuffer()
      #self.FormObject.PostResult()
      ph = self.FormObject.CallServerMethod('SimpanData',self.FormObject.GetDataPacket())
      status = ph.FirstRecord
      if status.Is_Err == 1 : raise 'ERROR', status.Err_Message
      
    if self.mode == 'New' :
        self.ObjectAccess.ClearuipartData(self.uipData,('mode','ID'))
    else :
      sender.ExitAction = 1
      
