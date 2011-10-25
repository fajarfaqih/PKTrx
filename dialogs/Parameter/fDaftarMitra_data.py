import sys
import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist,params):
  config = uideflist.config

  recParam = uideflist.uipParam.Dataset.AddRecord()
  recParam.BranchCode = config.SecurityContext.GetUserInfo()[4]
  
def GetDataMitra(config,parameters,returns):
  status = returns.CreateValues(
    ['IsErr',0],
    ['ErrMessage','']
  )

  dsData = returns.AddNewDatasetEx(
      'MasterData',
    ';'.join([
      'VolunteerId: string',
      'VolunteerName: string',
      'Email: string',
      'HomeAddress: string',
      'HomePhone: string',
      'MobilePhone: string',
      'BranchCode: string',
      'BranchName: string',
    ])
  )

  try:
    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate')

    dStatus = {'A' : 'Active','N' : 'Not Active'}
    strSQL = "select * from Volunteer order by BranchCode, VolunteerId"

    oRes = config.CreateSQL(strSQL).RawResult
    oRes.First()
    dictCabang = {}
    while not oRes.Eof:
      recData = dsData.AddRecord()
      recData.VolunteerId = oRes.VolunteerId
      recData.VolunteerName = oRes.VolunteerName
      recData.Email = oRes.Email
      recData.HomeAddress = oRes.HomeAddress
      recData.HomePhone = oRes.HomePhone
      recData.MobilePhone = oRes.MobilePhone

      BranchCode = oRes.BranchCode
      if not dictCabang.has_key(BranchCode):
        CabangInfo = corporate.GetCabangInfo(BranchCode)
        dictCabang[BranchCode] = CabangInfo.Nama_Cabang
        
      recData.BranchCode = BranchCode
      recData.BranchName = dictCabang[BranchCode]

      oRes.Next()
    # end while

  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])
