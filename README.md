# Home Assistant - SickGear Integration
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=thisisthetechie&repository=home-assistant-sickgear&category=integration)

<div><a id="top"><img alt="Home Assistant" height="100" src="https://www.home-assistant.io/images/favicon-192x192-full.png" /><img alt="SickGear" width="200" src="https://raw.githubusercontent.com/wiki/SickGear/SickGear.Wiki/images/SickGearLogo.png"></a></div>

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

_Home Assistant Integration to communicate with [sickgear][sickgear]._

**This integration will set up the following platforms.**

Platform | Description
-- | --
`switch` | Turn something `on` or `off`.
`sensor` | Show info from blueprint API.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `sickgear`.
1. Download _all_ the files from the `custom_components/sickgear/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Integration blueprint"

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[sickgear]: https://github.com/SickGear/SickGear/wiki
[buymecoffee]: https://www.buymeacoffee.com/thisisthetechie
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/thisisthetechie/home-assistant-sickgear.svg?style=for-the-badge
[commits]: https://github.com/thisisthetechie/home-assistant-sickgear/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[sick_image]: https://github.com/SickGear/SickGear/wiki/images/SickGearLogo.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/thisisthetechie/home-assistant-sickgear.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40thisisthetechie-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/thisisthetechie/home-assistant-sickgear.svg?style=for-the-badge
[releases]: https://github.com/thisisthetechie/home-assistant-sickgear/releases
