class fProdukZakat:
  def __init__(self, formObj, parentForm, mode):
    self.app = formObj.ClientApplication
    self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
    self.mode = mode
    self.ParamDisplay = {
    'NewGroup':'self.DisplayNewGroup()',
    'NewDetail':'self.DisplayNewDetail()',
    'Edit':'self.DisplayEdit()',
    'View':'self.DisplayView()',
    'SENTINEL':''
    }

  # ===== PRIVATE METHOD
  def DisplayNew(self):
    #self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').Visible = 0
    self.uipData.Edit()
    self.uipData.FundCategory = 'Z'
    self.uipData.Status = 'A'
    self.uipData.Level = 1

  def DisplayNewGroup(self) :
    self.DisplayNew()
    self.uipData.IsDetail = 'F'
    self.FormObject.Height = 160

  def DisplayNewDetail(self) :
    self.DisplayNew()
    self.uipData.IsDetail = 'T'

  def DisplayEdit(self) :
    pData =  self.FormObject.GetPanelByName('pData')
    #pData.GetControlByName(self.uipData.ID+'ID').ReadOnly = 1
    cProductCode = pData.GetControlByName('ProductCode')
    cProductCode.ReadOnly = 1
    cProductCode.Color = -2147483624
    pData.GetControlByName('IsDetail').Enabled = 0
    pData.GetControlByName('LProductParent').Enabled = 0
    if self.uipData.IsDetail == 'F':
      self.FormObject.Height = 160

    uipData = self.uipData
    #uipData.Edit()
    #uipData.SetFieldValue('LProductParent.ProductId',uipData.ParentProductId)
    #self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').ReadOnly = 1
    self.DetailOnClick(pData.GetControlByName('IsDetail'))

  def DisplayView(self) :
    self.FormObject.SetAllControlsReadOnly()
    self.pAction_bOK.Enabled = 1
    self.pAction_bOK.Caption = '&Close'
    self.pAction_bOK.Cancel = 1
    self.pAction_bClose.Visible = 0
    if self.uipData.IsDetail == 'F':
      self.FormObject.Height = 160

  # ===== FORM EVENT
  
  def LProductParentAfterLookup(self,ctlLParentProduk,LProductParent):
    uipData = self.uipData
    uipData.Edit()
    uipData.ParentProductId = uipData.GetFieldValue("LProductParent.ProductId")
    ParentLevel = uipData.GetFieldValue("LProductParent.Level") or 0
    uipData.Level = ParentLevel + 1

  def FormShow(self, mode) :
    eval(self.ParamDisplay[mode])
    self.FormContainer.Show()
    
  def bOKClick(self, sender):
    if self.pAction_bClose.Visible :
      self.FormObject.CommitBuffer()
      #self.FormObject.PostResult()
      self.FormObject.CallServerMethod('SimpanData',self.FormObject.GetDataPacket())
      self.app.ShowMessage('Data Berhasil Disimpan')

      formid = 'parameter/fDaftarProdukZakat'
      qForm = self.app.FindForm(formid)
      qPanel = qForm.FormObject.GetPanelByName('ZakahProduct')
      qPanel.Refresh()

    #if self.mode in ['NewGroup','NewDetail'] :
    #  self.ObjectAccess.ClearuipartData(self.uipData,('FundCategory','Status','mode','ID'))
    #else :
    #  sender.ExitAction = 1
    sender.ExitAction = 1
    
  def DetailOnClick(self,sender):
    form = self.FormObject
    Fields = ['Rate','PercentageOfAmilFunds','Nishab','Haul']
    uipData = self.uipData
    uipData.Edit()
    for FieldName in Fields:
      ctl = form.GetPanelByName('pData').GetControlByName(FieldName)
      ctl.Enabled = sender.checked
      uipData.SetFieldValue(FieldName,None)
