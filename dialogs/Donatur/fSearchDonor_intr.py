class fSearchDonor:
  def __init__(self, formObj, parentForm):
    self.app=formObj.ClientApplication
    self.form = formObj
    self.userapp = self.app.UserAppObject
    self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
    self.InputCtrl = ('DonorId','PhoneNumber','DonorName','DonorEmail')
    self.DonorId = None
    self.DonorIntId = None
    self.DonorName = None
    self.MarketerId = None
    self.MarketerName = None

  def FormShow(self,captionMode):
    self.FormObject.Caption += self.ListFunc[self.mode][3]
    return
    
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
      return
      if Value[0] != '+' :
        raise 'PERINGATAN','Awal No Telepon dengan +(tanda \'+\') diikuti<KodeNegara> '
        
  def OnExit(self,sender) :
    if sender.Text in (None,'') :
       return 0

    self.FilterData(sender.Name,sender.Text)
    self.CariData(sender.Name,sender.Text,self.uipData.IsAllCabang)

  def AllCabangOnClick(self,sender):
    uipData = self.uipData
    pData = self.form.GetPanelByName('PData')
    checkStatus = {0:'F',-1:'T'}
    for ctlname in self.InputCtrl :
      control = pData.GetControlByName(ctlname)
      if len(control.Text) > 0 :
        self.CariData(control.Name,control.Text,checkStatus[sender.Checked])
        break

  def CariData(self,fieldname,fieldvalue,isAllCabang):
    uipResult = self.uipResult
    uipResult.ClearData()

    res = self.FormObject.CallServerMethod('CariData',\
      self.app.CreateValues(['ID',fieldname],['Value',fieldvalue],['IsAllCabang',isAllCabang])
      )

    result = res.Packet.uipResult

    for i in range(result.RecordCount) :
      uipResult.Append()
      self.ObjectAccess.InsertData(uipResult,
        eval(res.FirstRecord.Struct), result.GetRecord(i).Values, 0)
    #-- end for
    
    uipResult.First()
    if result.RecordCount == res.FirstRecord.FIN :
       self.app.ShowMessage('Masukan Nama yang lebih spesifik')

  def gridDoubleClick(self,sender):
    self.PilihClick(self.PAction_BOK)
    
  def PilihClick(self,sender) :
    donorID = self.uipResult.DonorId
    donorIntId = self.uipResult.DonorIntId

    if donorID in [None,''] :
       if donorIntId in [None,'',0]:
         raise 'PERINGATAN','Tidak ada data yang dipilih'
       else:
         raise 'PERINGATAN','Data Donor tidak dapat digunakan karena belum memiliki ID'

    self.DonorId = donorID
    self.DonorIntId = donorIntId
    self.DonorName = self.uipResult.DonorName
    self.DonorNo = self.uipResult.DonorId
    self.PhoneNumber = self.uipResult.PhoneNumber
    self.Address = self.uipResult.AddressStreet
    self.NPWZ = self.uipResult.NPWZ
    self.NPWP = self.uipResult.NPWP
    self.DonorType = self.uipResult.DonorType
    self.MarketerId = self.uipResult.MarketerId
    self.MarketerName = self.uipResult.MarketerName
    self.FormObject.Close(1)
    #sender.ExitAction = 1

    return 1

  def GetDonorID(self):
    st = self.FormContainer.Show()
    if st == 1:
      return self.DonorIntId
    else:
      return None

  def GetDonorData(self):
    st = self.FormContainer.Show()
    if st == 1:
      return 1
    else:
      return None
