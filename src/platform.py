import re
import subprocess

from . import errors


class SubProcess:

    @classmethod
    def run_command(cls, cmd):
        pip = subprocess.Popen(
            args=cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        success: str = pip.stdout.read()
        failed: str = pip.stderr.read()

        if failed:
            raise errors.RunCmdError(failed)

        if success:
            return success


class NT:
    _check_port_cmd = "netstat -ano -p TCP | find \"LISTENING\""
    _get_name_from_pid = "tasklist | findstr \"{}\""

    @classmethod
    def get_listen_port(cls):
        # First get the port number and program id, and then get its name according to the program id

        result = SubProcess.run_command(
            cls._check_port_cmd).split("\n")

        result_dict = {}

        for line in set(result):
            line = re.sub(" +", " ", line.strip())
            col = line.split(" ")

            if len(col) > 1:
                re_search = re.search(":(\d+)", col[1])

                if re_search:
                    port = int(re_search.group(1))
                    pid = int(col[-1])

                    name = SubProcess.run_command(
                        cls._get_name_from_pid.format(pid)).split(" ")[0]

                    result_dict[port] = name

        return result_dict


class POSIX:
    _check_port_cmd = "lsof -i -sTCP:LISTEN -Pn | awk '{ print $1, $9 }'"

    @classmethod
    def get_listen_port(cls):

        # Get program id and program name
        result = SubProcess.run_command(
            cls._check_port_cmd).split("\n")[1:-1]

        result_dict = {}

        for line in set(result):
            col = line.split(" ", 1)
            name = col[0]
            port = col[1]

            re_search = re.search(":(\d+)", port)

            if re_search:
                port = int(re_search.group(1))

                result_dict[port] = name

        return result_dict
