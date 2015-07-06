#!/usr/bin/env python

import os
import sys
if os.name != 'posix':
    sys.exit('platform not supported')
import curses
from operator import itemgetter
from indexer import Index
import logging
import os
import sys
import pyperclip
import argparse

logger = logging.getLogger(__name__)

class Loader(object):
    def load(self):
        raise "Override me please"

class HistoryLoader(Loader):
    def load(self):
        from subprocess import Popen, PIPE, STDOUT
        shell_command = 'bash -i -c "history -r; history"'
        event = Popen(shell_command, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=STDOUT)

        output = event.communicate()
        lines = output[0].split('\n')
        ret = []
        for line in lines:
            try:
                l = ' '.join(line.split(' ')[1:])
                l = unicode(l, encoding='utf8')
                ret.append(l)
            except:
                print ">>>", line
                raise
        return ret

class FileLoader(Loader):
    def __init__(self, filename='history.txt'):
        self.filename = filename

    def load(self):
        f = open(self.filename)
        lines = f.readlines()
        ret = []
        for line in lines:
            try:
                l = ' '.join(line.split(' ')[1:])
                l = unicode(l, encoding='utf8')
                ret.append(l)
            except:
                print ">>>", line
                raise
        return ret

class LineLoader(object):
    def __init__(self, lines):
        self.lines = lines

    def load(self):
        ret = []
        for line in self.lines:
            try:
                l = ' '.join(line.split(' ')[1:])
                l = unicode(l, encoding='utf8')
                ret.append(l)
            except:
                print ">>>", line
                raise
        return ret


def shorter_esc_delay():
    try:
        os.environ['ESCDELAY']
    except KeyError:
        os.environ['ESCDELAY'] = '25'

class Picker(object):
    def __init__(self, loader=None):
        self.loader = loader
        self.lines = []
        self.lineno = 0
        self.selected_lineno = 0
        self.search_txt = ''
        self.mode = 'SEARCH'
        self.do_print = False
        self.do_debug = False
        self.last_lines = []
        self.win = None
        self.last_search_text = ''
        self.last_lines = []
        self.index = None

        self.keys = {
            10: self.key_ENTER,
            13: self.key_ENTER,
            curses.KEY_ENTER: self.key_ENTER,
            curses.KEY_F2: self.key_F2,
            127: self.key_BACKSPACE,
            curses.KEY_F5: self.key_F5,
            #
            curses.KEY_UP: self.key_UP,
            curses.KEY_DOWN: self.key_DOWN,
            curses.KEY_PPAGE: self.key_PPAGE,
            curses.KEY_NPAGE: self.key_NPAGE,
            27: self.key_ESC
        }

    def load_lines(self):
        self.lines = self.loader.load()
        for n in self.lines:
            self.index.add(n)

    def get_max_viewport(self):
        max_y, max_x = self.win.getmaxyx()
        return (max_y - 3, max_x)

    def print_line(self, line, highlight=False):
        """A thin wrapper around curses's addstr()."""
        try:
            if highlight:
                line += " " * (self.win.getmaxyx()[1] - len(line))
                self.win.addstr(self.lineno, 0, line, curses.color_pair(1))
            else:
                self.win.addstr(self.lineno, 0, line, 0)
        except curses.error:
            self.lineno = 0
            self.win.refresh()
            raise
        else:
            self.lineno += 1

    def print_header(self, title):
        self.print_line("> %s" % title)

    def print_footer(self, s):
        y, x = self.win.getmaxyx()
        self.win.addstr(y-1, 0, s.ljust(x), curses.color_pair(1))

    def which_lines(self, txt):
        if not txt:
            max_y, max_x = self.get_max_viewport()
            return [(0, n) for n in self.last_lines[0:max_y]]
        if self.last_search_text == txt:
            return self.last_lines
        self.last_search_text = txt
        import time
        t1 = time.time()
        ret = self.index.find(txt)

        logger.debug(">>> %s", time.time() - t1)

        t1 = time.time()
        ret = sorted(ret, key=itemgetter(0), reverse=True)
        logger.debug(">>> sort >>> %s", time.time() - t1)
        self.last_lines = ret
        return ret

    def refresh_window(self, pressed_key=None):
        self.lineno = 0
        if pressed_key:
            self.search_txt += pressed_key

        # curses.endwin()
        self.win.erase()

        self.print_header(self.search_txt)

        lines = self.which_lines(self.search_txt)

        if not lines:
            self.print_line("Results [%s]" % self.index.size(), highlight=True)
            return
        else:
            self.print_line("Results - [%s]" % len(lines), highlight=True)

        max_y, max_x = self.get_max_viewport()
        for i, p in enumerate(lines[0:max_y]):
            selected = self.selected_lineno == i
            try:
                if self.do_debug:
                    line = "> (%s) %s" % p
                else:
                    line = "> %s" % p[1]
            except:
                logger.exception("exception in adding line %s", p)
            else:
                try:
                    self.print_line(line, highlight=selected)
                except curses.error:
                    break
        try:
            s = 'type something to search | [F5] copy | [F6] edit | [ENTER] run | [ESC] quit'
            self.print_footer("[%s] %s" % (self.mode, s))
        except curses.error:
            pass
        self.win.refresh()

    def key_ENTER(self):
        line = self.last_lines[self.selected_lineno][1]
        if args.eval:
            if args.separator in args.eval:
                line = args.eval.replace(args.separator, line)
            else:
                line = "%s %s" % (args.eval, line)
        f = open(args.out, 'w')
        f.write(line)
        f.close()
        raise QuitException()

    def key_F2(self):
        self.do_print = True
        raise QuitException()

    def key_BACKSPACE(self):
        if self.search_txt:
            self.search_txt = self.search_txt[0:-1]
        self.refresh_window()

    def key_F5(self):
        logger.info("selected - %s %s",  self.selected_lineno, self.last_lines[self.selected_lineno])
        pyperclip.copy(self.last_lines[self.selected_lineno][1])
        raise QuitException()

    def key_UP(self):
        if self.selected_lineno >= 1:
            self.selected_lineno -= 1
        self.refresh_window()

    def key_DOWN(self):
        max_y, max_x = self.get_max_viewport()

        if self.selected_lineno < max_y - 1:
            self.selected_lineno += 1
        self.refresh_window()

    def key_PPAGE(self):
        if self.selected_lineno - 10 >= 0:
            self.selected_lineno -= 10
        self.refresh_window()

    def key_NPAGE(self):
        max_y, max_x = self.get_max_viewport()

        if self.selected_lineno + 10 <= max_y:
            self.selected_lineno += 10
        self.refresh_window()

    def key_ESC(self):
        raise QuitException

    def key_pressed(self, char):
        """
        this is our main dispatcher
        """
        if char in self.keys:
            self.keys[char]()
        else:
            try:
                self.refresh_window(chr(char))
            except ValueError:
                logger.exception("couldnt encode %s", char)

class QuitException(Exception):
    pass

def main():
    shorter_esc_delay()
    index = Index()

    picker = Picker()
    picker.index = index

    if args.debug:
        picker.do_debug = True

    if not sys.stdin.isatty():
        while True:
            stdin_line = sys.stdin.readline()
            picker.index.add(stdin_line)
            if not stdin_line:
                break
    else:
        if args.input:
            file_loader = FileLoader(args.input)
            picker.loader = file_loader
            picker.load_lines()
        else:
            history_loader = HistoryLoader()
            picker.loader = history_loader
            picker.load_lines()

    f = open("/dev/tty")
    os.dup2(f.fileno(), 0)

    picker.win = curses.initscr()
    curses.start_color()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    picker.win.timeout(-1)
    picker.win.keypad(1)

    max_y, max_x = picker.get_max_viewport()

    picker.last_lines = picker.index.last_lines[0:max_y]
    logger.debug("lastlines %s", picker.last_lines)

    try:
        picker.refresh_window("")

        while True:
            char = picker.win.getch()
            picker.key_pressed(char)
    except (KeyboardInterrupt, SystemExit, QuitException):
        pass
    finally:
        picker.win.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        if picker.do_print:
            print picker.last_lines[picker.selected_lineno][1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--out", type=str,
                    help="output to file")
    parser.add_argument("-d", "--debug",
                    help="debug mode - shows scores etc.")
    parser.add_argument("-i", "--input",
                    help="input file")
    parser.add_argument("-e", "--eval",
                    help="evaluate command output")
    parser.add_argument("-I", "--separator",
                        default='{}',
                        help="seperator in eval")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        hdlr = logging.FileHandler('hst.log')
        logger.addHandler(hdlr)
    else:
        logger.setLevel(logging.CRITICAL)
    main()