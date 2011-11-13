# Allows diff branches, e.g.: experimental/staging
BRANCH=${1:-master}
PKGS="nginx python-flup python-rrdtool rrdtool spawn-fcgi"
# Packages setup
sudo bash -xe << EOF || exit 1
  apt-get update
  apt-get -y install $PKGS
EOF

# Create 'bogomon' user, create and directories
REPO=https://raw.github.com/jjo/bogomon/${BRANCH?}
sudo bash -xe << EOF || exit 2
  id -u bogomon || useradd bogomon || exit 1
  mkdir -p /usr/lib/bogomon /var/lib/bogomon /var/run/bogomon
  for f in /etc/nginx/sites-available/bogomon /usr/lib/bogomon/bogomon.fcgi.py /etc/init.d/spawn-fcgi;do
    wget -O \$f $REPO\$f || exit 1
    case \$f in /etc/init.d/*|/usr/lib/*) chmod +x \$f;;esac
  done
  ln -sf ../sites-available/bogomon /etc/nginx/sites-enabled/bogomon
  chown -R bogomon:bogomon /var/lib/bogomon
EOF

# Start the services
sudo bash -xe << 'EOF' || exit 3
  /etc/init.d/spawn-fcgi restart
  /etc/init.d/nginx configtest
  /etc/init.d/nginx status && sudo /etc/init.d/nginx start || sudo /etc/init.d/nginx restart
EOF
