import pytest

import cr as cr


def test_replace_token():
    str = 'hello, {{x}}'
    str = cr.replace_token(str, '{{x}}', 'Roger')
    assert str == 'hello, Roger'


def test_add_command_line_args_separate():
    cmd_line = 'cmdline arg0={{0}} arg1={{1}} arg2={{2}} arg0={{0}}'
    args = ['crosby', 'stills', 'nash']
    created_cmd_line = cr.add_cmdline_args(cmd_line, args)
    assert 'cmdline arg0=crosby arg1=stills arg2=nash arg0=crosby' == \
           created_cmd_line


def test_add_command_line_args_separate_missing_one_arg():
    cmd_line = 'cmdline arg0={{0}} arg1={{1}} arg2={{2}} arg0={{0}}'
    args = ['crosby', 'stills']
    created_cmd_line = cr.add_cmdline_args(cmd_line, args)
    assert 'cmdline arg0=crosby arg1=stills arg2= arg0=crosby' == \
           created_cmd_line


def test_add_command_line_args_separate_missing_one_token():
    cmd_line = 'cmdline arg0={{0}} arg1={{1}}'
    args = ['crosby', 'stills', 'nash']
    created_cmd_line = cr.add_cmdline_args(cmd_line, args)
    assert 'cmdline arg0=crosby arg1=stills' == \
           created_cmd_line


def test_add_command_line_arg_as_single_string():
    cmd_line = 'myls {{args}}'
    args = ['-l', '-n']
    created_cmd_line = cr.add_cmdline_args(cmd_line, args)
    assert 'myls -l -n' == \
           created_cmd_line

    # def test_upper(self):
    #     self.assertEqual('foo'.upper(), 'FOOX')

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


# if __name__ == '__main__':
