SELECT
  i.AccountCode
  , i.BranchCode
  , i.CurrencyCode
  , i.MutationType
  , i.Rate
  , i.Amount
  , i.Amount * i.Rate as EkuivAmount
  , (t.Amount - i.Amount) as RAKAmount 
FROM
  Transaction t,
  TransactionItem i
WHERE
  t.TransactionId = i.TransactionId
  and i.TransactionItemId = %(TransactionItemId)d
