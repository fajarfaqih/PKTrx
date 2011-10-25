import S_HistoryAccess as HistoryAccess, S_ObjectTree as ObjTree
#Modul Script untuk manipulasi Object
#

def ValueToStrList(Obj, LsField) :
  #Mengubah Nilai dalam object menjadi string list(tupple)
  ListValue = '('
  for Field in LsField :
    ListValue += str(Obj.GetFieldByName(Field)) + ','
  ListValue = ListValue[:-1]+')'
  
  return ListValue

def CheckCharacter(input, DictOfCheck) :
  LsOfCheck = ('alpha','upper','lower','digit','specialchar')
  for Check in LsOfCheck  :
    if DictOfCheck.has_key(Check) :
      if Check != 'specialchar' :
        for ch in input :
          DictOfCheck[Check] = eval('ch.is%s()' % Check)
          if DictOfCheck[Check] :
            break
      else :
        for i in range (15) :
          if input.find(chr(33+i)) != -1 :
            DictOfCheck[Check] = True
            break
  return DictOfCheck
  
def SaveDataObject(ObjSource, ObjDest, LsFieldInput) :
  #Menyimpan ke object
  for Field in LsFieldInput :
    if type(Field) == type(LsFieldInput) :
      #untuk type link
      ObjDest.SetFieldByName(Field[1],ObjSource.GetFieldByName(Field[0]))
    else :
      #untuk type biasa
      ObjDest.SetFieldByName(Field,ObjSource.GetFieldByName(Field))
  return 1

def CreateDataFromList(config, ObjName, LsFieldValue) :
  Obj = config.CreatePObject(ObjName)
  for FieldValue in LsFieldValue :
    Obj.SetFieldByName(FieldValue[0],FieldValue[1])
  return Obj

def CreateOrEditDataObject(config, ObjName, LsFieldAndKey, ObjSource, LsFieldInput, Auto = 0, Cek = False) :
  ObjDest, keys = FindObj(config, ObjName, LsFieldAndKey, Cek)
  if ObjDest.IsNull :
     ObjDest = config.CreatePObject(ObjName)
     if not Auto :
       for rec in LsFieldAndKey :
         ObjDest.SetFieldByName(rec[0],rec[1])

  SaveDataObject(ObjSource, ObjDest, LsFieldInput)
  LsFieldInput += keys
  HistoryAccess.CreateHistory(config, ObjName, ObjDest, LsFieldInput, ObjSource.mode)
  
  return ObjDest

def NonActivateData(config, Obj) :
  HistoryAccess.CreateHistory(config, Obj.ClassName, Obj, '', 'NA')

def FindObj(config, ObjName, FieldAndKeys, Cek = False ) :
  Field = ()
  if Cek :
    ObjName = ObjTree.ParentObject(ObjName)
    
  Obj = config.CreatePObjImplProxy(ObjName)
  for rec in FieldAndKeys :
    if rec != '' :
      Obj.SetKey(rec[0],rec[1])
      Field += (rec[0],)

  if Cek and not Obj.IsNull :
    raise 'PERINGATAN','Data Sudah Tersimpan dalam System'

  return Obj,Field

def AccessValuesObject(config, ObjName, FieldAndKeys, FieldReturns, Cek = False) :
  Value = ()
  Obj, keys = FindObj(config, ObjName, FieldAndKeys, Cek)
  if not Obj.IsNull :
    for Field in FieldReturns :
      if Field != '' :
         Value += (Obj.GetFieldByName(Field),)
  return Value
  
def FillUserData(config, rec, mode='New') :
    rec.UserPengubah = config.SecurityContext.UserID
    rec.TglUbah = int(config.Now())
    rec.TerminalUbah = config.SecurityContext.InitIP

def ClearDataMode(uideflist, rec, parameter) :
    config = uideflist.config
    rec.Status = 'A'
    FillUserData(config, rec, parameter.FirstRecord.mode)
    return rec

def FillDataMode(uideflist, rec, parameter) :
    config = uideflist.config
    uideflist.SetData('uipData',parameter.FirstRecord.key)
    rec = uideflist.uipData.ActiveRecord
    if parameter.FirstRecord.mode == 'Edit' :
      FillUserData(config, rec, parameter.FirstRecord.mode)
    return rec

def FillUserDataCabang(config, rec, mode='New') :
    rec.UserOtorisasi = config.SecurityContext.UserID
    rec.TanggalOtorisasi = int(config.Now())
    rec.TerminalOtorisasi = config.SecurityContext.InitIP

def ClearDataModeCabang(uideflist, rec, parameter) :
    config = uideflist.config
    rec.Status = 'A'
    FillUserDataCabang(config, rec, parameter.FirstRecord.mode)
    return rec

def FillDataModeCabang(uideflist, rec, parameter) :
    config = uideflist.config
    uideflist.SetData('uipData',parameter.FirstRecord.key)
    rec = uideflist.uipData.ActiveRecord
    if parameter.FirstRecord.mode == 'Edit' :
      FillUserDataCabang(config, rec, parameter.FirstRecord.mode)
    return rec


def StrToDate(config,StrDate, format) :
    if format == 'MM/DD/YYYY' :
      MM = int(StrDate[:2])
      DD = int(StrDate[3:5])
      YY = int(StrDate[-4:])
      VDate = config.ModDateTime.EncodeDate(YY,MM,DD)
    elif format == 'MM/DD/YY' :
      MM = int(StrDate[:2])
      DD = int(StrDate[3:5])
      YY = 1900+int(StrDate[-2:])
      VDate = config.ModDateTime.EncodeDate(YY,MM,DD)
    else :
      raise 'PERINGATAN','format tanggal salah'
    return VDate

