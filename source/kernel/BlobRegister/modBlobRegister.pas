unit modBlobRegister;

interface

uses PObjConst, KernelIntf, XVariant, PClasses, SysUtils, Classes,
  PClassIntf;

type

  (* PCLASS: BLOBREGISTRATION *)

  TP_blobregistration = class(TPObjImpl, IP_blobregistration, IPObjImpl, IUnknown)
  protected
    function GetPClassImpl: IPClassImpl; override;
    procedure SetNewInstanceKey; override;
    procedure InitializeMethodList; override;
  public
    function _Destructor(var Msg: string): boolean; override;
  public
    function RegisterBLOB(AExtension: string): string;
    procedure SetBLOBField(AObj: IP_GeneralClass; LinkName: string);
    procedure SetBLOBText(AObj: IP_GeneralClass; LinkName: string; AText: string
      );
    function GetBLOBText(AObj: IP_GeneralClass; LinkName: string): string;
    procedure DeleteData();
    function GetURLToData(): string;

    // CANONCIAL METHODS
    procedure _RegisterBLOB(Parameters: IPMethodCallParams);
    procedure _SetBLOBField(Parameters: IPMethodCallParams);
    procedure _SetBLOBText(Parameters: IPMethodCallParams);
    procedure _GetBLOBText(Parameters: IPMethodCallParams);
    procedure _DeleteData(Parameters: IPMethodCallParams);
    procedure _GetURLToData(Parameters: IPMethodCallParams);
    // CANONCIAL - ANCESTOR DISPATCHER METHODS
  end;

  TPCls_blobregistration = class(TPClassImpl, IPClassImpl, IUnknown)
    function CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl; override;
  end;

implementation

uses PModClsDecl, Utils2;

(* -------------------------------------------------------------------------- *)
(* -------------------------------------------------------------------------- *)
(* *****************     CLASS TYPES IMPLEMENTATION        ********************)
(* -------------------------------------------------------------------------- *)
(* -------------------------------------------------------------------------- *)

(* blobregistration class type *)

function TPCls_blobregistration.CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl;
begin
  Result := TP_blobregistration.CreateInstance(ATransCtl);
end;

(* blobregistration class - canoncial methods *)

function TP_blobregistration.GetPClassImpl: IPClassImpl;
begin
  Result := PCls_blobregistration;
end;

procedure TP_blobregistration.InitializeMethodList;
begin
  Self.AddMethod(Self._RegisterBLOB);
  Self.AddMethod(Self._SetBLOBField);
  Self.AddMethod(Self._SetBLOBText);
  Self.AddMethod(Self._GetBLOBText);
  Self.AddMethod(Self._DeleteData);
  Self.AddMethod(Self._GetURLToData);
end;

procedure TP_blobregistration._RegisterBLOB(Parameters: IPMethodCallParams);
  var
    AExtension: string;
    return_value: string;
begin
  AExtension := Parameters['AExtension'].AsString;
  return_value := RegisterBLOB(AExtension);
  Parameters.ReturnValue.AsString := return_value;
end;

procedure TP_blobregistration._SetBLOBField(Parameters: IPMethodCallParams);
  var
    AObj: IP_GeneralClass;
    LinkName: string;
begin
  AObj := IP_GeneralClass(Parameters['AObj'].AsPObj);
  LinkName := Parameters['LinkName'].AsString;
  SetBLOBField(AObj, LinkName);
end;

procedure TP_blobregistration._SetBLOBText(Parameters: IPMethodCallParams);
  var
    AObj: IP_GeneralClass;
    LinkName: string;
    AText: string;
begin
  AObj := IP_GeneralClass(Parameters['AObj'].AsPObj);
  LinkName := Parameters['LinkName'].AsString;
  AText := Parameters['AText'].AsString;
  SetBLOBText(AObj, LinkName, AText);
end;

procedure TP_blobregistration._GetBLOBText(Parameters: IPMethodCallParams);
  var
    AObj: IP_GeneralClass;
    LinkName: string;
    return_value: string;
begin
  AObj := IP_GeneralClass(Parameters['AObj'].AsPObj);
  LinkName := Parameters['LinkName'].AsString;
  return_value := GetBLOBText(AObj, LinkName);
  Parameters.ReturnValue.AsString := return_value;
end;

procedure TP_blobregistration._DeleteData(Parameters: IPMethodCallParams);
begin
  DeleteData();
end;

procedure TP_blobregistration._GetURLToData(Parameters: IPMethodCallParams);
  var
    return_value: string;
begin
  return_value := GetURLToData();
  Parameters.ReturnValue.AsString := return_value;
end;

(* -------------------------------------------------------------------------- *)
(* -------------------------------------------------------------------------- *)
(* *****************    PERSISTENT OBJECT IMPLEMENTATION   ********************)
(* -------------------------------------------------------------------------- *)
(* -------------------------------------------------------------------------- *)

(* blobregistration class *)

procedure TP_blobregistration.SetNewInstanceKey;
begin
  (* Insert code to set primary key here. If inherited action is used,  auto *)
  (* primary key is automatically set from IDGen Server                      *)
  inherited SetNewInstanceKey;
end;

function TP_blobregistration._Destructor(var Msg: string): boolean;
begin
  (* Insert before deletion actions here. Remove the inherited part below if *)
  (* no referential integrity check / actions is required                    *)
  Result := inherited _Destructor(Msg);
end;

function TP_blobregistration.RegisterBLOB(AExtension: string): string;
var
  currentTime: TDateTime;
  cDay, cMonth, cYear: Word;
  sDateNewCode, sTimeNewCode: string;
  cHour, cMin, cSec, cMilSec: Word;
  fileName: string;
  sID: string;
begin
  currentTime := Now;
  DecodeDate(currentTime, cYear, cMonth, cDay);
  sDateNewCode := IntToStr(cYear * 10000 + cMonth * 100 + cDay);
  DecodeTime(Frac(currentTime), cHour, cMin, cSec, cMilSec);
  sTimeNewCode := IntToStr(cHour * 10000 + cMin * 100 + cSec);

  sID := IntToStr(Self['id']);
  fileName := format('%s-%s-%s.%s', [sID, sDateNewCode, sTimeNewCode, AExtension]);
  Self['actualfilename'] := fileName;
  Result := fileName;
end;

procedure TP_blobregistration.SetBLOBField(AObj: IP_GeneralClass
  ; LinkName: string);
var
  ExistingBLOB: IPObjImpl;
  FileName, BaseFileName, HomeDir: string;
begin
  ExistingBLOB := AObj.Links[LinkName];
  if not ExistingBLOB.IsNull then
  begin
    BaseFileName := ExistingBLOB['ActualFileName'];
    HomeDir := Config.GetSysVarIntf.GetStringSysVar('DIRECTORIES', 'BLOBDIR');
    FileName := IncludeTrailingBackslash(HomeDir) + BaseFileName;
    try
      if FileExists(FileName) then DeleteFile(FileName);
    except
    end;
    ExistingBLOB.Delete;
  end;
  AObj.Links[LinkName] := Self;
end;

procedure TP_blobregistration.SetBLOBText(AObj: IP_GeneralClass
  ; LinkName: string; AText: string);
var
  ExistingBLOB: IPObjImpl;
  FileName, BaseFileName, HomeDir: string;
  NewBLOB: IPObjImpl;
  F: TextFile;
  Param: IPMethodCallParams;
begin
  ExistingBLOB := AObj.Links[LinkName];
  HomeDir := Config.GetSysVarIntf.GetStringSysVar('DIRECTORIES', 'BLOBDIR');
  if not ExistingBLOB.IsNull then
  begin
    AObj.Links[LinkName] := nil;
    BaseFileName := ExistingBLOB['ActualFileName'];
    FileName := IncludeTrailingBackslash(HomeDir) + BaseFileName;
    try
      if FileExists(FileName) then DeleteFile(FileName);
    except
    end;
    ExistingBLOB.Delete;
  end;

  if AText <> '' then
  begin
    NewBLOB := Config.CreatePObject('blobregistration', TransCtl);

    Param := TPMethodCallParams.Create(Config, NewBLOB.PClassTypeDecl, 'RegisterBLOB');
    Param.SetParameterAt(0, TXVariant.CreateAsString('txt'));
    NewBLOB.Invoke('RegisterBLOB', Param);
    BaseFileName := Param.ReturnValue.AsString;

    FileName := IncludeTrailingBackslash(HomeDir) + BaseFileName;
    AssignFile(F, FileName);
    Rewrite(F);
    try
      Writeln(F, AText);
    finally
      CloseFile(F);
    end;
    AObj.Links[LinkName] := NewBLOB;
  end;
end;

function TP_blobregistration.GetBLOBText(AObj: IP_GeneralClass; LinkName: string
  ): string;
var
  ExistingBLOB: IPObjImpl;
  FileName, BaseFileName, HomeDir: string;
begin
  ExistingBLOB := AObj.Links[LinkName];
  HomeDir := Config.GetSysVarIntf.GetStringSysVar('DIRECTORIES', 'BLOBDIR');
  if not ExistingBLOB.IsNull then
  begin
    BaseFileName := ExistingBLOB['ActualFileName'];
    FileName := IncludeTrailingBackslash(HomeDir) + BaseFileName;
    if FileExists(FileName) then
      Result := Utils2.GetStringOfFile(FileName)
    else
      Result := '';
  end
  else
    Result := '';
end;

procedure TP_blobregistration.DeleteData();
var
  vBaseFileName: Variant;
  FileName, BaseFileName, HomeDir: string;
begin
  HomeDir := Config.GetSysVarIntf.GetStringSysVar('DIRECTORIES', 'BLOBDIR');
  vBaseFileName := Self['ActualFileName'];
  if VarIsNull(vBaseFileName) then
    BaseFileName := ''
  else
    BaseFileName := VarToStr(vBaseFileName);
  FileName := IncludeTrailingBackslash(HomeDir) + BaseFileName;
  try
    if FileExists(FileName) then DeleteFile(FileName);
  except
  end;
end;

function TP_blobregistration.GetURLToData(): string;
var
  HomeURL: string;
begin
  HomeURL := Config.GetSysVarIntf.GetStringSysVar('DIRECTORIES', 'BLOBHTTPPATH');
  Result := HomeURL + Self['ActualFileName'];
end;

end.
