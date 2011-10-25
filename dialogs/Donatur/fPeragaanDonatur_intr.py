PI_NONE = -1
PI_INDIVIDU = 0
PI_CORPORATE = 1

class fPeragaanDonatur :
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


    def SwitchDisplay(self, ModeDisplay) :
      self.uipFilter.Edit()
      self.uipFilter.ViewType = ModeDisplay
      if ModeDisplay == 'I' :
        PI = PI_INDIVIDU
      else :
        PI = PI_CORPORATE
      NOTPI = divmod(PI+1,2)[1]
      mpPeragaan = self.mpPeragaan
      for i in range(mpPeragaan.PageCount):
          mpPeragaan.GetPage(i).TabVisible = i != NOTPI

      mpPeragaan.ActivePageIndex = PI
      
    def SetEnabled (self) :
      self.pAction_bClose.Enabled = 1
      self.pTransFilter_TglAwal.Enabled = 1
      self.pTransFilter_TglAkhir.Enabled = 1
      self.pTransFilter_bView.Enabled = 1

    def DisplayPage(self,PageIdx) :
      mpPeragaan = self.mpPeragaan
      for i in range(mpPeragaan.PageCount):
          mpPeragaan.GetPage(i).TabVisible = i == PageIdx

      mpPeragaan.ActivePageIndex = PageIdx

    def DisplayNew(self) :
      self.FormObject.SetAllControlsReadOnly()
      self.pInput_Input_Data.Enabled = 1
      self.pInput_Data.Enabled = 1
      self.SetEnabled()
      self.DisplayPage(PI_NONE)

    def DisplayEdit(self) :
      self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').ReadOnly = 1

    def DisplayView(self) :
      self.FormObject.SetAllControlsReadOnly()
      self.SetEnabled()
      self.SwitchDisplay(self.uipFilter.ViewType)
      
    def FormShow(self, mode) :
       eval(self.ParamDisplay[mode])
       return self.FormContainer.Show()
    def OnExit_Data(self, sender) :
       if self.uipFilter.Data in (None,'') \
         or self.uipFilter.TempData == (self.uipFilter.Input_Data + self.uipFilter.Data):
          return
       res= self.FormObject.CallServerMethod("FindData",
         self.app.CreateValues(['SearchType',self.uipFilter.Input_Data],
           ['Data',self.uipFilter.Data],['ClassName','Donor'],['IDName',self.uipFilter.ID])
         )
       if res.FirstRecord.Values != '()' :
         self.ObjectAccess.InsertData(self.FormObject.GetUIPartByName(res.FirstRecord.uip),
           eval(res.FirstRecord.Struct),res.FirstRecord.Values,0)
         self.SwitchDisplay(res.FirstRecord.uip[-1])

       else :
         self.app.ShowMessage('Donatur tidak ditemukan!!')
         self.DisplayPage(PI_NONE)
       self.uipFilter.TempData = self.uipFilter.Input_Data + self.uipFilter.Data
       
    def OnClick_bView(self, sender) :
       if self.uipFilter.TglAwal > self.uipFilter.TglAkhir :
         raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari Tanggal Akhir'
       Type = self.uipFilter.ViewType
       return
       res= self.FormObject.CallServerMethod("GetHistData",
         self.app.CreateValues(['ModeType',Type],
           ['Data',self.FormObject.GetUIPartByName('uipData'+Type).GetFieldValue(self.uipFilter.ID)],
           ['ClassName',self.FormObject.GetUIPartByName('uipData'+Type).ClassName],
           ['IDName',self.uipFilter.ID])
         )
       if res.FirstRecord.Values != '()' :
         for i in range(result.RecordCount) :
            self.uipResult.Append()
            self.ObjectAccess.InsertData(self.FormObject.GetUIPartByName(res.FirstRecord.uip),
              eval(res.FirstRecord.Struct), result.GetRecord(i).Values, 0)
