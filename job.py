import redis
import git
import os
import subprocess

local_scripts_dir = os.getenv('SCRIPTS_HOME', './scripts')
local_checkout_dir = os.getenv('CHECKOUT_HOME', './checkout')
local_artifacts_dir = os.getenv('ARTIFACTS_HOME', './artifacts')

def wrap_console(fn):
    def new_fn(*args, **kwargs):
       r = redis.Redis()
       channel = args[0] + ".console"
       console = lambda msg: r.publish(channel, msg)
       kwargs['console'] = console
       try:
           result = fn(*args, **kwargs)
       finally:
           console("EOF")
       return result
    
    return new_fn

@wrap_console
def start_job(name, url, branch_name, path, script, console=None):
    
    console("Starting job %s..." % name)
        
    script = os.path.abspath(local_scripts_dir) + "/"+ script + "/run.sh"
    if not os.path.exists(script):
        console("Script doesn't exist: " + script)
        raise
    
    if not os.path.exists(local_checkout_dir):
        os.makedirs(local_checkout_dir)
    
    output_dir = os.path.join(local_artifacts_dir, name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    checkout_dir = os.path.join(local_checkout_dir, name)
    
    try:
        repo = git.Repo(checkout_dir)
        console("Updating repo...")
    except:
        console("Cloning repo...")
        repo = git.Repo.clone_from(url, checkout_dir, branch=branch_name)
    
    origin = repo.remotes.origin
    origin.fetch()
    
    try:
        branch = repo.heads[branch_name]    
    except IndexError:
        remote_branch = origin.refs[branch_name]
        branch = repo.create_head(branch_name, remote_branch).set_tracking_branch(remote_branch)
    
    branch.checkout()
    origin.pull()
    
    script = script + " " + os.path.abspath(checkout_dir) + " " + os.path.abspath(output_dir)
    console("Starting: " + script)
    process = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, ''):
       console(line.rstrip())
    


