SELECT
  i.AccountCode
  , i.BranchCode
  , i.CurrencyCode
  , i.MutationType
  , i.Rate
  , i.Amount
  , t.Amount as TransactAmount
  , d.PrincipalAmount
  , d.ShareAmount
FROM
  Transaction t,
  TransactionItem i,
  AccountTransactionItem a,
  AccReceivableTransactItem d  
WHERE
  t.TransactionId = i.TransactionId
  and i.TransactionItemId = a.TransactionItemId
  and i.TransactionItemId = %(TransactionItemId)d
  and a.TransactionItemId = d.TransactionItemId