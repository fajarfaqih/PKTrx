class fCash :
    def __init__(self, formObj, parentForm, mode) :
       self.app = formObj.ClientApplication
       self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
       self.ClientFilter = self.app.GetClientClass("TransactionClient",'Transaction')()
       self.mode = mode
       self.ParamDisplay = {
        'In':'self.DisplayIn()',
        'Out':'self.DisplayOut()',
        'View':'self.DisplayView()',
        'SENTINEL':''
       }


    def OnChange_pay(self, sender) :
      if sender.ItemIndex : #Cash
        self.pTransaction_LBank.Visible = 0
      else :
         self.pTransaction_LBank.Visible = 1

    def DisplayIn(self) :
      self.FormObject.Caption += ' In'
      self.pTransaction_JumlahTotal.ControlCaption = 'Cash In (Debet)'
      
    def DisplayOut(self) :
      self.FormObject.Caption += ' Out'
      self.pTransaction_JumlahTotal.ControlCaption = 'Cash Out (Kredit)'
      
    def DisplayView(self) :
      self.FormObject.SetAllControlsReadOnly()
      self.pAction_bOK.Enabled = 1
      self.pAction_bCancel.Visible = 0
      self.pAction_bOK.Caption = '&Close'
      self.pAction_bOK.Cancel = 1

    def FormShow(self, mode) :
       self.Input = (self.uipTransaction,)
       self.Data = ''
       self.ClientFilter.FirstFilterClient(self.Input,self.Data)
       eval(self.ParamDisplay[mode])
       return self.FormContainer.Show()
       
    def BeforePost_Item(self, sender) :
      sender.EkuivalenAmount = sender.Amount
      sender.rate = 1
      sender.CurrencyCode = '000'

    def OnAfterLookup_Check(self, sender, LinkUI) :
       uip = sender.Owner.UIPart
       if uip.GetFieldValue(sender.Name+'.Status') != 'A' :
          uip.ClearLink(sender.Name)
          raise 'PERINGATAN','Data yang dipakai sudah tidak aktif'
       return 1
       
    def CancelClick(self, sender) :
      if sender.Caption == '&Cancel' :
        sender.ExitAction = 2
        return

    def SaveClick(self,sender) :
       if self.pAction_bCancel.Visible :
         if self.app.ConfirmDialog('Anda Menyimpan Transaksi Ini ?') :
           self.FormObject.CommitBuffer()
           ph = self.FormObject.GetDataPacket()
           #rec = ph.Packet.AddNewDatasetEx('Structure','Fields : string;ClassName : string').AddRecord()
           #rec.Fields = str(self.Fields)
           #rec.ClassName = self.uipData.ClassTypeName

           self.ClientFilter.BeforeSaveClient(self.Input,self.Data)
           result = self.FormObject.CallServerMethod("SimpanData",ph)

       if self.mode == 'Input' :
          self.ObjectAccess.ClearuipartData(self.uipTransaksi,
             eval(result.FirstRecord.FieldInit), eval(result.FirstRecord.ValueInit)
           )
       else :
          sender.ExitAction = 1
