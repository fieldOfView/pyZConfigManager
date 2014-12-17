pyZConfigManager
================

ZOCP graph configuration management scripts based on pyZOCP

Stores the ZOCP graph (nodes, capabilities, subscriptions) into a file.
Restores node capabilities (values) and subscriptions from a file.

Installing
----------

pyZConfigManager is based on a special branch of ZOCP, which will be 
merged in the near future. For now you need the special branch.
Depending on wheter you installed ZOCP through git, or with pip,
do the following. Note that you may also need to update pyre,
since that changed a lot over the past few weeks.

If you previously installed ZOCP through git, do the following
in the folder you cloned pyZOCP into:
```
> git remote add fieldofview https://github.com/fieldOfView/pyZOCP.git
> git checkout -b feature_subscribe
> git pull fieldofview feature_subscribe
```
Now you should be able to use ZOCP as before, but you will notice
some new examples in the examples folder. If you want to go back
to the "normal" version of ZOCP without my changes, do the
following:
```
> git checkout master
```

If you previously used pip to install ZOCP, upgrade to my special
branch like so:
```
> sudo pip3 install -- upgrade https://github.com/fieldOfView/pyZOCP/archive/feature_subscribe.zip
```
Switching back to the normal ZOCP is done as follows:
```
> sudo pip3 install -- upgrade https://github.com/z25/pyZOCP/archive/master.zip
```

Next, clone pyZConfigManager somewhere:
```
> git clone https://github.com/fieldOfView/pyZConfigManager.git
```
Or just download it here:
https://github.com/fieldOfView/pyZOSC/archive/master.zip

