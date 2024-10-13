import defs,lexer

Tokens = defs.Tokens
Nodes = defs.Nodes
class Parser:
  def __init__(self):
    self.tokens = []

  def _pop(self):
    return self.tokens.pop(0)

  def _expect(self,tok,err):
    prev = self._pop()
    if (not(prev) or (prev[1] != tok)):
      raise(Exception("parser: {}, got {}".format(err,prev[0])))

    return prev

  def parse(self,text):
    self.tokens = lexer.tokenize(text)
    prog = Nodes["Main"]([])
    
    while (self.tokens[0][1] != Tokens["EOF"]):
      prog["body"].append(self._stmt())

    return prog

  def _stmt(self):
    if (self.tokens[0][1] == Tokens["Import"]):
      return self._stmt_import()
    elif ((self.tokens[0][1] == Tokens["Fn"]) or (self.tokens[0][1] == Tokens["Async"])):
      return self._stmt_fn()
    elif (self.tokens[0][1] == Tokens["Ret"]):
      return self._stmt_ret()
    elif (self.tokens[0][1] == Tokens["If"]):
      return self._stmt_if()
    elif (self.tokens[0][1] == Tokens["For"]):
      return self._stmt_for()
    elif (self.tokens[0][1] == Tokens["Foreach"]):
      return self._stmt_foreach()
    elif (self.tokens[0][1] == Tokens["While"]):
      return self._stmt_while()
    elif (self.tokens[0][1] == Tokens["Class"]):
      return self._stmt_class()
    elif (self.tokens[0][1] == Tokens["Try"]):
      return self._stmt_trycatch()
    else:
      return self._expr()


  def _expr(self):
    return self._expr_set()

  def _expr_set(self):
    if ((self.tokens[0][1] == Tokens["Bigger"]) and (self.tokens[1][1] == Tokens["POpen"])):
      return self._expr_lambda()

    left = self._expr_obj()
    if (self.tokens[0][1] == Tokens["Equals"]):
      self._pop()
      return Nodes["Assign"](left,self._expr_set())

    return left

  def _expr_lambda(self):
    self._pop()
    params = []
    args = self._args()
    i = 0
    while (i < len(args)):
      if ((args[i]["t"] == "Word") or (args[i]["t"] == "Assign")):
        params.append(args[i])
      else:
        raise(Exception("parser: expected fn params to be Word/Assign"))

      i = (i + 1)
    return Nodes["Lambda"](params,self._block())

  def _expr_obj(self):
    if (self.tokens[0][1] != Tokens["BOpen"]):
      return self._expr_arr()

    props = []
    self._pop()
    
    while ((self.tokens[0][1] != Tokens["EOF"]) and (self.tokens[0][1] != Tokens["BClose"])):
      if ((self.tokens[0][1] == Tokens["Str"]) or (self.tokens[0][1] == Tokens["Int"])):
        key = self._pop()[0]
      else:
        key = self._expect(Tokens["Word"],"expected Word")[0]

      if (self.tokens[0][1] == Tokens["Comma"]):
        self._pop()
        props.append(Nodes["Prop"](key,None))
      elif (self.tokens[0][1] == Tokens["BClose"]):
        props.append(Nodes["Prop"](key,None))
      else:
        self._expect(Tokens["Colon"],"expected : following key")
        props.append(Nodes["Prop"](key,self._expr()))
        if (self.tokens[0][1] != Tokens["BClose"]):
          self._expect(Tokens["Comma"],"expected , or } following prop")



    self._expect(Tokens["BClose"],"expected } after object")
    return Nodes["Object"](props)

  def _expr_arr(self):
    if (self.tokens[0][1] != Tokens["SOpen"]):
      return self._expr_logic()

    props = []
    self._pop()
    
    while ((self.tokens[0][1] != Tokens["EOF"]) and (self.tokens[0][1] != Tokens["SClose"])):
      props.append(self._expr())
      if (self.tokens[0][1] == Tokens["Comma"]):
        self._pop()


    self._expect(Tokens["SClose"],"expected ] after array")
    return Nodes["Array"](props)

  def _expr_logic(self):
    left = self._expr_math()
    if (self.tokens[0][0] in ["&","|",]):
      op = self._pop()[0]
      left = Nodes["BinOp"](left,self._expr_math(),op)

    return left

  def _expr_math(self):
    left = self._expr_call()
    
    while (self.tokens[0][0] in ["+","-","*","/","%","<",">","==","!=","in",]):
      op = self._pop()[0]
      left = Nodes["BinOp"](left,self._expr_call(),op)

    return left

  def _expr_call(self):
    def _call(caller):
      e = Nodes["Fcall"](caller,self._args())
      
      while (self.tokens[0][1] == Tokens["POpen"]):
        e = _call(e)

      return e

    left = self._expr_member()
    if (self.tokens[0][1] == Tokens["POpen"]):
      return _call(left)

    return left

  def _expr_member(self):
    left = self._expr_final()
    
    while (((self.tokens[0][1] == Tokens["Dot"]) or (self.tokens[0][1] == Tokens["SOpen"])) or (self.tokens[0][1] == Tokens["Colon"])):
      op = self._pop()
      if (op[1] == Tokens["Dot"]):
        computed = False
        prop = self._expr_final()
        if (prop["t"] != "Word"):
          raise(Exception("parser: expected dot op to be followed by Word"))

      elif (op[1] == Tokens["Colon"]):
        computed = True
        prop = self._expr_final()
        if (prop["t"] == "Word"):
          prop = Nodes["Str"](prop["val"])

      else:
        computed = True
        prop = self._expr()
        self._expect(Tokens["SClose"],"expected ]")

      left = Nodes["Member"](left,prop,computed)

    return left

  def _expr_final(self):
    if (self.tokens[0][1] == Tokens["Word"]):
      return Nodes["Word"](self._pop()[0])
    elif (self.tokens[0][1] == Tokens["Int"]):
      return Nodes["Int"](float(self._pop()[0]))
    elif (self.tokens[0][1] == Tokens["Str"]):
      return Nodes["Str"](self._pop()[0])
    elif (self.tokens[0][1] == Tokens["POpen"]):
      self._pop()
      val = self._expr()
      self._expect(Tokens["PClose"],"expected )")
      return val
    else:
      raise(Exception("parser: unexpected token '{}'".format(self.tokens[0][0])))


  def _stmt_import(self):
    self._pop()
    return Nodes["ImportStmt"](self._expr_arr())

  def _stmt_fn(self):
    isAsync = False
    if (self._pop()[1] == Tokens["Async"]):
      isAsync = True
      self._pop()

    name = self._expect(Tokens["Word"],"expected name after fn")[0]
    params = []
    args = self._args()
    i = 0
    while (i < len(args)):
      if ((args[i]["t"] == "Word") or (args[i]["t"] == "Assign")):
        params.append(args[i])
      else:
        raise(Exception("parser: expected fn params to be Word/Assign"))

      i = (i + 1)
    return Nodes["FnStmt"](name,params,self._block(),isAsync)

  def _stmt_ret(self):
    self._pop()
    return Nodes["RetStmt"](self._expr())

  def _stmt_if(self):
    self._pop()
    cond = self._expr()
    body = self._block()
    alt = []
    if (self.tokens[0][1] == Tokens["Else"]):
      self._pop()
      if (self.tokens[0][1] == Tokens["If"]):
        alt = [self._stmt_if(),]
      else:
        alt = self._block()


    return Nodes["IfStmt"](cond,body,alt)

  def _stmt_for(self):
    self._pop()
    self._expect(Tokens["POpen"],"expected ( after for")
    init = self._expr()
    self._expect(Tokens["Semi"],"expected ; following init")
    cond = self._expr()
    self._expect(Tokens["Semi"],"expected ; following condition")
    after = self._expr()
    self._expect(Tokens["PClose"],"expected ) after for")
    return Nodes["ForStmt"](init,cond,after,self._block())

  def _stmt_foreach(self):
    self._pop()
    return Nodes["ForeachStmt"](self._expr(),self._block())

  def _stmt_while(self):
    self._pop()
    return Nodes["WhileStmt"](self._expr(),self._block())

  def _stmt_class(self):
    self._pop()
    name = self._expect(Tokens["Word"],"expected Word after class")[0]
    inherits = ""
    if (self.tokens[0][1] == Tokens["Colon"]):
      self._pop()
      inherits = self._expr()

    return Nodes["ClassStmt"](name,inherits,self._block())

  def _stmt_trycatch(self):
    self._pop()
    body = self._block()
    self._expect(Tokens["Catch"],"expected catch after try")
    asVar = [self._expr_member(),self._expect(Tokens["Word"],"expected var name after catch")[0],]
    alt = self._block()
    return Nodes["TryCatch"](body,alt,asVar)

  def __arglist(self):
    def parse():
      left = self._expr()
      if (self.tokens[0][1] == Tokens["Equals"]):
        self._pop()
        return Nodes["Assign"](left,parse())

      return left

    args = [parse(),]
    
    while ((self.tokens[0][1] == Tokens["Comma"]) and self._pop()):
      args.append(parse())

    return args

  def _args(self):
    self._expect(Tokens["POpen"],"expected ( in args")
    args = []
    if (self.tokens[0][1] != Tokens["PClose"]):
      args = self.__arglist()

    self._expect(Tokens["PClose"],"expected ) in args")
    return args

  def _block(self):
    self._expect(Tokens["BOpen"],"expected { in block")
    body = []
    
    while ((self.tokens[0][1] != Tokens["EOF"]) and (self.tokens[0][1] != Tokens["BClose"])):
      body.append(self._stmt())

    self._expect(Tokens["BClose"],"expected } in block")
    return body


