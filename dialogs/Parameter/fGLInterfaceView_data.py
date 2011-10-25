
def FormSetDataEx(uideflist,parameters):
  config = uideflist.config
  oProduct = config.AccessPObject(parameters.FirstRecord.key)
  if oProduct.IsDetail <> 'T':
    raise 'OnSetDataEx', 'Not transaction product!'

  uideflist.SetData('uipProduct',parameters.FirstRecord.key)
  
