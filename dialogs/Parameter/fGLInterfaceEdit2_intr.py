class fGLInterfaceEdit:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    #self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
    #self.mode = mode
    self.ParamDisplay = {
    'NewGroup':'self.DisplayNewGroup()',
    'NewDetail':'self.DisplayNewDetail()',
    'Edit':'self.DisplayEdit()',
    'View':'self.DisplayView()',
    'SENTINEL':''
    }

  # ===== PRIVATE METHOD

  def FormShow(self) :
    self.FormContainer.Show()
    
  # ===== FORM EVENT

  def LAccountAfterLookup(self,sender,Link):
    Ls_GLInterface = self.Ls_GLInterface
    Ls_GLInterface.Edit()
    Ls_GLInterface.SetFieldValue('AccountCode' , Ls_GLInterface.GetFieldValue("LAccount.Account_Code"))
    Ls_GLInterface.SetFieldValue('AccountName' , Ls_GLInterface.GetFieldValue("LAccount.Account_Name"))
    
  def AfterNewRecord(self,sender):
    Ls_GLInterface = self.Ls_GLInterface
    Ls_GLInterface.Edit()
    Ls_GLInterface.ProductId = self.uipProduct.ProductId
