# python_bwapi_mirror_wrapper
Wrap Java BWAPI with stubs in python to support jython bots

I am making a BroodWar bot in jython. I was getting annoyed that my IDE had no idea what the underlying java api had.
This project creates a shallow copy of the java api. It's just smart enough to help my IDE do auto complete. 
An if else around every class makes sure that the python wrapper is actually removed from the picture at run time. This ensures that even if something is wrong with the wrapper it won't interfere with execution. I only want the wrapper for edit time help anyways.

## To Use
Copy the bwapi_mirror_wrapper folder into your IDE's python path. 

## TODO
Wrap some return types better ( Right now I only bother with the types made by bwapi, I should also wrap things like int)
