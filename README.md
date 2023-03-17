# Arknights Material Planner

![A full screenshot of the applicaiton](/img/readme/full-screenshot.png)

Streamline your Arknights planning with this all-in-one solution. Simply select the operator and the upgrade and let the
tool do the rest.

Requirements are **downloaded automatically** so no more researching upgrades and forgetting 10 seconds later which
materials you need to farm.

Compare the **total of your selected upgrades** against what is in your depot, **see what you could craft** and what you
are missing. Since keeping track of your depot's contents manually is exhausting let the tool do that too! Simply click 
one button and sit back as **image and text recognition** tells you exactly **what materials you have on hand**.

## Quick Setup

1. Download the latest version of Arknights Material Planner from the releases tab and unzip it into a folder of your
   choice
2. Download Tesseract from here: https://github.com/UB-Mannheim/tesseract/wiki and run the installer.
3. Rename `config-defaults.json` to `config.json` and open it in Notepad.
4. Modify the line that says: `"tesseractExeLocation": null,` to contain the location to the tesseract.exe which is 
   located in the folder you chose for the tesseract installation.
    1. The path needs to be in quotes(`"`) and backslashes(``\``) need to be escaped. Here is a full example:
    2. `"tesseractExeLocation": "C:\\Program Files\\tesseractOCR\\tesseract.exe",`
5. Modify the line that says: `"arknightsWindowName": "BlueStacks"` to contain the name of your BlueStacks window, if it
   is not `BlueStacks`.
6. Start the `ArknightsMaterials.exe`

## Features

### Planning

![An example of a planned upgrade](/img/readme/planning.png)

* Choose the operator, and the type of Upgrade you want. Material requirements are then automatically downloaded from
  Gamepress.
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
    * Gray if you have enough of the material,
    * Green if you can craft enough of the material,
    * Red if you don't have enough of the material.
    * The Colors and text colors are **fully customizable**, see the configuration reference below.
* A second page ![The button to toggle between the pages](/img/ui/arrow-down.png) is available for skill books, module
  components and experience cards and chips and LMD.

### Penguin Stats Export

Use https://penguin-stats.io/planner to plan your long-term farming strategy. Click the export
button ![The export button](/img/ui/export.png) and get all of the information in the depot copied to your clipboard. 
You can then paste and import that directly on Penguin Stats.

### Depot Scanning

If you play Arknights on PC you can make use of the image- and text recognition feature to scan and import 
![The button to toggle between the pages](/img/ui/research-button.png) the contents of your depot list into
the tool automatically.

* **This is unfortunately only 99% accurate. It can happen that the tool will miss certain digits or add digits that
  aren't there.** If there are any OCR experts I'm more than willing to accept help to reduce the error rate as far as
  possible.
* **Also Note that this feature will resize your Arknights window and send mouse input to it.** If you want to make sure
  not to accidentally do that you can turn the feature off entirely by setting the `depotParsingEnabled` configuration
  parameter to `false`.
* This requires an installation of [TesseractOCR](https://github.com/tesseract-ocr/tesseract).
    * Prebuilt Binaries for Tesseract are available here: https://github.com/UB-Mannheim/tesseract/wiki
    * After installing, add the path to the Tesseract executable as the `tesseractExeLocation` config parameter.
* You must always set `arknightsWindowName` to the name of the window that Arknights is running in.
* The tool is configured to work with BlueStacks out of the box. If you do not play on BlueStacks these additional steps
  are necessary:
    * Set `arknightsContainer` to `"genericWindow"`
    * If the root window is not the one accepting input you need to adjust `arknightsInputWindowClass` to set a child
      window that does accept input
    * Finally, you might need to adjust the border values in `arknightsWindowBorder` for the screenshots to get cropped
      correctly.

### Recipe Display

![A Recipe being display in the depot](/img/readme/recipe.png)

Click on any Material in the depot to display its recipe if it has one.

Please note that Chips are currently not considered craftable.

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
* Text Recognition(OCR) is not a perfect technology. Mistakes can and will happen so I doubt the depot scanning feature
  will ever be 100% accurate. Please do not submit bug reports for every single misread.
    * Additionally, this has been tested on the english client. I have seen that the korean client uses a different font
      for numbers. This might throw off the tool as well.

## Building or running from the source

### Requirements

Run `pip install requirements.txt` to set up your Python environment with the correct dependencies.
Then run `ArknightsMaterials.py`

### Building

In case you want to build the executable yourself you can run `build.py` and a `_dist` folder will be created with the
distribution. Simply move the contents where you want them.

## Configuration Reference

Configuration is read from a file called `config.json` and is a single JSON-Object with the following possible values.

| Parameter Name               | Type            | Default                                      | Description                                                                                                                                                                                                                                                                                                            |
|------------------------------|-----------------|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `uiScale`                    | Number          | `100`                                        | Controls the **size** of **all screen elements**.                                                                                                                                                                                                                                                                      |
| `scrollSpeed`                | Number          | `30`                                         | Controls how fast the **left panel** can be **scrolled with the mouse wheel**. Pro tip: Setting this to 110 will scroll exactly one element per tick.                                                                                                                                                                  |
| `saveFile`                   | String          | `"default.materials"`                        | Determines the **file** name of where the **data is saved and loaded from**. Have alt accounts? Switch back and forth between them with this parameter.                                                                                                                                                                |
| `backgroundImage`            | String/Filename | `null`                                       | Points to a **file on your computer** to load as the **background image** for the application.                                                                                                                                                                                                                         |
| `backgroundImageOffset`      | Number          | `0`                                          | Adjusts the **X-Position** of how the **background image** is placed.                                                                                                                                                                                                                                                  |
| `backgroundColor`            | String/Color    | `"#444444"`                                  | Controls the **color** of the **background**.                                                                                                                                                                                                                                                                          |
| `color`                      | String/Color    | `"#555555"`                                  | Controls the **primary color** of the application.                                                                                                                                                                                                                                                                     |
| `colorDark`                  | String/Color    | `"#444444"`                                  | Controls the **secondary color** of the application.                                                                                                                                                                                                                                                                   |
| `highlightColor`             | String/Color    | `"white"`                                    | Controls the **color** of **buttons, icons and lines** in the application.                                                                                                                                                                                                                                             |
| `highlightUpgrades`          | Boolean         | `false`                                      | Whether to also recolor the **Upgrade icons** with `hightlightColor`. Good for light background colors.                                                                                                                                                                                                                |
| `amountColor`                | String/Color    | `"black"`                                    | Controls the **color** of the labels displaying the **amount of materials**                                                                                                                                                                                                                                            |
| `amountColorFont`            | String/Color    | `"white"`                                    | Controls the **text color** in `amountColor`                                                                                                                                                                                                                                                                           |
| `depotColorSufficient`       | String/Color    | `"gray"`                                     | Controls the **color** of the labels displaying **sufficient amount of stock**                                                                                                                                                                                                                                         |
| `depotColorSufficientFont`   | String/Color    | `"white"`                                    | Controls the **text color** in `depotColorSufficient`                                                                                                                                                                                                                                                                  |
| `depotColorCraftable`        | String/Color    | `"#00DD00"`                                  | Controls the **color** of the labels displaying **insufficient stock that can be crafted**                                                                                                                                                                                                                             |
| `depotColorCraftableFont`    | String/Color    | `"black"`                                    | Controls the **text color** in `depotColorCraftable`                                                                                                                                                                                                                                                                   |
| `depotColorInsufficient`     | String/Color    | `"red"`                                      | Controls the **color** of the labels displaying **insufficient stock**                                                                                                                                                                                                                                                 |
| `depotColorInsufficientFont` | String/Color    | `"black"`                                    | Controls the **text color** in `depotColorInsufficient`                                                                                                                                                                                                                                                                |
| `gampressUrl`                | String/URL      | `"https://gamepress.gg/arknights/operator/"` | The **base URL** for Operators on **Gamepress**. Just in case this ever changes.                                                                                                                                                                                                                                       |
| `depotParsingEnabled`        | Boolean         | `true`                                       | Whether to **enable** the **depot scanning** feature. Disabling this will hide relevant UI-Elements                                                                                                                                                                                                                    |
| `arknightsContainer`         | String          | `"BlueStacks"`                               | The type of player you run Arknights with. Currently two modes are supported `"BlueStacks"` and `"genericWindow"`.                                                                                                                                                                                                     |
| `arknightsWindowName`        | String          | `"BlueStacks"`                               | The name of the **window** that **Arknights** is running in. This can either be read from the window title or a list is provided by `FindArknightsWindow.exe` is this value is left empty.                                                                                                                             |
| `arknightsInputWindowName`   | String          | `null`                                       | The name of the **child window class** that accepts input. Only supported for `arknightsContainer` = `"genericWindow"` This is an **expert setting**. `FindArknightsWindow.exe` will list available child windows for the window given in `arknightsContainer`. Can also be set to `null` to use the top-level window. |
| `arknightsWindowBorder`      | List[Number]    | `[1, 33, 33, 1]`                             | The amount of **pixels to crop away** from Arknights **screenshots** from the Left, Top, Right and Bottom respectively.                                                                                                                                                                                                |
| `colorLeniency`              | Number          | `3`                                          | How lenient certain pixel reads should be to determine which menu the Arknights app is in. This is a allowed delta in color value(0-255) per band.                                                                                                                                                                     |
| `imageRecognitionThreshold`  | Float           | `0.95`                                       | The confidence required for the image recognition to decide a certain material has been found. This is a value from 0 to 1. 0.95 means 95% confident.                                                                                                                                                                  |
| `tesseractExeLocation`       | String/Filename | `null`                                       | Path to the **Tesseract Exe** to use for Depot Scanning.                                                                                                                                                                                                                                                               |



