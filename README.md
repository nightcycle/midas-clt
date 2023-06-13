# midas-clt
A command line tool that automates the set-up and date-management processes for midas analytics.

## initializing
To set-up the analytics first add it to foreman / aftman, then in the console run this command:
```sh
	midas init
```
This should create a script called `midas.yaml` at the root of the workspace. Using a bash console is recommended.

## authorizing
Various credentials are used to authenticate throughout the workflow. Using `midas auth-___` you are able to store those securely on your computer for usage in the future.

### playfab
In order to send data to PlayFab from within Roblox you need to run this command:
```sh
midas auth-playfab
```
It will then prompt you to fill in two inputs:
#### title id
The title id is the 5 letter code associated with the Playfab game being tracked. It can be found in multiple places such as within the url of any page related to the project.

#### dev secret key
The dev secret key is a long set of characters that's stored in the title's settings page. It allows for analytics posts to be authenticated when sent from in-game.

### aad
In order to use python to query to PlayFab you need to create an azure-active-directory app to work as a middleman. This (guide)[https://learn.microsoft.com/en-us/gaming/playfab/features/insights/connectivity/creating-aad-app-for-insights] does a pretty good job, explaining how to set that up. To authorize the AAD app you'll need a client id, a client secret, and a tenant id.

## configuration

## building roblox scripts

### playfab
### aad
#### creating an aad app
#### hooking the app to PlayFab
### roblox

## clean

## download
