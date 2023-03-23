import sublime, sublime_plugin, re, time

class MyPanelCommand(sublime_plugin.WindowCommand):
	filepath = r"C:\Users\user\Documents\55776956"
	historyfile = filepath + r"\my_panel.txt"
	enum = 0
	items = []
	maxtol = 5  # maxtol stands for "maximum tolerance" in seconds
	# the initial value set here, for the variables below, doesn't really matter
	lc_len = 5	# how many characters (i.e. length) "line numbering" required
	mc_len = 5	# how many characters (i.e. length) "occurrance count for matches" required
	mark = ""	# this variable is for holding of the search term(s) for assorted matches
	case_i = True	# case_i stands for "case insensitive"
	ass_ao = False	# ass_ao stands for "assortment in ascending order"
	extraspace = ""	# this variable works actually for both space and semicolon
	tmbtp_itself = False	# tmbtp stands for "this might be the pattern"
	orisel = []	# orisel stands for "original selection"
	# end of variables initialization section

	def run(self, text=None):
		# Load from history upfront
		if MyPanelCommand.enum == 0:
			with open(MyPanelCommand.historyfile, "r") as f:
				MyPanelCommand.items += [item.strip("\n") for item in f.readlines()]
		MyPanelCommand.enum += 1
		# If anything is given as an argument, use it directly
		if text:
			# As this probably comes from the history list, show it on input_panel to enable further adjustment
			if len(MyPanelCommand.items) > 0:
				self.window.show_input_panel("Search:", "", self.on_done, None, self.on_cancel)
				self.window.run_command("insert", {"characters": text})
			# Otherwise, this comes from command argument at the very beginning (say, from console), hence need no adjustment
			else:
				self.on_done(text)
		# Otherwise, prompt the user for an input
		else:
			# Before the input_panel is shown, select the "target" first if any
			view = self.window.active_view()
			sel0 = view.sel()[0]
			point = sel0.begin()
			curlinbeg = view.line(point).begin()
			curlinend = view.line(point).end()
			if len(view.substr(sel0)) == 0:
				hash_region = view.find("##", curlinbeg)
				if hash_region.begin() >= curlinbeg and hash_region.end() <= curlinend:
					view.sel().clear(); view.sel().add(sublime.Region(hash_region.end(), curlinend))
			MyPanelCommand.orisel = list(view.sel())	# Keep the current selection in active_view for text-insert purpose
			self.window.show_input_panel("Search:", view.substr(view.sel()[0]), self.on_done, None, self.on_cancel)

	def on_done(self, text):
		view = self.window.active_view()
		# If anything is entered, process it and show the matches
		if text:
			# Check if any of the keywords for deleting history item is in place
			if re.search(r"\[del(?:ete)?\]|\[remove\]", text):
				text = re.sub(r"\[del(?:ete)?\]|\[remove\]", "", text)
				items = MyPanelCommand.items
				if text in items:
					items.remove(text)
					# Save changes
					with open(MyPanelCommand.historyfile, "w") as f:
						for item in MyPanelCommand.items: f.write(item + "\n")
				return self.window.run_command("my_panel")
			# No extra space by default
			MyPanelCommand.extraspace = ""
			# Check if a request is made for adding an extra leading space to the assortment return
			if re.search(r"^\s*=[ ;]=", text):
				MyPanelCommand.extraspace += ";" if re.search(r"^\s*=;=", text) else ""
				MyPanelCommand.extraspace += "head"
				text = re.sub(r"^\s*=[ ;]=", "", text)
			# Check if a request is made for adding an extra trailing space to the assortment return
			if re.search(r"=[ ;]=\s*$", text):
				MyPanelCommand.extraspace += ("&" if MyPanelCommand.extraspace[-4:] == "head" else "") + "tail"
				MyPanelCommand.extraspace += ";" if re.search(r"=;=\s*$", text) else ""
				text = re.sub(r"=[ ;]=\s*$", "", text)
			# Keep a history of all the entries but those already exist
			if text not in MyPanelCommand.items:
				MyPanelCommand.items.insert(0, text)
				# Save changes
				with open(MyPanelCommand.historyfile, "w") as f:
					for item in MyPanelCommand.items: f.write(item + "\n")
			# Do the essential process
			results = self.get_matched_lines(self.do_transformation(text))
			if results == [">>>Timeout<<<"]: self.prompt_timeout(view); return
			# print(MyPanelCommand.tmbtp_itself)#debug
			# Show the matched lines in quick_panel if found anything
			if len(results) > 0 and not MyPanelCommand.tmbtp_itself:
				view.erase_regions("MyPanel"); view.add_regions("MyPanel", view.find_all(MyPanelCommand.mark, sublime.IGNORECASE if MyPanelCommand.case_i else 0), "string", "dot")
				self.window.show_quick_panel(results, lambda idx: self.mpick(idx, results, text), 1, 0, lambda idx: self.on_highlight(idx, results))
			# Otherwise, attempt shorthand search
			else:
				results = self.get_matched_lines(self.do_transformation(text, "shorthand"))
				if results == [">>>Timeout<<<"]: self.prompt_timeout(view); return
				# Show the matched lines in quick_panel if found anything
				if len(results) > 0:
					view.erase_regions("MyPanel"); view.add_regions("MyPanel", view.find_all(MyPanelCommand.mark, sublime.IGNORECASE if MyPanelCommand.case_i else 0), "string", "dot")
					self.window.show_quick_panel(results, lambda idx: self.mpick(idx, results, text), 1, 0, lambda idx: self.on_highlight(idx, results))
				else:
					print("Nothing matched!"); self.window.status_message("Nothing matched!")
					self.window.run_command("my_panel", {"text": text})
					view.show_popup("<b style='background-color:red;color:lime'>: Nothing_matched! :</b>")
		# Otherwise, show the history in quick_panel
		else:
			items = MyPanelCommand.items
			if len(items) > 0:
				self.window.show_quick_panel(items, lambda idx: self.pick(idx, items, text))
			else:
				print("Empty list!"); self.window.status_message("Empty list!")
				self.window.run_command("my_panel", {"text": text})
				view.show_popup("<b style='background-color:red;color:yellow'>: Empty list! :</b>")

	def on_cancel(self):
		self.window.active_view().erase_regions("MyPanel")

	def prompt_timeout(self, view):
		print("Timeout!"); self.window.status_message("Timeout!")
		view.show_popup("<b style='background-color:lime;color:red'>: Timeout! :</b>")

	# Do the transformation if the syntax is matched
	def do_transformation(self, text, option=""):
		# Case insensitive by default
		MyPanelCommand.case_i = True
		# Handle case sensitive declaration if specified
		if re.search(r"^\s*=cs=|=cs=\s*$", text):
			MyPanelCommand.case_i = False
			text = re.sub(r"^\s*=cs=|=cs=\s*$", "", text)
		# Maintain chronological order for assortment by default
		MyPanelCommand.ass_ao = False
		# Handle assortment ascending order request
		if re.search(r"^\s*=aa=|=aa=\s*$", text):
			MyPanelCommand.ass_ao = True
			text = re.sub(r"^\s*=aa=|=aa=\s*$", "", text)
		# Prepare the text for shorthand search
		if option == "shorthand":
			text = (re.sub(r"([\w.])", r"(?:\\b\1\\w*\\b(?:[^\\w\\n]+|$))", re.sub(r"//$", "", text.strip())[:-1] if re.search(r"^/.+/$", text.strip()) else re.sub(r"//$", "", text.strip()))
			+ ("||" if re.search(r"^\S+\s+.+//$", text.strip()) else "|")
			+ re.sub(r"(?<=[\w.])(?=[\w.?])", r"(?:\w{0,3})", text.strip()[1:] if re.search(r"^/.+/$", text.strip()) else text.strip()))
		# Main transformation starts here
		if re.search(r"^\S+\s+.+//$", text.strip()):
			text = re.sub(r"//$", "", re.sub(r"\s+", " ", text.strip()))
			ta = text.strip().split("||") if re.search(r"^.+\|\|.+", text.strip()) else [text.strip()]
			text = ""
			MyPanelCommand.mark = ""
			for i in range(len(ta)):
				ts = ta[i].split(" ")
				text += "^"
				for j in range(len(ts)):
					if ts[j].startswith("-"):
						text += "(?!.*(?:" + ts[j][1:] + "))"
					else:
						text += "(?=.*(?:" + ts[j] + "))"
						MyPanelCommand.mark += "|" + ts[j]
				text += ".*$"
			text = text.replace(".*$^(?", ".*$|^(?")
			MyPanelCommand.mark = MyPanelCommand.mark[1:]
		elif re.search(r"^/.+/$", text.strip()):
			text = text.strip()[1:-1]
			MyPanelCommand.mark = text
		else:
			if "\\w{0,3}" not in text:
				text = re.escape(text)
			MyPanelCommand.mark = text
		sublime.set_clipboard(text)	# This exists for the user convenience as s/he may want to use the pattern to find the "needle" by other means, for instance, by ctrl+f
		return text

	# Generate a list of matched lines
	def get_matched_lines(self, text):
		results = []
		assortm = []
		seen = []
		lastfound = -1
		timeout = time.time() + MyPanelCommand.maxtol	# default to 5 seconds from now
		view = self.window.active_view()
		# Prepare for the line number formatting
		row, _ = view.rowcol(view.size())
		line_count = row + 1
		MyPanelCommand.lc_len = len(str(line_count))
		format_str = "{:>" + str(MyPanelCommand.lc_len) + "}:"
		# Find all possible marks as the preparation for assortment
		marks = [(i, i.begin(), i.end()) for i in view.find_all(MyPanelCommand.mark, sublime.IGNORECASE if MyPanelCommand.case_i else 0)]
		# Find all regions that match the text
		regions = view.find_all(text, sublime.IGNORECASE if MyPanelCommand.case_i else 0)
		# Loop through each region
		for region in regions:
			# Get the line number of the region
			line_number, _ = view.rowcol(region.begin())
			if line_number != lastfound:
				# Get the line text of the region
				line_text = view.substr(view.line(region))
				# Append the result to the list
				result = format_str.format(line_number + 1) + " " + line_text
				results.append(result)
				assortm += [view.substr(i[0]) for i in marks if i[1] >= view.line(region).begin() and i[2] <= view.line(region).end()]	#re.findall(MyPanelCommand.mark, line_text, re.IGNORECASE if MyPanelCommand.case_i else 0)
			lastfound = line_number
			if time.time() > timeout: return [">>>Timeout<<<"]
		# print(MyPanelCommand.mark)#debug
		# print(assortm)#debug
		stass = [item.strip() for item in assortm]
		if MyPanelCommand.ass_ao:	# Ascending order
			ulist = sorted([(i, stass.count(i)) for i in set(stass)], key=lambda x: x[0]) #; print(ulist)#debug
		else:	# Chronological order
			ulist = [(i, stass.count(i)) for i in [i for i in stass if i not in seen and not seen.append(i)]] #; print(ulist)#debug
		MyPanelCommand.mc_len = len(str(max(ulist, key=lambda x: x[1])[1])) if len(ulist) > 0 else 0
		assortm = [("{:>" + str(MyPanelCommand.mc_len) + "} <<< {}").format(value, key) for key, value in ulist]
		# print(assortm)#debug
		MyPanelCommand.tmbtp_itself = (len(regions) == 1 and regions[0].begin() in range(view.sel()[0].begin(), view.sel()[0].end()))
		# print(MyPanelCommand.tmbtp_itself)#debug
		return assortm + results

	# A helper function that runs this command again with the selected item
	def pick(self, index, items, text):
		# If a valid index is given (not -1 when cancelled)
		if index >= 0:
			# Run this command again with the selected item as an argument
			self.window.run_command("my_panel", {"text": items[index]})
		else:
			# Run this command again with the untransformed text
			self.window.run_command("my_panel", {"text": text})

	# A helper function that jump to the picked line
	def mpick(self, index, results, text):
		view = self.window.active_view()
		# If a valid index is given (not -1 when cancelled)
		if index >= 0:
			# If one of the assorted matches is picked, insert it directly
			if re.search(r"^\s*\d+ <<< ", results[index]):
				v = MyPanelCommand.mc_len + 5
				view.sel().clear(); view.sel().add_all(MyPanelCommand.orisel)	# Resume the original selection in active_view beforehand
				head = " " if MyPanelCommand.extraspace.startswith("head") else ";" if MyPanelCommand.extraspace.startswith(";") else ""
				tail = " " if MyPanelCommand.extraspace.endswith("tail") else ";" if MyPanelCommand.extraspace.endswith(";") else ""
				view.run_command("insert", {"characters": head + results[index][v:] + tail})
				MyPanelCommand.orisel = list(view.sel())	# Adopt new position(s) in active_view for next text-insert
				# Run this command again with the untransformed text
				self.window.run_command("my_panel", {"text": text})
			# Otherwise, goto the picked line
			else:
				v = MyPanelCommand.lc_len + 2
				# If it's my very log file, remove the first seven characters (which is the date stamp of that line) and insert it directly
				if view.file_name() == MyPanelCommand.filepath + r"\log.txt":
					view.sel().clear(); view.sel().add_all(MyPanelCommand.orisel)	# Resume the original selection in active_view beforehand
					view.run_command("insert", {"characters": results[index][v+7:]})
					MyPanelCommand.orisel = list(view.sel())	# Adopt new position(s) in active_view for next text-insert
					# Run this command again with the untransformed text
					self.window.run_command("my_panel", {"text": text})
					return
				# Otherwise, show the find_panel and insert the text (which is equivalent to "jump" to that line)
				self.window.run_command("show_panel", {"panel": "find", "regex": True})
				self.window.run_command("insert", {"characters": "\\Q" + results[index][v:]})	# Since i have always had my sublimetext3 "regex" option turned on, so use "\Q" (for "raw") to ensure "the find" found
				# Run this command again with the untransformed text
				self.window.run_command("my_panel", {"text": text})
		else:
			head = "= =" if MyPanelCommand.extraspace.startswith("head") else "=;=" if MyPanelCommand.extraspace.startswith(";") else ""
			tail = "= =" if MyPanelCommand.extraspace.endswith("tail") else "=;=" if MyPanelCommand.extraspace.endswith(";") else ""
			# Run this command again with the untransformed text
			self.window.run_command("my_panel", {"text": head + text + tail})

	# A helper function that scroll the buffer view to where the highlighted line is located
	def on_highlight(self, index, results):
		if not re.search(r"^\s*\d+ <<< ", results[index]):
			view = self.window.active_view()
			line_number = int(results[index][:MyPanelCommand.lc_len])
			line_region = view.full_line(view.text_point(line_number - 1, 0))
			view.set_viewport_position((0, view.text_to_layout(line_region.begin())[1] - view.viewport_extent()[1] / 2))
			line_region = view.line(view.text_point(line_number - 1, 0))
			mid_point = line_region.begin() + (line_region.end() - line_region.begin()) / 2
			view.sel().clear(); view.sel().add(sublime.Region(mid_point, mid_point))
