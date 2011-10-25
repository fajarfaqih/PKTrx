class fDistCADetail:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    
  def ShowDetail(self,DistributionId) :
  
    ph = self.app.CreateValues(
      ['DistributionId',DistributionId]
    )
    
    self.FormObject.SetDataWithParameters(ph)
    self.FormContainer.Show()
