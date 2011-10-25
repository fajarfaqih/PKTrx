# Volunteer.py

import com.ihsan.foundation.pobject as pobject

class Bank(pobject.PObject):
  # static variable
  pobject_classname = 'Bank'
  pobject_keys = ['BankCode']

  def CheckForDelete(self):
    sqlCheck = "select count(bankcode) from cashaccount where bankcode='%s'" % (self.BankCode)
    
    resSQL = self.Config.CreateSQL(sqlCheck).rawresult
    if resSQL.GetFieldValueAt(0) > 0:
      raise '','Data tidak dapat dihapus karena menjadi referensi oleh data lain'
      
    return 1
        