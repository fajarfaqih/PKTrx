#modul untuk mencari parent

def ParentObject(ObjName) :

  ListTreeName = {
    'IndividualDonor':'Donor',
    'CorporateDonor':'Donor',
    'SENTINEL':'PARENT CLASS'
  }
  if ListTreeName.has_key(ObjName) :
    return ListTreeName[ObjName]
  else :
    return ObjName

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)


  return 1
