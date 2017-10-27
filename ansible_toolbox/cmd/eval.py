from __future__ import absolute_import

import contextlib
import logging
import os
import subprocess
import sys
import tempfile

from ansible_toolbox.base import BaseApp

LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def temporary_file(*args, **kwargs):
    name = tempfile.mktemp(*args, **kwargs)
    yield name
    os.unlink(name)


class App (BaseApp):
    def build_argument_parser(self):
        p = super(App, self).build_argument_parser()
        p.add_argument('expr')
        return p

    def main(self):
        args = self.parse_args()
        template = self.get_template('eval.yml')

        with tempfile.NamedTemporaryFile(dir='.') as tmplfd, \
                temporary_file(dir='.') as output:
            tmplfd.write(template.render(
                expr=args.expr,
                hosts=args.hosts,
                gather=args.gather,
                output=output,
            ).encode('utf-8'))

            tmplfd.flush()

            cmd = ['ansible-playbook', tmplfd.name]
            cmd.extend(self.build_command_line(args))
            subprocess.check_output(cmd)
            with open(output, 'r') as fd:
                sys.stdout.write(fd.read())
                sys.stdout.write('\n')


def main():
    App().main()