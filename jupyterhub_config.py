# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()


# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
# Spawn containers from this image
# c.DockerSpawner.image = os.environ['DOCKER_NOTEBOOK_IMAGE']
# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
# spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
# Connect containers to this Docker network
network_name = os.environ['DOCKER_NETWORK_NAME']
# c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })
c.DockerSpawner.use_internal_ip = True
# c.DockerSpawner.internal_hostname = '0.0.0.0'
c.DockerSpawner.network_name = network_name
# c.DockerSpawner.network_name = "bridge"
c.DockerSpawner.host_ip = "0.0.0.0"
# c.DockerSpawner.ip = "0.0.0.0"
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
# c.DockerSpawner.remove_containers = True
c.DockerSpawner.remove = True
c.DockerSpawner.default_url = '/lab'

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = 'jupyterhub'
# c.JupyterHUb.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 9000

# TLS config
c.JupyterHub.port = 10001
# c.JupyterHub.ssl_key = os.environ['SSL_KEY']
# c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with GitHub OAuth
# c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
# c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')

# c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
#    'jupyterhub_cookie_secret')

c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=os.environ['POSTGRES_DB'],
)

# Whitlelist users and admins
# c.LocalAuthenticator.create_system_users=True
c.Authenticator.allowed_users = whitelist = set()
c.JupyterHub.authenticator_class = "dummy"
c.JupyterHub.admin_access = True
c.Authenticator.delete_invalid_users = True
c.Authenticator.admin_users = whitelist
pwd = os.path.dirname(__file__)
users_info = dict()
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        # in case of newline at the end of userlist file
        if len(parts) >= 1:
            name = parts[0]
            whitelist.add(name)
            if len(parts) >= 2:
                image = parts[1]
                users_info[name] = image

def get_image(spawner):
    user_name = spawner.user.name
    if user_name in users_info:
        spawner.image = users_info[user_name]
    else:
        spawner.image = os.environ['DOCKER_NOTEBOOK_IMAGE']

c.DockerSpawner.pre_spawn_hook = get_image
