
## Python 

**Initialization**

* init service: 
    ```bash 
    cd ~/GPS # be in the root of the repo
    uv init --app services/my-service
    ```
* init package:
    ```bash 
    cd ~/GPS # be in the root of the repo
    uv init --lib packages/my-package
    ```
---
**packages vs services**

packages should be the stuff that are not exposed over APIs like HTTP, gRPC, ... etc.  

**installing stuf for a package or a service**

```bash 
cd ~/GPS # be in the root of the repo
uv add --package my-work-dir numpy
```