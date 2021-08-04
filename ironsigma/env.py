import os


def load(fileOrStream, env_prefix='') -> dict:
    """Load environment file as dictionary.

    File is just lines of key value pairs separated by an equal sign.

    Blank lines and lines starting with # are ignored.

    Values that are numbers or decimal numbers are automatically converted.

    To define multi-line values use \n instead of line-brakes.

    You can back-reference variables using tokens like this ${ref}, these
    will also expand to evironment variables with optional prefix such
    as ${HOME} or if prefix is "MY_APP" and "MY_APP_LOGS" is in the
    environment then ${LOGS} will be expanded to MY_APP_LOGS value.

    Note: If the variable name is found in the environment with optional
          prefix, the environment value will be used instead, ignoring file.

    DOMAIN=example.com
    ADMIN_EMAIL=admin@${DOMAIN}
    GREETING_TEXT=Hello ${USER}\n\nWelcome to my site
    """
    env = {}

    if isinstance(fileOrStream, str):
        if os.path.exists(fileOrStream):
            with open(fileOrStream) as env_file:
                env = _load(env_file, env_prefix)
        else:
            print(f'Cannot open file "{fileOrStream}"')

    else:
        env = _load(fileOrStream, env_prefix)

    return env


def _load(stream, env_prefix: str) -> dict:
    env = {}

    for line in stream:
        line = line.strip()

        # skip empty lines
        if not line or line[0] == "#":
            continue

        if '=' not in line:
            print('invalid config line:', line)
            continue

        # split
        key, val = line.split('=', 1)

        # overide with env
        if f'{env_prefix}{key}' in os.environ:
            env[key] = os.environ[f'{env_prefix}{key}']
            continue

        # expand references
        start = 0
        while True:
            ref, start = _get_ref(val, start)
            if not ref:
                break

            # find ref in environment or previous vars
            ref_val = None
            if f'{env_prefix}{ref}' in os.environ:
                ref_val = os.environ[f'{env_prefix}{ref}']

            elif ref in os.environ:
                ref_val = os.environ[ref]

            elif ref in env:
                ref_val = env[ref]

            # if we found a value, replace it
            if ref_val:
                val = val.replace('${' + ref + '}', ref_val)
                start += len(ref_val) - (len(ref) + 3)

        # expand multi-line
        val = val.replace('\\n', '\n')

        # check to see if it's number
        if val.isdecimal():
            val = int(val, 10)

        else:
            # try as float
            try:
                val = float(val)
            except ValueError:
                pass

        # save into dict
        env[key] = val

    return env


def _get_ref(val: str, start: int) -> tuple:
    """Get the next reference starting from `start` position"""
    idx = start
    length = len(val)
    in_ref = False
    ref_name = ''

    while idx < length:
        ch = val[idx]
        if in_ref:
            # found end of ref, yeild
            if ch == '}':
                in_ref = False
                if ref_name:
                    return ref_name, idx + 1

            # Ref start inside ref, drop previous and use this one
            elif idx != length and ch == '$' and val[idx + 1] == '{':
                print(f'Unterminated placeholder starting at pos {start} in "{val}"')
                idx += 1
                ref_name = ''

            # nothing special, just add char
            else:
                ref_name += ch

            idx += 1

        # not at the end, and found ref start
        elif idx != length - 1 and ch == '$' and val[idx + 1] == '{':
            in_ref = True
            idx += 2
            ref_name = ''

        # nothing special, just skip
        else:
            idx += 1

    return None, -1
