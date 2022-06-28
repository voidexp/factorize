from .factorize import cli
from .factorize import Context


if __name__ == '__main__':
    context = Context()
    cli(obj=context)  # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
