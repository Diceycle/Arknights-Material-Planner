# Arknights Material Planner

![A full screenshot of the applicaiton](/img/readme/full-screenshot.png)

A simple application to plan all your upgrades to your favorite operators. Easily configure individual upgrades, toggle
them on or off and keep track of a total of all your upgrades.

No need to look up upgrade costs online, when the tool does it for you. Simply click the research button and the tool
will go to Gamepress in your stead.

Finally, no need to set up your depot contents manually. Sadly Arknights does not offer an API but that doesn't stop us
from taking screenshots and analyzing the depot contents ourselves.

## Features

### Planning

![An example of a planned upgrade](/img/readme/planning.png)

* Set up all the upgrades you are planning. Choose the operator, the Upgrade and the Materials. Include or exclude the
  Materials from the calculated total with the checkbox on the right.
* Add the materials yourself or automatically download the Material list from Gamepress.
    * Note: The Skill Rank 7 Upgrade only looks for Tier 3 and higher Materials on Gamepress.
* Delete or reorder the different upgrades to your liking.
* You can manually remove materials by right clicking them.

### Depot Overview

![An excerpt from a depot](/img/readme/depot-full.png) ![An excerpt from a filtered depot](/img/readme/depot-filtered.png)

* See all of your materials at one glance.
* Focus on only the materials needed in your selected upgrades or only on those you are still missing.
* If you do not have enough materials, the tool will also mark the needed crafting ingredients as required.

* A second page is available for skill books, module components and experience cards.

### Depot Scanning

If you play Arknights on PC you can make use of the inbuilt image- and text recognition to scan your
depot and import you material list into the tool automatically.

* **This is unfortunately only 99% accurate. It can happen that the tool will miss certain digits or add digits that
  aren't there.** If there are OCR experts I'm more than willing to accept help to reduce the error rate as far as
  possible
* This requires an installation of [TesseractOCR](https://github.com/tesseract-ocr/tesseract).
    * Prebuilt Binaries for Tesseract are available here: https://github.com/UB-Mannheim/tesseract/wiki
    * After installing add the path to the Tesseract executable as the `tesseractExeLocation` config parameter.
* You must always set `arknightsWindowName` to the name of the window that Arknights is running in.
* The tool is configured to work with BlueStacks out of the box. If you do not play on BlueStacks these additional steps
  are necessary:
    * Set `arknightsContainer` to `"genericWindow"`
    * If the root window is not the one accepting input you need to adjust `arknightsInputWindowClass` to set the child
      window that does accept input
    * Finally, you might need to adjust the border values in `arknightsWindowBorder` for the screenshots to get cropped
      correctly.
* **Note that this feature will resize your Arknights window and send mouse input to it.** If you want to make sure not
  to accidentally do that you can turn the feature off entirely by setting the `depotParsingEnabled` configuration
  parameter to `false`.

### Minor Features and UI

#### Recipe Display

![A Recipe being display in the depot](/img/readme/recipe.png)

Click on any Material in the depot to display its recipe if it has one.

#### Color Settings

![A example of a potential light mode](/img/readme/colors.png)

Not a fan of the default color scheme? Simply adjust the configuration parameters `color`, `colorDark` and
`highlightColor`, that control the primary, secondary, and line/icon color respectively.

#### Space for your assistant

There is a bit of unused space between your upgrades and your depot. Why not display your favorite operator?
Set `backgroundImage` to any image on your hard drive to get it displayed there. Use `backgroundImageOffset` to adjust
the position if necessary. The color behind the image can also be separately controlled by `backgroundColor`.

### Missing Features

* Module Costs can currently not be configured or downloaded from Gamepress. Gamepress unfortunately does not present
  them in a machine friendly way.
* Class Chips cannot be scanned for or configured as costs.

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
| `amountColor`                | String/Color    | `"black"`                                    | Controls the **color** of the labels displaying the **amount of materials**                                                                                                                                                                                                                                            |
| `amountColorFont`            | String/Color    | `"white"`                                    | Controls the **text color** in `amountColor`                                                                                                                                                                                                                                                                           |
| `depotColorSufficient`       | String/Color    | `"gray"`                                     | Controls the **color** of the labels displaying **sufficient amount of stock**                                                                                                                                                                                                                                         |
| `depotColorSufficientFont`   | String/Color    | `"white"`                                    | Controls the **text color** in `depotColorSufficient`                                                                                                                                                                                                                                                                  |
| `depotColorCraftable`        | String/Color    | `"#009900"`                                  | Controls the **color** of the labels displaying **insufficient stock that can be crafted**                                                                                                                                                                                                                             |
| `depotColorCraftableFont`    | String/Color    | `"white"`                                    | Controls the **text color** in `depotColorCraftable`                                                                                                                                                                                                                                                                   |
| `depotColorInsufficient`     | String/Color    | `"red"`                                      | Controls the **color** of the labels displaying **insufficient stock**                                                                                                                                                                                                                                                 |
| `depotColorInsufficientFont` | String/Color    | `"white"`                                    | Controls the **text color** in `depotColorInsufficient`                                                                                                                                                                                                                                                                |
| `gampressUrl`                | String/URL      | `"https://gamepress.gg/arknights/operator/"` | The **base URL** for Operators on **Gamepress**. Just in case this ever changes.                                                                                                                                                                                                                                       |
| `depotParsingEnabled`        | Boolean         | `true`                                       | Whether to **enable** the **depot scanning** feature. Disabling this will hide relevant UI-Elements                                                                                                                                                                                                                    |
| `arknightsContainer`         | String          | `"BlueStacks"`                               | The type of player you run Arknights with. Currently two modes are supported `"BlueStacks"` and `"genericWindow"`.                                                                                                                                                                                                     |
| `arknightsWindowName`        | String          | `"BlueStacks"`                               | The name of the **window** that **Arknights** is running in. This can either be read from the window title or a list is provided by `FindArknightsWindow.exe` is this value is left empty.                                                                                                                             |
| `arknightsInputWindowName`   | String          | `"plrNativeInputWindowClass"`                | The name of the **child window class** that accepts input. Only supported for `arknightsContainer` = `"genericWindow"` This is an **expert setting**. `FindArknightsWindow.exe` will list available child windows for the window given in `arknightsContainer`. Can also be set to `null` to use the top-level window. |
| `arknightsWindowBorder`      | List[Number]    | `[1, 33, 33, 1]`                             | The amount of **pixels to crop away** from Arknights **screenshots** from the Left, Top, Right and Bottom respectively.                                                                                                                                                                                                |
| `colorLeniency`              | Number          | `3`                                          | How lenient certain pixel reads should be to determine which menu the Arknights app is in. This is a allowed delta in color value(0-255) per band.                                                                                                                                                                     |
| `tesseractExeLocation`       | String/Filename | `null`                                       | Path to the **Tesseract Exe** to use for Depot Scanning.                                                                                                                                                                                                                                                               |



