import io
import os

from ironsigma import env


def test_simple_load():
    config_string = io.StringIO("""
APP_USER = foo
APP_EMAIL =foo@example.com

# Settings
APP_RES= 2.5
APP_PORT  =   6900""")

    config = env.load(config_string)

    assert config['APP_USER'] == 'foo'
    assert config['APP_EMAIL'] == 'foo@example.com'
    assert config['APP_PORT'] == 6900
    assert config['APP_RES'] == 2.5


def test_bad_config():
    config_string = io.StringIO("foo")
    config = env.load(config_string)


def test_prioritize_env():
    home = os.environ['HOME']
    config_string = io.StringIO("HOME=/foo")
    config = env.load(config_string)

    assert config['HOME'] == home


def test_load_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("===", dir_path)

    config = env.load(dir_path + "/res/env_test")

    assert config['DB_NAME'] == 'mydb'
    assert config['DB_USER'] == 'joe'
    assert config['DB_PASS'] == 's3cr3t'


def test_ref_var():
    config_string = io.StringIO("""
DOMAIN = example.com
TOKEN = ${str}
EMPTY = ${}
ADMIN_EMAIL = admin@${DOMAIN}""")

    config = env.load(config_string)

    assert config['ADMIN_EMAIL'] == "admin@example.com"
    assert config['TOKEN'] == "${str}"
    assert config['EMPTY'] == "${}"


def test_ref_environment_no_prefix_match():
    home = os.environ['HOME']
    config_string = io.StringIO("APP_HOME=${HOME}/app")

    config = env.load(config_string, env_prefix="MY_APP_")

    assert config['APP_HOME'] == f"{home}/app"


def test_ref_environment_prefix_match():
    home = os.environ['HOME']
    config_string = io.StringIO("APP_HOME=${ME}/app")

    config = env.load(config_string, env_prefix="HO")

    assert config['APP_HOME'] == f"{home}/app"


def test_unterminated_ref():
    home = os.environ['HOME']
    config_string = io.StringIO("PAGE=${DOM/${HOME}")

    config = env.load(config_string)

    assert config['PAGE'] == f"${{DOM/{home}"


def test_missing_file():
    config = env.load("foo.env")

    assert not config
