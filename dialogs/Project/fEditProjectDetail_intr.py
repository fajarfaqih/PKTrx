
class fEditProjectSponsor:
  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSearchDonor = None
    
  def FormShow(self):
    self.FormContainer.Show()

  def SponsorBeforeLookup(self,sender,linkui):
    if self.fSearchDonor == None :
      fSearch = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
      self.fSearchDonor = fSearch
    else :
      fSearch = self.fSearchDonor

    if fSearch.GetDonorData():
      uipSponsor = self.LsProjectSponsor
      uipSponsor.Edit()

      uipSponsor.SponsorId = fSearch.DonorIntId
      uipSponsor.ExtSponsor = fSearch.DonorName


#  def SimpanClick(self):
#    self
