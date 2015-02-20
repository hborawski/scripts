#!/usr/bin/env python3

import requests
import sched
import time

def vote(s):
    r = requests.post("http://www.rit.edu/imagine/posters/2015/", data={'posterpick1':'2015-30', 'submitlayout':'Submit'})
    print(r.status_code)
    s.enter(3600, 1, vote, (s,))

def main():
    s = sched.scheduler(time.time, time.sleep)
    s.enter(0, 1, vote, (s,))
    s.run()


if __name__ == '__main__':
    main()
