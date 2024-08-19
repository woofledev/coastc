import defs, lexer
import types


Tokens = defs.Tokens
Nodes = defs.Nodes
def Parser():
  tokens = []
  def _pop():
    nonlocal tokens
    return tokens.pop(0)

  def _expect(tok,err):
    nonlocal tokens
    prev = _pop()
    if (not(prev) or (prev[1] != tok)):
      raise(Exception("parser: {}, got {}".format(err,prev[0])))

    return prev

  def parse(text):
    nonlocal tokens
    tokens = lexer.tokenize(text)
    prog = Nodes["Main"]([])
    
    while (tokens[0][1] != Tokens["EOF"]):
      prog["body"].append(_stmt())

    return prog

  def _stmt():
    if (tokens[0][1] == Tokens["Import"]):
      return _stmt_import()
    elif ((tokens[0][1] == Tokens["Fn"]) or (tokens[0][1] == Tokens["Async"])):
      return _stmt_fn()
    elif (tokens[0][1] == Tokens["Ret"]):
      return _stmt_ret()
    elif (tokens[0][1] == Tokens["If"]):
      return _stmt_if()
    elif (tokens[0][1] == Tokens["For"]):
      return _stmt_for()
    elif (tokens[0][1] == Tokens["While"]):
      return _stmt_while()
    elif (tokens[0][1] == Tokens["Class"]):
      return _stmt_class()
    elif (tokens[0][1] == Tokens["Try"]):
      return _stmt_trycatch()
    else:
      return _expr()


  def _expr():
    return _expr_set()

  def _expr_set():
    if ((tokens[0][1] == Tokens["Bigger"]) and (tokens[1][1] == Tokens["POpen"])):
      return _expr_lambda()

    left = _expr_obj()
    if (tokens[0][1] == Tokens["Equals"]):
      _pop()
      return Nodes["Assign"](left,_expr_set())

    return left

  def _expr_lambda():
    _pop()
    params = []
    args = _args()
    i = 0
    while (i < len(args)):
      if ((args[i]["t"] == "Word") or (args[i]["t"] == "Assign")):
        params.append(args[i])
      else:
        raise(Exception("parser: expected fn params to be Word/Assign"))

      i = (i + 1)
    return Nodes["Lambda"](params,_block())

  def _expr_obj():
    if (tokens[0][1] != Tokens["BOpen"]):
      return _expr_arr()

    props = []
    _pop()
    _ = 0
    while ((tokens[0][1] != Tokens["EOF"]) and (tokens[0][1] != Tokens["BClose"])):
      if ((tokens[0][1] == Tokens["Str"]) or (tokens[0][1] == Tokens["Int"])):
        key = _pop()[0]
      else:
        key = _expect(Tokens["Word"],"expected Word")[0]

      if (tokens[0][1] == Tokens["Comma"]):
        _pop()
        props.append(Nodes["Prop"](key,None))
      elif (tokens[0][1] == Tokens["BClose"]):
        props.append(Nodes["Prop"](key,None))
      else:
        _expect(Tokens["Colon"],"expected : following key")
        props.append(Nodes["Prop"](key,_expr()))
        if (tokens[0][1] != Tokens["BClose"]):
          _expect(Tokens["Comma"],"expected , or } following prop")


      _ = 0
    _expect(Tokens["BClose"],"expected } after object")
    return Nodes["Object"](props)

  def _expr_arr():
    if (tokens[0][1] != Tokens["SOpen"]):
      return _expr_logic()

    props = []
    _pop()
    _ = 0
    while ((tokens[0][1] != Tokens["EOF"]) and (tokens[0][1] != Tokens["SClose"])):
      props.append(_expr())
      if (tokens[0][1] == Tokens["Comma"]):
        _pop()

      _ = 0
    _expect(Tokens["SClose"],"expected ] after array")
    return Nodes["Array"](props)

  def _expr_logic():
    left = _expr_math()
    if ["&","|",].__contains__(tokens[0][0]):
      op = _pop()[0]
      left = Nodes["BinOp"](left,_expr_math(),op)

    return left

  def _expr_math():
    left = _expr_call()
    
    while ["+","-","*","/","%","<",">","==","!=","in",].__contains__(tokens[0][0]):
      op = _pop()[0]
      left = Nodes["BinOp"](left,_expr_call(),op)

    return left

  def _expr_call():
    def _call(caller):
      e = Nodes["Fcall"](caller,_args())
      
      while (tokens[0][1] == Tokens["POpen"]):
        e = _call(e)

      return e

    left = _expr_member()
    if (tokens[0][1] == Tokens["POpen"]):
      return _call(left)

    return left

  def _expr_member():
    left = _expr_final()
    _ = 0
    while ((tokens[0][1] == Tokens["Dot"]) or (tokens[0][1] == Tokens["SOpen"])):
      op = _pop()
      if (op[1] == Tokens["Dot"]):
        computed = False
        prop = _expr_final()
        if (prop["t"] != "Word"):
          raise(Exception("parser: expected dot op to be followed by Word"))

      else:
        computed = True
        prop = _expr()
        _expect(Tokens["SClose"],"expected ]")

      left = Nodes["Member"](left,prop,computed)
      _ = 0
    return left

  def _expr_final():
    if (tokens[0][1] == Tokens["Word"]):
      return Nodes["Word"](_pop()[0])
    elif (tokens[0][1] == Tokens["Int"]):
      return Nodes["Int"](float(_pop()[0]))
    elif (tokens[0][1] == Tokens["Str"]):
      return Nodes["Str"](_pop()[0])
    elif (tokens[0][1] == Tokens["POpen"]):
      _pop()
      val = _expr()
      _expect(Tokens["PClose"],"expected )")
      return val
    else:
      raise(Exception("parser: unexpected token '{}'".format(tokens[0][0])))


  def _stmt_import():
    _pop()
    val = _expect(Tokens["Str"],"expected str after import")[0]
    return Nodes["ImportStmt"](val)

  def _stmt_fn():
    isAsync = False
    if (_pop()[1] == Tokens["Async"]):
      isAsync = True
      _pop()

    name = _expect(Tokens["Word"],"expected name after fn")[0]
    params = []
    args = _args()
    i = 0
    while (i < len(args)):
      if ((args[i]["t"] == "Word") or (args[i]["t"] == "Assign")):
        params.append(args[i])
      else:
        raise(Exception("parser: expected fn params to be Word/Assign"))

      i = (i + 1)
    return Nodes["FnStmt"](name,params,_block(),isAsync)

  def _stmt_ret():
    _pop()
    return Nodes["RetStmt"](_expr())

  def _stmt_if():
    _pop()
    cond = _expr()
    body = _block()
    alt = []
    if (tokens[0][1] == Tokens["Else"]):
      _pop()
      if (tokens[0][1] == Tokens["If"]):
        alt = [_stmt_if(),]
      else:
        alt = _block()


    return Nodes["IfStmt"](cond,body,alt)

  def _stmt_for():
    _pop()
    _expect(Tokens["POpen"],"expected ( after for")
    init = _expr()
    _expect(Tokens["Semi"],"expected ; following init")
    cond = _expr()
    _expect(Tokens["Semi"],"expected ; following condition")
    after = _expr()
    _expect(Tokens["PClose"],"expected ) after for")
    return Nodes["ForStmt"](init,cond,after,_block())

  def _stmt_while():
    _pop()
    return Nodes["WhileStmt"](_expr(),_block())

  def _stmt_class():
    _pop()
    name = _expect(Tokens["Word"],"expected Word after class")[0]
    inherits = []
    args = _args()
    i = 0
    while (i < len(args)):
      if (args[i]["t"] != "Word"):
        raise(Exception("parser: expected class inherits to be Word"))

      inherits.append(args[i]["val"])
      i = (i + 1)
    return Nodes["ClassStmt"](name,inherits,_block())

  def _stmt_trycatch():
    _pop()
    body = _block()
    _expect(Tokens["Catch"],"expected catch after try")
    asVar = [_expr_member(),_expect(Tokens["Word"],"expected var name after catch")[0],]
    alt = _block()
    return Nodes["TryCatch"](body,alt,asVar)

  def __arglist():
    def parse():
      left = _expr()
      if (tokens[0][1] == Tokens["Equals"]):
        _pop()
        return Nodes["Assign"](left,parse())

      return left

    args = [parse(),]
    _ = 0
    while ((tokens[0][1] == Tokens["Comma"]) and _pop()):
      args.append(parse())
      _ = 0
    return args

  def _args():
    _expect(Tokens["POpen"],"expected ( in args")
    args = []
    if (tokens[0][1] != Tokens["PClose"]):
      args = __arglist()

    _expect(Tokens["PClose"],"expected ) in args")
    return args

  def _block():
    _expect(Tokens["BOpen"],"expected { in block")
    body = []
    _ = 0
    while ((tokens[0][1] != Tokens["EOF"]) and (tokens[0][1] != Tokens["BClose"])):
      body.append(_stmt())
      _ = 0
    _expect(Tokens["BClose"],"expected } in block")
    return body

  return types.SimpleNamespace(parse = parse)

