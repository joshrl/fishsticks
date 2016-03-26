import redis
import git
import os
import subprocess
import config

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
def start_job(name, url, branch_name, recipes, console=None):
    
    console("Starting job %s..." % name)
    
    # make checkout base dir if it doesn't exist.
    if not os.path.exists(config.checkout_base_dir):
        os.makedirs(config.checkout_base_dir)
    
    artifacts_dir = os.path.join(config.artifacts_base_dir, name)
    if not os.path.exists(artifacts_dir):
        os.makedirs(artifacts_dir)
    
    checkout_dir = os.path.join(config.checkout_base_dir, name)
    
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
    
    for recipe in recipes:
    
        #sanitize recipe
        recipe_sanitized = recipe.replace("..", "").replace("~", "")
    
        recipe_path = os.path.abspath(config.recipes_base_dir) + "/"+ recipe_sanitized + "/run.sh"
        if not os.path.exists(recipe_path):
            raise Exception("Recipe doesn't exist: " + recipe)
        
        recipe_with_args = recipe_path + " " + os.path.abspath(checkout_dir) + " " + os.path.abspath(artifacts_dir)
        console("Starting: " + recipe)
        process = subprocess.Popen(recipe_with_args, shell=True, stdout=subprocess.PIPE)
        for line in iter(process.stdout.readline, ''):
           console(line.rstrip())
    


