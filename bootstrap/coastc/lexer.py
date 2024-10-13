import defs,re
def __lambda_1(c,first):
  if first:
    return bool(re.match("^[A-Za-z_]+$",c))
  else:
    return bool(re.match("^[A-Za-z0-9_]+$",c))

def __lambda_2(c):
  return bool(re.match("^[0-9]+$",c))
def __lambda_3(c):
  return bool(re.match("^\\s*$",c))
def __lambda_4(v,c,pos):
  return [v,c,pos,]

Tokens = defs.Tokens
isalpha = __lambda_1
isint = __lambda_2
isnone = __lambda_3
_tok = __lambda_4
def tokenize(text):
  out = []
  optable = {"(": Tokens["POpen"],")": Tokens["PClose"],"{": Tokens["BOpen"],"}": Tokens["BClose"],"[": Tokens["SOpen"],"]": Tokens["SClose"],"+": Tokens["BinOp"],"-": Tokens["BinOp"],"*": Tokens["BinOp"],"%": Tokens["BinOp"],"<": Tokens["Smaller"],">": Tokens["Bigger"],"in": Tokens["BinOp"],".": Tokens["Dot"],",": Tokens["Comma"],":": Tokens["Colon"],";": Tokens["Semi"],"&": Tokens["And"],"|": Tokens["Or"],}
  keywords = {"import": Tokens["Import"],"fn": Tokens["Fn"],"return": Tokens["Ret"],"if": Tokens["If"],"else": Tokens["Else"],"for": Tokens["For"],"foreach": Tokens["Foreach"],"while": Tokens["While"],"class": Tokens["Class"],"async": Tokens["Async"],"try": Tokens["Try"],"catch": Tokens["Catch"],}
  i = 0
  while (i < len(text)):
    char = text[i]
    if (char in optable):
      out.append(_tok(char,optable[char],i))
    elif (char == "/"):
      if (text[(i + 1)] == "/"):
        
        while ((i < len(text)) and (text[i] != "\n")):
          i = (i + 1)

      elif (text[(i + 1)] == "*"):
        i = (i + 2)
        
        while ((i < len(text)) and not(((text[i] == "*") and (text[(i + 1)] == "/")))):
          i = (i + 1)

        i = (i + 1)
      else:
        out.append(_tok(char,Tokens["BinOp"],i))

    elif (char == "!"):
      i = (i + 1)
      out.append(_tok("!=",Tokens["NEIf"],i))
    elif (char == "="):
      if (text[(i + 1)] == "="):
        i = (i + 1)
        out.append(_tok("==",Tokens["EIf"],i))
      else:
        out.append(_tok(char,Tokens["Equals"],i))

    elif (char == "\""):
      i = (i + 1)
      acc = ""
      
      while (i < len(text)):
        if (text[i] == "\""):
          break

        if (text[i] == "\\"):
          i = (i + 1)
          if (i < len(text)):
            if (text[i] == "\""):
              acc = (acc + "\"")
            elif (text[i] == "\\"):
              acc = (acc + "\\")
            elif (text[i] == "n"):
              acc = (acc + "\n")
            elif (text[i] == "t"):
              acc = (acc + "\t")
            else:
              acc = ((acc + "\\") + text[i])


        else:
          acc = (acc + text[i])

        i = (i + 1)

      out.append(_tok(acc,Tokens["Str"],i))
    elif isint(char):
      acc = ""
      hasDot = False
      
      while ((i < len(text)) and (isint(text[i]) or ((text[i] == ".") and (hasDot != True)))):
        if (text[i] == "."):
          hasDot = True

        acc = (acc + text[i])
        i = (i + 1)

      out.append(_tok(acc,Tokens["Int"],i))
      i = (i - 1)
    elif isalpha(char,True):
      acc = ""
      
      while ((i < len(text)) and isalpha(text[i],False)):
        acc = (acc + text[i])
        i = (i + 1)

      tok = Tokens["Word"]
      if (acc in keywords):
        tok = keywords[acc]

      out.append(_tok(acc,tok,i))
      i = (i - 1)
    elif (isnone(char) != True):
      raise(Exception(("lexer:unrecognized: " + char)))

    i = (i + 1)
  out.append(_tok("<EOF>",Tokens["EOF"],i))
  return out

