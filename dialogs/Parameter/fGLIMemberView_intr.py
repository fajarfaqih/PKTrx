class fGLIMemberView:
  def __init__(self,formObj,parentObj):
    self.app = formObj.ClientApplication
    self.form = formObj
    
  def FormShow(self):
    self.FormContainer.Show()
    
  def ItemAfterNewRecord(self,sender):
    sender.Delete()
  
  def LAccountAfterLookup(self,ctlLink,Link):
    LsGLInterface = self.LsGLInterface
    LsGLInterface.Edit()
    LsGLInterface.AccountCode = LsGLInterface.GetFieldValue("LAccount.Account_Code")
    LsGLInterface.AccountName = LsGLInterface.GetFieldValue("LAccount.Account_Name")

