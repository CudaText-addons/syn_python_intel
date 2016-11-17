import os
from sw import *
import sw_cmd as cmds
from .intel_work import *

OFFSET_LINES=5

def is_wordchar(s):
    return (s=='_') or s.isalnum()


class Command:

    def goto_file(self, filename, num_line, num_col):

        file_open(filename)
        ed.set_top(num_line-OFFSET_LINES) #must be
        ed.set_caret_xy(num_col, num_line)

        print('Goto "%s", line %d' % (filename, num_line+1))


    def get_params(self):
        fn = ed.get_filename()
        x0, y0 = ed.get_caret_xy()

        line = ed.get_text_line(y0)
        if not 0 < x0 <= len(line):
            return ''

        text = ed.get_text_all()
        if text:
            return text, fn, y0, x0


    def on_complete(self, ed_self):
        params = self.get_params()
        if not params: return True
        text, fn, y0, x0 = params

        #calc len left
        x = x0
        line = ed.get_text_line(y0)
        while x>0 and is_wordchar(line[x-1]): x -= 1
        len1 = x0-x

        #calc len right
#        x = x0
#        while x<len(line) and is_wordchar(line[x]): x += 1
#        len2 = x-x0

#        print('len1', len1)
#        print('len2', len2)
        if len1<=0: return True

        text = handle_autocomplete(text, fn, y0, x0)
        if text:
            ed.complete(text, len1, True)
        return True


    def on_goto_def(self, ed_self):
        params = self.get_params()
        if not params: return True

        res = handle_goto_def(*params)
        if res:
            self.goto_file(*res)
        return True


    def on_func_hint(self, ed_self):
        params = self.get_params()
        if not params: return

        res = handle_func_hint(*params)
        if not res: return ''

        while bool(res) and is_wordchar(res[0]):
            res = res[1:]
        return res


    def show_usages(self):
        params = self.get_params()
        if not params: return

        items = handle_usages(*params)
        if not items:
            msg_status('Cannot find usages')
            return

        items_show = [
            os.path.basename(item[0])+
            ', Line %s, Col %d' %(item[1]+1, item[2]+1)+
            '\t'+item[0]
            for item in items
            ]
        res = dlg_menu(MENU_DOUBLE, '_', '\n'.join(items_show))
        if res is None: return

        item = items[res]
        self.goto_file(item[0], item[1], item[2])


    def show_docstring(self):
        params = self.get_params()
        if not params: return

        text = handle_docstring(*params)
        if text:
            app_log(LOG_SET_PANEL, LOG_PANEL_OUTPUT)
            app_log(LOG_CLEAR, '')
            for s in text.splitlines():
                app_log(LOG_ADD, s)
            #
            ed.cmd(cmds.cmd_ToggleFocusOutput)
            ed.cmd(cmds.cmd_ToggleFocusOutput)
        else:
            msg_status('Cannot find doc-string')

