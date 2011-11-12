PKGS="nginx python-flup python-rrdtool rrdtool spawn-fcgi"

sudo apt-get -y install $PKGS
id -u bogomon || sudo useradd bogomon || exit 1
sudo mkdir -p /usr/lib/bogomon /var/lib/bogomon
REPO=https://raw.github.com/jjo/bogomon/master
sudo wget --directory-prefix=/etc/nginx/sites-available $REPO/etc/nginx/sites-available/bogomon || exit 1
sudo ln -sf ../sites-available/bogomon /etc/nginx/sites-enable/bogomon
sudo wget --directory-prefix=/usr/lib/bogomon $REPO/web/bogomon.fcgi.py || exit 1
sudo wget --directory-prefix=/etc/init.d -O spawn-fcgi $REPO/etc/init.d-spawn-fcgi || exit 1
sudo chmod +x /etc/init.d/spawn-fcgi
sudo /etc/init.d/spawn-fcgi start
/etc/init.d/nginx configtest || exit 1
/etc/init.d/nginx reload
