class fBudgetItem:
  def __init__(self, formObj, parentForm, mode):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
    self.mode = mode
    self.ParamDisplay = {
    'New':'self.DisplayNew()',
    'Edit':'self.DisplayEdit()',
    'View':'self.DisplayView()',
    'SENTINEL':''
    }

  # -- PRIVATE METHOD
  
  def ClearData(self) :
    rec = self.uipData
    rec.Edit()
    stat = rec.Status
    mode = rec.mode
    ID = rec.ID
    user = rec.UserName
    Tgl = rec.OpeningDate
    rec.ClearData()
    rec.Status = stat
    rec.mode = mode
    rec.OpeningDate = Tgl
    rec.UserName = user
    rec.ID = ID
    rec.Level = 1
    rec.Is_Detail='F'
    
  def DisplayNew(self) :
    #self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').Visible = 0
    uipData = self.uipData
    uipData.Edit()
    uipData.Is_Detail = 'F'
    uipData.Level = 1

  def DisplayEdit(self) :
    pData = self.FormObject.GetPanelByName('pData')

    #pData.GetControlByName(self.uipData.ID+'ID').ReadOnly = 1
    pData.GetControlByName('LParent').Enabled = 0
    pData.GetControlByName('Is_Detail').Enabled = 0
    #cProductCode.ReadOnly = 1
    #cProductCode.Color = -2147483624
  def DisplayView(self) :
    self.FormObject.SetAllControlsReadOnly()
    self.pAction_bOK.Enabled = 1
    self.pAction_bClose.Visible = 0
    self.pAction_bOK.Caption = '&Batal'
    self.pAction_bOK.Cancel = 1

  # -- FORM CONROL EVENT
  
  def LParentAfterLookup(self,ctlLink,Link):
    uipData = self.uipData
    uipData.Edit()
    uipData.ParentBudgetItemCode = uipData.GetFieldValue("LParent.BudgetItemCode")
    ParentLevel = uipData.GetFieldValue("LParent.Level") or 0
    uipData.Level = ParentLevel + 1

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

