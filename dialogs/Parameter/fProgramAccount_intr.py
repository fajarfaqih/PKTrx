class fProgramAccount:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()

  # ===== PRIVATE METHOD

  def FormShow(self) :
    self.uipInput.Edit()
    self.uipInput.IsAllCabang = 0
    self.uipInput.IsAllValuta = 0
    self.FormContainer.Show()
    
  # ===== FORM EVENT

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

  def bOKClick(self, sender):
    form = sender.OwnerForm
    uipInput = sender.OwnerForm.GetUIPartByName('uipInput')

    #cek isian cabang dan valuta
    if not uipInput.isAllCabang and (uipInput.GetFieldValue('LCabang.Kode_Cabang') in [None,'']):
      form.ShowMessage('Isian Kantor / Cabang masih kosong, mohon untuk diisi.')
      return
    elif not uipInput.isAllValuta and (uipInput.GetFieldValue('LValuta.Currency_Code') in [None,'']):
      form.ShowMessage('Isian Valuta masih kosong, mohon untuk diisi.')
      return

    form.CommitBuffer()
    try:
      ph = self.app.ExecuteScript('Product/SaveProductAccount',self.FormObject.GetDataPacket())

      rec = ph.FirstRecord
      if rec.Is_Error : raise 'PERINGATAN',rec.Err_Message

      sender.ExitAction = 1
    except:
      raise
