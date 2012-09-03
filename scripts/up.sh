#!/bin/bash

screens=`screen -ls`

if [[ $screens == *mc_fluid* ]]
        then
		echo "mc_fluid is already running"
	else
		echo "starting mc_fluid"
                cd fluid
                screen -dmS mc_fluid java -jar craftbukkit.jar
                cd ..
fi

if [[ $screens == *mc_creative* ]]
        then
                echo "mc_creative is already running"
        else
		echo "starting mc_creative"
                cd creative
                screen -dmS mc_creative java -jar craftbukkit.jar
                cd ..
fi

if [[ $screens == *mc_tekkit_restricted* ]]
        then
                echo "mc_tekkit_restricted is already running"
        else
                echo "starting mc_tekkit_restricted"
                cd tekkit_restricted
                screen -dmS mc_tekkit_restricted java -jar Tekkit.jar
                cd ..
fi

if [[ $screens == *mc_tekkit_creative* ]]
        then
                echo "mc_tekkit_creative is already running"
        else
                echo "starting mc_tekkit_creative"
                cd tekkit_creative
                screen -dmS mc_tekkit_creative java -jar Tekkit.jar
                cd ..
fi

if [[ $screens == *mc_experiment* ]]
        then
                echo "mc_experiment is already running"
        else
                echo "starting mc_experiment"
                cd experiment
                screen -dmS mc_experiment java -jar craftbukkit.jar
                cd ..
fi


