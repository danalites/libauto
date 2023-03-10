### Some examples
- [HeartStone open packs](https://github.com/ftdlyc/gaming_helper/blob/master/hs_auto_open_packs.py)

- [auto-game-player](https://github.com/anywheretogo/auto_player). it provides the same functionality as the `screen` operations; namely, it locates the image on the screen and click.

- [Minimal OpenCV based `Genshin` auto-fishing tool](https://github.com/ArsenicBismuth/Genshin-Fishing-Bot/blob/main/main.py). completely image based solution without any learning model involved. About resolution adoption - [ref](https://github.com/Nigh/Genshin-fishing/issues/9)

- DRL in games: [`Genshin` auto-fishing scripts]() using DQN, [a 3D strategy planning game using DRL](https://github.com/ArztSamuel/DRL_DeliveryDuel), [RL Card](https://github.com/datamllab/rlcard) playing card game using RL

### Thoughts
- **Simple repeating actions** are easy to handle. We just need to consider some scaling and offset issues; the bot just needs to replay the recorded actions.

- **RL for strategy games**. the abstraction of RL is pretty much given; the only thing left is to define the actions as well as the environment (i.e., what is observable from the env. maybe how to encode the current env information, and let RL agent make decisions)


