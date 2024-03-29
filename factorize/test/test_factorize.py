import re

from click.testing import CliRunner

from ..factorize import cli
from ..factorize import Context


def test_science():
    spm = 75
    runner = CliRunner()
    result = runner.invoke(
        cli,
        args=['science', '75'],
        catch_exceptions=False,
        obj=Context())

    assert result is not None
    assert result.exit_code == 0

    # expected number of factories for a 75 SPM
    # see https://wiki.factorio.com/Science_pack
    expected_science = {
        'automation-science-pack': 5,
        'logistic-science-pack': 6,
        'military-science-pack': 5,
        'chemical-science-pack': 12,
        'production-science-pack': 7,
        'utility-science-pack': 7,
    }

    for pack, factories in expected_science.items():
        name = pack.replace('-', ' ')
        # regular expression for a line such as
        # 75 automation science pack   ->    5 assembly machine 3
        pattern = rf'^\s*{spm}\s+{name}\s+->\s+{factories} assembly machine 3$'
        match = re.search(pattern, result.output, re.MULTILINE | re.IGNORECASE)
        assert match is not None, f'expected {factories} factories for {pack}'
