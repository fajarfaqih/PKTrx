class fCariDonatur:
  def __init__(self, formObj, parentForm, mode):
    self.app=formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    self.mode = mode
    self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
    self.ListFunc = {
      'fPeragaanDonatur':('View','Donatur/fPeragaanDonatur','DonorId','Peragaan Donatur' ),
      'fPenghimpunanDana':('New','Transaksi/fPenghimpunanDana','DonorId','Penghimpunan Dana'),
      'fTransaksiUmum':('NonTunaiDebit','Transaksi/fTransaksiUmum','DonorId','Penghimpunan (Non Tunai)'),
      'SENTINEL':''
    }
    self.InputCtrl = ('DonorId','PhoneNumber','DonorName')
    
  def FormShow(self,captionMode):
    self.FormObject.Caption += self.ListFunc[self.mode][3]
    return self.FormContainer.Show()
    
  def OnChange(self, sender) :
    if sender.Text == '' :
       for rec in self.InputCtrl :
         self.PData.GetControlByName(rec).color = 16777215 #white
         self.PData.GetControlByName(rec).ReadOnly = 0
    else :
       for rec in self.InputCtrl :
         if sender.Name == rec :
           self.PData.GetControlByName(rec).color = 12632256
           self.PData.GetControlByName(rec).ReadOnly = 0
         else :
           self.PData.GetControlByName(rec).color = 1
           self.PData.GetControlByName(rec).ReadOnly = 1


  def FilterData (self, mode, Value) :
    if mode == 'DonorId' :
      pass
    elif mode == 'PhoneNumber' :
      if Value[0] != '+' :
        raise 'PERINGATAN','Awal No Telepon dengan +(tanda \'+\') diikuti<KodeNegara> '
        
  def OnExit(self,sender) :
    if sender.Text in (None,'') :
       return 0
    self.uipResult.ClearData()
    self.FilterData(sender.Name,sender.Text)
    res = self.FormObject.CallServerMethod('CariData',\
      self.app.CreateValues(['ID',sender.Name],['Value',sender.Text])
      )
    result = res.Packet.uipResult

    for i in range(result.RecordCount) :
      self.uipResult.Append()
      self.ObjectAccess.InsertData(self.uipResult,
        eval(res.FirstRecord.Struct), result.GetRecord(i).Values, 0)

    if result.RecordCount == res.FirstRecord.FIN :
       self.app.ShowMessage('Masukan Nama yang lebih spesifik')

  def PilihClick(self,sender) :
    res = self.uipResult
    key = res.GetFieldValue(self.uipData.ID)

    if key == None :
       raise 'PERINGATAN','Tidak ada data yang dipilih'

    formname = self.ListFunc[self.mode][1]
    mode = self.ListFunc[self.mode][0]

    ph = self.app.CreateValues(['key',key],['mode',mode],['ID',self.uipData.ID])
    dlg = self.app.CreateForm(formname,formname,0,ph,[mode])
    state = dlg.FormShow(mode)

    if state == 1 :
      self.FormObject.Close(1)
      self.PAction_BOK.ExitAction = 1

    return 1
