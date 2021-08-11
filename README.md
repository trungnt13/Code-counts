# Code-counts

Count how many lines of code you had written during your doctoral study.


### Usage

```commandline
coconerd [path_or_url] -cache --clear
```

 ---------------
|Argument | Help|
|---------|-----|
|`path_or_url`| path to local directory or url to github repo, multiple input concatenated by `,`|
|`-cache`| path to cache directory|
|`--clear`|clear all cached source code|

### Example

```commandline
coconerd https://github.com/trungnt13/odin-ai,https://github.com/trungnt13/sisua
```

```text
Processing: 377files [00:00, 5727.62files/s]
https://github.com/trungnt13/sisua
 for_loop  : 891
 while_loop: 3
 if_cond   : 1199
 func_def  : 422
 class_def : 43
 lines     : 16744
https://github.com/trungnt13/odin-ai
 for_loop  : 3841
 while_loop: 57
 if_cond   : 6130
 func_def  : 3260
 class_def : 575
 lines     : 83649
---Total:
 for_loop  : 4732
 while_loop: 60
 if_cond   : 7329
 func_def  : 3682
 class_def : 618
 lines     : 100393
```
