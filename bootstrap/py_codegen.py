import json
def __lambda_1(val):
  try:
    f = float(val)
    if f.is_integer():
      return int(f)

    return f
  except Exception as e:
    return val


try_float = __lambda_1
class Codegen():
  lambda_c = 0
  indent_c = 0
  head = ""
  out = ""
  def idt(self):
    return ("  " * self.indent_c)

  def parse_block(self,body):
    cg = Codegen()
    cg.indent_c = (self.indent_c + 1)
    return cg.run({"t": "Main","body": body,})

  def do_args(self,args):
    cg = Codegen()
    i = 0
    while (i < len(args)):
      cg.run(args[i])
      cg.out = (cg.out + ",")
      i = (i + 1)
    if ((len(cg.out) > 0) and (cg.out[(0 - 1)] == ",")):
      cg.out = cg.out[:-1]

    return [cg.head,cg.out,]

  def run(self,node):
    run = self.run
    idt = self.idt
    if (node["t"] == "Main"):
      i = 0
      while (i < len(node["body"])):
        self.out = (self.out + idt())
        run(node["body"][i])
        self.out = (self.out + "\n")
        i = (i + 1)
      self.out = (self.head + self.out)
      return self.out
    elif (node["t"] == "Assign"):
      run(node["key"])
      self.out = (self.out + " = ")
      run(node["val"])
    elif (node["t"] == "ImportStmt"):
      self.head = (self.head + "import {}\n".format(node["mod"]))
    elif (node["t"] == "RetStmt"):
      self.out = (self.out + "return ")
      run(node["expr"])
    elif (node["t"] == "FnStmt"):
      if node["isAsync"]:
        self.out = (self.out + "async ")

      self.out = (self.out + "def {}(".format(node["name"]))
      self.out = (self.out + self.do_args(node["args"])[1])
      self.out = (self.out + "):\n")
      self.out = (self.out + self.parse_block(node["body"]))
    elif (node["t"] == "IfStmt"):
      self.out = (self.out + "if ")
      run(node["expr"])
      self.out = (self.out + ":\n")
      self.out = (self.out + self.parse_block(node["body"]))
      if ((len(node["alt"]) > 0) and (node["alt"][0]["t"] == "IfStmt")):
        self.out = ((self.out + idt()) + "el")
        run(node["alt"][0])
      elif (len(node["alt"]) > 0):
        self.out = ((self.out + idt()) + "else:\n")
        self.out = (self.out + self.parse_block(node["alt"]))

    elif (node["t"] == "ForStmt"):
      run(node["init"])
      self.out = (self.out + "\n{}while ".format(idt()))
      run(node["expr"])
      self.out = (self.out + ":\n")
      self.out = (self.out + self.parse_block(node["body"]))
      self.indent_c = (self.indent_c + 1)
      self.out = (self.out + idt())
      run(node["after"])
      self.indent_c = (self.indent_c - 1)
    elif (node["t"] == "WhileStmt"):
      self.out = (self.out + "\n{}while ".format(idt()))
      run(node["expr"])
      self.out = (self.out + ":\n")
      self.out = (self.out + self.parse_block(node["body"]))
    elif (node["t"] == "ClassStmt"):
      self.out = ((self.out + idt()) + "class ")
      self.out = (self.out + "{}({}):\n".format(node["name"],",".join(node["inherits"])))
      self.out = (self.out + self.parse_block(node["body"]))
    elif (node["t"] == "TryCatch"):
      self.out = (self.out + "try:\n")
      self.out = (self.out + self.parse_block(node["body"]))
      self.out = ((self.out + idt()) + "except ")
      run(node["asVar"][0])
      self.out = (self.out + " as {}:\n".format(node["asVar"][1]))
      self.out = (self.out + self.parse_block(node["alt"]))
    elif (node["t"] == "Fcall"):
      if ((node["caller"]["t"] == "Word") and (node["caller"]["val"] == "__inline")):
        self.out = (self.out + node["args"][0]["val"])
      else:
        run(node["caller"])
        self.out = (self.out + "(")
        args = self.do_args(node["args"])
        self.head = (self.head + args[0])
        self.out = (self.out + args[1])
        self.out = (self.out + ")")

    elif (node["t"] == "BinOp"):
      if (node["op"] == "&"):
        node["op"] = "and"
      elif (node["op"] == "|"):
        node["op"] = "or"

      self.out = (self.out + "(")
      run(node["l"])
      self.out = (self.out + " {} ".format(node["op"]))
      run(node["r"])
      self.out = (self.out + ")")
    elif (node["t"] == "Member"):
      if (node["computed"] == True):
        run(node["obj"])
        self.out = (self.out + "[")
        run(node["prop"])
        self.out = (self.out + "]")
      else:
        run(node["obj"])
        self.out = (self.out + ".")
        run(node["prop"])

    elif ((node["t"] == "Word") or (node["t"] == "Int")):
      self.out = (self.out + str(try_float(node["val"])))
    elif (node["t"] == "Str"):
      self.out = (self.out + json.dumps(node["val"]))
    elif (node["t"] == "Lambda"):
      self.lambda_c = (self.lambda_c + 1)
      self.head = ((self.head + idt()) + "def __lambda_{}(".format(self.lambda_c))
      self.head = (self.head + self.do_args(node["args"])[1])
      self.head = (self.head + "):\n")
      self.head = (self.head + self.parse_block(node["body"]))
      self.out = (self.out + "__lambda_{}".format(self.lambda_c))
    elif (node["t"] == "Object"):
      self.out = (self.out + "{")
      i = 0
      while (i < len(node["props"])):
        prop = node["props"][i]
        k = try_float(prop["k"])
        if (type(k) == float):
          self.out = (self.out + k)
        else:
          self.out = (((self.out + "\"") + k) + "\"")

        if (prop["v"] == None):
          self.out = ((self.out + ": ") + k)
        else:
          self.out = (self.out + ": ")
          run(prop["v"])

        self.out = (self.out + ",")
        i = (i + 1)
      self.out = (self.out + "}")
    elif (node["t"] == "Array"):
      self.out = (self.out + "[")
      i = 0
      while (i < len(node["props"])):
        run(node["props"][i])
        self.out = (self.out + ",")
        i = (i + 1)
      self.out = (self.out + "]")
    else:
      raise(Exception("unimplemented node type: {}".format(node["t"])))



