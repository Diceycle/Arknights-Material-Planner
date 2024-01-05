# Arknights Material Planner

![A full screenshot of the application](/img/readme/full-screenshot.jpg)

Streamline your Arknights planning with this all-in-one solution. Simply select the operator and the upgrade and let the
tool do the rest.

Requirements are **downloaded automatically**, so no more researching upgrades and forgetting 10 seconds later which
materials you need to farm.

Compare the **total of your selected upgrades** against what is in your depot, **see what you could craft** and what you
are missing. Since keeping track of your depot's contents manually is exhausting let the tool do that too! Simply click
one button and sit back as **image and text recognition** tells you exactly **what materials you have on hand**.

## Quick Setup

1. Download Tesseract from [here](https://github.com/UB-Mannheim/tesseract/wiki) and run the installer.
2. Download the zip of the latest version(`ArknightsMaterials_vX.Y.Z.zip`) of Arknights Material Planner from the 
   [releases tab](https://github.com/Diceycle/Arknights-Material-Planner/releases) and unzip it into a folder of your
   choice
3. Ensure Windows Defender didn't remove the exe due to a false positive. This tool trips up virus scanners occasionally
   so use your own judgement if you trust it. All releases are built using GitHub Actions:
   ![workflow badge](https://github.com/diceycle/arknights-material-planner/actions/workflows/release.yaml/badge.svg?event=push)
4. Rename `config-defaults.json` to `config.json` and open it in Notepad.
5. Modify the line that says: `"tesseractExeLocation": null,` to contain the location to the tesseract.exe which is
   located in the folder you chose for the tesseract installation.
    1. The path needs to be in quotes(`"`) and backslashes(``\``) need to be escaped with an additional backslash. Here is a full example:
    2. `"tesseractExeLocation": "C:\\Program Files\\tesseractOCR\\tesseract.exe"`
6. Replace the `"BlueStacks"` in the line: `"arknightsContainer": "BlueStacks"` with `"LDPlayer"` if you are using LDPlayer. 
7. Modify the line that says: `"arknightsWindowName": null` to contain the name of your BlueStacks/LDPlayer window, if it
   is not `BlueStacks` or `LDPlayer` respectively.
8. Start the `ArknightsMaterials.exe`

## Features

### Planning

![An example of a planned upgrade](/img/readme/planning.png)

* Start by adding a operator and the type of Upgrade you want. Material requirements are then automatically downloaded from
  Gamepress.
  * Material requirements are cached locally to not spam Gamepress. In case a module releases for an Operator, you can
    force a refresh on the material requirements ![The button to refresh material requirements](/img/ui/resetCache.png) 
* Multiple Upgrades can be selected per Operator. The individual Upgrades per Operator will be sorted automatically.
* Include ![The enable/disable checkbox in on state](/img/ui/check-on.png) or
  exclude ![The enable/disable checkbox in off state](/img/ui/check-off.png)
  the material list from the total requirements
* Delete ![The delete button](/img/ui/close.png) or reorder ![The Button to drag a set of materials](/img/ui/drag.png)
  the different upgrades to your liking.
* Choose from regular or cumulative upgrade types to set up your to-do list in fewer clicks.

### Depot Overview

![An excerpt from a depot](/img/readme/depot-full.png) ![An excerpt from a filtered depot](/img/readme/depot-filtered.png)

* See all of your materials at one glance ![The depot switch in full state](/img/ui/visibility-full.png).
* Focus on only the materials needed in your selected upgrades ![The depot switch in partial state](/img/ui/visibility-partial.png)
  or only on those you are still missing ![The depot switch in the lowest state](/img/ui/visibility-low.png).
* See indicators of how many materials you need of each type in
    * Green if you already have enough or can craft enough of the material,
    * Red if you don't have enough of the material.
    * The Colors and text colors are **fully customizable**, see the configuration reference below.
* Indicators can be switched between displaying the full amount that is needed ![The Indicator toggle in full state](/img/ui/total.png)
  and the amount that is still missing after subtracting current stock and crafting ![The Indicator toggle in missing state](/img/ui/missing.png).
* A second page ![The button to toggle between the pages](/img/ui/arrow-down.png) is available for skill books, module
  components and experience cards and chips and LMD.
* **Hint**: There are `+` and `-` buttons, but you can also adjust the amount with the mouse wheel while hovering over a
  material.

### Penguin Stats Export

Use https://penguin-stats.io/planner to plan your long-term farming strategy. Click the export
button ![The export button](/img/ui/export.png) and get all the information in the depot copied to your clipboard.
You can then paste and import that directly on Penguin Stats.

### Depot Scanning

If you play Arknights on PC you can make use of the image- and text recognition feature to scan and import
![The button to start scanning the depot](/img/ui/research-button.png) the contents of your depot list into
the tool automatically.

* **This is unfortunately only 99% accurate. It can happen that the tool will miss certain digits or add digits that
  aren't there.** If there are any OCR experts I'm more than willing to accept help to reduce the error rate as far as
  possible.
* **Also Note that this feature will resize your Arknights window and send mouse input to it.** If you want to make sure
  not to accidentally do that you can turn the feature off entirely by setting the `depotParsingEnabled` configuration
  parameter to `false`.
  * Additionally, your player should be in landscape(16:9) mode.
* This requires an installation of [TesseractOCR](https://github.com/tesseract-ocr/tesseract).
    * Prebuilt Binaries for Tesseract are available here: https://github.com/UB-Mannheim/tesseract/wiki
    * After installing, add the path to the Tesseract executable as the `tesseractExeLocation` config parameter.
* `arknightsWindowName` uses sane defaults if left empty but some BlueStacks versions have different names, so you might 
  need to change it to whatever it says in the top right corner of the window.
* `arknightsContainer` supports `"BlueStacks"` and `"LDPLayer"`. If you are not using either of those you can set it to
  `"genericWindow"` and add the remaining configuration yourself:
    * If the root window is not the one accepting input you need to adjust `arknightsInputWindowClass` to set a child
      window that does accept input. Use the `FindArknightsWindow.exe` to find the names
    * Also, you might need to provide the border values in `arknightsWindowBorder` for the screenshots to get cropped
      correctly.

### Recipe Display

![A Recipe being display in the depot](/img/readme/recipe.png)

Click on any Material in the depot to display its recipe if it has one.

**Please note that Class Chips are currently not considered craftable.**

### Color Settings

![A example of a potential light mode](/img/readme/colors.png)

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
* This tool has been primarily tested with BlueStacks. A configuration for other emulators can likely be found but is
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

### Hint: Updating the Operator List

I usually do not update the tool as soon as an operator comes out and instead just add the new operators in a batch 
every few months or so. But updating the operator list does not require an update to the code.

`operators.json` contains a full list of all operators with their name (which is used for the search in the operator 
selection), an image which has to be present in the `img/operator` folder, and an external name, in case the URL on
Gamepress differs from the name of the operator. 

By providing these details, the tool can be kept up to date in case the releases ever fall behind too far, or you want to 
plan further into the future. 

## Troubleshooting

* **Q**: The tool crashes on startup. What went wrong?
  * **A**: Usually that is an issue with the `config.json`. Use an online JSON verifier like [JSONLint](https://jsonlint.com/)
    to check if you've maybe made a mistake.
* **Q**: An operator recently got a new Module, but I don't see it in the tool, what happened?
  * **A**: The tool caches Operator data, so it doesn't know an update was released. You can force a manual refresh by 
    clicking the button under the operator image.
* **Q**: The tool keeps saying I need to navigate to the main menu or the depot even though I'm there already, what do I do?
  * **A**: Disable any hotkey overlays you might have in your player, make sure not to overlap your mouse with the player.
    If that does not work try increasing the `colorLeniency` config parameter. 
* **Q**: The tool added a digit to a number, did not recognize a number or is missing a digit. Can you fix that?
  * **A**: Text Recognition(OCR) is not a perfect technology. Mistakes can and will happen, so I doubt the depot 
    scanning feature will ever be 100% accurate. Please do not submit bug reports for every single misread.

## Configuration Reference

Configuration is read from a file called `config.json` and is a single JSON-Object with the following possible values.

| Parameter Name               | Type            | Default                                      | Description                                                                                                                                                                                                                                                                                                            |
|------------------------------|-----------------|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `uiScale`                    | Number          | `80`                                         | Controls the **size** of **all screen elements** as well as the **window itself**.                                                                                                                                                                                                                                     |
| `scrollSpeed`                | Number          | `30`                                         | Controls how fast the **left panel** can be **scrolled with the mouse wheel**. Pro tip: Setting this to 110 will scroll exactly one element per tick.                                                                                                                                                                  |
| `saveFile`                   | String          | `"default.materials"`                        | Determines the **file** name of where the **data is saved and loaded from**. Have alt accounts? Switch back and forth between them with this parameter.                                                                                                                                                                |
| `maintainNaturalOrder`       | Boolean         | `false`                                      | Whether to **sort** the **material list** in upgrades as they appear **in the game client** or apply a **consistent order** over all materials                                                                                                                                                                         |
| `sortUpgrades`               | Boolean         | `true`                                       | Whether to **sort** the **upgrades** within a set of upgrades for one operator automatically or not.                                                                                                                                                                                                                   |
| `backgroundImage`            | String/Filename | `null`                                       | Points to a **file on your computer** to load as the **background image** for the application.                                                                                                                                                                                                                         |
| `backgroundImageOffset`      | Number          | `0`                                          | Adjusts the **X-Position** of how the **background image** is placed.                                                                                                                                                                                                                                                  |
| `backgroundColor`            | String/Color    | `"#444444"`                                  | Controls the **color** of the **background**.                                                                                                                                                                                                                                                                          |
| `color`                      | String/Color    | `"#555555"`                                  | Controls the **primary color** of the application.                                                                                                                                                                                                                                                                     |
| `colorDark`                  | String/Color    | `"#444444"`                                  | Controls the **secondary color** of the application.                                                                                                                                                                                                                                                                   |
| `highlightColor`             | String/Color    | `"white"`                                    | Controls the **color** of **buttons, icons and lines** in the application.                                                                                                                                                                                                                                             |
| `highlightUpgrades`          | Boolean         | `false`                                      | Whether to also recolor the **Upgrade icons** with `hightlightColor`. Good for light background colors.                                                                                                                                                                                                                |
| `amountColor`                | String/Color    | `"black"`                                    | Controls the **color** of the labels displaying the **amount of materials**                                                                                                                                                                                                                                            |
| `amountColorFont`            | String/Color    | `"white"`                                    | Controls the **text color** in `amountColor`                                                                                                                                                                                                                                                                           |
| `depotColorSufficient`       | String/Color    | `"#00CC00"`                                  | Controls the **color** of the labels displaying **sufficient or craftable stock**                                                                                                                                                                                                                                      |
| `depotColorSufficientFont`   | String/Color    | `"black"`                                    | Controls the **text color** in `depotColorSufficient`                                                                                                                                                                                                                                                                  |
| `depotColorInsufficient`     | String/Color    | `"red"`                                      | Controls the **color** of the labels displaying **insufficient stock**                                                                                                                                                                                                                                                 |
| `depotColorInsufficientFont` | String/Color    | `"black"`                                    | Controls the **text color** in `depotColorInsufficient`                                                                                                                                                                                                                                                                |
| `gampressUrl`                | String/URL      | `"https://gamepress.gg/arknights/operator/"` | The **base URL** for Operators on **Gamepress**. Just in case this ever changes.                                                                                                                                                                                                                                       |
| `depotParsingEnabled`        | Boolean         | `true`                                       | Whether to **enable** the **depot scanning** feature. Disabling this will hide relevant UI-Elements                                                                                                                                                                                                                    |
| `arknightsContainer`         | String          | `"BlueStacks"`                               | The type of player you run Arknights with. Currently three modes are supported: `"BlueStacks"`, `"LDPlayer"` and `"genericWindow"`.                                                                                                                                                                                    |
| `arknightsWindowName`        | String          | `null`                                       | The name of the **window** that **Arknights** is running in. This can either be read from the window title or a list is provided by `FindArknightsWindow.exe` is this value is left empty. Defaults to `"BlueStacks"` or `"LDPlayer"` if the corresponding `arknightsContainer` is set.                                |
| `arknightsInputWindowName`   | String          | `null`                                       | The name of the **child window class** that accepts input. Only supported for `arknightsContainer` = `"genericWindow"` This is an **expert setting**. `FindArknightsWindow.exe` will list available child windows for the window given in `arknightsContainer`. Can also be set to `null` to use the top-level window. |
| `focusWindowBeforeScanning`  | Boolean         | `false`                                      | If the tool should pull the Arknights Container into the foreground before starting to scan. Reccommended for BlueStacks 5.6+ as the window will not take input while not in focus.                                                                                                                                    |
| `arknightsWindowBorder`      | List[Number]    | `null`                                       | The amount of **pixels to crop away** from Arknights **screenshots** from the Left, Top, Right and Bottom respectively. Defaults to `[1, 33, 33, 1]` for BlueStacks and `[1, 34, 41, 2]` for LDPlayer.                                                                                                                 |
| `depotScanScrollDelay`       | Number          | `2`                                          | The amount of **time to wait between individual mouse movements** while scrolling in 100ths of a second. Makes the scroll distance more consistent. Useful if the depot does not get scrolled far enough to scan the second and third pages.                                                                           |
| `depüotScanScrollOffset`     | Number          | `25`                                         | The amount of **pixels to scroll additionally** to the length of one page in the depot. This represents the **deadzone** built into either the app or the emulator. Defaults to 25 as tested on Bluestacks with default settings. Maxes out around 200 pixels as the window usually ends at that point.                |
| `colorLeniency`              | Number          | `3`                                          | How lenient certain pixel reads should be to determine which menu the Arknights app is in. This is a allowed delta in color value(0-255) per band.                                                                                                                                                                     |
| `imageRecognitionThreshold`  | Float           | `0.95`                                       | The confidence required for the image recognition to decide a certain material has been found. This is a value from 0 to 1. 0.95 means 95% confident.                                                                                                                                                                  |
| `tesseractExeLocation`       | String/Filename | `null`                                       | Path to the **Tesseract Exe** to use for Depot Scanning.                                                                                                                                                                                                                                                               |



