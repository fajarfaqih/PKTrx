import com.ihsan.foundation.pobjecthelper as phelper
import sys
import com.ihsan.util.customidgenAPI as customidgenAPI

new = 1
edit= 2

def FormSetDataEx(uideflist, parameter) :
    config = uideflist.config
    helper = phelper.PObjectHelper(config)

    rec = uideflist.uipProject.Dataset.AddRecord()
    
    mode = parameter.FirstRecord.mode
    #if mode == new:
    
    rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
    
    #elif mode == edit:
    #  rec.ID = ID
    #  rec.key = parameter.FirstRecord.key
    #rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))

      
      

def ProductOnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  oProduct = helper.GetObjectByInstance('Program', sender.ActiveInstance)
  if (rec.ParentProductId or 0) != 0:
    oParent = oProduct.LProductParent

    rec.SetFieldByName('LProductParent.ProductId',oParent.ProductId)
    rec.SetFieldByName('LProductParent.ProductName',oParent.ProductName)

def SaveProjectDetail(config,parameters,returns):
  status = returns.CreateValues(
         ['Is_Err',0],['Err_Message','']
         )

  helper = phelper.PObjectHelper(config)
  config.BeginTransaction()
  try:
    recProject = parameters.uipProject.GetRecord(0)
    
    # Create Project
    parentProductCode = recProject.GetFieldByName('LProductParent.ProductCode')
    ProductCode = parentProductCode #+ GetProjectCode(config,parentProductCode)
    

#    oProject = helper.CreatePObject('Project')
#    oProject.ProductCode = ProductCode #recProject.ProductCode
#    oProject.ProductName = recProject.ProductName
#    oProject.Description = recProject.Description
#    oProject.IsDetail = 'T'
#    oProject.Status = 'A'
#    oProject.PercentageOfAmilFunds = recProject.PercentageOfAmilFunds
#    oProject.ParentProductId =  recProject.GetFieldByName('LProductParent.ProductId')
#    oProject.BudgetAmount = recProject.BudgetAmount
#    oProject.Level = recProject.Level
#    oProject.StartDate = recProject.StartDate
#    oProject.FinsihDate = recProject.FinsihDate
#    oProject.SetHierarchy()


    # Create ProjectAccount
    BranchCode = recProject.BranchCode
    CurrencyCode = recProject.GetFieldByName('LValuta.Currency_Code')
    
    param = [ProductCode,BranchCode,CurrencyCode]
    
    oProjectAccount = helper.CreatePObject('ProjectAccount',param)
    oProjectAccount.AccountName = recProject.ProductName
    oProjectAccount.ProductId = recProject.ProductId
    oProjectAccount.StartDate = recProject.StartDate
    oProjectAccount.FinishDate = recProject.FinsihDate
    
    oProjectAccount.BranchCode = BranchCode
    oProjectAccount.CurrencyCode = CurrencyCode
    oProjectAccount.Status = 'A'
    oProjectAccount.Openingdate = config.Now()
    oProjectAccount.Balance = 0.0
    
#    oProjectAccount = helper.CreatePObject('ProductAccount',param)
#    oProjectAccount.AccountName = recProject.ProductName
#    oProjectAccount.ProductId = oProject.ProductId
#    oProjectAccount.BranchCode = BranchCode
#    oProjectAccount.CurrencyCode = CurrencyCode
#    oProjectAccount.Status = 'A'
#    oProjectAccount.Openingdate = config.Now()
#    oProjectAccount.Balance = 0.0
    

    for i in range(parameters.uipLsSponsor.RecordCount):
      recProjSponsor = parameters.uipLsSponsor.GetRecord(i)
      oProjectSponsor = helper.CreatePObject('ProjectSponsor')
      oProjectSponsor.ProjectSponsorCode =  recProjSponsor.ProjectSponsorCode
      oProjectSponsor.SponsorId =  recProjSponsor.SponsorId
      
      #oProjectSponsor.ProductId =  oProject.ProductId
      oProjectSponsor.AccountNo =  oProjectAccount.AccountNo

    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    
def GetProjectCode(config,idCode):
  # diubah dengan menggunakan sequence oracle
  customid = customidgenAPI.custom_idgen(config)
  customid.PrepareGetID('PROJECT', idCode)
  try:
    id = customid.GetLastID()
    strID = str(id).zfill(3)
    customid.Commit()
  except:
    customid.Cancel()
    raise '', str(sys.exc_info()[1])

  return strID
