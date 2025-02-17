import os.path
from typing import Dict, List

from e3.testsuite.driver.classic import TestAbortWithError

from drivers.base_driver import BaseDriver


class NameResolutionDriver(BaseDriver):
    """
    Test driver to run the ``nameres`` program and check its output.

    The following list documents supported keys (in ``test.yaml``). All keys
    are assumed to be optional unless told otherwise.

    ``input_sources``

        A list of filenames for the source files to process.

    ``charset``

        The name of a string encoding to use when processing files.

    ``project_file``

        A filename for a project file, used to create a project unit provider.

    ``project_path``

        List of directory names (relative to the testsuite root directory)
        to add to the project files lookup path (``GPR_PROJECT_PATH``).

    ``project_vars``

        Name/value mapping for project files external variables.

    ``auto_provider_dirs``

        A list of directory names, used to create an auto unit provider.

    ``imprecise_fallback``

        Boolean (false by default) to trigger implicit fallbacks during name
        resolution.

    ``batch``

        If true, run name resolution on the whole sources (not just the nameres
        pragmas) and only show failures, with no traceback. This is useful to
        check on a big codebase that there are no (new) name resolution
        failures.

    ``preprocesor_data_file``

        Filename for the preprocessor data file.

    ``preprocessor_path``

        List of directories where preprocessor data files can be found.
    """

    perf_supported = True

    def run(self):

        args: List[str] = ["nameres"]
        """
        Arguments to pass to "nameres".
        """

        env: Dict[str, str] = {}
        """
        Additional environment variables for "nameres".
        """

        # Path for project files: make directories from the "project_path" key
        # prioritary and append existing paths from the environment.
        env["GPR_PROJECT_PATH"] = os.path.pathsep.join(
            [
                os.path.join(self.env.root_dir, p)
                for p in self.test_env.get("project_path", [])
            ]
            + os.environ.get("GPR_PROJECT_PATH", "").split(os.path.pathsep)
        )

        # List of source files to process and unit provider
        input_sources = self.test_env.get("input_sources", [])

        project_file = self.test_env.get("project_file", None)
        if project_file:
            args.append(f"-P{project_file}")

        for name, value in sorted(
            self.test_env.get("project_vars", {}).items()
        ):
            args.append(f"-X{name}={value}")

        auto_provider_dirs = self.test_env.get("auto_provider_dirs", None)
        if auto_provider_dirs:
            args.extend(
                "--auto-dir={}".format(d)
                for d in auto_provider_dirs
            )

        # Preprocessor handling
        preprocessor_data_file = self.test_env.get("preprocessor_data_file",
                                                   None)
        preprocessor_path = self.test_env.get("preprocessor_path", [])
        if preprocessor_data_file:
            args.append(f"--preprocessor-data-file={preprocessor_data_file}")
            args.extend(f"--preprocessor-path={d}" for d in preprocessor_path)

        # Various options
        charset = self.test_env.get("charset")
        if charset:
            args.append(f"--charset={charset}")

        if self.test_env.get("imprecise_fallback"):
            args.append("--imprecise-fallback")

        # In batch mode, run name resolution on the whole code base (i.e. not
        # just on nameres-specific pragmas) and display only error messages,
        # not traceback (for test output stability).
        if self.test_env.get("batch"):
            args += ["--all", "--no-traceback"]

            # In perf mode, we need nameres not to print anything
            if not self.perf_mode:
                args.append("--only-show-failures")

        # Add optional explicit list of sources to process
        args += input_sources

        if self.perf_mode:
            self.run_for_perf(argv=args + ["--quiet"], env=env)
        else:
            self.run_and_check(argv=args, memcheck=True, env=env)
