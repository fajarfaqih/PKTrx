
def GetDayBalance(config, param):
  aDate = config.FormatDateTime('yyyy-mm-dd', param['Date'])
  
  res = config.CreateSQL("\
    select \
    	sum(case \
    		when mutationtype = 'D' and t.actualdate < '%s' then i.amount \
    		when mutationtype = 'C' and t.actualdate < '%s' then -i.amount \
    		else 0.0 \
    	end) as BeginBalance, \
    	sum(case \
    		when mutationtype = 'D' then i.amount else -i.amount \
    	end) as EndBalance\
    from transactionitem i, accounttransactionitem a, transaction t \
    where i.transactionitemid = a.transactionitemid \
      and i.transactionid = t.transactionid \
      and a.accountno = '%s' \
      and t.actualdate <= '%s' \
  " % (aDate, aDate, param['AccountNo'], aDate)).rawresult
  
  return res.GetFieldValueAt(0) or 0.0, res.GetFieldValueAt(1) or 0.0

def GetFundEntityBalance(FundEntityType):
  
  return  