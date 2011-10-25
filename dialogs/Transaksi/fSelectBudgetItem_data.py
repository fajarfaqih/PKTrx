import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter):
    config = uideflist.config
    uip = uideflist.uipBudgetItem
    helper = phelper.PObjectHelper(config)

    if parameter.DatasetCount != 0 :
      rec = parameter.FirstRecord
      OwnerId = rec.OwnerId
      PeriodId = rec.PeriodId

      sSQL = "\
             select * from budgetitem a \
             where exists \
                (select 1 from budget b,budgetperiod c \
                where a.budgetitemcode=b.itemcode and b.periodid=c.periodid \
                      and b.ownerid=%d and c.periodid=%d ) and is_detail='T' \
             " % (OwnerId,PeriodId)

      res = config.CreateSQL(sSQL).rawresult

      uipData = uideflist.uipBudgetItem.Dataset
      ParentDesc = {}
      while not res.Eof:
        oTran = uipData.AddRecord()
        ItemCode = res.BudgetItemCode

        oTran.SetFieldAt(0, 'PObj:BudgetItem#BudgetItemCode=%s' % ItemCode)
        oTran.BudgetItemCode = ItemCode
        oTran.BudgetItemDescription = res.BudgetItemDescription

        if not ParentDesc.has_key(res.ParentBudgetItemCode):
          oParent = helper.GetObject('BudgetItem',res.ParentBudgetItemCode)
          ParentDesc[res.ParentBudgetItemCode] = oParent.BudgetItemDescription
        # end if
        
        oTran.ParentBudgetItemDescription = ParentDesc[res.ParentBudgetItemCode]

        res.Next()

      #-- while
