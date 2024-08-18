import lparse, py_codegen, sys

parser = lparse.Parser()
cg = py_codegen.Codegen()
def main():
  if (len(sys.argv) < 3):
    print("usage: {} <input.co> <output.py>".format(sys.argv[0]))
    sys.exit(0)

  in_file = sys.argv[1]
  out_file = sys.argv[2]
  in_f = open(in_file,"r")
  content = in_f.read()
  in_f.close()
  ast = parser.parse(content)
  generated = cg.run(ast)
  out_f = open(out_file,"w")
  out_f.write(generated)
  out_f.close()

if (__name__ == "__main__"):
  main()

