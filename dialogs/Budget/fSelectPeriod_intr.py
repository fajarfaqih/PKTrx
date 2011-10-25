class fSelectPeriod:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    
  def LookUp(self):
    query = self.qBudgetPeriod
    res = self.FormContainer.Show()
    if (res == 1) and query.HasData:
      self.Bulan = query.GetFieldValue("BudgetPeriod.Bulan")
      self.Tahun = query.GetFieldValue("BudgetPeriod.Tahun")
      self.PeriodID = query.GetFieldValue("BudgetPeriod.PeriodID")
      if self.Bulan in ['',None]:
         raise "PERINGATAN","Tidak ada periode yang dipilih"
      return 1
    else:
      return 0
    
    
