Hst (the Picker)
==========================

HST is history search & picker in ncurses - also can pick other things

[![asciicast](https://asciinema.org/a/7aek3tjh816g22k7489vats07.png)](https://asciinema.org/a/7aek3tjh816g22k7489vats07)

Though it can search and pick other things as well. Such as git branch | git checkout

[![asciicast](https://asciinema.org/a/86zjkikdsjcrvvh5i60yt7up4.png)](https://asciinema.org/a/86zjkikdsjcrvvh5i60yt7up4)

You can also use it in multi select mode. Useful for select & copying some files etc. 

[![asciicast](https://asciinema.org/a/96ngad9i84m9ox7pwduhfh4sr.png)](https://asciinema.org/a/96ngad9i84m9ox7pwduhfh4sr)

Install
------------------------

Mac Os X:

```
sudo pip install hst
```

Linux:

```
sudo pip install hst
```

Virtualenv

```
pip install hst
```


Usage
------------------------

hst will grab your history by default.

```
hst
```

if you select something and press enter it will execute that command. If you press F6 it will open the command in editor ($EDITOR), any other key will be used to filter/search the results. hst will make your history lines unique and will favor the most used in search.

for example if you are using git commit 100 times a day and git push only once, when you type git, git commit will be in the first place.

you can also open a file in hst as an input, say you have a list of hosts
and select one and ping

```
hst -i hosts.txt -e "ping"
```

you can also pipe in some input and wrap it with something.

```
git branch | hst -e "git checkout"
```

you can give a separator, for example, copy some python file, {} will be replaced with file.

```
find . -name '*.py' | hst -e 'cp {} /tmp/'
```

Contribute
------------------------

All contributions are welcomed.

When you clone the repo, to check your changes and try, you can do this. Please don't send pull requests without testing.

```
git clone git://repoaddress/hst
cd hst
virtualenv env && source env/bin/activate
python setup.py develop
ln -s `which hst` /usr/local/bin/hst
```

now you can use your development version of hst in other terminal tabs etc.

please note that hst uses a single thread, and you shouldn't lock it for a long time, so if you do something like enhancing search results etc. you need to test it with a big file. some people's history is over 40k lines - eg. me.

License
------------------------
Its MIT license.

Why
------------------------

Because i live in the terminal, and hate trying to type something i've already typed. I've tried many things in the past and none of them worked well for me.

- cmd+R im never used to it (YMMV). it doesnt show what i am about select, just one line. most of the times, when i search for ssh, i want to see the most used ssh ones not the last ones. to find what i ssh'd i almost type all of the command. in hst i can just type ssh and see them - most used on the top.

- even if i could use cmd+R, it doesn't work for say git branches, or cd. hst is handy, you can pipe in any output.

- others: couldn't find a similar project

Similar & Notable Projects
------------------------

- https://github.com/facebook/PathPicker you pipe in a bunch of paths and it shows in a nice ui.

- https://github.com/dvorka/hstr its a nice project but its search wants you to remember the commands eg: you cant type in "ss app1" for "ssh ubuntu@app1.somefunkyprojects.example.com"
or for to find "cordova run ios" you cant type in "cord ios" you have to type in "cordova run"

- https://github.com/thoughtbot/pick it works great, but doesnt favor most used commands - well not designed to work with history - though you can just pipe in history eg: something like history | cut -c 8- | sort | uniq | pick but i really can't type in ssh app1 and try to find the command, but ymmv

- https://github.com/junegunn/fzf again nice picker that you can pipe in history with history | cut -c 8- | sort | uniq | fzf but doesn't favor most used commands, and i get lost while searching a command in my long history of commands. but its a nice generic tool for other purposes.

- https://github.com/mooz/percol generic fuzzy selector, you can use it to hack your history i think.

- https://github.com/peco/peco its one of the best tools that can work with history. use something like

$(history | cut -c 8- | sort | uniq | peco)

and it nearly works like hst. fzf doesn't find "ssh ubuntu@app1.someproject...." when i type in "ssh app1 ubuntu" finds some curl commands, but peco does a good job on finding. only you have to type in a few more things in peco since it doesn't favor the most used commands.

- https://github.com/garybernhardt/selecta

anyways, ymmv with other tools.

Missing Features - TODO's
------------------------
- need some viewport kind of logic, say you hit pagedown, it should scroll down.
- ~~ piping out the selected line doesn't work ~~
- can't do fuzzy match eg: "cord" works for "cordova" but not "crd". it takes too long on long list of lines.
- ~~ multiple selection ~~
- pipe in with scores, eg. boost current branch when piping git branch etc.

How
------------------------
uses Python and Curses library

Disclaimer
------------------------
Its as is, if your hard disk is wiped out because of hst, i'm not responsible.

