import redis
import git
import os
import subprocess
from werkzeug.utils import secure_filename

local_recipes_dir = os.getenv('RECIPES_HOME', './recipes')
local_checkout_dir = os.getenv('CHECKOUT_HOME', './checkout')
local_artifacts_dir = os.getenv('ARTIFACTS_HOME', './artifacts')

def wrap_console(fn):
    def new_fn(*args, **kwargs):
       r = redis.Redis()
       channel = args[0] + ".console"
       console = lambda msg: r.publish(channel, msg)
       kwargs['console'] = console
       try:
           fn(*args, **kwargs)
       except Exception as e:
            console("Failed: " + str(e))
       finally:
           console("EOF")
       return
    
    return new_fn

@wrap_console
def start_job(name, url, branch_name, path, recipe, console=None):
    
    console("Starting job %s..." % name)
    
    #sanitize recipe...
    recipe_path = recipe.replace("..", "_")
    
    recipe = os.path.abspath(local_recipes_dir) + "/"+ recipe_path + "/run.sh"
    if not os.path.exists(recipe):
        raise Exception("Recipe doesn't exist: " + recipe)
    
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
    
    recipe = recipe + " " + os.path.abspath(checkout_dir) + " " + os.path.abspath(output_dir)
    console("Starting: " + recipe)
    process = subprocess.Popen(recipe, shell=True, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, ''):
       console(line.rstrip())
    


