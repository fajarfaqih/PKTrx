class fVolunteer:
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
    self.FormObject.GetPanelByName('pData').GetControlByName('lblBranchCode').Caption = '.%s' % self.uipData.BranchCode

    pass

  def DisplayEdit(self) :
    self.FormObject.GetPanelByName('pData').GetControlByName('lblBranchCode').Caption = ''
    self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').Enabled = 0
    self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').ReadOnly = 1

  def DisplayView(self) :
    self.FormObject.SetAllControlsReadOnly()
    self.pAction_bOK.Enabled = 1
    self.pAction_bClose.Visible = 0
    self.pAction_bOK.Caption = '&Close'
    self.pAction_bOK.Cancel = 1

  # --- FORM EVENT
  
  def LCabangAfterLookup(self,ctlLink,Link):
    uipData = self.uipData
    uipData.Edit()
    uipData.BranchCode = uipData.GetFieldValue("LCabang.Kode_Cabang")

  def FormShow(self, mode) :
    eval(self.ParamDisplay[mode])
    self.FormContainer.Show()
    
  def bOKClick(self, sender):
    if self.pAction_bClose.Visible :
      self.FormObject.CommitBuffer()
      #self.FormObject.PostResult()
      self.FormObject.CallServerMethod('SimpanData',self.FormObject.GetDataPacket())
    if self.mode == 'New' :
        self.ObjectAccess.ClearuipartData(self.uipData,('mode','ID'))
    else :
      sender.ExitAction = 1
      
