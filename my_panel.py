import sublime, sublime_plugin, re, time, json, os

class MyPanelCommand(sublime_plugin.WindowCommand):
	filepath = r"C:\Users\user\Documents\55776956"
	historyfile = filepath + r"\my_panel.txt"
	histdict = {}	# this variable is added for "file specific history list"
	filename = ""	# this variable keep track of the file name of active_view
	maxtol = 5	# maxtol stands for "maximum tolerance" in seconds
	stack = []	# this variable is added for drilldown
	flags = []	# this variable is added for flow control
	lastdel = ""	# this variable is added for the undo feature
	# the initial value set here, for the variables below, doesn't really matter
	items = []	# this variable keep track all history items
	lc_len = 5	# how many characters (i.e. length) "line numbering" required
	mc_len = 5	# how many characters (i.e. length) "occurrance count for matches" required
	mark = ""	# this variable is for holding of the search term(s) for assorted matches
	case_i = True	# case_i stands for "case insensitive"
	ass_ao = False	# ass_ao stands for "assortment in ascending order"
	extraspace = ""	# this variable works actually for both space and semicolon
	tmbtp_itself = False	# tmbtp stands for "this might be the pattern"
	orisel = []	# orisel stands for "original selection"
	lastseenQP = 0	# keep last seen quick panel
	type_of_QP = ""	# either "history list" or "search result"
	lastview = 0	# keep last-activated view
	grptycoon = True	# a flag for prescan and pregroup for "too many"
	copywhat = ""	# this variable is added for holding of the copy instruction
	# end of variables initialization section

	def run(self, text=None):
		view = self.window.active_view()

		def s_handler(endpoint, skip_input=False):
			# Before the input_panel is shown, select the "target" first if any
			sel0 = view.sel()[0]
			if len(view.substr(sel0)) == 0:
				point = sel0.begin()
				curlinbeg = view.line(point).begin()
				hash_region = view.find("##", curlinbeg)
				if hash_region.begin() >= curlinbeg and hash_region.end() <= endpoint:
					view.sel().clear(); view.sel().add(sublime.Region(hash_region.end(), endpoint))
			# If still nothing selected, show history list directly
			if len(view.substr(view.sel()[0])) == 0 or ";;event;;" in self.flags:
				self.show_history()
			# Otherwise, bring up input_panel with the selected text
			else:
				self.orisel = list(view.sel())	# Keep the current selection in active_view for text-insert purpose
				if skip_input: self.on_done(view.substr(view.sel()[0]))	# Search it directly as this skip_input flag implied
				else:
					self.window.show_input_panel("Search:", view.substr(view.sel()[0]), self.on_done, None, self.on_cancel)

		# If anything is given as an argument, use it directly
		if text:
			# If it's this ";;event;;" particular string, it probably came from event listener
			if text == ";;event;;":
				text = ""; s_handler(view.sel()[0].begin(), True)
			# Otherwise, if not this "[=escape=]" particular string, it probably came from the history list, show it on input_panel to enable further adjustment
			elif text != "[=escape=]":
				# Provided that it's an existing item
				if not (self.quick_panel_ssos() or "no edit" in self.flags or ";;NonQP;;" in self.flags) or "yes edit" in self.flags:	# re.sub(r"^\s*=[ ;]=|=[ ;]=\s*$", "", text) in self.items
					if "yes edit" in self.flags: self.flags.remove("yes edit")
					self.window.show_input_panel("Search:", text, self.on_done, None, self.on_cancel)
					self.window.run_command('move_to', {"to": "bol", "extend": True})
				# Otherwise, search it directly
				else:
					if "no edit" in self.flags: self.flags.remove("no edit")
					if ";;NonQP;;" in self.flags: self.flags.remove(";;NonQP;;")
					self.on_done(text)
		# Otherwise, prompt the user for an input
		else: s_handler(view.line(view.sel()[0].begin()).end(), True)

	def show_history(self, index=1):
		h_dsc_only = self.quick_panel_ssos() and self.type_of_QP == "history list" and ";;event;;" in self.flags
		self.hide_quick_panel()
		if ";;event;;" in self.flags: self.flags.remove(";;event;;")
		if h_dsc_only: return	# quit if only double-semicolon is entered in history list
		if len(self.items) > 0:
			self.window.show_quick_panel(self.items, self.pick, 1, index, self.on_history_item_highlight)
		else:
			self.window.show_input_panel("Search:", "", self.on_done, None, self.on_cancel)

	def hide_quick_panel(self):
		if self.quick_panel_ssos():	# ssos stands for "still shown on screen"
			self.window.run_command("hide_overlay")
			if "chain" not in self.flags: self.flags.append("chain")

	def quick_panel_ssos(self):
		return self.lastview == self.lastseenQP

	def on_done(self, text):
		self.hide_quick_panel()
		view = self.window.active_view()
		# If anything is entered, process it and show the matches
		if text:
			# Check if any of the keywords for deleting history item is in place
			if re.search(r"\[del(?:ete)?\]|\[remove\]", text):
				text = re.sub(r"\[del(?:ete)?\]|\[remove\]", "", text)
				items = self.items
				if text in items:
					items.remove(text)
					self.save_history()
				return self.window.run_command("my_panel")
			# No need copy by default
			self.copywhat = ""
			# Check if the copy instruction is in place
			pattern = r"\[copy(?:\s*[+/]n)?\s+(?:plain|lines?|asso?|both)(?:\s*[+/]n)?\]|\[c(?:opy)?\]"
			copy_in_place = re.search(pattern, text)
			if copy_in_place:
				self.copywhat = copy_in_place.group()
				text = re.sub(pattern, "", text)
			# No extra space by default
			self.extraspace = ""
			# Check if a request is made for adding an extra leading space to the assortment return
			if re.search(r"^\s*=[ ;]=", text):
				self.extraspace += ";" if re.search(r"^\s*=;=", text) else ""
				self.extraspace += "head"
				text = re.sub(r"^\s*=[ ;]=", "", text)
			# Check if a request is made for adding an extra trailing space to the assortment return
			if re.search(r"=[ ;]=\s*$", text):
				self.extraspace += ("&" if self.extraspace[-4:] == "head" else "") + "tail"
				self.extraspace += ";" if re.search(r"=;=\s*$", text) else ""
				text = re.sub(r"=[ ;]=\s*$", "", text)
			# Keep a history of all the entries but those already exist
			if text not in self.items:
				self.items.insert(1, text)
				self.save_history()
			# Do the essential process
			results = self.get_matched_lines(self.do_transformation(text))
			if results == [">>>Timeout<<<"]: self.prompt_timeout(view); return
			# Show the matched lines in quick_panel if found anything
			if len(results) > 0 and not self.tmbtp_itself:
				view.erase_regions("MyPanel"); view.add_regions("MyPanel", view.find_all(self.mark, sublime.IGNORECASE if self.case_i else 0), "string", "dot")
				self.window.show_quick_panel(results, lambda idx: self.mpick(idx, results, text), 1, 0, lambda idx: self.on_highlight(idx, results)); self.stack = []
			# Otherwise, attempt shorthand search
			else:
				results = self.get_matched_lines(self.do_transformation(text, "shorthand"))
				if results == [">>>Timeout<<<"]: self.prompt_timeout(view); return
				# Show the matched lines in quick_panel if found anything
				if len(results) > 0:
					view.erase_regions("MyPanel"); view.add_regions("MyPanel", view.find_all(self.mark, sublime.IGNORECASE if self.case_i else 0), "string", "dot")
					self.window.show_quick_panel(results, lambda idx: self.mpick(idx, results, text), 1, 0, lambda idx: self.on_highlight(idx, results)); self.stack = []
				else:
					print("Nothing matched!"); self.window.status_message("Nothing matched!")
					self.window.run_command("my_panel", {"text": text})
					view.show_popup("<b style='background-color:red;color:lime'>: Nothing_matched! :</b>")
		# Otherwise, show the history in quick_panel
		else:
			items = self.items
			if len(items) > 0:
				self.show_history()
			else:
				print("Empty list!"); self.window.status_message("Empty list!")
				self.window.run_command("my_panel", {"text": text})
				view.show_popup("<b style='background-color:red;color:yellow'>: Empty list! :</b>")

	def on_cancel(self):
		self.window.active_view().erase_regions("MyPanel")

	def prompt_timeout(self, view):
		print("Timeout!"); self.window.status_message("Timeout!")
		view.show_popup("<b style='background-color:lime;color:red'>: Timeout! :</b>")

	def pf(self, a, n, i=0, c=""):
		r = ""
		for j in range(len(a)):
			if a[j] not in c:
				r = (self.pf(a, n, i + 1, a[j] + c) if i < n else "|" + c + a[j]) + r
		return r

	# Do the transformation if the syntax is matched
	def do_transformation(self, text, option=""):
		# Case insensitive by default
		self.case_i = True
		# Handle case sensitive declaration if specified
		if re.search(r"^\s*=cs=|=cs=\s*$", text):
			self.case_i = False
			text = re.sub(r"^\s*=cs=|=cs=\s*$", "", text)
		# Maintain chronological order for assortment by default
		self.ass_ao = False
		# Handle assortment ascending order request
		if re.search(r"^\s*=aa=|=aa=\s*$", text):
			self.ass_ao = True
			text = re.sub(r"^\s*=aa=|=aa=\s*$", "", text)
		# Prescan and pregroup for "too many" by default
		self.grptycoon = True
		# Handle no prescan&pregroup request
		if re.search(r"^\s*=np=|=np=\s*$", text):
			self.grptycoon = False
			text = re.sub(r"^\s*=np=|=np=\s*$", "", text)
		# Prepare the text for shorthand search
		if option == "shorthand":
			text = (re.sub(r"([\w.])", r"(?:\\b\1\\w*\\b(?:[^\\w\\n]+|$))", re.sub(r"//$", "", text.strip())[:-1] if re.search(r"^/.+/$", text.strip()) else re.sub(r"//$", "", text.strip()))
			+ ("||" if re.search(r"^\S+\s+.+//$", text.strip()) else "|")
			+ re.sub(r"(?<=[\w.])(?=[\w.?])", r"(?:\w{0,3})", text.strip()[1:] if re.search(r"^/.+/$", text.strip()) else text.strip()))
		# Otherwise, if it's my very log file
		elif self.window.active_view().file_name() == self.filepath + r"\log.txt":
			# If delimiter for permutation arrangement is found and it's not multi-term search
			if re.search(r"\S;\S", text) and not re.search(r"^\S+\s+.+//$", text.strip()):
				# Remove the leading and trailing slashes pair if found
				text = text.strip()[1:-1] if re.search(r"^/.+/$", text.strip()) else text.strip()
				# Permutation arrangement takes place
				ts = re.split(r"\s+", text) if re.search(r"\s+", text) else [text]
				text = "/"
				for i in range(len(ts)):
					ta = re.split(r"(?<=\S);(?=\S)", ts[i])
					for j in range(len(ta)):
						text = self.pf(ta, j) + text
				text = "/" + (text[1:] if text[:1] == "|" else text)
		# Main transformation starts here
		if re.search(r"^\S+\s+.+//$", text.strip()):
			text = re.sub(r"//$", "", re.sub(r"\s+", " ", text.strip()))
			ta = text.strip().split("||") if re.search(r"^.+\|\|.+", text.strip()) else [text.strip()]
			text = ""
			self.mark = ""
			for i in range(len(ta)):
				ts = ta[i].split(" ")
				text += "^"
				for j in range(len(ts)):
					if ts[j].startswith("-"):
						text += "(?!.*(?:" + ts[j][1:] + "))"
					else:
						text += "(?=.*(?:" + ts[j] + "))"
						self.mark += "|" + ts[j]
				text += ".*$"
			text = text.replace(".*$^(?", ".*$|^(?")
			self.mark = self.mark[1:]
		elif re.search(r"^/.+/$", text.strip()):
			text = text.strip()[1:-1]
			self.mark = text
		else:
			if "\\w{0,3}" not in text:
				text = re.escape(text); text = text.replace(r"\`", "`").replace(r"\'", "'")
			self.mark = text
		if not self.copywhat: sublime.set_clipboard(text)	# This exists for the user convenience as s/he may want to use the pattern to find the "needle" by other means, for instance, by ctrl+f
		return text

	# Generate a list of matched lines
	def get_matched_lines(self, text):
		results = []
		assortm = []
		seen = []
		lastfound = -1
		timeout = time.time() + self.maxtol	# default to 5 seconds from now
		view = self.window.active_view()
		# Prevent those assorted matches, being deemed "too many", from entering the main loop (as it unnecessarily slowdowns the process)
		slimark = self.mark
		if self.grptycoon and "|" in slimark and "\\w{0,3}" not in slimark:
			ma = slimark.split("|")
			for i in range(len(ma)):
				n = len(view.find_all(ma[i], sublime.IGNORECASE if self.case_i else 0))
				if n > 99:	# definition of "too many"
					assortm += [str(n) + " <<< " + ma[i]]
					slimark = ("|" + slimark + "|").replace("|" + ma[i] + "|", "|"); slimark = slimark[1:-1]
				elif n == 0:	# take the chance to remove those nonexistent candidates
					slimark = ("|" + slimark + "|").replace("|" + ma[i] + "|", "|"); slimark = slimark[1:-1]
		# Prepare for the line number formatting
		row, _ = view.rowcol(view.size())
		line_count = row + 1
		self.lc_len = len(str(line_count))
		format_str = "{:>" + str(self.lc_len) + "}:"
		# Find all possible marks as the preparation for assortment
# 		marks = [(view.substr(i), i.begin(), i.end()) for i in view.find_all(slimark if slimark else self.mark, sublime.IGNORECASE if self.case_i else 0)]
		# Find all regions that match the text
		regions = view.find_all(text, sublime.IGNORECASE if self.case_i else 0)
		# Loop through each region
		for ri, region in enumerate(regions):
			# Get the line number of the region
			line_number, _ = view.rowcol(region.begin())
			if line_number != lastfound:
				# Get the line text of the region
				line_text = view.substr(view.line(region))
				# Append the result to the list
				result = format_str.format(line_number + 1) + " " + line_text
				results.append(result)
# 				assortm += [i[0] for i in marks if i[1] >= view.line(region).begin() and i[2] <= view.line(region).end()]	#re.findall(self.mark, line_text, re.IGNORECASE if self.case_i else 0)
				assortm += re.findall(slimark if slimark else self.mark, line_text, re.IGNORECASE if self.case_i else 0)
			lastfound = line_number
			if time.time() > timeout:
				percent_completed = (ri + 1) / len(regions) * 100
				themessage = str(int(percent_completed)) + "% completed\n\nDo you want to continue?"
				yesno = sublime.yes_no_cancel_dialog(themessage, "Yes", "No")
				if yesno == sublime.DIALOG_YES: timeout = time.time() + self.maxtol	# reset timer
				else: return [">>>Timeout<<<"]
		stass = [item.strip() for item in assortm]
		if self.ass_ao:	# Ascending order
			ulist = sorted([(i, stass.count(i)) for i in set(stass)], key=lambda x: x[0])
		else:	# Chronological order
			ulist = [(i, stass.count(i)) for i in [i for i in stass if i not in seen and not seen.append(i)]]
		self.mc_len = len(str(max(ulist, key=lambda x: x[1])[1])) if len(ulist) > 0 else 0
		assortm = [("{:>" + str(self.mc_len) + "} " + (">>>" if "<<<" in key else "<<<") + " {}").format(value, key) for key, value in ulist]
		self.tmbtp_itself = (len(regions) == 1 and regions[0].begin() in range(view.sel()[0].begin(), view.sel()[0].end()))
		if self.copywhat:
			matchedlines = ""
			if "both" in self.copywhat or "ass" in self.copywhat:
				for item in assortm: matchedlines += (item if "/n" in self.copywhat or "+n" in self.copywhat else item[item.find(" <<< ") + 5:]) + "\n"
			if self.copywhat == "[c]" or self.copywhat == "[copy]" or "both" in self.copywhat or "line" in self.copywhat or "plain" in self.copywhat:
				for item in results: matchedlines += (item if "/n" in self.copywhat or "+n" in self.copywhat else item[self.lc_len + 2:]) + "\n"
			sublime.set_clipboard(matchedlines)
		return assortm + results

	# A helper function that runs this command again with the selected item
	def pick(self, index):
		self.lastseenQP = ""
		# If a valid index is given (not -1 when cancelled)
		if index >= 0:
			if "no edit" not in self.flags: self.flags.append("no edit")
			# Run this command again with the selected item as an argument
			self.window.run_command("my_panel", {"text": self.items[index]})
		else:
			if "chain" in self.flags: self.flags.remove("chain")
			# Run this command again with the untransformed text
			self.window.run_command("my_panel", {"text": "[=escape=]"})

	# A helper function that jump to the picked line
	def mpick(self, index, results, text):
		view = self.window.active_view()
		# If a valid index is given (not -1 when cancelled)
		if index >= 0:
			# If one of the assorted matches is picked, insert it directly
			if re.search(r"^(?:\s*\d+ >>> )?\s*\d+ <<< ", results[index]):
				v = results[index].find(" <<< ") + 5	#self.mc_len + 5
				if not self.grptycoon or results[index][v:] in self.mark:
					new_index = 0
					if results[index][v:] != text and (not self.grptycoon or int(re.search(r"\d+(?= <<< )", results[index]).group()) < 100):	# impose a limit for drilldown
						if len(self.stack) == 0 or len(self.stack) > 0 and self.stack[-1] != (index, results, text, self.extraspace, self.mark, self.grptycoon):
							self.stack += [(index, results, text, self.extraspace, self.mark, self.grptycoon)]
						text = results[index][v:]
						results = self.get_matched_lines(self.do_transformation(text))
						view.erase_regions("MyPanel"); view.add_regions("MyPanel", view.find_all(self.mark, sublime.IGNORECASE if self.case_i else 0), "string", "dot")
					else:
						self.window.status_message("Drilldown is rejected!"); new_index = index
					self.window.show_quick_panel(results, lambda idx: self.mpick(idx, results, text), 1, new_index, lambda idx: self.on_highlight(idx, results))
					return
				view.sel().clear(); view.sel().add_all(self.orisel)	# Resume the original selection in active_view beforehand
				head = " " if self.extraspace.startswith("head") else ";" if self.extraspace.startswith(";") else ""
				tail = " " if self.extraspace.endswith("tail") else ";" if self.extraspace.endswith(";") else ""
				view.run_command("insert", {"characters": head + results[index][v:] + tail})
				self.orisel = list(view.sel())	# Adopt new position(s) in active_view for next text-insert
				# Run this command again with the untransformed text
				self.window.run_command("my_panel", {"text": text})
			# Otherwise, goto the picked line
			else:
				v = self.lc_len + 2
				# If it's my very log file, remove the first seven characters (which is the date stamp of that line) and insert it directly
				if view.file_name() == self.filepath + r"\log.txt":
					view.sel().clear(); view.sel().add_all(self.orisel)	# Resume the original selection in active_view beforehand
					view.run_command("insert", {"characters": results[index][v+7:]})
					self.orisel = list(view.sel())	# Adopt new position(s) in active_view for next text-insert
					# Run this command again with the untransformed text
					self.window.run_command("my_panel", {"text": text})
					return
				# Otherwise, show the find_panel and insert the text (which is equivalent to "jump" to that line)
				self.window.run_command("show_panel", {"panel": "find", "regex": True})
				self.window.run_command("insert", {"characters": "\\Q" + results[index][v:]})	# Since i have always had my sublimetext3 "regex" option turned on, so use "\Q" (for "raw") to ensure "the find" found
				# Run this command again with the untransformed text
				self.window.run_command("my_panel", {"text": text})
		elif "chain" in self.flags:
			self.flags.remove("chain"); self.window.run_command("my_panel", {"text": "[=escape=]"})
		else:
			fallback = len(self.stack) > 0
			if fallback:
				index, results, text, self.extraspace, self.mark, self.grptycoon = self.stack.pop()
				view.erase_regions("MyPanel"); view.add_regions("MyPanel", view.find_all(self.mark, sublime.IGNORECASE if self.case_i else 0), "string", "dot")
			head = "= =" if self.extraspace.startswith("head") else "=;=" if self.extraspace.startswith(";") else ""
			tail = "= =" if self.extraspace.endswith("tail") else "=;=" if self.extraspace.endswith(";") else ""
			# Run this command again with the untransformed text
			if fallback: self.window.show_quick_panel(results, lambda idx: self.mpick(idx, results, text), 1, index, lambda idx: self.on_highlight(idx, results))
			else:
				if text:
					if "yes edit" not in self.flags: self.flags.append("yes edit")
				self.window.run_command("my_panel", {"text": head + text + tail})

	# A helper function that scroll the buffer view to where the highlighted line is located
	def on_highlight(self, index, results):
		self.lastseenQP = self.lastview; self.type_of_QP = "search result"
		if not re.search(r"^(?:\s*\d+ >>> )?\s*\d+ <<< ", results[index]):
			view = self.window.active_view()
			line_number = int(results[index][:self.lc_len])
			line_region = view.line(view.text_point(line_number - 1, 0))
			mid_point = line_region.begin() + (line_region.end() - line_region.begin()) / 2
			view.sel().clear(); view.sel().add(sublime.Region(mid_point, mid_point))
			view.show_at_center(mid_point)

	# A helper function that show a popup for item-delete
	def on_history_item_highlight(self, index):
		self.lastseenQP = self.lastview; self.type_of_QP = "history list"
		self.PanelView.show_popup("<a href='edit'><b style='background-color:blue;color:yellow'>: Edit :</b> <a href='delete'><b style='background-color:lime;color:red'>: Delete :</b>" + (" <a href='undo'><b style='background-color:chocolate;color:white'>: Undo :</b>" if len(self.lastdel) > 0 else ""), location= self.PanelView.visible_region().end(), on_navigate= lambda href: self.on_navigate(href, index))

	def on_navigate(self, href, index):
		if href == "delete":
			self.lastdel = self.items[index]
			if index > 0: self.items.pop(index)
		elif href == "edit":
			if "yes edit" not in self.flags: self.flags.append("yes edit")
			self.window.run_command("my_panel", {"text": self.items[index]})
		elif href == "undo":
			self.items.insert(index, self.lastdel); self.lastdel = ""
		if href in ["delete", "undo"]:
			self.save_history()
			self.lastseenQP = self.lastview; self.type_of_QP = "history list"; self.show_history(index)

	def save_history(self):
		with open(self.historyfile, "w", encoding="utf-8") as f:
			f.write(json.dumps(self.histdict)[2:-1].replace(r'\"', '&quot;').replace('", "', '\n').replace('": ["', '\n[\n').replace('"], "', '\n]\n\n').replace('"]', '\n]\n').replace('&quot;', '"'))

class MyListener(sublime_plugin.EventListener):
	timeout = 0

	def on_modified(self, view):
		sel0 = view.sel()[0]; dsc_detected = False	# dsc stands for double-semicolon
		if len(view.substr(sel0)) == 0:
			point = sel0.begin()
			if view.substr(sublime.Region(point - 2, point)) == ";;":
				if self.timeout > time.time(): dsc_detected = True
				else: self.timeout = time.time() + 2
			elif view.substr(sublime.Region(point - 1, point)) == ";":
				self.timeout = time.time() + 2
		if view.command_history(0) == ('insert', {'characters': ';;'}, 1) or dsc_detected:
			if view.command_history(0) == ('insert', {'characters': ';;'}, 1): view.run_command("undo")
			else: view.run_command("left_delete"); view.run_command("left_delete")
			MyPanelCommand.type_of_QP = ""
			if view == view.window().active_view():
				view.window().run_command("my_panel", {"text": ";;event;;"})
			else:
				line_text = view.substr(view.line(sublime.Region(0, 0)))
				if len(line_text) == 0:
					if ";;event;;" not in MyPanelCommand.flags: MyPanelCommand.flags.append(";;event;;")
				if MyPanelCommand.lastview != MyPanelCommand.lastseenQP:
					if ";;NonQP;;" not in MyPanelCommand.flags: MyPanelCommand.flags.append(";;NonQP;;")
				view.window().run_command("my_panel", {"text": line_text})

	def on_activated(self, view):
		# Use different history list for different file
		if view.window().active_view().file_name() != MyPanelCommand.filename:
			MyPanelCommand.filename = view.window().active_view().file_name()
			if MyPanelCommand.filename not in MyPanelCommand.histdict: MyPanelCommand.histdict[MyPanelCommand.filename] = []
			MyPanelCommand.items = MyPanelCommand.histdict[MyPanelCommand.filename]
			if len(MyPanelCommand.items) == 0 or MyPanelCommand.items[0] != MyPanelCommand.topline:
				if MyPanelCommand.topline in MyPanelCommand.items: MyPanelCommand.items.remove(MyPanelCommand.topline)
				MyPanelCommand.items.insert(0, MyPanelCommand.topline)
		# PanelView is set if it is not a buffer
		if view != view.window().active_view():
			MyPanelCommand.PanelView = view
		# lastview is set, and its content is the id of the activated view
		MyPanelCommand.lastview = view.id()

def plugin_loaded():
	MyPanelCommand.topline = ">>>" + " "*27 + "Top of history list"
	if os.path.isfile(MyPanelCommand.historyfile):
		with open(MyPanelCommand.historyfile, "r", encoding="utf-8") as f:
			filecontent = f.read()
			filecontent = filecontent.replace('"', r'\"')
			filecontent = re.sub(r"^(?![[\]]$)(.+)$", r'"\1"', filecontent, flags=re.MULTILINE)
			filecontent = re.sub(r'(?<=")\s+(?=\[)', ':', re.sub(r'(?<=["\]])\s+(?=")', ',', filecontent))
			filecontent = re.sub(r'^\s+|(?<=\[)\s+(?=")|(?<=")\s+(?=])|\s+$', '', filecontent)
			MyPanelCommand.histdict = json.loads("{" + filecontent + "}")
