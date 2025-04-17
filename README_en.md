# configCommand / cfgcmd

[简体中文](/README.md)
[Link](https://cfgcmd.wangyupu.com)

> Still translated by gpt-4o

Use MCDR commands in the game to modify configurations of other plugins/Mods!

**Version `1.3.1` supports online editor**

## Permissions

Currently, the plugin allows all players with permissions to modify the configuration (MCDR level 4). This plugin can modify **all files that the user running the MCDR process has access to** (especially `root`), so **please control permissions or run the server in a container**.

## Commands

- `!!cfg env <path, starting from the MCDR root path, can be absolute/relative path> <config file> [optional: reader type]`: Set the target file modified by the executor
- `!!cfg quit`: Clear the executor's target file
- `!!cfg write`: Write to the target file
- `!!cfg reload`: Reload the target file (overwrites all previous modifications)
- `!!cfg info`: View file information

---

- `!!cfg set <key> <value>`: Set a key-value pair, where `<key>` uses `.` to separate paths in the configuration tree (see the example below). This command does not support relative paths like `..` in the `key`. See the "Types" section below for types.
- `!!cfg setTyped <key> <type> <value>`: See the "Types" section below. If the value cannot be interpreted as the specified type, it will default to `STRING`.
- `!!cfg rm <key>`: Delete the key's content
- `!!cfg mv <sourceKey> <destKey>`: Move or rename
- `!!cfg cp <sourceKey> <destKey>`: Copy and paste
- `!!cfg cd <key>`: Since configuration files are tree-structured, this command provides a file-system-like `cd` operation. Not available when the reader is `plain`.
- `!!cfg ls [optional: page] [require prior key]: View the content of the current object. When the reader is `plain`, the entire file is printed. Each page contains 10 lines.
- `!!cfg lsLong [required: page] [optional: lines per page] [require prior key]`: Same as the previous command

---

- `!!cfg lsDir <path>`: View a list of files starting from the MCDR root directory
- `!!cfg rmFile <file>`: Delete a file (**cannot be undone**)
- `!!cfg touchFile <file>`: Create an **empty** file

---

- `!!cfg editor`: Open the online editor for the current file, requires setting `enableCloud` to `true`
- `!!cfg editorApply`: Synchronize the modified configuration file from the cloud
- `!!cfg editorDelete`: Delete the cloud session

> If upgrading from version `1.3.1` or below, you need to manually add `enableCloud: true` to your configuration file to use the online editor.

---

> After executing `!!cfg env ...`, the file will not be locked  
> Executing `!!cfg info` will display the current file information  
> Executing `!!cfg ls` will print the content of the object where the pointer is located  
> The reader is determined by the file extension. Files with no extension or unknown extensions will use the `plain` reader  
> When the reader is `plain`, the `<key>` parameter specifies the line number  
> If the `<key>` contains spaces and is followed by other parameters, wrap it in double quotes. Use `\` to escape. See [QuotableText](https://docs.mcdreforged.com/zh-cn/latest/code_references/command.html#mcdreforged.command.builder.nodes.arguments.QuotableText)

### Number Types

`setTyped` can specify the type of a value. The following types are available, and some types have special behaviors:

- `STRING`: Basic string
- `INT`: Number, including floating-point numbers (`float`)
- `BOOL`: Boolean value, case-insensitive, but must be either `T`/`True` (true) or `F`/`False` (false)
- `LIST`: List
- `OBJECT`: JS `Object`, Python `dict`, YAML `mapping`
- `AUTO`: This type directly uses the `set` command

#### Special Behavior for `LIST` and `OBJECT`

##### `LIST`

The input value is split by commas, and you can escape commas with `\` to avoid incorrect splitting. After splitting, each item will be type-inferred and a list will be created. If the value is empty, an empty list is created.

##### `OBJECT`

Similar to `LIST`, the input value is split by commas and then split into key-value pairs using `:`. Commas can also be escaped with `\` to avoid incorrect splitting. The items will be type-inferred (both keys and values) and an `OBJECT` will be created. If the value is empty, an empty `OBJECT` will be created.  
> It is not recommended to use `setTyped OBJECT ...`, as it can encounter input restrictions in chat. It is better to use it only for creating empty `OBJECT`s.

#### Type Inference

All inferred types follow a common logic:

1. If the value doesn't exist or is `None` (case-sensitive), it will start automatic inference, otherwise it will use the existing type.
2. If the value (in uppercase) matches one of `T`, `TRUE`, `F`, or `FALSE`, it is a boolean value.
3. If the value contains non-numeric characters (other than decimal points, negative signs, or double quotes), it is a string.
4. If the value is enclosed in double quotes, it is a string representation of a number. Remove the surrounding double quotes and proceed to step 5.
5. If it consists only of numbers (including possible decimals or signs), it is considered a number.
6. Otherwise, it is a string.

> `LIST` and `OBJECT` are not involved in this inference process, so automatic inference won't result in `LIST` or `OBJECT`.

### Example

Original configuration file:

```json
1  {
2      "foo": 123,
3      "bar": {
4          "barFoo": "?",
5          "barBar": {
6              "barBarFoo": 456
7          }
8      },
9      "buzz": [
10         "wangyupu","zzfx1166"
11     ]
12 }
```

Commands (in order):

1. `!!cfg env "config/foo/" bar.json`: Open the file
2. `!!cfg set foo 1231`: Set the value on line 2 to 1231
3. `!!cfg set bar.barFoo "!": Set the value on line 4 to "!"
4. `!!cfg rm buzz.1`: Remove the second item in the list on line 10 (0-based index)
5. `!!cfg cd bar.barBar`: Change the pointer to the object on line 5
6. `!!cfg set barBarFoo 789`: Set the value on line 6 to 789
7. `!!cfg write`: Write the file
8. `!!cfg quit`: Exit the file

Modified configuration file:

```json
1  {
2      "foo": 1231,
3      "bar": {
4          "barFoo": "!",
5          "barBar": {
6              "barBarFoo": 789
7          }
8      },
9      "buzz": [
10         "wangyupu"
11     ]
12 }
```

## Plugin Configuration

```yaml
ownerPlayer: PlayerName
cfgCmdPermission: 4
allowModifyConfig: true
allowOutBound: false
enableLog: true
onlyOwnerPlayer: false
```

- `ownerPlayer`: The player specified here bypasses all security controls. Leave it empty to apply permission control to all authorized players.
- `allowModifyConfig`: Determines whether the configuration of **this plugin (`cfgcmd`)** can be modified.
- `allowOutBound`: Determines whether accessing files outside the MCDR root path is allowed. When set to `false`, only files within the MCDR path are accessible.
- `enableLog`: Determines whether to enable logging, which will be saved in the *MCDR root path*/logs/cfgcmdLogs/<YYYY>-<mm>-<dd>_<COUNT>.log.
- `onlyOwnerPlayer`: Determines whether only the specified `ownerPlayer` is allowed to use this plugin.

> `allowModifyConfig` defaults to `true` to allow administrators to safely configure the plugin when they cannot access the backend. It is recommended to manually set it to `false` after installation.

## Supported Configuration File Formats

- `json`
- `yaml` (`yml`)
- `toml`
- Plain text
