from setuptools import setup, find_packages
import os

# -*- Requirements -*-


def _strip_comments(l):
    return l.split('#', 1)[0].strip()


def _pip_requirement(req):
    if req.startswith('-r '):
        _, path = req.split()
        return reqs(*path.split('/'))
    return [req]


def _reqs(*f):
    return [
        _pip_requirement(r) for r in (
            _strip_comments(l) for l in open(
                os.path.join(os.getcwd(), *f)).readlines()
        ) if r]


def reqs(*f):
    """Parse requirement file.
    Example:
        reqs('default.txt')          # requirements/default.txt
        reqs('extras', 'redis.txt')  # requirements/extras/redis.txt
    Returns:
        List[str]: list of requirements specified in the file.
    """
    return [req for subreq in _reqs(*f) for req in subreq]

setup(
    name="ecs-ansible-env",
    version="0.0.1.2",
    packages=find_packages(),
    url="https://github.com/mwaaas/ecs_ansible_env_file",
    install_requires=reqs("install_requires.txt"),
    include_package_data=True,
    license="",
    author="mwaaas",
    author_email="francismwangi152@gmail.com",
    description="Package used to mimic env files in docker compose",
)