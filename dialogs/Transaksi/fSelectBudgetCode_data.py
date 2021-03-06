import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter):
  config = uideflist.config
  helper = phelper.PObjectHelper(config)

  if parameter.DatasetCount != 0 :
    rec = parameter.FirstRecord
    #PeriodId = rec.PeriodId
    ActualDate = rec.ActualDate

    tahun = int(config.FormatDateTime('yyyy',ActualDate))

    oBudgetPeriod = helper.GetObjectByNames('BudgetPeriod', {'PeriodValue': tahun})
    if oBudgetPeriod.isnull : return
    
    PeriodId = oBudgetPeriod.PeriodId
    
    FilterCategory = rec.FilterCategory
    FilterText = rec.FilterText

    AddFilter = ''
    if FilterCategory != '0' :
      LsCategory = {
        '1' : 'BudgetCode',
        '2' : 'LBudgetItem.LParent.BudgetItemDescription',
        '3' : 'LBudgetItem.BudgetItemDescription',
      }

      AddFilter = " and %s LIKE '%s' " % ( LsCategory[FilterCategory], FilterText.upper() )

    BranchCode = config.SecurityContext.GetUserInfo()[4]

    s = ' \
      SELECT FROM BudgetYear \
      [ \
        BranchCode = :BranchCode \
        and PeriodId = :PeriodId \
        %s \
      ] \
      ( \
        BudgetId, \
        ItemCode, \
        ItemName, \
        BudgetCode, \
        Amount, \
        Realization, \
        CurrencyCode, \
        RevisionID, \
        PeriodId, \
        LOwner.OwnerName, \
        LBudgetItem.LParent.ItemId, \
        LBudgetItem.LParent.BudgetItemDescription as ItemGroup, \
        LBudgetItem.BudgetItemDescription as ItemDetail, \
        Self \
      ) \
      THEN ORDER BY ASC BudgetCode,ASC ItemId;' % AddFilter

    oql = config.OQLEngine.CreateOQL(s)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.SetParameterValueByName('PeriodId', PeriodId)

    oql.ApplyParamValues()

    oql.active = 1
    res  = oql.rawresult

    uipData = uideflist.uipBudget.Dataset
    while not res.Eof:
      oTran = uipData.AddRecord()
      oTran.BudgetId = res.BudgetId
      oTran.BudgetCode = res.BudgetCode
      oTran.BudgetOwner = res.OwnerName
      oTran.ItemGroup = res.BudgetItemDescription
      oTran.Description = res.BudgetItemDescription_1

      res.Next()

    #-- while
