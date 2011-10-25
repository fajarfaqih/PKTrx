class fCARPenyaluran:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    
  def GetData(self):
    return self.FormContainer.Show()
    
