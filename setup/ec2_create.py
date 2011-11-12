#!/usr/bin/env python
""" jjo is tired (1am) """
import boto, os, time, telnetlib, socket

IMG = 'ami-29f43840' ## ubuntu 11.10 32bit
KEY = 'ec2-keypair'  ## ssh pubkey to be planted into the instance

def start():
  """ jjo is tired (1am) """
  print 'Starting EC2 with image {0}'.format(IMG)
  ec2_conn = boto.connect_ec2()
  images = ec2_conn.get_all_images(image_ids=['ami-29f43840'])
  reserv = images[0].run(1, 1, 'ec2-keypair')
  instance = reserv.instances[0]
  time.sleep(10)
  while not instance.update() == 'running':
    time.sleep(5)
  while not instance.dns_name:
    instance.update()
    time.sleep(1)
  print 'Started the hostname: {0}'.format(instance.dns_name)
  return instance.dns_name

def run(host, cmd):
  """ jjo is tired (1am) """
  i = 30
  while i > 0:
    i = i - 1
    try:
      telnetlib.Telnet(host, 22)
      break
    except socket.error:
      time.sleep(5)
  os.system('ssh ubuntu@%s "%s"' % (host, cmd))

HOST = start()
run(HOST, "wget -O- https://raw.github.com/jjo/bogomon/master/setup/ec2-setup.sh |bash -x")
print "Ready at:\nhttp://%s:%d/stats.html \o/" % (HOST, 8000)
