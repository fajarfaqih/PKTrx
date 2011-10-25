class fWebViewer:

  def __init__(self,parentObj,formObj):
    self.form = formObj
    #self.app = formObj.ClientApplication
    
  def showWebPage(self,file):
    self.webviewer.Url = file
    self.FormContainer.Show()
