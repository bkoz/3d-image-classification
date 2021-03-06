# Pod Limits

The pod memory limits need to be increased to 16Gi in order to train this model.

Choose a notebook size that provides at least a 16Gi memory limit or
create a custom notebook container size using the configmap provided in the resources directory.

Example

```
oc create -f resources/developer-jupyterhub-sizes.yml
```

Details

```
$ nvidia-smi|grep MiB
              | N/A   42C    P0    28W /  70W |   5060MiB / 15109MiB |      0%      Default |

top - 23:21:06 up  2:31,  0 users,  load average: 2.62, 2.36, 1.89
Tasks:   5 total,   1 running,   4 sleeping,   0 stopped,   0 zombie
%Cpu(s): 12.5 us,  3.0 sy,  0.0 ni, 83.3 id,  0.3 wa,  0.6 hi,  0.4 si,  0.0 st
MiB Mem :  63607.6 total,  31793.1 free,  16616.5 used,  15198.1 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.  47719.1 avail Mem 

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND                                                  
    199 1000740+  20   0   26.9g   8.5g 829204 S 108.3  13.7  10:35.70 python3.8                                                
      1 1000740+  20   0   17136   3308   2932 S   0.0   0.0   0:00.03 start.sh                                                 
    104 1000740+  20   0 2732868 199476  31756 S   0.0   0.3   0:06.77 jupyter-labhub                                           
    162 1000740+  20   0   17396   4064   3320 S   0.0   0.0   0:00.55 sh                                                       
    357 1000740+  20   0   52064   4120   3456 R   0.0   0.0   0:00.00 top 
```
