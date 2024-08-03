import defs, re
def __lambda_1(c,first):
  if first:
    return bool(re.match("^[A-Za-z_]+$",c))
  else:
    return bool(re.match("^[A-Za-z0-9_]+$",c))

def __lambda_2(c):
  return bool(re.match("^[0-9]+$",c))
def __lambda_3(c):
  return bool(re.match("^\\s*$",c))
def __lambda_4(msg):
  raise Exception(msg)
def __lambda_5(v,c):
  return [v,c,]

Tokens = defs.Tokens
isalpha = __lambda_1
isint = __lambda_2
isnone = __lambda_3
throw = __lambda_4
_tok = __lambda_5
def tokenize(text):
  out = []
  optable = {"(": Tokens["POpen"],")": Tokens["PClose"],"{": Tokens["BOpen"],"}": Tokens["BClose"],"[": Tokens["SOpen"],"]": Tokens["SClose"],"+": Tokens["BinOp"],"-": Tokens["BinOp"],"*": Tokens["BinOp"],"%": Tokens["BinOp"],"<": Tokens["Smaller"],">": Tokens["Bigger"],".": Tokens["Dot"],",": Tokens["Comma"],":": Tokens["Colon"],";": Tokens["Semi"],"&": Tokens["And"],"|": Tokens["Or"],}
  keywords = {"import": Tokens["Import"],"fn": Tokens["Fn"],"return": Tokens["Ret"],"if": Tokens["If"],"else": Tokens["Else"],"for": Tokens["For"],"while": Tokens["While"],"class": Tokens["Class"],"async": Tokens["Async"],}
  i = 0
  while (i < len(text)):
    char = text[i]
    if char in optable:
      out.append(_tok(char,optable[char]))
    elif (char == "/"):
      if (text[(i + 1)] == "/"):
        _ = 0
        while ((i < len(text)) and (text[i] != "\n")):
          i = (i + 1)
          _ = 0
      else:
        out.append(_tok(char,Tokens["BinOp"]))

    elif (char == "!"):
      i = (i + 1)
      out.append(_tok("!=",Tokens["NEIf"]))
    elif (char == "="):
      if (text[(i + 1)] == "="):
        i = (i + 1)
        out.append(_tok("==",Tokens["EIf"]))
      else:
        out.append(_tok(char,Tokens["Equals"]))

    elif (char == "\""):
      i = (i + 1)
      acc = ""
      _ = 0
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
        _ = 0
      out.append(_tok(acc,Tokens["Str"]))
    elif isint(char):
      acc = ""
      hasDot = False
      _ = 0
      while ((i < len(text)) and (isint(text[i]) or ((text[i] == ".") and (hasDot != True)))):
        if (text[i] == "."):
          hasDot = True

        acc = (acc + text[i])
        i = (i + 1)
        _ = 0
      out.append(_tok(acc,Tokens["Int"]))
      i = (i - 1)
    elif isalpha(char,True):
      acc = ""
      _ = 0
      while ((i < len(text)) and isalpha(text[i],False)):
        acc = (acc + text[i])
        i = (i + 1)
        _ = 0
      tok = Tokens["Word"]
      if acc in keywords:
        tok = keywords[acc]

      out.append(_tok(acc,tok))
      i = (i - 1)
    elif (isnone(char) != True):
      throw(("lexer:unrecognized: " + char))

    i = (i + 1)
  out.append(_tok("<EOF>",Tokens["EOF"]))
  return out

