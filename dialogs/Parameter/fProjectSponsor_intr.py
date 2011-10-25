
class fProjectSponsor:
  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    
  def FormShow(self):
    self.FormContainer.Show()
    
    
