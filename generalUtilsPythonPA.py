import subprocess


def runCommand(cmd, quiet=False, shellVal=False):
  """
   Run a system command formatted as a single string.
   quiet    : set to True to prevent command being printed.
   shellVal : set to True to execute command through a shell 
              interpreter (allows things like wildcards to be used)
   """


  if shellVal == False:
    # Pass command as a list
    cmd = cmd.split(' ')
    cmd = filter(None, cmd)

  if not quiet:
    print ' '.join(cmd)

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

def chunkIndices(N, K):

    """

    Split up N indices,  i.e. the the indices

      0, 1, ... , N-1

    as evenly as possible into K chunks.

    There will be K intervals, indexed 0, 1, ... , K-1

    Each chunk will have 1+N/K indices or N/K indices.


    Inputs:

    N: The number of indices
    K: The number of chunks

    Returns:

    A list of paired tuples, each pair gives the first and last indices for a
    chunk of indices.

     Example
     For 19 indices among three, make a 7,6,6 split:

     1 1 1 1 1 1 1 2 2 2  2  2  2  3  3  3  3  3  3
     0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18

     Start indices: 0 = 0x7, 7=1x7, 13=1x7+1x6


    """

    N_mod_K = N % K


    # Chunks come in two sizes, N/K and 1+N/K
    smallChunk = N/K

    indexChunks = []

    for int_id in range(K):
        if int_id <= N_mod_K:
            startIndex = int_id * (1 + smallChunk)
        else:
            startIndex = N_mod_K * (1+ smallChunk) + (int_id - N_mod_K) * smallChunk

        if int_id < N_mod_K:
            endIndex = startIndex + smallChunk
        else:
            endIndex = startIndex + smallChunk - 1

        indexChunks.append((startIndex, endIndex))


    return indexChunks



