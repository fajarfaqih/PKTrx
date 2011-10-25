import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist,parameters):
  oKey = parameters.FirstRecord.key
  oProject = uideflist.config.AccessPObject(oKey)
  if oProject.IsDetail != 'T':
    raise 'SetData', 'Bukan proyek detail!'
    
  uideflist.SetData('uipProject',oKey)
