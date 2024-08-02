# coastc
a little language that compiles into python (WIP)

## features:
- **syntax**: lightly inspired from javascript, allows objects, floats, strings...
- **blocks**: uses {}-style blocks, allowing better flexibility and readability
- **inline**: allows you to insert inline python using `__inline("")`

*... and more!*

## example:
```
import "os"
fn greet(name) {
  print("hello, {}!".format(name))
}

greet(os.getlogin())
```


## getting started:
```sh
git clone https://github.com/woofledev/coastc.git
cd coastc
python bootstrap/coastc.py .examples/hello.co hello.py
python hello.py

# you can (optionally) build the language from its own source using:
sh build.sh
```

**PLEASE NOTE:** this language is very much in it's early stages of development. core features are implemented, but there's still a LOT that needs to be done.