#!/usr/bin/env python3
import datetime
import subprocess
from distutils.version import StrictVersion


def main():
    git_clean = subprocess.check_output(
        "git status --porcelain", shell=True, universal_newlines=True,
    ).strip()
    if git_clean:
        raise RuntimeError("Error, git workspace is not clean: \n{0}".format(git_clean))

    current_version = subprocess.check_output(
        "poetry version", shell=True, universal_newlines=True
    ).replace("dnsrobocert ", "")

    print("Current version is: {0}".format(current_version))
    print("Please insert new version:")
    new_version = str(input())

    if StrictVersion(new_version) <= StrictVersion(current_version):
        raise RuntimeError(
            "Error new version is below current version: {0} < {1}".format(
                new_version, current_version
            )
        )

    try:
        with open("CHANGELOG.md") as f:
            changelog = f.read()

        today = datetime.datetime.today()
        changelog = changelog.replace(
            "## master - CURRENT\n",
            """\
## master - CURRENT

## {0} - {1}
""".format(
                new_version, today.strftime("%d/%m/%Y")
            ),
        )

        with open("CHANGELOG.md", "w") as f:
            f.write(changelog)

        subprocess.check_call("poetry version {0}".format(new_version), shell=True)
        subprocess.check_call("poetry run isort -rc src test utils", shell=True)
        subprocess.check_call("poetry run black src test utils", shell=True)

        subprocess.check_call(
            'git commit -a -m "Version {0}"'.format(new_version), shell=True
        )
        subprocess.check_call("git tag v{0}".format(new_version), shell=True)
        subprocess.check_call("git push --tags", shell=True)
        subprocess.check_call("git push", shell=True)

    except subprocess.CalledProcessError as e:
        print("Error detected, cleaning state.")
        subprocess.call("git tag -d v{0}".format(new_version), shell=True)
        subprocess.check_call("git reset --hard", shell=True)
        raise e


if __name__ == "__main__":
    main()
