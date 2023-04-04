# usefulsearch
A Sublime Text 3 Plugin for useful (but not yet seen elsewhere) search features and shortlisting of buffer content

No time to complete this just yet. Will get back and have it done as soon as i can.

Let's see some typical examples first:

1.	to find all the lines in the "buffer" (a typical text editor jargon) which contains "one" and "def" (see note) and show them on a quick panel in a shortlisted manner, you can enter like:

	`one def//` or `def one//`

	where the "syntax" of this example depends on a space in between and the double slashes at the end.

	note: the sequential order of occurrences of these two substrings (jargon) on the line doesn't matter.

	A possible result may show like:

	```
	2 <<< def
	2 <<< one
	 21: def run(self, text=None):
	 51: def on_done(self, text):
	```

	You may use the up-arrow or down-arrow keyboard keys to highlight a line (or by rightclick it) on the quick panel, which will scroll that line into view (jargon)

2.	likewise, for lines which contains "def" yet does not contain "one", you can enter like:

	`def -one//` or `-one def//`

	A possible result may show like:

	```
	13 <<< def
	 65: # No extra space by default
	113: def on_cancel(self):
	116: def prompt_timeout(self, view):
	120: def pf(self, a, n, i=0, c=""):
	128: def do_transformation(self, text, option=""):
	129: # Case insensitive by default
	135: # Maintain chronological order for assortment by default
	189: def get_matched_lines(self, text):
	194: timeout = time.time() + MyPanelCommand.maxtol	# default to 5 seconds from now
	202: if n > 99:	# definition of "too many"
	254: def pick(self, index, items, text):
	264: def mpick(self, index, results, text):
	315: def on_highlight(self, index, results):
	```

3.	a simple shorthand search example goes like:

	`tef` (as long as "tef" does not exist anywhere in the "buffer", shorthand search will be attempted automatically)
	
	A possible result may show like:
	
	```
	5 <<< tself
	1 <<< to enable further
	1 <<< This exists for
	 17: tmbtp_itself = False	# tmbtp stands for "this might be the pattern"
	 29: # As this probably comes from the history list, show it on input_panel to enable further adjustment
	 86: # print(MyPanelCommand.tmbtp_itself)#debug
	 88: if len(results) > 0 and not MyPanelCommand.tmbtp_itself:
	185: sublime.set_clipboard(text)	# This exists for the user convenience as s/he may want to use the pattern to find the "needle" by other means, for instance, by ctrl+f
	245: MyPanelCommand.tmbtp_itself = (len(regions) == 1 and regions[0].begin() in range(view.sel()[0].begin(), view.sel()[0].end()))MyPanelCommand.tmbtp_itself = (len(regions) == 1 and regions[0].begin() in range(view.sel()[0].begin(), view.sel()[0].end()))
	246: # print(MyPanelCommand.tmbtp_itself)#debug
	```

4.	a simple regex example goes like:

	`/def.+one/`
	
	A possible result may show like:
	
	```
	1 <<< def run(self, text=None
	1 <<< def on_done
	 21: def run(self, text=None):
	 51: def on_done(self, text):
	```

5.	A typical example for permutation arrangement goes like:

	`abc;xyz;mno def;pqr` where the "syntax" of this example depends on the semi-colons and the space in between.

	which will generate a regex as below:

	```
	/pqrdef|defpqr|pqr|def|xyzmnoabc|abcmnoxyz|mnoxyzabc|abcxyzmno|mnoabcxyz|xyzabcmno|mnoxyz|mnoabc|xyzmno|xyzabc|abcmno|abcxyz|mno|xyz|abc/
	```

	and goes on for a regex search with it.
	
	simpler ones look like these two:

	`jkl;def;abc` >>> `/defabcjkl|jklabcdef|abcdefjkl|jkldefabc|abcjkldef|defjklabc|abcdef|abcjkl|defabc|defjkl|jklabc|jkldef|abc|def|jkl/`

	`ghi;stuvw` >>> `/stuvwghi|ghistuvw|stuvw|ghi/`

(to be continued)
