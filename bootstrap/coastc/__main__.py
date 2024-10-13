import lparse,py_codegen,glob,os
import sys,argparse


CO_GLOB = "src/**/*.co"
OUT_DIR = "dist/{}/"
STD_FEATURES = {"bools": "true, false, null = True, False, None","exargs": "def exargs(f): return (lambda *a, **kw: f(list(a), kw))","using": "def using(res, cb):\n  with res: cb(res)",}
def parse_str(s):
  parser = lparse.Parser()
  cg = py_codegen.Codegen()
  return cg.run(parser.parse(s))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("file",nargs = "?",help = "file to compile")
  parser.add_argument("-v","--verbose",action = "store_true",help = "enable verbose logging")
  def verbose(s):
    if args.verbose:
      print(s)


  args = parser.parse_args()
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
    if ("out_dir" in proj_var):
      OUT_DIR = proj_var["out_dir"]

    os.makedirs(OUT_DIR.format(proj_var["name"]),exist_ok = True)
    
    for src in files:
      dest = (OUT_DIR.format(proj_var["name"]) + src[slice(4,None)])
      dest = (dest[slice((0 - 2))] + "py")
      verbose("{} -> {}".format(src,dest))
      os.makedirs(os.path.dirname(dest),exist_ok = True)
      inf = open(src,"r")
      source = inf.read()
      inf.close()
      outf = open(dest,"w")
      outf.write((preludes + parse_str(source)))
      outf.close()

    if ("postprocess" in proj_var):
      verbose("calling postprocess()")
      proj_var["postprocess"]()



if (__name__ == "__main__"):
  main()

