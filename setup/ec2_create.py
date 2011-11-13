#!/usr/bin/env python
""" Spawn an EC2 instance, populating according with:
    https://raw.github.com/jjo/bogomon/<branch>/setup/ec2-setup.sh
    , which is essentially an ubuntu 32bits
    + nginx
    + spawn-fcgi running bogomon.fcgi.py, which does:
      - periodic cpu usage collection into RRD file
      - generate html+png stats

"""
import boto, os, time, telnetlib, socket, sys

IMG = 'ami-6936fb00' ## ubuntu 10.04 32bit, small, us-east-1
BOGOMON_PORT = 8000  ## only used for the final "informational" message
BRANCH = 'master'    ## potentially allows for e.g. 'staging', 'experimental'

class EC2bogo():
  """ Encapsulates EC2 instance creation and cmd running """
  def __init__(self, ec2_img, ec2_keypair, ssh_privk, branch):
    self.ec2_img = ec2_img
    self.ec2_keypair = ec2_keypair
    if ssh_privk and not os.path.isfile(ssh_privk):
      sys.exit('Error: file %s doesnt exist' % ssh_privk)
    self.ssh_privk = ssh_privk
    self.branch = branch
    self.instance = None

  def start(self):
    """ Connect to EC2, spawn an instance from ec2_img, attaching
        ec2_keypair to it """
    print 'Starting EC2 with image {0}'.format(self.ec2_img)
    ec2_conn = boto.connect_ec2()
    images = ec2_conn.get_all_images(image_ids=[self.ec2_img])
    reserv = images[0].run(1, 1, self.ec2_keypair)
    self.instance = reserv.instances[0]
    time.sleep(10)
    while not self.instance.update() == 'running':
      time.sleep(5)
    while not self.instance.dns_name:
      self.instance.update()
      time.sleep(1)
    print 'Started the hostname: {0}, instance: {1}'.format(
        self.instance.dns_name, self.instance)

  def run(self, cmd):
    """ Run: ssh ubunbu@... at just created host, to complete its setup """
    for _ in xrange(30):
      try:
        telnetlib.Telnet(self.instance.dns_name, 22)
        break
      except socket.error:
        time.sleep(5)
    # sshd already listening, but allow some time for key propagation
    time.sleep(5)
    if self.ssh_privk:
      ssh_i = '-i %s' % self.ssh_privk
    else:
      ssh_i = ''

    retval = os.system('set -x;ssh -v %s ubuntu@%s "%s"' % (
      ssh_i, self.instance.dns_name, cmd))

    if retval != 0:
      print 'Failed ssh setup, destroying {0}'.format(self.instance)
      self.instance.stop()
      raise SystemExit  ### 

def main():
  """ main(), what else """
  # Override default args with argv[1:] ,
  # also IMO easier for validation instead of len(sys.argv)
  args = [None, None, BRANCH, IMG]
  for i, val in enumerate(sys.argv[1:]):
    args[i] = val
  if args[0] is None:
    sys.exit('Usage: %s <ec2_keypair> [ssh_priv_key_filepath] [branch]\n')

  ec2_keypair, ssh_privk, branch, ec2_image = args
  try:
    ec2_instance = EC2bogo(ec2_image, ec2_keypair, ssh_privk, branch)
    ec2_instance.start()
    ec2_instance.run((
          'wget https://raw.github.com/jjo/bogomon/%s/setup/ec2-setup.sh;'
          'bash -x ec2-setup.sh %s') % (branch, branch))
    print ('Hopefully ready at:\n'
           'http://{0}:{1}/stats.html\ninstance: {2}'.format(
             ec2_instance.instance.dns_name, BOGOMON_PORT,
             ec2_instance.instance))
  except SystemExit:
    sys.exit(1)

if __name__ == '__main__':
  main()

