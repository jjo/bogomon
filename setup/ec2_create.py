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

def start(ec2_img, ec2_keypair):
  """ Connect to EC2, spawn an instance from ec2_img, attaching
      ec2_keypair to it """
  print 'Starting EC2 with image {0}'.format(ec2_img)
  ec2_conn = boto.connect_ec2()
  images = ec2_conn.get_all_images(image_ids=[ec2_img])
  reserv = images[0].run(1, 1, ec2_keypair)
  instance = reserv.instances[0]
  time.sleep(10)
  while not instance.update() == 'running':
    time.sleep(5)
  while not instance.dns_name:
    instance.update()
    time.sleep(1)
  print 'Started the hostname: {0}, instance: {1}'.format(
      instance.dns_name, instance)
  return instance

def run(ssh_pubk, host, cmd):
  """ Run: ssh ubunbu@... at just created host, to complete its setup """
  for _ in xrange(30):
    try:
      telnetlib.Telnet(host, 22)
      break
    except socket.error:
      time.sleep(5)
  # sshd already listening, but allow some time for key propagation
  time.sleep(5)
  if ssh_pubk:
    ssh_pubk = "-i %s" % ssh_pubk
  retval = os.system('set -x;ssh -v %s ubuntu@%s "%s"' % (
    ssh_pubk, host, cmd))
  if retval != 0:
    raise SystemExit

def main():
  """ main(), what else """
  # Override default args with argv[1:] ,
  # also IMO easier for validation instead of len(sys.argv)
  args = [None, None, BRANCH]
  for i, val in enumerate(sys.argv[1:]):
    args[i] = val
  if args[0] is None:
    sys.exit('Usage: %s <ec2_keypair> [ssh_priv_key_filepath] [branch]\n')

  ec2_keypair, ec2_sshpubk, branch = args
  if ec2_sshpubk and not os.path.isfile(ec2_sshpubk):
    sys.exit('Error: file %s doesnt exist' % ec2_sshpubk)

  instance = start(IMG, ec2_keypair)

  try:
    run(ec2_sshpubk, instance.dns_name, (
        'wget https://raw.github.com/jjo/bogomon/%s/setup/ec2-setup.sh;'
        'bash -x ec2-setup.sh %s') % (branch, branch))
  except SystemExit:
    print "Failed ssh setup, destroying {0}".format(instance)
    instance.stop()
    sys.exit(1)

  print "Hopefully ready at:\nhttp://{0}:{1}/stats.html\ninstance: {2}".format(
      instance.dns_name, BOGOMON_PORT, instance)

if __name__ == '__main__':
  main()

