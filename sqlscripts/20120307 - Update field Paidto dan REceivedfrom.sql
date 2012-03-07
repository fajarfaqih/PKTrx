-- View: olap.v_fct_transaction

DROP VIEW olap.v_fct_transaction;

alter table transaction.transaction alter column paidto type varchar(100);
alter table transaction.transaction alter column receivedfrom type varchar(100);


CREATE OR REPLACE VIEW olap.v_fct_transaction AS 
 SELECT date_part('year'::text, transaction.transactiondate)::smallint AS yyyy, date_part('month'::text, transaction.transactiondate)::smallint AS mm, date_part('day'::text, transaction.transactiondate)::smallint AS dd, (date_part('year'::text, transaction.transactiondate) * 10000::double precision + date_part('month'::text, transaction.transactiondate) * 100::double precision + date_part('day'::text, transaction.transactiondate))::integer AS yyyymmdd, 
        CASE transactionitem.mutationtype
            WHEN 'C'::text THEN transactionitem.amount
            ELSE 0::double precision
        END AS amount_credit, 
        CASE transactionitem.mutationtype
            WHEN 'D'::text THEN transactionitem.amount
            ELSE 0::double precision
        END AS amount_debit, 
        CASE transactionitem.mutationtype
            WHEN 'C'::text THEN transactionitem.ekuivalenamount
            ELSE 0::double precision
        END AS amount_eq_credit, 
        CASE transactionitem.mutationtype
            WHEN 'D'::text THEN transactionitem.ekuivalenamount
            ELSE 0::double precision
        END AS amount_eq_debit, transaction.transactionid, transaction.transactiondate, transaction.referenceno, transaction.transactioncode, transaction.branchcode, transaction.transactiontime, transaction.authstatus, transaction.channelcode, transaction.donorid, transaction.actualdate, transaction.transactionno, transaction.paidto, transaction.donorno, transaction.donorname, transaction.receivedfrom, transaction.marketerid, transaction.channelaccountno, transactionitem.transactionitemid, transactionitem.currencycode, transactionitem.mutationtype, transactionitem.amount, transactionitem.rate, transactionitem.ekuivalenamount, transactionitem.transactionitemtype, transactionitem.parameterjournalid, transactionitem.description, transactionitem.refaccountno, transactionitem.refaccountname, transactionitem.accountcode, accounttransactionitem.accounttitype, accounttransactionitem.accountno, accounttransactionitem.ashnaf, accounttransactionitem.fundentity, accounttransactionitem.percentageofamil, accounttransactionitem.cattype, productaccount.productid
   FROM transaction.transaction
   JOIN transaction.transactionitem ON transaction.transactionid = transactionitem.transactionid
   JOIN transaction.accounttransactionitem ON transactionitem.transactionitemid = accounttransactionitem.transactionitemid
   JOIN transaction.productaccount ON accounttransactionitem.accountno::text = productaccount.accountno::text;

ALTER TABLE olap.v_fct_transaction OWNER TO postgres;
