Spleef Challenge Manual Bot
===========================

This acts as a bot with the [Spleef Challenge](https://spleefchallenge.com/) judge but has a gui for you to control. This can be used for easy testing of bots by having them face off against you instead of a random AI. This requires having [Kivy](http://kivy.org/) installed (along with Python).

All you have to do is include this bot as if it were a regular bot (and increase the setup time and time per turn). E.g:

```python
python judge.py --time 60000 --setup 60000 "python -u ManualBot.py" "python -u Python2Starter/MyBot.py"
```