import subprocess


def runCommand(cmd, quiet=False):
  # Run a system command formatted as a single string.
  if not quiet:
    print cmd
    
  cmd = cmd.split(' ')
  try:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdOut, stdErr) = p.communicate()
    if not p.returncode == 0:
      print 'Error running command', ' '.join(cmd)
      print "Standard Error provided:"
      print stdErr
      return (None,None)
    return (stdOut, stdErr)
  except Exception as e:
    print 'Error raised of type ', e.__class__
    print 'Running command: ', ' '.join(cmd)
    print e.message
    return (None,None)
    