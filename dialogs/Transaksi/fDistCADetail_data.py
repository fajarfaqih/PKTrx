

def FormSetDataEx(uideflist,params):
  config = uideflist.Config
  recParam = params.FirstRecord

  if params.DatasetCount == 0 : return
  
  key = 'PObj:DistributionTransferInfo#DistributionId=%d' % recParam.DistributionId
  uideflist.SetData('uipDistTransInfo',key)
  
  
