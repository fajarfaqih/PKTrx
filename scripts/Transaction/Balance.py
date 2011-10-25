
def FundEntityBalance(config, Date=None, FundEntity=1):  
  if Date == None :
    Date = int(config.Now())

  aDate = config.FormatDateTime('yyyy-mm-dd', Date)
    
  param = {}
  param['FUNDENTITY'] = str(FundEntity)
  param['DATE'] = aDate
  
  sSQL ="\
    select \
    	sum(case \
    		when mutationtype = 'D' and t.transactiondate < '%(DATE)s' then -i.amount \
    		when mutationtype = 'C' and t.transactiondate < '%(DATE)s' then i.amount \
    		else 0.0 \
    	end) as BeginBalance \
    from transactionitem i, accounttransactionitem a, transaction t \
    where i.transactionitemid = a.transactionitemid \
      and i.transactionid = t.transactionid \
      and a.FundEntity = %(FUNDENTITY)s \
      and t.transactiondate <= '%(DATE)s' \
  " % param 
  
  res = config.CreateSQL(sSQL).rawresult
  
  return res.GetFieldValueAt(0) or 0.0
  
def AllFundEntityBalance(config, Date=None):  
  if Date == None :
    Date = int(config.Now())

  aDate = config.FormatDateTime('yyyy-mm-dd', Date)
    
  param = {}
  param['FUNDENTITY'] = str(FundEntity)
  param['DATE'] = aDate
  
  sSQL ="\
    select \
    	sum(case \
    		when mutationtype = 'D' then -i.amount \
    		when mutationtype = 'C' then i.amount \
    		else 0.0 \
    	end) as BeginBalance \
    from transactionitem i, accounttransactionitem a, transaction t \
    where i.transactionitemid = a.transactionitemid \
      and i.transactionid = t.transactionid \
      and a.FundEntity = %(FUNDENTITY)s \
      and t.transactiondate < '%(DATE)s' \
  " % param 
  
  res = config.CreateSQL(sSQL).rawresult
  
  return res.GetFieldValueAt(0) or 0.0