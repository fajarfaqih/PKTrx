class ftestform:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.userapp = self.app.UserAppObject

  def Show(self):
    return self.FormContainer.Show()


