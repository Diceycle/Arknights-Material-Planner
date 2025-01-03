# Arknights Material Planner

![A full screenshot of the application](/src/readme/img/full-screenshot.png)

Streamline your Arknights planning with this all-in-one solution. Simply select the operator and the upgrade and let the
tool do the rest.

Requirements are **downloaded automatically**, so no more researching upgrades and forgetting 10 seconds later which
materials you need to farm.

Compare the **total of your selected upgrades** against what is in your depot, **see what you could craft** and what you
are missing. Since keeping track of your depot's contents manually is exhausting let the tool do that too! Simply click
one button and sit back as **image and text recognition** tells you exactly **what materials you have on hand**.

## Quick Setup

1. Download the zip of the latest version(`ArknightsMaterials_vX.Y.Z.zip`) of Arknights Material Planner from the 
   [releases tab](https://github.com/Diceycle/Arknights-Material-Planner/releases) and unzip it into a folder of your
   choice
2. Ensure Windows Defender didn't remove the exe due to a false positive. This tool trips up virus scanners occasionally
   so use your own judgement if you trust it. All releases are built using GitHub Actions:
   ![workflow badge](https://github.com/diceycle/arknights-material-planner/actions/workflows/release.yaml/badge.svg?event=push)
3. Rename `config-defaults.json` to `config.json` and open it in Notepad.
4. Replace the `"BlueStacks"` in the line: `"arknightsContainer": "BlueStacks"` with `"LDPlayer"` if you are using LDPlayer. 
5. Modify the line that says: `"arknightsWindowName": null` to contain the name of your BlueStacks/LDPlayer window, if it
   is not `BlueStacks` or `LDPlayer` respectively.
6. Start the `ArknightsMaterials.exe`

## Features

### Updates

* Every time the tool is started it checks for up-to-date information regarding new operators and modules on the internet. 
  New modules should appear automatically in the tool because of that, new operators require a manual update to this repository
  so there might be some delay before they are available in the tool.
* Since all available information is downloaded at once after a fresh install, the first start of the tool might take 
  a little while.

### Planning

![An example of a planned upgrade](/src/readme/img/planning.png)

* Start by adding a operator. The desired Upgrade can be selected by clicking on the upgrade icon.
* More Upgrades can also be added. ![The enable/disable checkbox in on state](/src/main/img/ui/add.png) 
  The individual Upgrades per Operator will be sorted automatically.
* Include ![The enable/disable checkbox in on state](/src/main/img/ui/check-on.png) or
  exclude ![The enable/disable checkbox in off state](/src/main/img/ui/check-off.png)
  the material list from the total requirements
* Delete ![The delete button](/src/main/img/ui/close.png) or reorder ![The Button to drag a set of materials](/src/main/img/ui/drag.png)
  the different upgrades to your liking.
* Choose from regular or cumulative upgrade types to set up your to-do list in fewer clicks.

### Depot Overview

![An excerpt from a depot](/src/readme/img/depot-full.png) ![An excerpt from a filtered depot](/src/readme/img/depot-filtered.png)

* See all of your materials at one glance ![The depot switch in full state](/src/main/img/ui/visibility-full.png).
* Focus on only the materials needed in your selected upgrades ![The depot switch in partial state](/src/main/img/ui/visibility-partial.png)
  or only on those you are still missing ![The depot switch in the lowest state](/src/main/img/ui/visibility-low.png).
* See indicators of how many materials you need of each type in
    * Green if you already have enough or can craft enough of the material,
    * Red if you don't have enough of the material.
    * The Colors and text colors are **fully customizable**, see the configuration reference below.
* Indicators can be switched between displaying the full amount that is needed ![The Indicator toggle in full state](/src/main/img/ui/total.png)
  and the amount that is still missing after subtracting current stock and crafting ![The Indicator toggle in missing state](/src/main/img/ui/missing.png).
* A second page ![The button to toggle between the pages](/src/main/img/ui/arrow-down.png) is available for skill books, module
  components, experience cards, chips and LMD.
* **Hint**: There are `+` and `-` buttons, but you can also adjust the amount with the mouse wheel while hovering over a
  material.

### Penguin Stats Export

Use https://penguin-stats.io/planner to plan your long-term farming strategy. Click the export
button ![The export button](/src/main/img/ui/export.png) and get all the information in the depot copied to your clipboard.
You can then paste and import that directly on Penguin Stats.

### Depot Scanning

If you play Arknights on PC you can make use of the image- and text recognition feature to scan and import
![The button to start scanning the depot](/src/main/img/ui/research-button.png) the contents of your depot list into
the tool automatically.

* **This is unfortunately only 99% accurate. It can happen that the tool will miss certain digits or add digits that
  aren't there.**
* **Also Note that this feature will resize your Arknights window and send mouse input to it.** If you want to make sure
  not to accidentally do that you can turn the feature off entirely by setting the `depotParsingEnabled` configuration
  parameter to `false`.
  * Additionally, your player should be in landscape(16:9) mode.
* `arknightsWindowName` uses sane defaults if left empty but some BlueStacks versions have different names, so you might 
  need to change it to whatever it says in the top right corner of the window.
* `arknightsContainer` supports `"BlueStacks"` and `"LDPLayer"`. If you are not using either of those you can set it to
  `"genericWindow"` and add the remaining configuration yourself:
    * If the root window is not the one accepting input you need to adjust `arknightsInputWindowClass` to set a child
      window that does accept input. Use the `FindArknightsWindow.exe` to find the names
    * Also, you might need to provide the border values in `arknightsWindowBorder` for the screenshots to get cropped
      correctly.

### Recipe Display

![A Recipe being display in the depot](/src/readme/img/recipe.png)

Click on any Material in the depot to display its recipe if it has one.

**Please note that conversion between different class chips are not listed since it is a net-negative process and will 
cause issues with the calculation of required materials.**

### Color Settings

![A example of a potential light mode](/src/readme/img/colors.png)

Not a fan of the default color scheme? Simply adjust the configuration parameters `color`, `colorDark` and
`highlightColor`, that control the primary, secondary, and line/icon color respectively. For bright colors it is also
recommended to enable `highlightUpgrades` since most of these icons have a lot of white in them.

### Space for your assistant

There is a bit of unused space between your upgrades and your depot. Why not display your favorite operator?
Set `backgroundImage` to any image on your hard drive to get it displayed there. Use `backgroundImageOffset` to adjust
the position if necessary. The color behind the image can also be separately controlled by `backgroundColor`.

## Technical Limitations

* This is a Windows-only tool. Even running the python source directly, the tool still makes heavy use of the win32api
  to collect screenshots and control the Arknights player for depot scanning. The other features will likely work but no
  effort has been made to be linux compatible.
* This tool has been primarily tested with BlueStacks and LDPlayer. A configuration for other emulators can likely be found but is
  not guaranteed. As an example, Windows 11's native android emulation can not be interacted with in the same way
  BlueStacks can. As a result, it is not compatible with the depot scanning feature.
* This has been tested on the english client. I have seen that the korean client uses a different font
  for numbers. This might throw off the tool as well, but if enough demand exists for it, I might add a different mode
  for other regions.
* Scanning expects numbers attached to the materials. For numbers larger than 1000 Arknights starts to abbreviate them to
  1k, etc. This breaks the scanning.
* Since this tool relies on relatively exact pixel measurements, slight changes might throw it off. I have tried my best
  to add leniency but in the end the result is still somewhat fragile.

## Building or running from the source

### Requirements

Run `pip install -r requirements.txt` to set up your Python environment with the correct dependencies.
Then run `ArknightsMaterials.py`

### Building the source

In case you want to build the executable yourself you can run `build.py` and a `_dist` folder will be created with the
distribution. Simply move the contents where you want them.

### Hint: Updates that can be done without releases

Since almost all of the game data is downloaded from external sources, no update to the code is necessary to include
new operators, modules or even materials.

The `entityLists/operators.json` and `entityLists/materials.json` in this repository are used to determine which operators
and materials are available in the tool. These files are not part of a release and instead are downloaded by the tool
on startup. Per default the files are downloaded from this repository but this can be changed with `entityListRepository`.
Editing these files locally will also make the new operators available but might cause issues when the "official" update is downloaded.

Similarly, the actual data as well as all the operator, etc. images from the game client are sourced from dedicated repositories.
They can be changed with `dataRepository` and `imageRepository` respectively. The paths to the files can also be 
adjusted if the folder structure differs in another repository.

## Troubleshooting

* **Q**: The tool crashes on startup. What went wrong?
  * **A**: Usually that is an issue with the `config.json`. Use an online JSON verifier like [JSONLint](https://jsonlint.com/)
    to check if you've maybe made a mistake.
* **Q**: The tool keeps saying I need to navigate to the main menu or the depot even though I'm there already, what do I do?
  * **A**: Disable any hotkey overlays you might have in your player, make sure not to overlap your mouse with the player.
    If that does not work try increasing the `colorLeniency` config parameter. 
* **Q**: The tool added a digit to a number, did not recognize a number or is missing a digit. Can you fix that?
  * **A**: Text Recognition(OCR) is not a perfect technology. Mistakes can and will happen, so I doubt the depot 
    scanning feature will ever be 100% accurate. Please do not submit bug reports for every single misread.

## Configuration Reference

Configuration is read from a file called `config.json` and is a single JSON-Object with the following possible values.

| Parameter Name               | Type            | Default                                 | Description                                                                                                                                                                                                                                                                                                            |
|------------------------------|-----------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `uiScale`                    | Number          | `80`                                    | Controls the **size** of **all screen elements** as well as the **window itself**.                                                                                                                                                                                                                                     |
| `scrollSpeed`                | Number          | `30`                                    | Controls how fast the **left panel** can be **scrolled with the mouse wheel**. Pro tip: Setting this to 110 will scroll exactly one element per tick.                                                                                                                                                                  |
| `saveFile`                   | String          | `"default.materials"`                   | Determines the **file** name of where the **data is saved and loaded from**. Have alt accounts? Switch back and forth between them with this parameter.                                                                                                                                                                |
| `maintainNaturalOrder`       | Boolean         | `false`                                 | Whether to **sort** the **material list** in upgrades as they appear **in the game client** or apply a **consistent order** over all materials                                                                                                                                                                         |
| `sortUpgrades`               | Boolean         | `true`                                  | Whether to **sort** the **upgrades** within a set of upgrades for one operator automatically or not.                                                                                                                                                                                                                   |
| `backgroundImage`            | String/Filename | `null`                                  | Points to a **file on your computer** to load as the **background image** for the application.                                                                                                                                                                                                                         |
| `backgroundImageOffset`      | Number          | `0`                                     | Adjusts the **X-Position** of how the **background image** is placed.                                                                                                                                                                                                                                                  |
| `backgroundColor`            | String/Color    | `"#444444"`                             | Controls the **color** of the **background**.                                                                                                                                                                                                                                                                          |
| `color`                      | String/Color    | `"#555555"`                             | Controls the **primary color** of the application.                                                                                                                                                                                                                                                                     |
| `colorDark`                  | String/Color    | `"#444444"`                             | Controls the **secondary color** of the application.                                                                                                                                                                                                                                                                   |
| `highlightColor`             | String/Color    | `"white"`                               | Controls the **color** of **buttons, icons and lines** in the application.                                                                                                                                                                                                                                             |
| `highlightUpgrades`          | Boolean         | `false`                                 | Whether to also recolor the **Upgrade icons** with `hightlightColor`. Good for light background colors.                                                                                                                                                                                                                |
| `amountColor`                | String/Color    | `"black"`                               | Controls the **color** of the labels displaying the **amount of materials**                                                                                                                                                                                                                                            |
| `amountColorFont`            | String/Color    | `"white"`                               | Controls the **text color** in `amountColor`                                                                                                                                                                                                                                                                           |
| `depotColorSufficient`       | String/Color    | `"#00CC00"`                             | Controls the **color** of the labels displaying **sufficient or craftable stock**                                                                                                                                                                                                                                      |
| `depotColorSufficientFont`   | String/Color    | `"black"`                               | Controls the **text color** in `depotColorSufficient`                                                                                                                                                                                                                                                                  |
| `depotColorInsufficient`     | String/Color    | `"red"`                                 | Controls the **color** of the labels displaying **insufficient stock**                                                                                                                                                                                                                                                 |
| `depotColorInsufficientFont` | String/Color    | `"black"`                               | Controls the **text color** in `depotColorInsufficient`                                                                                                                                                                                                                                                                |
| `entityListRepository`       | String          | `"Diceycle/Arknights-Material-Planner"` | GitHub repository from where to download lists of operators and materials to display in the tool. This usually should point to the same repository the code is hosted in, but can be adjusted if necessary.                                                                                                            |
| `dataRepository`             | String          | `"Kengxxiao/ArknightsGameData"`         | GitHub repository from where to download Arknights game data like operator costs, modules, recipes, etc. The data in that repository needs to contain all the necessary jsons that are created from decompiling the FlatBuffer files in the Arknights APK                                                              |
| `dataRepositoryGameDataPath` | String          | `"zh_CN/gamedata/excel/"`               | The folder containing all the above mentioned Jsons in the Data repository                                                                                                                                                                                                                                             |
| `imageRepository`            | String          | `"PuppiizSunniiz/Arknight-Images"`      | GutHub repository from where to download images of operators, items, modules, etc. Due to the way the images are organized this should be a up-to-date fork of the repository that is providing images for AN-EN-Tags originally developed by Aceship                                                                  |
| `depotParsingEnabled`        | Boolean         | `true`                                  | Whether to **enable** the **depot scanning** feature. Disabling this will hide relevant UI-Elements                                                                                                                                                                                                                    |
| `arknightsContainer`         | String          | `"BlueStacks"`                          | The type of player you run Arknights with. Currently three modes are supported: `"BlueStacks"`, `"LDPlayer"` and `"genericWindow"`.                                                                                                                                                                                    |
| `arknightsWindowName`        | String          | `null`                                  | The name of the **window** that **Arknights** is running in. This can either be read from the window title or a list is provided by `FindArknightsWindow.exe` is this value is left empty. Defaults to `"BlueStacks"` or `"LDPlayer"` if the corresponding `arknightsContainer` is set.                                |
| `arknightsInputWindowClass`  | String          | `null`                                  | The name of the **child window class** that accepts input. Only supported for `arknightsContainer` = `"genericWindow"` This is an **expert setting**. `FindArknightsWindow.exe` will list available child windows for the window given in `arknightsContainer`. Can also be set to `null` to use the top-level window. |
| `arknightsWindowBorder`      | List[Number]    | `null`                                  | The amount of **pixels to crop away** from Arknights **screenshots** from the Left, Top, Right and Bottom respectively. Defaults to `[1, 33, 33, 1]` for BlueStacks and `[0, 34, 39, 0]` for LDPlayer. This is also used to determine which exact pixel measurements to resize the Arknights Window to.                |
| `depotScanScrollDelay`       | Number          | `5`                                     | The amount of **time to wait between individual mouse movements** while scrolling in 100ths of a second. Makes the scroll distance more consistent. Useful if the depot does not get scrolled far enough to scan the second and third pages.                                                                           |
| `depotScanScrollOffset`      | Number          | `25`                                    | The amount of **pixels to scroll additionally** to the length of one page in the depot. This represents the **deadzone** built into either the app or the emulator. Defaults to 25 as tested on Bluestacks with default settings. Maxes out around 200 pixels as the window usually ends at that point.                |
| `colorLeniency`              | Number          | `3`                                     | How lenient certain pixel reads should be to determine which menu the Arknights app is in. This is a allowed delta in color value(0-255) per band.                                                                                                                                                                     |
| `imageRecognitionThreshold`  | Float           | `0.8`                                   | The confidence required for the image recognition to decide a certain material has been found. This is a value from 0 to 1. 0.95 means 95% confident.                                                                                                                                                                  |



