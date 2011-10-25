/* Creating table for class AccountTransactionItem */
/* Creating table for class DonorTransactionItem */

CREATE TABLE ACCOUNTTRANSACTIONITEM(
  ACCOUNTTITYPE  VARCHAR(1),
  ACCOUNTNO VARCHAR(10),
  PRODUCTID INTEGER,  
  TRANSACTIONITEMID INTEGER NOT NULL,
  AMOUNTPERUNIT DOUBLE PRECISION,
  TOTALUNIT INTEGER,
PRIMARY KEY (TRANSACTIONITEMID)
);

/* Creating table for class BankCash */
/* Creating table for class CashAccount */
/* Creating table for class PettyCash */
/* Creating table for class BranchCash */

CREATE TABLE CASHACCOUNT(
  BANKNAME VARCHAR(30),
  BANKACCOUNTNO VARCHAR(20),
  ACCOUNTCURRENCY VARCHAR(5),
  CASHACCOUNTTYPE VARCHAR(1),
  USERNAME VARCHAR(30),
  ACCOUNTNO VARCHAR(10) NOT NULL,
PRIMARY KEY (ACCOUNTNO)
);

/* Creating table for class blobregistration */

CREATE TABLE BLOBREGISTRATION(
  ID INTEGER NOT NULL,
  ACTUALFILENAME VARCHAR(128),
  ISTEMPORARY VARCHAR(1),
PRIMARY KEY (ID)
);


/* Creating table for class BranchLocation */

CREATE TABLE BRANCHLOCATION(
  branch_code VARCHAR(5) NOT NULL,
  BranchName VARCHAR(50),
  BranchStatus VARCHAR(1),
  user_id VARCHAR(20),
  last_update TIMESTAMP,
  masterbranch_code VARCHAR(5),
PRIMARY KEY (branch_code)
);


/* Creating table for class CorporateDonor */

CREATE TABLE CORPORATEDONOR(
  CORPORATION VARCHAR(1),
  NPWP VARCHAR(20),
  SIUPP VARCHAR(20),
  TDP VARCHAR(20),
  LOCATIONTYPE VARCHAR(30),
  OWNERTYPE VARCHAR(30),
  ECONOMICSECTOR VARCHAR(30),
  DONORID VARCHAR(10) NOT NULL,
PRIMARY KEY (DONORID)
);

/* Creating table for class DistTransactionItem */

CREATE TABLE DISTTRANSACTIONITEM(
  DISTTRANSACTIONITEMTYPE VARCHAR(1),
  PRODUCTID INTEGER,
  TRANSACTIONITEMID INTEGER NOT NULL,
PRIMARY KEY (TRANSACTIONITEMID)
);

/* Creating table for class Donor */

CREATE TABLE DONOR(
  DONORID VARCHAR(10) NOT NULL,
  DONORNAME VARCHAR(50),
  ADDRESSSTREET VARCHAR(30),
  ADDRESSKELURAHAN VARCHAR(30),
  ADDRESSSUBDISTRICT VARCHAR(30),
  ADDRESSCITY VARCHAR(30),
  ADDRESSPROVINCE VARCHAR(30),
  ADDRESSPOSTALCODE VARCHAR(10),
  PHONENUMBER VARCHAR(20),
  PHONENUMBER2 VARCHAR(20),
  EMAIL VARCHAR(30),
  FAX VARCHAR(20),
  REFERENCEBY VARCHAR(30),
  STATUS VARCHAR(1),
  DONORTYPE VARCHAR(1),
PRIMARY KEY (DONORID)
);

/* Creating table for class DonorAccount */

CREATE TABLE DONORACCOUNT(
  DONORACCOUNTTYPE VARCHAR(1),
  ACCOUNTNO VARCHAR(10) NOT NULL,
  DONORID VARCHAR(10),
PRIMARY KEY (ACCOUNTNO)
);


/* Creating table for class enum_int */

CREATE TABLE ENUM_INT(
  enum_name VARCHAR(32) NOT NULL,
  enum_value INTEGER NOT NULL,
  enum_description VARCHAR(50),
PRIMARY KEY (enum_name, enum_value)
);

/* Creating table for class enum_varchar */

CREATE TABLE ENUM_VARCHAR(
  enum_name VARCHAR(32) NOT NULL,
  enum_value VARCHAR(2) NOT NULL,
  enum_description VARCHAR(50),
PRIMARY KEY (enum_name, enum_value)
);

/* Creating table for class FinancialAccount */

CREATE TABLE FINANCIALACCOUNT(
  ACCOUNTNO VARCHAR(10) NOT NULL,
  ACCOUNTNAME VARCHAR(50),
  BALANCE DOUBLE PRECISION,
  BRANCHCODE VARCHAR(5),
  CURRENCYCODE VARCHAR(5),
  FINANCIALACCOUNTTYPE VARCHAR(1),
  STATUS VARCHAR(1),
  OPENINGDATE TIMESTAMP,
PRIMARY KEY (ACCOUNTNO)
);

/* Creating table for class GeneralClass */

CREATE TABLE GENERALCLASS(
  ID INTEGER NOT NULL,
PRIMARY KEY (ID)
);

/* Creating table for class HistoryOfChanges */

CREATE TABLE HISTORYOFCHANGES(
  HISTORYID INTEGER NOT NULL,
  CHANGETYPE VARCHAR(1),
  DOMAINOFCHANGE VARCHAR(30),
  PROCESSTIME TIMESTAMP,
  USERID VARCHAR(30),
  DATASOURCETYPE VARCHAR(1),
  DATASOURCEREF VARCHAR(100),
  DATASOURCECLASS VARCHAR(50),
  DATASOURCEREFINTEGER INTEGER,
  TERMINALID VARCHAR(20),
PRIMARY KEY (HISTORYID)
);

/* Creating table for class id_gen */

CREATE TABLE ID_GEN(
  id_code VARCHAR(50) NOT NULL,
  last_id INTEGER,
  locked VARCHAR(1),
PRIMARY KEY (id_code)
);

/* Creating table for class IndividualDonor */

CREATE TABLE INDIVIDUALDONOR(
  GENDER VARCHAR(1),
  BIRTHPLACE VARCHAR(30),
  BIRTHDATE TIMESTAMP,
  IDENTITYTYPE VARCHAR(1),
  RELIGION INTEGER,
  IDENTITYNUMBER VARCHAR(20),
  NPWPNUMBER VARCHAR(20),
  MARTIALSTATE VARCHAR(1),
  LANGUAGE VARCHAR(1),
  LASTFORMALEDUCATION INTEGER,
  FIELDOFWORK VARCHAR(30),
  INCOMEPERMONTH DOUBLE PRECISION,
  EXPENSEPERMONTH DOUBLE PRECISION,
  DONORID VARCHAR(10) NOT NULL,
PRIMARY KEY (DONORID)
);

/* Creating table for class PackageDonorAccount */

CREATE TABLE PACKAGEDONORACCOUNT(
  PAYMENTPERIODVALUE INTEGER,
  PAYMENTAMOUNT DOUBLE PRECISION,
  ACCOUNTNO VARCHAR(10) NOT NULL,
  PAYMENTPERIODTYPE VARCHAR(1),
PRIMARY KEY (ACCOUNTNO)
);

CREATE TABLE PARAMETERGLOBAL (
kode_parameter varchar(10) NOT NULL,
tipe_parameter varchar(1) ,
nilai_parameter DOUBLE PRECISION ,
deskripsi varchar(60) ,
is_parameter_system varchar(1),
nilai_parameter_tanggal timestamp,
nilai_parameter_string varchar(30),
PRIMARY KEY (kode_parameter)
)
/* Creating table for class ParameterJournal */

CREATE TABLE PARAMETERJOURNAL(
  PARAMETERJOURNALID VARCHAR(5) NOT NULL,
  DESCRIPTION VARCHAR(100),
  SQLJOURNALINDIVIDUAL VARCHAR(30),
PRIMARY KEY (PARAMETERJOURNALID)
);

/* Creating table for class ParameterJournalItem */

CREATE TABLE PARAMETERJOURNALITEM(
  PARAMETERJOURNALITEMID  INTEGER NOT NULL,
  PARAMETERJOURNALITEMID VARCHAR(1),
  ACCOUNTCODE VARCHAR(20),
  BRANCHBASE VARCHAR(1),
  DESCRIPTION VARCHAR(50),
  BASESIGN VARCHAR(1),
  CURRENCYBASE VARCHAR(3),
  AMOUNTBASE VARCHAR(30),
  RATEBASE VARCHAR(30),
  PARAMETERJOURNALID VARCHAR(5),
PRIMARY KEY (PARAMETERJOURNALITEMID )
);


/* Creating table for class Product */
/* Creating table for class Program */

CREATE TABLE PRODUCT(
  PRODUCTID INTEGER NOT NULL,
  PRODUCTNAME VARCHAR(30),
  DESCRIPTION VARCHAR(100),
  ACCOUNTOFCOLLECTION VARCHAR(20),
  ACCOUNTOFDISTRIBUTION VARCHAR(20),
  PERCENTAGEOFAMILFUNDS DOUBLE PRECISION,
  PRODUCTTYPE VARCHAR,
  STATUS VARCHAR(1),
  CLOSEDDATE TIMESTAMP,
  FUNDCATEGORY VARCHAR(1),
  FIXEDVALUE VARCHAR(1),
  FIXEDVALUEAMOUNT DOUBLE PRECISION,
  MULTIPACKAGE VARCHAR(1),
PRIMARY KEY (PRODUCTID)
);

/* Creating table for class ProductAccount */

CREATE TABLE PRODUCTACCOUNT(
  ACCOUNTNO VARCHAR(10) NOT NULL,
  PRODUCTID INTEGER,
PRIMARY KEY (ACCOUNTNO)
);

/* Creating table for class ProductBalance */

CREATE TABLE PRODUCTBALANCE(
  PRODUCTBALANCEID INTEGER NOT NULL,
  BALANCE DOUBLE PRECISION,
  PRODUCTID INTEGER,
PRIMARY KEY (PRODUCTBALANCEID)
);

/* Creating table for class ProductDonorAccount */

CREATE TABLE PRODUCTDONORACCOUNT(
  PRODUCTDATYPE VARCHAR(1),
  PRODUCTID INTEGER,
  ACCOUNTNO VARCHAR(10) NOT NULL,
PRIMARY KEY (ACCOUNTNO)
);

/* Creating table for class ProductTransactionHistory */

CREATE TABLE PRODUCTTRANSACTIONHISTORY(
  TRANSACTIONHISTORYID INTEGER NOT NULL,
  PRODUCTBALANCEID INTEGER,
  TRANSACTIONITEMID INTEGER,
PRIMARY KEY (TRANSACTIONHISTORYID)
);


/* Creating table for class ProgramPackage */

CREATE TABLE PROGRAMPACKAGE(
  PACKAGEID INTEGER NOT NULL,
  DESCRIPTION VARCHAR(100),
  AMOUNT DOUBLE PRECISION,
  PRODUCTID INTEGER,
PRIMARY KEY (PACKAGEID)
);

/* Creating table for class Project */

CREATE TABLE PROJECT(
  BUDGETAMOUNT DOUBLE PRECISION,
  STARTDATE TIMESTAMP,
  FINSIHDATE TIMESTAMP,
  PRODUCTID INTEGER NOT NULL,
PRIMARY KEY (PRODUCTID)
);

/* Creating table for class ProjectSponsor */

CREATE TABLE PROJECTSPONSOR(
  PROJECTSPONSORID INTEGER NOT NULL,
  PRODUCTID INTEGER,
  SPONSORID INTEGER,
PRIMARY KEY (PROJECTSPONSORID)
);

/* Creating table for class ProspectiveDonor */

CREATE TABLE PROSPECTIVEDONOR(
  PROSPECTIVEDONORID INTEGER NOT NULL,
  PHONENUMBER VARCHAR(20),
  DONORNAME VARCHAR(30),
  REFERENCEBY VARCHAR(30),
PRIMARY KEY (PROSPECTIVEDONORID)
);

/* Creating table for class ReverseTransaction */

CREATE TABLE REVERSETRANSACTION(
  SOURCETRANSACTIONID INTEGER NOT NULL,
  REVTRANSACTIONID INTEGER,
PRIMARY KEY (SOURCETRANSACTIONID)
);

/* Creating table for class SessionBLOB */

CREATE TABLE SESSIONBLOB(
  ID INTEGER NOT NULL,
  SESSIONID VARCHAR(100),
  SESSIONCONTEXT INTEGER,
  ID1 INTEGER,
PRIMARY KEY (ID)
);

/* Creating table for class Sponsor */

CREATE TABLE SPONSOR(
  SPONSORID INTEGER NOT NULL,
  NAME VARCHAR(50),
  DESCRIPTION VARCHAR(100),
PRIMARY KEY (SPONSORID)
);

/* Creating table for class Transaction */

CREATE TABLE TRANSACTION(
  TRANSACTIONID INTEGER NOT NULL,
  TRANSACTIONDATE TIMESTAMP,
  REFERENCENO VARCHAR(30),
  DESCRIPTION VARCHAR(100),
  INPUTER VARCHAR(20),
  TRANSACTIONCODE VARCHAR(10),
  BRANCHCODE VARCHAR(5),
  AUTHUSER VARCHAR(20),
  TRANSACTIONTIME TIMESTAMP,
  AUTHDATE TIMESTAMP,
  AUTHSTATUS VARCHAR(1),
PRIMARY KEY (TRANSACTIONID)
);

/* Creating table for class TransactionItem */
/* Creating table for class GLTransactionItem */

CREATE TABLE TRANSACTIONITEM(
  TRANSACTIONITEMID INTEGER NOT NULL,
  BRANCHCODE VARCHAR(5),
  CURRENCYCODE VARCHAR(5),
  MUTATIONTYPE VARCHAR(1),
  AMOUNT DOUBLE PRECISION,
  RATE DOUBLE PRECISION,
  EKUIVALENAMOUNT DOUBLE PRECISION,
  TRANSACTIONITEMTYPE VARCHAR(1),
  TRANSACTIONID INTEGER,
  PARAMETERJOURNALID VARCHAR(5),
  GLNUMBER VARCHAR(30),
  GLNAME VARCHAR(100),
PRIMARY KEY (TRANSACTIONITEMID)
);

/* Creating table for class UserApp */

CREATE TABLE USERAPP(
  user_id VARCHAR(20) NOT NULL,
  UserName VARCHAR(30),
  Description VARCHAR(50),
  NoLimitLocation VARCHAR(1),
  login_count INTEGER,
  mod_user_id VARCHAR(20),
  last_update TIMESTAMP,
  branch_code VARCHAR(5),
  USER_ID1 VARCHAR(20),
PRIMARY KEY (user_id)
);

/* Creating table for class UserGroup */

CREATE TABLE USERGROUP(
  group_id VARCHAR(8) NOT NULL,
  GroupName VARCHAR(30),
  Description VARCHAR(50),
  user_id VARCHAR(20),
  last_update TIMESTAMP,
PRIMARY KEY (group_id)
);

/* Creating table for class UserGroupApp */

CREATE TABLE USERGROUPAPP(
  user_id VARCHAR(20) NOT NULL,
  group_id VARCHAR(8) NOT NULL,
PRIMARY KEY (user_id, group_id)
);

/* Creating table for class ZakahDistTransactItem */

CREATE TABLE DISTTRANSACTITEM(
  ASHNAF VARCHAR(1),
  TRANSACTIONITEMID INTEGER NOT NULL,
PRIMARY KEY (TRANSACTIONITEMID)
);

/* Creating table for class ZakahProduct */

CREATE TABLE PRODUCT(
  PRODUCTID INTEGER NOT NULL,
PRIMARY KEY (PRODUCTID)
);

/* Generating enumeration FTBoolean */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'FTBoolean';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('FTBoolean', 'F', 'false');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('FTBoolean', 'T', 'true');

/* Generating enumeration NYBoolean */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'NYBoolean';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('NYBoolean', 'F', 'no');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('NYBoolean', 'T', 'yes');

/* Generating enumeration eBranchStatus */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eBranchStatus';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eBranchStatus', 'B', 'Branch');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eBranchStatus', 'S', 'Sub-branch');

/* Generating enumeration eStatus */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eStatus';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eStatus', 'A', 'Active');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eStatus', 'N', 'NonActive');

/* Generating enumeration eGender */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eGender';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eGender', 'L', 'Laki-Laki');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eGender', 'P', 'Perempuan');

/* Generating enumeration eReligion */

DELETE FROM Enum_Int WHERE Enum_Name = 'eReligion';

INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eReligion', 1, 'Islam');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eReligion', 2, 'Katolik');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eReligion', 3, 'Protestan');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eReligion', 4, 'Hindu');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eReligion', 5, 'Budha');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eReligion', 6, 'Aliran Kepercayaan');

/* Generating enumeration eIdentityType */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eIdentityType';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eIdentityType', 'K', 'KTP');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eIdentityType', 'S', 'SIM');

/* Generating enumeration eMartialState */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eMartialState';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eMartialState', 'K', 'Menikah');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eMartialState', 'B', 'Belum Menikah');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eMartialState', 'S', 'Duda/Janda');

/* Generating enumeration eLanguage */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eLanguage';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eLanguage', 'I', 'Indonesia');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eLanguage', 'M', 'Malaysia');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eLanguage', 'A', 'Arab');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eLanguage', 'E', 'English');

/* Generating enumeration eEducation */

DELETE FROM Enum_Int WHERE Enum_Name = 'eEducation';

INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eEducation', 0, 'Tdk Sekolah Formal');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eEducation', 1, 'SD');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eEducation', 2, 'SMP');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eEducation', 3, 'SMU/Sederajat');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eEducation', 4, 'S1');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eEducation', 5, 'S2');
INSERT INTO Enum_Int (Enum_Name, Enum_Value, Enum_Description) VALUES ('eEducation', 6, 'S3');

/* Generating enumeration eCorporation */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eCorporation';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCorporation', 'B', 'Bank');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCorporation', 'C', 'CV');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCorporation', 'D', 'PD');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCorporation', 'F', 'Firma');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCorporation', 'K', 'Koperasi');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCorporation', 'L', 'Lainnya');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCorporation', 'P', 'PT');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCorporation', 'Y', 'Yayasan');

/* Generating enumeration ePeriodType */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'ePeriodType';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('ePeriodType', 'T', 'Tahunan');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('ePeriodType', 'B', 'Bulanan');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('ePeriodType', 'H', 'Harian');

/* Generating enumeration eAuthStatus */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eAuthStatus';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAuthStatus', 'T', 'Otorisasi');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAuthStatus', 'F', 'Belum Otorisasi');

/* Generating enumeration eAshnaf */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eAshnaf';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAshnaf', 'F', 'Fakir');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAshnaf', 'M', 'Miskin');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAshnaf', 'U', 'Mualaf');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAshnaf', 'H', 'Hamba Sahaya');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAshnaf', 'G', 'Gharimin');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAshnaf', 'S', 'Fisabillillah');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAshnaf', 'I', 'Ibnu Sabil');

/* Generating enumeration eAccountBase */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eAccountBase';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eAccountBase', 'B', 'Base');

/* Generating enumeration eBranchBase */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eBranchBase';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eBranchBase', 'P', 'Pusat');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eBranchBase', 'R', 'Rekening');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eBranchBase', 'T', 'Transaksi');

/* Generating enumeration eBaseSign */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eBaseSign';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eBaseSign', 'P', 'Positive');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eBaseSign', 'N', 'Negative');

/* Generating enumeration eCurrencyBase */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eCurrencyBase';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eCurrencyBase', 'IDR', 'Rupiah');

/* Generating enumeration eChangeType */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eChangeType';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eChangeType', 'C', 'Create');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eChangeType', 'E', 'Edit');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eChangeType', 'D', 'Delete');

/* Generating enumeration eDataSourceType */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eDataSourceType';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eDataSourceType', 'F', 'File');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eDataSourceType', 'S', 'ClassString');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eDataSourceType', 'I', 'ClassInteger');

/* Generating enumeration eFundCategory */

DELETE FROM Enum_Varchar WHERE Enum_Name = 'eFundCategory';

INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eFundCategory', 'Z', 'Zakat');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eFundCategory', 'I', 'Infaq');
INSERT INTO Enum_Varchar (Enum_Name, Enum_Value, Enum_Description) VALUES ('eFundCategory', 'W', 'Wakaf');

