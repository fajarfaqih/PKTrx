import com.ihsan.foundation.pobjecthelper as phelper

def NonAktifkanData(config, parameter, returnpacket) :
  helper = phelper.PObjectHelper(config)
  Obj = config.AccessPObject(parameter.FirstRecord.key)
  if Obj.IsNull :
    raise 'PERINGATAN','Data tidak ditemukan'
  if Obj.Status == 'N' :
    raise 'PERINGATAN','Data sudah nonaktif'
  config.BeginTransaction()
  try :
    Obj.Status = 'N'
    rec = helper.LoadScript('GeneralModule.S_ObjectEditor').\
      NonActivateData(config, Obj)
    config.Commit()
  except :
    config.Rollback()
    raise

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  NonAktifkanData(config, parameter, returnpacket)

  return 1
