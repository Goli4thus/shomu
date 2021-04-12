# ShoMu - shortcut multiplexer

<img src="resources/shomu.png" alt="ShoMu" width="350" height="350">

## Motivation
How about the ability to launch a small application with a global shortcut, which then transforms your keyboard 
into some kind of `vim normal mode`, where each key (including modifiers) will launch another application or script.
On top of that being able to easily switch between mutliple contexts, each with its own mappings.

### Why would this be useful?

Sure, there are ways to set up global shortcuts on a given OS (i.e. Linux, Windows, macOS).
But the more such global shortcuts one defines (e.g. Alt-F2), the less of these combinations are available for applications that actually need them.

Furthermore there's just one scope: the global scope. 
And that means the number of actually easily reachable (i.e. ergonomic) shortcuts is quite limited.

But if we offload shortcuts to a dedicated "launcher application", which creates more of these "scopes", then there's both less need for such global shortcuts and more space to map keys as desired (i.e. combinations that could never be used as a global shortcut, because they would interfere with every other application; e.g. single key 'f').

Concrete example:

Let's say you're working on multiple projects, each with a similar folder structure.
Then let's say there are four locations in each project you frequenlty want to access via a file manager.
Of course, you could just set up a plethora of file manager bookmarks and then use that.
But that can quickly become a pain to navigate.

How about using four keys (e.g. `a, s, d, f`), where each one will open a file manager in a specific location based on a previously selected *context*?

With this you can say (assuming launching the app beforehand via some form of global hotkey):
- press `1a`: open file manager at context 1, location 1
- press `2a`: open file manager at context 2, location 1
- press `3a`: open file manager at context 3, location 1
- press `4a`: open file manager at context 4, location 1
- press `1s`: open file manager at context 1, location 2
- press `2s`: open file manager at context 2, location 2
- ...

![ShoMu](resources/ShoMu__example.png)

## Dependencies
### For python 3.7 or newer
- python (that's it)
### For python older than version 3.7
- python
- tkinter

#### Example: Ubuntu
`sudo apt-get install python3-tk`

But yeah, it's basically cross platform (i.e. Linux, Windows, macOS).

_Note:_ I don't have access to macOS, so I can't really test it myself. Feedback is welcome!


## Configuration
### Config file selection
Prioritization of config file lookup is as follows:
1) `--config` argument (optional)
2) `./shomu_cfg.json`: config file in same directory as script itself
3) `~/.config/shomu/shomu_cfg.json`: config file in home folder


### Config file syntax
Have a look at `shomu_cfg_example_linux.json` for reference.

- top level is about contexts
- `conf` section is about a context's visual presentation (colors can either be keywords or hex values) 
- `keys` section is where a context's shortcuts and associated commands are defined

### Keys in detail
- keys and modifiers:
    - keyboard letters need to be defined in lower case; exception: if `Shift-` modifier is being used, then keys need to be defined in upper case (there's some config sanity checking built in, so even if you forget about this, it will warn you about it during startup)
    - here's a list of special keys: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/key-names.html
    - see the example config file for a couple modifier usecases
- `command`:
    - rule of thumb: if the command runs within a terminal (regardless of the current directory), then there's a good chance the command will work here as well
    - for scripts:
        - if you want your script (e.g. "my_script.py") to launch in a new terminal window and stay open at the end, then try this:
            -  example Linux: "xfce4-terminal -x bash -c \"python /path/to/my_script/my_script.py;read\"" (that final `read` is for keeping console open; just hit enter afterwards to close it)
            -  example Windows: "start cmd /c python /path/to/my_script/my_script.py"
    - for "opening {myfile.txt} with OS default application", try the following:
        - Linux: `xdg-open myfile.txt`
        - Windows: `start myfile.txt`
        - macOS: `open myfile.txt`
- `cwd`:
    - if `cwd` is set to a path, the given `command` will be executed within that directory; otherwise (i.e. if`"None"), no directory change will be performed
    - rule of thumb: if the script doesn't depend on being executed from a specific directory (i.e. because there are no things it references via relative paths based on where it's executed from), then you can probably skip setting `cwd`


## Usage
- initial setup:
    - it's recommended to set up one global shortcut for launching this app (starting it via application menu defeats its purpose kind of)
    - examples:
        - Linux: most window managers should come with the ability to do this
        - Windows: using something like _autohotkey_ works well (e.g. `run pythonw D:\path\to\script\shomu.py --config shomu_cfg_windows.json, D:\path\to\script\`)
        - macOS: _open for feedback_
    - recommendation:
        - this whole thing becomes really useful if you can basically control it all via one hand, especially if it's about launching graphical applications and mouse interaction

- default keys (i.e. regardless of config file):
    - `Esc`: closes application
    - `?`: opens config file with default OS application associated with '.json' files (_hint_: if in your case that's not a text editor of some kind, it might not be that useful)
    - number keys `1` through `9`: direct selection of respective context

- basic workflow:
    - launch the app
    - select desired context
    - run command via configured shortcut
    - repeat as needed

## Further thoughts
- depending on your needs, you could easily set up more than one global shortcut for launching the app, each one loading a dedicated config file
