import os
import sys

import sublime
import sublime_plugin

from .isort import SortImports

sys.path.append(os.path.dirname(__file__))

class ViewHelper():

    def __init__(self, view=None):
        self.view = view

    def get_region(self):
        return sublime.Region(0, self.view.size())

    def get_buffer_contents(self):
        return self.view.substr(self.get_region())

    def set_view(self):
        self.view = sublime.active_window().active_view()
        return self.view

    def get_view(self):
        if self.view is None:
            return self.set_view()
        return self.view

    def set_cursor_back(self, begin_positions):
        this_view = self.get_view()
        for pos in begin_positions:
            this_view.sel().add(pos)

    def get_positions(self):
        pos = []
        for region in self.get_view().sel():
            pos.append(region)
        return pos

    def get_syntax(self):
        parts = self.view.settings().get('syntax').split('/') # Packages/Python/Python.sublime-syntax
        parts[-1] = parts[-1].replace('.sublime-syntax', '')
        if len(parts) > 1:
            return parts[-2], parts[-1]
        else:
            return parts[-1], parts[-1]

def get_settings():
    profile = sublime.active_window().active_view().settings().get('isort')
    return profile or {}

class IsortMonitor(sublime_plugin.EventListener):

    def on_pre_save(self, view):
        view_helper = ViewHelper(view)
        if ('Python', 'Python') == view_helper.get_syntax():
            view.run_command('isort')

class IsortCommand(sublime_plugin.TextCommand):
    view = None

    def run(self, edit):
        view_helper = ViewHelper()
        this_view = view_helper.set_view()

        current_positions = view_helper.get_positions()

        this_contents = view_helper.get_buffer_contents()
        settings = get_settings()
        sorted_imports = SortImports(
            file_contents=this_contents,
            **settings
        ).output
        this_view.replace(edit, view_helper.get_region(), sorted_imports)

        # Our sel has moved now..
        remove_sel = this_view.sel()[0]
        this_view.sel().subtract(remove_sel)
        view_helper.set_cursor_back(current_positions)
