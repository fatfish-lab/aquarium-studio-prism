# Aquarium Studio plugin for Prism

> Aquarium Studio plugin for Prism allow you to sync and publish your shots and assets with [Prism](https://prism-pipeline.com/)

Aquarium Studio is developed by [Fatfish Lab](https://fatfi.sh).

## Installation
This plugin is compatible with v1.3 of Prism.

1. Open your command line
1. Go to the Prism's dedicated plugin folder for ProjectManagers: `C:\Prism\Plugins\ProjectManagers`
1. Clone the repository in the previous folder, with a custom directory name
    1. `git clone ssh://git@github.com/fatfish-lab/aquarium-studio-prism.git Aquarium`
1. Open Prism
1. Go to Prism's settings > `Plugins` tab
1. Enable `Aquarium Studio` plugin
1. Configure Aquarium Studio integration in Prism

## Configuration
To be able to use the plugin in Prism, you have to enable it, in your project Settings :

1. Open Prism
1. Go to Prism's settings > `Project Settings` tab
1. Enable `Aquarium Studio integration`
1. Add your Aquarium Studio site url
    1. To get your Aquarium site url go to your Aquarium Studio instance
    1. On the `Dashboard` page, go to `Organisation` tab
    1. In the `Development` section, click on the `API url endpoint` to copy it
    1. Paste it in Prism
1. Click on the button `Save and go to 'User' tab to add your Aquarium credentials`
1. Add your `email` and `password` you use to connect to Aquarium Studio
1. Click on the `Signin` button
1. Go back to the `Project Settings` tab
1. In the `Aquarium project` list, choose the corresponding Aquarium's project
1. Don't forget to save your modification by pressing the `Save` or `Apply` button at the bottom of the window

Now, we need to configure Prism, directly from Aquarium Studio's web interface :

1. Go to your Aquarium Studio instance
1. Open the project settings
1. Go to the `Connectors` tab and click on `Enable connector` for Prism pipeline v1

### Where do you store your assets, shots and timelogs in this project ?
1. Choose your assets, shots and timelogs locations by picking the folder where you store them.

> - Those parameters are `optionnal`. If you let them empty, the project's will be used instead.

### Prism steps and categories
1. Drag and drop the `Available tasks` in Prism `steps` to create the categories.

> - In Aquarium, `steps` doesn't exist. So you can organize them as you want
> - The `categorie names`, need to match with the tasks name of your shots and/or assets to be synced by the connector
> - During `Aquarium to Prism sync`, if a task doesn't exist, the category will be ignored

> :warning: Don't forget to save the configuration before closing the window

## Update
To update your Aquarium Studio plugin for Prism, you can use `git` commands

1. Open your command line
1. Go to the `Aquarium` prism's dedicated plugin folder: `C:\Prism\Plugins\ProjectManagers`
1. Pull the lastest changes
    1. `git pull`
1. (Re)start Prism or use the `Reload all plugins` button in Prism's settings > `Plugins` tab

## Documentation

A dedicated documentation is in writing progress. In the meantime, fill free to [contact us](https://fatfi.sh/contact-us/) if you have any questions or issues.

## Security disclaimer
To connect and exchange data between Prism and Aquarium Studio, you need to add your Aquarium's credentials.

During this process, you will be asked to provide your email and password. Those data will not be stored in the Prism's user settings file. Instead we only store the user authentication token.

This token is stored in **plain text** in the `Prism.yml` file of the user. We are currently implementing a solution to encrypt this token.

## Maintainer

The repository is maintained by [Fatfish Lab](https://fatfi.sh). 

## Support

You can contact our team at [support@fatfi.sh](mailto:support@fatfi.sh).

## Licence

This project uses the following license: GPL-3.0-only. See the license file to read it.

