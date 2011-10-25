SELECT
  i.AccountCode
  , i.BranchCode
  , i.CurrencyCode
  , i.MutationType
  , i.Rate
  , i.Amount
  , f.AssetAccountNo
FROM
  Transaction t,
  TransactionItem i,
  InvoiceFA f
WHERE
  t.TransactionId = i.TransactionId
  and i.TransactionItemId = a.TransactionItemId
  and i.TransactionItemId = %(TransactionItemId)d
  and t.TransactionId = f.TransactionId
