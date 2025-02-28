# Genie

We introduce *independent view fuzzing*, a novel, fully automated approach for
detecting non-crashing functional bugs in Android apps. 
We have realized this approach as an automated, end-to-end functional
fuzzing tool, *Genie*. 

Given an app, (1) Genie automatically detects non-crashing bugs without requiring
human-provided tests and oracles (thus fully automated); and (2) the detected non-crashing bugs are diverse
(thus general and not limited to specific functional properties), which set Genie apart from prior work.

# Publication

[1] ["Fully Automated Functional Fuzzing of Android Apps for Detecting Non-Crashing Logic Bugs"](https://tingsu.github.io/files/oopsla21-Genie.pdf)
Ting Su, Yichen Yan, Jue Wang, Jingling Sun, Yiheng Xiong, Geguang Pu, Ke Wang, Zhendong Su. In SPLASH/OOPSLA 2021. 

```
@article{10.1145/3485533,
   author = {Su, Ting and Yan, Yichen and Wang, Jue and Sun, Jingling and Xiong, Yiheng and Pu, Geguang and Wang, Ke and Su, Zhendong},
   title = {Fully Automated Functional Fuzzing of Android Apps for Detecting Non-Crashing Logic Bugs},
   year = {2021},
   issue_date = {October 2021},
   volume = {5},
   number = {OOPSLA},
   doi = {10.1145/3485533},
   journal = {Proc. ACM Program. Lang.},
   month = oct,
   articleno = {156},
   numpages = {31}
}
```

## 1. Video illustrations of functional bugs found by Genie 
(corresponding to RQ4: Bug Types and Characteristics)


### Bug type 1 (User data/setting lost)

This bug type leads to user data/setting lost. Sometimes, this bug type can bring severe consequences and critical user complaints.

Example Issue from [Markor](https://play.google.com/store/apps/details?id=net.gsantner.markor)

Bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/5))


### Bug type 2 (Function cannot proceed)

This bug type means one specific app functionality that works well before suddenly cannot proceed anymore and loses effect.

Example Issue from [SkyTube](https://skytube-app.com/)

Bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/6))


### Bug type 3 (Unexpected wrong behavior)

This bug type means the specific functionality shows wrong behavior w.r.t. its previous correct behavior.

Example Issue from [ActivityDiary](https://play.google.com/store/apps/details?id=de.rampro.activitydiary)

Bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/1))


### Bug type 4 (Inconsistent GUI states)

This bug type means the GUI states are inconsistent for specific functionality, which counters users’ intuition on app function.

Example Issue from [Transistor](https://play.google.com/store/apps/details?id=org.y20k.transistor)

Bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/4))


### Bug type 5-1 (Duplicated GUI views)

This bug type means some GUI views are erroneously duplicated.

Example Issue from [Tasks](https://play.google.com/store/apps/details?id=org.tasks)

Bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/3))


### Bug type 5-2 (Disappeared GUI views)

This bug type means some GUI views inadvertently disappear.

Example Issue from [Fosdem](https://play.google.com/store/apps/details?id=be.digitalia.fosdem)

Bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/2))


### Bug type 5-3 (Incorrect GUI display information)

This bug type means some views are incorrectly displayed.

Example Issue from [RadioDroid](https://play.google.com/store/apps/details?id=net.programmierecke.radiodroid2)

Bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/9))


### Other bug samples (much more complicated)

[UnitConverter](https://play.google.com/store/apps/details?id=com.physphil.android.unitconverterultimate) (1,000,000~50,000,000 installations on Google Play, 144 Github stars)

- User data/setting lost - bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/7))

- This issue escaped from developer/user testing for more than 4 years.


[Markor](https://play.google.com/store/apps/details?id=net.gsantner.markor) (50,000~100,000 installations on Google Play, 1200+ Github stars)

- Inconsistent GUI states - bug report ([link](https://github.com/functional-fuzzing-android-apps/home/issues/8))

- This issue escaped from developer/user testing for more than 2.5 years and affected 74 releases.


## 2. Bug report visualization by Genie (a bug report sample)

Bug summary ([link](https://github.com/functional-fuzzing-android-apps/home/issues/10))

Bug report generated by Genie during functional fuzzing ([link](https://functional-fuzzing-android-apps.github.io/home/app-ActivityDiary-bug-report-example/seed-tests/seed-test-7/mutant-659/index_aligned_9.html))

Explanation:

1. The left column is the seed test (randomly generated), while the right column is the mutant test. The two tests are aligned to ease inspection (the indpendent event trace is representd by trace [4,5] in the mutant test).

2. For each test, the GUI pages denote the layouts (GUI states), and the text besides each page denotes the GUI event that works on the previous page and leads to the current page. The icon on top of the text is the receiver view of the event on the previous page. 

3. The oracle checking checking is conducted on the layouts highlighted by the two red boxes. The GUI consistencies are highlighted by small red boxes on the corresponding GUI pages. Due to the GUI effect of seed test, i.e., chaning from ``<No Activity>`` to ``Empty Activity`` is not contained in that of mutant test, i.e., chaning from ``Gardening`` to ``<No Activity>``.  Thus, a likely functional bug was detected and it is a true positve.

4. Model, seed, and mutant visualization

- The concrete GUI transitional model ([link](https://functional-fuzzing-android-apps.github.io/home/app-ActivityDiary-bug-report-example/index.html));  

- the abstracted GUI transitional model ([link](https://functional-fuzzing-android-apps.github.io/home/app-ActivityDiary-bug-report-example/index_cluster.html));  

- the seed test (``seed-test-7`` in this case) ([link](https://functional-fuzzing-android-apps.github.io/home/app-ActivityDiary-bug-report-example/seed-tests/seed-test-7/index.html)); 

- the generated mutant test (``mutant-659`` in this case) from the seed test at 3th insertion position: ([link](https://functional-fuzzing-android-apps.github.io/home/app-ActivityDiary-bug-report-example/seed-tests/seed-test-7/mutant-659/index.html)).

---

# Documentation: Using Genie 

## Step 0. Preparation

Create a fresh Android 6.0 emulator:

```
avdmanager create avd --force --name testAVD_Android6.0 --package 'system-images;android-23;google_apis;x86' --abi google_apis/x86 --sdcard 512M --device 'Nexus 7'
```

Modify the fresh emulator for Genie (add files into sdcard and remove unnecessary default apps):

```
emulator -avd testAVD_Android6.0 &
python3 -m deploy.emulator init -s emulator-5554
```

Start the emulator in the read-only mode (without leaving any side-effect for next start-up)

```
emulator -avd testAVD_Android6.0 -read-only &
```

Now, we have three phases:

## Step 1. Model construction

```
python3 -m droidbot.start -d emulator-5554 -a apps_for_test/de.rampro.activitydiary_118.apk -policy weighted -count 500 -grant_perm -is_emulator -interval 2 -o ./tmp-diary -script user_script.json
```

Here, 

``-d``: the device serial number

``-a``: the file path of apk 

``-policy``: ``weighted`` (recommended), ``dfs_greedy``

``-count``: the maximum allowed events (``2000``, recommended)

``-grant_perm``: grant all permissions while installing the apk

``-is_emulator``: declare the target device to be an emulator

``-interval``: interval in seconds between each two events (Default: 1). This option is especially used for the situation: the app has dynamic features (like the ActivityDiary app we tested). In practice, 2 should be enough. If the app is quite stable and your testing environment is good, 0 or 1 is also okay.

**Note**: In general, we cannot ensure the app state can always reach stable during testing. Internally, Genie implements a simple workaround to check whether the app state reaches stable.

``-o``: the output directory

``-script``: the optional file path of user-defined script, which contains a sequence of input events (e.g., bypass welcome page, login user account)

## Step 2. Property-preserving mutant generation

### Mode 1. mutant generation from random seed tests (without execution of mutants)

If you want to only generate mutant tests (without actual execution), then use the following command line:

```
python3 -m droidbot.start -d emulator-5554 -a apps_for_test/de.rampro.activitydiary_118.apk -policy fuzzing_gen -count 100000 -max_seed_test_suite_size 10 -max_random_seed_test_length 15 -max_independent_trace_length 8 -max_mutants_per_insertion_position 30 -grant_perm -is_emulator -interval 1 -coverage -o ./tmp-diary -script user_script.json
```

Here, 

``-policy``: ``fuzzing_gen`` (generate seed tests and their corresponding mutants, but do not execute the mutant tests, used for distributed testing (see below)); or
            ``fuzzing_gen_seeds`` (only generate seed tests)

``-multi-mutant-gen n``: use multiprocessing when generating mutants, n is optional, default to number of seed tests

``-count``: the maximal number of allowed events for generating seed tests (just give a large enough number, e.g., ``100000``); 

``-max_seed_test_suite_size``: the maximal number of seed tests to generate;

``-max_random_seed_test_length``: the maximal length of each seed test; 

``-max_independent_trace_length``: the maximal length of independent trace (#independent events) that is inserted into the seed test; 

``-max_mutants_per_insertion_position``: the maximal number of mutants generated for one insertion position;

``-max_mutants_per_seed_test``: the maximal number of mutants generated for one seed test;

``-coverage``: dump the coverage for seed tests (the apk should be already instrumented);

``-o``: the output directory used in Step 1, which is used to recover the model constructed in Step 1

**Note**: 

1. You can specify ``-max_seed_test_suite_size``, ``-max_random_seed_test_length``, ``-max_independent_trace_length``, ``-max_mutants_per_insertion_position`` and ``-max_mutants_per_seed_test`` to control the number of generated mutant tests.

2. We recommend to add ``-interval 1`` to make sure the seed generation process is stable.

3. By default, Genie use ``weighted`` policy to generate random seed tests.

4. In this mode, we do not need to specify ``-config-script``, which is used for oracle checking and relocate views during actual execution of mutant tests.

### Mode 2. run one specific mutant (internally called by multiple-threads fuzzing)

```
python3 -m droidbot.start -d emulator-5554 -a apps_for_test/de.rampro.activitydiary_118.apk -policy fuzzing_run -config-script script_samples/diary_activity_ignore_view_diffs_script.json -grant_perm -is_emulator -keep_app -o ./tmp-diary/ -mutant ./tmp-diary/seed-tests/seed-test-1/mutant-1 -coverage
```

Here,

``-policy``: ``fuzzing_run`` (run the mutant)

``-mutant``: the dir of one specified mutant (Genie will automatically infer its seed test)

``-keep_app``: keep the app after running the mutant 

``-config-script``: the script that specifies which views or the order of children views can be ignored when do oracle checking (this file is very important to reduce false positives). 

**Note**:
 
1. Please do not use ``-keep_env``, which may bring some issues.

2. Please use ``-keep_app``, which will not uninstall the app after running the mutant test. Before running each mutant, Droidmutant will restore the app to its original state. So, we do not need to worry about this.

3. We may not need to specify ``-interval``.

### Mode 3. mutant generation and execution (single-thread, combine mode 1 and 2)

```
python3 -m droidbot.start -d emulator-5554 -a apps_for_test/de.rampro.activitydiary_118.apk -policy fuzzing -count 10000 -max_seed_test_suite_size 10 -max_random_seed_test_length 15 -max_independent_trace_length 8 -max_mutants_per_insertion_position 30 -config-script script_samples/diary_activity_ignore_view_diffs_script.json -grant_perm -is_emulator -interval 1 -o ./tmp-diary -script user_script.json
```

Here, 

``-policy``: fuzzing (it generates one property-preserving mutant and executes it at one time, mainly used for debugging). If we use ``fuzzing_gen``, then we only generate mutants and dump them without actual execution. This option is used for distributed testing (see below);

``-count``: the total number of events for generating seed tests (just give it a large enough number); 

``-max_seed_test_suite_size``: number of seed tests to generate;

``-max_random_seed_test_length``: the maximal length of each seed test; 

``-max_independent_trace_length``: the maximal length of independent trace that is inserted into the seed test; 

``-max_mutants_per_insertion_position``: the maximal number of mutants generated for one insertion position;

``-max_mutants_per_seed_test``: the maximal number of mutants generated for one seed test;

``-o``: specify the same directory as Phase 1, which we use to recover the model constructed in Phase 1

``-coverage``: dump the coverage for seed tests and mutant tests

``-config-script``: the script that specifies which views or the order of children views can be ignored when do oracle checking (this file is very important to reduce false positives). 


## Step 1 and 2 Run together

We provide a script to run model construction and seed/mutant generation together.

```
python3 deploy/prerun.py base apps_for_test/de.rampro.activitydiary_118.apk ./tmp-diary --no-headless --script script_samples/user_script.json --offset 3
```

Positional arguments: ``avd``, ``apk``, ``out``

Optional arguments: 

``--no-model``: do not construct model

``--no-seed``: do not generate seeds and mutants

### Output of Step 1 and Step 2

``tmp-diary/`` -- data of the original utg model

``tmp-diary/{app_package_name}_testing_result.txt`` -- the final testing results (valid only when use 2.1)

``tmp-diary/seed-tests/``  -- data of all randomly generated seed tests

``tmp-diary/seed-tests/seed-test-1/`` -- data of the seed test and all mutants

``tmp-diary/seed-tests/seed-test-1/mutant-1`` -- data of the mutant test

``tmp-diary/seed-tests/seed-test-1/mutant-1/index_x.html`` -- the execution results with annotation info to highlight the semantic errors

``tmp-diary/seed-tests/seed-test-1/mutant-1/checking_result.json`` -- the detailed results of oracle checking

``tmp-diary/seed-tests/seed-test-1/mutant-1/gui_diff_analysis.txt`` -- the summary results of oracle checking


## Step 3. Multiple-threads functional fuzzing (mutant execution)

We currently support distributed testing on Android emulators.

```
python3 -m deploy.start --no-headless -n 8 --apk apps_for_test/de.rampro.activitydiary_118.apk -o ./tmp-diary/ --script script_samples/diary_activity_ignore_view_diffs_script.json --timeout 900 --offset 2
```

Here,

``-n N``: number of emulators/devices that will be used for distributed testing

``--offset N``: specify the starting emulator serial number. If N=1, starting from ``emulator-5556``

``--timeout``: the maximum allowed testing time allocated for each mutant test. If timeouts, we will run the mutant one more time and give up if it timeouts again.

``--script``: the ignore view diffs script


Other options:

``--no-headless``: do not hide the emulators 

``--no-trie-reduce``: do not use trie to prune infeasible mutant tests (By default, we do not add this option. We use trie to prune infeasible mutant tests.)

``--no-trie-load``: do not load trie data from previous log (By default, we do not add this option. We use load trie data from previous run.)

``--no-skip``: do not skip any executed mutant tests (By default, we do not add this option. We will skip any executed mutant tests if we restart the fuzzing.)

``--no-coverage``: do not dump coverage of mutant tests (By default, we do not add this option. We will dump coverage for each mutant test.)

``--seeds-to-run``: ``all``, or ids of seed tests to run, like "1;2;3" (run all the mutant tests of seed tests with ids 1, 2, 3, **remember to add quotes**)

``--debug`` or ``--test-single-mutant``: the file path of a mutant (run a single mutant), this implies `--no-skip`

``--interval``: interval in seconds between each two events (Default: 0)

``--trie-delete``: delete infeasible mutants according to the trie structure during fuzzing

Note: In some cases, we may hope to rerun the mutants of some specific seeds, we can simply append ``--no-skip`` to the original command line.  But if we also add
``--no-trie-reduce``, then all the mutants will be executed again but will not use the previous trie to prune unreplayable mutants. Another way is to manually
delete the corresponding log files and rerun. 

Please see ``script_samples/run_genie.sh`` for reference.


## Step 4. Postprocess the results (reduce false positives and merge similar reported errors)


```
python3 -m droidbot.postprocess -o ./tmp-diary/ -f script_samples/app-ActivityDiary-script/checking_config.json
```

Output Report, e.g.,

``
./tmp-diary/merged_results.txt
``

The report includes:
 
 - ``#mutants`` and ``#executed_mutants``
 
 - ``crash errors`` and ``semantic errors``

We can focus on ``Crash Errors`` and ``Semantic Errors``.


## 5. Compute Jacoco-based coverage

#### Merge Coverage
`$ python3 -m deploy.coverage.merge <output-dir> --seed-cov-out <merged-seed-coverage-file-name> --mutant-cov-out <merged-mutant-coverage-file-name>`

or

`$ python3 -m deploy.coverage.merge <output-dir> --seed --mutant`, in this case `seed.ec` and `mutant.ec` will be generated under `<output-dir>`

Example (merge all coverage files of seeds and mutants):

```
python3 -m deploy.coverage.merge /mnt/droidbot-share/test-ActivityDiary-r1 --seed-cov --mutant-cov
```

Merge coverage files of specific seeds or mutants

```
python3 -m deploy.coverage.merge /mnt/droidbot-share/test-ActivityDiary-r1 --seed-cov --mutant-cov [--seeds '1;2;3'] [--mutants '1;2;3']
```

#### Get report
```$ python3 -m deploy.coverage.report --project ~/Projs/app-coverage-analysis/apps/org.jtb.alogcat_43_src-gradle --class app/build/intermediates/classes/ --source app/src/main/java/ coverage.ec[, coverages] <html-report-gen>```

Example:

```
python3 -m deploy.coverage.report --project ~/droid_repo/ActivityDiary --class app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes/ /mnt/droidbot-share/test-ActivityDiary-r1/mutant.ec /mnt/droidbot-share/test-ActivityDiary-r1-mutant-report
```

# Documentation: Debugging/Verifying Genie 

To debug and verify Genie, we offer a number of debugging strategies.

#### (1) generate a number of mutants for a given seed test

This strategy can let us inspect whether Genie can indeed generate specific mutants from a given seed test. Usually, this seed test is also specified by us. 

```
python3 -m droidbot.start -d emulator-5554 -a apps_for_test/de.rampro.activitydiary_118.apk -policy fuzzing_gen -count 100000 -max_seed_test_suite_size 1 -max_random_seed_test_length 1 -max_independent_trace_length 8 -max_mutants_per_insertion_position 100 -grant_perm -is_emulator -interval 1 -coverage -script script_samples/diary_seed_test.json -o ./tmp-diary
```

**Note**:

1. We add the option ``-script script_samples/diary_seed_test.json`` so that Genie will execute this predefined seed test first before generating random seed tests.

2. We set ``-max_seed_test_suite_size 1 -max_random_seed_test_length 1`` so that Genie will only execute the given seed test and will not generate random seed tests.

3. We set ``-max_independent_trace_length 8 -max_mutants_per_insertion_position 100`` to control the mutant generation.


We provide a functionality that can show the seed test, mutant test, critical events (necessary for mutation) on the clustered utg. After successfully running the following commands, it will dump a file named ``index_clustered_utg_with_annotated_test.html`` under
the output directory, which annotates the seed test or the mutant test in red and critical views in blue.

**Note**: When a seed test was executed, the utg event ids (of the transitions of this seed test) will be updated (i.e., increased). 
Thus, when you execute a seed test and generate a number of mutant test, and want to verify the results, you should run the following
commands accordingly, so that it can reflect the change of the utg event ids.

Example usages:

#### (2) Show the seed test

Show a given seed test on the clustered utg.

```
python3 -m droidbot.debug --apk apps_for_test/instrumented_apps/org.tasks.debug-gplay-6.6.5.apk --output test-tasks-model-1/ --seed test-tasks-model-1/seed-tests/seed-test-17
```

#### (3) Show the mutant test (with its corresponding seed test)

Show a given mutant test (with its seed test) on the clustered utg.

```
python3 -m droidbot.debug --apk apps_for_test/instrumented_apps/org.tasks.debug-gplay-6.6.5.apk --output test-tasks-model-1/ --mutant test-tasks-model-1/seed-tests/seed-test-17/mutant-113/
```

#### (4) Show the seed test and highlight critical events


```
python3 -m droidbot.debug --apk apps_for_test/instrumented_apps/org.tasks.debug-gplay-6.6.5.apk --output test-tasks-model-1/ test-tasks-model-1/seed-tests/seed-test-17 --views script_samples/app-tasks-script/critical_views.json
```


## Note

Genie is built upon Droidbot and Stoat.

