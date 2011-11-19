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


ProjectAccountNo = None
LsProjectSponsorId = {}

def ProjectAfterApplyRow(sender,instance):
  global ProjectAccountNo
  uideflist = sender.uideflist
  config = uideflist.config

  recData = sender.ActiveRecord

  BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  ProductCode = recData.GetFieldByName('LProduct.ProductCode')
  CurrencyCode = recData.GetFieldByName('LCurrency.Currency_Code')

  helper = phelper.PObjectHelper(config)
  #oProjectAccount = helper.GetObjectByInstance('ProjectAccount', instance)

  oProjectAccount = helper.CreatePObject('ProjectAccount', [ProductCode, BranchCode, CurrencyCode])
  oProjectAccount.AccountName = recData.AccountName

  oProjectAccount.Status = 'A'
  oProjectAccount.BranchCode = BranchCode
  oProjectAccount.Openingdate = config.Now()
  oProjectAccount.Balance = 0.0

  oProjectAccount.ProductId = recData.GetFieldByName('LProduct.ProductId')
  oProjectAccount.StartDate = recData.StartDate
  oProjectAccount.FinishDate = recData.FinishDate
  oProjectAccount.CurrencyCode = CurrencyCode

  ProjectAccountNo = oProjectAccount.AccountNo
  #oProjectAccount.AccountNo = ProjectAccountNo
  
def SponsorAfterApplyRow(sender,instance):
  #global LsProjectSponsorId
  global ProjectAccountNo
  
  uideflist = sender.uideflist
  helper = phelper.PObjectHelper(uideflist.config)
  oProjectSponsor = helper.GetObjectByInstance('ProjectSponsor', instance)
  oProjectSponsor.AccountNo = ProjectAccountNo

  #LsProjectSponsorId[sender.ActiveRecord.__SYSID] = oProjectSponsor.ProjectSponsorId
    
def DisbursementAfterApplyRow(sender, instance):
  global LsProjectSponsorId
  uideflist = sender.uideflist

  helper = phelper.PObjectHelper(uideflist.config)
  oProjectSponsorDisb = helper.GetObjectByInstance('ProjectSponsorDisbursement', instance)

