PKGS="nginx python-flup python-rrdtool rrdtool spawn-fcgi"

sudo apt-get -y install $PKGS
id -u bogomon || sudo useradd bogomon || exit 1
sudo mkdir -p /usr/lib/bogomon /var/lib/bogomon /var/run/bogomon
REPO=https://raw.github.com/jjo/bogomon/master
sudo wget -O /etc/nginx/sites-available/bogomon $REPO/etc/nginx/sites-available/bogomon || exit 1
sudo ln -sf ../sites-available/bogomon /etc/nginx/sites-enabled/bogomon
sudo wget -O /usr/lib/bogomon/bogomon.fcgi.py $REPO/bogomon.fcgi.py || exit 1
sudo wget -O /etc/init.d/spawn-fcgi $REPO/etc/init.d/spawn-fcgi || exit 1
sudo chmod +x /etc/init.d/spawn-fcgi
sudo /etc/init.d/spawn-fcgi restart
sudo /etc/init.d/nginx configtest || exit 1
sudo /etc/init.d/nginx status && sudo /etc/init.d/nginx start || sudo /etc/init.d/nginx restart
