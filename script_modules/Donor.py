# Donor.py

import com.ihsan.foundation.pobject as pobject

class Donor(pobject.PObject):
    # static variable
    pobject_classname = 'Donor'
    pobject_keys = ['DonorId']
    
    def OnCreate(self):
        self.Status = 'A'

class CorporateDonor(Donor):
    # static variable
    pobject_classname = 'CorporateDonor'
        
class IndividualDonor(Donor):
    # static variable
    pobject_classname = 'IndividualDonor'    
