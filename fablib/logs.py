from fabric.api import sudo


def site_logs(site):
    """
    Show logs for a site.
    Usage:
        fab appbalancer site_logs:sitename
    """
    sudo("echo 'NGINX ######' && sudo tail /var/log/nginx/error.log && \
          echo 'SUPERVISOR ######' && tail /var/log/supervisor/{0}.log && \
          echo 'GUNICORN ######' && tail /var/log/gunicorn/{0}.log".format(site))
