import json
import types, lexer
def __lambda_1(val):
  try:
    f = float(val)
    if f.is_integer(): return int(f)
    return f
  except Exception: return val


throw = lexer.throw
eol = "\n"
try_float = __lambda_1
def Codegen():
  lambda_c = 0
  indent_c = 0
  head = ""
  out = ""
  def setIndent(v):
    nonlocal indent_c
    indent_c = v

  def idt():
    return ("  " * indent_c)

  def parse_block(body):
    cg = Codegen()
    cg.setIndent((indent_c + 1))
    return cg.run({"t": "Main","body": body,})

  def run(node):
    nonlocal out, head, indent_c, lambda_c
    if (node["t"] == "Main"):
      i = 0
      while (i < len(node["body"])):
        out = (out + idt())
        run(node["body"][i])
        out = (out + eol)
        i = (i + 1)
      out = (head + out)
      return out
    elif (node["t"] == "Assign"):
      run(node["key"])
      out = (out + " = ")
      run(node["val"])
    elif (node["t"] == "ImportStmt"):
      head = (head + "import {}{}".format(node["mod"],eol))
    elif (node["t"] == "RetStmt"):
      out = (out + "return ")
      run(node["expr"])
    elif (node["t"] == "FnStmt"):
      out = (out + "def {}({}):{}".format(node["name"],",".join(node["args"]),eol))
      out = (out + parse_block(node["body"]))
    elif (node["t"] == "IfStmt"):
      out = (out + "if ")
      run(node["expr"])
      out = (out + ":{}".format(eol))
      out = (out + parse_block(node["body"]))
      if ((len(node["alt"]) > 0) and (node["alt"][0]["t"] == "IfStmt")):
        out = ((out + idt()) + "el")
        run(node["alt"][0])
      elif (len(node["alt"]) > 0):
        out = ((out + idt()) + "else:{}".format(eol))
        out = (out + parse_block(node["alt"]))

    elif (node["t"] == "ForStmt"):
      run(node["init"])
      out = (out + "{}{}while ".format(eol,idt()))
      run(node["expr"])
      out = (out + ":{}".format(eol))
      out = (out + parse_block(node["body"]))
      indent_c = (indent_c + 1)
      out = (out + idt())
      run(node["after"])
      indent_c = (indent_c - 1)
    elif (node["t"] == "Fcall"):
      if ((node["caller"]["t"] == "Word") and (node["caller"]["val"] == "__inline")):
        out = (out + node["args"][0]["val"])
      else:
        run(node["caller"])
        out = (out + "(")
        i = 0
        while (i < len(node["args"])):
          run(node["args"][i])
          out = (out + ",")
          i = (i + 1)
        if (out[(0 - 1)] == ","):
          out = out[:-1]

        out = (out + ")")

    elif (node["t"] == "BinOp"):
      if (node["op"] == "&"):
        node["op"] = "and"
      elif (node["op"] == "|"):
        node["op"] = "or"

      out = (out + "(")
      run(node["l"])
      out = (out + " {} ".format(node["op"]))
      run(node["r"])
      out = (out + ")")
    elif (node["t"] == "Member"):
      if (node["computed"] == True):
        run(node["obj"])
        out = (out + "[")
        run(node["prop"])
        out = (out + "]")
      else:
        run(node["obj"])
        out = (out + ".")
        run(node["prop"])

    elif ((node["t"] == "Word") or (node["t"] == "Int")):
      out = (out + str(try_float(node["val"])))
    elif (node["t"] == "Str"):
      out = (out + json.dumps(node["val"]))
    elif (node["t"] == "Lambda"):
      lambda_c = (lambda_c + 1)
      head = (head + "def __lambda_{}({}):{}".format(lambda_c,",".join(node["args"]),eol))
      head = (head + parse_block(node["body"]))
      out = (out + "__lambda_{}".format(lambda_c))
    elif (node["t"] == "Object"):
      out = (out + "{")
      i = 0
      while (i < len(node["props"])):
        prop = node["props"][i]
        k = try_float(prop["k"])
        if (type(k) == float):
          out = (out + k)
        else:
          out = (((out + "\"") + k) + "\"")

        if (prop["v"] == None):
          out = ((out + ": ") + k)
        else:
          out = (out + ": ")
          run(prop["v"])

        out = (out + ",")
        i = (i + 1)
      out = (out + "}")
    else:
      throw("unimplemented node type: {}".format(node["t"]))


  exports = {"run": run,"setIndent": setIndent,}
  return types.SimpleNamespace(**exports)

