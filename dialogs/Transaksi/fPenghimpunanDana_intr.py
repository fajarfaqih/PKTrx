class fPenghimpunanDana :
    def __init__(self, formObj, parentForm, mode) :
       self.app = formObj.ClientApplication
       self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
       self.ClientFilter = self.app.GetClientClass("TransactionClient",'Transaction')()
       self.mode = mode
       self.ParamDisplay = {
        'New':'self.DisplayNew()',
        'Edit':'self.DisplayEdit()',
        'View':'self.DisplayView()',
        'SENTINEL':''
       }

    def OnChange_pay(self, sender) :
      if sender.ItemIndex : #Cash
        self.pTransaction_LBank.Visible = 0
      else :
         self.pTransaction_LBank.Visible = 1

    def DisplayNew(self) :
      pass
      
    def DisplayEdit(self) :
      self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').ReadOnly = 1

    def DisplayView(self) :
      self.FormObject.SetAllControlsReadOnly()
      self.pAction_bOK.Enabled = 1
      self.pAction_bCancel.Visible = 0
      self.pAction_bOK.Caption = '&Close'
      self.pAction_bOK.Cancel = 1

    def FormShow(self, mode) :
       self.Fields = ((self.uipData.ID),('DonorName','PhoneNumber','Email','ReferenceBy'
               ))
       self.Input = (self.uipTransaction,)
       self.Data = ''
       self.ClientFilter.FirstFilterClient(self.Input,self.Data)
       eval(self.ParamDisplay[mode])
       return self.FormContainer.Show()

    def BeforePost_Item(self, sender) :
      if sender.GetFieldValue('LProduct.FixedValue') == 'T' :
         sender.Amount = (sender.TotalUnit or 0) * sender.GetFieldValue('LProduct.FixedValueAmount')
      sender.EkuivalenAmount = sender.Amount
      sender.rate = 1
      sender.CurrencyCode = '000'

    def OnExit_ID(self, sender) :
       if self.mode != 'Input' :
         return
       if self.uipData.GetFieldValue(self.uipData.ID+'ID') in (None,'') :
          return
       res= self.FormObject.CallServerMethod("FindData",
         self.app.CreateValues(['ClassName',self.uipData.ClassTypeName],
           ['ID',self.uipData.GetFieldValue(self.uipData.ID+'ID')],['Fields',str(self.Fields)])
         )
       if res.FirstRecord.LsValue != '()' :
         self.ObjectAccess.ClearuipartData(self.uipData,
             eval(res.FirstRecord.FieldInit), eval(res.FirstRecord.ValueInit)
           )
         self.ObjectAccess.InsertData(self.uipData,
           self.Fields[1],res.FirstRecord.LsValue,0)

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
       if self.uipData.GetFieldValue(self.uipData.ID+'ID') in (None,'') :
          return
       if self.pAction_bCancel.Visible :
         if self.app.ConfirmDialog(
             'Anda Menyimpan Transaksi : %s' % self.uipData.GetFieldValue(self.uipData.ID+'ID') ) :
           self.uipTransaction.Edit()
           self.uipData.Edit()
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
