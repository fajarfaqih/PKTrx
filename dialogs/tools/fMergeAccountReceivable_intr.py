class fMergeAccountReceivable:
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
    
    AccountNo = self.uipData1.GetFieldValue('LAccountReceivable.AccountNo') or ''
    if AccountNo == '' :
      raise 'Peringatan','Pilih Dahulu Akun Piutang Data 1'

    AccountNo = self.uipData2.GetFieldValue('LAccountReceivable.AccountNo') or ''
    if AccountNo == '' :
      raise 'Peringatan','Pilih Dahulu Akun Piutang Data 2'

    if self.app.ConfirmDialog(
         "Anda Yakin Akan Menggabung Data %s Ke Data %s " % (
           sender.ControlCaption, OPPOSITE_DATA[sender.ControlCaption]) ):
      SourceAccountNo = SourceData.GetFieldValue('LAccountReceivable.AccountNo')
      ToAccountNo = ToData.GetFieldValue('LAccountReceivable.AccountNo')
      
      rph = self.form.CallServerMethod(
          "MergeAccountReceivable",
          self.app.CreateValues(
               ["SourceAccountNo",SourceAccountNo],
               ["ToAccountNo",ToAccountNo] )
          )

      status = rph.FirstRecord
      if status.IsErr :
        raise 'PERINGATAN',status.ErrMessage

      sender.ExitAction = 1

