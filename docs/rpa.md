## Existing robotic process automation (RPA) tools

### Low-code block diagram RPA
- [BluePrism](https://www.youtube.com/watch?v=IcCLpzt7cLQ)
- [OpenRPA](https://github.com/open-rpa/openrpa)
- [`Automagica`](https://github.com/automagica/automagica)
- [UiBot](https://store.uibot.com.cn/robotscase)
- [Is-RPA](https://www.i-search.com.cn/industry-case/all/)
- [WinRobot360](https://www.winrobot360.com/)

### APIs/language-based RPA
- [`Tasket`](https://github.com/saucepleez/taskt)
- [RobotFramework](https://github.com/robotframework/robotframework)
- [TagUI](https://github.com/kelaberetiv/TagUI)
- [`Anjian`](http://www.anjian.com/)
- AutoHotKey. DSL is hard to learn (at least for me)
- PyAutoGUI. Cannot support background mouse/click

### Problems
- Expensive, close-sourced
- Low-code but cumbersome: Need `CodeGen` from recorded actions
- Not extensible: e.g., how to integrate a third-party ML model
- Cross-device/user interaction
- Messy abstraction: they try to cover everything,e.g., PDF watermark, encryption/decryption

### Improvement
- [Emulate mouse & keyboard in background](https://zhuanlan.zhihu.com/p/363186784)
- Generate code from 