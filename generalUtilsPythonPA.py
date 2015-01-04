import subprocess


def runCommand(cmd, quiet=False, shellVal=False):
  """
  
   Run a system command formatted as a single string.
   
   quiet    : set to True to prevent command being printed.
   
   shellVal : set to True to execute command through a shell 
              interpreter (allows things like wildcards to be used)

   """
  
  if not quiet:
    print cmd
    
  if shellVal == False:
    # Pass command as a list
    cmd = cmd.split(' ')
    
  try:    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shellVal)
    (stdOut, stdErr) = p.communicate()
    
    if not p.returncode == 0:
      s1 = 'Error running command\n'
      s2 = ' '.join(cmd)
      s3 = 'Standard Error provided:\n' + stdErr
      s4 = 'Standard Out provided:\n' + stdOut
      s = '\n'.join([s1, s2, s3, s4])
      raise Exception(s)
    
    # Success!
    return (stdOut, stdErr)
  
  except Exception as e:
    raise e
    