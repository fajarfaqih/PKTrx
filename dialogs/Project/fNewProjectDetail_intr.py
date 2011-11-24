class fNewProjectDetail:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
    self.fSearchDonor = None

  # ===== PRIVATE METHOD
  
  # ===== FORM EVENT
  
  def LProductParentAfterLookup(self,ctlLParentProduk,LProductParent):
    # FIXME : Masih Error ketika pilih parent
    uipData = self.uipData
    uipData.Edit()
    uipData.ParentProductId = uipData.GetFieldValue("LProductParent.ProductId")
    ParentLevel = uipData.GetFieldValue("LProductParent.Level") or 0
    uipData.Level = ParentLevel + 1

  def LProductAfterLookup(self,sender,linkUI):
    uipProject = self.uipProject
    uipProject.Edit()
    uipProject.AccountName = uipProject.GetFieldValue("LProduct.ProductName")

  def Show(self,mode) :
    self.FormContainer.Show()
    
  def SponsorBeforeLookup(self,sender,linkui):
    if self.fSearchDonor == None :
      fSearch = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
      self.fSearchDonor = fSearch
    else :
      fSearch = self.fSearchDonor

    if fSearch.GetDonorData():
      uipSponsor = self.uipLsSponsor
      uipSponsor.Edit()

      uipSponsor.SponsorId = fSearch.DonorIntId
      uipSponsor.ExtSponsor = fSearch.DonorName

  
  def bSaveClick(self, sender):
    form = sender.OwnerForm
    uipProject = sender.OwnerForm.GetUIPartByName('uipProject')

    if (uipProject.GetFieldValue('LCurrency.Currency_Code') in [None,'']):
      form.ShowMessage('Isian Valuta masih kosong, mohon untuk diisi.')
      return
      
    form.CommitBuffer()
    form.PostResult()
    
    self.app.ShowMessage('Data Project Baru Berhasil Disimpan')
    sender.ExitAction = 1
