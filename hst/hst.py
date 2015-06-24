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

index = Index()

logger = logging.getLogger(__name__)

def print_line(line, highlight=False):
    """A thin wrapper around curses's addstr()."""
    global lineno
    try:
        if highlight:
            line += " " * (win.getmaxyx()[1] - len(line))
            win.addstr(lineno, 0, line, curses.color_pair(1))
        else:
            win.addstr(lineno, 0, line, 0)
    except curses.error:
        lineno = 0
        win.refresh()
        raise
    else:
        lineno += 1

def print_header(title):
    print_line("> %s" % title)


def print_footer(s):
    y, x = win.getmaxyx()
    win.addstr(y-1, 0, s.ljust(x), curses.color_pair(1))

last_search_text = ''
last_lines = []

def get_max_viewport():
    max_y, max_x = win.getmaxyx()
    return (max_y - 3, max_x)

def which_lines(txt):
    global last_search_text, last_lines
    if not txt:
        max_y, max_x = get_max_viewport()
        return [(0, n) for n in last_lines[0:max_y]]
    if last_search_text == txt:
        return last_lines
    last_search_text = txt
    import time
    t1 = time.time()
    ret = index.find(txt)

    logger.debug(">>> %s", time.time() - t1)

    t1 = time.time()
    ret = sorted(ret, key=itemgetter(0), reverse=True)
    logger.debug(">>> sort >>> %s", time.time() - t1)
    last_lines = ret
    return ret

def refresh_window(pressed_key=None):
    global search_txt, lineno, mode, do_debug
    lineno = 0
    if pressed_key:
        search_txt += pressed_key

    # curses.endwin()
    win.erase()

    print_header(search_txt)

    lines = which_lines(search_txt)

    if not lines:
        print_line("Results [%s]" % index.size(), highlight=True)
        return
    else:
        print_line("Results - [%s]" % len(lines), highlight=True)

    max_y, max_x = get_max_viewport()
    for i, p in enumerate(lines[0:max_y]):
        selected = selected_lineno == i
        try:
            if do_debug:
                line = "> (%s) %s" % p
            else:
                line = "> %s" % p[1]
        except:
            logger.exception("exception in adding line %s", p)
        else:
            try:
                print_line(line, highlight=selected)
            except curses.error:
                break
    try:

        if mode == 'SEARCH':
            s = 'type something to search | [ESC] to select'
        elif mode == 'SELECT':
            s = 'use arrows to select | [ESC] to search | [c] copy | [e] edit | [ENTER] run | [q] quit'

        print_footer("[%s] %s" % (mode, s))
    except curses.error:
        pass
    win.refresh()

lines = []
def load_history():
    global lines
    from subprocess import Popen, PIPE, STDOUT
    shell_command = 'bash -i -c "history -r; history"'
    event = Popen(shell_command, shell=True, stdin=PIPE, stdout=PIPE, 
        stderr=STDOUT)

    output = event.communicate()
    lines = output[0].split('\n')
    for line in lines:
        try:
            l = ' '.join(line.split(' ')[1:])
            l = unicode(l, encoding='utf8')
            index.add(l)
        except:
            print ">>>", line
            raise

def load_file(filename='history.txt'):
    global lines
    f = open(filename)
    lines = f.readlines()

    for line in lines:
        try:
            l = ' '.join(line.split(' ')[1:])
            l = unicode(l, encoding='utf8')
            index.add(l)
        except:
            print ">>>", line
            raise

def load_lines(lines):
    for line in lines:
        try:
            l = ' '.join(line.split(' ')[1:])
            l = unicode(l, encoding='utf8')
            index.add(l)
        except:
            print ">>>", line
            raise


def shorter_esc_delay():
    try:
        os.environ['ESCDELAY']
    except KeyError:
        os.environ['ESCDELAY'] = '25'

shorter_esc_delay()

lineno = 0
selected_lineno = 0
search_txt = ''
mode = 'SEARCH'
do_print = False
do_debug = False


class Picker(object):
    def __init__(self, loader):
        self.loader = loader
        self.lines = []

    def load_lines(self):
        self.lines = []



def main():
    global selected_lineno, search_txt, win, last_lines, mode, do_print, do_debug

    if args.debug:
        do_debug = True

    if not sys.stdin.isatty():
        while True:
            stdin_line = sys.stdin.readline()
            index.add(stdin_line)
            if not stdin_line:
                break
    else:
        if args.input:
            load_file(args.input)
        else:
            load_history()
    f=open("/dev/tty")
    os.dup2(f.fileno(), 0)

    win = curses.initscr()
    curses.start_color()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    win.timeout(-1)
    win.keypad(1)
    # curses.endwin()

    max_y, max_x = get_max_viewport()

    last_lines = index.last_lines[0:max_y]
    logger.debug("lastlines %s", last_lines)

    try:
        logger.debug("colors: %s", curses.COLORS)
        refresh_window("")

        while True:
            char = win.getch()
            max_y, max_x = get_max_viewport()

            if mode == 'SEARCH':
                if char in (27, curses.KEY_UP, curses.KEY_DOWN, 
                                curses.KEY_PPAGE, curses.KEY_NPAGE):
                    mode = 'SELECT'
                    refresh_window()
                elif char == curses.KEY_ENTER or char==10 or char==13: # linefeed, enter carriage return all same imho
                    mode = 'SEARCH'
                    refresh_window()
                elif char == 127:
                    if search_txt:
                        search_txt = search_txt[0:-1]
                    refresh_window()
                else:
                    try:
                        refresh_window(chr(char))
                    except ValueError:
                        print ">>> couldnt encode", char

            elif mode == 'SELECT':
                if char == 27:
                    mode = 'SEARCH'
                    refresh_window()
                elif char == curses.KEY_ENTER or char==10 or char==13: # linefeed, enter carriage return all same imho
                    line = last_lines[selected_lineno][1]
                    f = open(args.out, 'w')
                    f.write(line)
                    f.close()
                    break
                elif char == ord('e'):
                    mode = 'SEARCH'
                    refresh_window()
                elif char == ord('q'):
                    break
                elif char == ord('s'):
                    do_print = True
                    break
                elif char == ord('c'):
                    logger.info("selected - %s %s",  selected_lineno, last_lines[selected_lineno])
                    pyperclip.copy(last_lines[selected_lineno][1])
                    break
                elif char == curses.KEY_ENTER or char==10 or char==13: # linefeed, enter carriage return all same imho
                    pass
                elif char == 127:
                    if search_txt:
                        search_txt = search_txt[0:-1]
                    refresh_window()
                elif char == curses.KEY_UP:
                    if selected_lineno >= 1:
                        selected_lineno -= 1
                    refresh_window()
                elif char == curses.KEY_DOWN:
                    if selected_lineno < max_y - 1:
                        selected_lineno += 1
                    refresh_window()
                elif char == curses.KEY_PPAGE:
                    if selected_lineno - 10 >= 0:
                        selected_lineno -= 10
                    refresh_window()
                elif char == curses.KEY_NPAGE:
                    if selected_lineno + 10 <= max_y:
                        selected_lineno += 10
                    refresh_window()
            else:
                break
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        win.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        if do_print:
            print last_lines[selected_lineno][1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--out", type=str,
                    help="output to file")
    parser.add_argument("-d", "--debug",
                    help="debug mode - shows scores etc.")
    parser.add_argument("-i", "--input",
                    help="input file")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        hdlr = logging.FileHandler('hst.log')
        logger.addHandler(hdlr)
    else:
        logger.setLevel(logging.CRITICAL)
    main()