## ISA
- `Aba` defines an programming abstraction for procedure automation
- `Aba` ISA is not general-purpose or Turing-complete; it is only designed for procedure automation and information gathering & sharing

### Window ops
- `window.active("App")`: get foreground window
- `window.find(text|image)`: locate text/image and returns location vector

### System ops
- `os.shell()`: run shell scripts (`powershell` or `applescript`)
- `os.notify()`: send notification to any device associated with ur account

### Web ops
- `web.init()`: initialize web session
- `web.open()`: open an link
- `web.find()`: find an element on webpage with CSS or XPATH
- `web.click|type|select|get()`: action on a web element 

### Data ops
- `data.read()` load data from local database or JSON
- `data.parse()`: fuzzy parsing or regex exact matching


### Visualization 
### Compare with other tools
- [uTools](https://u.tools/docs/guide/about-uTools.html): web-based plugin based on Electron. (C1) high-code. Users have to be familiar with JS/HTML. (C2) cannot control desktop for cross-device

- Quicker: windows-based PC automation tool (primitives are disaggregated). It is low-code but learning curve is high. It cannot support some [complex operations that Im interested in](https://zhuanlan.zhihu.com/p/357089651)

- KitX: cross-platform natively rendered app that supports plugin in all languages. It can support cross-platform communication. KitX is based on [`Avalonia`](https://github.com/AvaloniaUI/Avalonia) a cross-platform UI framework that can be shipped to mobile devices.