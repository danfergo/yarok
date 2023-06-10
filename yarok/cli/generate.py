import os
import shutil


def generate(template):
    cwd = os.getcwd()
    drafts_path = os.path.dirname(os.path.abspath(__file__))

    cwd_file = os.path.join(cwd, template + '.py')
    drafts_file = os.path.join(drafts_path, 'drafts', template + '.py')

    if os.path.exists(cwd_file):
        print(f'File {template}.py already exits.')
        return

    print(f'Generated {template}.py')
    shutil.copyfile(drafts_file, cwd_file)