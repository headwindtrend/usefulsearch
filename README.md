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

Change log:

* May 20, 2023&nbsp;&nbsp;&nbsp;&nbsp;adjusted some codes that i made some time ago today.

* May 20, 2023&nbsp;&nbsp;&nbsp;&nbsp;added a feature to load last result back on screen. it can save time when your file is big and/or your search term is sophisticated which takes noticeable time to complete, "load last result" is handy to show the last search result in memory without having to search again. enter this `[ll]` as your search term (or it exists anywhere in your search term) to get the result back.

* May 20, 2023&nbsp;&nbsp;&nbsp;&nbsp;added a feature for reverse order. it could be useful in dealing with a big log file that you very often interested in the matches close to the bottom than to the top. add this `=rv=` in your search term to get the search results listed in reverse order (by line).

* May 20, 2023&nbsp;&nbsp;&nbsp;&nbsp;spotted a careless omission in code (since 2023.5.13) hence this "commit" to have it replenished.

* May 16, 2023&nbsp;&nbsp;&nbsp;&nbsp;since both the "search by ime codes" and the "search by ime shorthand" require a pair of slashes (as they ultimately are converted to a regex search) and "search by ime shorthand" also require `=np=` as well, i figured to make it a bit more user-friendly by checking if you forgot to do it, the script will do it for you automatically. that's what this "commit" is done for.

* May 13, 2023&nbsp;&nbsp;&nbsp;&nbsp;improved the highlighting feature for multi-term search. for instance, given three lines of text, in which, `abcdefghijklm` is on the top, `nopqrstuvwxyz` at the bottom, and `abcdefghijklmnopqrstuvwxyz` in the middle, and you entered this `vwx cde//` for a multi-term search: in the old days, although only the middle line is shown on the quick_panel (as it's the only line that has both `vwx` and `cde`), all the `cde` and the `vwx` will be highlighted regardless of which line they are on. that was, the `cde` on both the top line and the middle line, as well as the `vwx` on both the middle line and the bottom line will be highlighted (in yellow). now, after this "commit", only the `cde` and `vwx` on the matched line(s) (in this case, the middle line) will be highlighted in yellow, whereas the `cde` on the top line and the `vwx` on the bottom line will be highlighted in gray instead.

* May 13, 2023&nbsp;&nbsp;&nbsp;&nbsp;minor adjustment. to make drilldown feature sticking with the `case insensitive` convention.

* May 4, 2023&nbsp;&nbsp;&nbsp;&nbsp;Branch "IME Shorthand Search" is created out of "Allow Search By IME Codes". imesh (ime shorthand) search is a new feature which will take the content of the current buffer and the udmtable to generate an imesh searchable version of the content in memory hence user can search text by any improvised ime shorthands. since generating the imesh searchable content takes time, i figured to keep it in memory for subsequent searches until user issues a "renew" instruction to regenerate it. i included a sample text file (which has lyrics) to show the power of this new feature. just open it up in sublime text editor and search this `/[[sws]]/=np=` to get a sense of it. to renew the content in memory, just add `[r]` or `[rn]` or `[renew]` in your search term, for instance, `/[[yjy]]/=np=[r]`.

* May 1, 2023&nbsp;&nbsp;&nbsp;&nbsp;fixed a minor bug which was induced on the first "commit" (re: slim ...) made on march-25.

* Apr 25, 2023&nbsp;&nbsp;&nbsp;&nbsp;Branch "Hotstring dqq" is created out of "main". i noticed i use ctrl+d ctrl+q (i assigned `my_panel` to ctrl+q, btw) quite often that i decided to add a hotstring feature as `dqq` for it.

* Apr 25, 2023&nbsp;&nbsp;&nbsp;&nbsp;three minor but necessary adjustments are made.

* Apr 24, 2023&nbsp;&nbsp;&nbsp;&nbsp;a minor adjustment to the last "commit": i should have had the temporary buffer closed when the user chosen not to continue on a timeout dialog. so here you go.

* Apr 23, 2023&nbsp;&nbsp;&nbsp;&nbsp;a month ago, i tried to avoid "re.findall". though the method i used was not up to my satisfaction after two days of practical usage. now, i believe i found a better way to achieve it, by using a temporary buffer. hence this "commit" to implement it.

* Apr 17, 2023&nbsp;&nbsp;&nbsp;&nbsp;A minor bug fix. Noticed an omission in the stack for drilldown operation, hence this "commit" to have it replenished.

* Apr 15, 2023&nbsp;&nbsp;&nbsp;&nbsp;1. Renewed the mechanism in identifying of history list from others; and 2. Added some codes in on_modified so that more scenarios of double-semicolon trick are covered hence a smoother operation is attained in using the trick.

* Apr 14, 2023&nbsp;&nbsp;&nbsp;&nbsp;Branch "Allow Search By IME Codes" is created out of "main". Added a new feature which enables you to search your target text by its ime code(s) directly without any necessity to pick the actual word(s) from the ime of the os.

* Apr 14, 2023&nbsp;&nbsp;&nbsp;&nbsp;Omitted "utf-8" encoding when the file is opened for "r" (read), hence this "commit" to have it replenished.

* Apr 12, 2023&nbsp;&nbsp;&nbsp;&nbsp;"File Specific History List" is a new feature which uses/records different history list for different file. To migrate from the old history list, you can rename `my_panel.txt` to something else; and when a new `my_panel.txt` is generated upon the plugin is loaded and used, you may move your old history items from the old list to the new list manually if you want to.

* Apr 9, 2023&nbsp;&nbsp;&nbsp;&nbsp;1. Added a copy feature as an option to put the search results into the clipboard. Can copy lines or asso or both, with or without line numbering; 2. Added UTF-8 encoding for the history list; and 3. Fixed two minor bugs, both related to flow control.

* Apr 8, 2023&nbsp;&nbsp;&nbsp;&nbsp;Found two minor bugs, both related to double-semicolon flow control, hence this "commit" to have them fixed.

* Apr 6, 2023&nbsp;&nbsp;&nbsp;&nbsp;Noticed an undesirable reaction to a double-semicolon in input_panel when some text is selected, which just stayed in input_panel and reshow the text rather than proceeding the search with the given text. Hence this "commit" to have it adjusted.

* Apr 5, 2023&nbsp;&nbsp;&nbsp;&nbsp;A minor adjustment. The zero was a careless mistake (though with no harm), it should be "index" by design.

* Apr 4, 2023&nbsp;&nbsp;&nbsp;&nbsp;Rewritten the drilldown mechanism which makes use of a stack to hold the information for fallback operation hence it can get back to the previous search results directly without going through the input_panel. And can cope with multi-level drilldown-n-fallback, even though one level can satisfy 99% requirement already in practical usages.

* Apr 4, 2023&nbsp;&nbsp;&nbsp;&nbsp;1. Added a few lines which raises/drops/checks the "history list is shown" flag, so that, the script can identify the scenario when you entered a double-semicolon without any other text typed in the history list hence taking it as the exit request instead of reshowing the history list. 2. Found another special case in addition to the one found some days ago regarding the backtick character. This time, the apostrophe character, same as backtick, need special handling.

* Apr 4, 2023&nbsp;&nbsp;&nbsp;&nbsp;An adjustment to the "commit" a while ago.

* Apr 4, 2023&nbsp;&nbsp;&nbsp;&nbsp;Changed the method to capture a double-semicolon, so that, only those consecutive semicolons within two seconds will be recognized as a valid double-semicolon. This way can increase the flexibility in text typing when `;;` is deliberately needed, simply by waiting for a while after the first `;` and before the second `;`. Otherwise, you may have to make use of `; ;` `leftarrow key` `backspace` `rightarrow key` or `;` `leftarrow key` `;` `rightarrow key` those kinds of hastles to get it around.

* Apr 2, 2023&nbsp;&nbsp;&nbsp;&nbsp;Used plugin_loaded(), and ditched the old way.

* Apr 1, 2023&nbsp;&nbsp;&nbsp;&nbsp;i realized a particular line should be somewhere else in the testing process, but i forgot to delete it from what it was. And i didn't retest the whole thing all over again that caused the omission unnoticed, hence this "commit" to fix it.

* Apr 1, 2023&nbsp;&nbsp;&nbsp;&nbsp;1. Added an undo "button" in history list to undo the last item-delete. The item revived by undo will be inserted into the current highlighted position on history list. The undo "button" only appears when there is something can be undoing. And only the last item-delete can be undoing (coz, it just supposed for the scenario when the item-delete was an accident/mistake, never thought a sophisticated undoing mechanism is necessary for this interface). 2. Added "=np=" as a possible modifier (in addition to the existing "=cs=" and "=aa=" modifiers) for the search term to NOT prescan-thus-pregroup the "too many" assorted matches. 3. Fixed the unwanted behavior for double-semicolon trick when some text is selected in active_view and nothing entered in the panel but only a double-semicolon.

* Mar 30, 2023&nbsp;&nbsp;&nbsp;&nbsp;Added a "button" into history list for item-edit. Now, by whichever way you type/pick your search term, it goes straight to generate the search result, unless you explicitly click "Edit". In case you want to type your search term from blank instead of edit upon an existing one, you either type directly in history list and end it with a double-semicolon, or pick any item and click edit (since the text brought to input_panel will be entirely selected by default, so just start typing, it will automatically be deleted as soon as your first keystroke is hit). Another way to reach input_panel is from the search result, press esc there will bring you to input_panel. Contrarily, you may use a double-semicolon there to get back to history list without going through input_panel. You may also type your search term directly in the search result interface with the double-semicolon trick. In fact, it works in find panel and console panel as well. Basically, anywhere you can type, it will work, supposedly.

* Mar 29, 2023&nbsp;&nbsp;&nbsp;&nbsp;Fixed a bug which came from the last "commit".

* Mar 29, 2023&nbsp;&nbsp;&nbsp;&nbsp;Added a popup (which serves as an action button) in history list for item-delete, as a better user interface for the job than the existing one. Since the popup inevitably obstructed the first row of the list, i added a dummy item on top of the list to minimize the impact. However, as soon as you start typing, the list gets shortening that obstruction will still be encountered. To get around it, i suggest you type a few tab characters beforehand. Because, the popup will stick with the caret hence a few tabs will move it to the right for certain distance and make the text underneath visible again.

* Mar 29, 2023&nbsp;&nbsp;&nbsp;&nbsp;It used to be placing the caret at the end of the text when input_panel is shown. Now, i changed it to entire text selected instead.

* Mar 29, 2023&nbsp;&nbsp;&nbsp;&nbsp;Replaced all "MyPanelCommand." with "self."

* Mar 28, 2023&nbsp;&nbsp;&nbsp;&nbsp;It used to be a two-level arrangement in terms of user interface. That was, it always show_input_panel (for input) first and therefore show_quick_panel (for search result, or history list if null string is entered). Now, to simplify (in operational point of view) it a bit, it goes straight to the history list if no selection is found for search. (So, this also implied if a selection is found for search, it will go straight to search and show you the search result.) You can select an item and edit upon, or type your search term directly there (since the history list will keep on shortening as you type, you can always pick one from the list). When you finish your typing and it's non-existent (i.e. nothing matched on the list), you have to type a double-semicolon instead of hitting the enter key though. Because the enter key is not functioning when nothing matched. In fact, please note, the enter key there is NOT for ending your typing and taking whatever you have typed for search. It's only for selecting the highlighted item. So, by all means, the safest bet there, is always use a double-semicolon to end it, unless you eventually go for picking an item from the list. By the way, the double-semicolon trick also works in active_view, it simply triggers the search (or a history list if the "##something" (in which, "something" means you have something after "##" and before where you typed a double-semicolon) is not found) there.

* Mar 28, 2023&nbsp;&nbsp;&nbsp;&nbsp;A minor adjustment, no impact to the outcome nor any parts of the code whatsoever. Just because i found that i can use show_at_center instead of set_viewport_position, that's why.

* Mar 26, 2023&nbsp;&nbsp;&nbsp;&nbsp;Found a special case that needs to be handled. It's regarding the backtick character, which will become "\\\`" from re.escape() whereas view.find_all() expects just "\`". "\\\`" simply doesn't work, makes it not found. It's another kind of inconsistency between Python and Sublime Text 3, i guess.

* Mar 25, 2023&nbsp;&nbsp;&nbsp;&nbsp;After two days of practical usage of the post-"avoided re.findall" code, i found that some of the scenarios are as slow as unbearable. so, i have to revoke it for now. besides, i also fixed another bug in the "slim mechanism" that was put on lately.

* Mar 25, 2023&nbsp;&nbsp;&nbsp;&nbsp;Fixed a bug (which was brought in from the last "commit").

* Mar 25, 2023&nbsp;&nbsp;&nbsp;&nbsp;Added a mechanism, which slimed the search result, to improve response time when too many hits have been returned from the search. The final outcome is not much changed while the response time is improved. A slight bump is nevertheless caused. Some of the existing codes have been tuned to work with it.

* Mar 23, 2023&nbsp;&nbsp;&nbsp;&nbsp;Added a dialog to the timeout logic, so that users can choose to continue when maximum tolerance (in seconds) is reached. If continue is chosen, next timeout will become "now + maxtol".

* Mar 23, 2023&nbsp;&nbsp;&nbsp;&nbsp;Some of the behaviors between "view.find_all" and "re.findall" are inconsistent (perhaps they adopted different regular expression standards) enough that i decided to avoid "re.findall" (even though it is rather handy) and use only "view.find_all" to achieve everything i needed. so, this "commit" is all about it, as well as a minor code adjustment (to move some code out of the loop, as they were not needed inside, but before it). that's all.

* Mar 23, 2023&nbsp;&nbsp;&nbsp;&nbsp;Forgot to cater for "case_i" when i added the code for "visual effects" on March 20. Besides, i also forgot to reset the "orisel" after any text is picked and inserted into the buffer, which should have been part of the code added for, again, "visual effects" on March 20. so here you go, this "commit" have them put on.

* Mar 21, 2023&nbsp;&nbsp;&nbsp;&nbsp;Found a scenario where tmbtp_itself checking missed, so here you go, this "commit" has it covered.

* Mar 20, 2023&nbsp;&nbsp;&nbsp;&nbsp;Forgot to handle the implication of "the selection in active_view may be changed" in the last "commit", so here you go, this "commit" has it rounded up.

* Mar 20, 2023&nbsp;&nbsp;&nbsp;&nbsp;Added some visual effects to the matched text in active_view, and place the insertion point (caret) to that line in active_view when that line is highlighted on the quick_panel.

* Mar 19, 2023&nbsp;&nbsp;&nbsp;&nbsp;Minor update: moved the "text" variable initialization line upward until it stood outside the "... doesn't really matter" scope. it was not appropriate to be put inside that scope in the first place.

* Mar 19, 2023&nbsp;&nbsp;&nbsp;&nbsp;This is the second batch of changes for this branch. Added a drilldown feature: when an assorted match is picked and it is part of the search term, that item will be searched and show in the quick_panel, whereas the original text in the input_panel will be maintained.

* Mar 19, 2023&nbsp;&nbsp;&nbsp;&nbsp;Branch "With Permutation Arrangement" is created. This is the very first change for this newly created branch. In other words, before this change, this branch was exactly the same as the "main".

* Mar 19, 2023&nbsp;&nbsp;&nbsp;&nbsp;Branch "main" is created.
