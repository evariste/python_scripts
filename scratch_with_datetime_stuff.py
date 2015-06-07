
# coding: utf-8

# In[19]:

import datetime
import calendar
monthNums = {v: k for k,v in enumerate(calendar.month_abbr)}


# In[41]:

# File with dates in standard format,
# i.e.
# Thu 21 May 2015 09:58:49 BST

timeFile = 'timings-hpc-kcl.txt'
f = open(timeFile)
alltimes = []

for line in f:
    s = line[:-1]
    s = s.split(' ')
    y = int(s[6])
    m = monthNums[s[1]]
    d = int(s[3])
    ts = map(int, s[4].split(':'))
    dt = datetime.datetime(y, m, d, ts[0], ts[1], ts[2])
    alltimes.append(dt)
    print dt
    
f.close()


# In[42]:

for i in range(0, len(alltimes), 2):
    print i, alltimes[i], alltimes[i+1], ' = ', alltimes[i+1] - alltimes[i]


# In[18]:




# In[17]:




# In[ ]:



