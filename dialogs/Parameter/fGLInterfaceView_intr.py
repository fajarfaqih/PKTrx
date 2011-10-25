class fGLInterfaceView:
  def __init__(self,formObj,parentObj):
    self.app = formObj.ClientApplication
    self.form = formObj
    
  def FormShow(self):
    self.FormContainer.Show()
