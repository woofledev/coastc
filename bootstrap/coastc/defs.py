def __lambda_1(body):
  return {"t": "Main","body": body,}
def __lambda_2(key,val):
  return {"t": "Assign","key": key,"val": val,}
def __lambda_3(mod):
  return {"t": "ImportStmt","mod": mod,}
def __lambda_4(name,args,body,isAsync):
  return {"t": "FnStmt","name": name,"args": args,"body": body,"isAsync": isAsync,}
def __lambda_5(expr):
  return {"t": "RetStmt","expr": expr,}
def __lambda_6(expr,body,alt):
  return {"t": "IfStmt","expr": expr,"body": body,"alt": alt,}
def __lambda_7(init,expr,after,body):
  return {"t": "ForStmt","init": init,"expr": expr,"after": after,"body": body,}
def __lambda_8(expr,body):
  return {"t": "ForeachStmt","expr": expr,"body": body,}
def __lambda_9(expr,body):
  return {"t": "WhileStmt","expr": expr,"body": body,}
def __lambda_10(name,inherits,body):
  return {"t": "ClassStmt","name": name,"inherits": inherits,"body": body,}
def __lambda_11(body,alt,asVar):
  return {"t": "TryCatch","body": body,"alt": alt,"asVar": asVar,}
def __lambda_12(caller,args):
  return {"t": "Fcall","caller": caller,"args": args,}
def __lambda_13(l,r,op):
  return {"t": "BinOp","l": l,"r": r,"op": op,}
def __lambda_14(val):
  return {"t": "Word","val": val,}
def __lambda_15(val):
  return {"t": "Int","val": val,}
def __lambda_16(val):
  return {"t": "Str","val": val,}
def __lambda_17(args,body):
  return {"t": "Lambda","args": args,"body": body,}
def __lambda_18(props):
  return {"t": "Array","props": props,}
def __lambda_19(k,v):
  return {"t": "Prop","k": k,"v": v,}
def __lambda_20(props):
  return {"t": "Object","props": props,}
def __lambda_21(obj,prop,computed):
  return {"t": "Member","obj": obj,"prop": prop,"computed": computed,}
Tokens = {"Int": 0,"Str": 1,"Word": 2,"BinOp": 3,"Equals": 4,"Dot": 5,"Comma": 6,"Colon": 7,"Semi": 8,"POpen": 9,"PClose": 10,"BOpen": 11,"BClose": 12,"SOpen": 13,"SClose": 14,"EIf": 15,"NEIf": 16,"Smaller": 17,"Bigger": 18,"And": 19,"Or": 20,"Import": 21,"Fn": 22,"Ret": 23,"If": 24,"Else": 25,"For": 26,"While": 27,"Class": 28,"Async": 29,"Try": 30,"Catch": 31,"Foreach": 32,"EOF": 33,}
Nodes = {"Main": __lambda_1,"Assign": __lambda_2,"ImportStmt": __lambda_3,"FnStmt": __lambda_4,"RetStmt": __lambda_5,"IfStmt": __lambda_6,"ForStmt": __lambda_7,"ForeachStmt": __lambda_8,"WhileStmt": __lambda_9,"ClassStmt": __lambda_10,"TryCatch": __lambda_11,"Fcall": __lambda_12,"BinOp": __lambda_13,"Word": __lambda_14,"Int": __lambda_15,"Str": __lambda_16,"Lambda": __lambda_17,"Array": __lambda_18,"Prop": __lambda_19,"Object": __lambda_20,"Member": __lambda_21,}
