class fPrintTextPreview :
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    
  def PrintClick(self):
    pass
    
  def Show(self,filename=''):

    filename = 'c:/tes.txt'
    
    filehandle = open(filename)
    try :
      while 1:
        line = filehandle.readline()
        if not line:
          break
        self.app.ShowMessage(line[:-1])
        self.pPreview_ePreview.Text += line[:-1] + '\'
        
    finally :
      filehandle.close()

    # end try finally
      
    self.FormContainer.Show()
