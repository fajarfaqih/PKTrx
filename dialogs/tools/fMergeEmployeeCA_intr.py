class fMergeEmployeeCA:
  def __init__(self,formObj,parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    
  def Show(self):
    self.FormContainer.Show()
    
  def Merge1Click(self,sender):
    self.DoMerge(self.uipData1 , self.uipData2, sender)

  def Merge2Click(self,sender):
    self.DoMerge(self.uipData2 , self.uipData1, sender)

  def DoMerge(self,SourceData,ToData,sender):
    OPPOSITE_DATA = {'1' : '2' ,'2' : '1'}
    
    AccountNo1 = self.uipData1.GetFieldValue('LEmployeeCashAdvance.AccountNo') or ''
    if AccountNo1 == '' :
      raise 'Peringatan','Pilih Dahulu Akun Piutang Data 1'

    AccountNo2 = self.uipData2.GetFieldValue('LEmployeeCashAdvance.AccountNo') or ''
    if AccountNo2 == '' :
      raise 'Peringatan','Pilih Dahulu Akun Piutang Data 2'

    if AccountNo1 == AccountNo2 :
      raise 'Peringatan','Data 1 dan Data 2 adalah data yang sama.\nSilakan Periksa kembali data yang diinputkan'\
      
    if self.app.ConfirmDialog(
         "Anda Yakin Akan Menggabung Data %s Ke Data %s " % (
           sender.ControlCaption, OPPOSITE_DATA[sender.ControlCaption]) ):
      SourceAccountNo = SourceData.GetFieldValue('LEmployeeCashAdvance.AccountNo')
      ToAccountNo = ToData.GetFieldValue('LEmployeeCashAdvance.AccountNo')
      
      rph = self.form.CallServerMethod(
          "MergeEmployeeCashAdvance",
          self.app.CreateValues(
               ["SourceAccountNo",SourceAccountNo],
               ["ToAccountNo",ToAccountNo] )
          )

      status = rph.FirstRecord
      if status.IsErr :
        raise 'PERINGATAN',status.ErrMessage

      self.app.ShowMessage('Data Telah Berhasil Digabungkan')
      sender.ExitAction = 1

