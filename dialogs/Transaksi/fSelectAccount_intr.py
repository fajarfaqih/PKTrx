class fSelectAccount :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.Account_Code = None
    self.Account_Name = None
    self.Account_Type = None

  def GetAccount(self, sFilter=''):
    self.qAccount.OQLText = "\
      select from Account \
       [ Is_Detail = 'T' and Account_Type <> 'M' %s] \
       ( \
         Account_Code, \
         Account_Name, \
         Account_Type, \
         self \
       ) \
      then order by Account_Code; \
    " % (sFilter)
    self.qAccount.DisplayData()
    
    st = self.FormContainer.Show()
    if st == 1:
      self.Account_Code = self.qAccount.GetFieldValue('Account.Account_Code')
      self.Account_Name = self.qAccount.GetFieldValue('Account.Account_Name')
      self.Account_Type = self.qAccount.GetFieldValue('Account.Account_Type')
    #-- if

    return st



