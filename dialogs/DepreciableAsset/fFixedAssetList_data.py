import com.ihsan.foundation.pobjecthelper as phelper
import sys
import com.ihsan.timeutils as timeutils


dictAssetType = {'T' : 'Asset Terikat' , 'N' : 'Asset Tidak Terikat'}
def FormatDateForOQL(config,aDate):
  y , m , d = config.ModLibUtils.DecodeDate(aDate)[:3]
  return '%s/%s/%d' % (str(m).zfill(2),str(d).zfill(2),y)

def FormSetDataEx(uideflist,params):
  config = uideflist.Config

  if params.DatasetCount == 0 :

    recData = uideflist.uipData.Dataset.AddRecord()

    recData.BranchCode = config.SecurityContext.GetUserInfo()[4]
    Now = config.Now()
    NowTup = config.ModDateTime.DecodeDate(Now)
    recData.BeginDate = config.ModDateTime.EncodeDate(NowTup[0], 1, 1)
    recData.EndDate = Now

  else:
    helper = phelper.PObjectHelper(config)
    
    recParam = params.FirstRecord

    ds = GetDataAsset(config,recParam)
    
    LsProduct = {}
    while not ds.Eof:
      oFA = uideflist.uipFixedAsset.Dataset.AddRecord()
      oFA.SetFieldAt(0, 'PObj:FixedAsset#AccountNo=%s' % ds.AccountNo)
      oFA.AccountNo = ds.AccountNo
      oFA.AccountName = ds.AccountName
      oFA.NilaiAwal = ds.NilaiAwal
      oFA.Balance = ds.Balance
      oFA.TotalPenyusutan = ds.TotalPenyusutan
      oFA.OpeningDate = timeutils.AsTDateTime(config, ds.OpeningDate)
      oFA.AssetTypeName = dictAssetType[ds.AssetType]
      oFA.AssetCategoryName = ds.AssetCategoryName

      # Get Product Name
      AccountNoProduct = ds.AccountNoProduct or ''
      ProductName = ''
      if AccountNoProduct != '' :
        if LsProduct.has_key(AccountNoProduct) :
          ProductName = LsProduct[AccountNoProduct]
        else:
          oProductAccount = helper.GetObject('ProductAccount',AccountNoProduct)
          ProductName = oProductAccount.AccountName
          LsProduct[AccountNoProduct] = ProductName
        # end if else
      # end if
      oFA.ProductName = ProductName

      oFA.TransactionNo = GetBuyTransactionNo(helper,ds.AccountNo)
        
      ds.Next()
    # end while
    
def GetBuyTransactionNo(helper,AccountNo):
  TransactionNo = ''

  # Get Buy Transaction TransactionNo
  oTran = helper.GetObjectByNames('AccountTransactionItem',
      {'AccountNo' : AccountNo,
       'LTransaction.TransactionCode' : 'FA',
      }
    )

  if not oTran.isnull :
    TransactionNo = oTran.LTransaction.TransactionNo
    
  return TransactionNo
  
def GetDataAsset(config,recParam):

  IsAllAsset = recParam.IsAllAsset
  BranchCode = recParam.BranchCode
  AssetType = recParam.AssetType
  AssetCategoryId = recParam.AssetCategoryId
  AccountProduct = recParam.AccountProduct
  BeginDate = recParam.BeginDate
  EndDate = recParam.EndDate

  AddParam = ""
  if IsAllAsset == 'F' :
    AddParam += "and LAssetCategory.AssetType = '%s' " % AssetType

    if AccountProduct != '' :
      AddParam += " and AccountNoProduct='%s' " % AccountProduct

    if AssetCategoryId != '':
      AddParam += " and AssetCategoryId= %d " % AssetCategoryId

    BeginDate = config.FormatDateTime('mm/dd/yyyy', BeginDate)
    EndDate = config.FormatDateTime('mm/dd/yyyy', EndDate)

    AddParam += " and OpeningDate >= '%s' and OpeningDate <= '%s' " % (BeginDate,EndDate)


  OQLText = " \
    select from FixedAsset \
    [ BranchCode = '%s' \
      %s ] \
    ( AccountNo as Kode_Asset, \
      AccountName as Nama_Asset, \
      NilaiAwal , \
      Balance , \
      TotalPenyusutan , \
      OpeningDate ,\
      AccountNoProduct, \
      LAssetCategory.AssetType, \
      LAssetCategory.AssetCategoryName, \
      self \
    ) then order by Kode_Asset ;" % (BranchCode,AddParam)

  oql = config.OQLEngine.CreateOQL(OQLText)
  oql.ApplyParamValues()
  oql.active = 1
  return oql.rawresult
    
def GetAssetList(config,params,returns):
  status = returns.CreateValues(
     ['Is_Err',0],
     ['Err_Message',''],
     ['BranchName',''],
     ['PeriodStr',''],
     ['AssetTypeName',''],
     ['AssetCategoryName',''],
  )
     
  rdsAssetList = returns.AddNewDatasetEx(
      'AssetList',
    ';'.join([
      'AccountNo: string',
      'AccountName: string',
      'NilaiAwal: float',
      'Balance: float',
      'TotalPenyusutan: float',
      'OpeningDate: string',
      'ProductName: string',
      'TransactionNo: string',
      'AssetTypeName: string',
      'AssetCategoryName: string',
    ])
  )
     
  try:
    helper = phelper.PObjectHelper(config)
    recParam = params.FirstRecord
    data = GetDataAsset(config,recParam)
    
    BeginDate = recParam.BeginDate
    EndDate = recParam.EndDate
    if BeginDate == EndDate :
      PeriodStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
    else:
      PeriodStr = "%s s/d %s" % (
                     config.FormatDateTime('dd-mm-yyyy',BeginDate),
                     config.FormatDateTime('dd-mm-yyyy',EndDate)
                   )
    # end if


    status.BranchName = str(config.SecurityContext.GetUserInfo()[5])
    status.PeriodStr = PeriodStr
    status.AssetTypeName = dictAssetType[recParam.AssetType]
    
    LsProduct = {}
    while not data.Eof :

      recAsset = rdsAssetList.AddRecord()
      recAsset.AccountNo = data.AccountNo
      recAsset.AccountName = data.AccountName
      recAsset.NilaiAwal = data.NilaiAwal
      recAsset.Balance = data.Balance
      recAsset.TotalPenyusutan = data.TotalPenyusutan
      #raise '',config.FormatDateTime("dd/mm/yyyy", config.Now())
      #recAsset.OpeningDate = ''
      recAsset.OpeningDate = config.FormatDateTime('dd/mm/yyyy', timeutils.AsTDateTime(config, data.OpeningDate))
      
      recAsset.AssetTypeName = dictAssetType[data.AssetType]
      recAsset.AssetCategoryName = data.AssetCategoryName

      recAsset.TransactionNo = GetBuyTransactionNo(helper,data.AccountNo)
      
      # Get Product Name
      AccountNoProduct = data.AccountNoProduct or ''
      ProductName = ''
      if AccountNoProduct != '' :
        if LsProduct.has_key(AccountNoProduct) :
          ProductName = LsProduct[AccountNoProduct]
        else:
          oProductAccount = helper.GetObject('ProductAccount',AccountNoProduct)
          ProductName = oProductAccount.AccountName
          LsProduct[AccountNoProduct] = ProductName
        # end if else
      # end if
      recAsset.ProductName = ProductName

      data.Next()
    # end while

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
     
     
