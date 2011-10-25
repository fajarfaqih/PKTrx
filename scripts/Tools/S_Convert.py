#Modul Script konversi nilai
#
import string
def Terbilang(config,Nominal,KodeMataUang='000',NamaMataUang='Rupiah'): 
  strNominal = config.FormatFloat('0.00', Nominal)
      
  lsNominal = string.split(strNominal,".")
  
  if KodeMataUang == '000' :
    cJmlNominalUtama = int2wordINA(int(lsNominal[0]))
  else :
    cJmlNominalUtama = int2wordEN(int(lsNominal[0]))
       
  cJmlNominalSen = ""
  if int(lsNominal[1]) != 0:
    if KodeMataUang == '000' :
      #cJmlNominalUtama = int2wordINA(lsNominal[0])
      cJmlNominalSen = " Koma " + int2wordINA(int(lsNominal[1]))
    else :
      #cJmlNominalUtama = int2wordEN(lsNominal[0])
      cJmlNominalSen = " point " + int2wordEN(int(lsNominal[1]))
  
  #if KodeMataUang == '000' :
  #  Nominal_Terbilang = cJmlNominalUtama + cJmlNominalSen #+ ' ' + NamaMataUang[KodeMataUang]
  #elif KodeMataUang == '411' : 
  #  Nominal_Terbilang = cJmlNominalUtama + cJmlNominalSen #+ ' ' + NamaMataUang[KodeMataUang]
  Nominal_Terbilang = cJmlNominalUtama + cJmlNominalSen + ' ' + NamaMataUang  
  return Nominal_Terbilang
  
def int2wordINA(b):
  def ParsingTiga(b):    
    if b == 0:
      return "nol"
    bs = str(b)
    pjg = len(bs)
    kalimat = []
    for i in range(pjg):
      c = int(bs[pjg-i-1])
      if c == 0:
        s = ""
      else:
        s = angka[c]
        if i == 1:
          if c == 1:
            sebelum = bs[pjg-1]
            if sebelum == "0":
              s = "Sepuluh"
            else:
              j = len(kalimat)
              if sebelum == "1":
                s = "Sebelas"
              else:
                s = kalimat[j-2] + " Belas"
              kalimat[j-2] = ""
          else:
            s = s + " Puluh"
        elif i == 2:
          if c == 1:
            s = "Seratus"
          else:
            s = s + " Ratus"

      kalimat.append(s)
    kalimat.reverse()
    s = ""
    for i in kalimat:
      s = string.strip(s + " " + i)
    return s
  
  blok = ['','Ribu','Juta','Milyar','Trilyun','Bilyun']
  angka = ['','Satu','Dua','Tiga','Empat','Lima','Enam','Tujuh','Delapan','Sembilan']
  bs = str(b)
  pjg = len(bs)
  JmlBlok = pjg / 3
  if pjg % 3 > 0:
    JmlBlok = JmlBlok + 1
  k = []
  for i in range(JmlBlok):
    c = int(bs[-3:])
    if i == 1 and c == 1:
      s = "seribu"
    elif c == 0 and JmlBlok > 1:
      s = ""
    else:
      s = ParsingTiga(c) + " " + blok[i]
    k.append(string.strip(s))
    bs = bs[:-3]
  k.reverse()
  s = ""
  for i in k:
    s = string.strip(s + " " + i)
  return s

def int2wordEN(n):
    ############# globals ################
    
    ones = ["", "One ","Two ","Three ","Four ", "Five ",
        "Six ","Seven ","Eight ","Nine "]
    
    tens = ["Ten ","Eleven ","Twelve ","Thirteen ", "Fourteen ",
        "Fifteen ","Sixteen ","Seventeen ","Eighteen ","Nineteen "]
    
    twenties = ["","","Twenty ","Thirty ","Forty ",
        "Fifty ","Sixty ","Seventy ","Eighty ","Ninety "]
    
    thousands = ["","Thousand ","Million ", "Billion ", "Trillion ",
        "Quadrillion ", "Quintillion ", "Sextillion ", "Septillion ","Octillion ",
        "Nonillion ", "Decillion ", "Undecillion ", "Duodecillion ", "Tredecillion ",
        "Quattuordecillion ", "Sexdecillion ", "Septendecillion ", "Octodecillion ",
        "Novemdecillion ", "Vigintillion "]

    """
    convert an integer number n into a string of english words
    """
    # break the number into groups of 3 digits using slicing
    # each group representing hundred, thousand, million, billion, ...
    n3 = []
    r1 = ""
    # create numeric string
    ns = str(n)
    for k in range(3, 33, 3):
        r = ns[-k:]
        q = len(ns) - k
        # break if end of ns has been reached
        if q < -2:
            break
        else:
            if  q >= 0:
                n3.append(int(r[:3]))
            elif q >= -1:
                n3.append(int(r[:2]))
            elif q >= -2:
                n3.append(int(r[:1]))
        r1 = r
    
    # break each group of 3 digits into
    # ones, tens/twenties, hundreds
    # and form a string
    nw = ""
    for i, x in enumerate(n3):
        b1 = x % 10
        b2 = (x % 100)//10
        b3 = (x % 1000)//100
        #print b1, b2, b3  # test
        if x == 0:
            continue  # skip
        else:
            t = thousands[i]
        if b2 == 0:
            nw = ones[b1] + t + nw
        elif b2 == 1:
            nw = tens[b1] + t + nw
        elif b2 > 1:
            nw = twenties[b2] + ones[b1] + t + nw
        if b3 > 0:
            nw = ones[b3] + "Hundred " + nw
    return nw

def Divider(kalimat, max):
    s = string.splitfields(kalimat,'\n')
    #t = ""
    r = []
    for k in s:
      t = ""
      s1 = string.splitfields(k)
      for i in s1:
        if len(string.strip(t + " " + i)) > max:
          r.append(t)
          t = ""
        t = string.strip(t+" "+i)
      r.append(t)
    return r

