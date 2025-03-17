import lparse,py_codegen,glob,os
import sys,argparse
def __lambda_1(node,c):
  c.out = (c.out + "*")
  c.run(node["args"][0])
def __lambda_2(node,c):
  c.out = (c.out + "**")
  c.run(node["args"][0])


CO_GLOB = "src/**/*.co"
STD_FEATURES = {"bools": "true, false, null = True, False, None","using": "def using(res, cb):\n  with res: return cb(res)","exargs": "def exargs(f): return (lambda *a, **kw: f(list(a), kw))","unstruct": "def unstruct(ns, *args): return [ns[i] for i in args]","unpack": "",}
FEAT_UNPACK = {"unpack": __lambda_1,"unpack_kv": __lambda_2,}
def parse_str(s,custom = {}):
  parser = lparse.Parser()
  cg = py_codegen.Codegen()
  cg.custom_fn.update(custom)
  return cg.run(parser.parse(s))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("file",nargs = "?",help = "file to compile")
  parser.add_argument("-v","--verbose",action = "store_true",help = "enable verbose logging")
  def verbose(s):
    if args.verbose:
      print(s)


  args = parser.parse_args()
  try:
    if args.file:
      f = open(args.file,"r")
      code = f.read()
      f.close()
      print(parse_str(code),end = "")
    else:
      f = open("./project.co","r")
      proj_code = f.read()
      f.close()
      verbose("running project file...")
      proj_code = parse_str(proj_code)
      proj_var = {}
      exec(proj_code,{},proj_var)
      verbose("project file vars: {}".format(proj_var))
      preludes = ""
      
      for k in proj_var.get("std_features",[]):
        preludes = ((preludes + STD_FEATURES[k]) + "\n")

      files = glob.glob(CO_GLOB,recursive = True)
      verbose("globbed {} files from {}".format(len(files),CO_GLOB))
      OUT_DIR = "dist/{}/"
      if ("out_dir" in proj_var):
        OUT_DIR = proj_var["out_dir"]

      os.makedirs(OUT_DIR.format(proj_var["name"]),exist_ok = True)
      CUST_FEATURES = {}
      if ("unpack" in proj_var.get("std_features",[])):
        CUST_FEATURES.update(FEAT_UNPACK)

      
      for src in files:
        try:
          dest = (OUT_DIR.format(proj_var["name"]) + src[slice(4,None)])
          dest = (dest[slice((0 - 2))] + "py")
          verbose("{} -> {}".format(src,dest))
          os.makedirs(os.path.dirname(dest),exist_ok = True)
          inf = open(src,"r")
          source = inf.read()
          inf.close()
          outf = open(dest,"w")
          outf.write((preludes + parse_str(source,CUST_FEATURES)))
          outf.close()
        except Exception as e:
          if str(e).startswith("parser:"):
            [_,pos,msg,] = str(e).split(":")
            pos = (source[slice(0,int(pos))].count("\n") + 1)
            print("Error: {} ln {}: {}".format(src,pos,msg))
          else:
            print("Error: {}".format(str(e)))

          sys.exit(1)


      if ("postprocess" in proj_var):
        verbose("calling postprocess()")
        proj_var["postprocess"]()


  except Exception as e:
    print("error: {}".format(e))
    sys.exit(1)


if (__name__ == "__main__"):
  main()

