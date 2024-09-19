# Scripts to run the tasks on self-contained derived data

## Requirements
In order to execute the scripts in this folder, [O2Physics](https://github.com/AliceO2Group/O2Physics) must be installed

## Run the B<sup>0</sup> task
The script [run_b0_analysis.sh](https://github.com/beauty-hunters/b_analysis/blob/main/derived_data_analysis/run_b0_analysis.sh) can be used to execute the [taskB0Reduced.cxx](https://github.com/AliceO2Group/O2Physics/blob/master/PWGHF/D2H/Tasks/taskB0Reduced.cxx) locally
In order to do that, the user must:
- enter the `O2Physics` environment
- edit the [dpl-config_b0.json](https://github.com/beauty-hunters/b_analysis/blob/main/derived_data_analysis/dpl-config_b0.json) or [dpl-config_b0_mc.json](https://github.com/beauty-hunters/b_analysis/blob/main/derived_data_analysis/dpl-config_b0_mc.json) (depending if MC or real data are analysed) config files with the desired configurations
- if the output tree is selected in the task, specity the output tables in [OutputDirector.json](https://github.com/beauty-hunters/b_analysis/blob/main/derived_data_analysis/OutputDirector.json)
- run the [run_b0_analysis.sh](https://github.com/beauty-hunters/b_analysis/blob/main/derived_data_analysis/run_b0_analysis.sh) script with `./run_b0_analysis.sh` in case of real data, or `./run_b0_analysis.sh --mc 1` in case of MC data.