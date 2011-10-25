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
    uipProject.ProductName = uipProject.GetFieldValue("LProductParent.ProductName")
    uipProject.ProductId = uipProject.GetFieldValue("LProductParent.ProductId")

  def Show(self,mode) :
    #self.uipInput.Edit()
    #self.uipInput.IsAllCabang = 0
    #self.uipInput.IsAllValuta = 0
    self.FormContainer.Show()
    
  def IsAllCabangClick(self,sender):
    LCabang = sender.OwnerForm.GetControlByName('pInput.LCabang')

    if sender.Checked:
      LCabang.Enabled = 0
      uipCV = sender.OwnerForm.GetUIPartByName('uipInput')
      uipCV.Edit()
      uipCV.SetFieldValue('LCabang.Kode_Cabang', '')
      uipCV.SetFieldValue('LCabang.Nama_Cabang', '')
    else:
      LCabang.Enabled = 1

  def IsAllValutaClick(self,sender):
    LValuta = sender.OwnerForm.GetControlByName('pInput.LValuta')

    if sender.Checked:
      LValuta.Enabled = 0
      uipCV = sender.OwnerForm.GetUIPartByName('uipInput')
      uipCV.Edit()
      uipCV.SetFieldValue('LValuta.Currency_Code', '')
      uipCV.SetFieldValue('LValuta.Full_Name', '')
    else:
      LValuta.Enabled = 1

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

  
  def bOKClick(self, sender):
    form = sender.OwnerForm
    uipProject = sender.OwnerForm.GetUIPartByName('uipProject')

    #cek isian cabang dan valuta
    #if not uipInput.isAllCabang and (uipInput.GetFieldValue('LCabang.Kode_Cabang') in [None,'']):
    #  form.ShowMessage('Isian Kantor / Cabang masih kosong, mohon untuk diisi.')
    #  return
    #elif not uipInput.isAllValuta and (uipInput.GetFieldValue('LValuta.Currency_Code') in [None,'']):
    #  form.ShowMessage('Isian Valuta masih kosong, mohon untuk diisi.')
    #  return

    if (uipProject.GetFieldValue('LValuta.Currency_Code') in [None,'']):
      form.ShowMessage('Isian Valuta masih kosong, mohon untuk diisi.')
      return
      
    form.CommitBuffer()
    try:
      ph = form.CallServerMethod('SaveProjectDetail',self.FormObject.GetDataPacket())

      rec = ph.FirstRecord
      if rec.Is_Err : raise 'PERINGATAN',rec.Err_Message
      self.app.ShowMessage('Data project berhasil disimpan')
      sender.ExitAction = 1
    except:
      raise
