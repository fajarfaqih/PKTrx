
def Form_SetDataEx(uideflist, param):
    config = uideflist.Config
    res = config.CreateSQL("\
      select * from ParameterJournal order by JournalCode").rawresult

    uipJournal = uideflist.uipJournal.Dataset
    while not res.Eof:
        rec = uipJournal.AddRecord()
        idParameter = res.ParameterJournalId
        rec.SetFieldAt(0, 'PObj:ParameterJournal#ParameterJournalId=%d' % idParameter)
        rec.ParameterJournalId = idParameter
        rec.JournalCode        = res.JournalCode
        rec.Description        = res.Description
        rec.DataSource         = res.DataSource

        # get item
        resItem = config.CreateSQL("\
            select * from ParameterJournalItem where ParameterJournalId = %d \
        " % idParameter).rawresult

        while not resItem.Eof:
            recItem = rec.uipJournalItem.AddRecord()
            idItem = resItem.ParameterJournalItemId
            recItem.SetFieldAt(0, 'PObj:ParameterJournalItem#ParameterJournalItemId=%d' % idItem)
            recItem.ParameterJournalItemId = idItem
            recItem.Description    = resItem.Description
            recItem.AccountBase    = resItem.AccountBase
            recItem.AccountCode    = resItem.AccountCode
            recItem.BaseSign       = resItem.BaseSign
            recItem.BranchBase     = resItem.BranchBase
            recItem.CurrencyBase   = resItem.CurrencyBase
            recItem.AmountBase     = resItem.AmountBase
            recItem.RateBase       = resItem.RateBase
            recItem.IsSendJournalDescription = resItem.IsSendJournalDescription
            #recItem.__SYSFLAG = 'L'

            resItem.Next()
        #-- while

        res.Next()
    #-- while

def Form_BeforeDeleteRow(aData):
    if aData.IsA('ParameterJournal'):
        aData.Ls_ParameterJournalItem.DeleteAllPObjs()

