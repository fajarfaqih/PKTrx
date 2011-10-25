# ExternalDebtor.py

import com.ihsan.foundation.pobject as pobject

class ExternalDebtor(pobject.PObject):
  # static variable
  pobject_classname = 'ExternalDebtor'
  pobject_keys = ['DebtorId']
  
  def CheckForDelete(self): return 1   