SELECT
  i.AccountCode
  , i.BranchCode
  , i.CurrencyCode
  , i.MutationType
  , i.Rate
  , i.Amount
  , t.Amount as TransactAmount
  , (t.Amount - i.Amount) as TransactToItemAmount
  , (i.Amount - t.Amount) as ItemToTransactAmount
  , d.ProductId
  , c.CostAccountNo
FROM
  Transaction t,
  TransactionItem i,
  AccountTransactionItem a,
  DepreciableAsset d,
  AmortizedCost c
WHERE
  t.TransactionId = i.TransactionId
  and i.TransactionItemId = a.TransactionItemId
  and i.TransactionItemId = %(TransactionItemId)d
  and a.AccountNo = d.AccountNo
  and d.AccountNo = c.AccountNo
