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
Upon initializing, a file named "midas.yaml" will appear in your workspace. This is what each aspect of it means and how you can configure it to fit your project.

### build
This tool builds various scripts to be loaded into the target game.

#### midas_package_rbx_path
This is the roblox environment path to the Midas wally package.

#### client_boot_script_path
This is where you want the client boot script to be generated. It will never need to be referenced by another script, however it will need to be somewhere in the client.

#### shared_state_tree_path
This is where the state is exported into a type-safe tree of trackers that can then be called to pass a player + solver function to the relevant state.

#### shared_event_tree_path
This is where the event is exported into a type-safe tree of trackers that can be fired by scripts, passing extra information if relevant.

#### server_boot_script_path
This is where you want the server boot script to be generated. It will never need to be referenced by another script, however it will need to be somewhere in ServerScriptService due to it containing sensitive information.

### version
This is the game version that will be attached to events.

#### major
Reserved for major changes to the game.

#### minor
Reserved for updates to the game.

#### patch
Reserved for fixes to the game.

#### hotfix
Reserved for emergency fixes to the game.

### monetization
Allows for the encoding and easy tracking of purchases.

#### products
```yaml
product_a: 12345
product_b: 67890
```

#### gamepasses
```yaml
gamepass_a: 12345
gamepass_b: 67890
```

#### id

##### group_id
The group that owns the place.

##### place_id
The place in question.

#### interval
The number of minutes between snapshots, GitHub actions have a lower limit of 5 minutes.

#### branch
The branch you want the data sent to - typically not the main one due to the frequency of commits. Since its set-up is a one-time-thing midas does not create the branch manually, so be sure to do that to avoid errors.

#### out_path
The directory path under the branch it will store the data under - useful if you intend to merge the branch into main on occasion for processing.

### tree
This defines the organization and storage of data within the game. Due to rigid encoding standards for the sake of high efficiency, you can add new stuff later, but once something is added you can't remove it without corrupting the decoding process for older data. 

#### basic data
If you want to store basic data then you can. Include a "?" at the end if the data is sometimes null. 
##### string
Any text.
##### boolean
Any true / false value.
##### integer
Any number, with rounding applied after being received.
##### double
Any number, with rounding to the hundredths place after being received.
##### float
Any number, with no rounding applied.

#### finite option strings
If you have a limited number of options that can fill a value you can get improved encoding efficiency by listing out all options in an array. For example:
```yaml
Weapons:
	- Gun
	- Sword
	- Knife
	- Crossbow
```

#### boolean dictionaries
If you have a number of known items that the user can either have or not, you can get improved encoding efficiency by listing them as booleans. For example:
```yaml
Vehicles:
	Bike: boolean
	Car: boolean
	Boat: boolean
	Plane: boolean
```

### templates
Some information is just useful to have. If you enable a template these data structures will be appended to the state tree. You don't need to do anything with them, however they will also be available on the build luau trees to support developer extensions of these states.

#### character
```json
{
	"Character": {
		"IsDead": "boolean",
		"Height": "double",
		"Mass": "double",
		"State": [
			"FallingDown", 
			"Running", 
			"RunningNoPhysics", 
			"Climbing",
			"StrafingNoPhysics",
			"Ragdoll",
			"GettingUp",
			"Jumping",
			"Landed",
			"Flying",
			"Freefall",
			"Seated",
			"PlatformStanding",
			"Dead",
			"Swimming",
			"Physics",
			"None"
		],
		"WalkSpeed": "double",
		"Position": {
			"X": "double",
			"Y": "double",
		},
		"Altitude": "double",
		"JumpPower": "double",
		"Health": "double",
		"MaxHealth": "double",
		"Deaths": "integer",
	}	
}
```

#### chat
```json
{
	"Chat": {
		"LastMessage": "string",
		"Count": "integer",
	}	
}
```

#### client_performance
```json
{
	"Performance": {
		"Client": {
			"Ping": "integer",
			"FPS": "integer",
		}	
	}	
}
```
#### demographics
```json
{
	"Demographics": {
		"AccountAge": "integer",
		"RobloxLanguage": "string",
		"SystemLanguage": "string",
		"Platform": {
			"Accelerometer": "boolean",
			"Gamepad": "boolean",
			"Gyroscope": "boolean",
			"Keyboard": "boolean",
			"Mouse": "boolean",
			"Touch": "boolean",
			"ScreenSize": "integer",
			"ScreenRatio": ["16:10","16:9","5:4","5:3","3:2","4:3","9:16","uncommon"],
		},
	}	
}
```

#### group
```json
{
	"Groups": {
		"group_a_name": "boolean",
		"group_b_name": "boolean",
		"group_c_name": "boolean",
		"group_d_name": "boolean",
	}	
}
```

#### market
```json
{
	"Market": {
		"Spending": {
			"Gamepass": "integer",
			"Product": "integer",
			"Total": "integer",
		},
		"Gamepasses": {
			"Gamepass_A_Name": "boolean",
			"Gamepass_B_Name": "boolean",
			"Gamepass_C_Name": "boolean",
		},
		"Purchase": {
			"Product": {
				"Name": ["dev_product_name_1", "dev_product_name_2"],
				"Price": "integer"
			},
			"Gamepass": {
				"Name": ["gamepass_name_1", "gamepass_name_2"],
				"Price": "integer"
			}
		},
	}	
}
```

#### population
```json
{
	"Population": {
		"Total": "integer",
		"Team": "integer",
		"PeakFriends": "integer",
		"Friends": "integer",
		"SpeakingDistance": "integer",
	}	
}
```

#### server_performance
```json
{
	"Performance": {
		"Server": {
			"EventsPerMinute": "integer",
			"Ping": "integer",
			"ServerTime": "integer",
			"HeartRate": "integer",
			"Instances": "integer",
			"MovingParts": "integer",
			"Network": {
				"Data": {
					"Send": "integer",
					"Receive": "integer",
				},
				"Physics": {
					"Send": "integer",
					"Receive": "integer",
				},
				"Memory": {
					"Internal": "integer",
					"HttpCache": "integer",
					"Instances": "integer",
					"Signals": "integer",
					"LuaHeap": "integer",
					"Script": "integer",
					"PhysicsCollision": "integer",
					"PhysicsParts": "integer",
					"CSG": "integer",
					"Particle": "integer",
					"Part": "integer",
					"MeshPart": "integer",
					"SpatialHash": "integer",
					"TerrainGraphics": "integer",
					"Textures": "integer",
					"CharacterTextures": "integer",
					"SoundsData": "integer",
					"SoundsStreaming": "integer",
					"TerrainVoxels": "integer",
					"Guis": "integer",
					"Animations": "integer",
					"Pathfinding": "integer",
				},
			},
		}	
	}	
}
```

## building roblox scripts
After you've adjusted configuration to your desired settings, you can build your Roblox scripts with this command:
```
midas build
```

## download
If you want to download your data you can do so with this command:
```sh
midas download path/to/file.json "2023-06-25 18:37:11.0000" 30 1000000
```
You can add ``-raw`` at the end if you're debugging a decoding issue and wish to see the data pre-decoding.
### parameters
#### #1: path
Downloads data to this file as json.

#### #2: start
Downloads data from users who joined after this date. Please use the exact format in the example above

#### #3: duration
The number of days after the start date which data will be collected.

#### #4: limit
The maximum amount of users which will be processed.

## clean
If you ever wish to remove midas from your project, you can do so with this command:
```
midas clean
```
