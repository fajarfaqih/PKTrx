import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
    config = uideflist.config
    helper = phelper.PObjectHelper(uideflist.config)
    paramMode = {
    'New':'ClearDataMode(uideflist,rec, parameter)',
    'Edit':'FillDataMode(uideflist,rec, parameter)',
    'View':'FillDataMode(uideflist,rec, parameter)',
    'SENTINEL':''
    }
    rec = uideflist.uipData.Dataset.AddRecord()
    rec = eval('helper.LoadScript(\'GeneralModule.S_ObjectEditor\').'+ \
      paramMode[parameter.FirstRecord.mode])
    ID = parameter.FirstRecord.ID
    rec.ID = ID
    rec.mode = parameter.FirstRecord.mode
    rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))
    rec.BranchCode = config.SecurityContext.GetUserInfo()[4]

                                         
def VolunteerOnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  if (rec.BranchCode or '') != '':
    corporate = helper.CreateObject('Corporate')
    CabangInfo = corporate.GetCabangInfo(rec.BranchCode)

    rec.SetFieldByName('LCabang.Kode_Cabang',rec.BranchCode)
    rec.SetFieldByName('LCabang.Nama_Cabang',CabangInfo.Nama_Cabang)


def OnBeginProcessData (uideflist, AData) :
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  uData = AData.uipData.GetRecord(0)
  if uData.mode == 'New' :
     pass

def SimpanData(config, parameter, returnpacket) :
    rsrc = parameter.uipData.GetRecord(0)
    #Parameter
    ObjName = 'Volunteer'
    LsFieldInput = ('VolunteerName','HomeAddress','HomePhone','MobilePhone','Email')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)
        rsrc.SetFieldByName(rsrc.ID,rsrc.GetFieldByName(rsrc.ID+'ID'))
        BranchCode = config.SecurityContext.GetUserInfo()[4]

        ID = rsrc.GetFieldByName(rsrc.ID)
        if rsrc.mode in ['New'] :
          if ID in ['',None,0] : raise '','Kode Mitra Belum Diisi'
          VolunteerId = '%s.%s' % (ID,BranchCode)
          oVolunteer = helper.GetObject('Volunteer',VolunteerId)
          if not oVolunteer.isnull : raise 'PERINGATAN','Data Mitra dengan kode %s sudah ada'
        else:
          VolunteerId = ID
          
        obj = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject\
         (config, ObjName, ((rsrc.ID,VolunteerId),), rsrc, LsFieldInput)
        
        obj.BranchCode = BranchCode
        
        config.Commit()
    except :
        config.Rollback()
        raise
    return 1
