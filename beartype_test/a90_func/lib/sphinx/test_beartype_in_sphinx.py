#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional beartype-in-Sphinx tests.**

This submodule functionally tests the :func:`beartype.beartype` decorator to
conditionally reduce to a noop when the active Python interpreter is building
documentation for the third-party :mod:`sphinx` package.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_unless_package

# ....................{ TESTS                             }....................
#FIXME: *NON-IDEAL.* This test manually invokes Sphinx internals. Instead, this
#test should be fundamentally refactored from the ground up to leverage the
#public (and increasingly documented) "sphinx.testing" subpackage.
@skip_unless_package('sphinx')
def test_beartype_in_sphinx(tmp_path) -> None:
    '''
    Functional test validating that the :func:`beartype.beartype` decorator
    conditionally reduces to a noop when the active Python interpreter is
    building documentation for the third-party :mod:`sphinx` package.

    To do so, this test externally runs the ``sphinx-build`` command against a
    minimal-length Sphinx document tree exercising all known edge cases.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this unit
        test, created in the base temporary directory.
    '''

    # ..................{ SPHINX-BUILD                      }..................
    # Defer heavyweight imports.
    from beartype import beartype
    from beartype._util.mod.lib.utilsphinx import (
        _SPHINX_AUTODOC_SUBPACKAGE_NAME)
    from beartype_test.util.cmd.pytcmdexit import is_success
    from beartype_test.util.path.pytpathtest import (
        get_test_func_data_lib_sphinx_dir)
    from sys import modules as modules_imported_name

    # Entry-point (i.e., pure-Python function accepting a list of zero or more
    # command-line arguments) underlying the external "sphinx-build" command.
    from sphinx.cmd.build import main as sphinx_build

    # List of all command-line options (i.e., "-"-prefixed strings) to be
    # effectively passed to the external "sphinx-build" command.
    #
    # Note this iterable *MUST* be defined as a list rather than tuple. If a
    # tuple, the function called below raises an exception. Hot garbage!
    SPHINX_OPTIONS = [
        # Avoid caching data into a "{OUTPUTDIR}/.doctrees/" subdirectory.
        # Although typically advisable, "{OUTPUTDIR}" is an ignorable temporary
        # test-specific directory deleted immediately after completion of this
        # test. Caching data would only needlessly consume time and space.
        '-E',

        # Enable the HTML mode, rendering HTML-specific documentation files.
        # Although technically arbitrary, this is the typical default mode.
        '-b', 'html',

        # Treat non-fatal warnings as fatal errors. This is *CRITICAL.* By
        # default, Sphinx insanely emits non-fatal warnings for fatal "autodoc"
        # errors resembling:
        #     WARNING: autodoc: failed to import module 'beartype_sphinx'; the following exception was raised:
        #     No module named 'beartype_sphinx'
        '-W',
    ]

    # List of all command-line arguments (i.e., non-options) to be effectively
    # passed to the external "sphinx-build" command.
    #
    # Note this iterable *MUST* be defined as a list rather than tuple. If a
    # tuple, the function called below raises an exception. Steaming trash!
    SPHINX_ARGUMENTS = [
        # Absolute or relative dirname of a test-specific subdirectory
        # containing a sample Sphinx structure exercising edge cases in the
        # @beartype decorator.
        str(get_test_func_data_lib_sphinx_dir()),
        # Absolute or relative dirname of a test-specific temporary directory
        # to which Sphinx will emit ignorable rendered documentation files.
        str(tmp_path),
    ]

    # Run "sphinx-build" to build documentation for this fake project.
    sphinx_build_exit_code = sphinx_build(SPHINX_OPTIONS + SPHINX_ARGUMENTS)

    # Assert that "sphinx-build" successfully builds documentation for this
    # fake project *WITHOUT* raising an exception.
    assert is_success(sphinx_build_exit_code), (
        f'"sphinx-build" exit code {sphinx_build_exit_code} != 0.')

    # ..................{ VALIDATION                        }..................
    def thou_art_there() -> str:
        '''
        Arbitrary callable *not* decorated by the :func:`beartype.beartype`
        decorator intentionally annotated by one or more arbitrary unignorable
        type hints to prevent that decorator from silently reducing to a noop.
        '''

        return 'From which they fled recalls them'

    # That callable decorated by @beartype.
    thou_art_there_beartyped = beartype(thou_art_there)

    # Assert @beartype decorated that callable with runtime type-checking
    # rather than erroneously reducing to a noop.
    assert thou_art_there_beartyped is not thou_art_there

    # ..................{ OPTIMIZATION                      }..................
    # Crudely unimport the Sphinx "autodoc" extension. Doing so optimizes
    # subsequent invocations of the @beartype decorator by reducing the
    # beartype._util.mod.lib.utilsphinx.is_sphinx_autodocing() tester
    # internally called by that decorator from an O(n) test with non-negligible
    # constants to an O(1) test with negligible constants.
    del modules_imported_name[_SPHINX_AUTODOC_SUBPACKAGE_NAME]
