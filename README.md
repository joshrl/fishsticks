


# Fishsticks

Fishsticks is just what the world needs: [yet another Continuous Integration server](https://en.wikipedia.org/wiki/Comparison_of_continuous_integration_software). 

Actually, Fishsticks is nothing more than a very simple mechanism to run jobs on-demand or when changes are detected in a git repository. It's quite bland and not very extra-ordinary, which is exactly the point. C.I. should be dull and straight forward - you should save your brain power for more interesting things like building software. 

Fishsticks is currently in development and not really ready for primetime, but check back in a while or get in touch if you have ideas and thoughts.

# Goals

- [ ] One line installation
- [ ] Run jobs on-demand with a single curl command with < 5 configuration parameters.
- [ ] Flip a switch to schedule jobs to happen on commit.
- [ ] Fully traceable output and artifacts
- [ ] Special attention to make things run smoothly on OSX and for the sticky task of doing CI/CD for iOS and Android mobile projects.  
- [ ] A nice set of ~20-30 recipes that handle many common CI tasks for a couple of common platforms
- [ ] Pluggable architecture for doing all the other stuff


# Hacking Notes

Fishsticks is written in python and requires Redis.

Until we get the whole thing settled, here are some notes:

Install redis, e.g.:

	$ brew install redis

Install requirement with pip:

	$ pip install -r requirements.txt

Run locally:

	(venv)$ honcho start

