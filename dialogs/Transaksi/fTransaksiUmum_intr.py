PI_NONE = -1
PI_TRANSUMUM = 0
PI_TRANSNONCASH = 1
PI_DONOR = 2
PI_DIST = 3
PI_CASH = 4
PI_ACC = 5

class fTransaksiUmum :
    def __init__(self, formObj, parentForm, mode) :
       self.app = formObj.ClientApplication
       self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
       self.ClientFilter = self.app.GetClientClass("TransactionClient",'Transaction')()
       self.mode = mode
       self.HiddenMutation = 0
       self.ParamDisplay = {
        'New':'self.DisplayNew()',
        'NonTunaiDebit':'self.DisplayNonTunai(True)',
        'NonTunaiKredit':'self.DisplayNonTunai(False)',
        'Edit':'self.DisplayEdit()',
        'View':'self.DisplayView()',
        'SENTINEL':''
       }


    def DisplayPage(self, mpPage, PageIdx) :
      for i in range(mpPage.PageCount):
          mpPage.GetPage(i).TabVisible = i == PageIdx

      mpPage.ActivePageIndex = PageIdx

    def EnabledButton(self, State) :
      self.pAction_bOK.Enabled = State
      self.pAction_bCancel.Enabled = State
      self.pAction_bClose.Enabled = State
      self.pAction_bPrintAdv.Enabled = State
      self.pAction_bPrintBSZ.Enabled = State

    def DisplayNew(self) :
      self.DisplayPage(self.mpTrans,PI_TRANSUMUM)
      self.pDonor_TotalUnit.Enabled = 0
      self.pDonor_Amount.Enabled = 1

    def DisplayNonTunai(self, modeDebet) :
      self.DisplayPage(self.mpTrans,PI_TRANSNONCASH)
      self.HiddenMutation = 1
      if modeDebet :
        self.FormObject.Caption = 'Transaksi Pengumpulan Non Tunai'
        self.pData.Visible = 1
        self.Mutation = 'D'
      else :
        self.FormObject.Caption = 'Transaksi Penyaluran Non Tunai'
        self.Mutation = 'C'

    def DisplayEdit(self) :
      pass

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

    def OnExit_Donor(self, sender) :
      rec = self.uipItem
      if rec.GetFieldValue(self.uipData.ID) in (None,'') :
          return
      Field = ('DonorName',)
      res= self.FormObject.CallServerMethod("FindData",
         self.app.CreateValues(['ClassName',self.uipData.ClassTypeName],
           ['ID',rec.GetFieldValue(self.uipData.ID)],['Fields',str(('DonorId',Field))])
         )
      if res.FirstRecord.LsValue != '()' :
         self.ObjectAccess.InsertData(rec,
           Field,res.FirstRecord.LsValue,0)
      else :
         for fl in Field :
           self.uipItem.SetFieldValue(fl,None)

    def BeforePost_Item(self, sender) :
      if self.HiddenMutation :
        sender.MutationType = self.Mutation
        sender.TransType = PI_ACC

      if sender.TransType in (PI_DONOR,) :
        sender.MutationType = 'C'

      if sender.TransType in (PI_DIST,) :
        sender.MutationType = 'D'
        
    def GridToPage(self, idxPage, mode):
      self.uipItem.Edit()
      self.uipItem.EditRow = mode
      self.DisplayPage(self.mpTrans, idxPage)
      self.EnabledButton(0)

    def OnClick_Item(self, sender) :
      if sender.UIPart.TransType != None :
        self.GridToPage(sender.UIPart.TransType,1)

    def OnClick_Trans(self, sender) :
      self.uipItem.Insert()
      self.GridToPage(sender.LayoutOrder+1,0)

    def OnAfterLookup_Produk(self, sender, linkui) :
      if self.uipItem.GetFieldValue('LProduct.FixedValue') == 'T' :
        self.pDonor_TotalUnit.Enabled = 1
        self.pDonor_Amount.Enabled = 0
      else :
        self.pDonor_Amount.Enabled = 1
        self.pDonor_TotalUnit.Enabled = 0

    def OnExit_Nom(self, sender) :
      self.uipItem.TotalUnit = 0

    def OnExit_NomKas(self, sender) :
      if self.uipItem.GetFieldValue('LCashAccount.CurrencyCode') == '000' :
        self.uipItem.Rate = 1
        
    def OnExit_Total(self, sender) :
      self.uipItem.Amount = self.uipItem.TotalUnit * self.uipItem.GetFieldValue('LProduct.FixedValueAmount')
      
    def CopyRowData(self, mode, uip) :
      lsField = {
       'DonorTransactionItem':('Id_Produk_Rekening|LProduct.ProductId',
          'Keterangan|LProduct.ProductName','CurrencyCode|LCurrencyD.Currency_Code',PI_DONOR),
       'DistTransactionItem':('Id_Produk_Rekening|LProduct.ProductId',
          'Keterangan|LProduct.ProductName','CurrencyCode|LCurrencyD.Currency_Code',PI_DIST),
       'AccountTransactionItem':('Id_Produk_Rekening|LCashAccount.AccountNo',
          'Keterangan|LCashAccount.AccountName','CurrencyCode|LCashAccount.CurrencyCode',PI_CASH),
       'GLTransactionItem':('Id_Produk_Rekening|LAccountA.Account_Code',
          'Keterangan|LAccountA.Account_Name','LAccount.Account_Code|LAccountA.Account_Code',
          'LAccount.Account_Name|LAccountA.Account_Name','CurrencyCode|LCurrencyA.Currency_Code',PI_ACC),
       'SENTINEL':''
      }
      for fieldmap in lsField[mode] :
        if type(fieldmap) == type(0) :
          uip.TransType = fieldmap
        else :
          dfield, sfield  = fieldmap.split('|')
          if type(uip.GetFieldValue(sfield)) == type(0) :
            uip.SetFieldValue(dfield,str(uip.GetFieldValue(sfield)))
          else :
            uip.SetFieldValue(dfield,uip.GetFieldValue(sfield))

    def FilterInput(self, mode, uip) :
      lsField = ('Id_Produk_Rekening|Produk/Rekening','CurrencyCode|Valuta','Amount|Nominal')
      lsFieldMode = {
       'DonorTransactionItem':('DonorName|Donatur',),
       'DistTransactionItem':('Ashnaf|Ashnaf',),
       'AccountTransactionItem':('MutationType|Jenis Mutasi',),
       'GLTransactionItem':('MutationType|jenis Mutasi',),
       'SENTINEL':''
      }
      for fieldchk in (lsField + lsFieldMode[mode]) :
        field, info = fieldchk.split('|')
        if uip.GetFieldValue(field) in (None, 0, '') :
          uip.Delete()
          raise 'PERINGATAN','%s Tidak boleh kosong' % info

    
    def PageToGridSwitch(self) :
      self.DisplayPage(self.mpTrans, PI_TRANSUMUM)
      self.EnabledButton(1)

    def OnRow_Save(self, sender) :
      uip = self.uipItem
      self.PageToGridSwitch()
      self.CopyRowData(sender.Name, uip)
      uip.EkuivalenAmount = (uip.Rate or 0.0) * (uip.Amount or 0.0)
      self.FilterInput(sender.Name, uip)
      uip.Post()
      
    def OnRow_Cancel(self, sender) :
      self.PageToGridSwitch()
      self.uipItem.Post()
      if not self.uipItem.EditRow :
        self.uipItem.Delete()
    
    def CancelClick(self, sender) :
      if sender.Caption == '&Cancel' :
        sender.ExitAction = 2
        return
        
    def AfterLookup_Currency (self, sender, linkui) :
      uip = sender.Owner.UIPart
      Link, Field = (sender.LookupField).split('.')
      uip.Rate = uip.GetFieldValue(Link+'.Kurs_Tengah_BI')
      uip.EkuivalenAmount = (uip.Rate or 0.0) * (uip.Amount or 0.0)
      
    def SaveClick(self,sender) :
       if self.pAction_bCancel.Visible :
         if self.app.ConfirmDialog('Anda Menyimpan Transaksi Ini ?') :
           self.uipTransaction.Edit()
           self.FormObject.CommitBuffer()
           ph = self.FormObject.GetDataPacket()
           #rec = ph.Packet.AddNewDatasetEx('Structure','Fields : string;ClassName : string').AddRecord()
           #rec.Fields = str(self.Fields)
           #rec.ClassName = self.uipData.ClassTypeName

           self.ClientFilter.BeforeSaveClient(self.Input,self.Data)
           result = self.FormObject.CallServerMethod("SimpanData",ph)
           sender.ExitAction = 1

       #if self.mode == 'Input' :
       #   self.ObjectAccess.ClearuipartData(self.uipTransaksi,
       #      eval(result.FirstRecord.FieldInit), eval(result.FirstRecord.ValueInit)
       #    )
       #else :
       #   sender.ExitAction = 1
