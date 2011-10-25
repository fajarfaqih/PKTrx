class fDonaturIndividu :
    def __init__(self, formObj, parentForm, mode) :
       self.app = formObj.ClientApplication
       self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
       self.mode = mode
       self.ParamDisplay = {
        'New':'self.DisplayNew()',
        'Edit':'self.DisplayEdit()',
        'View':'self.DisplayView()',
        'SENTINEL':''
       }

    def DisplayNew(self) :
      pass
      
    def DisplayEdit(self) :
      self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').ReadOnly = 1

    def DisplayView(self) :
      self.FormObject.SetAllControlsReadOnly()
      self.pAction_bOK.Enabled = 1
      self.pAction_bClose.Visible = 0
      self.pAction_bOK.Caption = '&Close'
      self.pAction_bOK.Cancel = 1

    def FormShow(self, mode) :
       self.Fields = ((self.uipData.ID),('DonorName','AddressStreet','AddressKelurahan','AddressSubDistrict',
          'AddressCity','AddressProvince','AddressPostalCode','PhoneNumber',
          'PhoneNumber2','Email','Fax','ReferenceBy','Gender','BirthPlace','BirthDate',
          'IdentityType','IdentityNumber','Religion','NPWPNumber','MartialState',
          'Language','LastFormalEducation','FieldOfWork','IncomePerMonth','ExpensePerMonth'
               ))
       self.FieldInit = ('mode','ID','IdentityType','Religion','MartialState','Language','LastFormalEducation')
       self.ValueInit = (mode,self.uipData.ID,'K',1,'K','I',4)
       eval(self.ParamDisplay[mode])
       self.FormContainer.Show()

    def OnExit_Tlp(self, sender) :
       if sender.Text[0] != '+' :
         sender.SetFocus()
         raise 'PERINGATAN','No Telepon awal dengan + (tanda \'+\') diikuti kode negara'
         
    def OnExit_ID(self, sender) :
       if self.mode != 'New' :
         return
       if self.uipData.GetFieldValue(self.uipData.ID+'ID') in (None,'') :
          return
       res= self.FormObject.CallServerMethod("FindData",
         self.app.CreateValues(['ClassName',self.uipData.ClassTypeName],
           ['ID',self.uipData.GetFieldValue(self.uipData.ID+'ID')],['Fields',str(self.Fields)])
         )
       if res.FirstRecord.LsValue != '()' :
         self.ObjectAccess.InsertData(self.uipData,
           self.Fields[1],res.FirstRecord.LsValue,0)

    def OnAfterLookup_Check(self, sender, LinkUI) :
       uip = sender.Owner.UIPart
       if uip.GetFieldValue(sender.Name+'.Status') != 'A' :
          uip.ClearLink(sender.Name)
          raise 'PERINGATAN','Data yang dipakai sudah tidak aktif'
       return 1
       
    def SaveClick(self,sender) :
       if self.uipData.GetFieldValue(self.uipData.ID+'ID') in (None,'') :
          return
       if self.pAction_bClose.Visible :
         if self.app.ConfirmDialog(
             'Anda Menyimpan Data : %s' % self.uipData.GetFieldValue(self.uipData.ID+'ID') ) :
           self.FormObject.CommitBuffer()
           ph = self.FormObject.GetDataPacket()
           rec = ph.Packet.AddNewDatasetEx('Structure','Fields : string;ClassName : string').AddRecord()
           rec.Fields = str(self.Fields)
           rec.ClassName = self.uipData.ClassTypeName
           result = self.FormObject.CallServerMethod("SimpanData",ph)

       if self.mode == 'New' :
          self.ObjectAccess.ClearuipartData(self.uipData,
             self.FieldInit, self.ValueInit
           )
       else :
          sender.ExitAction = 1
